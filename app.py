from flask import Flask, request, render_template
import importlib
import os

app = Flask(__name__)

# Charger tous les scrapers dynamiquement
scrapers = []
for file in os.listdir("scrapers"):
    if file.endswith(".py") and file not in ["base.py", "__init__.py"]:
        module_name = file[:-3]
        module = importlib.import_module(f"scrapers.{module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            try:
                if issubclass(cls, module.BaseScraper) and cls != module.BaseScraper:
                    scrapers.append(cls())
            except TypeError:
                continue

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        url = request.form["url"]
        for scraper in scrapers:
            if scraper.can_handle(url):
                result = scraper.scrape(url)
                break
        if not result:
            result = {"error": "Aucun scraper ne peut gérer cette URL."}
    
    if result:
        import json
        json_result = json.dumps(result, indent=2, ensure_ascii=False)
        # Extraire l'image si elle existe
        image_url = result.get("image") if isinstance(result, dict) else None
        return render_template("index.html", result=json_result, image_url=image_url)
    else:
        return render_template("index.html", result=None, image_url=None)

if __name__ == "__main__":
    app.run(debug=True)
