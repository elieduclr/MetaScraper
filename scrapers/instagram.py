import requests
from lxml import html
import re
import json
import time
from scrapers.base import BaseScraper

class InstagramScraper(BaseScraper):
    def can_handle(self, url: str) -> bool:
        return "instagram.com/p/" in url or "instagram.com/reel/" in url

    def scrape(self, url: str) -> dict:
        # Headers plus complets pour imiter un vrai navigateur
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }

        # Tentative 1: Requête normale
        data = self._try_standard_request(url, headers)
        if self._has_valid_data(data):
            return data

        # Tentative 2: Ajouter un délai et refaire la requête
        time.sleep(2)
        data = self._try_standard_request(url, headers)
        if self._has_valid_data(data):
            return data

        # Tentative 3: Essayer avec l'URL embed d'Instagram
        embed_url = url.replace('/p/', '/p/').rstrip('/') + '/embed/'
        data = self._try_embed_request(embed_url, headers)
        if self._has_valid_data(data):
            return data

        # Tentative 4: Parsing JSON depuis les scripts
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = self._extract_json_from_scripts(response.text)
            if json_data:
                return self._format_json_data(json_data, url)

        # Fallback: données minimales
        return {
            "caption": None,
            "username": self._extract_username_from_url(url),
            "date": None,
            "likes": None,
            "comments": None,
            "hashtags": [],
            "url": url,
            "image": None,
            "type": "reel" if "/reel/" in url else "post"
        }

    def _try_standard_request(self, url: str, headers: dict) -> dict:
        """Tentative de scraping standard"""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Erreur HTTP {response.status_code}"}

            tree = html.fromstring(response.text)
            return self._extract_meta_data(tree, url, response.text)
        except Exception as e:
            return {"error": str(e)}

    def _try_embed_request(self, embed_url: str, headers: dict) -> dict:
        """Tentative avec l'URL embed d'Instagram"""
        try:
            response = requests.get(embed_url, headers=headers, timeout=10)
            if response.status_code == 200:
                tree = html.fromstring(response.text)
                return self._extract_meta_data(tree, embed_url, response.text)
        except:
            pass
        return {}

    def _extract_meta_data(self, tree, url: str, html_content: str) -> dict:
        """Extraction des métadonnées depuis le HTML"""
        data = {}

        # Caption et métadonnées depuis og:description
        og_description = tree.xpath('//meta[@property="og:description"]/@content')
        if og_description:
            desc_text = og_description[0]
            
            # Extraction des likes et commentaires
            stats_match = re.search(r'(\d+) likes?, (\d+) comments?', desc_text)
            if stats_match:
                likes_count = int(stats_match.group(1))
                comments_count = int(stats_match.group(2))
                
                data['likes'] = self._format_count(likes_count)
                data['comments'] = self._format_count(comments_count)
            else:
                data['likes'] = None
                data['comments'] = None
            
            # Extraction du username
            username_match = re.search(r'- ([a-zA-Z0-9._]+) ', desc_text)
            data['username'] = username_match.group(1) if username_match else None
            
            # Extraction de la date
            date_match = re.search(r'le\s+([A-Za-z]+ \d+, \d+)', desc_text)
            if not date_match:
                date_match = re.search(r'on\s+([A-Za-z]+ \d+, \d+)', desc_text)
            data['date'] = date_match.group(1) if date_match else None
            
            # Extraction de la caption
            caption_match = re.search(r'"([^"]*)"', desc_text)
            if caption_match:
                caption_text = caption_match.group(1)
                data['caption'] = caption_text
                hashtags = re.findall(r'#(\w+)', caption_text)
                data['hashtags'] = hashtags
            else:
                data['caption'] = None
                data['hashtags'] = []
        else:
            # Fallback: essayer avec meta name="description"
            description = tree.xpath('//meta[@name="description"]/@content')
            if description:
                desc_text = description[0]
                caption_match = re.search(r'"([^"]*)"', desc_text)
                data['caption'] = caption_match.group(1) if caption_match else None
                data['hashtags'] = re.findall(r'#(\w+)', data['caption'] or '')
            else:
                data['caption'] = None
                data['hashtags'] = []
            
            data['username'] = None
            data['date'] = None
            data['likes'] = None
            data['comments'] = None

        # URL canonique
        canonical = tree.xpath('//link[@rel="canonical"]/@href')
        data['url'] = canonical[0] if canonical else url

        # Image
        thumbnail = tree.xpath('//meta[@property="og:image"]/@content')
        data['image'] = thumbnail[0] if thumbnail else None

        # Type
        data['type'] = "reel" if "/reel/" in url else "post"

        return data

    def _extract_json_from_scripts(self, html_content: str) -> dict:
        """Extraction des données JSON depuis les balises script"""
        try:
            # Recherche de différents patterns JSON
            patterns = [
                r'window\._sharedData\s*=\s*({.*?});',
                r'"gql_data":\s*({.*?}),"hostname"',
                r'{"config":.*?"entry_data":({.*?}),"hostname"',
                r'"PostPage":\s*\[({.*?})\]'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        continue
            
            return {}
        except Exception:
            return {}

    def _format_json_data(self, json_data: dict, url: str) -> dict:
        """Formatage des données JSON extraites"""
        data = {
            "caption": None,
            "username": None,
            "date": None,
            "likes": None,
            "comments": None,
            "hashtags": [],
            "url": url,
            "image": None,
            "type": "reel" if "/reel/" in url else "post"
        }
        
        # Navigation dans la structure JSON (adaptable selon la structure trouvée)
        try:
            # Essayer différentes structures
            if 'graphql' in json_data:
                media = json_data['graphql'].get('shortcode_media', {})
            elif 'shortcode_media' in json_data:
                media = json_data['shortcode_media']
            else:
                media = json_data
            
            # Extraction des données
            if 'edge_media_preview_like' in media:
                data['likes'] = self._format_count(media['edge_media_preview_like'].get('count', 0))
            
            if 'edge_media_to_comment' in media:
                data['comments'] = self._format_count(media['edge_media_to_comment'].get('count', 0))
            
            if 'taken_at_timestamp' in media:
                from datetime import datetime
                data['date'] = datetime.fromtimestamp(media['taken_at_timestamp']).strftime('%B %d, %Y')
            
            if 'owner' in media:
                data['username'] = media['owner'].get('username')
            
            # Caption et hashtags
            if 'edge_media_to_caption' in media:
                edges = media['edge_media_to_caption'].get('edges', [])
                if edges:
                    caption_text = edges[0]['node'].get('text', '')
                    data['caption'] = caption_text
                    data['hashtags'] = re.findall(r'#(\w+)', caption_text)
            
        except (KeyError, TypeError, IndexError):
            pass
        
        return data

    def _format_count(self, count: int) -> str:
        """Formatage des compteurs"""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        else:
            return str(count)

    def _extract_username_from_url(self, url: str) -> str:
        """Extraction du username depuis l'URL si disponible dans le path"""
        # Fallback basique - ne fonctionne que si l'username est dans l'URL
        return None

    def _has_valid_data(self, data: dict) -> bool:
        """Vérifie si les données extraites sont valides"""
        return (data.get('caption') is not None or 
                data.get('likes') is not None or 
                data.get('image') is not None) and 'error' not in data