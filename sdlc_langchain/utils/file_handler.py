import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config import app_config


class FileHandler:
    """Handle file operations for SDLC outputs."""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.base_dir = Path(app_config.output_dir) / self._sanitize_name(project_name)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize project name for file system."""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def save_stage_output(self, stage: str, content: str, substage: str = None) -> Path:
        """Save output from an SDLC stage."""
        stage_dir = self.base_dir / stage
        stage_dir.mkdir(exist_ok=True)
        
        filename = f"{substage or stage}_{self.timestamp}.md"
        filepath = stage_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def save_full_output(self, outputs: Dict[str, Any]) -> Path:
        """Save complete SDLC output as JSON."""
        filepath = self.base_dir / f"complete_sdd_{self.timestamp}.json"
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2, default=str)
        
        return filepath
    
    def save_combined_document(self, outputs: Dict[str, Any]) -> Path:
        """Save combined SDD as single markdown document."""
        filepath = self.base_dir / f"SDD_{self.project_name}_{self.timestamp}.md"
        
        sections = [
            f"# System Design Document: {self.project_name}",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "---",
            ""
        ]
        
        stage_titles = {
            "requirements": "Requirements Analysis",
            "architecture": "System Architecture",
            "database": "Database Design",
            "api": "API Design",
            "security": "Security Architecture",
            "implementation": "Implementation Plan",
            "testing": "Testing Strategy",
            "devops": "DevOps & CI/CD",
            "monitoring": "Monitoring & Observability",
            "documentation": "Documentation",
        }
        
        for stage, title in stage_titles.items():
            if stage in outputs and outputs[stage]:
                sections.append(f"# {title}")
                sections.append("")
                sections.append(str(outputs[stage]))
                sections.append("")
                sections.append("---")
                sections.append("")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(sections))
        
        return filepath
