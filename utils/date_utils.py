from datetime import datetime, date
from typing import Any

def parse_date(val: Any) -> date:
    if isinstance(val, date):
        return val
    return datetime.strptime(val, "%Y-%m-%d").date()