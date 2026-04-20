"""
Enhanced SDLC LangChain Orchestrator
====================================

Features:
- Multiple LLM providers (OpenAI, Anthropic, Azure, Ollama)
- Memory and conversation history
- Streaming output
- Parallel execution

Usage:
    python main.py --provider openai --mode sequential
    python main.py --interactive
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from config import (
    llm_config, execution_config,
    LLMProvider, ExecutionMode,
)
from models.project_context import ProjectContext, CloudProvider, DatabaseType
from providers.provider_factory import LLMProviderFactory
from memory.conversation_memory import ConversationMemoryManager
from memory.project_memory import ProjectMemory
from streaming.console_streamer import RichConsoleStreamer
from execution.parallel_executor import ParallelExecutor, StageStatus
from chains import (
    RequirementsChain,
    ArchitectureChain,
    DatabaseChain,
    APIChain,
    SecurityChain,
    ImplementationChain,
    TestingChain,
    DevOpsChain,
    MonitoringChain,
    DocumentationChain,
)
from utils.file_handler import FileHandler


console = Console()


class SDLCOrchestrator:
    """Main orchestrator for SDLC documentation generation."""
    
    def __init__(
        self,
        context: ProjectContext,
        provider: LLMProvider = None,
        execution_mode: ExecutionMode = None,
        enable_memory: bool = True,
        enable_streaming: bool = True,
    ):
        self.context = context
        self.enable_memory = enable_memory
        self.enable_streaming = enable_streaming
        self.execution_mode = execution_mode or execution_config.mode
        
        # Initialize LLM provider
        self.provider = LLMProviderFactory.create(
            provider=provider or llm_config.provider,
            streaming=enable_streaming,
        )
        
        # Initialize memory systems
        self.project_memory = ProjectMemory(context)
        self.conversation_memory = ConversationMemoryManager(
            project_id=self.project_memory.project_id,
        )
        
        # Initialize streaming
        self.streamer = RichConsoleStreamer() if enable_streaming else None
        
        # File handler
        self.file_handler = FileHandler(context.project_name)
        
        # Initialize chains
        self._init_chains()
        
        # Results storage
        self.results: Dict[str, Any] = {}
    
    def _init_chains(self):
        """Initialize all SDLC chains."""
        chain_kwargs = {
            "provider": self.provider,
            "conversation_memory": self.conversation_memory if self.enable_memory else None,
            "project_memory": self.project_memory if self.enable_memory else None,
            "enable_streaming": self.enable_streaming,
        }
        
        self.chains = {
            "requirements": RequirementsChain(**chain_kwargs),
            "architecture": ArchitectureChain(**chain_kwargs),
            "database": DatabaseChain(**chain_kwargs),
            "api": APIChain(**chain_kwargs),
            "security": SecurityChain(**chain_kwargs),
            "implementation": ImplementationChain(**chain_kwargs),
            "testing": TestingChain(**chain_kwargs),
            "devops": DevOpsChain(**chain_kwargs),
            "monitoring": MonitoringChain(**chain_kwargs),
            "documentation": DocumentationChain(**chain_kwargs),
        }
    
    def run_stage(self, stage_name: str) -> str:
        """Run a single stage."""
        if self.streamer:
            self.streamer.start_stage(stage_name)
        
        chain = self.chains[stage_name]
        
        # Build input based on stage
        input_data = {"project_context": self.context.to_context_string()}
        
        # Add stage-specific inputs
        if stage_name == "requirements":
            input_data["business_requirements"] = self.context.business_requirements
        elif stage_name == "architecture":
            input_data["requirements_summary"] = self.results.get("requirements", "")[:2000]
        elif stage_name == "database":
            input_data["architecture_summary"] = self.results.get("architecture", "")[:2000]
            input_data["data_requirements"] = f"Features: {', '.join(self.context.features)}"
        elif stage_name == "api":
            input_data["architecture_summary"] = self.results.get("architecture", "")[:2000]
            input_data["service_name"] = self.context.project_name
        elif stage_name == "security":
            input_data["architecture_summary"] = self.results.get("architecture", "")[:2000]
            input_data["compliance_requirements"] = ", ".join(self.context.compliance_requirements)
        elif stage_name == "testing":
            input_data["features_to_test"] = ", ".join(self.context.features)
            input_data["requirements_reference"] = self.results.get("requirements", "")[:1000]
        elif stage_name == "devops":
            input_data["source_control"] = "GitHub"
            input_data["deployment_target"] = "Kubernetes"
            input_data["environments"] = "dev, staging, production"
        elif stage_name == "monitoring":
            input_data["architecture_summary"] = self.results.get("architecture", "")[:2000]
            input_data["sla_requirements"] = "99.9% availability"
        elif stage_name == "documentation":
            input_data["component_name"] = self.context.project_name
            input_data["component_purpose"] = self.context.project_description
            input_data["technical_details"] = self.results.get("architecture", "")[:2000]
        
        result = chain.invoke(input_data)
        self.results[stage_name] = result
        
        if self.streamer:
            self.streamer.complete_stage()
        
        return result
    
    def run(self, stages: List[str] = None) -> Dict[str, Any]:
        """Run the pipeline."""
        all_stages = list(self.chains.keys())
        stages = stages or all_stages
        
        console.print(Panel.fit(
            f"[bold blue]SDLC Document Generator[/bold blue]\n"
            f"Project: {self.context.project_name}\n"
            f"Provider: {self.provider.get_model_info()['provider']}\n"
            f"Model: {self.provider.model_name}\n"
            f"Mode: {self.execution_mode.value}",
            title="Starting Pipeline"
        ))
        
        start_time = datetime.now()
        
        # Execute stages based on mode
        stage_order = [s for s in all_stages if s in stages]
        
        for stage in stage_order:
            try:
                console.print(f"\n[yellow]▶[/yellow] Running: {stage}...")
                self.run_stage(stage)
                console.print(f"[green]✓[/green] Completed: {stage}")
            except Exception as e:
                console.print(f"[red]✗[/red] Error in {stage}: {str(e)}")
                if self.execution_mode == ExecutionMode.SEQUENTIAL:
                    break
        
        # Save outputs
        self._save_outputs()
        
        elapsed = datetime.now() - start_time
        
        # Show summary
        if self.streamer:
            self.streamer.show_summary()
        
        console.print(Panel.fit(
            f"[bold green]Pipeline Complete![/bold green]\n\n"
            f"✓ Stages completed: {len(self.results)}\n"
            f"⏱ Total Time: {elapsed.seconds // 60}m {elapsed.seconds % 60}s\n\n"
            f"📁 Output: {self.file_handler.base_dir}",
            title="Summary"
        ))
        
        return self.results
    
    def _save_outputs(self):
        """Save all outputs."""
        for stage_name, content in self.results.items():
            self.file_handler.save_stage_output(stage_name, content, stage_name)
        
        self.file_handler.save_combined_document(self.results)
        self.file_handler.save_full_output({
            "project": self.context.model_dump(),
            "outputs": self.results,
            "stats": self.project_memory.get_execution_stats(),
        })
    
    def run_interactive(self):
        """Run in interactive mode."""
        console.print(Panel(
            Markdown(f"""
## Interactive SDLC Document Generator

**Project:** {self.context.project_name}

### Available Stages:
1. requirements
2. architecture
3. database
4. api
5. security
6. implementation
7. testing
8. devops
9. monitoring
10. documentation
            """),
            title="Welcome"
        ))
        
        all_stages = list(self.chains.keys())
        
        selection = Prompt.ask(
            "\nEnter stages (comma-separated) or 'all'",
            default="all"
        )
        
        if selection.lower() == "all":
            stages = all_stages
        else:
            stages = [s.strip() for s in selection.split(",")]
        
        if not Confirm.ask(f"Run stages: {', '.join(stages)}?"):
            console.print("Cancelled.")
            return {}
        
        return self.run(stages)


def create_sample_context() -> ProjectContext:
    """Create a sample project context."""
    return ProjectContext(
        project_name="E-Commerce Platform",
        project_description="A modern e-commerce platform with microservices architecture.",
        business_domain="E-commerce / Retail",
        
        tech_stack=["Python", "FastAPI", "React", "PostgreSQL", "Redis", "Kubernetes"],
        programming_languages=["Python", "TypeScript"],
        frameworks=["FastAPI", "React", "SQLAlchemy"],
        cloud_provider=CloudProvider.AWS,
        database_types=[DatabaseType.POSTGRESQL, DatabaseType.REDIS],
        
        expected_users=50000,
        expected_requests_per_second=500,
        data_volume_gb=500,
        
        features=[
            "User Authentication",
            "Product Catalog",
            "Shopping Cart",
            "Order Processing",
            "Payment Integration",
        ],
        
        user_roles=["Customer", "Seller", "Admin"],
        integrations=["Stripe", "SendGrid", "AWS S3"],
        compliance_requirements=["GDPR", "PCI-DSS"],
        security_level="High",
        team_size=8,
        
        business_requirements="""
        Multi-vendor marketplace with real-time inventory,
        mobile-responsive design, and advanced search.
        """
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="SDLC Document Generator")
    
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "anthropic", "azure", "ollama"],
        default="openai",
        help="LLM provider"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Model name"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["sequential", "parallel", "hybrid"],
        default="sequential",
        help="Execution mode"
    )
    
    parser.add_argument(
        "--stages",
        type=str,
        help="Comma-separated stages to run"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Check API key
    if args.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        console.print("Set it with: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    provider_map = {
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC,
        "azure": LLMProvider.AZURE_OPENAI,
        "ollama": LLMProvider.OLLAMA,
    }
    
    mode_map = {
        "sequential": ExecutionMode.SEQUENTIAL,
        "parallel": ExecutionMode.PARALLEL,
        "hybrid": ExecutionMode.HYBRID,
    }
    
    if args.model:
        llm_config.model_name = args.model
    
    context = create_sample_context()
    
    orchestrator = SDLCOrchestrator(
        context=context,
        provider=provider_map.get(args.provider),
        execution_mode=mode_map.get(args.mode),
        enable_streaming=not args.no_stream,
    )
    
    if args.interactive:
        orchestrator.run_interactive()
    else:
        stages = None
        if args.stages:
            stages = [s.strip() for s in args.stages.split(",")]
        orchestrator.run(stages)
    
    console.print("\n[bold green]✓ Complete![/bold green]")


if __name__ == "__main__":
    main()
