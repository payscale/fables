import nox


py_versions = ["3.7.4", "3.8.0", "3.8.1"]


@nox.session(python=py_versions, reuse_venv=True)
def blacken(session):
    # pinning black version until unstable formatting is fixed
    # https://github.com/psf/black/issues/1629
    session.install("black==19.10b0")
    session.run("black", "fables", "tests", "noxfile.py", "setup.py")


@nox.session(python=py_versions, reuse_venv=True)
def lint(session):
    session.install("flake8")
    session.run("flake8", "fables")
    session.run("flake8", "tests")


@nox.session(python=py_versions, reuse_venv=True)
def type_check(session):
    session.install("mypy")
    session.run("mypy", "--strict", "fables")


@nox.session(python=py_versions, reuse_venv=True)
@nox.parametrize("pandas", ["0.25.1", "1.0.1"])
def test(session, pandas):
    session.install("-r", "requirements.txt")
    session.install(f"pandas=={pandas}")
    session.install("-e", ".")
    session.run("pytest", "--cov=fables")
