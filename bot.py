from google import genai
import requests
import random
import os
from instagrapi import Client

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
PEXELS_API_KEY = "ETWbUEAkpzHrKYgZ068n9byjx2qBF6u8S5bFiyY9oCxElaivhqpFCygP"

# تلگرام
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
TELEGRAM_CHANNEL_ID = "@shetabafza"

# بله
BALE_BOT_TOKEN = "1384853358:6_bxC3Qwe3V07cWJytRgY9WdgscJ8vW4XQE"
BALE_CHANNEL_ID = "@shetabafza_ir" 

# اینستاگرام
IG_USERNAME = "shetabafza_ir"
IG_PASSWORD = "9EXiJVTP"
# ============================================

def generate_post_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # دستور بهینه‌شده برای ایجاد تعادل بین کوتاهی متن و انتقال کامل پیام
    prompt = """
    تو یک متخصص ارشد دیجیتال مارکتینگ برای 'شتاب‌افزا' هستی.
    یک پست کاربردی، جذاب و خوش‌خوان در مورد ترفندهای رشد کسب‌وکار بنویس.
    
    خروجی دقیقاً با این فرمت:
    متن: [کپشنی بنویس که نه خسته‌کننده و طولانی باشد، و نه آن‌قدر کوتاه که پیام اصلی منتقل نشود. 
    ساختار دقیق: یک جمله جذاب به عنوان قلاب (تیتر)، سپس یک پاراگراف کوتاه (۳ الی ۴ خط) برای انتقال کامل و دقیق مفهوم بازاریابی، و در نهایت یک جمله برای نتیجه‌گیری.
    حجم کل کپشن حدود ۷۰ تا ۱۰۰ کلمه باشد. پاراگراف‌ها را با فاصله از هم جدا کن تا در موبایل راحت خوانده شود. از ایموجی‌های مناسب استفاده کن. از هیچ‌گونه تگ HTML یا ستاره (*) استفاده نکن تا در همه پلتفرم‌ها به درستی نمایش داده شود.]
    موضوع_تصویر: [یک عبارت انگلیسی برای جستجوی عکس مثل: marketing team, business growth, startup success]
    """
    
    try:
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        parts = response.text.split("موضوع_تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_topic = parts[1].strip()
        return caption_part, image_topic
    except Exception as e:
        print("❌ خطا در تولید متن:", e)
        return None, None

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

def download_image_locally(image_url, file_name="post_image.jpg"):
    response = requests.get(image_url)
    with open(file_name, 'wb') as file:
        file.write(response.content)
    return file_name

def send_to_telegram(caption, image_url):
    print("در حال ارسال به تلگرام...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {TELEGRAM_CHANNEL_ID}"}
    requests.post(url, data=payload)

def send_to_bale(caption, image_url):
    print("در حال ارسال به بله...")
    url = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": BALE_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {BALE_CHANNEL_ID}"}
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ پست بله با موفقیت منتشر شد.")
    else:
        print(f"❌ خطا در بله: {response.text}")

def send_to_instagram(caption, image_path):
    print("در حال اتصال به اینستاگرام...")
    try:
        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.photo_upload(image_path, caption)
        print("✅ پست اینستاگرام با موفقیت منتشر شد.")
    except Exception as e:
        print("❌ خطا در ارسال به اینستاگرام:", e)

if __name__ == "__main__":
    print("شروع پروسه ربات چندپلتفرمی شتاب‌افزا...")
    
    base_caption, topic = generate_post_content()
    
    if base_caption and topic:
        image_url = get_pexels_image(topic)
        local_image_path = download_image_locally(image_url)
        
        send_to_telegram(base_caption, image_url)
        send_to_bale(base_caption, image_url)
        send_to_instagram(base_caption, local_image_path)
        
        if os.path.exists(local_image_path):
            os.remove(local_image_path)
            
        print("🎉 عملیات کلی به پایان رسید.")
    else:
        print("❌ عملیات تولید محتوا ناموفق بود.")
