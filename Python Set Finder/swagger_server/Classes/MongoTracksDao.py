import pymongo
import json
import datetime
from collections import Counter
from typing import List
from collections import namedtuple
from .Track import Track
from .Set import Set, SetFactory
from flask import current_app
import time
from .TracksDao import TracksDao


class MongoTracksDao(TracksDao):
    def __init__(self):
        uri = current_app.config["MONGO_HOST_URI"]
        self.client = pymongo.MongoClient(uri)
        self.db = self.client['MixCloudSetsData']

        self.sets_collection = self.db["SetsContent"]
        self.artists_collection = self.db["Artists"]

    def insert_to_db(self, tracks: List[Track]):
        sets_json = MongoTracksDao.get_json_of_set_name_for_artists(tracks) 
        self.sets_collection.insert_many(sets_json)

        artists_json = MongoTracksDao.get_json_of_artists(tracks)
        self.artists_collection.insert_many(artists_json)

    def find_sets_matching(self, artists: List[str]) -> List[Set]:
        sets_records = self.sets_collection.find({"artist_name": { "$in": [str.lower(artist) for artist in artists]}})
        return [self.create_set_object(set_record) for set_record in sets_records]

    def set_exists_in_db(self, set_name: str, uploader: str, source: str) -> bool:
            self._set_in_db(set_name, uploader, source)

    def _set_in_db(self, set_name: str, uploader: str, source: str):
        results = self.sets_collection.find({"set_name": set_name, "uploader": uploader, "set_source": source}).limit(1).count(with_limit_and_skip=True)
        return results > 0

    def create_set_object(self, set_details: dict):
        # using set source to initialize the class correctly
        return SetFactory.get_instance(set_details["set_source"], set_details["set_name"], set_details["uploader"], set_details["set_title"])

    def get_track_list(self, set_name: str, uploader: str, source: str) -> List[Track]:
        raise NotImplementedError
            
    @staticmethod
    def get_json_of_set_name_for_artists(tracks: List[Track]): 
        return [MongoTracksDao.get_json_of_set_name_and_artist(track) for track in tracks]

    @staticmethod
    def get_json_of_set_name_and_artist(track: Track): 
        return {
            "set_name": track.set_details.set_name.lower(), 
            "set_title": track.set_details.set_title.lower(), 
            "set_source": track.set_details.source.lower(), 
            "uploader": track.set_details.uploader.lower(), 
            "artist_name": track.artist_name.lower(), 
            "song_name": track.song_name.lower(), 
            "date_created": datetime.datetime.now(),
            "date_updated": datetime.datetime.now()}

    @staticmethod
    def get_json_of_artists(tracks: List[Track]):
        artist_names = [track.artist_name for track in tracks]
        return [MongoTracksDao.get_json_of_artist(artist_name) for artist_name in artist_names]
    
    @staticmethod
    def get_json_of_artist(artist_name: str):
        return {"artist_name": artist_name.lower()}
