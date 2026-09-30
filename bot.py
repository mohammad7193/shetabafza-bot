from google import genai
import requests
import random
import os
import time
import xml.etree.ElementTree as ET
import re

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
    تو یک متخصص دیجیتال مارکتینگ در کانال 'شتاب‌افزا' هستی.
    مخاطب تو: ادمین‌ها، صاحبان پیج‌های اینستاگرامی، کانال‌های فروشگاهی و کسب‌وکارهای آنلاین هستند که نیاز به راهنمایی دارند اما دانش فنی سنگینی ندارند.
    
    ⚠️ موضوعات تکراری که نباید استفاده شوند: {past_topics}
    
    یک پست آموزشی درباره دیجیتال مارکتینگ یا فروش آنلاین بنویس. 
    قوانین: 
    ۱. فضا کاملاً دیجیتال و آنلاین باشد (درباره پیج، کانال، محتوا، مشتری آنلاین و...) اما با زبانی بسیار ساده، روان و قابل فهم.
    ۲. از اصطلاحات سنگین و قلمبه‌سلمبه (مثل سئو تکنیکال، هاست، سرور، کراولر) استفاده نکن.
    ۳. یک تکنیک خرد، عملی و راحت برای افزایش فروش یا جذب مخاطب در فضای مجازی یاد بده.
    ۴. هیچ داستان خیالی، اغراق یا روایت ساختگی نباید نوشته شود. کلمات عاشقانه (مثل عشق و عاشقی) مطلقاً ممنوع است.
    
    خروجی دقیقاً با این فرمت سه بخشی باشد:
    متن: [یک کپشن جذاب و روان، با پاراگراف‌های کوتاه، همراه با ایموجی. بدون تگ HTML. بین ۷۰ تا ۱۰۰ کلمه]
    موضوع_تصویر: [دقیقاً ۱ تا ۳ کلمه انگلیسی که «ملموس‌ترین شیء فیزیکی» مرتبط با متن را توصیف کند. توجه: هیچ المانی از شخص، آدم یا چهره نباید باشد! فقط اشیاء. مثلاً: smartphone keyboard]
    موضوع_تاریخچه: [یک عبارت فارسی ۳ تا ۴ کلمه‌ای که مشخص کند امروز درباره چه تکنیک آنلاینی حرف زدی]
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
            print(f"⚠ تلاش {attempt + 1} برای مارکتینگ ناموفق بود. در حال تلاش مجدد... خطا: {e}")
            time.sleep(15)
            
    print("❌ خطای قطعی در تولید پست مارکتینگ.")
    return None, None, None

def fetch_relevant_tech_news():
    print("در حال دریافت اخبار و استخراج تصاویر اورجینال سایت‌ها...")
    feeds = [
        "https://www.zoomit.ir/feed/",
        "https://digiato.com/topic/tech/feed/"
    ]
    all_news = []
    
    for feed in feeds:
        try:
            response = requests.get(feed, timeout=15)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text
                link = item.find('link').text
                
                # استخراج عکس اصلی خبر از RSS
                image_url = None
                
                # بررسی تگ enclosure
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    image_url = enclosure.get('url')
                
                # بررسی تگ description برای پیدا کردن عکس
                if not image_url:
                    desc = item.find('description')
                    if desc is not None and desc.text:
                        img_match = re.search(r'src="([^"]+(?:jpg|jpeg|png|webp))"', desc.text)
                        if img_match:
                            image_url = img_match.group(1)
                
                if image_url:
                    all_news.append({"title": title, "link": link, "image": image_url})
                    
        except Exception as e:
            print("⚠️ خطا در خواندن RSS:", e)
            
    if not all_news:
        return None, None, None

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        titles_text = "\n".join([f"{i}. {news['title']}" for i, news in enumerate(all_news)])
        
        prompt = f"""
        من لیستی از اخبار امروز را دارم. کانال من درباره "کسب‌وکار اینترنتی، دیجیتال مارکتینگ و فناوری" است. 
        اخبار بی‌ربط (مثل خودرو، سیاست، حوادث) را نادیده بگیر.
        از بین تیترهای زیر، مرتبط‌ترین خبر به کانال من را پیدا کن و فقط شماره آن خبر را بنویس (بدون هیچ توضیح اضافه‌ای).
        
        تیترها:
        {titles_text}
        """
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        
        numbers = re.findall(r'\d+', response.text)
        selected_index = int(numbers[0]) if numbers else 0
        
        if 0 <= selected_index < len(all_news):
            selected = all_news[selected_index]
            print(f"✅ خبر هوشمند انتخاب شد: {selected['title']}")
            return selected['title'], selected['link'], selected['image']
        else:
            return all_news[0]['title'], all_news[0]['link'], all_news[0]['image']
    except Exception as e:
        print("⚠️ خطا در انتخاب خبر:", e)
        return all_news[0]['title'], all_news[0]['link'], all_news[0]['image']

def generate_news_caption_with_retry(title, link, max_retries=3):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    یک خبر با این تیتر منتشر شده است: "{title}"
    لطفاً یک معرفی کوتاه و جذاب (۲ تا ۳ خط) برای کانال دیجیتال مارکتینگ بنویس.
    قوانین: کاملاً خبری و واقعی باشد. اغراق نشود. کلمات عاشقانه استفاده نشود.
    در انتها بنویس: برای خواندن کامل خبر روی لینک زیر کلیک کنید.
    (فقط متن نهایی را به من بده)
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            return response.text.strip() + f"\n\n🔗 لینک خبر:\n{link}"
        except Exception:
            time.sleep(10)
            
    return f"📰 {title}\n\n🔗 برای خواندن خبر روی لینک زیر کلیک کنید:\n{link}"

def get_pexels_image(image_topic):
    headers = {"Authorization": PEXELS_API_KEY}
    search_url = f"https://api.pexels.com/v1/search?query={image_topic}&per_page=15"
    try:
        response = requests.get(search_url, headers=headers).json()
        if "photos" in response and len(response["photos"]) > 0:
            return random.choice(response["photos"])["src"]["large"]
    except Exception as e:
        pass
    return "https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg"

def send_photo_to_channels(caption, image_url):
    payload_tg = {"chat_id": TELEGRAM_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {TELEGRAM_CHANNEL_ID}"}
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto", data=payload_tg)
    
    payload_bale = {"chat_id": BALE_CHANNEL_ID, "photo": image_url, "caption": caption + f"\n\n🆔 {BALE_CHANNEL_ID}"}
    requests.post(f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendPhoto", data=payload_bale)

if __name__ == "__main__":
    print("=== شروع پروسه ربات هوشمند شتاب‌‌افزا ===")
    
    # ------------------ بخش اول: پست دیجیتال مارکتینگ ------------------
    base_caption, topic, history_topic = generate_post_content_with_retry()
    if base_caption and topic and history_topic:
        save_to_history(history_topic)
        print(f"✅ موضوع '{history_topic}' در تاریخچه ذخیره شد.")
        edu_image_url = get_pexels_image(topic)
        print("در حال ارسال پست آموزشی به تلگرام و بله...")
        send_photo_to_channels(base_caption, edu_image_url)
    
    # ------------------ بخش دوم: اخبار تکنولوژی (با عکس اورجینال سایت) ------------------
    news_title, news_link, news_image_url = fetch_relevant_tech_news()
    if news_title and news_link and news_image_url:
        news_caption = generate_news_caption_with_retry(news_title, news_link)
        print("در حال ارسال خبر همراه با عکس اورجینال سایت به تلگرام و بله...")
        send_photo_to_channels(news_caption, news_image_url)
        print("✅ خبر تکنولوژی با موفقیت ارسال شد.")
        
    print("🎉 پروسه امروز به پایان رسید.")
