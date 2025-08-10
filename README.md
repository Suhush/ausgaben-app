
# Ausgaben-Tracker (Web-App, Streamlit)

**Funktion:** Eingabemaske wie in Access: heutiges Datum vorausgefüllt, Dropdowns für Währung/Kategorie/Zahlung, Speichern in CSV, Analyse (Tabellen + Diagramme).

## Start (Lokal auf deinem Rechner)
1. **Python 3.10+** installieren.
2. Im Terminal in den Ordner wechseln:
   ```bash
   cd ausgaben_webapp
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. Browser öffnet sich unter `http://localhost:8501`.

### iPhone wie App benutzen
- Wenn die App am selben WLAN-Rechner läuft: IP des Rechners benutzen, z. B.
  `http://192.168.1.23:8501` im iPhone-Safari öffnen.
- In Safari: Teilen → **Zum Home-Bildschirm** → Icon anlegen. Fertig.

## Dateien
- **data/expenses.csv** – deine Daten (kannst du mit Excel öffnen).
- **config/categories.yaml** – Kategorienliste (Dropdown).
- **config/fx.yaml** – Basiswährung und Wechselkurse.

## Hinweise
- Wechselkurse manuell pflegen (z. B. TRY→EUR).
- Kategorien jederzeit anpassbar, App neu laden.

Viel Spaß! 🍷
