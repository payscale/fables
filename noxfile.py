import nox


@nox.session(python=["3.7"], reuse_venv=True)
def test(session):
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run("pytest", "--cov=fables")


@nox.session(python=["3.7"], reuse_venv=True)
def lint(session):
    session.install("flake8")
    session.run("flake8", "fables")
    session.run("flake8", "tests")


@nox.session(python=["3.7"], reuse_venv=True)
def type_check(session):
    session.install("mypy")
    session.run("mypy", "--strict", "fables")

