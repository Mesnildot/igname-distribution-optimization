"""
Base Collector - Classe abstraite pour tous les collecteurs
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Classe de base pour tous les collecteurs de veille"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = []

    @abstractmethod
    def collect(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Collecte les données pour la période donnée

        Args:
            start_date: Date de début de la période
            end_date: Date de fin de la période

        Returns:
            Liste de dictionnaires contenant les informations collectées
        """
        pass

    def filter_by_keywords(self, text: str, keywords: List[str]) -> bool:
        """Filtre le texte par mots-clés"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def format_article(self, title: str, url: str, date: datetime,
                       summary: str, source: str, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Formate un article au format standard

        Returns:
            Dict avec les clés: title, url, date, summary, source, keywords
        """
        return {
            "title": title,
            "url": url,
            "date": date.isoformat() if isinstance(date, datetime) else date,
            "summary": summary,
            "source": source,
            "keywords": keywords or [],
            "collected_at": datetime.now().isoformat()
        }

    def save_raw_data(self, filename: str):
        """Sauvegarde les données brutes collectées"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw data saved to {filename}")
