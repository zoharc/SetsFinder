import pymysql
import logging
import datetime

from .Track import Track
from .Set import Set, SetFactory
from typing import List
from .TracksDao import TracksDao
from flask import current_app

class MySqlTracksDao(TracksDao):
    def __init__(self):
            host = current_app.config["MYSQL_HOST_URI"]
            user = current_app.config["MYSQL_USER"]
            password = current_app.config["MYSQL_PASSWD"]

            self.connection = pymysql.connect(host, port=3306, user=user, passwd=password, db='sets')    
            self.cursor = self.connection.cursor()

    def insert_to_db(self, tracks: List[Track]):
        values = [self.get_track_values_for_db(track) for track in tracks]
        query = f"""INSERT INTO Tracks (set_name, set_title, set_source, set_likes, uploader, artist_name, song_name) VALUES {", ".join(values)};"""
        self.cursor.execute(query)
        self.connection.commit()

    def get_track_values_for_db(self, track: Track) -> str:
        query_values =  "(" + f'''
        "{track.set_details.set_name.lower()}", 
        "{track.set_details.set_title.lower()}", 
        "{track.set_details.source.lower()}", 
        "{track.set_details.set_likes}", 
        "{track.set_details.uploader.lower()}", 
        "{track.artist_name.lower()}", 
        "{track.song_name.lower()}"''' + ")"
        return query_values

    def find_sets_matching(self, artists: List[str]) -> List[Set]:
        sets = []
        artists_param = "(" + ",".join(['"' + artist + '"' for artist in artists]) + ")"
        query = f"""SELECT set_source, set_name, uploader, set_title, set_likes FROM Tracks where artist_name IN {artists_param};"""                         
        self.cursor.execute(query)
        rs = self.cursor.fetchall()
        for line in rs:
            set_data_valuess = list(line) #converting set to list
            set_data = SetFactory.get_instance(set_data_valuess[0], set_data_valuess[1], set_data_valuess[2], set_data_valuess[3], set_data_valuess[4])
            sets.append(set_data)
        return sets
    
    def get_track_list(self, set_name: str, uploader: str, source: str) -> List[Track]:
        tracks = []

        query = f"""SELECT set_source, set_name, uploader, set_title, set_likes, song_name, artist_name FROM Tracks where set_name="{set_name}" AND uploader="{uploader}" AND set_source="{source}";"""                         
        self.cursor.execute(query)
        rs = self.cursor.fetchall()
        for line in rs:
            set_data_valuess = list(line) #converting set to list
            set_data = SetFactory.get_instance(set_data_valuess[0], set_data_valuess[1], set_data_valuess[2], set_data_valuess[3], set_data_valuess[4])
            track = Track(set_data_valuess[6], set_data_valuess[5], set_data)
            tracks.append(track)
        return tracks

    def set_exists_in_db(self, set_name: str, uploader: str, source: str) -> bool:
        query = f"""SELECT EXISTS(SELECT * FROM Tracks WHERE set_name="{set_name}" AND uploader="{uploader}" AND set_source="{source}")"""
        self.cursor.execute(query)
        return self.cursor.fetchone()[0] == 1


