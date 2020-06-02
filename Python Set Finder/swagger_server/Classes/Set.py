import typing
from abc import ABC, abstractmethod 
from typing import List

MIXCLOUD_SOURCE_NAME = "mixcloud"

class Set(ABC):
    def __init__(self, set_name: str, uploader: str, set_title: str, set_likes: int):
        self.set_name = set_name
        self.uploader = uploader
        self.source = None
        self.set_title = set_title
        self.set_likes = set_likes

    @abstractmethod
    def get_set_url(self): 
        pass
       
    def __repr__(self):
        return self.set_name

    def __lt__(self, other):
        return "-".join([self.source, self.uploader, self.set_name]) < "-".join([other.source, other.uploader, other.set_name])
    
    def __eq__(self, other):
        return "-".join([self.source, self.uploader, self.set_name]) == "-".join([other.source, other.uploader, other.set_name])

    
class MixCloudSet(Set):

    def __init__(self, set_name: str, uploader: str, set_title: str, set_likes: int):
        Set.__init__(self, set_name, uploader, set_title, set_likes)
        self.source = MIXCLOUD_SOURCE_NAME

    def get_set_url(self):
        return f"https://www.mixcloud.com/{self.uploader}/{self.set_name}"


class SetFactory:
    set_sources = {MIXCLOUD_SOURCE_NAME: MixCloudSet}
    
    @staticmethod
    def get_instance(set_source: str, set_name: str, uploader: str, set_title: str, set_likes: int) -> Set:
        return SetFactory.set_sources.get(set_source)(set_name, uploader, set_title, set_likes)

class SetsCounter:
    def __init__(self, sets: List[Set] = []):
        self.sets_to_append = sets
        self.sets_counter = {}

    def append_set(self, set_data: Set):
        self.sets_to_append.append(set_data)
    
    def append_sets(self, sets: List[Set]):
        self.sets_to_append.extend(sets)

    def get_most_comxmon_sets(self, max_sets: int):
        self._build_sets_counter()
        sets_details = list(self.sets_counter.values())
        sets_details.sort(key = lambda tup: tup[1])
        return [set_details[0] for set_details in sets_details[:max_sets]]

    def _build_sets_counter(self):
        for set_details in self.sets_to_append[:]:
            set_id = f"{set_details.source}-{set_details.uploader}-{set_details.set_name}"
            self._update_sets_counter(set_id, set_details)
            self.sets_to_append.remove(set_details)

    def _update_sets_counter(self, set_id, set_details):
        set_details_and_counter = self.sets_counter.get(set_id, (set_details, 0)) 
        updated_set_details_and_counter = (set_details_and_counter[0], set_details_and_counter[1] + 1)
        self.sets_counter[set_id] = updated_set_details_and_counter
        