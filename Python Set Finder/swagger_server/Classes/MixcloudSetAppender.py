from .SetsDataUploader import SetsDataUploader

class MixcloudSetAppender():
    def __init__(self, sets_data_uploader: SetsDataUploader):
        self.sets_data_uploader = sets_data_uploader

    def appendSet(self, url: str) -> bool:
        url_parts = url.strip("/").split("/")
        set_appended = self.sets_data_uploader.upload_set_data(set_name = url_parts[-1], set_uploader = url_parts[-2], set_source = "mixcloud", set_url = url)
        return set_appended
