#!/bin/sh
# Übungskarte „Ilsetal“ 1:50 000 neu erzeugen (dauert etwa eine Minute).
# Braucht: numpy scipy matplotlib numba pyproj  (pip install numpy scipy matplotlib numba pyproj)
# Ergebnis: handwerk/karte/uebungskarte-ilsetal.pdf
set -e
cd "$(dirname "$0")"
W=$(mktemp -d)
cp gelaende.py gelaende_fein.py merkmale.py zeichnen.py "$W"
cd "$W"
python3 gelaende.py . 25 0.03            # Erosionsrechnung, 40-m-Raster
python3 gelaende_fein.py gelaende.npz fein.npz   # Talauen, 20-m-Raster, Abflussnetz
python3 merkmale.py                      # Bäche, Straßen, Bahn, Orte, Wald
python3 zeichnen.py uebungskarte-ilsetal # PDF (A4, 1:50 000) und PNG
cp uebungskarte-ilsetal.pdf "$OLDPWD/../../handwerk/karte/"
rm -rf "$W"
echo "fertig: handwerk/karte/uebungskarte-ilsetal.pdf"
