from dataclasses import dataclass

@dataclass
class Blackout:
    # region_number: int
    district: str
    place: str
    address: str
    begin_date: str
    end_date: str
