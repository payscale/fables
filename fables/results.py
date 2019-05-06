"""
A `ParseResult` bundled object returned from visiting a node that is parsed
for tabular data.
"""

from dataclasses import dataclass
from typing import List, Optional

from fables.table import Table
from fables.errors import ParseError


@dataclass
class ParseResult:
    name: Optional[str]
    tables: List[Table]
    errors: List[ParseError]
