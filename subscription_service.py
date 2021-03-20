from typing import List
from subscription import Subscription
import dbHelper


def get_all_subscriptions() -> List[Subscription]:
    # последовательность полей в запросе должна быть такой же как последовательность полей в dataclass Subscription
    sql = 'SELECT Id, ChatId, Text, RegionCode FROM Subscriptions'
    rows = dbHelper.select(sql)
    return [Subscription(*r) for r in rows] if rows else []

def create_subscriprion(chat_id: int, text: str, region_code: int) -> Subscription:
    subscription = Subscription(chat_id, text, region_code)
    subscription.id = subscription.get_subscription_hash()
    sql = 'INSERT INTO Subscriptions (Id, ChatId, Text, RegionCode) VALUES (?, ?, ?, ?)'
    insert_values = (subscription.id, subscription.chat_id, subscription.text, subscription.region_code)
    dbHelper.insert_or_update(sql, insert_values)
    return subscription

def get_region_codes() -> List[int]:
    sql = 'SELECT DISTINCT RegionCode FROM Subscriptions'
    rows = dbHelper.select(sql)
    return [*r[0] for r in rows]