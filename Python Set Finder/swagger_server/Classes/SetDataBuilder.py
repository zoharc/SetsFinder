from ..models.sets_and_occurrences_data import SetsAndOccurrencesData
from ..models.set_data import SetData
from .SetAndOccurences import SetAndOccurences
from typing import List

class SetDataBuilder:
    def build_from(self, sets: List[SetAndOccurences]) -> List[SetsAndOccurrencesData]:
        return [SetsAndOccurrencesData(
            set_data = SetData(set_and_occurences.set_data.set_name, 
                    set_and_occurences.set_data.source, 
                    set_and_occurences.set_data.get_set_url(), 
                    set_and_occurences.set_data.uploader, 
                    set_and_occurences.set_data.set_title),
            artists_occurrences = set_and_occurences.occurences) 
            for set_and_occurences in sets]