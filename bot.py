from google import genai
import requests
import urllib.parse

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_content():
    # اتصال با ساختار جدید کتابخانه گوگل
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
    تو یک متخصص تولید محتوا برای آژانس دیجیتال مارکتینگ 'شتاب‌افزا' هستی.
    یک خروجی دقیقاً با فرمت زیر بده:
    متن: [یک کپشن حرفه‌ای، جذاب و مرتبط با ترفندهای دیجیتال مارکتینگ. از هیچ نماد ستاره یا هشتگ‌های غیرمتعارف استفاده نکن.]
    تصویر: [یک پرامپت دقیق و حرفه‌ای به زبان انگلیسی برای ساخت عکسی مرتبط. 
    دقت کن: حتماً باید عین متن فارسی تولید شده برای کپشن را بدون هیچگونه خلاصه‌سازی یا حذف، داخل این پرامپت انگلیسی قرار دهی تا مستقیماً روی عکس رندر شود. 
    به هیچ عنوان از پرچم کشورها (مانند پرچم اسرائیل) یا نمادهای سیاسی نامربوط در پرامپت تصویر استفاده نکن.]
    """
    
    try:
        # استفاده از مدل پایدار و سریع flash در API
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        text_output = response.text
        
        parts = text_output.split("تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_prompt_part = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        return final_caption, image_prompt_part
    except Exception as e:
        print("❌ خطا در اتصال به جمینای:", e)
        return None, None

def send_post_to_telegram(caption, image_prompt):
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("✅ پست با موفقیت منتشر شد!")
    else:
        print("❌ خطا در ارسال به تلگرام:", response.text)

if __name__ == "__main__":
    print("در حال اجرای ربات و تولید محتوا...")
    final_caption, img_prompt = generate_content()
    if final_caption and img_prompt:
        send_post_to_telegram(final_caption, img_prompt)
    else:
        print("❌ محتوایی برای ارسال ساخته نشد.")
