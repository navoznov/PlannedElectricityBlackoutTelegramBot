from typing import List
from subscriprion import Subscription
import dbHelper


def get_all_subscriptions() -> List[Subscription]:
    # последовательность полей в запросе должна быть такой же как последовательность полей в dataclass Subscription
    sql = 'SELECT Id, UserId, Text, RegionCode FROM Subscriptions'
    rows = dbHelper.select(sql)
    return [Subscription(*r) for r in rows] if rows else []


def get_subscription_hash(subscriprion: Subscription) -> str:
    fields = [subscriprion.chat_id, subscriprion.text, subscriprion.region_code]
    unique_str = ''.join(fields)
    return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()