# Fables - (F)ile T(ables)

[![CircleCI](https://circleci.com/gh/payscale/fables.svg?style=svg)](https://circleci.com/gh/payscale/fables)
[![Apache2.0License](https://img.shields.io/hexpm/l/plug.svg)](LICENSE)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## For users:

Parse the tabular data in the input file:

```
import fables

for parse_result in fables.parse('myfile.zip'):
    for table in parse_result.tables:
        print(table.name)
        print(table.df.head())
    for error in parse_result.errors:
        print(error.message)
```

Inspect the contents of the input file:

```
node = fables.detect('myfile.zip')
print(node.name)
print(node.mimetype)

for child in node.children:
    print(child.name)
    print(child.mimetype)
```

Note if you've already discovered the input tree from `detect()`,
you can pass it into `parse()`:

```
parse_results = parse(tree=node)
```

Handling encrypted `zip`, `xlsx`, `xlsb`, and `xls` files:

```
node = fables.detect('encrypted.xlsx')
assert node.encrypted
node.add_password('encrypted.xlsx', 'fables')
assert not node.encrypted
```

You can also supply a passwords dictionary (filename -> password)
into detect and parse:

```
node = fables.detect(
    'encrypted.zip',
    passwords={
        'encrypted.zip': 'fables',
        # an encrypted file inside the zip
        'encrypted.xlsx': 'foobles',
    }
)
# and/or parse
parse_results = fables.parse(
    'sub_dir',
    passwords={
        'sub_dir/encrypted.xlsx': 'fables',
        'sub_dir/encrypted.xls': 'foobles',
    },
)
```

## Seeing is believing:

Clone the repository & run the example file by executing the example.py script with the following command:

```
python3 example.py
```

### Installation

The python library [`python-magic`](https://github.com/ahupp/python-magic)
requires additional system dependencies. There are installation instructions
there, but here are recommended routes to try:

- on OSX: `brew install libmagic`.

- on Windows: [this](https://pypi.org/project/python-magic-bin/)
  `pip install python-magic-bin` will install a built version using
  ctypes to access the libmagic file type identification library.

Then `pip install -r requirements.txt` should do the trick.

## For contributors:

### Tests

- all tests: `pytest`
  - coverage: `pytest --cov=fables tests`
- integration: `pytest tests/integration`
  - coverage: `pytest --cov=fables tests/integration`
- unit: `pytest tests/unit`
  - coverage: `pytest --cov=fables tests/unit`

Note all the coverage statistics are for statements.

### Type checking with mypy

- `mypy fables`

### Linting

- We enforce flake8:
  - `flake8 .`

### Run test, type checking, and linter all at once

- `nox`
