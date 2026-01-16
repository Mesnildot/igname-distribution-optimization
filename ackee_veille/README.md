# 🔍 Ackee Veille - Système de Veille Automatisé

Système de veille concurrentielle et réglementaire automatisé pour **Ackee Financial Services**.

## 📋 Description

Ce système collecte, analyse et synthétise automatiquement les informations stratégiques pour Ackee sur 6 axes clés :

1. 🎯 **Concurrence & Acteurs** : Levées de fonds, acquisitions, expansions, pricing
2. ⚖️ **Régulation & Compliance** : Nouvelles régulations, licences, sanctions, AML/KYC
3. ⚙️ **Technologie & Infrastructure** : Blockchain, BaaS, rails de paiement, sécurité
4. 📊 **Marché & Tendances** : Reports institutionnels, études, comportements diaspora
5. 🤝 **Écosystème & Partenaires** : Partenariats BaaS/fintechs, VCs, M&A
6. 🆕 **Nouveaux Entrants** : Détection de nouveaux concurrents et acteurs

### Fonctionnalités principales

- ✅ **Collecte automatique** depuis multiples sources (RSS, APIs, Web search)
- ✅ **Analyse intelligente** via API Anthropic Claude
- ✅ **Rapports structurés** (Markdown + Email)
- ✅ **Exécution programmée** (tous les lundis à 08:00)
- ✅ **Priorisation P0/P1/P2** pour chaque information
- ✅ **Sources vérifiables** avec URLs complètes

---

## 🚀 Installation rapide

### Prérequis

- Python 3.8+
- API Key Anthropic (REQUIS)
- API Keys optionnelles : Serper (recherche web), Crunchbase (funding data)

### Installation

```bash
# 1. Cloner ou télécharger le projet
cd ackee_veille

# 2. Lancer le script d'installation
chmod +x setup.sh
./setup.sh

# 3. Configurer les API keys
nano .env

# Ajoutez au minimum :
ANTHROPIC_API_KEY=sk-ant-...

# Recommandé (pour une meilleure collecte) :
SERPER_API_KEY=...
CRUNCHBASE_API_KEY=...
```

---

## 📖 Utilisation

### Mode Manuel (Test)

Pour lancer une veille immédiatement :

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer la veille
python veille_orchestrator.py
```

Le système vous demandera la date de référence (appuyez sur Entrée pour aujourd'hui).

**Fichiers générés** :
- `reports/ackee_veille_sXX_YYYY.md` : Rapport Markdown complet
- `reports/ackee_veille_sXX_email.eml` : Email prêt à envoyer
- `reports/raw_data_sXX_YYYY.json` : Données brutes collectées

### Mode Automatisé (Production)

#### Option 1 : Scheduler Python (Recommandé)

Lance un processus permanent qui exécute la veille tous les lundis à 08:00 :

```bash
source venv/bin/activate
python scheduler.py
```

Le processus tourne en continu. Pour l'arrêter : `Ctrl+C`

#### Option 2 : Service systemd (Linux)

Pour un service qui redémarre automatiquement :

```bash
# 1. Éditez le fichier service
nano ackee-veille.service

# Remplacez :
# - your-username par votre nom d'utilisateur
# - /path/to/ackee_veille par le chemin absolu

# 2. Installez le service
sudo cp ackee-veille.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ackee-veille
sudo systemctl start ackee-veille

# 3. Vérifiez le statut
sudo systemctl status ackee-veille

# 4. Consultez les logs
sudo journalctl -u ackee-veille -f
```

#### Option 3 : Crontab

Alternative simple via cron :

```bash
# Éditez votre crontab
crontab -e

# Ajoutez (adaptez les chemins) :
0 8 * * 1 cd /path/to/ackee_veille && /path/to/ackee_veille/venv/bin/python veille_orchestrator.py >> /path/to/ackee_veille/logs/cron.log 2>&1
```

---

## 📁 Architecture du projet

```
ackee_veille/
├── collectors/              # Modules de collecte de données
│   ├── base_collector.py    # Classe abstraite
│   ├── rss_collector.py     # Collecteur RSS (TechCrunch, The Block, etc.)
│   ├── web_search_collector.py  # Recherche web (Serper API)
│   └── crunchbase_collector.py  # Funding data (Crunchbase API)
│
├── analyzers/               # Modules d'analyse
│   └── llm_analyzer.py      # Analyse et synthèse via Claude
│
├── generators/              # Modules de génération de rapports
│   └── report_generator.py # Génération MD + EML
│
├── config/                  # Configuration
│   └── config.yaml          # Config principale (sources, concurrents, etc.)
│
├── reports/                 # Rapports générés (créé automatiquement)
├── data/                    # Données temporaires (créé automatiquement)
├── logs/                    # Logs (créé automatiquement)
│
├── veille_orchestrator.py   # Orchestrateur principal
├── scheduler.py             # Scheduler automatique
├── setup.sh                 # Script d'installation
├── requirements.txt         # Dépendances Python
├── .env.example             # Template pour les API keys
├── ackee-veille.service     # Service systemd
├── crontab.example          # Exemple crontab
└── README.md                # Ce fichier
```

---

## ⚙️ Configuration

### Fichier `config/config.yaml`

Configuration centralisée :

- **Contexte Ackee** : Corridors, concurrents, stade
- **Sources de veille** : Médias (RSS), APIs, régulateurs
- **Concurrents à tracker** : Liste des acteurs directs et écosystème
- **Recipients** : Liste des emails destinataires
- **Scheduler** : Fréquence et timing d'exécution
- **LLM** : Configuration du modèle Claude

**Pour modifier** :
```bash
nano config/config.yaml
```

### Fichier `.env`

Contient les API keys sensibles :

```bash
ANTHROPIC_API_KEY=sk-ant-...      # REQUIS
SERPER_API_KEY=...                # Recommandé
CRUNCHBASE_API_KEY=...            # Optionnel
```

⚠️ **Ne jamais committer le fichier `.env` dans Git**

---

## 🔑 API Keys

### Anthropic API (REQUIS)

**Obtention** :
1. Créez un compte sur https://console.anthropic.com
2. Générez une API key dans Settings > API Keys
3. Coût estimé : ~$2-5 par semaine (selon volume de données)

**Modèle utilisé** : `claude-sonnet-4-5-20250929` (optimal qualité/prix)

### Serper API (Recommandé)

**Obtention** :
1. Créez un compte sur https://serper.dev
2. 2500 requêtes gratuites/mois
3. Alternative gratuite : SerpAPI (https://serpapi.com)

**Utilité** : Recherches web ciblées sur Google pour compléter les flux RSS

### Crunchbase API (Optionnel)

**Obtention** :
1. Compte sur https://www.crunchbase.com
2. Plan payant requis pour l'API (~$29/mois minimum)

**Utilité** : Données structurées sur les levées de fonds et acquisitions

**Alternative gratuite** : Désactiver ce collecteur (la veille fonctionnera sans)

---

## 📊 Format des rapports

### Rapport Markdown

Structure complète avec :
- Dashboard hebdomadaire (tableau de métriques)
- 6 axes de veille avec scoring P0/P1/P2
- Signaux faibles (tendances émergentes)
- Recommandations stratégiques
- Quick wins (actions <7 jours)

### Email (.eml)

Email prêt à envoyer avec :
- **Sujet** : Semaine + alerte principale
- **Corps** : Résumé exécutif (alertes critiques, quick wins, recommandations)
- **Pièce jointe** : Rapport Markdown complet
- **Destinataires** : 13 co-fondateurs (configurables dans `config.yaml`)

**Envoi** :
1. Double-cliquez sur le fichier `.eml`
2. Votre client email s'ouvre avec l'email pré-rempli
3. Vérifiez et envoyez

---

## 🛠️ Dépannage

### Problème : Pas de données collectées

**Solutions** :
1. Vérifiez votre connexion internet
2. Vérifiez les API keys dans `.env`
3. Consultez les logs : `tail -f veille_scheduler.log`

### Problème : Erreur Anthropic API

**Solutions** :
1. Vérifiez que `ANTHROPIC_API_KEY` est valide
2. Vérifiez votre crédit API sur https://console.anthropic.com
3. Le modèle utilisé est disponible : `claude-sonnet-4-5-20250929`

### Problème : Service ne démarre pas (systemd)

**Solutions** :
```bash
# Vérifiez les logs
sudo journalctl -u ackee-veille -n 50

# Vérifiez les permissions
ls -la /path/to/ackee_veille

# Testez manuellement
cd /path/to/ackee_veille
source venv/bin/activate
python scheduler.py
```

### Problème : Trop de données, réponse LLM tronquée

**Solutions** :
1. Éditez `config/config.yaml` et augmentez `llm.max_tokens` (ex: 16000)
2. Réduisez le nombre de sources dans `sources` (commentez certaines)
3. Ajoutez plus de filtres par mots-clés

---

## 🔄 Maintenance

### Mise à jour des dépendances

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Ajout de nouvelles sources

Éditez `config/config.yaml` :

```yaml
sources:
  media:
    - name: "Nouvelle Source"
      rss: "https://example.com/feed.rss"
      keywords: ["fintech", "remittance"]
```

### Ajout de nouveaux concurrents

```yaml
competitors:
  direct:
    - name: "Nouveau Concurrent"
      url: "https://example.com"
      crunchbase: "example-slug"
      linkedin: "example-company"
```

### Consultation des logs

```bash
# Logs du scheduler
tail -f veille_scheduler.log

# Logs systemd
sudo journalctl -u ackee-veille -f

# Logs cron
tail -f logs/cron.log
```

---

## 📈 Évolutions futures possibles

- [ ] Interface web de consultation des veilles
- [ ] Alertes Slack/Teams en temps réel
- [ ] Dashboard interactif avec graphiques
- [ ] Intégration LinkedIn pour monitoring des annonces
- [ ] Scraping avancé des sites régulateurs
- [ ] Détection automatique de signaux faibles via ML
- [ ] Export PDF des rapports
- [ ] API REST pour interroger l'historique

---

## 🤝 Support

Pour toute question ou problème :

1. Consultez les logs
2. Vérifiez la configuration
3. Testez en mode manuel
4. Contactez l'équipe technique Ackee

---

## 📄 Licence

Propriétaire - Ackee Financial Services
Usage interne uniquement.

---

**Généré par le système de veille Ackee**
*Version 1.0 - Janvier 2026*
