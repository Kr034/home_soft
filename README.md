# 🧠 home_soft — Automatisation personnelle & assistant IA

Une application web simple et modulaire conçue pour :
- gérer tes **scripts personnalisés**,
- convertir des documents Markdown en PDF,
- interagir avec un **assistant IA local** (type LLM) pour l’aide à la programmation et l’automatisation,
- le tout dans une interface web **responsive avec TailwindCSS**.

---

## 🚀 Fonctionnalités principales

### 🔧 Gestion des scripts
- Ajouter, modifier, exécuter ou supprimer des scripts `.sh`
- Interface intuitive avec aperçu au survol (description du script)
- Catégorisation dynamique via `categories.yaml`

### 🧠 Assistant IA (via Ollama)
- Utilise des modèles comme `codellama` ou `mistral` en local
- Pose des questions liées à la programmation, bash, Python, etc.
- Fonctionne hors ligne, **aucune donnée envoyée à des serveurs distants**

### 📄 Conversion Markdown → PDF
- Téléverser ou coller ton Markdown
- Conversion directe via Pandoc + LaTeX
- Historique et logs consultables

---

## 🧰 Stack technique

- **FastAPI** + **HTMX** pour le backend dynamique
- **Jinja2** pour le templating
- **TailwindCSS** pour le design moderne
- **Ollama** pour l’IA locale (LLM)
- **Pandoc** + `texlive-*` pour les conversions

---

## 📦 Installation

### 1. Dépendances système

```bash
# Arch Linux
sudo pacman -S pandoc texlive-core texlive-latexextra

# Ollama (pour l'IA locale)
curl -fsSL https://ollama.com/install.sh | sh
````

### 2. Cloner et installer les dépendances

```bash
git clone https://github.com/Kr034/home_soft.git
cd home_soft
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
uvicorn main:app --reload
```

L’application sera disponible sur [http://localhost:8000](http://localhost:8000)

---

## 🧠 Lancer le modèle IA local

```bash
ollama run codellama:7b-instruct
```

Tu peux aussi essayer :

```bash
ollama run mistral
ollama run phi3
```

Ensuite, l’interface `/assistant` permet de dialoguer avec le modèle local.

---

## 📁 Structure

```

```

---

## 📌 To-do

* [x] Éditeur complet de scripts
* [x] Assistant IA local
* [x] Menu dynamique
* [ ] Authentification utilisateur
* [ ] Thèmes customisables
* [ ] Auto-tagging des scripts

---

## 🛡️ Sécurité

⚠️ Le projet n’est pas sécurisé pour une exposition publique par défaut.
Si tu veux l’ouvrir en ligne :

* ajoute une authentification (FastAPI Users, OAuth, etc.)
* sécurise l’exécution des scripts (`subprocess.run` à isoler)
* sandboxe les entrées utilisateur

---

## 📜 Licence

MIT — libre pour tout usage personnel ou professionnel.

---

> Projet réalisé par [Kr034](https://github.com/Kr034) pour automatiser, apprendre et expérimenter ✨
