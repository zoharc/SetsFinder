from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import requests
from urllib.parse import unquote
from .Track import Track
from .Set import MixCloudSet
from typing import List
from .TracksDao import TracksDao

import logging
from selenium.common.exceptions import NoSuchElementException

class MixCloudTrackExtracter:

    def __init__(self, tracks_dao: TracksDao):
        self.mixcloud_base_url = "https://www.mixcloud.com/"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        self.chromedriver_url = "/usr/bin/chromedriver"
        self.c_value = "6ajhk67gwsticap8vfoo797212rbx488"
        self.mixcloud_source = "Mixcloud"
        self.tracks_dao = tracks_dao
      
    def get_track_list(self, user_name, set_name) -> List[Track]:
        if (self.tracks_dao.set_exists_in_db(set_name, user_name, source = "mixcloud")):
            return self.tracks_dao.get_track_list(set_name, user_name, source = "mixcloud")
        else:
            return self.extract_track_list_from_mixcloud(user_name, set_name)
    
    def extract_track_list_from_mixcloud(self, user_name, set_name):
        url = self.mixcloud_base_url + user_name + "/" + set_name
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(self.chromedriver_url, options=options)
        driver.get(url)
        set_title = self.get_set_title(driver, set_name)
        set_likes = self.get_set_likes(driver, set_name)
        csrf_token = self.get_cookie(driver, "csrftoken")
        cast_id = self.get_cloudcast_id(csrf_token, url, set_name, user_name)
        body = self.get_query_body(cast_id)
        driver.close()
        return self.get_tracks_from_mixcloud(csrf_token, body, url, set_name, user_name, set_title, set_likes)
    
    def get_cloudcast_id(self, csrf_token, url, set_name, user_name):
        body = self.get_cloudcast_id_body(user_name, set_name)
        query_result = self.execute_query(csrf_token, body, url)
        res = json.loads(query_result.text)
        return res.get("data").get("cloudcastLookup").get("id")

    def get_tracks_from_mixcloud(self, csrf_token, body, url, set_name, user_name, set_title, set_likes):
        query_result = self.execute_query(csrf_token, body, url)
        res = json.loads(query_result.text)
        sections = res.get("data").get("cloudcast").get("sections")
        tracks = [Track(track.get("artistName"), track.get("songName"), set_details = MixCloudSet(set_name, user_name, set_title, set_likes)) for track in sections if track.get("__typename") == "TrackSection"]
        return tracks

    def get_set_likes(self, driver, set_name):
        likes = self.get_set_properties_by_xpath(driver, "//span[@class='amount']", default = "0", set_name = set_name)
        return likes.replace("k","000")

    def get_set_title(self, driver, set_name):
        return self.get_set_properties_by_xpath(driver, "//div[@class='title-inner-wrapper']/h1/a", default = set_name, set_name = set_name)
    
    def get_set_properties_by_xpath(self, driver, xpath, default, set_name):
        try:
            set_property = driver.find_element_by_xpath(xpath).text
        except NoSuchElementException:
            logging.info(f"MixCloud Track Extracter - failed extracting field with xpath {xpath} for set {set_name}")
            set_property = default

        return set_property

    def execute_query(self, csrf_token, body, url):
        headers = {
            'X-CSRFToken': csrf_token,
            'referer': url,
            'user-agent': self.user_agent
            }
        cookie_to_use = {
            "csrftoken": csrf_token,
            "c": self.c_value
            } # the c value is valid for 10 years 
        r = requests.post(self.mixcloud_base_url + "/graphql", json=body, headers=headers, cookies=cookie_to_use)
        return r
        
    def get_cast_id(self, driver: webdriver.Chrome):
        # old version to get cast Id - was deprecated by mixcloud
        datas = json.loads(driver.find_element_by_id("relay-data").get_attribute('innerHTML').replace("&quot;", '"'))
        for data in datas:
            if "cloudcast" in data:
                return data.get("cloudcast").get("data").get("cloudcast").get("id")

    def get_cookie(self, driver: webdriver.Chrome, cookie_name: str):
        return driver.get_cookie(cookie_name).get('value')

    def get_query_body(self, id):
        return {"id":"q70",
                "query": "query PlayerControls($id_0:ID!) {cloudcast(id:$id_0) {id,...Fc}} fragment F9 on TrackSection {artistName,songName,startSeconds,id} fragment Fa on ChapterSection {chapter,startSeconds,id} fragment Fc on Cloudcast {sections {__typename,...F9,...Fa},id}",
                "variables":{  
                    "id_0": id
                    }
                }
    
    def get_cloudcast_id_body(self, user_name, set_name):
        return {"id":"q70",
            "query": "query HeaderQuery($lookup_0:CloudcastLookup!,$lighten_1:Int!,$alpha_2:Float!) {cloudcastLookup(lookup:$lookup_0) {id,...Fo}} fragment F0 on Picture {urlRoot,primaryColor} fragment F1 on Cloudcast {picture {urlRoot,primaryColor},id} fragment F2 on Cloudcast {id,name,slug,owner {username,id}} fragment F3 on Cloudcast {owner {id,displayName,followers {totalCount}},id} fragment F4 on Cloudcast {restrictedReason,owner {displayName,country,username,isSubscribedTo,isViewer,id},slug,id,isAwaitingAudio,isDraft,isPlayable,streamInfo {hlsUrl,dashUrl,url,uuid},audioLength,currentPosition,proportionListened,repeatPlayAmount,hasPlayCompleted,seekRestriction,previewUrl,isExclusivePreviewOnly,isExclusive,picture {primaryColor,isLight,_primaryColor2pfPSM:primaryColor(lighten:$lighten_1),_primaryColor3Yfcks:primaryColor(alpha:$alpha_2)}} fragment F5 on Node {id,__typename} fragment F6 on Cloudcast {id,isFavorited,isPublic,hiddenStats,favorites {totalCount},slug,owner {id,isFollowing,username,isSelect,displayName,isViewer}} fragment F7 on Cloudcast {id,isUnlisted,isPublic} fragment F8 on Cloudcast {id,isReposted,isPublic,hiddenStats,reposts {totalCount},owner {isViewer,id}} fragment F9 on Cloudcast {id,isUnlisted,isPublic,slug,description,picture {urlRoot},owner {displayName,isViewer,username,id}} fragment Fa on Cloudcast {id,slug,isSpam,owner {username,isViewer,id}} fragment Fb on Cloudcast {owner {isViewer,isSubscribedTo,username,hasProFeatures,isBranded,id},sections {__typename,...F5},id,slug,isExclusive,isUnlisted,isShortLength,...F6,...F7,...F8,...F9,...Fa} fragment Fc on Cloudcast {qualityScore,listenerMinutes,id} fragment Fd on Cloudcast {slug,plays,publishDate,hiddenStats,owner {username,id},id,...Fc} fragment Fe on User {id} fragment Ff on User {username,hasProFeatures,hasPremiumFeatures,isStaff,isSelect,id} fragment Fg on User {id,isFollowed,isFollowing,isViewer,followers {totalCount},username,displayName} fragment Fh on Cloudcast {isExclusive,isExclusivePreviewOnly,slug,id,owner {username,id}} fragment Fi on Cloudcast {isExclusive,owner {id,username,displayName,...Fe,...Ff,...Fg},id,...Fh} fragment Fj on Cloudcast {id,streamInfo {uuid,url,hlsUrl,dashUrl},audioLength,seekRestriction,currentPosition} fragment Fk on Cloudcast {owner {displayName,isSelect,username,id},seekRestriction,id} fragment Fl on Cloudcast {id,waveformUrl,previewUrl,audioLength,isPlayable,streamInfo {hlsUrl,dashUrl,url,uuid},restrictedReason,seekRestriction,currentPosition,...Fk} fragment Fm on Cloudcast {__typename,isExclusivePreviewOnly,isExclusive,owner {isSelect,isSubscribedTo,username,displayName,isViewer,id},id} fragment Fn on Cloudcast {owner {username,displayName,isSelect,id},id} fragment Fo on Cloudcast {id,name,picture {isLight,primaryColor,...F0},owner {displayName,isViewer,isBranded,selectUpsell {text},id},repeatPlayAmount,restrictedReason,seekRestriction,...F1,...F2,...F3,...F4,...Fb,...Fd,...Fi,...Fj,...Fl,...Fm,...Fn}",
                "variables": {  
                    "lookup_0": {"username": user_name, "slug": set_name}, 
                    "lighten_1": 15, 
                    "alpha_2": 0.3}
                }
        
