"""
RSS Collector - Collecte les articles depuis les flux RSS
"""
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from .base_collector import BaseCollector, logger


class RSSCollector(BaseCollector):
    """Collecteur pour les flux RSS"""

    def collect(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Collecte les articles RSS pour la période"""
        logger.info("Starting RSS collection...")
        self.data = []

        sources = self.config.get('sources', {}).get('media', [])

        for source in sources:
            if 'rss' in source:
                logger.info(f"Fetching RSS feed: {source['name']}")
                try:
                    articles = self._fetch_rss(
                        source['rss'],
                        source['name'],
                        source.get('keywords', []),
                        start_date,
                        end_date
                    )
                    self.data.extend(articles)
                    logger.info(f"Collected {len(articles)} articles from {source['name']}")
                except Exception as e:
                    logger.error(f"Error fetching {source['name']}: {str(e)}")

        logger.info(f"Total RSS articles collected: {len(self.data)}")
        return self.data

    def _fetch_rss(self, rss_url: str, source_name: str,
                   keywords: List[str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère et filtre les articles d'un flux RSS"""
        articles = []

        try:
            feed = feedparser.parse(rss_url)

            for entry in feed.entries:
                # Parse date
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if not published:
                    continue

                article_date = datetime(*published[:6])

                # Filtre par date
                if not (start_date <= article_date <= end_date):
                    continue

                # Filtre par mots-clés
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                full_text = f"{title} {summary}"

                if keywords and not self.filter_by_keywords(full_text, keywords):
                    continue

                # Formate l'article
                article = self.format_article(
                    title=title,
                    url=entry.get('link', ''),
                    date=article_date,
                    summary=summary[:500],  # Limite à 500 caractères
                    source=source_name,
                    keywords=keywords
                )

                articles.append(article)

        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_url}: {str(e)}")

        return articles
