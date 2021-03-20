from dataclasses import dataclass
import hashlib

@dataclass
class Subscription:
    chat_id: int
    text: str
    region_code: int
    id: str = ''

    def get_subscription_hash(self) -> str:
        fields = [str(x) for x in [self.chat_id, self.text, self.region_code]]
        unique_str = ''.join(fields)
        return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()