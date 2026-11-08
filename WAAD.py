import telebot
from telebot import types
import sqlite3
import threading
import time
import re
import asyncio
import uuid
import json
import requests
import random
import string
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.sessions import StringSession
import telethon.errors
#احبك وعد 🌷
# ========= إعدادات =========
TOKEN = "9179054433:AAGvYc5o87fMtcGr8bi-Huv1uv1iQsEqpd8"
OWNER_ID = 7715736133
SUPPORT = "https://t.me/zk_jii"
ACTIVATION_CHANNEL_ID = -100442305461
ACTIVATION_CHANNEL_URL = "https://t.me/kakakmzo"

MY_API_ID = 34723624
MY_API_HASH = '8ea8625c2c6f7986974a1ff041d3401a'

PROXY_HOST = "geo.iproyal.com"
PROXY_PORT = 53918
PROXY_USER = "KdPw0m23CfZVA4394"
PROXY_PASS = "jagrttuuio_streaming-1"

proxies = {
    'http': f'socks5://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
    'https': f'socks5://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
}

bot = telebot.TeleBot(TOKEN)

# ========= إعداد حلقة asyncio =========
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ========= قاعدة بيانات =========
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points REAL DEFAULT 0,
    join_date TEXT,
    last_active TEXT,
    referred_by INTEGER,
    captcha_passed INTEGER DEFAULT 0
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS admins(
    user_id INTEGER PRIMARY KEY,
    added_by INTEGER,
    added_date TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS numbers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE,
    code TEXT,
    price REAL DEFAULT 10,
    service TEXT DEFAULT 'تيليجرام',
    country TEXT DEFAULT '🏳️ دول أخرى',
    added_by INTEGER,
    added_date TEXT,
    status TEXT DEFAULT 'متاح',
    session_str TEXT,
    api_id INTEGER,
    api_hash TEXT,
    is_2fa INTEGER DEFAULT 0,
    two_factor TEXT,
    category_name TEXT DEFAULT '2026'
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    number TEXT,
    code TEXT,
    two_factor TEXT,
    price REAL,
    country TEXT,
    service TEXT,
    purchase_date TEXT,
    session_str TEXT,
    api_id INTEGER,
    api_hash TEXT,
    is_2fa INTEGER,
    code_received INTEGER DEFAULT 0,
    activation_sent INTEGER DEFAULT 0
)""")

# إعادة إنشاء جدول mandatory_channels بالشكل الصحيح (عمود واحد)
cur.execute("DROP TABLE IF EXISTS mandatory_channels")
cur.execute("""CREATE TABLE mandatory_channels(
    channel_username TEXT PRIMARY KEY
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS settings(
    key TEXT PRIMARY KEY,
    value TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS external_api_orders(
    order_id TEXT PRIMARY KEY,
    user_id INTEGER,
    phone TEXT,
    country_id TEXT,
    service TEXT,
    price REAL,
    status TEXT,
    code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS asiacell_sessions(
    user_id INTEGER PRIMARY KEY,
    phone_number TEXT,
    pid TEXT,
    access_token TEXT,
    device_id TEXT,
    api_key TEXT,
    step TEXT,
    amount INTEGER
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS charge_codes(
    code TEXT PRIMARY KEY,
    amount REAL,
    created_by INTEGER,
    is_used INTEGER DEFAULT 0
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS stars_transactions(
    id TEXT PRIMARY KEY,
    user_id INTEGER,
    stars_amount INTEGER,
    balance_added REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS pending_payments(
    invoice_id TEXT PRIMARY KEY,
    user_id INTEGER,
    amount_usd REAL,
    stars_needed INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS user_captcha(
    user_id INTEGER PRIMARY KEY,
    expression TEXT,
    answer INTEGER,
    referrer_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS referral_pending(
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER
)""")

# إعدادات افتراضية
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('star_price', '20')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ref_reward', '0.1')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('asia_exchange_rate', '1300')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('asia_admin_number', '07776326105')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('external_api_key', 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MDY5NjA4NzQsImlhdCI6MTc3NTQyNDg3NCwicmF5IjoiNGUzNjcyYTViMDkwMDg0YjlmOTc4NzdlYmM0YWNlMmYiLCJzdWIiOjM5NDAwMjZ9.IBNddznWzFIEnLaPEktnI0QbxN2SZf-iFBtCC4JU34DJXUvUVVNK3-h50ALrjf5UWvSh-WpvOETxHc9Lw8jbVv_3vbAC8em9BfYALGDsfBuTeEkVAnAy_CRv2aSzPrUN7ZKYOyCb4kGNXOrW1H1He9WFxeINTTLS8o0RUwNLll1frKnSKdksKKyhUVNqYZBJKDQBibum1w9zj0jhSnBaDIxdPNxGUBeVWRQ2t80X1O1nlNqE-hP1VVi-IHr1X1A9q4NRGJXxvtvXw9DGhVEb4SlXULoMBLz6d1fH4HmxXT9uaGfuj0rHBDnPKTSKBuDNpoFSe1vy07demBJZygFzOA')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('external_api_profit', '0.2')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('external_api_status', 'on')")
cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('asia_topup_hidden', 'off')")
cur.execute("REPLACE INTO settings (key, value) VALUES ('activation_channel_id', ?)", (str(ACTIVATION_CHANNEL_ID),))
cur.execute("REPLACE INTO settings (key, value) VALUES ('activation_channel_url', ?)", (ACTIVATION_CHANNEL_URL,))

try:
    cur.execute("ALTER TABLE numbers ADD COLUMN category_name TEXT DEFAULT '2026'")
except:
    pass
conn.commit()

# ========= تعريف الدول =========
DEFAULT_COUNTRY = "🏳️ دول أخرى"

COUNTRY_CODES = {
'1': "🇺🇸 أمريكا", '12': "🇨🇦 كندا", '7': "🇷🇺 روسيا", '20': "🇪🇬 مصر", '27': "🇿🇦 جنوب أفريقيا",
'30': "🇬🇷 اليونان", '31': "🇳🇱 هولندا", '32': "🇧🇪 بلجيكا", '33': "🇫🇷 فرنسا",
'34': "🇪🇸 إسبانيا", '36': "🇭🇺 المجر", '39': "🇮🇹 إيطاليا", '40': "🇷🇴 رومانيا",
'41': "🇨🇭 سويسرا", '43': "🇦🇹 النمسا", '44': "🇬🇧 بريطانيا", '45': "🇩🇰 الدنمارك",
'46': "🇸🇪 السويد", '47': "🇳🇴 النرويج", '48': "🇵🇱 بولندا", '49': "🇩🇪 ألمانيا",
'51': "🇵🇪 بيرو", '52': "🇲🇽 المكسيك", '53': "🇨🇺 كوبا", '54': "🇦🇷 الأرجنتين",
'55': "🇧🇷 البرازيل", '56': "🇨🇱 تشيلي", '57': "🇨🇴 كولومبيا", '58': "🇻🇪 فنزويلا",
'60': "🇲🇾 ماليزيا", '61': "🇦🇺 أستراليا", '62': "🇮🇩 إندونيسيا", '63': "🇵🇭 الفلبين",
'64': "🇳🇿 نيوزيلندا", '65': "🇸🇬 سنغافورة", '66': "🇹🇭 تايلاند", '81': "🇯🇵 اليابان",
'82': "🇰🇷 كوريا الجنوبية", '84': "🇻🇳 فيتنام", '86': "🇨🇳 الصين", '90': "🇹🇷 تركيا",
'91': "🇮🇳 الهند", '92': "🇵🇰 باكستان", '93': "🇦🇫 أفغانستان", '94': "🇱🇰 سريلانكا",
'95': "🇲🇲 ميانمار", '98': "🇮🇷 إيران",
'211': "🇸🇸 جنوب السودان", '212': "🇲🇦 المغرب", '213': "🇩🇿 الجزائر",  
'216': "🇹🇳 تونس", '218': "🇱🇾 ليبيا", '220': "🇬🇲 غامبيا",  
'221': "🇸🇳 السنغال", '222': "🇲🇷 موريتانيا", '223': "🇲🇱 مالي",  
'224': "🇬🇳 غينيا", '225': "🇨🇮 ساحل العاج", '226': "🇧🇫 بوركينا فاسو",  
'227': "🇳🇪 النيجر", '228': "🇹🇬 توغو", '229': "🇧🇯 بنين",  
'230': "🇲🇺 موريشيوس", '231': "🇱🇷 ليبيريا", '232': "🇸🇱 سيراليون",  
'233': "🇬🇭 غانا", '234': "🇳🇬 نيجيريا", '235': "🇹🇩 تشاد",  
'236': "🇨🇫 أفريقيا الوسطى", '237': "🇨🇲 الكاميرون", '238': "🇨🇻 الرأس الأخضر",  
'239': "🇸🇹 ساو تومي وبرينسيب", '240': "🇬🇶 غينيا الاستوائية",  
'241': "🇬🇦 الغابون", '242': "🇨🇬 الكونغو", '243': "🇨🇩 الكونغو الديمقراطية",  
'244': "🇦🇴 أنغولا", '245': "🇬🇼 غينيا بيساو", '246': "🇮🇴 إقليم المحيط الهندي",  
'248': "🇸🇨 سيشل", '249': "🇸🇩 السودان", '250': "🇷🇼 رواندا",  
'251': "🇪🇹 إثيوبيا", '252': "🇸🇴 الصومال", '253': "🇩🇯 جيبوتي",  
'254': "🇰🇪 كينيا", '255': "🇹🇿 تنزانيا", '256': "🇺🇬 أوغندا",  
'257': "🇧🇮 بوروندي", '258': "🇲🇿 موزمبيق", '260': "🇿🇲 زامبيا",  
'261': "🇲🇬 مدغشقر", '262': "🇷🇪 ريونيون", '263': "🇿🇼 زيمبابوي",  
'264': "🇳🇦 ناميبيا", '265': "🇲🇼 مالاوي", '266': "🇱🇸 ليسوتو",  
'267': "🇧🇼 بوتسوانا", '268': "🇸🇿 إسواتيني", '269': "🇰🇲 جزر القمر",  
'290': "🇸🇭 سانت هيلينا", '291': "🇪🇷 إريتريا",  
'297': "🇦🇼 أروبا", '298': "🇫🇴 جزر فارو", '299': "🇬🇱 غرينلاند",  
'350': "🇬🇮 جبل طارق", '351': "🇵🇹 البرتغال", '352': "🇱🇺 لوكسمبورغ",  
'353': "🇮🇪 أيرلندا", '354': "🇮🇸 آيسلندا", '355': "🇦🇱 ألبانيا",  
'356': "🇲🇹 مالطا", '357': "🇨🇾 قبرص", '358': "🇫🇮 فنلندا",  
'359': "🇧🇬 بلغاريا", '370': "🇱🇹 ليتوانيا", '371': "🇱🇻 لاتفيا",  
'372': "🇪🇪 إستونيا", '373': "🇲🇩 مولدوفا", '374': "🇦🇲 أرمينيا",  
'375': "🇧🇾 بيلاروسيا", '376': "🇦🇩 أندورا", '377': "🇲🇨 موناكو",  
'378': "🇸🇲 سان مارينو", '380': "🇺🇦 أوكرانيا", '381': "🇷🇸 صربيا",  
'382': "🇲🇪 الجبل الأسود", '383': "🇽🇰 كوسوفو", '385': "🇭🇷 كرواتيا",  
'386': "🇸🇮 سلوفينيا", '387': "🇧🇦 البوسنة والهرسك",  
'389': "🇲🇰 مقدونيا الشمالية", '420': "🇨🇿 التشيك",  
'421': "🇸🇰 سلوفاكيا", '423': "🇱🇮 ليختنشتاين",  
'500': "🇫🇰 جزر فوكلاند", '501': "🇧🇿 بليز", '502': "🇬🇹 غواتيمالا",  
'503': "🇸🇻 السلفادور", '504': "🇭🇳 هندوراس", '505': "🇳🇮 نيكاراغوا",  
'506': "🇨🇷 كوستاريكا", '507': "🇵🇦 بنما", '508': "🇵🇲 سان بيير وميكلون",  
'509': "🇭🇹 هايتي", '590': "🇬🇵 غوادلوب", '591': "🇧🇴 بوليفيا",  
'592': "🇬🇾 غيانا", '593': "🇪🇨 الإكوادور", '594': "🇬🇫 غويانا الفرنسية",  
'595': "🇵🇾 باراغواي", '596': "🇲🇶 مارتينيك", '597': "🇸🇷 سورينام",  
'598': "🇺🇾 أوروغواي", '599': "🇨🇼 كوراساو",  
'850': "🇰🇵 كوريا الشمالية", '852': "🇭🇰 هونغ كونغ",  
'853': "🇲🇴 ماكاو", '855': "🇰🇭 كمبوديا", '856': "🇱🇦 لاوس",  
'880': "🇧🇩 بنغلاديش", '886': "🇹🇼 تايوان",  
'960': "🇲🇻 جزر المالديف", '961': "🇱🇧 لبنان", '962': "🇯🇴 الأردن",  
'963': "🇸🇾 سوريا", '964': "🇮🇶 العراق", '965': "🇰🇼 الكويت",  
'966': "🇸🇦 السعودية", '967': "🇾🇪 اليمن", '968': "🇴🇲 عمان",  
'970': "🇵🇸 فلسطين", '971': "🇦🇪 الإمارات", '972': "🇮🇱 إسرائيل",  
'973': "🇧🇭 البحرين", '974': "🇶🇦 قطر", '975': "🇧🇹 بوتان",  
'976': "🇲🇳 منغوليا", '977': "🇳ﭘ نيبال",  
'992': "🇹🇯 طاجيكستان", '993': "🇹🇲 تركمانستان",  
'994': "🇦🇿 أذربيجان", '995': "🇬🇪 جورجيا",  
'996': "🇰🇬 قيرغيزستان", '998': "🇺🇿 أوزبكستان"
}

def detect_country_from_number(number):
    number = str(number).strip().lower()
    if not number.isdigit():
        eng_to_ar = {
            'canada': "🇨🇦 كندا", 'usa': "🇺🇸 أمريكا", 'russia': "🇷🇺 روسيا",
            'england': "🇬🇧 بريطانيا", 'united kingdom': "🇬🇧 بريطانيا",
            'germany': "🇩🇪 ألمانيا", 'france': "🇫🇷 فرنسا", 'egypt': "🇪🇬 مصر",
            'iraq': "🇮🇶 العراق", 'turkey': "🇹🇷 تركيا", 'indonesia': "🇮🇩 إندونيسيا",
            'india': "🇮🇳 الهند", 'vietnam': "🇻🇳 فيتنام", 'thailand': "🇹🇭 تايلاند"
        }
        if number in eng_to_ar:
            name = eng_to_ar[number]
            return {'name': name, 'emoji': name.split()[0], 'code': 'ext'}
        for code, name in COUNTRY_CODES.items():
            if number in name.lower():
                return {'name': name, 'emoji': name.split()[0], 'code': code}
        return {'name': number.capitalize(), 'emoji': '🌍', 'code': 'ext'}
    number = re.sub(r'[^0-9]', '', number)
    if number.startswith('0'):
        number = number[1:]
    if number.startswith('12'):
        return {'name': "🇨🇦 كندا", 'emoji': "🇨🇦", 'code': "12"}
    for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
        if number.startswith(code):
            return {'name': COUNTRY_CODES[code], 'emoji': COUNTRY_CODES[code].split()[0], 'code': code}
    return {'name': DEFAULT_COUNTRY, 'emoji': '🏳️', 'code': '000'}

def get_country_name(phone):
    phone = str(phone).lstrip('+')
    for code, name in COUNTRY_CODES.items():
        if phone.startswith(code):
            return name
    return DEFAULT_COUNTRY

def mask_phone(phone):
    p = str(phone).lstrip('+')
    if len(p) < 7:
        return phone
    return f"+{p[:1]} ({p[1:4]}) *** {p[-2:]}"

def mask_id(uid):
    s = str(uid)
    if len(s) < 6: return s
    return f"{s[:3]}**{s[-4:]}"

def format_phone_full(phone):
    p = str(phone).lstrip('+')
    if len(p) < 7:
        return phone
    return f"+{p[:1]} ({p[1:4]}) {p[4:7]}-{p[7:]}"

def format_price(price):
    try:
        return f"${float(price):.2f}"
    except:
        return "$0.00"

# ========= دوال مساعدة =========
def ensure_column(table, column, col_type="TEXT", default=None):
    try:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [r[1] for r in cur.fetchall()]
        if column not in columns:
            if default is not None:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT '{default}'")
            else:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            conn.commit()
    except:
        pass

def initialize_columns():
    ensure_column("users", "points", "REAL", 0)
    ensure_column("users", "referred_by", "INTEGER")
    ensure_column("users", "captcha_passed", "INTEGER", 0)
    ensure_column("numbers", "price", "REAL", 10)
    ensure_column("numbers", "country", "TEXT", DEFAULT_COUNTRY)
    ensure_column("numbers", "two_factor", "TEXT", "")
    ensure_column("numbers", "session_str", "TEXT", "")
    ensure_column("numbers", "api_id", "INTEGER", 0)
    ensure_column("numbers", "api_hash", "TEXT", "")
    ensure_column("numbers", "is_2fa", "INTEGER", 0)
    ensure_column("history", "code_received", "INTEGER", 0)
    ensure_column("history", "activation_sent", "INTEGER", 0)
    ensure_column("numbers", "category_name", "TEXT", "2026")

initialize_columns()

def get_setting(key, default=None):
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = cur.fetchone()
    return res[0] if res else default

def set_config(key, value):
    cur.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()

def is_admin(uid):
    if uid == OWNER_ID:
        return True
    cur.execute("SELECT 1 FROM admins WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def get_user_points(uid):
    cur.execute("SELECT points FROM users WHERE user_id=?", (uid,))
    res = cur.fetchone()
    return res[0] if res else 0

def add_points_to_user(uid, amount):
    cur.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, uid))
    conn.commit()

def remove_points_from_user(uid, amount):
    cur.execute("UPDATE users SET points = points - ? WHERE user_id=?", (amount, uid))
    conn.commit()

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_user_activity(uid):
    cur.execute("INSERT OR IGNORE INTO users (user_id, join_date, last_active) VALUES (?, ?, ?)",
                (uid, get_current_time(), get_current_time()))
    cur.execute("UPDATE users SET last_active=? WHERE user_id=?", (get_current_time(), uid))
    conn.commit()

def generate_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = num1 + num2
        expr = f"{num1} + {num2}"
    else:
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        expr = f"{num1} - {num2}"
    return expr, answer

# ========= دوال الإشتراك الإجباري (مثل Bilal.py) =========
def check_subscription(uid):
    """التحقق من الاشتراك في القنوات الإجبارية"""
    cur.execute("SELECT channel_username FROM mandatory_channels")
    channels = cur.fetchall()
    if not channels:
        return []  # لا توجد قنوات
    not_joined = []
    for (ch_username,) in channels:
        try:
            member = bot.get_chat_member(f"@{ch_username}", uid)
            if member.status in ['left', 'kicked']:
                not_joined.append(ch_username)
        except:
            not_joined.append(ch_username)
    return not_joined

def subscription_markup(not_joined):
    """إنشاء أزرار الاشتراك"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    for ch_username in not_joined:
        kb.add(types.InlineKeyboardButton(f"📢 اشترك في @{ch_username}", url=f"https://t.me/{ch_username}"))
    kb.add(types.InlineKeyboardButton("✅ تحققت من اشتراكي", callback_data="check_sub"))
    return kb

# ========= شحن النجوم =========
def show_stars_menu(uid):
    star_price = float(get_setting('star_price', 20))
    kb = types.InlineKeyboardMarkup(row_width=2)
    amounts = [1, 5, 10, 20, 50, 100]
    for amt in amounts:
        points = amt * star_price
        kb.add(types.InlineKeyboardButton(f"🌟 {amt} نجمة = {points} نقطة", callback_data=f"paystars_{amt}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="auto_recharge"))
    bot.send_message(uid, f"🌟 **شحن النقاط عبر نجوم تيليجرام**\n\n💰 السعر الحالي: `1 نجمة = {star_price} نقطة`\n\nاختر الكمية المطلوبة:", reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("paystars_"))
def handle_paystars(call):
    uid = call.from_user.id
    stars_amt = int(call.data.split("_")[1])
    star_price = float(get_setting('star_price', 20))
    points_to_add = stars_amt * star_price
    
    invoice_id = str(uuid.uuid4())
    cur.execute("INSERT INTO pending_payments(invoice_id, user_id, amount_usd, stars_needed) VALUES(?,?,?,?)",
                (invoice_id, uid, points_to_add, stars_amt))
    conn.commit()

    prices = [types.LabeledPrice(label=f"شحن {points_to_add} نقطة", amount=stars_amt)]
    bot.send_invoice(
        uid,
        title="شحن نقاط البوت",
        description=f"شحن {points_to_add} نقطة عبر نجوم تيليجرام",
        provider_token="",
        currency="XTR",
        prices=prices,
        invoice_payload=invoice_id,
        start_parameter="recharge"
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(msg):
    uid = msg.from_user.id
    payload = msg.successful_payment.invoice_payload
    cur.execute("SELECT amount_usd FROM pending_payments WHERE invoice_id=?", (payload,))
    row = cur.fetchone()
    if row:
        amount = row[0]
        add_points_to_user(uid, amount)
        cur.execute("INSERT INTO stars_transactions(id, user_id, stars_amount, balance_added) VALUES(?,?,?,?)",
                    (payload, uid, msg.successful_payment.total_amount, amount))
        cur.execute("DELETE FROM pending_payments WHERE invoice_id=?", (payload,))
        conn.commit()
        bot.send_message(uid, f"✅ **تم شحن {amount} نقطة بنجاح عبر النجوم!**", parse_mode="Markdown")

# ========= آسيا سيل =========
class AsiacellAPI:
    ASIA_BASE_URL = "https://odpapp.asiacell.com/api/v1/"
    def __init__(self):
        self.api_key = ''.join(random.choices(string.hexdigits.lower(), k=32))

    def _headers(self, device_id, access_token=None):
        h = {
            'User-Agent': "okhttp/5.0.0-alpha.2",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'X-ODP-API-KEY': self.api_key,
            'Cache-Control': "no-cache",
            'DeviceID': str(device_id),
            'X-OS-Version': "11",
            'X-Device-Type': "[Android][realme][RMX3834 11][TIRAMISU][HMS][4.3.7:90000325]",
            'X-ODP-APP-VERSION': "4.3.7",
            'X-FROM-APP': "odp",
            'X-ODP-CHANNEL': "mobile",
            'X-SCREEN-TYPE': "false",
            'Content-Type': "application/json; charset=UTF-8"
        }
        if access_token:
            h['Authorization'] = f"Bearer {access_token}"
        return h

    def login(self, phone: str, device_id: str) -> dict:
        url = f"{self.ASIA_BASE_URL}login?lang=en"
        phone = phone.lstrip('0')
        if not phone.startswith('964'):
            phone = '964' + phone
        payload = {"captchaCode": "", "username": str(phone)}
        try:
            r = requests.post(url, data=json.dumps(payload),
                              headers=self._headers(device_id), timeout=20)
            try:
                data = r.json()
                if data.get("success") and "nextUrl" in data:
                    data['success'] = True
                return data
            except:
                return {'success': False, 'message': f'Invalid JSON Response (HTTP {r.status_code})'}
        except Exception as e:
            return {'success': False, 'message': f'Connection Error: {str(e)}'}

    def validate_sms(self, pid: str, passcode: str, device_id: str) -> dict:
        url = f"{self.ASIA_BASE_URL}smsvalidation?lang=en"
        payload = {"PID": str(pid), "passcode": str(passcode), "token": ""}
        try:
            r = requests.post(url, data=json.dumps(payload),
                              headers=self._headers(device_id), timeout=20)
            try:
                return r.json()
            except:
                return {'success': False, 'message': 'Invalid JSON Response'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def start_transfer(self, access_token: str, amount: int, receiver: str, device_id: str) -> dict:
        url = f"{self.ASIA_BASE_URL}credit-transfer/start?lang=ar"
        receiver = receiver.lstrip('0')
        if not receiver.startswith('964'):
            receiver = '964' + receiver
        payload = {"amount": float(amount), "receiverMsisdn": str(receiver)}
        try:
            r = requests.post(url, data=json.dumps(payload),
                              headers=self._headers(device_id, access_token), timeout=20)
            try:
                data = r.json()
                if data.get("success") or "PID" in data:
                    data['success'] = True
                return data
            except:
                return {'success': False, 'message': 'Invalid JSON Response'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def confirm_transfer(self, access_token: str, pid: str, passcode: str, device_id: str) -> dict:
        url = f"{self.ASIA_BASE_URL}credit-transfer/do-transfer?lang=ar"
        payload = {"PID": str(pid), "passcode": str(passcode)}
        try:
            r = requests.post(url, data=json.dumps(payload),
                              headers=self._headers(device_id, access_token), timeout=20)
            try:
                return r.json()
            except:
                return {'success': False, 'message': 'Invalid JSON Response'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def _extract_pid(self, res: dict) -> str | None:
        pid = res.get("PID") or res.get("transactionId")
        if not pid and "nextUrl" in res:
            m = re.search(r'PID=([a-f0-9\-]+)', res["nextUrl"])
            if m:
                pid = m.group(1)
        return pid

asia_api = AsiacellAPI()

# ========= 5SIM API =========
class FiveSimAPI:
    BASE_URL = "https://5sim.net/v1"
    def __init__(self):
        pass
    def _headers(self):
        api_key = get_setting('external_api_key', '')
        return {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    def get_balance(self):
        try:
            r = requests.get(f"{self.BASE_URL}/user/profile", headers=self._headers(), timeout=10)
            return r.json()
        except:
            return {"balance": 0}
    def get_prices(self):
        try:
            r = requests.get(f"{self.BASE_URL}/guest/prices?service=telegram", timeout=15)
            return r.json()
        except:
            return {}
    def buy_number(self, country, service="telegram", operator="any"):
        try:
            r = requests.get(f"{self.BASE_URL}/user/buy/activation/{country}/{operator}/{service}", headers=self._headers(), timeout=30)
            return r.json()
        except Exception as e:
            return {"error": str(e)}
    def check_order(self, order_id):
        try:
            r = requests.get(f"{self.BASE_URL}/user/check/{order_id}", headers=self._headers(), timeout=10)
            return r.json()
        except:
            return {"status": "error"}
    def finish_order(self, order_id):
        try:
            r = requests.get(f"{self.BASE_URL}/user/finish/{order_id}", headers=self._headers(), timeout=10)
            return r.json()
        except:
            return {"status": "error"}
    def cancel_order(self, order_id):
        try:
            r = requests.get(f"{self.BASE_URL}/user/cancel/{order_id}", headers=self._headers(), timeout=10)
            return r.json()
        except:
            return {"status": "error"}

external_api = FiveSimAPI()

# ========= دوال Telethon =========
async def send_code_async(client, phone):
    try:
        await client.connect()
        await client.send_code_request(phone)
        return True
    except Exception as e:
        print(f"send_code error: {e}")
        return False

async def verify_code_async(client, phone, code):
    try:
        await client.sign_in(phone, code)
        return True
    except telethon.errors.SessionPasswordNeededError:
        return "2fa_required"
    except Exception as e:
        print(f"verify_code error: {e}")
        return False

async def verify_2fa_async(client, password):
    try:
        await client.sign_in(password=password)
        return True
    except:
        return False

async def disconnect_client_async(client):
    try:
        await client.disconnect()
    except:
        pass

async def fetch_code_from_account(session_str, api_id, api_hash):
    try:
        device = get_random_device()
        client = TelegramClient(StringSession(session_str), api_id, api_hash,
                                device_model=device['model'], system_version=device['os'], app_version="10.9.1")
        await client.connect()
        if not await client.is_user_authorized():
            return None
        await asyncio.sleep(random.uniform(1, 3))
        msgs = await client(GetHistoryRequest(peer=777000, limit=10, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        code = None
        for m in msgs.messages:
            if m.message:
                match = re.search(r'(\b\d{5,6}\b)', m.message)
                if match:
                    code = match.group(0)
                    break
        await client.disconnect()
        return code
    except:
        return None

async def change_all_2fa_passwords(new_password="WAAD"):
    cur.execute("SELECT id, session_str, api_id, api_hash, two_factor FROM numbers WHERE status='متاح'")
    rows = cur.fetchall()
    success_count = 0
    fail_count = 0
    for row in rows:
        num_id, session_str, api_id, api_hash, old_pwd = row
        try:
            device = get_random_device()
            client = TelegramClient(StringSession(session_str), api_id, api_hash,
                                    device_model=device['model'], system_version=device['os'], app_version="10.9.1")
            await client.connect()
            if not await client.is_user_authorized():
                fail_count += 1
                continue
            await client.edit_2fa(new_password=new_password, current_password=old_pwd if old_pwd else None)
            cur.execute("UPDATE numbers SET two_factor=? WHERE id=?", (new_password, num_id))
            conn.commit()
            success_count += 1
            await client.disconnect()
        except:
            fail_count += 1
    return success_count, fail_count

DEVICES = [
    {"model": "SM-S928B", "brand": "Samsung", "os": "Android 14"},
    {"model": "Pixel 8 Pro", "brand": "Google", "os": "Android 14"},
    {"model": "Xiaomi 14 Ultra", "brand": "Xiaomi", "os": "Android 14"},
    {"model": "iPhone 15 Pro Max", "brand": "Apple", "os": "iOS 17.4"},
    {"model": "SM-G998B", "brand": "Samsung", "os": "Android 13"},
    {"model": "RMX3834", "brand": "Realme", "os": "Android 11"}
]

def get_random_device():
    return random.choice(DEVICES)

def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

def run_async_void(coro):
    asyncio.run_coroutine_threadsafe(coro, loop)

# ========= /start =========
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    name = msg.from_user.first_name
    
    update_user_activity(uid)

    # معالجة الإحالة من رابط الدعوة
    if len(msg.text.split()) > 1:
        ref_id = msg.text.split()[1]
        if ref_id.isdigit() and int(ref_id) != uid:
            cur.execute("INSERT OR IGNORE INTO referral_pending(user_id, referrer_id) VALUES(?,?)", (uid, int(ref_id)))
            conn.commit()

    # الخطوة 1: الاشتراك الإجباري
    not_joined = check_subscription(uid)
    if not_joined:
        bot.send_message(uid, "⚠️ **يجب الاشتراك في القنوات التالية للمتابعة:**\n\n", reply_markup=subscription_markup(not_joined), parse_mode="Markdown")
        return

    # بعد التأكد من الاشتراك، ننتقل إلى الكابتشا
    cur.execute("SELECT captcha_passed FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    if not row or row[0] == 0:
        expr, answer = generate_captcha()
        cur.execute("INSERT OR REPLACE INTO user_captcha(user_id, expression, answer) VALUES(?,?,?)", (uid, expr, answer))
        conn.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_captcha"))
        bot.send_message(uid,
            "🔒 **تحقق أمني** 🔒\n\nللتحقق من أنك لست روبوت، الرجاء حل المعادلة التالية:\n\n"
            f"**{expr} = ?**\n\n📌 أرسل الإجابة كرقم فقط:",
            reply_markup=kb, parse_mode="Markdown")
        return

    # إذا اجتاز الكابتشا بالفعل، أظهر القائمة الرئيسية
    show_main_menu(uid, msg)

def show_main_menu(uid, msg=None):
    points = get_user_points(uid)
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("شـراء رقـم", callback_data="buy_menu"),
        types.InlineKeyboardButton("شراء أرقام SMS", callback_data="buy_api_countries")
    )
    kb.add(
        types.InlineKeyboardButton("رصـيدك الحـالي", callback_data="points"),
        types.InlineKeyboardButton("الشـحن التـلقـائي", callback_data="auto_recharge")
    )
    kb.add(
        types.InlineKeyboardButton("دعـوة صـديق", callback_data="referral"),
        types.InlineKeyboardButton("الوكـيل الـرسمـي", url=SUPPORT)
    )
    if is_admin(uid):
        kb.add(types.InlineKeyboardButton("⚙️ لوحة التحكم", callback_data="admin_panel"))

    welcome_text = (
        f"👋 **أهلاً بك في بوت بيع حسابات تيليجرام!**\n\n"
        f"🆔 **أيديك:** `{uid}`\n"
        f"💰 **نقاطك:** `{points}`\n\n"
        f"✨ **يختص هذا البوت في بيع حسابات تيليجرام.**\n"
        f"🚀 **استخدم الأزرار أدناه للتحكم.**"
    )
    if msg:
        bot.send_message(uid, welcome_text, reply_markup=kb, parse_mode="Markdown")
    else:
        bot.send_message(uid, welcome_text, reply_markup=kb, parse_mode="Markdown")

# ========= معالجة الكابتشا عبر الرسائل النصية =========
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_captcha_answer(msg):
    uid = msg.from_user.id
    cur.execute("SELECT expression, answer FROM user_captcha WHERE user_id=?", (uid,))
    captcha = cur.fetchone()
    if not captcha:
        return

    expr, correct_answer = captcha
    user_answer = int(msg.text.strip())

    if user_answer == correct_answer:
        # نجاح الكابتشا
        cur.execute("UPDATE users SET captcha_passed=1 WHERE user_id=?", (uid,))
        cur.execute("DELETE FROM user_captcha WHERE user_id=?", (uid,))
        conn.commit()

        # ✅ إرسال إشعار للأدمن عند دخول مستخدم جديد (أول مرة يكمل الكابتشا)
        # نتحقق إذا كان المستخدم جديداً (أي ليس لديه نقاط أو مشتريات سابقة)
        cur.execute("SELECT points, join_date FROM users WHERE user_id=?", (uid,))
        user_data = cur.fetchone()
        is_new = (user_data[0] == 0 and user_data[1] == get_current_time())
        if is_new:
            try:
                bot.send_message(OWNER_ID, f"👤 **عضو جديد دخل البوت!**\n🆔 `{uid}`\n📅 الوقت: {get_current_time()}")
            except:
                pass

        # منح مكافأة الإحالة إذا كانت معلقة
        cur.execute("SELECT referrer_id FROM referral_pending WHERE user_id=?", (uid,))
        ref_row = cur.fetchone()
        if ref_row:
            referrer_id = ref_row[0]
            ref_reward = float(get_setting('ref_reward', 0.1))
            add_points_to_user(referrer_id, ref_reward)
            try:
                bot.send_message(referrer_id, f"🎁 **لقد حصلت على {ref_reward} نقطة لدعوتك صديق!**", parse_mode="Markdown")
            except:
                pass
            cur.execute("DELETE FROM referral_pending WHERE user_id=?", (uid,))
            conn.commit()

        # عرض القائمة الرئيسية
        show_main_menu(uid, msg)
    else:
        expr, new_answer = generate_captcha()
        cur.execute("UPDATE user_captcha SET expression=?, answer=? WHERE user_id=?", (expr, new_answer, uid))
        conn.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_captcha"))
        bot.send_message(uid,
            "❌ **إجابة خاطئة!**\n\nحل المعادلة:\n"
            f"**{expr} = ?**\n\n📌 أرسل الإجابة كرقم فقط:",
            reply_markup=kb, parse_mode="Markdown")

# ========= معالجة الأزرار الرئيسية =========
recent_purchases = {}
user_states = {}
temp_clients = {}

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    uid = call.from_user.id
    update_user_activity(uid)

    if call.data == "retry_captcha":
        expr, answer = generate_captcha()
        cur.execute("UPDATE user_captcha SET expression=?, answer=? WHERE user_id=?", (expr, answer, uid))
        conn.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_captcha"))
        bot.edit_message_text(
            "🔒 **تحقق أمني** 🔒\n\nللتحقق من أنك لست روبوت، الرجاء حل المعادلة التالية:\n\n"
            f"**{expr} = ?**\n\n📌 أرسل الإجابة كرقم فقط:",
            uid, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        return

    if call.data == "check_sub":
        not_joined = check_subscription(uid)
        if not_joined:
            bot.answer_callback_query(call.id, "❌ ما زلت غير مشترك.", show_alert=True)
            # تحديث الرسالة بنفس القنوات التي لم يشترك فيها
            bot.edit_message_text(
                "⚠️ **يجب الاشتراك في القنوات التالية للمتابعة:**\n\n",
                uid, call.message.message_id, reply_markup=subscription_markup(not_joined), parse_mode="Markdown"
            )
        else:
            bot.delete_message(uid, call.message.message_id)
            # بعد الاشتراك، نتحقق من الكابتشا
            cur.execute("SELECT captcha_passed FROM users WHERE user_id=?", (uid,))
            row = cur.fetchone()
            if not row or row[0] == 0:
                expr, answer = generate_captcha()
                cur.execute("INSERT OR REPLACE INTO user_captcha(user_id, expression, answer) VALUES(?,?,?)", (uid, expr, answer))
                conn.commit()
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="retry_captcha"))
                bot.send_message(uid,
                    "🔒 **تحقق أمني** 🔒\n\nللتحقق من أنك لست روبوت، الرجاء حل المعادلة التالية:\n\n"
                    f"**{expr} = ?**\n\n",
                    reply_markup=kb, parse_mode="Markdown")
            else:
                show_main_menu(uid, call.message)
        return

    elif call.data == "auto_recharge":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📲 شحن آسيا سيل", callback_data="recharge_asia"),
            types.InlineKeyboardButton("🌟 شحن نجوم", callback_data="recharge_stars"),
            types.InlineKeyboardButton("🎟 شحن كود", callback_data="charge_via_code"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
        )
        bot.edit_message_text("⚡ **قسم الشحن:**\n\nاختر وسيلة الشحن المناسبة:", uid, call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    elif call.data == "recharge_stars":
        bot.delete_message(uid, call.message.message_id)
        show_stars_menu(uid)

    elif call.data == "recharge_asia":
        if get_setting('asia_topup_hidden') == 'on' and not is_admin(uid):
            return bot.answer_callback_query(call.id, "❌ هذا الخيار غير متاح حالياً.", show_alert=True)
        admin_num = get_setting('asia_admin_number', '07776326105')
        if not admin_num:
            return bot.answer_callback_query(call.id, "⚠️ الشحن متوقف مؤقتاً.", show_alert=True)
        rate = get_setting('asia_exchange_rate', '1000')
        bot.send_message(uid,
            f"📱 **شحن آسيا سيل**\n\n✨ **سعر الصرف:** `{rate} دينار = 1.00 نقطة`\n\n"
            f"⚙️ **الخطوات:**\n"
            f"1️⃣ أرسل رقمك الآسيا سيل (مثال: 077******)\n"
            f"2️⃣ ستصلك رسالة OTP، أرسلها هنا\n"
            f"3️⃣ اختر المبلغ المطلوب شحنه\n"
            f"4️⃣ سيصلك كود تأكيد التحويل، أرسله هنا\n\n"
            f"سيتم إضافة النقاط تلقائياً إلى حسابك.",
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="main_menu")))
        user_states[uid] = ("asia_user", "wait_phone", str(uuid.uuid4()))
        return

    elif call.data == "charge_via_code":
        user_states[uid] = ("redeem_code_flow",)
        bot.send_message(uid, "🎟 **شحن كود**\n\nأرسل الكود الخاص بك:", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="main_menu")), parse_mode="Markdown")

    elif call.data == "referral":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        ref_reward = get_setting('ref_reward', '0.1')
        ref_text = (
            f"👥 **دعـوة صـديـق:**\n\n"
            f"قم بدعوة أصدقائك للبوت واحصل على **{ref_reward} نقطة** لكل شخص يشترك!\n\n"
            f"🔗 **رابط الإحالة الخاص بك:**\n`{ref_link}`"
        )
        bot.edit_message_text(ref_text, uid, call.message.message_id, parse_mode="Markdown",
                              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")))

    elif call.data == "points":
        points = get_user_points(uid)
        bot.answer_callback_query(call.id, f"رصـيدك: {points} نقطة", show_alert=True)

    elif call.data == "buy_menu":
        kb = types.InlineKeyboardMarkup(row_width=1)
        if get_setting('external_api_status', 'on') == 'on':
            kb.add(types.InlineKeyboardButton("🚀 أرقام عالمية (تفعيل فوري)", callback_data="buy_api_countries"))
        cur.execute("SELECT category_name, COUNT(*) FROM numbers WHERE status='متاح' GROUP BY category_name")
        categories = cur.fetchall()
        if categories:
            for cat_name, count in categories:
                kb.add(types.InlineKeyboardButton(f"📁 {cat_name} | {count} رقم", callback_data=f"show_cat_{cat_name}"))
        if not categories and get_setting('external_api_status', 'on') == 'off':
            bot.answer_callback_query(call.id, "❌ لا توجد أرقام متاحة حالياً.", show_alert=True)
            return
        kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("📱 **اختر الفئة المطلوبة:**\n\n(أرقام الـ API توفر تفعيلاً فورياً لمئات الدول)", uid, call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    elif call.data == "buy_api_countries":
        bot.answer_callback_query(call.id, "⏳ جاري جلب الدول المتاحة...")
        prices = external_api.get_prices()
        if not prices:
            return bot.send_message(uid, "❌ عذراً، لا توجد دول متاحة حالياً في الموقع.")
        kb = types.InlineKeyboardMarkup(row_width=2)
        profit = float(get_setting('external_api_profit', 0.40))
        available_countries = []
        for country_name, operators in prices.items():
            best_price = float('inf')
            total_count = 0
            for op_name, services in operators.items():
                tg = services.get("telegram")
                if not tg:
                    for s_name, s_info in services.items():
                        if "telegram" in s_name.lower():
                            tg = s_info
                            break
                if tg:
                    count = tg.get("count", 0)
                    cost = tg.get("cost", float('inf'))
                    total_count += count
                    if cost < best_price:
                        best_price = cost
            if best_price != float('inf'):
                available_countries.append({'id': country_name, 'price': best_price, 'count': total_count})
        priority_countries = ['canada', 'usa', 'england', 'russia']
        final_list = []
        for pc in priority_countries:
            for i, c in enumerate(available_countries):
                if c['id'].lower() == pc:
                    final_list.append(available_countries.pop(i))
                    break
        available_countries.sort(key=lambda x: (x['count'] > 0, x['count']), reverse=True)
        real_available = [c for c in available_countries if c['count'] > 0]
        final_list.extend(real_available if real_available else available_countries)
        if not final_list:
            final_list = [{'id': 'usa', 'price': 0.5, 'count': 0}, {'id': 'canada', 'price': 0.5, 'count': 0}]
        for c in final_list[:30]:
            cid = c['id']
            price = c['price']
            count = c['count']
            c_info = detect_country_from_number(cid)
            c_name = c_info.get('name', cid.capitalize())
            c_emoji = c_info.get('emoji', '🌍')
            c_display = f"{c_emoji} {c_name} ({count}) | {price + profit:.2f}p"
            kb.add(types.InlineKeyboardButton(c_display, callback_data=f"api_buy_{cid}"))
        kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
        bot.edit_message_text("🌍 **اختر الدولة المطلوبة (SMS):**\n\nيتم تحديث الأسعار والدول تلقائياً بناءً على المخزون.", uid, call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    elif call.data.startswith("api_buy_"):
        country_id = call.data.replace("api_buy_", "")
        buy_external_number(uid, country_id, call.message.message_id, call.id)

    elif call.data.startswith("show_cat_"):
        cat_name = call.data.replace("show_cat_", "")
        cur.execute("SELECT id, number, price, country FROM numbers WHERE category_name=? AND status='متاح' LIMIT 20", (cat_name,))
        nums = cur.fetchall()
        kb = types.InlineKeyboardMarkup(row_width=1)
        for n in nums:
            btn_text = f"📱 {n[3]} | {mask_phone(n[1])} | 💰 {n[2]}ن"
            kb.add(types.InlineKeyboardButton(btn_text, callback_data=f"buy_{n[0]}"))
        kb.add(types.InlineKeyboardButton("🔄 تحديث القائمة", callback_data=f"show_cat_{cat_name}"))
        kb.add(types.InlineKeyboardButton("🔙 رجوع لفئات الأرقام", callback_data="buy_menu"))
        bot.edit_message_text(f"📂 **أرقام فئة {cat_name}:**\n\n✨ اختر الرقم الذي ترغب بشرائه:", uid, call.message.message_id, reply_markup=kb, parse_mode="Markdown")

    elif call.data == "main_menu":
        bot.delete_message(uid, call.message.message_id)
        start(call.message)

    elif call.data == "admin_panel":
        if is_admin(uid):
            show_admin_panel(uid, call.message.message_id)

    elif call.data.startswith("admin_"):
        if is_admin(uid):
            handle_admin_actions(uid, call.data, call.message.message_id, call.id)

    elif call.data.startswith("buy_"):
        num_id = int(call.data.split("_")[1])
        purchase_number(uid, num_id, call.message.message_id, call.id)

    elif call.data.startswith("get_code_"):
        user_id = int(call.data.split("_")[2])
        if user_id != uid:
            bot.answer_callback_query(call.id, "⚠️ هذا الإجراء غير متاح لك.", show_alert=True)
            return
        if uid not in recent_purchases:
            bot.answer_callback_query(call.id, "❌ لا توجد عملية شراء حديثة.", show_alert=True)
            return
        data = recent_purchases[uid]
        bot.answer_callback_query(call.id, "🔍 جاري طلب الكود...", show_alert=False)

        def fetch_code():
            return run_async(fetch_code_from_account(data['session_str'], data['api_id'], data['api_hash']))

        code = fetch_code()

        if code:
            cur.execute("UPDATE history SET code_received=1 WHERE user_id=? AND number=? AND purchase_date=(SELECT MAX(purchase_date) FROM history WHERE user_id=? AND number=?)",
                        (uid, data['number'], uid, data['number']))
            conn.commit()
            full_number = format_phone_full(data['number'])
            message_text = (
                f"✅ **تم الحصول على الكود!**\n\n"
                f"📱 **الرقم:** `{full_number}`\n"
                f"🔢 **الكود:** `{code}`\n"
            )
            if data.get('two_factor'):
                message_text += f"🔐 **التحقق بخطوتين:** `{data['two_factor']}`\n"
            message_text += "\n⚠️ **احفظ الكود جيداً ولا تشاركه مع أي شخص.**"
            bot.send_message(uid, message_text, parse_mode="Markdown")
            bot.answer_callback_query(call.id, "✅ تم إرسال الكود.")
            admin_log = (
                f"💸 **عملية شراء ناجحة!**\n\n"
                f"👤 **المشتري:** {uid}\n"
                f"📱 **الرقم:** `{data['number']}`\n"
                f"💰 **السعر:** {data['price']} نقطة\n"
                f"🌍 **الدولة:** {data['country']}"
            )
            try: bot.send_message(OWNER_ID, admin_log)
            except: pass
            channel_id = ACTIVATION_CHANNEL_ID
            if channel_id:
                receipt = (
                    f"🆕 **تـم شـراء رقـم جـديد**\n\n"
                    f"👤 **المـشـتري:** {mask_id(uid)}\n"
                    f"📱 **الــرقم:** `{mask_phone(data['number'])}`\n"
                    f"🌍 **الـدولة:** {data['country']}\n"
                    f"💰 **السـعر:** {data['price']} نقطة\n"
                    f"⏰ **الوقـت:** {get_current_time()}\n\n"
                    f"✅ تـم التفعيل بنجاح عبر البوت الخاص بنا!"
                )
                try: bot.send_message(channel_id, receipt, parse_mode="Markdown")
                except: pass
        else:
            bot.answer_callback_query(call.id, "⚠️ لم يصل الكود بعد. حاول مرة أخرى خلال دقيقة.", show_alert=True)

    elif call.data.startswith("cancel_purchase_"):
        bot.answer_callback_query(call.id, "⚠️ عذراً، لا يمكن إلغاء العملية أو استرداد الرصيد بعد الشراء.", show_alert=True)
        return

    elif call.data.startswith("logout_"):
        user_id = int(call.data.split("_")[1])
        if user_id != uid:
            bot.answer_callback_query(call.id, "⚠️ هذا الإجراء غير متاح لك.", show_alert=True)
            return
        if uid in recent_purchases:
            del recent_purchases[uid]
        bot.send_message(uid, "👋 **تم تسجيل الخروج بنجاح.**\nيمكنك استخدام /start للعودة.")
        bot.answer_callback_query(call.id)

    elif call.data.startswith("asia_amount_"):
        amount = int(call.data.split("_")[2])
        state = user_states.get(uid)
        if not state or state[0] != "asia_user" or state[1] != "logged_in":
            bot.answer_callback_query(call.id, "⚠️ انتهت الجلسة.", show_alert=True)
            return
        access_token, phone, device_id = state[2], state[3], state[4]
        admin_phone = get_setting('asia_admin_number', '07776326105')
        bot.answer_callback_query(call.id, "⏳ جاري بدء التحويل...", show_alert=False)
        res = asia_api.start_transfer(access_token, amount, admin_phone, device_id)
        pid = asia_api._extract_pid(res)
        if pid:
            user_states[uid] = ("asia_user", "wait_transfer_otp", access_token, pid, amount, device_id)
            bot.edit_message_text(f"📩 **تم إرسال كود تأكيد التحويل**\nأرسل الكود هنا:", uid, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 إلغاء", callback_data="main_menu")))
        else:
            bot.edit_message_text(f"❌ فشل بدء التحويل: {res.get('message', 'خطأ')}", uid, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="auto_recharge")))

    elif call.data in ["asia_set_rate", "asia_set_admin_phone", "asia_toggle_hidden"]:
        if not is_admin(uid): return
        if call.data == "asia_set_rate":
            bot.send_message(uid, "💵 أرسل سعر الصرف الجديد (IQD مقابل 1$):\nمثال: `1300`", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, lambda m: set_config('asia_exchange_rate', m.text.strip()))
        elif call.data == "asia_set_admin_phone":
            bot.send_message(uid, "📞 أرسل رقم المالك الآسيا سيل الجديد (مثال: 07712345678):", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, lambda m: set_config('asia_admin_number', m.text.strip()))
        elif call.data == "asia_toggle_hidden":
            curr = get_setting('asia_topup_hidden', 'off')
            new = 'on' if curr == 'off' else 'off'
            set_config('asia_topup_hidden', new)
            bot.answer_callback_query(call.id, f"✅ زر آسيا سيل الآن: {'مخفي' if new=='on' else 'ظاهر'}", show_alert=True)
            show_admin_panel(uid, call.message.message_id)

# ========= دوال البيع =========
def show_numbers_direct(uid, message_id):
    cur.execute("SELECT id, number, price, country FROM numbers WHERE service='تيليجرام' AND status='متاح' ORDER BY price ASC LIMIT 20")
    nums = cur.fetchall()
    if not nums:
        bot.edit_message_text("❌ **لا توجد أرقام متاحة حالياً.**\nيمكنك المحاولة لاحقاً.", uid, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")), parse_mode="Markdown")
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for n in nums:
        kb.add(types.InlineKeyboardButton(f"{n[3]} {mask_phone(n[1])} - {n[2]} نقطة", callback_data=f"buy_{n[0]}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_menu"))
    bot.edit_message_text("📱 **قائمة الحسابات المتاحة:**\n\nاختر الحساب المناسب:", uid, message_id, reply_markup=kb, parse_mode="Markdown")

def purchase_number(uid, num_id, message_id, callback_id):
    points = get_user_points(uid)
    cur.execute("SELECT number, code, two_factor, price, service, country, session_str, api_id, api_hash, is_2fa FROM numbers WHERE id=? AND status='متاح'", (num_id,))
    num = cur.fetchone()
    if not num:
        bot.answer_callback_query(callback_id, "❌ الحساب غير متاح حالياً")
        return
    number, code, two_factor, price, service, country, session_str, api_id, api_hash, is_2fa = num
    if points < price:
        bot.answer_callback_query(callback_id, f"❌ رصيدك غير كافٍ!\nرصيدك: {points} نقطة\nالسعر: {price} نقطة", show_alert=True)
        return
    remove_points_from_user(uid, price)
    cur.execute("UPDATE numbers SET status='مباع' WHERE id=?", (num_id,))
    cur.execute("""INSERT INTO history(user_id, number, code, two_factor, price, country, service, purchase_date, session_str, api_id, api_hash, is_2fa, code_received, activation_sent)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0,0)""",
                (uid, number, code, two_factor, price, country, service, get_current_time(), session_str, api_id, api_hash, is_2fa))
    conn.commit()
    bot.delete_message(uid, message_id)
    recent_purchases[uid] = {
        'number': number, 'code': code, 'two_factor': two_factor, 'price': price,
        'country': country, 'service': service, 'session_str': session_str,
        'api_id': api_id, 'api_hash': api_hash, 'is_2fa': is_2fa
    }
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔍 طلب الكود", callback_data=f"get_code_{uid}"))
    kb.add(types.InlineKeyboardButton("🚪 تسجيل الخروج", callback_data=f"logout_{uid}"))
    bot.send_message(uid,
        f"✅ **تم شراء الرقم بنجاح!**\n\n"
        f"📱 **الرقم:** `{format_phone_full(number)}`\n"
        f"💰 **السعر:** {price} نقطة\n"
        f"🌍 **الدولة:** {country}\n\n"
        f"يمكنك الآن طلب الكود بالضغط على الزر أدناه.",
        reply_markup=kb, parse_mode="Markdown")

def buy_external_number(uid, country_id, message_id, callback_id):
    bot.answer_callback_query(callback_id, "⏳ جاري جلب الأسعار...")
    prices = external_api.get_prices()
    try:
        country_data = prices.get(country_id, {})
        best_price = float('inf')
        best_op = "any"
        for op, services in country_data.items():
            tg = services.get("telegram")
            if tg and tg.get("cost", float('inf')) < best_price:
                best_price = tg.get("cost")
                best_op = op
        if best_price == float('inf'):
            bot.send_message(uid, "❌ عذراً، لا يوجد مخزون حالياً لهذه الدولة.")
            return
        cost_usd = best_price
        profit = float(get_setting('external_api_profit', 0.40))
        total_price = cost_usd + profit
        user_points = get_user_points(uid)
        if user_points < total_price:
            bot.send_message(uid, f"❌ رصيدك غير كافٍ!\nالسعر: {total_price:.2f} نقطة\nرصيدك: {user_points:.2f} نقطة")
            return
        bot.edit_message_text("⏳ جاري شراء الرقم من الموقع...", uid, message_id)
        res = external_api.buy_number(country_id, "telegram", best_op)
        if "id" not in res:
            bot.send_message(uid, f"❌ فشل الشراء: {res.get('error', 'السيرفر مشغول')}")
            return
        order_id = res.get("id")
        phone = res.get("phone")
        remove_points_from_user(uid, total_price)
        cur.execute("""INSERT INTO external_api_orders(order_id, user_id, phone, country_id, service, price, status)
                       VALUES(?,?,?,?,?,?,?)""", (str(order_id), uid, phone, country_id, "telegram", total_price, "waiting"))
        conn.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔍 تحديث الكود", callback_data=f"ext_check_{order_id}"))
        kb.add(types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data=f"ext_cancel_{order_id}"))
        bot.edit_message_text(
            f"🚀 **تم حجز الرقم بنجاح!**\n\n"
            f"📱 **الرقم:** `{phone}`\n"
            f"💰 **السعر:** {total_price:.2f} نقطة\n\n"
            f"⏳ بانتظار وصول الكود... اضغط على الزر أدناه للتحديث.",
            uid, message_id, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(uid, f"⚠️ حدث خطأ غير متوقع: {str(e)}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("ext_check_") or c.data.startswith("ext_cancel_"))
def handle_ext_actions(call):
    uid = call.from_user.id
    if call.data.startswith("ext_check_"):
        order_id = call.data.replace("ext_check_", "")
        res = external_api.check_order(order_id)
        status = res.get("status")
        sms_list = res.get("sms", [])
        code = sms_list[0].get("code") if sms_list else None
        if code:
            cur.execute("UPDATE external_api_orders SET status='completed', code=? WHERE order_id=?", (code, order_id))
            conn.commit()
            external_api.finish_order(order_id)
            cur.execute("SELECT phone, price FROM external_api_orders WHERE order_id=?", (order_id,))
            phone, price = cur.fetchone()
            bot.edit_message_text(
                f"✅ **وصل الكود بنجاح!**\n\n"
                f"📱 **الرقم:** `{phone}`\n"
                f"🔢 **الكود:** `{code}`\n\n"
                f"شكراً لاستخدامك بوتنا!",
                uid, call.message.message_id, parse_mode="Markdown")
            channel_id = ACTIVATION_CHANNEL_ID
            if channel_id:
                receipt = (
                    f"🆕 **تـم شـراء رقـم جـديد (SMS)**\n\n"
                    f"👤 **المـشـتري:** {mask_id(uid)}\n"
                    f"📱 **الــرقم:** `{mask_phone(phone)}`\n"
                    f"💰 **السـعر:** {price:.2f} نقطة\n"
                    f"✅ تـم التفعيل بنجاح!"
                )
                try: bot.send_message(channel_id, receipt, parse_mode="Markdown")
                except: pass
        elif status == "CANCELED" or status == "TIMEOUT":
            cur.execute("SELECT price, status FROM external_api_orders WHERE order_id=?", (order_id,))
            row = cur.fetchone()
            if row and row[1] == 'waiting':
                add_points_to_user(uid, row[0])
                cur.execute("UPDATE external_api_orders SET status='canceled' WHERE order_id=?", (order_id,))
                conn.commit()
                bot.edit_message_text("❌ تم إلغاء الطلب لعدم وصول الكود، وتم إعادة النقاط لرصيدك.", uid, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "⏳ لم يصل الكود بعد...", show_alert=False)
    elif call.data.startswith("ext_cancel_"):
        order_id = call.data.replace("ext_cancel_", "")
        res = external_api.cancel_order(order_id)
        if res.get("status") == "CANCELED" or "success" in str(res).lower():
            cur.execute("SELECT price, status FROM external_api_orders WHERE order_id=?", (order_id,))
            row = cur.fetchone()
            if row and row[1] == 'waiting':
                add_points_to_user(uid, row[0])
                cur.execute("UPDATE external_api_orders SET status='canceled' WHERE order_id=?", (order_id,))
                conn.commit()
                bot.edit_message_text("✅ تم إلغاء الطلب بنجاح وإعادة النقاط لرصيدك.", uid, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ لا يمكن الإلغاء حالياً (ربما وصل الكود أو انتهى الوقت)", show_alert=True)

# ========= إضافة الأرقام =========
def start_add_number(uid):
    user_states[uid] = ("add_number", "wait_phone")
    msg = (
        "📞 **أرسل رقم الهاتف مع رمز الدولة (مثال: +96477...)**\n\n"
        "💡 **ملاحظة للأرقام الكندية:** أرسل الرقم يبدأ بـ `12` بدلاً من `1` لتمييزه عن الأمريكي.\n"
        "مثال: `1222666...`"
    )
    bot.send_message(uid, msg, parse_mode="Markdown")

def add_number_step(uid, text):
    state = user_states.get(uid)
    if not state or state[0] != "add_number": return
    if state[1] == "wait_phone":
        phone = text.strip().lstrip('+')
        if not phone.isdigit():
            bot.send_message(uid, "❌ رقم غير صحيح.")
            return
        telegram_phone = phone
        if phone.startswith('12'):
            telegram_phone = '1' + phone[2:]
        client = TelegramClient(StringSession(), MY_API_ID, MY_API_HASH)
        temp_clients[uid] = client
        bot.send_message(uid, "⏳ جاري الاتصال بتيليجرام وإرسال الكود...")
        try:
            success = run_async(send_code_async(client, telegram_phone))
            if success:
                user_states[uid] = ("add_number", "wait_code", phone)
                bot.send_message(uid, "📩 تم إرسال الكود بنجاح! أرسله هنا:")
            else:
                bot.send_message(uid, "❌ فشل إرسال الكود. قد يكون الرقم محظوراً أو الـ API غير صحيح.")
                del temp_clients[uid]
                del user_states[uid]
        except Exception as e:
            bot.send_message(uid, f"⚠️ حدث خطأ أثناء الاتصال: {str(e)}")
            del temp_clients[uid]
            del user_states[uid]
    elif state[1] == "wait_code":
        phone = state[2]
        code = text.strip()
        # ✅ إزالة المسافات من الكود (مثال: "1 3 4 7" -> "1347")
        code = code.replace(" ", "")
        client = temp_clients.get(uid)
        telegram_phone = phone
        if phone.startswith('12'):
            telegram_phone = '1' + phone[2:]
        res = run_async(verify_code_async(client, telegram_phone, code))
        if res == True:
            finish_add_number(uid, phone, client)
        elif res == "2fa_required":
            user_states[uid] = ("add_number", "wait_2fa", phone)
            bot.send_message(uid, "🔐 الحساب محمي بكلمة سر. أرسلها:")
        else:
            bot.send_message(uid, "❌ كود خاطئ.")
    elif state[1] == "wait_2fa":
        phone = state[2]
        password = text.strip()
        # ✅ إزالة المسافات من كلمة السر أيضاً
        password = password.replace(" ", "")
        client = temp_clients.get(uid)
        res = run_async(verify_2fa_async(client, password))
        if res:
            finish_add_number(uid, phone, client, password)
        else:
            bot.send_message(uid, "❌ كلمة سر خاطئة.")
    elif state[1] == "wait_price_cat":
        process_price_cat(uid, text)

def finish_add_number(uid, phone, client, password=""):
    session_str = client.session.save()
    country_info = detect_country_from_number(phone)
    country = country_info['name']
    final_phone = phone
    if phone.startswith('12'):
        final_phone = '1' + phone[2:]
    phone = final_phone
    try:
        time.sleep(2)
        device = get_random_device()
        client.device_model = device['model']
        client.system_version = device['os']
        client.app_version = "10.9.1"
    except:
        pass
    new_pwd = "WAAD"
    try:
        run_async(client.edit_2fa(new_password=new_pwd, current_password=password if password else None))
        password = new_pwd
    except Exception as e:
        print(f"Error changing 2FA: {e}")
    user_states[uid] = ("add_number", "wait_price_cat", phone, session_str, country, password)
    bot.send_message(uid, "💰 **أرسل السعر والفئة (مثال: 10 | 2026)**", parse_mode="Markdown")

def process_price_cat(uid, text):
    state = user_states.get(uid)
    try:
        price, cat = text.split('|')
        price = float(price.strip())
        cat = cat.strip()
        phone, session_str, country, password = state[2], state[3], state[4], state[5]
        cur.execute("""INSERT INTO numbers(number, price, country, category_name, session_str, api_id, api_hash, two_factor, added_by, added_date)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (phone, price, country, cat, session_str, MY_API_ID, MY_API_HASH, password, uid, get_current_time()))
        conn.commit()
        bot.send_message(uid, f"✅ تم إضافة الرقم {phone} بنجاح في فئة {cat}!")
        del user_states[uid]
        if uid in temp_clients:
            run_async_void(disconnect_client_async(temp_clients[uid]))
            del temp_clients[uid]
    except:
        bot.send_message(uid, "❌ خطأ في الصيغة. استخدم: `السعر | الفئة`")

# ========= لوحة التحكم =========
def show_admin_panel(uid, message_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ إضافة رقم", callback_data="admin_add_num_start"),
        types.InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")
    )
    kb.add(types.InlineKeyboardButton("🔐 توحيد كلمة السر (WAAD)", callback_data="admin_fix_2fa"))
    kb.add(
        types.InlineKeyboardButton("📢 قنوات الإجباري", callback_data="admin_channels"),
        types.InlineKeyboardButton("➕ إضافة نقاط", callback_data="admin_add_pts")
    )
    kb.add(
        types.InlineKeyboardButton("➖ خصم نقاط", callback_data="admin_rem_pts"),
        types.InlineKeyboardButton("🎟 إنشاء كود", callback_data="admin_create_code")
    )
    kb.add(
        types.InlineKeyboardButton("⚙️ إعدادات آسيا سيل", callback_data="admin_asia_settings"),
        types.InlineKeyboardButton("🔔 إعدادات قناة التفعيل", callback_data="admin_activation_channel")
    )
    kb.add(
        types.InlineKeyboardButton("🚀 إعدادات الـ API الخارجي", callback_data="admin_external_api"),
        types.InlineKeyboardButton("🌟 سعر النجوم", callback_data="admin_star_price")
    )
    kb.add(
        types.InlineKeyboardButton("🎁 مكافأة الإحالة", callback_data="admin_ref_reward")
    )
    kb.add(types.InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu"))
    bot.edit_message_text("⚙️ **لوحة التحكم:**\n\nاختر الإجراء المطلوب:", uid, message_id, reply_markup=kb, parse_mode="Markdown")

def handle_admin_actions(uid, action, message_id, callback_id):
    if action == "admin_add_num_start":
        start_add_number(uid)
        bot.answer_callback_query(callback_id, "📞 أرسل رقم الهاتف", show_alert=False)
        return
    elif action == "admin_stats":
        cur.execute("SELECT COUNT(*) FROM users")
        u_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM numbers WHERE status='متاح'")
        n_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM history")
        s_count = cur.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT SUM(price) FROM history WHERE purchase_date LIKE ?", (f"{today}%",))
        today_sales = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM external_api_orders WHERE status='completed'")
        api_sales_count = cur.fetchone()[0]
        cur.execute("SELECT SUM(price) FROM external_api_orders WHERE status='completed'")
        api_total_sales = cur.fetchone()[0] or 0
        stats_text = (
            f"📊 **إحصائيات البوت:**\n\n"
            f"👥 **المستخدمين:** `{u_count}`\n"
            f"📱 **الأرقام اليدوية المتاحة:** `{n_count}`\n"
            f"✅ **الأرقام اليدوية المباعة:** `{s_count}`\n"
            f"🌐 **أرقام SMS المباعة (API):** `{api_sales_count}`\n"
            f"💰 **مجموع مبيعات اليوم:** `{today_sales + api_total_sales:.2f} نقطة`"
        )
        bot.edit_message_text(stats_text, uid, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙", callback_data="admin_panel")), parse_mode="Markdown")
    elif action == "admin_star_price":
        msg = bot.send_message(uid, "🌟 **أرسل سعر النجمة الواحدة (كم نقطة تساوي؟)**\nمثال: `20`")
        bot.register_next_step_handler(msg, lambda m: set_config('star_price', m.text.strip()))
    elif action == "admin_ref_reward":
        msg = bot.send_message(uid, "🎁 **أرسل قيمة مكافأة الإحالة (نقاط)**\nمثال: `0.5`")
        bot.register_next_step_handler(msg, lambda m: set_config('ref_reward', m.text.strip()))
    elif action == "admin_channels":
        cur.execute("SELECT channel_username FROM mandatory_channels")
        channels = cur.fetchall()
        text = "📢 **قنوات الاشتراك الإجباري الحالية:**\n\n"
        if channels:
            for (ch,) in channels:
                text += f"🔹 @{ch}\n"
        else:
            text += "لا توجد قنوات حالياً"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="admin_add_channel"))
        kb.add(types.InlineKeyboardButton("🗑️ حذف قناة", callback_data="admin_del_channel"))
        kb.add(types.InlineKeyboardButton("🗑️ مسح الكل", callback_data="admin_clear_channels"))
        kb.add(types.InlineKeyboardButton("🔙", callback_data="admin_panel"))
        bot.edit_message_text(text, uid, message_id, reply_markup=kb, parse_mode="Markdown")
    elif action == "admin_add_channel":
        msg = bot.send_message(uid, "📝 **أرسل معرف القناة (بدون @)**\nمثال: `taf3ila`")
        bot.register_next_step_handler(msg, process_add_channel)
    elif action == "admin_del_channel":
        cur.execute("SELECT channel_username FROM mandatory_channels")
        channels = cur.fetchall()
        if not channels:
            bot.answer_callback_query(callback_id, "❌ لا توجد قنوات لحذفها.", show_alert=True)
            return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for (ch,) in channels:
            kb.add(types.InlineKeyboardButton(f"🗑️ @{ch}", callback_data=f"do_del_channel:{ch}"))
        kb.add(types.InlineKeyboardButton("🔙", callback_data="admin_channels"))
        bot.edit_message_text("🗑️ **اختر القناة لحذفها:**", uid, message_id, reply_markup=kb, parse_mode="Markdown")
    elif action.startswith("do_del_channel:"):
        ch = action.split(":", 1)[1]
        cur.execute("DELETE FROM mandatory_channels WHERE channel_username=?", (ch,))
        conn.commit()
        bot.answer_callback_query(callback_id, f"✅ تم حذف @{ch}", show_alert=True)
        show_admin_panel(uid, message_id)
    elif action == "admin_clear_channels":
        cur.execute("DELETE FROM mandatory_channels")
        conn.commit()
        bot.answer_callback_query(callback_id, "✅ تم مسح جميع القنوات", show_alert=True)
        show_admin_panel(uid, message_id)
    elif action == "admin_add_pts":
        msg = bot.send_message(uid, "📝 **أرسل: أيدي المستخدم | عدد النقاط**")
        bot.register_next_step_handler(msg, lambda m: process_point_change(m, "add"))
    elif action == "admin_rem_pts":
        msg = bot.send_message(uid, "📝 **أرسل: أيدي المستخدم | عدد النقاط**")
        bot.register_next_step_handler(msg, lambda m: process_point_change(m, "rem"))
    elif action == "admin_create_code":
        msg = bot.send_message(uid, "🎟 **أرسل قيمة الكود (نقاط):**")
        bot.register_next_step_handler(msg, process_create_code)
    elif action == "admin_asia_settings":
        curr_rate = get_setting('asia_exchange_rate', '1000')
        curr_num = get_setting('asia_admin_number', '07776326105')
        hide_status = "مخفي" if get_setting('asia_topup_hidden', 'off') == 'on' else "ظاهر"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💵 تعديل سعر الصرف", callback_data="asia_set_rate"))
        kb.add(types.InlineKeyboardButton("📞 تعديل رقم المالك", callback_data="asia_set_admin_phone"))
        kb.add(types.InlineKeyboardButton(f"🙈 إخفاء/إظهار زر الشحن ({hide_status})", callback_data="asia_toggle_hidden"))
        kb.add(types.InlineKeyboardButton("🔙", callback_data="admin_panel"))
        bot.edit_message_text(f"⚙️ **إعدادات آسيا سيل**\n\n💰 سعر الصرف الحالي: `{curr_rate} دينار = 1 نقطة`\n📞 رقم المالك: `{curr_num}`\n👁 زر الشحن: {hide_status}", uid, message_id, reply_markup=kb, parse_mode="Markdown")
    elif action == "admin_activation_channel":
        current_id = get_setting('activation_channel_id', 'غير محدد')
        current_url = get_setting('activation_channel_url', 'غير محدد')
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📝 تعيين معرف القناة", callback_data="set_channel_id"))
        kb.add(types.InlineKeyboardButton("🔗 تعيين رابط القناة", callback_data="set_channel_url"))
        kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
        bot.edit_message_text(f"🔔 **إعدادات قناة التفعيلات**\n\n🆔 معرف القناة: `{current_id}`\n🔗 رابط القناة: {current_url}", uid, message_id, reply_markup=kb, parse_mode="Markdown")
    elif action == "set_channel_id":
        msg = bot.send_message(uid, "📝 **أرسل معرف القناة (ID)**")
        bot.register_next_step_handler(msg, lambda m: set_config('activation_channel_id', m.text.strip()))
    elif action == "set_channel_url":
        msg = bot.send_message(uid, "🔗 **أرسل رابط القناة**")
        bot.register_next_step_handler(msg, lambda m: set_config('activation_channel_url', m.text.strip()))
    elif action == "admin_external_api":
        api_key = get_setting('external_api_key', 'غير محدد')
        profit = get_setting('external_api_profit', '0.40')
        status = "متصل ✅" if get_setting('external_api_status', 'on') == 'on' else "متوقف ❌"
        balance_info = external_api.get_balance()
        balance = balance_info.get('balance', 'خطأ في الجلب')
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("🔑 تغيير الـ API Key", callback_data="ext_set_key"),
            types.InlineKeyboardButton("💰 تعديل هامش الربح", callback_data="ext_set_profit"),
            types.InlineKeyboardButton(f"🔌 تشغيل/إيقاف ({status})", callback_data="ext_toggle_status"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")
        )
        text = (
            f"🚀 **إعدادات الـ API الخارجي (5SIM)**\n\n"
            f"🔑 الـ API Key: `{api_key[:10]}...`\n"
            f"💰 هامش الربح المضاف: `{profit} نقطة`\n"
            f"📡 الحالة: {status}\n"
            f"💳 رصيد الموقع: `{balance}`"
        )
        bot.edit_message_text(text, uid, message_id, reply_markup=kb, parse_mode="Markdown")
    elif action == "ext_set_key":
        msg = bot.send_message(uid, "🔑 **أرسل الـ API Key الجديد:**")
        bot.register_next_step_handler(msg, lambda m: set_config('external_api_key', m.text.strip()))
    elif action == "ext_set_profit":
        msg = bot.send_message(uid, "💰 **أرسل هامش الربح الإضافي (بالنقاط):**\nمثال: `0.2` تعني إضافة 20 سنت فوق سعر الموقع.")
        bot.register_next_step_handler(msg, lambda m: set_config('external_api_profit', m.text.strip()))
    elif action == "ext_toggle_status":
        curr = get_setting('external_api_status', 'on')
        new = 'off' if curr == 'on' else 'on'
        set_config('external_api_status', new)
        bot.answer_callback_query(callback_id, f"✅ تم {'إيقاف' if new=='off' else 'تشغيل'} الـ API الخارجي", show_alert=True)
        handle_admin_actions(uid, "admin_external_api", message_id, callback_id)
    elif action == "admin_fix_2fa":
        bot.answer_callback_query(callback_id, "⏳ جاري البدء في توحيد كلمات السر...")
        def run_fix():
            try:
                s, f = run_async(change_all_2fa_passwords("WAAD"))
                bot.send_message(uid, f"✅ **اكتملت العملية!**\n\nتم تحديث: `{s}` حساب\nفشل: `{f}` حساب\nكلمة السر الجديدة: `WAAD`")
            except Exception as e:
                bot.send_message(uid, f"❌ فشل تنفيذ العملية: {str(e)}")
        threading.Thread(target=run_fix, daemon=True).start()

def process_add_channel(msg):
    try:
        ch_username = msg.text.strip().replace('@', '').replace('https://t.me/', '').replace('t.me/', '')
        if not ch_username:
            bot.send_message(msg.from_user.id, "❌ معرف القناة غير صالح.")
            return
        cur.execute("INSERT INTO mandatory_channels (channel_username) VALUES (?)", (ch_username,))
        conn.commit()
        bot.send_message(msg.from_user.id, f"✅ تم إضافة القناة @{ch_username} بنجاح!")
    except sqlite3.IntegrityError:
        bot.send_message(msg.from_user.id, "⚠️ القناة موجودة بالفعل.")
    except Exception as e:
        bot.send_message(msg.from_user.id, f"❌ خطأ: {str(e)}")

def process_point_change(msg, mode):
    try:
        target_id, amount = msg.text.split('|')
        target_id, amount = int(target_id.strip()), float(amount.strip())
        if mode == "add": add_points_to_user(target_id, amount)
        else: remove_points_from_user(target_id, amount)
        bot.send_message(msg.from_user.id, "✅ تم العملية بنجاح!")
    except: bot.send_message(msg.from_user.id, "❌ خطأ في الصيغة!")

def process_create_code(msg):
    try:
        amount = float(msg.text.strip())
        code = str(uuid.uuid4())[:10].upper()
        cur.execute("INSERT INTO charge_codes(code, amount, created_by, is_used) VALUES(?,?,?,0)", (code, amount, msg.from_user.id))
        conn.commit()
        bot.send_message(msg.from_user.id, f"🎟 كود جديد: `{code}` بقيمة {amount} نقطة")
    except: bot.send_message(msg.from_user.id, "❌ أرسل رقماً صحيحاً")

# ========= معالجة الرسائل النصية =========
@bot.message_handler(func=lambda m: True)
def handle_all_messages(msg):
    uid = msg.from_user.id
    text = msg.text.strip()
    if uid in user_states:
        state = user_states[uid]
        if state[0] == "redeem_code_flow":
            code = text.upper()
            cur.execute("SELECT amount, is_used FROM charge_codes WHERE code=?", (code,))
            row = cur.fetchone()
            if row and row[1] == 0:
                add_points_to_user(uid, row[0])
                cur.execute("UPDATE charge_codes SET is_used=1 WHERE code=?", (code,))
                conn.commit()
                bot.send_message(uid, f"✅ تم شحن {row[0]} نقطة!")
            else: bot.send_message(uid, "❌ كود غير صالح.")
            del user_states[uid]; return
        elif state[0] == "asia_user":
            if state[1] == "wait_phone":
                if not re.match(r'^0?7[3-9]\d{8}$', text):
                    bot.send_message(uid, "❌ رقم غير صحيح.")
                    return
                device_id = state[2]
                res = asia_api.login(text, device_id)
                pid = asia_api._extract_pid(res)
                if pid:
                    user_states[uid] = ("asia_user", "wait_otp", pid, text, device_id)
                    bot.send_message(uid, "📩 **تم إرسال كود التحقق (OTP)**\nأرسله هنا الآن:")
                else:
                    msg_err = res.get('message') or res.get('error') or "خطأ غير معروف"
                    bot.send_message(uid, f"❌ **فشل في الاتصال:**\n`{msg_err}`\n\nحاول مرة أخرى لاحقاً.")
                return
            elif state[1] == "wait_otp":
                pid, phone, device_id = state[2], state[3], state[4]
                res = asia_api.validate_sms(pid, text, device_id)
                token = res.get("token") or res.get("access_token")
                if token:
                    user_states[uid] = ("asia_user", "logged_in", token, phone, device_id)
                    rate = float(get_setting('asia_exchange_rate', 1000))
                    kb = types.InlineKeyboardMarkup(row_width=2)
                    for amt in [1000, 2000, 5000, 10000]:
                        points = amt / rate
                        kb.add(types.InlineKeyboardButton(f"💰 {amt} د.ع = {points:.2f} نقطة", callback_data=f"asia_amount_{amt}"))
                    bot.send_message(uid, f"✅ تم الدخول بنجاح!\n\n✨ سعر الصرف: **{rate} دينار = 1.00 نقطة**\nاختر المبلغ الذي ترغب بشحنه:", reply_markup=kb)
                else: bot.send_message(uid, "❌ كود خاطئ.")
                return
            elif state[1] == "wait_transfer_otp":
                access_token, pid, amount, device_id = state[2], state[3], state[4], state[5]
                res = asia_api.confirm_transfer(access_token, pid, text, device_id)
                if res.get("success") or res.get("status") == "SUCCESS" or "نجاح" in str(res.get("message", "")):
                    rate = float(get_setting('asia_exchange_rate', 1000))
                    points_to_add = float(amount) / rate
                    add_points_to_user(uid, points_to_add)
                    bot.send_message(uid, f"✅ **تم الشحن بنجاح!**\n\nتم إضافة `{points_to_add:.2f}` نقطة إلى رصيدك بنجاح.")
                    admin_notify = (
                        f"💳 **عملية شحن آسيا ناجحة!**\n\n"
                        f"👤 **المستخدم:** `{uid}`\n"
                        f"💰 **المبلغ:** `{amount} دينار`\n"
                        f"💵 **سعر الصرف:** `{rate}`\n"
                        f"✨ **النقاط المضافة:** `{points_to_add:.2f}`"
                    )
                    try: bot.send_message(OWNER_ID, admin_notify)
                    except: pass
                    del user_states[uid]
                else:
                    msg_err = res.get('message') or "فشل في تأكيد التحويل"
                    bot.send_message(uid, f"❌ **فشل التأكيد:**\n`{msg_err}`")
                return
        elif state[0] == "add_number":
            add_number_step(uid, text)
            return

# ========= تشغيل البوت =========
if __name__ == "__main__":
    def start_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()
    threading.Thread(target=start_loop, daemon=True).start()
    print("KAYNO")
    bot.infinity_polling()