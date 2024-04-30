import pymongo
import mysql.connector

class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db = None

    def setup_mysql(self):
        if self.db_config["type"] == "mongodb":
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS category (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    slug VARCHAR(255) NOT NULL,
                    INDEX (slug)
                )
            """)
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS source (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    slug VARCHAR(255) NOT NULL,
                    INDEX (slug)
                )
            """)
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    views INT DEFAULT 0,
                    title VARCHAR(600) NOT NULL,
                    description TEXT NOT NULL,
                    media VARCHAR(255) NOT NULL,
                    hash VARCHAR(255) NOT NULL,
                    url VARCHAR(600) NOT NULL,
                    slug VARCHAR(700) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX (slug),
                    INDEX (views),
                    INDEX (title),
                    INDEX (created_at)
                )
            """)

            self.db.execute("""
                CREATE TABLE IF NOT EXISTS news_category (
                    news_id INT NOT NULL,
                    category_id INT NOT NULL,
                    FOREIGN KEY (news_id) REFERENCES news(id),
                    FOREIGN KEY (category_id) REFERENCES category(id),
                    PRIMARY KEY (news_id, category_id)
                )
            """)

            self.db.execute("""
                CREATE TABLE IF NOT EXISTS news_source (
                    news_id INT NOT NULL,
                    source_id INT NOT NULL,
                    FOREIGN KEY (news_id) REFERENCES news(id),
                    FOREIGN KEY (source_id) REFERENCES source(id),
                    PRIMARY KEY (news_id, source_id)
                )
            """)

    def connect(self):
        if self.db_config["type"] == "mongodb":
            self.connect_mongodb()
            self.db.create_collection("news")
        elif self.db_config["type"] == "mysql":
            self.connect_mysql()
            self.setup_mysql()
        else:
            raise ValueError("Unsupported database type")

    def connect_mongodb(self):
        my_client = pymongo.MongoClient(self.db_config["connection_string"])
        self.db = my_client[self.db_config["database"]]

    def connect_mysql(self):
        self.db = mysql.connector.connect(**self.db_config)

    def get_db(self):
        return self.db