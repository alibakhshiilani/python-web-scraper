# Python Web Scraper for News Aggregator

This project is a Python-based web scraper that fetches news articles from various websites, stores them in a MySQL database, and then sends the articles to specified Telegram channels using the Telegram Bot API. The scraper is highly configurable and can be customized to work with different websites and messengers.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Dependencies](#dependencies)
6. [Website Configuration](#website-configuration)
7. [Bot Configuration](#bot-configuration)

## Introduction

The scraper consists of three main components:
1. **bot.py**: Contains classes for interacting with different messaging platforms, specifically Telegram and Bale. It sends messages and media to the configured channels.
2. **crawler.py**: The core web scraping logic is implemented here. It fetches news articles from websites, extracts relevant information, downloads images, and stores data in the MySQL database. It also interacts with the messaging bots to send articles to channels.
3. **website_config.json**: Contains the configuration for the websites to be scraped. Each website configuration includes details about the structure of the HTML and the categories to scrape.
4. **bot_config.json**: Contains configuration for messaging bots (Telegram and Bale) including API keys, channel IDs, and base URLs.
5. **requirements.txt**: Lists the required Python packages for this project.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo

2. Install the required dependencies:
    pip install -r requirements.txt


## Configuration

1. Modify `website_config.json` to configure the websites you want to scrape. Each website should have a name, base URL, HTML schema, and categories to scrape.
2. Configure `bot_config.json` to set up messaging bots. Provide your API keys, channel IDs, and base URLs.


## Usage

1. Run the web scraper using the following command:

```python crawler.py
```
The scraper will fetch news articles from the configured websites, store them in the MySQL database, and send them to the specified messaging channels.


## Dependencies

requests
beautifulsoup4
mysql-connector-python
selenium
datetime
validators
telegram


## Website Configuration

Configure the `website_config.json` file to define the websites you want to scrape. Each website should have the following attributes:

`name`: The name of the website.
`is_spa`: Whether the website is a Single Page Application (SPA).
`base_url`: The base URL of the website.
`html_schema`: HTML structure for extracting data:
`top_base_class`: The top-level HTML tag and class containing the list of articles.
`items_base_class`: The HTML tag and class for individual articles.
`title`: HTML tag for the article title.
`description`: HTML tag for the article description.
`image`: HTML tag for the article image.
`url`: HTML tag for the article URL.
`categories`: List of categories to scrape, each with a URL and category ID.


## Bot Configuration

Configure the` bot_config.json` file to set up messaging bots. Each bot should have the following attributes:

`messanger`: The messaging platform (e.g., "telegram" or "bale").
`api_key`: Your bot's API key.
`channel_id`: The ID of the channel to send messages to.
`time_between_schedule`: Time between scheduled scraping (optional).
`base_url`: The base URL for constructing article URLs.

```Copy and paste this code into your README file, and make any necessary adjustments to match your project structure and details.
```
