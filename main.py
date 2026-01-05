import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from datetime import datetime
import jdatetime
import calendar
import logging
import os
import random
import time
import sys
import json
from colorama import Fore, Style, init

# --- بخش مدیریت تنظیمات و API ---
CONFIG_FILE = 'config.json'

def get_credentials():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"{Fore.YELLOW}--- تنظیمات اولیه سلف‌بات ---")
        api_id = input("لطفا API ID خود را وارد کنید: ")
        api_hash = input("لطفا API Hash خود را وارد کنید: ")
        data = {'api_id': api_id, 'api_hash': api_hash}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return data

config = get_credentials()
api_id = config['api_id']
api_hash = config['api_hash']

client = TelegramClient('session_name', api_id, api_hash)
# --------------------------------

DATA_FILE = 'database.json'
enemies = {}
friends = {}
muted_users = {}  
troll_list = {}  

def save_data():
    data = {
        'enemies': enemies,
        'friends': friends,
        'muted_users': muted_users,
        'troll_list': troll_list
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    global enemies, friends, muted_users, troll_list
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                enemies.update({int(k): v for k, v in data.get('enemies', {}).items()})
                friends.update({int(k): v for k, v in data.get('friends', {}).items()})
                muted_users.update({int(k): v for k, v in data.get('muted_users', {}).items()})
                troll_list.update({int(k): v for k, v in data.get('troll_list', {}).items()})
        except:
            pass

# لیست پاسخ‌ها (همان لیست‌های شما در اینجا قرار می‌گیرند)
enemy_responses = [
    "یا الله کیرم به قلب مادرت", "مادرتو میدم سگ بگاد", # بقیه لیست شما...
]

friend_responses = [
    "کیرتم مشتی", "بشاش شنا کنم", # بقیه لیست شما...
]

# ... بقیه توابع انیمیشن و مدیریت پیام‌ها که در کد خودتان بود را اینجا قرار دهید ...
# (توابعی مثل selfbot_logo_animation, connection_progress, handle_new_message و غیره)

async def main():
    load_data()
    await client.start()
    print(f"{Fore.GREEN}اتصال برقرار شد!")
    asyncio.create_task(update_profile_name_task())
    await client.run_until_disconnected()

if __name__ == "__main__":
    init(autoreset=True)
    selfbot_logo_animation()
    connection_progress()
    # load_modules()
    final_ready()
    asyncio.run(main())
