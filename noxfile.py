import nox


py_versions = ["3.7.4", "3.8.0", "3.8.1"]


@nox.session(python=py_versions, reuse_venv=True)
def blacken(session):
    session.install("black")
    session.run("black", "fables", "tests", "noxfile.py", "setup.py")


@nox.session(python=py_versions, reuse_venv=True)
def test(session):
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run("pytest", "--cov=fables")


@nox.session(python=py_versions, reuse_venv=True)
def lint(session):
    session.install("flake8")
    session.run("flake8", "fables")
    session.run("flake8", "tests")


@nox.session(python=py_versions, reuse_venv=True)
def type_check(session):
    session.install("mypy")
    session.run("mypy", "--strict", "fables")
