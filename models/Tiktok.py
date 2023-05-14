from models import Log
import requests
import telebot
import bs4


def send_photos_or_video(url: str, message: telebot.types.Message, bot: telebot.TeleBot):
    """
    MIT License

    Copyright (c) 2021 AkasakaID

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.


    This feature sends photos or videos from a tiktok link

    :param url: (str) Link to video or photo in tiktok
    :param message: (telebot.types.Message)
    :param bot: (telebot.TeleBot)
    :return: None
    """
    ses = requests.Session()
    server_url = 'https://musicaldown.com/'
    headers = {
        "Host": "musicaldown.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers"
    }
    ses.headers.update(headers)
    req = ses.get(server_url)
    data = {}
    parse = bs4.BeautifulSoup(req.text, 'html.parser')
    get_all_input = parse.findAll('input')
    for i in get_all_input:
        if i.get("id") == "link_url":
            data[i.get("name")] = url
        else:
            data[i.get("name")] = i.get("value")
    post_url = server_url + "id/download"
    req_post = ses.post(post_url, data=data, allow_redirects=True)
    if req_post.status_code == 302 or 'This video is currently not available' in req_post.text or 'Video is private or removed!' in req_post.text or 'Video bersifat pribadi atau dihapus!' in req_post.text:
        Log.log.send(message, Log.Loglevel.WARNING,
                     f"User {message.chat.id} tried to download a private or deleted video url: {url}")
        bot.send_message(message.chat.id, "This video is private or remove")
    elif 'Submitted Url is Invalid, Try Again' in req_post.text or 'TikTok mengembalikan halaman utama!' in req_post.text:
        Log.log.send(message, Log.Loglevel.WARNING,
                     f"User {message.chat.id} tried to download a invalid link video url: {url}")
        bot.send_message(message.chat.id, "invalid link")
    html = bs4.BeautifulSoup(req_post.text, 'html.parser')
    if len(html.findAll('div', attrs={'class': 'col s12 m3'})) == 0:
        download_link = html.findAll(
            'a', attrs={'target': '_blank'})[0].get('href')
        get_content = requests.get(download_link).content
        bot.send_video(message.chat.id, get_content)
        Log.log.send(message, Log.Loglevel.INFO, f"User {message.chat.id}  finished uploading the video url: {url}")
        return
    for i in html.findAll('div', attrs={'class': 'col s12 m3'}):
        download_link = i.find(
            'a', attrs={'class': 'btn waves-effect waves-light orange'}).get('href')
        bot.send_photo(message.chat.id, requests.get(download_link).content)
    bot.send_message(message.chat.id, "End")
    Log.log.send(message, Log.Loglevel.INFO, f"User {message.chat.id}  finished uploading the photos url: {url}")
