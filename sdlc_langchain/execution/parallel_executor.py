import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback
from concurrent.futures import ThreadPoolExecutor

from config import execution_config, ExecutionMode


class StageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result from a stage execution."""
    stage_name: str
    status: StageStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tokens_used: int = 0
    
    @property
    def execution_time(self) -> float:
        """Get execution time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


@dataclass
class StageConfig:
    """Configuration for a stage."""
    name: str
    func: Callable
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    can_parallel: bool = True


class ParallelExecutor:
    """Executes pipeline stages with parallel processing support."""
    
    def __init__(
        self,
        max_parallel: int = None,
        mode: ExecutionMode = None,
    ):
        self.max_parallel = max_parallel or execution_config.max_parallel_chains
        self.mode = mode or execution_config.mode
        
        self._stages: Dict[str, StageConfig] = {}
        self._results: Dict[str, StageResult] = {}
        self._lock = asyncio.Lock()
        
        self.on_stage_start: Optional[Callable[[str], None]] = None
        self.on_stage_complete: Optional[Callable[[str, StageResult], None]] = None
        self.on_stage_error: Optional[Callable[[str, Exception], None]] = None
    
    def register_stage(
        self,
        name: str,
        func: Callable,
        dependencies: List[str] = None,
        timeout: int = 300,
        can_parallel: bool = True,
    ):
        """Register a stage for execution."""
        self._stages[name] = StageConfig(
            name=name,
            func=func,
            dependencies=dependencies or [],
            timeout=timeout,
            can_parallel=can_parallel,
        )
    
    def _get_ready_stages(self) -> List[str]:
        """Get stages that are ready to execute."""
        ready = []
        
        for name, config in self._stages.items():
            if name in self._results:
                continue
            
            deps_satisfied = all(
                dep in self._results and 
                self._results[dep].status == StageStatus.COMPLETED
                for dep in config.dependencies
            )
            
            if deps_satisfied:
                ready.append(name)
        
        return ready
    
    async def _execute_stage(
        self,
        name: str,
        context: Dict[str, Any],
    ) -> StageResult:
        """Execute a single stage."""
        config = self._stages[name]
        result = StageResult(
            stage_name=name,
            status=StageStatus.RUNNING,
            start_time=datetime.now(),
        )
        
        if self.on_stage_start:
            self.on_stage_start(name)
        
        try:
            dep_outputs = {
                dep: self._results[dep].output
                for dep in config.dependencies
                if dep in self._results
            }
            
            if asyncio.iscoroutinefunction(config.func):
                output = await asyncio.wait_for(
                    config.func(context, dep_outputs),
                    timeout=config.timeout
                )
            else:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    output = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            lambda: config.func(context, dep_outputs)
                        ),
                        timeout=config.timeout
                    )
            
            result.output = output
            result.status = StageStatus.COMPLETED
            result.end_time = datetime.now()
            
            if self.on_stage_complete:
                self.on_stage_complete(name, result)
            
        except asyncio.TimeoutError:
            result.status = StageStatus.FAILED
            result.error = f"Stage timed out after {config.timeout}s"
            result.end_time = datetime.now()
            
            if self.on_stage_error:
                self.on_stage_error(name, TimeoutError(result.error))
                
        except Exception as e:
            result.status = StageStatus.FAILED
            result.error = f"{type(e).__name__}: {str(e)}"
            result.end_time = datetime.now()
            
            if self.on_stage_error:
                self.on_stage_error(name, e)
        
        return result
    
    async def execute_all(
        self,
        context: Dict[str, Any],
        stages: List[str] = None,
    ) -> Dict[str, StageResult]:
        """Execute all registered stages."""
        self._results = {}
        
        if stages:
            self._stages = {
                k: v for k, v in self._stages.items() 
                if k in stages
            }
        
        if self.mode == ExecutionMode.SEQUENTIAL:
            await self._execute_sequential(context)
        else:
            await self._execute_parallel(context)
        
        return self._results
    
    async def _execute_sequential(self, context: Dict[str, Any]):
        """Execute stages one at a time."""
        execution_order = self._topological_sort()
        
        for stage_name in execution_order:
            result = await self._execute_stage(stage_name, context)
            async with self._lock:
                self._results[stage_name] = result
            
            if result.status == StageStatus.FAILED:
                break
    
    async def _execute_parallel(self, context: Dict[str, Any]):
        """Execute stages in parallel where possible."""
        while True:
            ready = self._get_ready_stages()
            
            if not ready:
                if len(self._results) == len(self._stages):
                    break
                remaining = set(self._stages.keys()) - set(self._results.keys())
                if remaining:
                    for name in remaining:
                        self._results[name] = StageResult(
                            stage_name=name,
                            status=StageStatus.SKIPPED,
                            error="Skipped due to failed dependencies",
                        )
                break
            
            batch = ready[:self.max_parallel]
            tasks = [
                self._execute_stage(name, context)
                for name in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            async with self._lock:
                for name, result in zip(batch, results):
                    if isinstance(result, Exception):
                        self._results[name] = StageResult(
                            stage_name=name,
                            status=StageStatus.FAILED,
                            error=str(result),
                        )
                    else:
                        self._results[name] = result
    
    def _topological_sort(self) -> List[str]:
        """Sort stages based on dependencies."""
        visited = set()
        order = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            
            config = self._stages.get(name)
            if config:
                for dep in config.dependencies:
                    visit(dep)
            
            order.append(name)
        
        for name in self._stages:
            visit(name)
        
        return order
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of execution results."""
        completed = sum(
            1 for r in self._results.values() 
            if r.status == StageStatus.COMPLETED
        )
        failed = sum(
            1 for r in self._results.values() 
            if r.status == StageStatus.FAILED
        )
        
        total_time = sum(
            r.execution_time for r in self._results.values()
        )
        
        return {
            "total_stages": len(self._stages),
            "completed": completed,
            "failed": failed,
            "total_execution_time": total_time,
        }
