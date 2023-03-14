from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.all import crop
from tiktok_module import downloader
from dotenv import load_dotenv
from telebot import types
from colorama import Fore
from io import BytesIO
from PIL import Image
import audioread
import datetime
import requests
import logging
import telebot
import pytube
import os

users = []

load_dotenv()

logging.basicConfig(level=logging.DEBUG, filename="logs.log", filemode="w",
                    format='[%(asctime)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

bot = telebot.TeleBot(os.getenv("TOKEN"))


def logs(message: telebot.types.Message, level: int, log_mes: str, error: Exception = None):
    """
    This function sends to the console and saves to a log file.

    :param message: telebot.types.Message
    :param level: Logging levels
            0 - DEBUG
            1 - INFO
            2 - WARNING
            3 - ERROR
            4 - CRITICAL
    :param log_mes: message log
    :param error: error message

    :return: None
    """
    global users
    if not message.chat.id in users:
        users.append(message.chat.id)
        logging.info(f"New user {message.chat.id}")
        print(Fore.GREEN + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO New user {message.chat.id}")

    if level == 0:
        logging.debug(log_mes)
        print(Fore.BLUE + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DEBUG {log_mes}",error)
    elif level == 1:
        logging.info(log_mes)
        print(Fore.GREEN + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO {log_mes}",error)
    elif level == 2:
        logging.debug(log_mes)
        print(Fore.YELLOW + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WARNING {log_mes}",error)
    elif level == 3:
        logging.error(log_mes, exc_info=error)
        print(Fore.RED + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR {log_mes}",error)
    elif level == 4:
        logging.critical(log_mes)
        print(Fore.RED + f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CRITICAL {log_mes}",error)


def get(videoid: str):
    """
    This function returns information about the song, namely: title, id, link, cover link, author name, author url.

    :param videoid: id song in YouTube music

    :return: Information about the song in YouTube music
    """
    headers = dict({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/103.0.5060.134 Safari/537.36"})

    data = dict(requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={videoid}",
                             headers=headers).json())

    return dict(
        trackName=data["title"],
        trackId=videoid,
        trackUrl=f"https://music.youtube.com/watch?v={videoid}",
        artworkUrl=f"https://img.youtube.com/vi/{videoid}/0.jpg",
        artistName=data["author_name"][:-8],
        artistUrl=data["author_url"]
    )


def download_and_send(url: str, message: telebot.types.Message):
    """
    This function sends music from YouTube music with metadata

    :param url: link to song in YouTube music
    :param message: telebot.types.Message

    :return:Sending status True/False
    """
    song = get(pytube.extract.video_id(url))
    logs(message, 1, f"User {message.chat.id} start download song Youtube music {song['trackUrl']}")
    chat_id = message.chat.id
    try:
        destination = "tmp"

        yt = pytube.YouTube(song['trackUrl'])
        filename = "_".join((song["trackName"]).split(" "))
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=destination, filename=filename)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        response = requests.get(song["artworkUrl"])
        img = Image.open(BytesIO(response.content))
        area = (110, 50, 370, 310)
        cropped_img = img.crop(area)
        cropped_img.save(f"{base}.png")

        with audioread.audio_open(new_file) as f:
            totalsec = f.duration
            bot.send_audio(chat_id, audio=open(f"{new_file}", "rb"), thumb=open(f"{base}.png", "rb"),
                           title=song["trackName"], performer=song["artistName"], duration=totalsec)
        os.remove(new_file)
        os.remove(f"{base}.png")
        return True
    except Exception as e:
        bot.send_message(chat_id, (song['trackName'] + " has not been successfully downloaded."))
        logs(message, 3, f"User {message.chat.id} error download song Youtube music url:{song['trackUrl']}", e)
        return False
@bot.message_handler(content_types=["video"])
def video_message(message):
    logs(message, 1, f"User {message.chat.id} start function selection video message id {message.message_id}")
    try:
        input_path = f"tmp/{message.chat.id}_{message.message_id}.mp4"
        output_path = f"tmp/output_{message.chat.id}_{message.message_id}.mp4"
        raw = message.video.file_id
        file_info = bot.get_file(raw)
        video = bot.download_file(file_info.file_path)
        with open(input_path, 'wb') as fd:
            fd.write(video)

        video = VideoFileClip(input_path, verbose=False)
        width, height = video.size
        new_size = min(width, height)
        cropped_video = crop(video, width=new_size, height=new_size, x_center=width / 2, y_center=height / 2)
        cropped_video.write_videofile(output_path, logger=None)
        bot.send_video_note(message.chat.id, open(output_path,"rb"))
        os.remove(output_path)
        os.remove(input_path)
    except Exception as e:
        logs(message, 3, f"User {message.chat.id} error function selection video  message id {message.message_id}", e)

@bot.message_handler(content_types=["audio"])
def audio_message(message):
    logs(message, 1, f"User {message.chat.id} start convert audio to voice message id {message.message_id}")
    try:
        raw = message.audio.file_id
        file_info = bot.get_file(raw)
        audio = bot.download_file(file_info.file_path)
        bot.send_voice(message.chat.id, audio)
    except Exception as e:
        logs(message, 3, f"User {message.chat.id} error convert audio to voice message id {message.message_id}", e)


@bot.message_handler(content_types=["voice"])
def voice_message(message):
    logs(message, 1, f"User {message.chat.id} start convert voice to audio message id {message.message_id}")
    try:
        raw = message.voice.file_id
        file_info = bot.get_file(raw)
        audio = bot.download_file(file_info.file_path)
        bot.send_audio(message.chat.id, audio)
    except Exception as e:
        logs(message, 3, f"User {message.chat.id} error convert voice to audio message id {message.message_id}", e)


@bot.message_handler(content_types=["text"])
def text(message):
    mess = message.text
    if mess.startswith("https://vm.tiktok.com/"):
        logs(message, 1, f"User {message.chat.id} start download tiktok {mess}")
        try:
            dl = downloader.tiktok_downloader()
            content = dl.content(url=mess)
            if content == "private/remove":
                logs(message, 2, f"User {message.chat.id} tried to download a private or deleted video url: {mess}")
                bot.send_message(message.chat.id, "This video is private or remove")
            elif content == "url-invalid":
                logs(message, 2, f"User {message.chat.id}  entered an invalid url: {mess}")
                bot.send_message(message.chat.id, "This video is private or remove")
            else:
                logs(message, 1, f"User {message.chat.id}  finished uploading the video url: {mess}")
                bot.send_video(message.chat.id, content)
        except Exception as e:
            logs(message, 3, f"User {message.chat.id} error download tiktok", e)
    elif mess.startswith("https://music.youtube.com/watch?v="):
        bot.send_message(message.chat.id, "Start download")
        download_and_send(mess, message)
    elif mess.startswith("https://music.youtube.com/playlist?list="):

        logs(message, 1, f"User {message.chat.id} start download playlist Youtube music {mess}")
        try:
            bot.send_message(message.chat.id, f"Start download playlist {mess}")
            Error_msg = ""
            Error = 0
            for url in pytube.Playlist(mess):
                song = get(pytube.extract.video_id(url))
                if not download_and_send(url, message):
                    Error_msg += f"Name:{song['trackName']}\nurl:{song['trackUrl']}\n\n"
                    Error += 1
            if Error > 0:
                bot.send_message(message.chat.id, (Error_msg + f"A total of {Error} have not been downloaded"))
            bot.send_message(message.chat.id, f"End download playlist {mess}")
        except Exception as e:

            logs(message, 3, f"User {message.chat.id} error download playlist Youtube music url:{mess}", e)
    else:

        logs(message, 1, f"User {message.chat.id} send message {mess}")


if __name__ == '__main__':
    bot.infinity_polling()
