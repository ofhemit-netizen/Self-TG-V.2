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
    "یا الله کیرم به قلب مادرت", "مادرتو میدم سگ بگاد", "با کیرم ناموستو پاره میکنم",
    "کیرمو حلقه میکنم دور گردن مادرت", "کسخارتو بتن ریزی کردم", "ننتو تو پورن هاب دیدم",
    "کیر و خایه هام به کل اجدادت", "فیلم ننت فروشی", "کسننت پدرتم",
    "میرم تو کسمادرت با بیل پارش میکنم", "کیر به ناموس گشادت", "خسته نشدی ننتو گاییدم؟",
    "کیرم شلاقی به ناموس جندت", "با ناموست تریسام زدم", "برج خلیفه تو مادرت",
    "دو پایی میرم تو کسمادرت", "داگی استایل ننتو گاییدم", "هندل زدم به کون مادرت گاییدمش",
    "یگام دو گام ننتو میگام", "کیرمو نکن تو کسمادرت", "کیر و خایم به توان دو تو کسمادرت",
    "قمه تو کسمادرت", "نود ننتو دارم مادرکسده", "با کله میرم تو کسمادرت",
    "دستام تو کسمادرت", "کیرم به استخون های ننت", "مادرتو حراج زدم مادرجنده",
    "بریم برای راند بعد با ننت", "کیرم به رحم نجس ننت", "کیرم به چش و چال ننت",
    "کیروم به فرق سر ناموست", "مادرجنده کیری ناموس", "با کون ننت ناگت درست کردم",
    "خایه هام به کسمادرت", "برج میلاد تو کسمادرت", "یخچال تو کسمادرت",
    "کیرم به پوزه مادرت", "مادرتو زدم به سیخ", "کسمادرت","کیر شتر تو ناموست",
    "نودا ننت فروشی","خایه با پرزش تو ننت","چشای ننت تو کون خارت بره","ننتو ریدم",
    "لال شو مادرجنده اوبنه ای","اوب از کون ننت میباره","ماهی تو کسمادرت",
    "کیر هرچی خره تو کسمادرت","کیر رونالدو به کس خار و مادرت","مادرت زیر کیرم شهید شد",
    "اسپنک زدم به کون مادر جندت","کیرم یهویی به مرده و زندت","کیر به فیس ننت",
    "برو مادرجنده بی غیرت","استخون های مرده هات تو کسمادرت","اسپرمم تو نوامیست",
    "مادرتو با پوزیشن های مختلف گاییدم","میز و صندلی تو کسمادرت","کیر به ناموس دلقکت",
    "دمپایی تو کون ننت","دماغ پینوکیو رو گذاشتم جلو کص مادرت و بهش گفتم که بگه مادرت جنده نیست تا با دراز شدن دماغش کص مادرت پاره بشه",
    "مادر فلش شده جوری با کیر میزنم ب فرق سر ننت ک حافظش بپره","كيرم شيك تو كس ننت",
    "مادرتو کردم تو بشکه نفت از بالا کوه قل دادم پایین","با کیرم مادرتو هیپنوتیزم کردم",
    "ناموستو تو کوچه موقع عید دیدنی دیدم رفتم خونه به یادش جق زدم","با خیسی عرق کون مادرت جقیدم",
    "با سرعت نور تو فضا حرکت میکنم تا پیر نشم و بزارم آبجی کوچیکت بزرگ بشه تا وقتی بزرگ شد باهاش سکس کنم",
    "مادرتو پودر میکنم ازش سنگ توالت میسازم هر روز صبح رو مادرت میرینم",
    "مادرتو مجبور میکنم خودکشی کانتومی کنه تا در بی نهایت جهان موازی یتیم بشی",
    "دیدی چه لگدی به مادرت زدم ؟","فرشی که مادرت روش کونشو گذاشته بو کردم",
    "مادرتو جوری گاییدم که همسایه ها فکر کردن اسب ترکمن اومده خونتون" # بقیه لیست شما...
]

friend_responses = [
    "کیرتم مشتی", "بشاش شنا کنم", "شق کن بارفیکس برم", "کیرتو بخورم ستون",
    "جات رو کیرمه مشتی", "کیرتو بده لیس بزنیم", "خایه هام مال خودت مشتی",
    "داشمی", "تاج سری ستونم", "کیرت تو کسمادر بدخات", "مادر بدخاتو گاییدم",
    "ایدی بدخا بده ننشو بگام", "کیر تو ناموس کسی که ازت بدش بیاد", "خایتو بخورم ستونم",
    "بمولا که عشقمی", "دوست دارم داپشی", "ناموس بدخاتو گاییدم", "کیرت تو دنیا",
    "بکش پایین بکنمت", "رفاقت ابدی داپش", "کیرتو الکسیس بخوره", "امار ننه بدخاتو دربیارم؟",
    "بدخات ننش شب خوابه", "کیرت تو هرچی ادم مادرجندس", "کیرمون تو کسمادر بدخات",
    "کسخار دنیا داپش", "هعی مشتی کیر تو روزگار", "رفاقت پابرجا",
    "گاییدن کونت بهترین لذته", "کیرم به کونت بیب", # بقیه لیست شما...
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
