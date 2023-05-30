unit-tests:
	pytest tests

security-report:
	bandit -c pyproject.toml -r src/blackpickle

lint:
	black src tests
	ruff --fix src tests

doc-serve:
	mkdocs serve

doc-build:
	mkdocs build