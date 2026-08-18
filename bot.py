from google import genai
import requests
import urllib.parse

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_content_and_image():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
    تو یک متخصص ارشد تولید محتوا برای آژانس دیجیتال مارکتینگ 'شتاب‌افزا' هستی. 
    یک پست تلگرامی حرفه‌ای درباره ترفندهای رشد کسب‌وکار یا دیجیتال مارکتینگ بساز.
    خروجی باید دقیقاً با این فرمت باشد:

    متن: [یک کپشن تلگرامی با استانداردهای بالا. شامل پاراگراف‌های کوتاه (حداکثر ۲ الی ۳ خط). از ایموجی‌های مرتبط استفاده کن. برای بولد کردن کلمات کلیدی فقط از تگ <b>کلمه</b> استفاده کن و از ستاره استفاده نکن.]
    
    تصویر: [یک پرامپت دقیق و حرفه‌ای به زبان انگلیسی برای ساخت عکس مرتبط با موضوع. حتماً عین متن فارسی تیتر را درون این پرامپت انگلیسی بگذار تا روی عکس قرار گیرد. از پرچم یا نمادهای سیاسی استفاده نکن.]
    """
    
    try:
        # استفاده از مدل جدید برای تولید متن و پرامپت
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt
        )
        text_output = response.text
        
        parts = text_output.split("تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_prompt_part = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        
        print("در حال تولید تصویر با هوش مصنوعی...")
        # استفاده از مدل تصویرساز جدید گوگل با متد generate_content
        image_result = client.models.generate_content(
            model='imagen-3.0-generate-002',
            contents=image_prompt_part,
        )
        
        # استخراج لینک یا داده تصویر تولید شده و ارسال مستقیم به تلگرام
        # با استفاده از سرویس استاندارد برای ساخت لینک عکس و ارسال به تلگرام به صورت فرمت واقعی عکس
        encoded_prompt = urllib.parse.quote(image_prompt_part)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
        
        return final_caption, image_url
        
    except Exception as e:
        print("❌ خطا در تولید محتوا:", e)
        return None, None

def send_to_telegram(caption, image_url):
    print("در حال ارسال عکس واقعی به کانال تلگرام...")
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("✅ پست با موفقیت به صورت عکس واقعی و کپشن استاندارد در کانال منتشر شد!")
    else:
        print("❌ خطا در ارسال به تلگرام:", response.text)

if __name__ == "__main__":
    print("شروع پروسه ربات شتاب‌افزا...")
    caption, img_url = generate_content_and_image()
    if caption and img_url:
        send_to_telegram(caption, img_url)
    else:
        print("❌ عملیات ناموفق بود.")
