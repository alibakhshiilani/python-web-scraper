import json
import os
import requests
import hashlib
from datetime import datetime
import time
from typing import Dict, Any
from bs4 import BeautifulSoup
# import mysql.connector
from bot import TelegramBot
import validators
import boto3
from slugify import slugify
import pymongo

class Crawler:
    def __init__(self, website_config: Dict[str, Any], db_config: Dict[str, Any], bot_config: Dict[str, Any]):
        self.website_config = website_config
        self.db_config = db_config
        self.bot_config = bot_config
        self.db = None
        self.cursor = None

    def setup_database(self):
        # self.db = mysql.connector.connect(**self.db_config)
        my_client = pymongo.MongoClient("mongodb://admin:1q2w3e@localhost:27017/")
        self.db = my_client["newsportal"]
        # self.cursor = self.db.cursor()
        self.create_tables()

    def create_tables(self):
        collection_ist = self.db.list_collection_names()
        if "news" in collection_ist:
            print("The collection exists.")
            


    def fetch_proxies(self):
        try:
            response = requests.get("https://api.getproxylist.com/proxy")
            return response.json()
        except Exception as e:
            print(f"Failed to fetch proxy list: {e}")
            return None

    def upload_image(self, url: str, save_path: str) -> str:
        now = datetime.now()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        folder_path = os.path.join(save_path, year, month, day)
        os.makedirs(folder_path, exist_ok=True)

        max_retries = 3
        timeout = 60
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200: 
                    print("Request successful")
                    break
                else:
                    print(f"Request attempt {attempt + 1} failed with status code {response.status_code}")
            except requests.Timeout:
                print(f"Request attempt {attempt + 1} timed out.")
            except requests.RequestException as e:
                print(f"An error occurred on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        content = response.content

        md5_hash = hashlib.md5(content).hexdigest()
        ext = url.split(".")
        image_format = ext[-1].split("?")[0]
        # file_path = os.path.join(folder_path, md5_hash + '.' + image_format)
        
        # with open(file_path, 'wb') as f:
        #     f.write(content)

        session = boto3.Session(
            aws_access_key_id='',
            aws_secret_access_key='',
            region_name='ir-thr-at1',
        )

        s3 = session.resource("s3",
            endpoint_url='https://s3.ir-thr-at1.arvanstorage.ir',
        )

        # response = s3.client.put(Bucket="gpnews", Key=md5_hash + "." + image_format, Body=content)

        bucket = s3.Bucket("gpnews")
        obj = bucket.Object(md5_hash + "." + image_format)
        obj.put(Body=content)

        # print(response)
        return md5_hash + "." + image_format


    def slug(self, string: str) -> str:
        return slugify(string)

    def crawl_website(self, website_config: Dict[str, Any]):
        print(f"Crawling website: {website_config['name']}")
        categories = website_config['categories']

        try:
            for category in categories:
                response = requests.get(category["url"])
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                html_schema = website_config["html_schema"]

                if "id" in html_schema["top_base_class"]:
                    parent = soup.find(html_schema["top_base_class"]["tag"], id=html_schema["top_base_class"]["id"])
                else:
                    parent = soup.find(html_schema["top_base_class"]["tag"], class_=html_schema["top_base_class"]["class"])

                if "id" in html_schema["items_base_class"]:
                    items = parent.find_all(html_schema["items_base_class"]["tag"], id=html_schema["items_base_class"]["id"])
                else:
                    items = parent.find_all(html_schema["items_base_class"]["tag"], class_=html_schema["items_base_class"]["class"])

                for post in items:
                    title = post.find(html_schema["title"]).text.strip()
                    description = post.find(html_schema["description"]["tag"], class_=html_schema["description"]["class"]).text.strip()
                    image_url = post.find(html_schema["image"])['src']
                    post_url = post.find(html_schema["url"])['href']

                    if not validators.url(post_url):
                        post_url = f"{website_config['base_url']}{post_url}"

                    post_hash = hashlib.sha256((title + description + image_url).encode()).hexdigest()

                    print(f"Scrapping Post : {post_hash}")

                    existing_news = self.db.news.find_one({"hash": post_hash})

                    if existing_news:
                        print("Post exists already !")
                        if category["category_id"] not in existing_news["categories"]:
                            self.db.news.update_one({"_id": existing_news["_id"]}, {"$addToSet": {"categories": category["category_id"]}})
                            print("Post exist but added to current category")
                        if website_config["source_id"] not in existing_news["sources"]:
                            self.db.news.update_one({"_id": existing_news["_id"]}, {"$addToSet": {"sources": website_config["source_id"]}})
                            print("Post exist but added to current source")

                    else:
                        if validators.url(image_url):
                            image_name = self.upload_image(image_url,image_path)
                            news_doc = {
                                "title": title,
                                "description": description,
                                "media": image_name,
                                "hash": post_hash,
                                "url": post_url,
                                "slug": self.slug(title),
                                "categories": [category["category_id"]],
                                "sources": [website_config["source_id"]],
                                "created_at": datetime.utcnow()
                            }
                            self.db.news.insert_one(news_doc)
                            last_news = self.db.news.find({}).sort({"_id":-1}).limit(1)
                            if html_schema["tags"]:
                                try:
                                    response = requests.get(post_url)
                                    response.raise_for_status()
                                    soup = BeautifulSoup(response.content, 'html.parser') # here !
                                    tags = []
                                    if "id" in html_schema["tags"]:
                                        tags = parent.find_all(html_schema["tags"]["tag"], id=html_schema["tags"]["id"])
                                    else:
                                        tags = parent.find_all(html_schema["tags"]["tag"], class_=html_schema["tags"]["class"])

                                    for tag in tags:
                                        self.db.news.update_one({"_id": last_news["_id"]}, {"$addToSet": {"tags": tag.text.strip()}})
                                except Exception as e:
                                    print(f"An error occurred in TAGS scrapping : {e}")
                                
                            print("Post added successfully")

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying...")
            print("Start Again crawling process")
            # self.crawl_website(website_config)

    def main(self):
        sleep_time = 3
        for wc in self.website_config:
            print(f"Start crawling process")
            self.crawl_website(wc)
            print(f"Stop For {sleep_time} seconds until next crawl")
            time.sleep(sleep_time)

if __name__ == "__main__":
    with open('config/website_config.json', 'r') as f:
        website_config = json.load(f)

    with open('config/database_config.json', 'r') as f:
        database_config = json.load(f)
    
    with open('config/bot_config.json', 'r') as f:
        bot_config = json.load(f)

    image_path = './'  # Update with your image path
    crawler = Crawler(website_config, database_config, bot_config)
    crawler.setup_database()
    crawler.main()
