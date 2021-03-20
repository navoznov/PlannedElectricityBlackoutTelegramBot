from dataclasses import dataclass
import hashlib

@dataclass
class Blackout:
    region_code: int
    district: str
    place: str
    address: str
    begin_date: str
    end_date: str
    id: str = ''


    def get_blackout_hash(self) -> str:
        fields = [str(x) for x in [self.region_code, self.district, self.place, self.address, self.begin_date, self.end_date]]
        unique_str = ''.join(fields)
        return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()