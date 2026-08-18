from google import genai
import requests

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
PEXELS_API_KEY = "ETWbUEAkpzHrKYgZ068n9byjx2qBF6u8S5bFiyY9oCxElaivhqpFCygP"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_post_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
    تو یک متخصص ارشد دیجیتال مارکتینگ و تولید محتوا برای کانال تلگرام 'شتاب‌افزا' هستی.
    یک پست جذاب، حرفه‌ای و تعاملی در مورد یکی از ترفندهای رشد کسب‌وکار، دیجیتال مارکتینگ یا استراتژی‌های بازاریابی بنویس.
    
    خروجی باید دقیقاً با این فرمت باشد و هیچ کلمه اضافه‌ای در ابتدا و انتهای آن نباشد:

    متن: [کپشن تلگرامی با رعایت استانداردهای حرفه‌ای: پاراگراف‌های کوتاه (حداکثر ۲ الی ۳ خط) برای جلوگیری از خستگی مخاطب، استفاده از ایموجی‌های مرتبط و جذاب. برای برجسته کردن کلمات کلیدی، فقط و فقط از تگ HTML یعنی <b>کلمه مورد نظر</b> استفاده کن و به هیچ وجه از ستاره (*) استفاده نکن.]
    
    موضوع_تصویر: [یک عبارت کوتاه و دقیق به زبان انگلیسی برای جستجوی عکس واقعی و مرتبط در Pexels. مثل: marketing strategy, business meeting, growth charts, digital entrepreneur]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt
        )
        text_output = response.text
        
        # جداسازی متن و موضوع تصویر
        parts = text_output.split("موضوع_تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_topic = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        return final_caption, image_topic
        
    except Exception as e:
        print("❌ خطا در تولید متن با جمینای:", e)
        return None, None

def send_to_telegram(caption, image_topic):
    print("در حال جستجوی تصویر زنده و مرتبط از Pexels...")
    
    # جستجوی تصویر زنده از پکسلز بر اساس موضوع کپشن
    headers = {"Authorization": PEXELS_API_KEY}
    search_url = f"https://api.pexels.com/v1/search?query={image_topic}&per_page=1"
    
    try:
        pexels_response = requests.get(search_url, headers=headers).json()
        
        if "photos" in pexels_response and len(pexels_response["photos"]) > 0:
            # دریافت لینک تصویر باکیفیت و بزرگ
            image_url = pexels_response["photos"][0]["src"]["large"]
        else:
            # تصویر پیش‌فرض در صورت عدم پیدا شدن مورد خاص
            image_url = "https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg"
            
    except Exception as e:
        print("⚠️ خطا در دریافت تصویر از پکسلز، استفاده از تصویر پیش‌فرض:", e)
        image_url = "https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg"

    print("در حال ارسال پست نهایی به کانال شتاب‌افزا...")
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML" # فعال‌سازی تگ‌های HTML برای بولد شدن صحیح کلمات
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("✅ پست با موفقیت همراه با عکس زنده و کپشن استاندارد در کانال منتشر شد!")
    else:
        print("❌ خطا در ارسال به تلگرام:", response.text)

if __name__ == "__main__":
    print("شروع پروسه ربات هوشمند شتاب‌افزا...")
    caption, topic = generate_post_content()
    if caption and topic:
        send_to_telegram(caption, topic)
    else:
        print("❌ عملیات ناموفق بود.")

