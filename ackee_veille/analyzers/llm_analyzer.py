"""
LLM Analyzer - Utilise l'API Anthropic Claude pour analyser et synthétiser la veille
"""
import os
import json
from typing import List, Dict, Any
from datetime import datetime
from anthropic import Anthropic
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analyseur utilisant Claude pour synthétiser la veille"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.model = config.get('llm', {}).get('model', 'claude-sonnet-4-5-20250929')
        self.max_tokens = config.get('llm', {}).get('max_tokens', 8000)
        self.temperature = config.get('llm', {}).get('temperature', 0.3)

    def analyze(self, raw_data: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Analyse les données brutes et génère la synthèse structurée

        Args:
            raw_data: Liste des articles/infos collectés
            start_date: Date de début de la période
            end_date: Date de fin de la période

        Returns:
            Dictionnaire structuré avec toutes les sections de la veille
        """
        logger.info(f"Starting LLM analysis of {len(raw_data)} items...")

        # Prépare le contexte pour Claude
        context = self._prepare_context(raw_data, start_date, end_date)

        # Génère la synthèse via Claude
        synthesis = self._generate_synthesis(context, start_date, end_date)

        logger.info("LLM analysis completed")
        return synthesis

    def _prepare_context(self, raw_data: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> str:
        """Prépare le contexte des données pour Claude"""

        # Groupe les données par source
        grouped_data = {}
        for item in raw_data:
            source = item.get('source', 'Other')
            if source not in grouped_data:
                grouped_data[source] = []
            grouped_data[source].append(item)

        # Format le contexte
        context = f"""# DONNÉES COLLECTÉES POUR LA VEILLE ACKEE
Période: {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}
Total items: {len(raw_data)}

## DONNÉES PAR SOURCE

"""
        for source, items in grouped_data.items():
            context += f"### {source} ({len(items)} items)\n\n"
            for item in items[:20]:  # Limite à 20 items par source pour éviter de dépasser la limite
                context += f"- **{item.get('title', 'No title')}**\n"
                context += f"  Date: {item.get('date', 'N/A')}\n"
                context += f"  URL: {item.get('url', 'N/A')}\n"
                context += f"  Summary: {item.get('summary', 'N/A')[:200]}...\n\n"

        return context

    def _generate_synthesis(self, context: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Génère la synthèse via l'API Claude"""

        # Charge le prompt de veille original
        prompt = self._build_analysis_prompt(context, start_date, end_date)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse la réponse de Claude
            synthesis_text = response.content[0].text

            # Structure la réponse
            synthesis = {
                "metadata": {
                    "period_start": start_date.isoformat(),
                    "period_end": end_date.isoformat(),
                    "generated_at": datetime.now().isoformat(),
                    "model": self.model,
                    "total_items_analyzed": len(context.split('\n'))
                },
                "synthesis": synthesis_text,
                "raw_response": synthesis_text
            }

            return synthesis

        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise

    def _build_analysis_prompt(self, context: str, start_date: datetime, end_date: datetime) -> str:
        """Construit le prompt d'analyse pour Claude"""

        week_number = start_date.isocalendar()[1]
        year = start_date.year

        prompt = f"""Tu es un analyste stratégique spécialisé en fintech et remittances pour Ackee Financial Services.

# CONTEXTE ACKEE
Ackee développe une plateforme blockchain de transferts d'argent pour la diaspora africaine en Europe avec 0,5% de frais.
- Corridors: France/UK/EU → Togo/Bénin/Côte d'Ivoire/UEMOA
- Concurrents: Wave, Wise, Remitly, WorldRemit, Revolut, néobanques diaspora
- Stade: Développement produit, 13 co-fondateurs

# PÉRIODE ANALYSÉE
Semaine {week_number}/{year} : {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}

# DONNÉES COLLECTÉES
{context}

# TA MISSION
Analyse ces données et génère un rapport de veille structuré selon les 6 axes suivants. IMPORTANT: Pour chaque information, tu DOIS inclure le lien source (URL) extrait des données.

## AXE 1: CONCURRENCE & ACTEURS 🎯
Identifie les mouvements stratégiques (levées de fonds, acquisitions, partenariats, expansion, pricing, nouveaux produits).
Pour chaque info, indique:
- Priorité [P0/P1/P2]
- Nom acteur + Type mouvement
- Date
- Résumé (2-3 lignes)
- Implication pour Ackee
- **Source (URL complète)**

## AXE 2: RÉGULATION & COMPLIANCE ⚖️
Identifie nouvelles régulations, licences, sanctions, sandboxes, exigences AML/KYC.
Format identique avec impact timeline et action Ackee.

## AXE 3: TECHNOLOGIE & INFRASTRUCTURE ⚙️
Innovations blockchain, partenariats tech, nouveaux rails, cybersécurité, standards.
Indique si c'est une opportunité ou menace pour Ackee.

## AXE 4: MARCHÉ & TENDANCES 📊
Reports institutionnels, études marché, pricing, consumer insights.
Liste les key findings et insights pour Ackee.

## AXE 5: ÉCOSYSTÈME & PARTENAIRES 🤝
Nouveaux partenariats BaaS/fintechs, VCs activity, incubateurs, M&A.
Indique les opportunités de partenariat pour Ackee.

## AXE 6: NOUVEAUX ENTRANTS 🆕
Détecte les nouveaux acteurs (funding, sandboxes, accelerators).
Pour chaque: segment, corridor, stade, funding, team, différenciateur, action suggérée.

## SIGNAUX FAIBLES 📡
2-3 tendances émergentes à surveiller avec implications potentielles à 6-12 mois.

## RECOMMANDATIONS 💡
1-2 actions stratégiques basées sur cette veille.

## QUICK WINS ⚡
1-3 actions concrètes réalisables en <7 jours avec deadlines.

# FORMAT DE SORTIE
Génère un rapport structuré en Markdown, en français, avec:
- Dashboard semaine (tableau avec métriques)
- Les 6 axes avec scoring P0/P1/P2
- Signaux faibles
- Recommandations
- Quick wins

CRITIQUE: Chaque information DOIT avoir son URL source extraite des données fournies.
Focus sur l'actionabilité: "Et alors, pour Ackee?"
Prioriser qualité > quantité.
"""

        return prompt

    def extract_critical_alerts(self, synthesis: Dict[str, Any]) -> List[str]:
        """Extrait les alertes critiques (P0) de la synthèse"""
        # Cette fonction pourrait utiliser un second appel à Claude pour extraire uniquement les P0
        # Pour l'instant, on retourne une liste vide
        return []
