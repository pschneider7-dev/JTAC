# Drohnenblick-Bilder aus den 3D-Modellen

Erzeugt die Bilder `manoever/img/uav-*.webp` und die Liste `UAV` im Manöver-Trainer.

1. Arbeitskopie anlegen: `manoever/3d/*.html` nach `<site>/manoever/3d/` kopieren und vor dem letzten `  return {` in `init3D` den Inhalt von `hook.js` einfügen; `assets/` nach `<site>/assets/` kopieren.
2. `python3 -m http.server 8790 --directory <site>`
3. `node gen.js cfg.json raw` – rendert jede Aufnahme (Seite, Version, Azimut, Elevation, Abstand, Boden, Tag/Wärmebild) und schreibt `raw/shots.json` mit den projizierten Merkmals-Ankern.
4. `python3 post.py final` – Sensor-Look (Rauschen, Unschärfe, Vignette, Wärmebild in Graustufen), wählt bis zu drei sichtbare Merkmale je Bild und schreibt `final/uav.json`.

Die Markierungen kommen direkt aus den Merkmals-Ankern der 3D-Modelle, verdeckte Anker werden per Strahltest ausgelassen.
