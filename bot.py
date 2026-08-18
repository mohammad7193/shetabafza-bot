import google.generativeai as genai
import requests
import urllib.parse

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_content():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = """
    تو یک متخصص تولید محتوا برای آژانس دیجیتال مارکتینگ 'شتاب‌افزا' هستی.
    یک پست حرفه‌ای طراحی کن. خروجی باید دقیقاً با فرمت زیر باشد و هیچ کلمه اضافه‌ای نداشته باشد:

    متن: [یک کپشن حرفه‌ای، جذاب و مرتبط با ترفندهای دیجیتال مارکتینگ و رشد کسب‌وکار. لحن تخصصی اما روان باشد.]
    تصویر: [یک پرامپت دقیق و حرفه‌ای به زبان انگلیسی برای ساخت عکسی مرتبط با موضوع کپشن. حتماً باید متن فارسی و تیتر اصلی کپشن را به صورت کامل داخل این پرامپت انگلیسی قرار دهی تا روی عکس نوشته شود.]
    """
    
    try:
        response = model.generate_content(prompt)
        text_output = response.text
        
        parts = text_output.split("تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_prompt_part = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        return final_caption, image_prompt_part
    except Exception as e:
        print("خطا در تولید محتوا توسط جمینای:", e)
        return None, None

def send_post_to_telegram(caption, image_prompt):
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("پست با موفقیت منتشر شد!")
    else:
        print("خطا در ارسال:", response.text)

if __name__ == "__main__":
    final_caption, img_prompt = generate_content()
    if final_caption and img_prompt:
        send_post_to_telegram(final_caption, img_prompt)
