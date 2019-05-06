import pandas as pd

from tests.context import fables


def test_table_str():
    df = pd.DataFrame(columns=['a', 'b'], data=[[1, 2], [3, 4], [5, 6]])
    table = fables.Table(df=df, name='test.csv', sheet=None)
    assert str(table) == "Table(df=DataFrame(nrow=3, ncol=2), name='test.csv', sheet=None)"

    df = pd.DataFrame(columns=['a', 'b', 'c'], data=[[1, 2, 3], [4, 5, 6]])
    table = fables.Table(df=df, name='test.xls', sheet='Sheet1')
    assert str(table) == "Table(df=DataFrame(nrow=2, ncol=3), name='test.xls', sheet='Sheet1')"
