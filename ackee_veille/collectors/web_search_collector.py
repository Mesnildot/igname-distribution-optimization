"""
Web Search Collector - Utilise des APIs de recherche (Serper, SerpAPI, etc.)
"""
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base_collector import BaseCollector, logger


class WebSearchCollector(BaseCollector):
    """Collecteur utilisant des APIs de recherche web"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"

    def collect(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Collecte via recherches web ciblées"""
        logger.info("Starting web search collection...")
        self.data = []

        if not self.api_key:
            logger.warning("SERPER_API_KEY not found, skipping web search collection")
            return self.data

        # Recherches pour les concurrents
        competitors = self.config.get('competitors', {}).get('direct', [])
        for competitor in competitors[:5]:  # Limite pour éviter trop de requêtes
            competitor_name = competitor.get('name', competitor)
            queries = [
                f"{competitor_name} funding announcement",
                f"{competitor_name} new feature launch",
                f"{competitor_name} expansion africa",
            ]

            for query in queries:
                try:
                    results = self._search(query, start_date, end_date)
                    self.data.extend(results)
                except Exception as e:
                    logger.error(f"Error searching '{query}': {str(e)}")

        # Recherches thématiques
        thematic_queries = [
            "fintech remittance africa funding",
            "mobile money UEMOA regulation",
            "stablecoin payments africa",
            "BaaS provider europe fintech",
            "BCEAO fintech license",
        ]

        for query in thematic_queries:
            try:
                results = self._search(query, start_date, end_date)
                self.data.extend(results)
            except Exception as e:
                logger.error(f"Error searching '{query}': {str(e)}")

        logger.info(f"Total web search results collected: {len(self.data)}")
        return self.data

    def _search(self, query: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Effectue une recherche via Serper API"""
        results = []

        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        # Calcul du paramètre de date pour Google
        days_back = (datetime.now() - start_date).days
        date_restrict = f"d{days_back}" if days_back <= 30 else "m1"

        payload = {
            'q': query,
            'num': 10,
            'gl': 'fr',  # Géolocalisation France
            'hl': 'fr',  # Langue
            'tbs': date_restrict,  # Restriction temporelle
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get('organic', []):
                article = self.format_article(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    date=datetime.now(),  # Serper ne fournit pas toujours la date exacte
                    summary=item.get('snippet', ''),
                    source="Web Search",
                    keywords=[query]
                )
                results.append(article)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for query '{query}': {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for query '{query}': {str(e)}")

        return results
