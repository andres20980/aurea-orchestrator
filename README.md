# aurea-orchestrator
Automated Unified Reasoning &amp; Execution Agents

## Installation

```bash
pip install -e .
```

## Usage

The `aurea` CLI tool provides the following commands:

### Submit a Request
```bash
aurea request "Deploy microservice" --priority high --agent deployment-agent
```

### Check Status
```bash
# Check specific request
aurea status req-12345

# Check all requests
aurea status --all
```

### Approve a Request
```bash
aurea approve req-12345 --comment "Looks good to deploy"
```

### Run Simulation
```bash
aurea simulate "load-test" --duration 120 --agents 5 --verbose
```

### View Metrics
```bash
aurea metrics --range 7d --export json
```

## Autocomplete

Install shell completion for your shell:

```bash
# Bash
aurea --install-completion bash

# Zsh
aurea --install-completion zsh

# Fish
aurea --install-completion fish
```

## Help

Get help for any command:

```bash
aurea --help
aurea request --help
aurea status --help
aurea approve --help
aurea simulate --help
aurea metrics --help
```
