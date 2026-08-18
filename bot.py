from google import genai
import requests
import random
import urllib.parse

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_post_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
    تو متخصص تولید محتوا برای 'شتاب‌افزا' هستی. یک پست تلگرامی حرفه‌ای درباره دیجیتال مارکتینگ بنویس.
    خروجی باید با فرمت زیر باشد (بدون هیچ حرف اضافه‌ای):

    متن: [کپشن حرفه‌ای با پاراگراف‌های کوتاه. از ایموجی استفاده کن. کلمات کلیدی را با تگ <b>...</b> بولد کن.]
    موضوع_تصویر: [یک عبارت کوتاه انگلیسی که موضوع اصلی کپشن را توصیف می‌کند تا بتوانم عکس مرتبط از آن پیدا کنم. مثلا: business meeting, growth chart, digital marketing team, laptop office]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt
        )
        text_output = response.text
        
        parts = text_output.split("موضوع_تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        topic_part = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        return final_caption, topic_part
    except Exception as e:
        print("❌ خطا در تولید متن:", e)
        return None, None

def send_to_telegram(caption, image_topic):
    # انتخاب تصویر واقعی از Unsplash بر اساس موضوع به همراه پارامتر تصادفی
    random_id = random.randint(1, 100)
    image_url = f"https://source.unsplash.com/featured/?{urllib.parse.quote(image_topic)}&sig={random_id}"
    
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("✅ پست با تصویر باکیفیت و کپشن استاندارد منتشر شد!")
    else:
        print("❌ خطا در ارسال به تلگرام:", response.text)

if __name__ == "__main__":
    caption, topic = generate_post_content()
    if caption and topic:
        send_to_telegram(caption, topic)
