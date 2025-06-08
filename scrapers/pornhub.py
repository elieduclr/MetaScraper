import requests
from lxml import html
import re
from scrapers.base import BaseScraper

class PornhubScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "pornhub.com/view_video.php" in url or "pornhub.com" in url

    def scrape(self, url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Erreur HTTP {response.status_code}"}

        tree = html.fromstring(response.content)

        data = {}

        # Titre (xpath simplifié)
        title = tree.xpath('//h1//span/text()')
        data['title'] = title[0].strip() if title else None

        # URL canonique
        canonical = tree.xpath('//link[@rel="canonical"]/@href')
        data['url'] = canonical[0] if canonical else url

        # Date d'upload
        upload_date = tree.xpath('//script[contains(text(), "uploadDate")]/text()')
        if upload_date:
            match = re.search(r'"uploadDate"\s*:\s*"([^"]+)"', upload_date[0])
            data['date'] = match.group(1) if match else None
        else:
            data['date'] = None

        # Tags et catégories
        tags = tree.xpath('//div[contains(@class,"video-detailed-info")]//a[@data-label="category" or @data-label="tag"]/text()')
        data['tags'] = [t.strip() for t in tags]

        # Uploader
        uploader = tree.xpath('//span[contains(@class,"usernameBadgesWrapper")]//a[contains(@class,"bolded")]/text()')
        data['uploader'] = uploader[0] if uploader else None

        # Performers
        performers = tree.xpath('//div[contains(@class,"video-detailed-info")]//a[@data-label="pornstar"]/text()')
        data['performers'] = [p.strip() for p in performers if p.strip()]

        # Image principale
        image = tree.xpath('//meta[@property="og:image"]/@content')
        data['image'] = image[0] if image else None

        # Studio
        studio = tree.xpath('//div[contains(@class,"video-detailed-info")]//a[@data-label="channel"]/text()')
        data['studio'] = studio[0].strip() if studio else None

        # Note
        rating = tree.xpath('//span[contains(@class,"votesUp")]/@data-rating')
        data['rating'] = rating[0].strip() if rating else None

        # Vues
        views = tree.xpath('//span[contains(@class,"count")]/text()')
        data['views'] = views[0].strip() if views else None

        return data
