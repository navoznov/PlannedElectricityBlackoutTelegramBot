from typing import List
from subscriprion import Subscription
import dbHelper


def get_all_subscriptions() -> List[Subscription]:
    # последовательность полей в запросе должна быть такой же как последовательность полей в dataclass Subscription
    sql = 'SELECT Id, UserId, Text, RegionCode FROM Subscriptions'
    rows = dbHelper.select(sql)
    return [Subscription(*r) for r in rows] if rows else []