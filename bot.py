import telebot
import requests
from datetime import datetime
from telebot import types
import json

BOT_TOKEN = ""

bot = telebot.TeleBot(BOT_TOKEN)

REGIONS = [
    "Toshkent", "Andijon", "Buxoro", "Farg'ona", "Jizzax", 
    "Namangan", "Navoiy", "Qashqadaryo", "Qoraqalpog'iston", 
    "Samarqand", "Sirdaryo", "Surxondaryo", "Xorazm"
]

# Store user data (in production, use database)
user_data = {}

# Daily Hadith and Islamic content
DAILY_HADITH = [
    {
        "text": "Rasululloh sollallohu alayhi vasallam dedilar: «Kim tongda ikki rakat bomdod namozini o'qisa, u dunyodan va undagi barcha narsalardan afzaldir.»",
        "source": "Muslim rivoyati"
    },
    {
        "text": "«Besh vaqt namozni o'qish - gunohlarni kechiradi.»",
        "source": "Buxoriy va Muslim rivoyati"
    },
    {
        "text": "«Eng yaxshi amal - vaqtida o'qilgan namozdir.»",
        "source": "Buxoriy va Muslim rivoyati"
    }
]

DUAS = {
    "tong": "☀️ *Tong duosi*\n\nاَللّٰهُمَّ بِكَ اَصْبَحْنَا وَبِكَ اَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَاِلَيْكَ النُّشُورُ\n\n_Allohumma bika asbaxnaa va bika amsaynaa va bika naxya va bika namuutu va ilayka n-nushuur._\n\nMa'nosi: Ey Alloh, Sening nomingni tilga olib tonglani va kechani o'tkazdik, Senga yuz tutib hayot kechiramiz va o'lamiz. Va Sengagina qaytamiz.",
    
    "kech": "🌙 *Kech duosi*\n\nاَللّٰهُمَّ بِكَ اَمْسَيْنَا وَبِكَ اَصْبَحْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَاِلَيْكَ الْمَصِيرُ\n\n_Allohumma bika amsaynaa va bika asbaxnaa va bika naxya va bika namuutu va ilayka l-masiir._\n\nMa'nosi: Ey Alloh, Senga yuz tutib kechani va tonglani o'tkazamiz, Sening nomingni tilga olib hayot kechiramiz va o'lamiz. Va Sengagina qaytamiz.",
    
    "ovqat_oldi": "🍽 *Ovqatdan oldin*\n\nبِسْمِ اللهِ وَعَلَى بَرَكَةِ اللهِ\n\n_Bismillahi va 'ala barakatillah._\n\nMa'nosi: Allohning nomi bilan va Allohning barakasi ila boshlayman.",
    
    "ovqat_keyin": "🙏 *Ovqatdan keyin*\n\nاَلْحَمْدُ لِلّٰهِ الَّذِيْ اَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِيْنَ\n\n_Alhamdulillahil-lazii at'amanaa va saqoonaa va ja'alanaa muslimiina._\n\nMa'nosi: Bizni ovqatlantirgan, suv ichirgan va musulmon qilgan Allohga hamd bo'lsin.",
    
    "masjidga": "🕌 *Masjidga kirishda*\n\nاَللّٰهُمَّ افْتَحْ لِيْ اَبْوَابَ رَحْمَتِكَ\n\n_Allohummaftax lii abvaaba rahmatik._\n\nMa'nosi: Ey Alloh, men uchun rahmat eshiklaringni och!"
}

def get_user_data(user_id):
    """Get or create user data"""
    if user_id not in user_data:
        user_data[user_id] = {
            'region': 'Toshkent',
            'notifications': True,
            'language': 'uz'
        }
    return user_data[user_id]

def get_prayer_times(endpoint, region, **params):
    """Fetch prayer times from API"""
    try:
        url = f"https://islomapi.uz/api/{endpoint}"
        params['region'] = region
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API xatolik: {str(e)}"}

def format_daily_times(data):
    """Format daily prayer times"""
    if "error" in data:
        return data["error"]
    
    times = data.get('times', {})
    date = data.get('date', 'N/A')
    region = data.get('region', 'N/A')
    
    message = "┌─────────────────────────┐\n"
    message += f"│   🕌 NAMOZ VAQTLARI   │\n"
    message += "└─────────────────────────┘\n\n"
    message += f"📅 *{date}*\n"
    message += f"📍 *{region}*\n\n"
    message += "─────────────────────────\n"
    message += f"🌅 Bomdod:  `{times.get('tong_saharlik', 'N/A')}`\n"
    message += f"☀️ Quyosh:  `{times.get('quyosh', 'N/A')}`\n"
    message += f"🌞 Peshin:  `{times.get('peshin', 'N/A')}`\n"
    message += f"🌤 Asr:     `{times.get('asr', 'N/A')}`\n"
    message += f"🌆 Shom:    `{times.get('shom_iftor', 'N/A')}`\n"
    message += f"🌙 Xufton:  `{times.get('hufton', 'N/A')}`\n"
    message += "─────────────────────────\n"
    
    return message

def format_weekly_times(data):
    """Format weekly prayer times"""
    if "error" in data:
        return data["error"]
    
    region = data[0].get('region', 'N/A') if data else 'N/A'
    message = "┌─────────────────────────┐\n"
    message += "│  📆 HAFTALIK TAQVIM   │\n"
    message += "└─────────────────────────┘\n\n"
    message += f"📍 *{region}*\n\n"
    
    for day_data in data:
        date = day_data.get('date', 'N/A')
        weekday = day_data.get('weekday', '')
        times = day_data.get('times', {})
        message += f"*{weekday}, {date}*\n"
        message += f"🌅 `{times.get('tong_saharlik', 'N/A')}` "
        message += f"🌞 `{times.get('peshin', 'N/A')}` "
        message += f"🌤 `{times.get('asr', 'N/A')}` "
        message += f"🌆 `{times.get('shom_iftor', 'N/A')}` "
        message += f"🌙 `{times.get('hufton', 'N/A')}`\n\n"
    
    return message

def format_monthly_times(data):
    """Format monthly prayer times (condensed)"""
    if "error" in data:
        return data["error"]
    
    region = data[0].get('region', 'N/A') if data else 'N/A'
    month = datetime.now().strftime('%B')
    
    message = f"📆 *{month} oyi - {region}*\n\n"
    message += "```\n"
    message += "Kun | Bomdod | Peshin | Asr   | Shom  | Xufton\n"
    message += "----|--------|--------|-------|-------|-------\n"
    
    for day_data in data:
        day = day_data.get('day', 'N/A')
        times = day_data.get('times', {})
        message += f"{day:>2}  | {times.get('tong_saharlik', 'N/A')} | "
        message += f"{times.get('peshin', 'N/A')} | {times.get('asr', 'N/A')} | "
        message += f"{times.get('shom_iftor', 'N/A')} | {times.get('hufton', 'N/A')}\n"
    
    message += "```"
    return message

def get_main_keyboard():
    """Main menu keyboard"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📅 Bugungi kun"),
        types.KeyboardButton("📆 Haftalik"),
        types.KeyboardButton("📊 Oylik"),
        types.KeyboardButton("🤲 Duolar"),
        types.KeyboardButton("📿 Kunlik hadis"),
        types.KeyboardButton("⚙️ Sozlamalar")
    )
    return markup

def get_duas_keyboard():
    """Duas menu keyboard"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("☀️ Tong duosi"),
        types.KeyboardButton("🌙 Kech duosi"),
        types.KeyboardButton("🍽 Ovqat duolari"),
        types.KeyboardButton("🕌 Masjid duosi"),
        types.KeyboardButton("« Orqaga")
    )
    return markup

def get_settings_keyboard():
    """Settings menu keyboard"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📍 Hududni o'zgartirish"),
        types.KeyboardButton("🔔 Bildirishnomalar"),
        types.KeyboardButton("ℹ️ Bot haqida"),
        types.KeyboardButton("« Orqaga")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message with region selection"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    
    welcome_text = (
        "🕌 *Assalomu alaykum va rahmatullohi va barokatuh!*\n\n"
        "Namoz vaqtlari botiga xush kelibsiz!\n\n"
        "Bu bot orqali siz:\n"
        "✅ Kunlik namoz vaqtlarini ko'rishingiz\n"
        "✅ Haftalik va oylik taqvimni olishingiz\n"
        "✅ Kunlik hadis va duolarni o'qishingiz\n"
        "✅ Bildirishnoma olishingiz mumkin\n\n"
        "Davom etish uchun hududingizni tanlang:"
    )
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for region in REGIONS:
        markup.add(types.KeyboardButton(region))
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text in REGIONS)
def set_region(message):
    """Save user's region and show menu"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    user_info['region'] = message.text
    
    bot.send_message(
        message.chat.id,
        f"✅ Hudud tanlandi: *{message.text}*\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == "📅 Bugungi kun")
def show_daily(message):
    """Show daily prayer times"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    region = user_info['region']
    
    loading_msg = bot.send_message(message.chat.id, "⏳ Ma'lumotlar yuklanmoqda...")
    
    data = get_prayer_times("present/day", region)
    formatted = format_daily_times(data)
    
    # Get random daily hadith
    import random
    hadith = random.choice(DAILY_HADITH)
    formatted += f"\n\n📿 *Kunlik hadis:*\n_{hadith['text']}_\n\n— {hadith['source']}"
    
    bot.delete_message(message.chat.id, loading_msg.message_id)
    bot.send_message(message.chat.id, formatted, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📆 Haftalik")
def show_weekly(message):
    """Show weekly prayer times"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    region = user_info['region']
    
    loading_msg = bot.send_message(message.chat.id, "⏳ Ma'lumotlar yuklanmoqda...")
    
    data = get_prayer_times("present/week", region)
    formatted = format_weekly_times(data)
    
    bot.delete_message(message.chat.id, loading_msg.message_id)
    bot.send_message(message.chat.id, formatted, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📊 Oylik")
def show_monthly(message):
    """Show monthly prayer times"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    region = user_info['region']
    
    loading_msg = bot.send_message(message.chat.id, "⏳ Ma'lumotlar yuklanmoqda...")
    
    current_month = datetime.now().month
    data = get_prayer_times("monthly", region, month=current_month)
    formatted = format_monthly_times(data)
    
    bot.delete_message(message.chat.id, loading_msg.message_id)
    bot.send_message(message.chat.id, formatted, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🤲 Duolar")
def show_duas_menu(message):
    """Show duas menu"""
    bot.send_message(
        message.chat.id,
        "🤲 *Kundalik Duolar*\n\nQuyidagilardan birini tanlang:",
        reply_markup=get_duas_keyboard(),
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == "☀️ Tong duosi")
def show_morning_dua(message):
    bot.send_message(message.chat.id, DUAS['tong'], parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🌙 Kech duosi")
def show_evening_dua(message):
    bot.send_message(message.chat.id, DUAS['kech'], parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🍽 Ovqat duolari")
def show_food_duas(message):
    text = DUAS['ovqat_oldi'] + "\n\n" + DUAS['ovqat_keyin']
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🕌 Masjid duosi")
def show_mosque_dua(message):
    bot.send_message(message.chat.id, DUAS['masjidga'], parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📿 Kunlik hadis")
def show_daily_hadith(message):
    """Show daily hadith"""
    import random
    hadith = random.choice(DAILY_HADITH)
    
    text = f"📿 *Kunlik Hadis*\n\n_{hadith['text']}_\n\n— {hadith['source']}"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar")
def show_settings(message):
    """Show settings menu"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    
    text = (
        "⚙️ *Sozlamalar*\n\n"
        f"📍 Joriy hudud: *{user_info['region']}*\n"
        f"🔔 Bildirishnomalar: *{'Yoqilgan' if user_info['notifications'] else "O\\'chirilgan"}*\n"
    )
    
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=get_settings_keyboard(),
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == "📍 Hududni o'zgartirish")
def change_region(message):
    """Change region"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for region in REGIONS:
        markup.add(types.KeyboardButton(region))
    
    bot.send_message(
        message.chat.id,
        "📍 Yangi hududni tanlang:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🔔 Bildirishnomalar")
def toggle_notifications(message):
    """Toggle notifications"""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    user_info['notifications'] = not user_info['notifications']
    
    status = "yoqildi" if user_info['notifications'] else "o'chirildi"
    bot.send_message(
        message.chat.id,
        f"🔔 Bildirishnomalar {status}!"
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ Bot haqida")
def show_about(message):
    """Show about information"""
    about_text = (
        "ℹ️ *Namoz Vaqtlari Bot*\n\n"
        "Versiya: 2.0\n"
        "API: islomapi.uz\n\n"
        "Bu bot islom.uz sayti asosida yaratilgan va musulmonlarga "
        "namoz vaqtlarini, duolarni va islomiy bilimlarni "
        "qulay tarzda yetkazish maqsadida ishlab chiqilgan.\n\n"
        "© 2025 Namoz Vaqtlari Bot\n"
        "Barcha huquqlar himoyalangan.\n"
        "owner: @isroiloff112"
    )
    bot.send_message(message.chat.id, about_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "« Orqaga")
def go_back(message):
    """Go back to main menu"""
    bot.send_message(
        message.chat.id,
        "🏠 Asosiy menyu",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    """Help message"""
    help_text = (
        "📖 *Yordam*\n\n"
        "*Asosiy buyruqlar:*\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam\n\n"
        "*Bo'limlar:*\n"
        "📅 Bugungi kun - Bugungi namoz vaqtlari\n"
        "📆 Haftalik - Haftalik taqvim\n"
        "📊 Oylik - Oylik taqvim\n"
        "🤲 Duolar - Kundalik duolar\n"
        "📿 Kunlik hadis - Har kungi hadis\n"
        "⚙️ Sozlamalar - Bot sozlamalari\n\n"
        "Savol va takliflar uchun: @support"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Handle unknown messages"""
    bot.send_message(
        message.chat.id,
        "❌ Noto'g'ri buyruq.\n\n"
        "Iltimos, tugmalardan foydalaning yoki /help buyrug'ini yuboring."
    )

if __name__ == '__main__':
    print("🤖 Bot ishga tushdi...")
    print("📡 API: islomapi.uz")
    print("✅ Tayyor!")
    bot.infinity_polling()