from selenium import webdriver
import pika
import json 
import logging
import time
import requests
import sys
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers = [
        logging.FileHandler("debug.log"),
        logging.StreamHandler()])

MIXCLOUD_QUEUE_NAME = "MixcloudMessages"

class MixcloudSetsCrawler:

    def __init__(self):
        self.mixcloud_base_url = "https://www.mixcloud.com/"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        self.chromedriver_url = "/usr/bin/chromedriver"
        self.url_to_append_sets = os.environ['URL_TO_APPEND_SETS']
        
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(self.chromedriver_url, options=options)

        connection_params = pika.ConnectionParameters(host = 'localhost', blocked_connection_timeout=600, heartbeat = 0)
        connection = pika.BlockingConnection(connection_params)
        self.channel = connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(queue = MIXCLOUD_QUEUE_NAME)

        self.channel.basic_consume(MIXCLOUD_QUEUE_NAME,
        on_message_callback = self.handle_mixcloud_message,
        auto_ack=False)

    def handle_mixcloud_message(self, channel, method, properties, body):
        logging.info(f"Mixcloud Crawler - Handling message: {body.decode()}")
        body_json = json.loads(body.decode())
        message_type = body_json["type"]
        if message_type == "userProfile":
            self.handle_mixcloud_user(body_json["body"])
        elif message_type == "setLink":
            self.handle_mixcloud_set(body_json["body"])
        else: 
            logging.warning(f"Mixcloud Crawler - Error - Unknown message type: {message_type}")
        channel.basic_ack(delivery_tag = method.delivery_tag)

    def handle_mixcloud_set(self, set_url):
        if self.append_set(set_url):
            favorited_users_profile = self.get_favorited_users(set_url)
            for user_profile in favorited_users_profile:
                message = json.dumps({"type": "userProfile", "body": user_profile})
                self.channel.basic_publish(exchange = "", 
                routing_key = MIXCLOUD_QUEUE_NAME, 
                body = message,
                properties=pika.BasicProperties(
                delivery_mode=2  # this makes message persistent
            ))
        
    def append_set(self, set_url) -> bool:
        set_url_parts = set_url.strip("/").split("/")
        set_data = {"name": set_url_parts[-1],
                    "source": "MixCloud",
                    "url": set_url,
                    "uploader": set_url_parts[-2]}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        body = json.dumps(set_data)
        return requests.post(self.url_to_append_sets, data = body, headers = headers)
      
    def get_favorited_users(self, url):
        self.driver.get(url.strip("/") + "/favorites") 
        usernames =  self.driver.find_elements_by_class_name("username")      
        return [username.get_attribute('href') for username in usernames[5:]]       

    def handle_mixcloud_user(self, user_profile):
        user_favorites_url = f"{user_profile}/favorites"
        self.driver.get(user_favorites_url)
        elements = self.driver.find_elements_by_xpath("//hgroup[@class='card-title']/h1/a")
        set_links = [element.get_attribute('href') for element in elements]
        for set_link in set_links:
            message = json.dumps({"type": "setLink", "body": set_link})
            self.channel.basic_publish(exchange = "", 
            routing_key = MIXCLOUD_QUEUE_NAME, 
            body = message)
        
    def start_consuming(self):
        self.channel.start_consuming()

if __name__ == "__main__":
    crawler = MixcloudSetsCrawler()
    crawler.start_consuming()

