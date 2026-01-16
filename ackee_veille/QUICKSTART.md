# 🚀 QUICKSTART - Démarrage Rapide

Lancez votre première veille Ackee en 5 minutes !

## ⚡ Installation Express (5 min)

```bash
# 1. Aller dans le répertoire
cd ackee_veille

# 2. Installer (automatique)
chmod +x setup.sh
./setup.sh

# 3. Configurer les API keys (REQUIS)
nano .env
```

Dans `.env`, ajoutez au minimum :
```bash
ANTHROPIC_API_KEY=sk-ant-votre-clé-ici
```

**Obtenir une clé Anthropic** :
1. Allez sur https://console.anthropic.com
2. Créez un compte
3. Générez une API key dans Settings > API Keys
4. Ajoutez $10 de crédit pour commencer

## 🧪 Test du système

```bash
source venv/bin/activate
python test_system.py
```

Si tous les tests passent ✅, vous êtes prêt !

## 🏃 Première veille (test)

```bash
source venv/bin/activate
python veille_orchestrator.py
```

Le système va :
1. Vous demander la date (appuyez sur Entrée pour aujourd'hui)
2. Collecter les données (2-3 min)
3. Analyser avec Claude (1-2 min)
4. Générer les rapports

**Résultat** : Deux fichiers dans `reports/` :
- `ackee_veille_sXX_2026.md` : Rapport complet
- `ackee_veille_sXX_email.eml` : Email prêt à envoyer

## 📧 Envoyer l'email

**Sur Mac/Linux** :
```bash
cd reports
open ackee_veille_s*_email.eml
```

**Sur Windows** :
Double-cliquez sur le fichier `.eml`

Votre client email s'ouvre avec l'email pré-rempli. Vérifiez et envoyez !

## ⏰ Automatiser (lundi à 08:00)

### Option simple : Scheduler Python

```bash
source venv/bin/activate
python scheduler.py
```

Laissez tourner (ou utilisez `screen`/`tmux` pour détacher la session).

### Option robuste : Service systemd (Linux)

```bash
# 1. Éditez le service
nano ackee-veille.service

# Remplacez :
# - your-username → votre user
# - /path/to/ackee_veille → le chemin complet

# 2. Installez
sudo cp ackee-veille.service /etc/systemd/system/
sudo systemctl enable ackee-veille
sudo systemctl start ackee-veille

# 3. Vérifiez
sudo systemctl status ackee-veille
```

## 📊 Consulter les résultats

```bash
# Logs du scheduler
tail -f veille_scheduler.log

# Derniers rapports
ls -lt reports/

# Ouvrir le dernier rapport
cat reports/ackee_veille_s*_2026.md | head -100
```

## 🆘 Problèmes courants

### ❌ "ANTHROPIC_API_KEY not found"

**Solution** : Vérifiez que `.env` existe et contient la clé :
```bash
cat .env
```

### ❌ "No module named 'anthropic'"

**Solution** : Réinstallez les dépendances :
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ "No data collected"

**Solutions** :
1. Vérifiez votre connexion internet
2. Ajoutez `SERPER_API_KEY` dans `.env` pour plus de sources
3. Consultez les logs : `tail -f veille_scheduler.log`

### ❌ Rate limit Anthropic API

**Solution** : Ajoutez du crédit sur https://console.anthropic.com/settings/billing

## ✅ Checklist post-installation

- [ ] `test_system.py` passe tous les tests
- [ ] Première veille manuelle réussie
- [ ] Rapports générés dans `reports/`
- [ ] Email `.eml` s'ouvre correctement
- [ ] Scheduler configuré (systemd ou cron)

## 📚 Documentation complète

Pour aller plus loin, consultez le [README.md](README.md) complet.

---

**Besoin d'aide ?** Consultez les logs ou contactez l'équipe technique Ackee.
