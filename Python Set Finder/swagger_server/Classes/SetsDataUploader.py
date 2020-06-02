from .MixCloudSetsDataUploader import MixCloudSetsDataUploader
import logging

class SetsDataUploader:

    def __init__(self, mixcloud_sets_data_uploader: MixCloudSetsDataUploader):
        self.mixcloud_sets_data_uploader = mixcloud_sets_data_uploader
    
    def upload_set_data(self, set_name: str, set_uploader: str, set_source: str, set_url: str):
        if set_source.lower() == "mixcloud":
            return self.mixcloud_sets_data_uploader.upload_set_data(set_name, set_uploader)   
        else:
            logging.error(f"SetsDataUploader - set source {set_source} is invalid for set url {set_url}")
            return False


class InvalidSetSourceException(Exception):
    """set source is invalid"""
    pass