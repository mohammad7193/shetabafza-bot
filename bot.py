from google import genai
import requests

# ================= تنظیمات =================
GEMINI_API_KEY = "AQ.Ab8RN6I6fF8z24IDPkHI2jPf4Ef9QQUOUp0Yv0ShNerVIF19XA"
TELEGRAM_BOT_TOKEN = "8945684990:AAEem4Fuoe0t8I3hBHNy1jwx35lme2aQpSU"
CHANNEL_ID = "@shetabafza"
# ============================================

def generate_content():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
    تو یک متخصص ارشد تولید محتوا برای آژانس دیجیتال مارکتینگ 'شتاب‌افزا' هستی. 
    وظیفه تو نوشتن یک پست تلگرامی بسیار حرفه‌ای و جذاب است. 
    خروجی باید دقیقاً با فرمت زیر باشد:

    متن: [یک کپشن تلگرامی با استانداردهای بالا. شامل پاراگراف‌های کوتاه (حداکثر ۲ الی ۳ خط) تا چشم مخاطب خسته نشود. از ایموجی‌های مرتبط و به اندازه استفاده کن. 
    نکته بسیار مهم: برای بولد کردن کلمات کلیدی فقط و فقط از تگ <b>کلمه</b> استفاده کن و به هیچ وجه از ستاره (*) استفاده نکن.]
    
    تصویر: [یک پرامپت دقیق، حرفه‌ای و پرجزئیات به زبان انگلیسی برای ساخت عکس با کیفیت بالا و مرتبط با موضوع کپشن. 
    دقت کن: حتماً باید عین متن فارسی تولید شده برای تیتر کپشن را بدون هیچگونه خلاصه‌سازی یا حذف، داخل این پرامپت انگلیسی قرار دهی تا مستقیماً روی عکس رندر شود. به هیچ عنوان از پرچم کشورها (مانند پرچم اسرائیل) یا نمادهای سیاسی نامربوط در پرامپت تصویر استفاده نکن.]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt
        )
        text_output = response.text
        
        parts = text_output.split("تصویر:")
        caption_part = parts[0].replace("متن:", "").strip()
        image_prompt_part = parts[1].strip()
        
        final_caption = f"{caption_part}\n\n🆔 {CHANNEL_ID}"
        return final_caption, image_prompt_part
    except Exception as e:
        print("❌ خطا در تولید متن توسط جمینای:", e)
        return None, None

def generate_image_and_send(caption, image_prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    try:
        print("در حال ساخت تصویر اختصاصی با گوگل Imagen 3...")
        # ساخت تصویر با موتور Imagen 3 گوگل
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=image_prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/jpeg",
            )
        )
        
        # استخراج فایل تصویر تولید شده
        image_bytes = result.generated_images[0].image.image_bytes
        
        print("در حال ارسال پست کامل به تلگرام...")
        telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        # ارسال مستقیم فایل تصویر همراه با کپشن به سرور تلگرام
        files = {'photo': ('shetabafza.jpg', image_bytes, 'image/jpeg')}
        data = {
            "chat_id": CHANNEL_ID,
            "caption": caption,
            "parse_mode": "HTML"
        }
        
        response = requests.post(telegram_api_url, data=data, files=files)
        if response.status_code == 200:
            print("✅ پست با موفقیت و کیفیت بالا در کانال منتشر شد!")
        else:
            print("❌ خطا در ارسال به تلگرام:", response.text)
            
    except Exception as e:
        print("❌ خطا در بخش ساخت تصویر یا ارتباط با تلگرام:", e)

if __name__ == "__main__":
    print("شروع پروسه تولید محتوای شتاب‌افزا...")
    final_caption, img_prompt = generate_content()
    if final_caption and img_prompt:
        generate_image_and_send(final_caption, img_prompt)
    else:
        print("❌ محتوایی برای ارسال آماده نشد.")
