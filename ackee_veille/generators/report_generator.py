"""
Report Generator - Génère les rapports Markdown et fichiers EML
"""
import os
from datetime import datetime
from typing import Dict, Any, List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Générateur de rapports de veille (Markdown + EML)"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reports_dir = config.get('output', {}).get('reports_dir', 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate(self, synthesis: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère les rapports à partir de la synthèse

        Returns:
            Dict avec les chemins des fichiers générés: {'markdown': path, 'eml': path}
        """
        logger.info("Generating reports...")

        # Extrait les métadonnées
        metadata = synthesis.get('metadata', {})
        start_date = datetime.fromisoformat(metadata['period_start'])
        end_date = datetime.fromisoformat(metadata['period_end'])
        week_number = start_date.isocalendar()[1]
        year = start_date.year

        # Génère le rapport Markdown
        md_path = self._generate_markdown(synthesis, week_number, year, start_date, end_date)

        # Génère le fichier EML
        eml_path = self._generate_eml(synthesis, md_path, week_number, year, start_date, end_date)

        logger.info(f"Reports generated: {md_path}, {eml_path}")

        return {
            'markdown': md_path,
            'eml': eml_path
        }

    def _generate_markdown(self, synthesis: Dict[str, Any], week_number: int,
                          year: int, start_date: datetime, end_date: datetime) -> str:
        """Génère le rapport Markdown"""

        filename = f"ackee_veille_s{week_number:02d}_{year}.md"
        filepath = os.path.join(self.reports_dir, filename)

        synthesis_text = synthesis.get('synthesis', '')

        # Construit le contenu Markdown
        content = f"""# 📅 ACKEE WEEKLY INTEL - Semaine {week_number:02d}/{year}

**Période**: {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}
**Généré le**: {datetime.now().strftime('%d/%m/%Y à %H:%M')}

---

{synthesis_text}

---

*Rapport généré automatiquement par le système de veille Ackee*
*Modèle: {synthesis.get('metadata', {}).get('model', 'N/A')}*
*Items analysés: {synthesis.get('metadata', {}).get('total_items_analyzed', 'N/A')}*
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Markdown report saved: {filepath}")
        return filepath

    def _generate_eml(self, synthesis: Dict[str, Any], md_path: str,
                     week_number: int, year: int, start_date: datetime, end_date: datetime) -> str:
        """Génère le fichier EML prêt à envoyer"""

        filename = f"ackee_veille_s{week_number:02d}_email.eml"
        filepath = os.path.join(self.reports_dir, filename)

        # Extrait un titre principal depuis la synthèse
        main_alert = self._extract_main_alert(synthesis)

        # Récupère les destinataires
        recipients = self.config.get('recipients', [])
        to_addresses = ', '.join(recipients)

        # Crée le message email
        msg = MIMEMultipart()
        msg['Subject'] = f"ACKEE WEEKLY INTEL - Semaine {week_number:02d}/{year} ({start_date.strftime('%d/%m')} au {end_date.strftime('%d/%m')}): {main_alert}"
        msg['To'] = to_addresses
        msg['From'] = "veille@ackee.com"  # À ajuster
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

        # Corps de l'email (version texte)
        email_body = self._generate_email_body(synthesis, start_date, end_date, week_number, year)
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

        # Attache le fichier Markdown
        if os.path.exists(md_path):
            with open(md_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(md_path)}',
                )
                msg.attach(part)

        # Sauvegarde le fichier EML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(msg.as_string())

        logger.info(f"EML file saved: {filepath}")
        return filepath

    def _extract_main_alert(self, synthesis: Dict[str, Any]) -> str:
        """Extrait le titre principal de l'alerte depuis la synthèse"""
        # Par défaut, on retourne un titre générique
        # Cette fonction pourrait être améliorée pour extraire le vrai titre depuis la synthèse
        synthesis_text = synthesis.get('synthesis', '')

        # Cherche une section "ALERTES CRITIQUES"
        if '🚨' in synthesis_text or 'ALERTES CRITIQUES' in synthesis_text:
            lines = synthesis_text.split('\n')
            for i, line in enumerate(lines):
                if '🚨' in line or 'ALERTES CRITIQUES' in line:
                    # Prend la ligne suivante non vide
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('#'):
                            return lines[j].strip()[:80]  # Limite à 80 caractères

        return "Points clés de la semaine"

    def _generate_email_body(self, synthesis: Dict[str, Any], start_date: datetime,
                            end_date: datetime, week_number: int, year: int) -> str:
        """Génère le corps de l'email"""

        synthesis_text = synthesis.get('synthesis', '')

        # Extrait les sections clés pour le résumé email
        critical_alerts = self._extract_section(synthesis_text, '🚨')
        quick_wins = self._extract_section(synthesis_text, '⚡')
        recommendations = self._extract_section(synthesis_text, '💡')

        body = f"""Chers co-fondateurs,

Voici la veille concurrentielle et réglementaire de la semaine {week_number:02d}/{year} ({start_date.strftime('%d/%m')} au {end_date.strftime('%d/%m')}).

{critical_alerts if critical_alerts else "✅ Aucune alerte critique cette semaine."}

{quick_wins if quick_wins else ""}

{recommendations if recommendations else ""}

📎 DOCUMENT COMPLET

La veille exhaustive est disponible en pièce jointe : ackee_veille_s{week_number:02d}_{year}.md

Le rapport contient:
- Analyse complète des 6 axes de veille
- Signaux faibles et tendances émergentes
- Recommandations stratégiques détaillées
- Liens sources pour chaque information

---

Le prompt est opérationnel pour veilles hebdomadaires automatisées.

Disponible pour discussion.

Veille Ackee (automatisé)
"""

        return body

    def _extract_section(self, text: str, emoji: str) -> str:
        """Extrait une section spécifique du rapport basée sur l'emoji"""
        lines = text.split('\n')
        section = []
        in_section = False

        for line in lines:
            if emoji in line:
                in_section = True
                section.append(line)
                continue

            if in_section:
                # Arrête à la prochaine section (identifiée par un emoji ou un titre de niveau 2)
                if ('##' in line and line.startswith('#')) or any(e in line for e in ['🎯', '⚖️', '⚙️', '📊', '🤝', '🆕', '📡']):
                    break
                section.append(line)

        # Limite à 10 lignes pour l'email
        return '\n'.join(section[:15]) if section else ''
