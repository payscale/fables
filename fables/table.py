"""
A `Table` is a dataframe, along with info about where it came from i.e.
the file's 'name' and 'sheet'.
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd  # type: ignore


@dataclass
class Table:
    df: pd.DataFrame
    name: Optional[str] = None
    sheet: Optional[str] = None

    def __str__(self) -> str:
        s = (
            f"{self.__class__.__name__}("
            + f"df=DataFrame(nrow={len(self.df)}, ncol={len(self.df.columns)}), "
            + f"name='{self.name}', "
            + f"sheet='{self.sheet}')"
        )
        return s.replace("'None'", "None")
