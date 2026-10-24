# JTAC-Trainer

Web-App (PWA) mit sieben Trainern für CAS aus JTAC-Sicht. Installierbar auf dem Home-Bildschirm, läuft nach dem ersten Aufruf vollständig offline.

| Ordner | Trainer |
|---|---|
| `manoever/` | Manöver-Trainer |
| `artillerie/` | Artillerie-Trainer |
| `flugabwehr/` | Flugabwehr-Trainer |
| `waffen/` | Waffen-Trainer |
| `pods/` | Pod-Trainer |
| `drill/` | JTAC-Drill |
| `brevity/` | Brevity-Trainer |

## Aufbau

- `index.html` – Übersicht mit Fortschritt je Trainer, Installieren, Fortschritt sichern und laden
- `<trainer>/index.html` – der jeweilige Trainer: Daten, Fragen und Code in einer Datei
- `<trainer>/img/` – Bilder des Trainers, z. B. `t72-3.webp` = viertes Bild der Familie `t72` (Zählung ab 0)
- `assets/app.css`, `assets/app.js` – gemeinsame Basis: Schriften, Grundstil, Service Worker anmelden
- `assets/fonts/` – Barlow, Barlow Condensed, JetBrains Mono (lokal, SIL Open Font License)
- `sw.js` – Service Worker für die Offline-Nutzung
- `manifest.webmanifest`, `icons/` – App-Name und Icons
- `tools/build.py` – baut die Website nach `_site/` und trägt die Offline-Liste in `sw.js` ein

Der Fortschritt liegt im `localStorage` des Geräts, je Trainer unter einem eigenen Schlüssel (`manoevertrainer.v1`, `jtacdrill.v1` usw.).

## Lokal testen

```sh
python3 tools/build.py
python3 -m http.server -d _site 8000
```

Dann <http://localhost:8000/> öffnen.

## Veröffentlichen

Jeder Push auf `main` baut die Website und veröffentlicht sie über GitHub Pages (`.github/workflows/pages.yml`). Einmalig in den Repo-Einstellungen unter *Settings → Pages → Source* „GitHub Actions“ wählen.

## Updates

Beim Build bekommt jede Datei eine Prüfsumme. Der Service Worker lädt beim nächsten Start nur Dateien neu, deren Inhalt sich geändert hat. Seiten kommen aus dem Netz, wenn es innerhalb von drei Sekunden antwortet, sonst aus dem Speicher.
