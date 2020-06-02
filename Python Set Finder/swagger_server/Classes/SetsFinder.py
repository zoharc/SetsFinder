from .TracksDao import TracksDao
from collections import Counter
from typing import List
from .SetAndOccurences import SetAndOccurences
from .SetsCounter import SetsCounter
import typing

class SetsFinder:

    def __init__(self, tracks_dao: TracksDao):
        self.tracks_dao: TracksDao = tracks_dao

    def find_sets_matching(self, artists_names: List[str], max_sets: int = 10) -> List[SetAndOccurences]:
        sets = self.tracks_dao.find_sets_matching(artists_names)
        return SetsCounter(sets).get_most_common_sets(max_sets)
