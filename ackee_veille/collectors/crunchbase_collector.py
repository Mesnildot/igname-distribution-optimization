"""
Crunchbase Collector - Collecte les données de funding via l'API Crunchbase
"""
import os
import requests
from datetime import datetime
from typing import List, Dict, Any
from .base_collector import BaseCollector, logger


class CrunchbaseCollector(BaseCollector):
    """Collecteur pour les données Crunchbase (funding, acquisitions)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv('CRUNCHBASE_API_KEY')
        self.base_url = "https://api.crunchbase.com/api/v4"

    def collect(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Collecte les annonces de funding et M&A"""
        logger.info("Starting Crunchbase collection...")
        self.data = []

        if not self.api_key:
            logger.warning("CRUNCHBASE_API_KEY not found, skipping Crunchbase collection")
            return self.data

        # Collecte des funding rounds
        try:
            funding_rounds = self._get_funding_rounds(start_date, end_date)
            self.data.extend(funding_rounds)
        except Exception as e:
            logger.error(f"Error collecting funding rounds: {str(e)}")

        # Collecte des acquisitions
        try:
            acquisitions = self._get_acquisitions(start_date, end_date)
            self.data.extend(acquisitions)
        except Exception as e:
            logger.error(f"Error collecting acquisitions: {str(e)}")

        logger.info(f"Total Crunchbase items collected: {len(self.data)}")
        return self.data

    def _get_funding_rounds(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère les funding rounds pertinents"""
        results = []

        # Note: L'API Crunchbase v4 nécessite des requêtes complexes
        # Cette implémentation est simplifiée
        endpoint = f"{self.base_url}/searches/funding_rounds"

        headers = {
            'X-cb-user-key': self.api_key,
            'Content-Type': 'application/json'
        }

        # Recherche de startups fintech liées aux remittances
        payload = {
            "field_ids": [
                "announced_on",
                "funded_organization_identifier",
                "money_raised",
                "investment_type",
                "investor_identifiers"
            ],
            "query": [
                {
                    "type": "predicate",
                    "field_id": "announced_on",
                    "operator_id": "between",
                    "values": [
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    ]
                },
                {
                    "type": "predicate",
                    "field_id": "funded_organization_categories",
                    "operator_id": "includes",
                    "values": ["fintech", "payments", "blockchain", "financial services"]
                }
            ],
            "limit": 50
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data.get('entities', []):
                properties = item.get('properties', {})
                org_id = properties.get('funded_organization_identifier', {})
                org_name = org_id.get('value', 'Unknown')

                article = self.format_article(
                    title=f"Funding: {org_name} raises {properties.get('money_raised', {}).get('value_usd', 'N/A')}",
                    url=f"https://www.crunchbase.com/organization/{org_id.get('permalink', '')}",
                    date=datetime.strptime(properties.get('announced_on', ''), '%Y-%m-%d'),
                    summary=f"Investment type: {properties.get('investment_type', 'N/A')}",
                    source="Crunchbase",
                    keywords=["funding"]
                )
                results.append(article)

        except requests.exceptions.RequestException as e:
            logger.error(f"Crunchbase API request error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing Crunchbase data: {str(e)}")

        return results

    def _get_acquisitions(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère les acquisitions pertinentes"""
        results = []

        endpoint = f"{self.base_url}/searches/acquisitions"

        headers = {
            'X-cb-user-key': self.api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            "field_ids": [
                "announced_on",
                "acquirer_identifier",
                "acquiree_identifier",
                "price"
            ],
            "query": [
                {
                    "type": "predicate",
                    "field_id": "announced_on",
                    "operator_id": "between",
                    "values": [
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    ]
                }
            ],
            "limit": 50
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data.get('entities', []):
                properties = item.get('properties', {})
                acquirer = properties.get('acquirer_identifier', {}).get('value', 'Unknown')
                acquiree = properties.get('acquiree_identifier', {}).get('value', 'Unknown')

                article = self.format_article(
                    title=f"Acquisition: {acquirer} acquires {acquiree}",
                    url=f"https://www.crunchbase.com/acquisition/{item.get('uuid', '')}",
                    date=datetime.strptime(properties.get('announced_on', ''), '%Y-%m-%d'),
                    summary=f"Price: {properties.get('price', {}).get('value_usd', 'Undisclosed')}",
                    source="Crunchbase",
                    keywords=["acquisition", "M&A"]
                )
                results.append(article)

        except requests.exceptions.RequestException as e:
            logger.error(f"Crunchbase acquisitions API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing acquisitions data: {str(e)}")

        return results
