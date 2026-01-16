# 🏗️ Architecture du Système de Veille Ackee

## Vue d'ensemble

Le système de veille Ackee est une plateforme modulaire automatisée qui collecte, analyse et synthétise les informations stratégiques pour Ackee Financial Services.

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTÈME DE VEILLE ACKEE                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   COLLECTE   │────▶│   ANALYSE    │────▶│  GÉNÉRATION  │
│              │     │              │     │              │
│ - RSS Feeds  │     │ LLM Analyzer │     │ - Markdown   │
│ - Web Search │     │ (Claude API) │     │ - Email EML  │
│ - Crunchbase │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
       ▲                                           │
       │                                           ▼
       │                                  ┌──────────────┐
       │                                  │ DESTINATAIRES│
       │                                  │              │
       └──────────────────────────────────│  13 Co-fnd  │
                 SCHEDULER                └──────────────┘
           (Lundi 08:00 auto)
```

---

## 🔧 Composants principaux

### 1. **Orchestrateur** (`veille_orchestrator.py`)

**Rôle** : Chef d'orchestre du système

**Responsabilités** :
- Coordonne l'exécution des 3 phases (Collecte → Analyse → Génération)
- Gère le cycle de vie complet d'une veille
- Sauvegarde les données intermédiaires
- Affiche les résultats et statistiques

**Flux d'exécution** :
```python
1. ask_date() → Demande date de référence
2. calculate_period() → Calcule semaine (date - 7 jours)
3. collect_data() → Lance tous les collecteurs
4. save_raw_data() → Sauvegarde JSON brut
5. analyze() → Envoie à Claude pour synthèse
6. generate_reports() → Crée MD + EML
7. print_summary() → Affiche résultats
```

---

### 2. **Collecteurs** (`collectors/`)

#### 2.1 Base Collector (`base_collector.py`)

Classe abstraite définissant l'interface commune :
```python
class BaseCollector(ABC):
    def collect(start_date, end_date) -> List[Dict]
    def filter_by_keywords(text, keywords) -> bool
    def format_article(...) -> Dict
```

#### 2.2 RSS Collector (`rss_collector.py`)

**Sources** :
- TechCrunch, The Block, TechCabal, Briter Bridges, etc.

**Fonctionnement** :
1. Parse chaque flux RSS avec `feedparser`
2. Filtre par date (période de 7 jours)
3. Filtre par mots-clés (fintech, remittance, africa, etc.)
4. Extrait : title, url, date, summary

**Configuration** : `config.yaml > sources.media`

#### 2.3 Web Search Collector (`web_search_collector.py`)

**API** : Serper (Google Search API)

**Fonctionnement** :
1. Génère des requêtes ciblées :
   - Par concurrent : "Wave funding announcement"
   - Thématiques : "fintech remittance africa funding"
2. Effectue recherches via API Serper
3. Filtre et structure les résultats

**Limite** : 10 résultats par requête (configurable)

#### 2.4 Crunchbase Collector (`crunchbase_collector.py`)

**API** : Crunchbase API v4

**Données collectées** :
- Funding rounds (levées de fonds)
- Acquisitions

**Filtres** :
- Catégories : fintech, payments, blockchain, financial services
- Période : 7 derniers jours
- Géographie : Focus Afrique + Europe

---

### 3. **Analyseur** (`analyzers/llm_analyzer.py`)

**Rôle** : Intelligence du système

**Modèle** : Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)

**Fonctionnement** :

```python
1. prepare_context(raw_data)
   ├─ Groupe les données par source
   ├─ Formate en contexte structuré
   └─ Limite à 20 items/source (évite dépassement tokens)

2. build_analysis_prompt(context)
   ├─ Intègre le prompt de veille original
   ├─ Ajoute le contexte Ackee
   └─ Spécifie les 6 axes + format attendu

3. generate_synthesis()
   ├─ Appel API Anthropic
   ├─ Température: 0.3 (cohérence)
   ├─ Max tokens: 8000 (ajustable)
   └─ Retourne synthèse structurée
```

**Prompting Strategy** :

Le prompt inclut :
- ✅ Contexte Ackee (corridors, concurrents, stade)
- ✅ Période analysée (semaine X/année)
- ✅ Données brutes structurées
- ✅ Instructions par axe avec scoring P0/P1/P2
- ✅ Format de sortie (Markdown structuré)
- ✅ Contrainte : URL source obligatoire

**Coût estimé** : $1-3 par veille (selon volume)

---

### 4. **Générateur** (`generators/report_generator.py`)

**Rôle** : Crée les livrables finaux

#### 4.1 Rapport Markdown

**Structure** :
```markdown
# ACKEE WEEKLY INTEL - Semaine XX/YYYY
[Dashboard]
[6 Axes avec infos scorées P0/P1/P2]
[Signaux faibles]
[Recommandations]
[Quick wins]
```

**Nom fichier** : `ackee_veille_sXX_YYYY.md`

#### 4.2 Email EML

**Composition** :
- **Headers** : To (13 destinataires), Subject, From, Date
- **Body** : Résumé exécutif (alertes critiques + quick wins)
- **Attachment** : Fichier Markdown complet

**Format** : RFC 2822 (compatible tous clients email)

**Nom fichier** : `ackee_veille_sXX_email.eml`

**Envoi** :
```bash
# Mac/Linux
open *.eml

# Windows
double-click sur .eml
```

---

### 5. **Scheduler** (`scheduler.py`)

**Rôle** : Automatisation de l'exécution

**Bibliothèque** : `schedule` (Python)

**Configuration** :
```python
schedule.every().monday.at("08:00").do(run_veille)
```

**Modes d'exécution** :

#### Mode 1 : Processus Python

```bash
python scheduler.py
# Tourne indéfiniment, check toutes les 60 secondes
```

#### Mode 2 : Service systemd (recommandé Linux)

```bash
sudo systemctl enable ackee-veille
sudo systemctl start ackee-veille
# Redémarre automatiquement si crash
```

#### Mode 3 : Crontab

```bash
0 8 * * 1 /path/to/venv/bin/python veille_orchestrator.py
# Exécuté par le système cron
```

**Logging** : `veille_scheduler.log`

---

## 📊 Flux de données

### Schéma complet

```
LUNDI 08:00
    │
    ▼
┌─────────────────┐
│   SCHEDULER     │ Déclenche l'orchestrateur
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ORCHESTRATOR    │ 1. Calcule période (aujourd'hui - 7 jours)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         PHASE 1: COLLECTE               │
├─────────────────────────────────────────┤
│ RSS Collector                           │ → TechCrunch, The Block, etc.
│ Web Search Collector                    │ → Serper API (Google)
│ Crunchbase Collector                    │ → Crunchbase API v4
└────────┬────────────────────────────────┘
         │
         ▼ (47 items collectés)
         │
    [Sauvegarde]
         │
    raw_data_sXX_YYYY.json
         │
         ▼
┌─────────────────────────────────────────┐
│         PHASE 2: ANALYSE                │
├─────────────────────────────────────────┤
│ LLM Analyzer                            │
│   ├─ Prépare contexte                   │
│   ├─ Build prompt (6 axes)              │
│   └─ API Call: Claude Sonnet 4.5        │ ← ANTHROPIC_API_KEY
└────────┬────────────────────────────────┘
         │
         ▼ (Synthèse structurée)
         │
┌─────────────────────────────────────────┐
│         PHASE 3: GÉNÉRATION             │
├─────────────────────────────────────────┤
│ Report Generator                        │
│   ├─ Génère Markdown                    │ → ackee_veille_sXX_YYYY.md
│   └─ Génère EML                         │ → ackee_veille_sXX_email.eml
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  DESTINATAIRES  │ Double-click .eml → Client email
└─────────────────┘
```

---

## ⚙️ Configuration

### Fichier `config/config.yaml`

**Sections** :

```yaml
ackee:           # Contexte business
sources:         # Sources de veille (RSS, APIs)
competitors:     # Concurrents à tracker
api_keys:        # Références aux env vars
schedule:        # Timing d'exécution
llm:             # Config Claude
output:          # Répertoires de sortie
recipients:      # Liste emails
```

### Fichier `.env`

**Variables sensibles** :

```bash
ANTHROPIC_API_KEY=    # REQUIS
SERPER_API_KEY=       # Recommandé
CRUNCHBASE_API_KEY=   # Optionnel
```

---

## 🔒 Sécurité

### Données sensibles

**Protégées** :
- ✅ API keys dans `.env` (ignoré par Git)
- ✅ Rapports dans `reports/` (ignorés par Git)
- ✅ Données brutes dans `data/` (ignorées par Git)

**Best practices** :
- Ne jamais commit `.env`
- Rotation régulière des API keys
- Restriction des permissions systemd service

---

## 📈 Performance

### Temps d'exécution typique

| Phase | Durée estimée |
|-------|---------------|
| Collecte RSS | 30-60 sec |
| Collecte Web Search | 60-120 sec |
| Collecte Crunchbase | 30-60 sec |
| Analyse LLM | 60-90 sec |
| Génération rapports | <10 sec |
| **TOTAL** | **3-5 min** |

### Optimisations possibles

1. **Parallélisation collecteurs** : Actuellement séquentiel, pourrait être parallèle
2. **Cache RSS** : Éviter de re-parser les feeds identiques
3. **Batch API calls** : Grouper les requêtes Serper
4. **Streaming LLM** : Afficher la synthèse en temps réel

---

## 🧪 Tests

### Script de test

```bash
python test_system.py
```

**Tests effectués** :
1. ✅ Imports des modules
2. ✅ Chargement config.yaml
3. ✅ Variables d'environnement
4. ✅ Instanciation collecteurs
5. ✅ Instanciation analyzer
6. ✅ Instanciation generator
7. ✅ Répertoires de sortie

---

## 🚀 Évolutions futures

### Court terme (Q1 2026)

- [ ] Collecteur LinkedIn (annonces de posts/jobs)
- [ ] Collecteur régulateurs (ACPR, FCA, BCEAO scraping)
- [ ] Détection de nouveaux entrants via Product Hunt API
- [ ] Alertes Slack en temps réel pour les P0

### Moyen terme (Q2-Q3 2026)

- [ ] Interface web de consultation
- [ ] Dashboard interactif (graphiques, tendances)
- [ ] Historique des veilles (BDD)
- [ ] API REST pour interroger les données
- [ ] Export PDF des rapports

### Long terme (2027)

- [ ] ML pour détection automatique de signaux faibles
- [ ] Scoring automatique de la criticité (P0/P1/P2)
- [ ] Recommandations prédictives
- [ ] Intégration CRM (tracking des actions)

---

## 📞 Support & Maintenance

### Logs à consulter

```bash
# Scheduler
tail -f veille_scheduler.log

# Systemd
sudo journalctl -u ackee-veille -f

# Cron
tail -f logs/cron.log
```

### Debugging

1. **Pas de données collectées** :
   ```bash
   cat reports/raw_data_*.json | jq length
   ```

2. **Erreur LLM** :
   ```bash
   # Tester l'API key
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -d '{"model":"claude-sonnet-4-5-20250929","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
   ```

3. **Vérifier la config** :
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"
   ```

---

**Documentation technique complète**
*Système de veille Ackee - Version 1.0*
*Dernière mise à jour: Janvier 2026*
