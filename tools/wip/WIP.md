# Zwischenstand: BTR-60PB/BTR-70, 2S43 Malva, Blau-Trainer

Nicht eingebaut – die App auf `main` ist unverändert. Unterbrochen, weil Wikimedia die Downloads stark drosselt (HTTP 429).

## Dateien
- `wm.py` – Wikimedia-Helfer: `search`, `info` (Lizenz, Thumbnail-URL), `get` (langsamer Download mit Wartezeiten)
- `cand.txt`, `info.json` – Bildkandidaten für BTR-60PB, BTR-70 und Malva mit Lizenz (Index = Nummer in `info.json`)
- `dl/a-NN.jpg` – schon geladene Bilder (NN = Index in `info.json`), alle gemeinfrei:
  05, 08, 11, 13 = BTR-60PB; 19, 21, 23 = BTR-70
- `patch_btr.py` – fügt BTR-60PB und BTR-70 in `manoever/index.html` ein (DATA, IMG, VAR, AR, ARS, PINS, ANNO, CMP, Frage r-9)
- `patch_malva.py` – fügt die 2S43 Malva in `artillerie/index.html` ein (neue Kategorie Radhaubitze, Frage r-8, Vergleich mit 2S19)
- `blau_data.py` – Daten des Blau-Trainers: 22 Fahrzeuge KR Blau mit Gegenstück KR Rot, Merkblatt, Fragen
- `gen_blau.py` – erzeugt `blau/index.html` aus dem Manöver-Trainer als Vorlage
- `blau_search.py` – sucht die Bildkandidaten für den Blau-Trainer (Ergebnis nach `blau/<id>.json`)

## Noch offen
1. Bilder laden: BTR-70 (Index 24, 27), Malva (Index 2, 3, beide CC0). Dann zuschneiden (max. 840×630, WebP), Pins setzen, `patch_btr.py` und `patch_malva.py` ausführen.
2. In `patch_btr.py` noch ergänzen: `btr60` und `btr70` in die hart codierte `GROUPS`-Liste des Manöver-Trainers eintragen.
3. Blau-Trainer: `blau_search.py` laufen lassen, je Fahrzeug 2–3 gemeinfreie Bilder wählen, `gen_blau.py` ausführen, Kachel in der Übersicht `index.html` ergänzen, README-Tabelle ergänzen.
4. Im Browser testen, `python3 tools/build.py`, dann auf `main` bringen.
