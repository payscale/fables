import setuptools


# Note: It would be nice to have a single source of truth for the version; (it exists here and in
# fables/__init__.py). Here is a nice reference of different ways this can be achieved:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = "1.1.0"


with open("README.md") as f:
    long_description = f.read()


setuptools.setup(
    name="fables",
    version=VERSION,
    description="(F)ile T(ables)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    packages=["fables"],
    url="https://github.com/payscale/fables",
    author="PayScale, Inc.",
    author_email="pypi@payscale.com",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        "pandas==0.25.1",
        "chardet==3.0.4",
        "python-magic==0.4.15",
        "xlrd==1.2.0",
        "msoffcrypto-tool==4.6.4",
        'python-magic-bin==0.4.14;platform_system=="Windows"',
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-mock"],
    zip_safe=True,
)
