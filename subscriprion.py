from dataclasses import dataclass
import hashlib

@dataclass
class Subscription:
    id: int = -1
    chat_id: int
    text: str
    region_code: int

    def get_subscription_hash(self) -> str:
        fields = [subscriprion.chat_id, subscriprion.text, subscriprion.region_code]
        unique_str = ''.join(fields)
        return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()