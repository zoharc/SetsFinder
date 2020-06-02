import typing
from abc import ABC, abstractmethod 
from typing import List
from .Track import Track
from .Set import Set

class TracksDao(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def insert_to_db(self, tracks: List[Track]):
        pass

    @abstractmethod
    def get_track_list(self, set_name: str, uploader: str, source: str) -> List[Track]:
        pass

    @abstractmethod
    def find_sets_matching(self, artists: List[str]) -> List[Set]:
        pass

    @abstractmethod
    def set_exists_in_db(self, set_name: str, uploader: str, source: str) -> bool:
        pass