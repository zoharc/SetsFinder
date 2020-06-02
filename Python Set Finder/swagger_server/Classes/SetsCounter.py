from typing import List
from .Set import Set
from .SetAndOccurences import SetAndOccurences

class SetsCounter:
    def __init__(self, sets: List[Set] = []):
        self.sets_to_append = sets
        self.sets_counter = {}

    def append_set(self, set_data: Set):
        self.sets_to_append.append(set_data)
    
    def append_sets(self, sets: List[Set]):
        self.sets_to_append.extend(sets)

    def get_most_common_sets(self, max_sets: int):
        self._build_sets_counter()
        sets_details = list(self.sets_counter.values())
        sets_details.sort(key = lambda tup: tup[1], reverse=True)
        return [SetAndOccurences(set_details[0], set_details[1]) for set_details in sets_details[:max_sets]]

    def _build_sets_counter(self):
        for set_details in self.sets_to_append[:]:
            set_id = f"{set_details.source}-{set_details.uploader}-{set_details.set_name}"
            self._update_sets_counter(set_id, set_details)
            self.sets_to_append.remove(set_details)

    def _update_sets_counter(self, set_id, set_details):
        set_details_and_counter = self.sets_counter.get(set_id, (set_details, 0)) 
        updated_set_details_and_counter = (set_details_and_counter[0], set_details_and_counter[1] + 1)
        self.sets_counter[set_id] = updated_set_details_and_counter