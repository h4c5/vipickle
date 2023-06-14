"""Nox configuration file."""
import nox


@nox.session
def tests(session):
    """Unit tests."""
    session.install(".[test]")
    session.run("pytest")


@nox.session
def bandit(session):
    """Bandit static security analysis."""
    session.install(".[test]")
    session.run("bandit", "-r", "src", "-c", "pyproject.toml")
