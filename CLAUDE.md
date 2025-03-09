# Code Analysis Agent - Commands & Guidelines

## Commands
- **Run Server**: `python run.py` or `./scripts/run_server.sh`
- **Run All Tests**: `pytest` or `./scripts/run_tests.sh`
- **Run Single Test**: `pytest tests/test_file.py::test_function_name`
- **Coverage Report**: `pytest --cov=src tests/`
- **Lint Check**: `flake8 src/ tests/`
- **Format Code**: `black src/ tests/`
- **Sort Imports**: `isort src/ tests/`
- **Type Check**: `mypy src/`
- **Security Scan**: `bandit -r src/`

## Style Guidelines
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Formatting**: 100 char line length, follow PEP 8, use Black for auto-formatting
- **Imports**: Group standard library, third-party, and local imports; use isort
- **Documentation**: Google-style docstrings for all public functions/classes
- **Type Hints**: Use them consistently throughout the codebase
- **Error Handling**: Use specific exceptions, avoid bare except, log errors with context
- **Testing**: Write pytest unit tests with ≥90% coverage, mock external dependencies
- **Security**: Use environment variables for secrets, validate all inputs, keep dependencies updated
- **Architecture**: Follow src/tests/docs structure with clean separation of concerns