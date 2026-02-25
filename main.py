import telebot
from gtts import gTTS
import requests
import os
from flask import Flask
from threading import Thread

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8386106210:AAGmidWuDlq3vk_ziH4yTAScMzNGDN003vs"
GEMINI_API_KEY = "AIzaSyAOvzU4yI6PFDZd2q7QXtLgN3acUv7Jud0"

bot = telebot.TeleBot(BOT_TOKEN)

# ====== KEEP ALIVE (24/7) ======
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ====== КОМАНДЫ ======
@bot.message_handler(commands=['fire'])
def fire_cmd(message):
    bot.send_message(message.chat.id, "🔥")

@bot.message_handler(commands=['water'])
def water_cmd(message):
    bot.send_message(message.chat.id, "💧")

@bot.message_handler(commands=['diamond'])
def diamond_cmd(message):
    bot.send_message(message.chat.id, "💎")

# ====== БАТАРЕЙКА СКАЖИ (ГОЛОС) ======
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("батарейка скажи"))
def battery_voice(message):
    text = message.text[len("батарейка скажи"):].strip()
    if not text:
        return

    try:
        tts = gTTS(text=text, lang="ru")
        filename = "voice.mp3"
        tts.save(filename)

        with open(filename, "rb") as audio:
            bot.send_voice(message.chat.id, audio)

        os.remove(filename)
    except:
        pass

# ====== БАТАРЕЙКА ИИ ======
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("батарейка"))
def battery_ai(message):
    question = message.text[len("батарейка"):].strip()
    if not question:
        return

    try:
        url = (
            "https://generativelanguage.googleapis.com/v1/models/"
            "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
        )

        data = {
            "contents": [{
                "parts": [{"text": question}]
            }]
        }

        r = requests.post(url, json=data, timeout=20)
        result = r.json()

        if "candidates" not in result:
            return

        parts = result["candidates"][0]["content"].get("parts", [])
        if not parts:
            return

        answer = parts[0].get("text")
        if not answer:
            return

        bot.send_message(message.chat.id, answer)

    except:
        pass

# ====== ЗАПУСК ======
keep_alive()
print("🤖 Бот работает 24/7")
bot.infinity_polling()
