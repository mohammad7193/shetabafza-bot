from google import genai
import requests
import urllib.parse

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_post_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # پرامپت حرفه‌ای برای رعایت استانداردهای کپشن‌نویسی تلگرام
    prompt = """
    تو یک متخصص ارشد دیجیتال مارکتینگ و تولید محتوا برای کانال تلگرام 'شتاب‌افزا' هستی.
    یک پست جذاب، حرفه‌ای و تعاملی در مورد یکی از ترفندهای رشد کسب‌وکار، دیجیتال مارکتینگ یا معرفی ارزش محصول بنویس.
    
    خروجی باید دقیقاً با این فرمت باشد و هیچ کلمه اضافه‌ای در ابتدا و انتهای آن نباشد:

    متن: [کپشن تلگرامی با رعایت استانداردهای حرفه‌ای: پاراگراف‌های کوتاه (حداکثر ۲ الی ۳ خط) برای جلوگیری از خستگی مخاطب، استفاده از ایموجی‌های مرتبط و جذاب. 
    نکته بسیار مهم برای بولد کردن: برای برجسته کردن کلمات کلیدی، فقط و فقط از تگ HTML یعنی <b>کلمه مورد نظر</b> استفاده کن و به هیچ وجه از ستاره (*) استفاده نکن.]
    
    تصویر: [یک پرامپت دقیق، باکیفیت و حرفه‌ای به زبان انگلیسی برای ساخت عکس مرتبط با موضوع پست. هیچ متن فارسی یا پرچم و نماد سیاسی داخل این پرامپت قرار نده.]
    """
    
    try:
        # تولید متن و پرامپت تصویر با مدل قدرتمند گوگل
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt
        )
        text_output = response.text
        
        # جداسازی بخش متن و پرامپت تصویر
        parts = text_output.split("تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_prompt_part = parts[1].strip()
        
        # اضافه کردن واترمارک آیدی کانال در انتها
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        
        return final_caption, image_prompt_part
        
    except Exception as e:
        print("❌ خطا در اتصال به جمینای:", e)
        return None, None

def send_to_telegram(caption, image_prompt):
    print("در حال ساخت تصویر و ارسال پست به کانال شتاب‌افزا...")
    
    # تبدیل پرامپت انگلیسی به عکس باکیفیت و واقعی
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML" # فعال‌سازی تگ‌های HTML برای بولد شدن کلمات
    }
    
    response = requests.post(telegram_api_url, data=payload)
    if response.status_code == 200:
        print("✅ پست با موفقیت به صورت عکس واقعی و کپشن استاندارد در کانال منتشر شد!")
    else:
        print("❌ خطا در ارسال به تلگرام:", response.text)

if __name__ == "__main__":
    print("شروع پروسه ربات شتاب‌افزا...")
    caption, img_prompt = generate_post_content()
    if caption and img_prompt:
        send_to_telegram(caption, img_prompt)
    else:
        print("❌ عملیات ناموفق بود.")
