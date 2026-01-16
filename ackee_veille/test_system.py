"""
Script de test pour vérifier l'installation du système de veille
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

def test_imports():
    """Test des imports de modules"""
    print("\n🔍 Test 1: Imports des modules...")
    try:
        from collectors.rss_collector import RSSCollector
        from collectors.web_search_collector import WebSearchCollector
        from collectors.crunchbase_collector import CrunchbaseCollector
        from analyzers.llm_analyzer import LLMAnalyzer
        from generators.report_generator import ReportGenerator
        print("   ✅ Tous les modules sont importables")
        return True
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_config():
    """Test du chargement de la configuration"""
    print("\n🔍 Test 2: Configuration...")
    try:
        import yaml
        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("   ✅ Fichier config.yaml chargé")
        print(f"   - Sources média: {len(config.get('sources', {}).get('media', []))}")
        print(f"   - Concurrents directs: {len(config.get('competitors', {}).get('direct', []))}")
        print(f"   - Recipients: {len(config.get('recipients', []))}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur de configuration: {e}")
        return False

def test_env():
    """Test des variables d'environnement"""
    print("\n🔍 Test 3: Variables d'environnement...")
    load_dotenv()

    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    crunchbase_key = os.getenv('CRUNCHBASE_API_KEY')

    if anthropic_key:
        print(f"   ✅ ANTHROPIC_API_KEY trouvée (commence par: {anthropic_key[:10]}...)")
    else:
        print("   ❌ ANTHROPIC_API_KEY manquante (REQUIS)")
        return False

    if serper_key:
        print(f"   ✅ SERPER_API_KEY trouvée (recommandé)")
    else:
        print("   ⚠️  SERPER_API_KEY manquante (recommandé mais optionnel)")

    if crunchbase_key:
        print(f"   ✅ CRUNCHBASE_API_KEY trouvée (optionnel)")
    else:
        print("   ℹ️  CRUNCHBASE_API_KEY manquante (optionnel)")

    return True

def test_collectors():
    """Test de l'instanciation des collecteurs"""
    print("\n🔍 Test 4: Collecteurs de données...")
    try:
        import yaml
        from collectors.rss_collector import RSSCollector
        from collectors.web_search_collector import WebSearchCollector

        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Test RSS Collector
        rss = RSSCollector(config)
        print("   ✅ RSSCollector initialisé")

        # Test Web Search Collector
        web = WebSearchCollector(config)
        print("   ✅ WebSearchCollector initialisé")

        return True
    except Exception as e:
        print(f"   ❌ Erreur d'instanciation: {e}")
        return False

def test_analyzer():
    """Test de l'analyseur LLM"""
    print("\n🔍 Test 5: Analyseur LLM...")
    try:
        import yaml
        from analyzers.llm_analyzer import LLMAnalyzer

        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        analyzer = LLMAnalyzer(config)
        print("   ✅ LLMAnalyzer initialisé")
        print(f"   - Modèle: {analyzer.model}")
        print(f"   - Max tokens: {analyzer.max_tokens}")
        return True
    except ValueError as e:
        print(f"   ❌ {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_generator():
    """Test du générateur de rapports"""
    print("\n🔍 Test 6: Générateur de rapports...")
    try:
        import yaml
        from generators.report_generator import ReportGenerator

        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        generator = ReportGenerator(config)
        print("   ✅ ReportGenerator initialisé")
        print(f"   - Répertoire de sortie: {generator.reports_dir}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_directories():
    """Test de la création des répertoires"""
    print("\n🔍 Test 7: Répertoires...")
    dirs = ['reports', 'data', 'logs']
    all_ok = True

    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ existe")
        else:
            print(f"   ⚠️  {dir_name}/ n'existe pas (sera créé automatiquement)")

    return all_ok

def main():
    """Execute tous les tests"""
    print("="*80)
    print("  ACKEE VEILLE - Test du système")
    print("="*80)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Variables d'environnement", test_env()))
    results.append(("Collecteurs", test_collectors()))
    results.append(("Analyseur", test_analyzer()))
    results.append(("Générateur", test_generator()))
    results.append(("Répertoires", test_directories()))

    # Résumé
    print("\n" + "="*80)
    print("  RÉSUMÉ DES TESTS")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"  {status:12} - {name}")

    print("\n" + "-"*80)
    print(f"  Total: {passed}/{total} tests passés")
    print("-"*80)

    if passed == total:
        print("\n🎉 Tous les tests sont passés ! Le système est prêt.")
        print("\nProchaines étapes:")
        print("  1. Lancez une veille test: python veille_orchestrator.py")
        print("  2. Configurez l'automatisation: python scheduler.py")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        print("\nConsultez le README.md pour plus d'informations.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
