import os
import logging
import telebot
import youtube_dl
from pytube import YouTube
from moviepy.audio.io.AudioFileClip import AudioFileClip

TELEGRAM_BOT_TOKEN = 'YourToken'

# Створення об'єкту телеграм-бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Каталог для збереження завантажених аудіофайлів
DOWNLOADS_DIR = 'downloads'
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Включення логування для налагодження
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
def download_audio(url):
    try:
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True).first()
        audio_stream.download(DOWNLOADS_DIR)
        return audio_stream.default_filename
    except Exception as e:
        logging.error(f"Error while downloading audio: {e}")
        return None

# Функція для конвертації аудіо в mp3
def convert_to_mp3(audio_file):
    try:
        mp3_file = os.path.splitext(audio_file)[0] + '.mp3'
        audio_clip = AudioFileClip(os.path.join(DOWNLOADS_DIR, audio_file))
        audio_clip.write_audiofile(os.path.join(DOWNLOADS_DIR, mp3_file))
        audio_clip.close()
        os.remove(os.path.join(DOWNLOADS_DIR, audio_file))
        return mp3_file
    except Exception as e:
        logging.error(f"Error while converting audio to mp3: {e}")
        return None

# Обробка команди /start
@bot.message_handler(commands=['start'])
def start(message):
    url = bot.reply_to(message, "Вітаю! Це бот для завантаження аудіо з ютуб. Щоб розпочати завантаження пропишіть /youtube та вставте посилання на відео з якого хочете завантажити.")

# Обробка команди /youtube та посилання на YouTube відео
@bot.message_handler(commands=['youtube'])
def youtube(message):
    url = bot.reply_to(message, "Вітаю! Введіть посилання на відео з YouTube, щоб завантажити аудіо.")
    bot.register_next_step_handler(url, download_from_youtube)

# Обробка команди /youtube та посилання на YouTube відео
def download_from_youtube(message):
    try:
        url = message.text
        audio_file = download_audio(url)
        if audio_file:
            mp3_file = convert_to_mp3(audio_file)
            if mp3_file:
                with open(os.path.join(DOWNLOADS_DIR, mp3_file), 'rb') as audio:
                    bot.send_audio(message.chat.id, audio)
                os.remove(os.path.join(DOWNLOADS_DIR, mp3_file))
            else:
                bot.reply_to(message, "Помилка при конвертації аудіо в mp3.")
        else:
            bot.reply_to(message, "Помилка при завантаженні аудіо. Переконайтеся, що посилання є правильним.")
    except IndexError:
        bot.reply_to(message, "Будь ласка, введіть посилання на YouTube відео після команди /youtube.")

# Головна функція
def main():
    bot.polling()

if __name__ == '__main__':
    main()