import csv
import logging
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Plant:
    id: str
    name: str
    scientific_name: str
    o2_data: str
    co2_data: str
    description: str
    rating: float

    @property
    def search_text(self) -> str:
        return f"{self.name.lower()} {self.scientific_name.lower()}"


class DataManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.plants: List[Plant] = []
        self.load_data()

    def load_data(self):
        self.plants = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        desc = row.get('Short Description of Plant') or row.get(
                            'Short Description of the plant') or "No description available"

                        plant = Plant(
                            id=str(row['Plant ID']),
                            name=row['Plant Name'],
                            scientific_name=row['Plant Scientific Name'],
                            o2_data=row['Plant O2 Release Data'],
                            co2_data=row['Plant CO Absorb Data'],
                            description=desc,
                            rating=float(row['Recommendation Rating out of 5'])
                        )
                        self.plants.append(plant)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping malformed row: {row} -> {e}")
            logger.info(f"Loaded {len(self.plants)} plants.")
        except FileNotFoundError:
            logger.error(f"File not found: {self.filepath}")

    def get_top_10(self) -> List[Plant]:
        return sorted(self.plants, key=lambda p: (-p.rating, p.name))[:10]

    def get_all_sorted(self, by_rating: bool = False) -> List[Plant]:
        key = (lambda p: (-p.rating, p.name)) if by_rating else (lambda p: p.name)
        return sorted(self.plants, key=key)

    def search(self, query: str) -> List[Plant]:
        q = query.lower().strip()
        if not q:
            return self.get_top_10()
        return [p for p in self.plants if q in p.search_text]

    def search_all(self, query: str) -> List[Plant]:
        q = query.lower().strip()
        if not q:
            return self.get_all_sorted()
        return [p for p in self.plants if q in p.search_text]