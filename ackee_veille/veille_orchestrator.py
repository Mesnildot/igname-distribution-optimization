"""
Veille Orchestrator - Orchestre l'ensemble du processus de veille
"""
import os
import sys
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv
import logging

# Import des modules
from collectors.rss_collector import RSSCollector
from collectors.web_search_collector import WebSearchCollector
from collectors.crunchbase_collector import CrunchbaseCollector
from analyzers.llm_analyzer import LLMAnalyzer
from generators.report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VeilleOrchestrator:
    """Orchestrateur principal du système de veille"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialise l'orchestrateur avec la configuration"""
        load_dotenv()

        # Charge la configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Initialise les modules
        self.collectors = [
            RSSCollector(self.config),
            WebSearchCollector(self.config),
            CrunchbaseCollector(self.config)
        ]
        self.analyzer = LLMAnalyzer(self.config)
        self.generator = ReportGenerator(self.config)

        logger.info("Veille Orchestrator initialized")

    def run(self, reference_date: datetime = None):
        """
        Execute le processus complet de veille

        Args:
            reference_date: Date de référence (par défaut: aujourd'hui)
        """
        logger.info("=" * 80)
        logger.info("ACKEE VEILLE - Démarrage du processus")
        logger.info("=" * 80)

        # Si pas de date fournie, demande à l'utilisateur
        if reference_date is None:
            reference_date = self._ask_date()

        # Calcule la période (7 jours avant la date de référence)
        end_date = reference_date
        start_date = reference_date - timedelta(days=7)

        logger.info(f"Période de veille: {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}")
        logger.info(f"Semaine: {start_date.isocalendar()[1]:02d}/{start_date.year}")

        # ÉTAPE 1: Collecte des données
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 1/4: COLLECTE DES DONNÉES")
        logger.info("=" * 80)
        raw_data = self._collect_data(start_date, end_date)

        # Sauvegarde les données brutes
        self._save_raw_data(raw_data, start_date)

        # ÉTAPE 2: Analyse avec LLM
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 2/4: ANALYSE ET SYNTHÈSE (LLM)")
        logger.info("=" * 80)
        synthesis = self.analyzer.analyze(raw_data, start_date, end_date)

        # ÉTAPE 3: Génération des rapports
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 3/4: GÉNÉRATION DES RAPPORTS")
        logger.info("=" * 80)
        report_paths = self.generator.generate(synthesis)

        # ÉTAPE 4: Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 4/4: PROCESSUS TERMINÉ")
        logger.info("=" * 80)
        self._print_summary(raw_data, synthesis, report_paths)

        return report_paths

    def _ask_date(self) -> datetime:
        """Demande la date de référence à l'utilisateur"""
        print("\n" + "="*80)
        print("VEILLE HEBDOMADAIRE ACKEE - CONFIGURATION")
        print("="*80)
        print("\nQuelle est la date du jour où tu lances cette veille ?")
        print("Format: JJ/MM/AAAA (exemple: 16/01/2026)")
        print("Appuie sur ENTRÉE pour utiliser la date d'aujourd'hui\n")

        date_str = input("Date: ").strip()

        if not date_str:
            return datetime.now()

        try:
            return datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            print("❌ Format invalide. Utilisation de la date d'aujourd'hui.")
            return datetime.now()

    def _collect_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Collecte les données de tous les collecteurs"""
        all_data = []

        for collector in self.collectors:
            collector_name = collector.__class__.__name__
            logger.info(f"\n[{collector_name}] Démarrage de la collecte...")

            try:
                data = collector.collect(start_date, end_date)
                all_data.extend(data)
                logger.info(f"[{collector_name}] ✅ {len(data)} items collectés")
            except Exception as e:
                logger.error(f"[{collector_name}] ❌ Erreur: {str(e)}")

        logger.info(f"\n📊 TOTAL: {len(all_data)} items collectés")
        return all_data

    def _save_raw_data(self, raw_data: List[Dict[str, Any]], start_date: datetime):
        """Sauvegarde les données brutes"""
        import json

        data_dir = self.config.get('output', {}).get('reports_dir', 'reports')
        os.makedirs(data_dir, exist_ok=True)

        week_number = start_date.isocalendar()[1]
        year = start_date.year
        filename = os.path.join(data_dir, f'raw_data_s{week_number:02d}_{year}.json')

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📁 Données brutes sauvegardées: {filename}")

    def _print_summary(self, raw_data: List[Dict[str, Any]],
                      synthesis: Dict[str, Any], report_paths: Dict[str, str]):
        """Affiche le résumé final"""
        print("\n" + "="*80)
        print("✅ VEILLE TERMINÉE AVEC SUCCÈS")
        print("="*80)
        print(f"\n📊 Statistiques:")
        print(f"  - Items collectés: {len(raw_data)}")
        print(f"  - Modèle utilisé: {synthesis.get('metadata', {}).get('model', 'N/A')}")
        print(f"\n📄 Fichiers générés:")
        print(f"  - Rapport Markdown: {report_paths['markdown']}")
        print(f"  - Email (.eml): {report_paths['eml']}")
        print(f"\n📧 Prochaines étapes:")
        print(f"  1. Double-cliquez sur le fichier .eml")
        print(f"  2. Vérifiez le contenu et les destinataires")
        print(f"  3. Envoyez l'email!")
        print("\n" + "="*80)


def main():
    """Point d'entrée principal"""
    try:
        # Chemin vers la config
        config_path = os.path.join(os.path.dirname(__file__), 'config/config.yaml')

        # Initialise et lance l'orchestrateur
        orchestrator = VeilleOrchestrator(config_path)
        orchestrator.run()

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Processus interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n❌ Erreur fatale: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
