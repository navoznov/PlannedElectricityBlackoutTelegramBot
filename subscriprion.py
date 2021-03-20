from dataclasses import dataclass

@dataclass
class Subscription:
    id: int
    chat_id: int
    text: str
    region_code: int