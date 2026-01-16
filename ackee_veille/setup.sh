#!/bin/bash

# Script de setup pour le système de veille Ackee

echo "=============================================="
echo "  ACKEE VEILLE - Installation"
echo "=============================================="
echo ""

# Vérifie Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python 3 détecté: $(python3 --version)"

# Crée un environnement virtuel
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Active l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installe les dépendances
echo ""
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Copie le fichier .env.example
if [ ! -f .env ]; then
    echo ""
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Éditez le fichier .env et ajoutez vos API keys:"
    echo "   - ANTHROPIC_API_KEY (REQUIS)"
    echo "   - SERPER_API_KEY (Recommandé)"
    echo "   - CRUNCHBASE_API_KEY (Optionnel)"
else
    echo ""
    echo "✅ Fichier .env déjà existant"
fi

# Crée les répertoires nécessaires
echo ""
echo "📁 Création des répertoires..."
mkdir -p reports data logs

echo ""
echo "=============================================="
echo "  ✅ Installation terminée!"
echo "=============================================="
echo ""
echo "📋 Prochaines étapes:"
echo ""
echo "1. Configurez vos API keys dans le fichier .env:"
echo "   nano .env"
echo ""
echo "2. Lancez une veille manuelle (pour tester):"
echo "   source venv/bin/activate"
echo "   python veille_orchestrator.py"
echo ""
echo "3. Configurez l'automatisation (lundi à 08:00):"
echo "   python scheduler.py"
echo ""
echo "   OU avec systemd (service permanent):"
echo "   sudo cp ackee-veille.service /etc/systemd/system/"
echo "   sudo systemctl enable ackee-veille"
echo "   sudo systemctl start ackee-veille"
echo ""
echo "4. Consultez les logs:"
echo "   tail -f veille_scheduler.log"
echo ""
echo "=============================================="
