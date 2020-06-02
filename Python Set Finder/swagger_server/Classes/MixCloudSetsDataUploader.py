from .ExtractTrackList import MixCloudTrackExtracter
from .TracksDao import TracksDao
import logging
import time 

class MixCloudSetsDataUploader:

    def __init__(self, extract_track_list: MixCloudTrackExtracter, tracks_dao: TracksDao):
        self.extract_track_list = extract_track_list
        self.tracks_dao = tracks_dao
    
    def upload_set_data(self, set_name: str, set_uploader: str) -> bool:
        need_to_handle_set = not self.tracks_dao.set_exists_in_db(set_name, set_uploader, source = "mixcloud")
        if (need_to_handle_set):
            logging.info(f"MixCloudSetsDataUploader - handling set data for {set_uploader}/{set_name}")
            try:
                tracks = self.extract_track_list.get_track_list(set_uploader, set_name)
                logging.info(f"MixCloudSetsDataUploader - extracted tracks for {set_uploader}/{set_name}")
                if tracks:
                    self.tracks_dao.insert_to_db(tracks)
                    logging.info(f"MixCloudSetsDataUploader - inserted tracks to db for {set_uploader}/{set_name}")
                else:
                    logging.info(f"MixCloudSetsDataUploader - empty tracklist for {set_uploader}/{set_name}")

            except Exception as e:
                raise e
                #logging.info(f"MixCloudSetsDataUploader - got error {e} for {set_uploader}/{set_name}")
                #tracks = []
                


        return need_to_handle_set
        
    
    