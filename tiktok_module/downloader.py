import requests
import bs4


class tiktok_downloader:
    def __init__(self):
        pass
    def content(self, url):
        """
        This function returns the content of a TikTok video link

        :param url: TikTok video url

        :return video content or error
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
            return 'private/remove'
        elif 'Submitted Url is Invalid, Try Again' in req_post.text or 'TikTok mengembalikan halaman utama!' in req_post.text:
            return 'url-invalid'
        get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
            'a', attrs={'target': '_blank'})

        download_link = get_all_blank[0].get('href')
        get_content = requests.get(download_link)
        return get_content.content
