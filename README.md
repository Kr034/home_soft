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
- Utilise des modèles comme `codellama`, `mistral`, `phi3` en local
- Pose des questions liées à la programmation, bash, Python, etc.
- Fonctionne **100% hors ligne**, aucune donnée externe n’est transmise

### 📄 Conversion Markdown → PDF
- Téléverser ou coller ton Markdown
- Conversion directe via Pandoc + LaTeX (contenus gérés par Docker)
- Historique et logs disponibles

---

## 🧰 Stack technique

- **FastAPI** + **HTMX** pour un backend interactif
- **Jinja2** pour le rendu HTML
- **TailwindCSS** pour un style moderne responsive
- **Ollama** pour l’IA locale
- **Pandoc** + LaTeX installés dans le conteneur

---

## ⚙️ Installation & Lancement

### 1. Installer Ollama

> Ollama doit tourner **sur ta machine hôte**, pas dans le conteneur Docker.

```bash
curl -fsSL https://ollama.com/install.sh | sh
````

Télécharger ensuite le modèle souhaité :

```bash
ollama pull codellama:7b-instruct
```

---

### 2. Lancer l’application

Utilise le script de gestion inclus :

```bash
./manage.sh start
```

Ce script :

* lance l’application via Docker,
* rend l’interface dispo sur [http://localhost:8000](http://localhost:8000),
* et se connecte à Ollama (sur l’hôte).

> Pour arrêter l’application :

```bash
./manage.sh stop
```
---

### 🔁 Changer de modèle Ollama

Par défaut, le script utilise **`codellama:7b-instruct`**.

Si tu veux utiliser un autre modèle (comme `mistral` ou `phi3`), édite le fichier `manage.sh` et modifie cette ligne :

```bash
MODEL="codellama:7b-instruct"
```

Par exemple, pour utiliser Mistral :

```bash
MODEL="deepseek-r1:32b"
```

Assure-toi que le modèle est bien téléchargé :

```bash
ollama pull deepseek-r1:32b
```

Puis relance l’application :

```bash
./manage.sh restart
```
---

## 📁 Structure

```
.
├── app
│   ├── categories.yaml
│   ├── converter.py
│   ├── main.py
│   ├── requirements.txt
│   └── templates/
│       ├── dashboard.html
│       └── sections/
│           ├── conversion.html
│           ├── default.html
│           ├── edit_script.html
│           ├── generation.html
│           ├── history.html
│           └── scripts.html
├── data/
│   ├── history/
│   │   └── conversations.json
│   ├── logs/
│   │   └── conversions.log
│   ├── outputs/
│   ├── pasted/
│   ├── scripts/
│   │   └── test_ollama.sh
│   └── uploads/
├── manage.sh
├── docker-compose.yml
└── Dockerfile
```

---

## ✅ TODO

* [x] Éditeur complet de scripts
* [x] Assistant IA local
* [x] Menu dynamique par `categories.yaml`
* [x] Sauvegarde des conversations
* [ ] Authentification (à venir)
* [ ] Système de thèmes
* [ ] Exécution sécurisée en sandbox

---

## 🛡️ Sécurité

⚠️ Ne pas exposer publiquement sans :

* authentification (FastAPI Users, etc.),
* restrictions sur l’exécution de scripts,
* sandboxing des entrées.

---

## 📜 Licence

MIT — usage libre personnel & pro.

---

> Fait maison par [Kr034](https://github.com/Kr034) pour automatiser, apprendre et expérimenter.

````
