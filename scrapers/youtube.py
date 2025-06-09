import requests
from lxml import html
import re
from scrapers.base import BaseScraper

class YouTubeScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "youtube.com/watch" in url or "youtu.be/" in url

    def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Erreur HTTP {response.status_code}"}

        tree = html.fromstring(response.text)

        data = {}

        # Titre
        title = tree.xpath('//meta[@name="title"]/@content')
        data['title'] = title[0] if title else None

        # URL canonique
        canonical = tree.xpath('//link[@rel="canonical"]/@href')
        data['url'] = canonical[0] if canonical else url

        # Uploader
        uploader = tree.xpath('//link[@itemprop="name"]/@content')
        data['uploader'] = uploader[0] if uploader else None

        # Date de publication
        upload_date = tree.xpath('//meta[@itemprop="datePublished"]/@content')
        data['date'] = upload_date[0] if upload_date else None

        # Miniature (meta)
        thumbnail = tree.xpath('//meta[@property="og:image"]/@content')
        data['image'] = thumbnail[0] if thumbnail else None

        # Vues (par parsing JSON dans le HTML)
        views_match = re.search(r'"viewCount":"(\d+)"', response.text)
        if views_match:
            count = int(views_match.group(1))
            if count >= 1_000_000:
                data['views'] = f"{count / 1_000_000:.1f}M"
            elif count >= 1_000:
                data['views'] = f"{count / 1_000:.1f}K"
            else:
                data['views'] = str(count)
        else:
            data['views'] = None

        # Tags (depuis les mots-clés si dispo)
        keywords = tree.xpath('//meta[@name="keywords"]/@content')
        data['tags'] = [tag.strip() for tag in keywords[0].split(',')] if keywords else []

        return data
