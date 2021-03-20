import hashlib
from blackout import Blackout


def get_blackout_hash(blackout: Blackout) -> str:
    fields = [blackout.region_code, blackout.district, blackout.place, blackout.address, blackout.begin_date, blackout.end_date]
    unique_str = ''.join(fields)
    return hashlib.md5(unique_str.encode(encoding='utf-8')).hexdigest()
