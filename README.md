
# 🧠 MetaScraper

🚀 Une interface web simple pour extraire automatiquement les **métadonnées** depuis :
- 📺 **YouTube**
- 🔞 **Pornhub**
- 📷 **Instagram** (Reels & Posts)

Crée avec ❤️ par Élie, ce projet permet de scrapper des informations vidéo ou post via une interface élégante, rapide et légère.

---

## ✨ Fonctionnalités

✅ Interface web responsive (Flask + HTML)  
✅ Scraping de plusieurs plateformes populaires  
✅ Architecture modulaire (`scrapers/`)  
✅ Facile à lancer en local

---

## 📂 Arborescence du projet

```bash
MetaScraper/
│
├── app.py                 # Serveur Flask principal
├── requirements.txt       # Dépendances Python
├── templates/
│   └── index.html         # Interface utilisateur
├── scrapers/
│   ├── base.py            # Classe de base
│   ├── youtube.py         # Scraper YouTube
│   ├── pornhub.py         # Scraper Pornhub
│   └── instagram.py       # Scraper Instagram
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Installation

> 📌 Prérequis : Python 3.10+ installé sur ta machine

1. Clone le repo :
```bash
git clone https://github.com/ton-utilisateur/MetaScraper.git
cd MetaScraper
```

2. Installe les dépendances :
```bash
pip install -r requirements.txt
```

3. Lance le serveur :
```bash
python app.py
```

4. Ouvre ton navigateur :
```
http://127.0.0.1:5000
```

---

## 🧩 Technologies utilisées

- 🐍 Python + Flask
- 🕸️ BeautifulSoup / Requests
- 🖥️ HTML/CSS pour l’interface
- 🧱 Architecture modulaire pour les scrapers

---

## ⚠️ Avertissement

> Ce projet est uniquement destiné à des **usages éducatifs et personnels**.  
> Respecte les [Conditions d'utilisation](https://www.youtube.com/t/terms) des plateformes que tu analyses.

---

## 📃 Licence

Ce projet est sous licence **MIT** — libre à toi de le modifier, utiliser ou partager.

---

## 👨‍💻 Auteur

Développé par **Élie**  
📍 Millau, France | 🎓 Lycéen passionné de sciences & tech  
💬 N'hésite pas à me contacter ou contribuer au projet !

---

## ⭐️ Si tu aimes ce projet...

N'oublie pas de mettre une ⭐ sur le repo pour le soutenir 😄
