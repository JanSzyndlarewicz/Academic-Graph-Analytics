# How to start

1. Create `.env` file in the root directory and add the following variables:
```
SEMANTIC_SCHOLAR_API_KEY=your_api_key
NEO4J_USER=username
NEO4J_PASSWORD=password
```

2. Install requirements
```bash
pip install -r requirements.txt
```

# Pre-commit Hooks
This project uses `pre-commit` to ensure consistent formatting and quality checks.

## How to Enable Pre-commit
1. Install pre-commit
```bash
pip install pre-commit
```

2. Install pre-commit hooks
```bash
pre-commit install
```

### How to disable pre-commit
```bash
pre-commit uninstall
```
