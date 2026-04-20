# SDLC LangChain Document Generator

A comprehensive LangChain-based system for generating complete Software Development Life Cycle (SDLC) documentation.

## Features

- **Multiple LLM Providers**: OpenAI, Anthropic Claude, Azure OpenAI, Ollama (local)
- **Memory & History**: Conversation memory across stages
- **Streaming Output**: Real-time token streaming with Rich console
- **Parallel Execution**: Run independent stages concurrently
- **10 SDLC Stages**: Complete coverage from requirements to documentation
- **Real-World Problem Statements**: Comprehensive list of [10 practical use cases](./PROBLEM_STATEMENTS.md) for application.

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Usage
```bash
# Run with OpenAI (default)
python main.py

# Run with specific provider
python main.py --provider anthropic --model claude-3-opus-20240229

# Run specific stages
python main.py --stages requirements,architecture,database

# Interactive mode
python main.py --interactive
```

### Command Line Options
| Option | Description |
| --- | --- |
| --provider | LLM provider (openai, anthropic, azure, ollama) |
| --model | Model name to use |
| --mode | Execution mode (sequential, parallel, hybrid) |
| --stages | Comma-separated stages to run |
| --interactive | Run in interactive mode |
| --no-stream | Disable streaming output |

## SDLC Stages
1. **Requirements** - Requirements extraction and user stories
2. **Architecture** - System architecture design
3. **Database** - Database schema design
4. **API** - API design and OpenAPI specs
5. **Security** - Security architecture
6. **Implementation** - Implementation planning
7. **Testing** - Test strategy and plans
8. **DevOps** - CI/CD pipeline design
9. **Monitoring** - Observability strategy
10. **Documentation** - Technical docs and runbooks

## Output
Generated documents are saved to `output/{project_name}/`:
- Individual stage documents (Markdown)
- Combined SDD document
- JSON export with metadata

## Project Structure
```
sdlc_langchain/
├── main.py              # Entry point
├── config.py            # Configuration
├── chains/              # SDLC chain implementations
├── prompts/             # Prompt templates
├── models/              # Data models
├── providers/           # LLM providers
├── memory/              # Memory management
├── streaming/           # Streaming handlers
├── execution/           # Parallel execution
├── utils/               # Utilities
└── output/              # Generated documents
```

## License
MIT
