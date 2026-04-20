import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"


class MemoryType(str, Enum):
    """Memory storage types."""
    BUFFER = "buffer"
    SUMMARY = "summary"
    VECTOR = "vector"
    REDIS = "redis"
    PERSISTENT = "persistent"


class ExecutionMode(str, Enum):
    """Pipeline execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


@dataclass
class LLMConfig:
    """LLM Configuration settings."""
    provider: LLMProvider = LLMProvider.OPENAI
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.3
    max_tokens: int = 4096
    streaming: bool = True
    
    # Provider-specific settings
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    azure_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY")
    )
    azure_endpoint: Optional[str] = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    azure_deployment: Optional[str] = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    ollama_base_url: str = "http://localhost:11434"
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get configuration for the selected provider."""
        configs = {
            LLMProvider.OPENAI: {
                "api_key": self.openai_api_key,
                "model": self.model_name,
            },
            LLMProvider.ANTHROPIC: {
                "api_key": self.anthropic_api_key,
                "model": self.model_name,
            },
            LLMProvider.AZURE_OPENAI: {
                "api_key": self.azure_api_key,
                "azure_endpoint": self.azure_endpoint,
                "azure_deployment": self.azure_deployment,
            },
            LLMProvider.OLLAMA: {
                "base_url": self.ollama_base_url,
                "model": self.model_name,
            },
        }
        return configs.get(self.provider, {})


@dataclass
class MemoryConfig:
    """Memory configuration settings."""
    type: MemoryType = MemoryType.BUFFER
    max_token_limit: int = 4000
    
    # Redis settings
    redis_url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )
    redis_ttl: int = 86400  # 24 hours
    
    # Persistent memory
    persistence_path: str = "./memory/persistent"
    auto_save: bool = True


@dataclass
class ExecutionConfig:
    """Execution configuration settings."""
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_parallel_chains: int = 4
    timeout_per_stage: int = 300  # 5 minutes
    
    # Dependencies (stages that must complete before others)
    dependencies: Dict[str, List[str]] = field(default_factory=lambda: {
        "architecture": ["requirements"],
        "database": ["architecture"],
        "api": ["architecture"],
        "security": ["architecture"],
        "implementation": ["architecture", "database", "api"],
        "testing": ["implementation"],
        "devops": ["architecture"],
        "monitoring": ["architecture"],
        "documentation": ["implementation", "testing"],
    })


@dataclass
class StreamingConfig:
    """Streaming output configuration."""
    enabled: bool = True
    chunk_size: int = 20
    show_tokens: bool = True
    color_output: bool = True


@dataclass
class AppConfig:
    """Application configuration."""
    output_dir: str = "output"
    verbose: bool = True
    save_intermediate: bool = True
    log_level: str = "INFO"
    
    # Feature flags
    enable_memory: bool = True
    enable_streaming: bool = True
    enable_parallel: bool = True
    enable_caching: bool = True


# Global config instances
llm_config = LLMConfig()
memory_config = MemoryConfig()
execution_config = ExecutionConfig()
streaming_config = StreamingConfig()
app_config = AppConfig()


def load_config_from_env():
    """Load configuration from environment variables."""
    global llm_config, memory_config, execution_config, app_config
    
    # LLM Config
    if provider := os.getenv("LLM_PROVIDER"):
        llm_config.provider = LLMProvider(provider.lower())
    if model := os.getenv("LLM_MODEL"):
        llm_config.model_name = model
    if temp := os.getenv("LLM_TEMPERATURE"):
        llm_config.temperature = float(temp)
    if streaming := os.getenv("LLM_STREAMING"):
        llm_config.streaming = streaming.lower() == "true"
    
    # Execution Config
    if mode := os.getenv("EXECUTION_MODE"):
        execution_config.mode = ExecutionMode(mode.lower())
    
    # Memory Config
    if mem_type := os.getenv("MEMORY_TYPE"):
        memory_config.type = MemoryType(mem_type.lower())


# Load config on import
load_config_from_env()
