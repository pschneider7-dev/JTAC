"""Daten des Blau-Trainers: gängige Landfahrzeuge KR Blau (NATO und Partner), dazu je ein ähnliches Fahrzeug KR Rot.
red: (Trainer, Familie, Bildindex, Name, Unterschied)"""

CATS = {
    "kpz": {"label": "Kampfpanzer", "cap": "Schwer gepanzert, große Kanone im Drehturm"},
    "spz": {"label": "Schützenpanzer (Kette)", "cap": "Transportiert Infanterie, Maschinenkanone im Turm"},
    "rpz": {"label": "Radpanzer (6×6 bzw. 8×8)", "cap": "Transport- oder Schützenpanzer auf Rädern"},
    "tpzk": {"label": "Transportpanzer (Kette)", "cap": "Leicht gepanzerter Kasten auf Ketten, meist nur MG"},
    "gfz": {"label": "Geschütztes Fahrzeug bzw. Spähwagen (4×4)", "cap": "Geschützte Kabine auf Rädern, Waffenstation oder MG"},
    "art": {"label": "Rohrartillerie (Panzer- bzw. Radhaubitze)", "cap": "Selbstfahrende Haubitze, schießt indirekt aus großer Entfernung"},
    "rak": {"label": "Raketenartillerie", "cap": "Raketenwerfer mit geschlossenen Behältern für Lenkraketen"},
}
CAT_ORDER = ["kpz", "spz", "rpz", "tpzk", "gfz", "art", "rak"]
CAT_EXCL = {"spz": ["tpzk"], "tpzk": ["spz"], "rpz": ["gfz"], "gfz": ["rpz"]}

GROUPS = [
    ["Kampfpanzer", ["leo2", "m1", "leclerc", "chall"]],
    ["Schützenpanzer", ["puma", "marder", "cv90", "bradley"]],
    ["Rad- und Transportpanzer", ["boxer", "stryker", "vbci", "griffon", "fuchs", "m113"]],
    ["Geschützte Fahrzeuge", ["dingo", "fennek", "hmmwv"]],
    ["Artillerie", ["pzh2000", "m109", "caesar", "himars", "m270"]],
]

ORIGINS = ["Deutschland", "Frankreich", "USA", "Großbritannien", "Schweden", "Deutschland und Niederlande"]

F = []


def fam(**k):
    k.setdefault("vars", [{"v": None, "name": k["name"]}])
    k.setdefault("confuse", [])
    F.append(k)


fam(id="leo2", name="Leopard 2", short="LEO2", cat="kpz", origin="Deutschland",
    designation="Leopard 2 – deutscher Kampfpanzer (1979), der verbreitetste westliche Kampfpanzer in Europa. 2A4 mit senkrechter Turmfront, ab 2A5 mit keilförmiger Zusatzpanzerung, 2A6 und 2A7 mit langer L55-Kanone",
    users="Deutschland, Polen, Spanien, Norwegen, Finnland, Schweden, Dänemark, Österreich, Kanada, Griechenland, Ukraine u. a.",
    weapons=["120-mm-Glattrohrkanone (L44, ab 2A6 L55)", "2 × 7,62-mm-MG"],
    recog="Sieben Laufrollen unter Seitenschürzen, großer, kantiger Turm mit senkrechten Seiten und flachem Heck.",
    confuse=["m1", "leclerc"],
    jtac=["Laufrollen zählen: sieben haben Leopard 2 und M1, sechs haben Leclerc, Challenger 2 und alle T-Panzer.",
          "Auch die Ukraine fährt Leopard 2 – erbeutete Fahrzeuge zeigt Russland als Trophäen. Freund oder Feind immer über die Lage bestätigen."],
    vars=[{"v": "a4", "name": "Leopard 2A4", "recog": "Senkrechte, flache Turmfront ohne Keil; kürzeres Rohr (L44)."},
          {"v": "a6", "name": "Leopard 2A5/A6/A7", "recog": "Keilförmige Zusatzpanzerung an der Turmfront; 2A6 und 2A7 mit langem L55-Rohr."}],
    red=("manoever", "t90", 0, "T-90", "Leopard 2: sieben Laufrollen und hoher, kantiger Turm mit senkrechten Seiten. T-90: sechs Laufrollen und flacher Turm mit Reaktivpanzerung."))

fam(id="m1", name="M1 Abrams", short="M1", cat="kpz", origin="USA",
    designation="M1A1/M1A2 Abrams – US-Kampfpanzer (1980) mit Gasturbine; in Europa auch bei Polen und der Ukraine",
    users="USA, Polen, Ukraine, Australien und weitere Staaten",
    weapons=["120-mm-Glattrohrkanone M256", "12,7-mm-MG und 2 × 7,62-mm-MG"],
    recog="Sehr flacher, breiter und kantiger Turm mit Staukorb am Heck, sieben Laufrollen unter Seitenschürzen.",
    confuse=["leo2"],
    jtac=["Gasturbine: sehr heißes Heck im Wärmebild – wie beim russischen T-80.",
          "Flacher als der Leopard 2: Turmseiten schräg, Turm wirkt wie eine flache Platte."],
    red=("manoever", "t80", 0, "T-80", "M1: sieben Laufrollen und sehr flacher, kantiger Turm. T-80: sechs Laufrollen und runder Turm mit Reaktivpanzerung. Beide haben eine Gasturbine – im Wärmebild beide mit heißem Heck."))

fam(id="leclerc", name="Leclerc", short="LEC", cat="kpz", origin="Frankreich",
    designation="Leclerc – französischer Kampfpanzer (1992) mit Ladeautomat, modernisiert als Leclerc XLR",
    users="Frankreich, Vereinigte Arabische Emirate, Jordanien",
    weapons=["120-mm-Glattrohrkanone mit Ladeautomat", "12,7-mm-MG koaxial, 7,62-mm-MG"],
    recog="Sechs Laufrollen, kastenförmiger Turm mit flacher Front und langem Heck (Ladeautomat), Optiken oben auf dem Turm.",
    confuse=["leo2", "chall"],
    jtac=["Sechs Laufrollen wie die T-Panzer – hier entscheidet der hohe, kastige Turm.",
          "Im Lehrgang in Frankreich der Kampfpanzer, den du am ehesten siehst."],
    red=("manoever", "t72", 0, "T-72", "Beide haben sechs Laufrollen. Leclerc: hoher, kastiger Turm mit langem Heck. T-72: flacher, runder Gussturm."))

fam(id="chall", name="Challenger 2", short="CR2", cat="kpz", origin="Großbritannien",
    designation="Challenger 2 – britischer Kampfpanzer (1998) mit gezogener Kanone; Nachfolger Challenger 3",
    users="Vereinigtes Königreich, Oman, Ukraine",
    weapons=["120-mm-Zugrohrkanone L30", "2 × 7,62-mm-MG"],
    recog="Sechs Laufrollen, hoher, kantiger Turm mit senkrechten Seiten, oft mit Zusatzpanzerung und Gitterschutz am Heck.",
    confuse=["leo2", "leclerc"],
    jtac=["Sechs Laufrollen – nicht allein darauf verlassen, der Turm ist kantig und hoch."],
    red=("manoever", "t72", 0, "T-72", "Beide haben sechs Laufrollen. Challenger 2: hoher, kantiger Turm. T-72: niedriger, runder Turm."))

fam(id="puma", name="Puma", short="PUMA", cat="spz", origin="Deutschland",
    designation="Puma – Schützenpanzer der Bundeswehr (ab 2015) mit unbemanntem Turm, Nachfolger des Marder",
    users="Deutschland",
    weapons=["30-mm-Maschinenkanone MK30-2 im unbemannten Turm", "Panzerabwehr-Lenkflugkörper MELLS (Spike LR)", "5,56-mm-MG"],
    recog="Sehr kantige, flache Wanne mit breiten Schürzen, kleiner, flacher unbemannter Turm.",
    confuse=["marder", "cv90"],
    jtac=["Der Turm ist unbemannt und flach – das Fahrzeug wirkt wie ein Kasten mit kleinem Aufsatz."],
    red=("manoever", "bmp3", 0, "BMP-3", "Puma: hohe, kantige Wanne mit kleinem, flachem Turm. BMP-3: flache Wanne mit großem Turm und dicker 100-mm-Kanone."))

fam(id="marder", name="Marder 1", short="MAR", cat="spz", origin="Deutschland",
    designation="Marder 1A3/1A5 – Schützenpanzer der Bundeswehr (1971), wird vom Puma abgelöst; auch in der Ukraine im Einsatz",
    users="Deutschland, Ukraine, Griechenland, Chile, Jordanien",
    weapons=["20-mm-Maschinenkanone", "Panzerabwehr-Lenkflugkörper MILAN (teils)", "7,62-mm-MG"],
    recog="Hohe, kastenförmige Wanne mit steiler Front, kleiner Turm mit 20-mm-Kanone, sechs Laufrollen.",
    confuse=["puma", "bradley"],
    jtac=["In der Ukraine kämpfen Marder neben sowjetischen BMP – Typ und Seite immer getrennt prüfen."],
    red=("manoever", "bmp2", 0, "BMP-2", "Marder: hohe, kastige Wanne mit steiler Front. BMP-2: niedrige, keilförmige Wanne mit spitzer Bugplatte."))

fam(id="cv90", name="CV90", short="CV90", cat="spz", origin="Schweden",
    designation="CV90 – schwedischer Schützenpanzer (1993), in Europa weit verbreitet; Kaliber je nach Land 30, 35 oder 40 mm",
    users="Schweden, Norwegen, Finnland, Dänemark, Niederlande, Estland, Schweiz, Tschechien, Slowakei, Ukraine",
    weapons=["30-, 35- oder 40-mm-Maschinenkanone (je nach Nation)", "7,62-mm-MG"],
    recog="Kantige Wanne mit flacher Front, Turm mittig mit langer Kanone, sieben Laufrollen, Hecktür für die Infanterie.",
    confuse=["puma", "bradley"],
    jtac=["Sieben Laufrollen – russische Schützenpanzer BMP-1/2/3 haben sechs."],
    red=("manoever", "bmp2", 0, "BMP-2", "CV90: sieben Laufrollen und kantige, hohe Wanne. BMP-2: sechs Laufrollen und niedrige, spitze Wanne."))

fam(id="bradley", name="M2 Bradley", short="M2", cat="spz", origin="USA",
    designation="M2/M3 Bradley – US-Schützenpanzer (1981), M3 als Aufklärungsversion; in der Ukraine im Einsatz",
    users="USA, Ukraine, Kroatien und weitere Staaten",
    weapons=["25-mm-Maschinenkanone M242 Bushmaster", "TOW-Panzerabwehr-Lenkflugkörper im Doppelstarter am Turm", "7,62-mm-MG"],
    recog="Hohe Wanne mit senkrechten Seiten, Turm mit kastenförmigem TOW-Starter an der linken Seite, sechs Laufrollen.",
    confuse=["marder", "cv90"],
    jtac=["Der TOW-Kasten an der Turmseite ist das sicherste Merkmal."],
    red=("manoever", "bmp2", 0, "BMP-2", "Bradley: hoch und kastig, TOW-Kasten an der Turmseite. BMP-2: niedrige Wanne, Lenkflugkörper oben auf dem Turm."))

fam(id="boxer", name="Boxer", short="BOX", cat="rpz", origin="Deutschland und Niederlande",
    designation="Boxer – Radpanzer 8×8 (ab 2011) mit tauschbaren Missionsmodulen: Transport, Sanität, Führung oder Schützenpanzer mit Turm",
    users="Deutschland, Niederlande, Vereinigtes Königreich, Litauen, Australien",
    weapons=["Je nach Version 12,7-mm-MG, 40-mm-Granatmaschinenwaffe oder 30-mm-Turm"],
    recog="Sehr hoher, kantiger Aufbau auf acht großen Rädern, flache, steile Front, Heckrampe.",
    confuse=["stryker", "vbci"],
    jtac=["Viel höher als ein BTR – auch auf Drohnenbildern wirkt der Boxer wie ein großer Kasten."],
    red=("manoever", "btr", 0, "BTR-82A", "Boxer: sehr hoch und kastig, Heckrampe. BTR-82A: niedrig und bootsförmig, Seitentür zwischen 2. und 3. Achse, Turm vorn."))

fam(id="stryker", name="Stryker", short="STRY", cat="rpz", origin="USA",
    designation="Stryker – US-Radpanzer 8×8 (2002) in vielen Versionen; das in Deutschland stationierte 2. Kavallerieregiment fährt ihn auch mit 30-mm-Turm",
    users="USA, Ukraine, Bulgarien",
    weapons=["12,7-mm-MG oder 40-mm-Granatmaschinenwaffe in der fernbedienten Waffenstation", "Version Dragoon: 30-mm-Maschinenkanone"],
    recog="Kantiger, flacher Kasten auf acht Rädern, fernbediente Waffenstation statt Turm, oft mit Gitterpanzerung.",
    confuse=["boxer", "vbci"],
    jtac=["Ohne Turm mit Waffenstation – der BTR hat immer einen Turm vorn."],
    red=("manoever", "btr", 0, "BTR-82A", "Stryker: kantiger Kasten mit Waffenstation statt Turm. BTR-82A: bootsförmige Wanne mit Turm vorn."))

fam(id="vbci", name="VBCI", short="VBCI", cat="rpz", origin="Frankreich",
    designation="VBCI – französischer Schützenpanzer 8×8 (2008) mit 25-mm-Turm",
    users="Frankreich, Katar",
    weapons=["25-mm-Maschinenkanone im Turm", "7,62-mm-MG"],
    recog="Hoher, kantiger Aufbau auf acht Rädern, kleiner Turm mit 25-mm-Kanone, Heckrampe.",
    confuse=["boxer", "griffon"],
    jtac=["Hat einen Turm wie der BTR, ist aber viel höher und kantiger."],
    red=("manoever", "btr", 0, "BTR-82A", "VBCI: hoch und kantig, Heckrampe. BTR-82A: niedrig, bootsförmig, Seitentür zwischen den Achsen."))

fam(id="griffon", name="VBMR Griffon", short="GRIF", cat="rpz", origin="Frankreich",
    designation="VBMR Griffon – französischer Radpanzer 6×6 (2019), Nachfolger des VAB",
    users="Frankreich, Belgien",
    weapons=["Fernbediente Waffenstation mit 12,7-mm-MG oder 40-mm-Granatmaschinenwaffe"],
    recog="Hoher, kantiger Aufbau auf sechs Rädern, große Panzerkabine mit Frontscheiben, Waffenstation auf dem Dach.",
    confuse=["vbci", "fuchs"],
    jtac=["Sechs Räder: Griffon und Fuchs. Russische Radschützenpanzer haben acht."],
    red=("manoever", "btr", 0, "BTR-82A", "Griffon: sechs Räder und hoher Kasten mit Waffenstation. BTR-82A: acht Räder, niedrig, mit Turm."))

fam(id="fuchs", name="Fuchs", short="FUX", cat="rpz", origin="Deutschland",
    designation="TPz 1 Fuchs – Transportpanzer 6×6 der Bundeswehr (1979), auch als ABC-Spürpanzer",
    users="Deutschland, Niederlande, Saudi-Arabien, Algerien u. a.",
    weapons=["7,62-mm- bzw. 12,7-mm-MG"],
    recog="Bootsförmige Wanne auf sechs Rädern, steile Front mit großen Scheiben, große Hecktüren.",
    confuse=["griffon"],
    jtac=["Sechs Räder und kein Turm – der BTR hat acht Räder und einen Turm."],
    red=("manoever", "btr", 7, "BTR-80", "Fuchs: sechs Räder, kein Turm. BTR-80: acht Räder und Kegelturm."))

fam(id="m113", name="M113", short="M113", cat="tpzk", origin="USA",
    designation="M113 – Transportpanzer auf Ketten (1960), der häufigste Transportpanzer der Welt; die Ukraine erhielt Hunderte",
    users="Sehr viele Staaten, u. a. USA, Ukraine, Litauen, Spanien, Italien, Australien",
    weapons=["12,7-mm-MG M2"],
    recog="Hoher, glatter Aluminiumkasten mit schräger Front, fünf Laufrollen, Heckrampe.",
    jtac=["Fünf Laufrollen und hoher Kasten – der russische MT-LB ist sehr flach und hat sechs."],
    red=("manoever", "mtlb", 0, "MT-LB", "M113: hoher Kasten mit fünf Laufrollen. MT-LB: sehr flache Wanne mit sechs Laufrollen ohne Stützrollen."))

fam(id="dingo", name="Dingo 2", short="DIN", cat="gfz", origin="Deutschland",
    designation="ATF Dingo 2 – geschütztes Fahrzeug 4×4 der Bundeswehr mit Minenschutz",
    users="Deutschland, Belgien, Österreich, Luxemburg, Tschechien, Norwegen u. a.",
    weapons=["Fernbediente Waffenstation mit 12,7-mm-MG oder 40-mm-Granatmaschinenwaffe"],
    recog="Hohes 4×4-Fahrzeug mit großen Reifen, gepanzerte Kabine mit kleinen Scheiben, Waffenstation auf dem Dach.",
    confuse=["hmmwv", "fennek"],
    jtac=["Geschützte 4×4 sehen sich ähnlich – auf Markierungen und Lage achten."],
    red=("manoever", "typhoon", 0, "Typhoon", "Dingo: kompaktes 4×4 mit Kabine bis nach vorn. Typhoon: größer, mit Lkw-Front und Motorhaube."))

fam(id="fennek", name="Fennek", short="FEN", cat="gfz", origin="Deutschland und Niederlande",
    designation="Fennek – Spähwagen 4×4 (2003) mit ausfahrbarem Sensormast, sehr flach und leise",
    users="Deutschland, Niederlande",
    weapons=["12,7-mm-MG bzw. 40-mm-Granatmaschinenwaffe"],
    recog="Sehr flaches, keilförmiges 4×4-Fahrzeug, Sensorkopf auf ausfahrbarem Mast.",
    confuse=["dingo"],
    jtac=["Späher stehen weit vorn – oft vor der eigenen Front in der Nähe des Gegners."],
    red=("manoever", "brdm2", 0, "BRDM-2", "Fennek: flach und kantig, ohne Turm. BRDM-2: spitzer Bootsbug und Kegelturm."))

fam(id="hmmwv", name="HMMWV / JLTV", short="HMV", cat="gfz", origin="USA",
    designation="HMMWV (Humvee, 1985) und Nachfolger JLTV (2019) – leichte geländegängige Fahrzeuge 4×4 der US-Streitkräfte",
    users="USA und sehr viele weitere Staaten, auch die Ukraine",
    weapons=["12,7-mm-MG, 40-mm-Granatmaschinenwaffe oder TOW auf dem Dach"],
    recog="Breites 4×4-Fahrzeug mit großen Reifen, flache Motorhaube, Waffe auf dem Dach.",
    confuse=["dingo"],
    jtac=["Der HMMWV ist sehr breit und flach, der JLTV höher mit steiler Front."],
    vars=[{"v": "hmmwv", "name": "HMMWV", "recog": "Sehr breit und flach, kantige Motorhaube, kleine Scheiben."},
          {"v": "jltv", "name": "JLTV", "recog": "Höher als der HMMWV, steile Front, keilförmiger Unterboden."}],
    red=("manoever", "tigr", 0, "Tigr", "HMMWV: sehr breit und flach. Tigr: höher und schmaler, mit Lkw-artigem Kühlergrill."))

fam(id="pzh2000", name="Panzerhaubitze 2000", short="PzH", cat="art", origin="Deutschland",
    designation="Panzerhaubitze 2000 – 155-mm-Panzerhaubitze (1998), Reichweite ca. 30–40 km; auch in der Ukraine im Einsatz",
    users="Deutschland, Niederlande, Italien, Griechenland, Litauen, Ungarn, Kroatien, Katar, Ukraine",
    weapons=["155-mm-Haubitze L52 (ca. 30 km, mit Reichweitenmunition ca. 40 km)", "7,62-mm-MG"],
    recog="Großer, kantiger Turm weit hinten, sehr langes Rohr mit Mündungsbremse, sieben Laufrollen.",
    confuse=["m109"],
    jtac=["Steht weit hinter der Front – mit Reichweitenmunition 40 km und mehr."],
    red=("artillerie", "2s19", 0, "2S19 Msta-S", "PzH 2000: Turm weit hinten, sieben Laufrollen. 2S19: Turm mittig auf dem Kampfpanzer-Laufwerk mit sechs Laufrollen."))

fam(id="m109", name="M109", short="M109", cat="art", origin="USA",
    designation="M109 – US-Panzerhaubitze 155 mm (1963), aktuell M109A6 Paladin und M109A7",
    users="USA, Ukraine, Lettland, Norwegen, Schweiz und weitere Staaten",
    weapons=["155-mm-Haubitze (ca. 22–30 km)", "12,7-mm-MG"],
    recog="Großer Kastenturm über der hinteren Wannenhälfte, Rohr mit Mündungsbremse, sieben Laufrollen.",
    confuse=["pzh2000"],
    jtac=["Kürzeres Rohr als die PzH 2000 – Reichweite etwas geringer."],
    red=("artillerie", "2s3", 0, "2S3 Akatsiya", "M109: sieben Laufrollen und flacher Kastenturm. 2S3: sechs Laufrollen, Turm mit gerundeten Kanten."))

fam(id="caesar", name="CAESAR", short="CAE", cat="art", origin="Frankreich",
    designation="CAESAR – französische 155-mm-Radhaubitze (2008) auf 6×6-Lkw, als CAESAR 8×8 auf Tatra-Fahrgestell; auch in der Ukraine",
    users="Frankreich, Belgien, Dänemark, Tschechien, Litauen, Estland, Ukraine, Saudi-Arabien, Indonesien",
    weapons=["155-mm-Haubitze L52, ca. 40 km"],
    recog="Lkw mit Panzerkabine vorn, Geschütz offen auf der Ladefläche; in Stellung mit Erdsporn hinten abgestützt.",
    jtac=["Schießt und fährt sofort weiter – nach wenigen Minuten nicht mehr in der Stellung."],
    red=("artillerie", "2s43", 0, "2S43 Malva", "Beide tragen das Geschütz offen auf einem Lkw. CAESAR: meist sechs Räder, französisch. Malva: acht Räder, russisch – im Zweifel Lage und Kennung prüfen."))

fam(id="himars", name="M142 HIMARS", short="HIM", cat="rak", origin="USA",
    designation="M142 HIMARS – Raketenwerfer auf 6×6-Lkw (2005) mit einem Behälter: 6 Lenkraketen GMLRS (ca. 70–80 km) oder 1 ATACMS",
    users="USA, Ukraine, Polen, Estland, Lettland, Litauen, Rumänien, Australien u. a.",
    weapons=["6 Lenkraketen GMLRS (ca. 70–80 km) oder 1 ATACMS (bis ca. 300 km)"],
    recog="Sechs-Rad-Lkw mit Panzerkabine, ein geschlossener Kasten (Behälter) auf dem Heck statt offener Rohre.",
    confuse=["m270"],
    jtac=["Ein geschlossener Behälter: HIMARS. Offene Rohre: russischer Raketenwerfer."],
    red=("artillerie", "bm21", 0, "BM-21 Grad", "HIMARS: ein geschlossener Behälter auf sechs Rädern. BM-21 Grad: 40 offene Rohre auf dem Ural-Lkw."))

fam(id="m270", name="M270 / MARS II", short="MARS", cat="rak", origin="USA",
    designation="M270 MLRS (Deutschland: MARS II, Frankreich: LRU) – Raketenwerfer auf Ketten mit zwei Behältern für je 6 Lenkraketen",
    users="USA, Vereinigtes Königreich, Deutschland, Frankreich, Italien, Norwegen, Finnland, Ukraine",
    weapons=["12 Lenkraketen GMLRS in zwei Behältern (ca. 70–80 km)"],
    recog="Kettenfahrzeug mit Kabine vorn und großem Startkasten mit zwei Behältern auf dem Heck.",
    confuse=["himars"],
    jtac=["Ketten und zwei Behälter: M270. Räder und ein Behälter: HIMARS."],
    red=("artillerie", "bm27", 0, "BM-27 Uragan", "M270: Ketten und geschlossene Behälter. Uragan: acht Räder und 16 offene Rohre."))

MERK = [
    ["Freund oder Feind", [
        "Fahrzeugtyp allein reicht nicht: Die Ukraine fährt sowjetische und westliche Fahrzeuge, Russland zeigt erbeutete westliche Fahrzeuge.",
        "Immer abgleichen: eigene Lage und Frontverlauf, Meldungen der Bodentruppe, Blue Force Tracking, Funk.",
        "Kennzeichnung bei Tag: Markierungstafeln VS-17 (orange bzw. pink), taktische Zeichen; nachts: IR-Marker und -Leuchten, Wärmebild-Kennungstafeln.",
        "Im Zweifel nicht freigeben – erst bestätigen lassen.",
    ]],
    ["Laufrollen zählen", [
        "Kampfpanzer: sieben Laufrollen = Leopard 2 oder M1. Sechs = Leclerc, Challenger 2 und alle T-Panzer.",
        "Schützenpanzer: CV90 hat sieben, Marder und Bradley haben sechs – wie BMP-1/2/3.",
        "M113: fünf Laufrollen. MT-LB: sechs, sehr flach.",
        "Panzerhaubitzen: PzH 2000 und M109 haben sieben, 2S19 und 2S3 sechs.",
    ]],
    ["Räder zählen", [
        "Sechs Räder: Fuchs, Griffon, HIMARS, CAESAR (6×6).",
        "Acht Räder: Boxer, Stryker, VBCI – und auf Seite Rot BTR-60/70/80/82A und Malva.",
        "Westliche Radpanzer sind hoch und kastig, BTR niedrig und bootsförmig mit Turm vorn.",
    ]],
    ["Raketenwerfer", [
        "Geschlossene Behälter (HIMARS, M270/MARS II): KR Blau. Offene Rohrbündel (Grad, Uragan, Smerch/Tornado): KR Rot.",
    ]],
]

CURATED = [
    ["f-1", "gen", "Du siehst einen T-72 im Raum der Ukraine. Ist das sicher Feind?",
     ["Nein – beide Seiten fahren T-72; Freund oder Feind nur über Lage, Kennzeichnung und Meldungen bestätigen",
      "Ja – T-72 fährt nur Russland", "Ja, wenn er sich bewegt", "Nein – T-72 fährt nur die Ukraine"],
     "Sowjetische Fahrzeuge wie T-72, BMP und BTR stehen auf beiden Seiten. Der Typ sagt nichts über die Seite – Lage, Frontverlauf, Kennzeichnung und Meldungen der Bodentruppe entscheiden."],
    ["f-2", "gen", "Womit kennzeichnen sich eigene Fahrzeuge bei Tag gegenüber Lfz?",
     ["Mit Markierungstafeln wie VS-17 (orange bzw. pink) und vereinbarten Zeichen", "Mit eingeschaltetem Licht", "Mit Nebel", "Gar nicht – Lfz erkennen Fahrzeuge am Typ"],
     "Markierungstafeln (z. B. VS-17) und vereinbarte Zeichen helfen der Besatzung bei Tag. Nachts gelten IR-Marker und Wärmebild-Kennungstafeln. Was gilt, steht im Befehl bzw. in den SPINS."],
    ["f-3", "gen", "Ein Kampfpanzer hat sieben Laufrollen. Was kommt in Frage?",
     ["Leopard 2 oder M1 Abrams", "T-72 oder T-90", "Leclerc oder Challenger 2", "T-80"],
     "Sieben Laufrollen haben Leopard 2 und M1. Leclerc, Challenger 2 und alle T-Panzer haben sechs."],
    ["f-4", "gen", "Ein Raketenwerfer trägt einen geschlossenen Kasten statt offener Rohre. Was ist das am ehesten?",
     ["HIMARS bzw. M270/MARS II – KR Blau", "BM-21 Grad – KR Rot", "TOS-1A", "BM-27 Uragan"],
     "Westliche Raketenwerfer laden Lenkraketen in geschlossenen Behältern. Russische Werfer wie Grad, Uragan und Smerch tragen offene Rohrbündel."],
    ["f-5", "gen", "Ein Kampfpanzer zeigt im Wärmebild ein auffällig heißes Heck. Was kann das sein?",
     ["M1 Abrams oder T-80 – beide mit Gasturbine", "Nur Leopard 2", "Nur T-72", "Ein Panzer mit Motorschaden"],
     "M1 Abrams und T-80 haben eine Gasturbine mit sehr heißem Abgas. Die Wärmesignatur hilft beim Typ, nicht bei der Seite."],
    ["r-1", "gen", "Ein Radpanzer mit sechs Rädern und ohne Turm. Was ist das am ehesten?",
     ["Ein westlicher Radpanzer wie Fuchs oder Griffon", "BTR-82A", "BTR-80", "BRDM-2"],
     "Russische Radschützenpanzer (BTR-60 bis BTR-82A) haben acht Räder und einen Turm vorn. Sechs Räder ohne Turm: Fuchs oder Griffon."],
]
