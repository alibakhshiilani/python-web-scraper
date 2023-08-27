import asyncio
import json
import logging
from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup

class TelegramBot :

    def __init__(self):
        with open('bot_config.json', 'r') as f:
            bot_configs = json.load(f)
        bot_configs = [item for item in bot_configs if item.get("messanger") == "telegram"]      
        self.bot = Bot(token=bot_configs["api_key"]) 
        self.channel_id = bot_configs["channel_id"]   

    def send_message(self,message):
        asyncio.run(self.bot.send_message(chat_id=self.channel_id, text=message))

    def send_photo(self,image_url,title,description,url):
        keyboard = [[InlineKeyboardButton(text='ادامه خبر', url=url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asyncio.run(self.bot.send_photo(chat_id=self.channel_id, caption=f'🔴{title}\n\n{description}\n{self.channel_id}',photo=image_url,reply_markup=reply_markup))    


    def send_media(self,image_url,title,description,url):
        media = [InputMediaPhoto(media=image_url, caption=f'{title}\n\n{description}\n{self.channel_id}')]
        asyncio.run(self.bot.send_media_group(chat_id=self.channel_id, media=media))    



class BaleBot :

    def __init__(self):
        with open('bot_config.json', 'r') as f:
            bot_configs = json.load(f)
        bot_configs = [item for item in bot_configs if item.get("messanger") == "bale"]  
        self.bot = Bot(token=bot_configs["api_key"],
          base_url="https://tapi.bale.ai/",
          base_file_url="https://tapi.bale.ai/file/")
        self.channel_id = bot_configs["channel_id"]
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

    def send_message(self,message):
        asyncio.run(self.bot.send_message(chat_id=self.channel_id, text=message))

    def send_photo(self,image_url,title,description,url):
        keyboard = [[InlineKeyboardButton(text='ادامه خبر', url=url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asyncio.run(self.bot.send_photo(chat_id=self.channel_id, caption=f'{title}\n\n{description}',photo=image_url,reply_markup=reply_markup))    


    def send_media(self,image_url,title,description,url):
        media = [InputMediaPhoto(media=image_url, caption=f'{title}\n\n{description}\n{self.channel_id}')]
        asyncio.run(self.bot.send_media_group(chat_id=self.channel_id, media=media))    

