from dataclasses import dataclass
import hashlib

@dataclass
class Blackout:
    region_code: int
    district: str
    place: str
    address: str = ''
    begin_date: str
    end_date: str


    def get_blackout_hash(self) -> str:
        fields = [blackout.region_code, blackout.district, blackout.place, blackout.address, blackout.begin_date, blackout.end_date]
        unique_str = ''.join(fields)
        return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()