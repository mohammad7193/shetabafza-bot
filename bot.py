from google import genai
import requests
import random
import os
import time
import xml.etree.ElementTree as ET

# ================= تنظیمات امنیتی =================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BALE_BOT_TOKEN = os.environ.get("BALE_BOT_TOKEN")

TELEGRAM_CHANNEL_ID = "@shetabafza"
BALE_CHANNEL_ID = "@shetabafza_ir" 
# ===================================================

def get_history():
    if os.path.exists("history.txt"):
        with open("history.txt", "r", encoding="utf-8") as file:
            return file.read().strip()
    return "تاریخچه‌ای وجود ندارد."

def save_to_history(topic):
    with open("history.txt", "a", encoding="utf-8") as file:
        file.write(f"- {topic}\n")

def generate_post_content_with_retry(max_retries=3):
    client = genai.Client(api_key=GEMINI_API_KEY)
    past_topics = get_history()
    
    prompt = f"""
    تو یک متخصص ارشد دیجیتال مارکتینگ برای 'شتاب‌افزا' هستی.
    ⚠️ موضوعات تکراری که نباید استفاده شوند: {past_topics}
    
    یک پست جدید بنویس. 
    قوانین: 
    - یک تکنیک خرد و عملی آموزش بده و از کلی‌گویی پرهیز کن.
    - هیچ داستان خیالی، اغراق یا روایت ساختگی نباید نوشته شود.
    - از کلمات عاشقانه (مثل عشق و عاشقی) مطلقاً استفاده نکن.
    
    خروجی دقیقاً با این فرمت سه بخشی باشد (بدون کلمات اضافه):
    متن: [یک کپشن جذاب و تخصصی، با پاراگراف‌های کوتاه، همراه با ایموجی. بدون تگ HTML و ستاره. بین ۷۰ تا ۱۰۰ کلمه]
    موضوع_تصویر: [دقیقاً ۱ تا ۳ کلمه انگلیسی که «ملموس‌ترین شیء فیزیکی» مرتبط با متن را توصیف کند. توجه: هیچ المانی از شخص، آدم یا چهره نباید باشد! فقط اشیاء. مثلاً: popcorn cinema]
    موضوع_تاریخچه: [یک عبارت فارسی ۳ تا ۴ کلمه‌ای که مشخص کند امروز درباره چه تکنیک جزئی‌ای حرف زدی]
    """
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            text_output = response.text
            
            caption_part = text_output.split("متن:")[1].split("موضوع_تصویر:")[0].strip()
            image_topic = text_output.split("موضوع_تصویر:")[1].split("موضوع_تاریخچه:")[0].strip()
            history_topic = text_output.split("موضوع_تاریخچه:")[1].strip()
            
            return caption_part, image_topic, history_topic
        except Exception as e:
            print(f"⚠️️ تلاش {attempt + 1} برای مارکتینگ ناموفق بود (احتمالاً شلوغی سرور). در حال تلاش مجدد... خطا: {e}")
            time.sleep(15) # 15 ثانیه صبر قبل از تلاش مجدد
            
    print("❌ خطای قطعی در تولید پست مارکتینگ.")
    return None, None, None

def get_pexels_image(image_topic):
    headers = {"Authorization": PEXELS_API_KEY}
    search_url = f"https://api.pexels.com/v1/search?query={image_topic}&per_page=15"
    try:
        response = requests.get(search_url, headers=headers).json()
        if "photos" in response and len(response["photos"]) > 0:
            return random.choice(response["photos"])["src"]["large"]
    except Exception as e:
        print("⚠️ خطا در دریافت تصویر از پکسلز:", e)
    return "https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg"

def fetch_tech_news():
    print("در حال دریافت آخرین اخبار تکنولوژی...")
    feeds = [
        "https://www.zoomit.ir/feed/",
        "https://digiato.com/topic/tech/feed/"
    ]
    try:
        response = requests.get(random.choice(feeds), timeout=15)
        root = ET.fromstring(response.content)
        item = root.find('.//item')
        if item is not None:
            title = item.find('title').text
            link = item.find('link').text
            return title, link
    except Exception as e:
        print("⚠️ خطا در دریافت اخبار RSS:", e)
    return None, None

def generate_news_caption_with_retry(title, link, max_retries=3):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    یک خبر تکنولوژی با این تیتر منتشر شده است: "{title}"
    لطفاً یک کپشن ۲ تا ۳ خطی جذاب برای کانال تلگرام بنویس که این خبر را معرفی کند.
    قوانین: کاملاً خبری و واقعی باشد. هیچ داستان خیالی یا اغراق استفاده نشود. کلمات عاشقانه استفاده نشود.
    در انتها بنویس برای خواندن کامل خبر روی لینک زیر کلیک کنید.
    فقط متن نهایی را به من بده.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            return response.text.strip() + f"\n\n🔗 لینک خبر: {link}"
        except Exception:
            time.sleep(10)
            
    # اگر هوش مصنوعی نتوانست، همان تیتر ساده را برگردان
    return f"📰 {title}\n\n🔗 برای خواندن خبر روی لینک زیر کلیک کنید:\n{link}"

def send_photo_to_channels(caption, image_url):
    print("در حال ارسال عکس به تلگرام و بله...")
    payload_tg = {"chat_id": TELEGRAM_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {TELEGRAM_CHANNEL_ID}"}
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=payload_tg)
    
    payload_bale = {"chat_id": BALE_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {BALE_CHANNEL_ID}"}
    requests.post(f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendPhoto", data=payload_bale)

def send_text_to_channels(text):
    print("در حال ارسال خبر متنی به تلگرام و بله...")
    payload_tg = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text + f"\n\n🆔 {TELEGRAM_CHANNEL_ID}"}
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=payload_tg)
    
    payload_bale = {"chat_id": BALE_CHANNEL_ID, "text": text + f"\n\n🆔 {BALE_CHANNEL_ID}"}
    requests.post(f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendMessage", data=payload_bale)

if __name__ == "__main__":
    print("=== شروع پروسه ربات هوشمند شتاب‌افزا ===")
    
    # ------------------ بخش اول: پست مارکتینگ ------------------
    base_caption, topic, history_topic = generate_post_content_with_retry()
    if base_caption and topic and history_topic:
        save_to_history(history_topic)
        print(f"✅ موضوع '{history_topic}' در تاریخچه ذخیره شد.")
        image_url = get_pexels_image(topic)
        send_photo_to_channels(base_caption, image_url)
    
    # ------------------ بخش دوم: اخبار تکنولوژی ------------------
    news_title, news_link = fetch_tech_news()
    if news_title and news_link:
        news_caption = generate_news_caption_with_retry(news_title, news_link)
        send_text_to_channels(news_caption)
        print("✅ خبر تکنولوژی با موفقیت ارسال شد.")
        
    print("🎉 پروسه امروز به پایان رسید.")
