from google import genai
import requests
import random
import os

# ================= تنظیمات امنیتی (خواندن از سکرت‌های گیت‌هاب) =================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BALE_BOT_TOKEN = os.environ.get("BALE_BOT_TOKEN")

# آیدی کانال‌ها
TELEGRAM_CHANNEL_ID = "@shetabafza"
BALE_CHANNEL_ID = "@shetabafza_ir" 
# =========================================================================

def get_history():
    if os.path.exists("history.txt"):
        with open("history.txt", "r", encoding="utf-8") as file:
            return file.read().strip()
    return "تاریخچه‌ای وجود ندارد. این اولین پست است."

def save_to_history(topic):
    with open("history.txt", "a", encoding="utf-8") as file:
        file.write(f"- {topic}\n")

def generate_post_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    past_topics = get_history()
    
    prompt = f"""
    تو یک متخصص ارشد دیجیتال مارکتینگ برای 'شتاب‌افزا' هستی.
    
    ⚠️ توجه بسیار مهم: این موضوعاتی است که در روزهای گذشته درباره آن‌ها حرف زده‌ای و به هیچ وجه نباید تکرار شوند:
    {past_topics}
    
    لطفاً یک پست جدید بنویس. 
    قانون طلایی: به شدت از کلی‌گویی پرهیز کن! به جای آن، وارد جزئیات شو و یک "تکنیک خرد و بسیار عملی" (مثلاً یک ابزار خاص، یک ترفند در قیمت‌گذاری، یا یک روش دقیق برای افزایش نرخ کلیک) را آموزش بده تا مخاطب احساس کند یک چیز جدید و تخصصی یاد گرفته است.
    
    خروجی باید دقیقاً با این فرمت سه بخشی باشد (بدون کلمات اضافه):
    متن: [یک کپشن جذاب و تخصصی، با پاراگراف‌های کوتاه، همراه با ایموجی. بدون تگ HTML و ستاره. بین ۷۰ تا ۱۰۰ کلمه]
    موضوع_تصویر: [یک عبارت کوتاه انگلیسی برای جستجوی عکس مرتبط]
    موضوع_تاریخچه: [یک عبارت فارسی ۳ تا ۴ کلمه‌ای که مشخص کند امروز درباره چه تکنیک جزئی‌ای حرف زدی]
    """
    
    try:
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        text_output = response.text
        
        caption_part = text_output.split("متن:")[1].split("موضوع_تصویر:")[0].strip()
        image_topic = text_output.split("موضوع_تصویر:")[1].split("موضوع_تاریخچه:")[0].strip()
        history_topic = text_output.split("موضوع_تاریخچه:")[1].strip()
        
        return caption_part, image_topic, history_topic
    except Exception as e:
        print("❌ خطا در تولید متن:", e)
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

def send_to_telegram(caption, image_url):
    print("در حال ارسال به تلگرام...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {TELEGRAM_CHANNEL_ID}"}
    requests.post(url, data=payload)

def send_to_bale(caption, image_url):
    print("در حال ارسال به بله...")
    url = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": BALE_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {BALE_CHANNEL_ID}"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    print("شروع پروسه ربات هوشمند شتاب‌افزا (تلگرام و بله)...")
    
    base_caption, topic, history_topic = generate_post_content()
    
    if base_caption and topic and history_topic:
        save_to_history(history_topic)
        print(f"✅ موضوع '{history_topic}' در تاریخچه ذخیره شد.")
        
        image_url = get_pexels_image(topic)
        
        send_to_telegram(base_caption, image_url)
        send_to_bale(base_caption, image_url)
        
        print("🎉 عملیات کلی به پایان رسید.")
    else:
        print("❌ عملیات تولید محتوا ناموفق بود.")
