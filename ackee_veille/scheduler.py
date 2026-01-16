"""
Scheduler - Automatisation de l'exécution de la veille
"""
import schedule
import time
import os
from datetime import datetime
from veille_orchestrator import VeilleOrchestrator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('veille_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_veille():
    """Execute la veille automatiquement"""
    try:
        logger.info("="*80)
        logger.info("DÉMARRAGE AUTOMATIQUE DE LA VEILLE")
        logger.info("="*80)

        # Initialise l'orchestrateur
        config_path = os.path.join(os.path.dirname(__file__), 'config/config.yaml')
        orchestrator = VeilleOrchestrator(config_path)

        # Execute avec la date du jour
        orchestrator.run(reference_date=datetime.now())

        logger.info("✅ Veille terminée avec succès")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de la veille: {str(e)}", exc_info=True)


def main():
    """Configure et lance le scheduler"""
    logger.info("🚀 Démarrage du scheduler de veille Ackee")
    logger.info("Configuration: Tous les lundis à 08:00 (Europe/Paris)")

    # Configure la tâche planifiée
    # Tous les lundis à 08:00
    schedule.every().monday.at("08:00").do(run_veille)

    logger.info("⏰ Scheduler actif. En attente de la prochaine exécution...")
    logger.info("   Prochaine exécution: Lundi à 08:00")
    logger.info("   (Appuyez sur Ctrl+C pour arrêter)")

    # Boucle d'exécution
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
        except KeyboardInterrupt:
            logger.info("\n⚠️  Scheduler arrêté par l'utilisateur")
            break
        except Exception as e:
            logger.error(f"❌ Erreur dans le scheduler: {str(e)}", exc_info=True)
            time.sleep(300)  # Attend 5 minutes avant de réessayer


if __name__ == '__main__':
    main()
