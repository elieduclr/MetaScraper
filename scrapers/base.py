from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Vérifie si ce scraper peut gérer cette URL"""
        pass

    @abstractmethod
    def scrape(self, url: str) -> dict:
        """Scrape les métadonnées depuis l'URL"""
        pass
