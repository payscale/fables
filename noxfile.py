import nox


# @nox.session(python=["3.7"])
# def test(session):
#     session.install("pytest")
#     session.run("pytest")


@nox.session(python=["3.7"])
def lint(session):
    session.install("flake8")
    session.run("flake8", "fables")
    session.run("flake8", "tests")


@nox.session(python=["3.7"])
def type_check(session):
    session.install("mypy")
    session.run("mypy", "--strict", "fables")

