from typing import Optional, Dict
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table


class RichConsoleStreamer:
    """Rich console streamer with live updates."""
    
    def __init__(
        self,
        show_tokens: bool = True,
        color_output: bool = True,
    ):
        self.console = Console(force_terminal=True)
        self.show_tokens = show_tokens
        self.color_output = color_output
        
        self._current_stage: Optional[str] = None
        self._buffer = ""
        self._token_count = 0
        self._start_time: Optional[datetime] = None
        self._live: Optional[Live] = None
        self._stage_stats: Dict[str, Dict] = {}
    
    def _create_panel(self) -> Panel:
        """Create a panel showing current output."""
        display_text = self._buffer
        if len(display_text) > 2000:
            display_text = "..." + display_text[-2000:]
        
        elapsed = 0
        tps = 0
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            if elapsed > 0:
                tps = self._token_count / elapsed
        
        footer = f"Tokens: {self._token_count} | Speed: {tps:.1f} tok/s | Time: {elapsed:.1f}s"
        
        return Panel(
            Text(display_text) if self.show_tokens else Text("Generating..."),
            title=f"[bold blue]{self._current_stage}[/bold blue]",
            subtitle=footer,
            border_style="blue",
        )
    
    def start_stage(self, stage_name: str):
        """Start streaming for a stage."""
        self._current_stage = stage_name
        self._buffer = ""
        self._token_count = 0
        self._start_time = datetime.now()
        
        self.console.print()
        self.console.rule(f"[bold]{stage_name}[/bold]", style="blue")
        
        if self.show_tokens:
            self._live = Live(
                self._create_panel(),
                console=self.console,
                refresh_per_second=4,
            )
            self._live.start()
    
    def write_token(self, token: str):
        """Write a token during streaming."""
        self._buffer += token
        self._token_count += 1
        
        if self._live and self.show_tokens:
            self._live.update(self._create_panel())
    
    def complete_stage(self):
        """Complete the current stage."""
        if self._live:
            self._live.stop()
            self._live = None
        
        elapsed = (datetime.now() - self._start_time).total_seconds() if self._start_time else 0
        self._stage_stats[self._current_stage] = {
            "tokens": self._token_count,
            "time": elapsed,
            "tps": self._token_count / elapsed if elapsed > 0 else 0,
        }
        
        self.console.print(
            f"[green]✓[/green] {self._current_stage} completed: "
            f"{self._token_count} tokens in {elapsed:.1f}s"
        )
    
    def show_summary(self):
        """Show summary of all stages."""
        table = Table(title="Stage Execution Summary")
        table.add_column("Stage", style="cyan")
        table.add_column("Tokens", justify="right")
        table.add_column("Time (s)", justify="right")
        table.add_column("Speed (tok/s)", justify="right")
        
        total_tokens = 0
        total_time = 0
        
        for stage, stats in self._stage_stats.items():
            table.add_row(
                stage,
                str(stats["tokens"]),
                f"{stats['time']:.1f}",
                f"{stats['tps']:.1f}",
            )
            total_tokens += stats["tokens"]
            total_time += stats["time"]
        
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total_tokens}[/bold]",
            f"[bold]{total_time:.1f}[/bold]",
            f"[bold]{total_tokens/total_time:.1f}[/bold]" if total_time > 0 else "0",
            style="bold",
        )
        
        self.console.print()
        self.console.print(table)
    
    def error(self, stage_name: str, error: Exception):
        """Display an error."""
        if self._live:
            self._live.stop()
            self._live = None
        
        self.console.print(
            f"[red]✗[/red] Error in {stage_name}: {str(error)}"
        )
