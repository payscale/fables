import fables


tree = fables.detect(io='sample_data')
print(tree)

for parse_result in fables.parse(tree=tree):
    errors = parse_result.errors
    tables = parse_result.tables

    if errors:
        for error in errors:
            print(error)
    if tables:
        for table in tables:
            print(table)
