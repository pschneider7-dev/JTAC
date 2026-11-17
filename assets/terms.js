/* Hintergrund für alle Trainer: Fachbegriffe, die in Frage, Antwort oder Steckbrief vorkommen, werden unter
   „Hintergrund“ erklärt – nach jeder Antwort (im Feedback-Kasten .fb) und am Ende jedes Steckbriefs (#sheet).
   Geschrieben für Einsteiger ohne Vorwissen aus Luftraumüberwachung, Artillerie oder Flugabwehr.
   Der Brevity-Trainer hat eine eigene, ausführlichere Liste. */
(() => {
  const T = [
    /* ---- Luftlage, Führung, Verfahren ---- */
    ['Track (Spur)', /\btracks?\b|tracknummer|luftlagespur/i, 'Ein Track ist der Eintrag eines Objekts im Lagebild – keine Spur in der Luft. Das Radar liefert bei jeder Umdrehung nur einen Echopunkt; der Rechner fasst die Punkte zu einem Track mit Position, Kurs, Geschwindigkeit, Höhe und Identität zusammen. In der Luftwaffe heißt das „Spur“ (Luftlagespur).'],
    ['Luftlagebild', /lagebild/i, 'Gesamtbild aller Tracks in einem Raum aus Radar, Datenlink und Meldungen. Führungsstellen wie AWACS oder CRC erstellen und verteilen es.'],
    ['C2, AWACS, CRC', /awacs|\bcrc\b|\bc2\b|führungsstelle|\basoc\b|\bdasc\b/i, 'C2 (Command and Control) sind die Führungsstellen im Luftraum: AWACS (fliegendes Radar mit Leitstelle), CRC (Radarleitstelle am Boden), für CAS zusätzlich ASOC bzw. DASC. Sie führen die Lfz, teilen Aufträge zu und verteilen das Lagebild.'],
    ['Datenlink (Link 16)', /datenlink|data ?link|link[- ]?16/i, 'Digitale Funkverbindung, über die Lfz, Schiffe und Führungsstellen automatisch Tracks, Positionen und Aufträge austauschen. Link 16 ist der NATO-Standard – jeder Teilnehmer sieht dasselbe Lagebild auf seinem Display.'],
    ['IFF (Freund-Feind-Kennung)', /\biff\b|transponder|mode ?[45]\b/i, 'Ein Abfragegerät sendet, der Transponder im Lfz antwortet mit einem Code. Mode 1 bis 3 sind einfache Codes, Mode 4 und 5 verschlüsselt und militärisch. Keine Antwort heißt nicht automatisch Feind, aber der Nachweis „Freund“ fehlt.'],
    ['ATO, SPINS, ACO', /\bato\b|\bspins\b|\baco\b|luftraumordnung/i, 'ATO = täglicher Einsatzbefehl für alle Lfz (wer fliegt wann wohin mit welchem Auftrag). SPINS = besondere Anweisungen dazu, z. B. Funk, Codes, Identifizierung. ACO = Luftraumordnung mit Korridoren, Sperrräumen und Höhenbändern.'],
    ['ROE', /\broe\b|einsatzregeln/i, 'Rules of Engagement: Regeln, wann und wie Waffengewalt angewendet werden darf.'],
    ['PID', /\bpid\b|positive identif|positiv identifiz/i, 'Positive Identifizierung: hinreichende Gewissheit, dass ein Objekt ein legitimes militärisches Ziel ist – Voraussetzung für jeden Waffeneinsatz.'],
    ['CAS, JTAC, FAC(A)', /\bcas\b|\bjtac\b|fac\(a\)|luftnahunterstützung/i, 'CAS = Luftnahunterstützung für Bodentruppen nahe am Feind. JTAC = Fliegerleitoffizier am Boden, der die Angriffe steuert und freigibt. FAC(A) = Fliegerleiter in der Luft mit denselben Befugnissen.'],
    ['Type 1, 2 und 3', /type[- ]?[123]\b/i, 'Steuerungsarten im CAS: Type 1 = du siehst Lfz und Ziel und gibst jeden Angriff frei. Type 2 = du siehst Lfz oder Ziel nicht, gibst aber jeden Angriff frei. Type 3 = du gibst Raum, Zeit und Ziele frei, die Lfz greifen darin selbstständig an.'],
    ['GFC (Bodenführer)', /\bgfc\b|bodenführer/i, 'Ground Force Commander: der Führer der Bodentruppe, für die du arbeitest. Er entscheidet über Ziele, Prioritäten und das Risiko für die eigenen Leute; du berätst ihn zum Waffeneinsatz.'],
    ['Talk-on', /talk-on|bezugspunkt/i, 'Du führst den Piloten mit Worten vom Groben ins Feine zum Ziel – über markante Bezugspunkte wie Straßenkreuzung, Waldrand oder auffälliges Gebäude.'],
    ['IP, CP, Holding', /\bip\b|\bcp\b|kontaktpunkt|anfangspunkt|holding|warteraum/i, 'IP (Initial Point) = Ausgangspunkt für den Zielanflug. CP (Contact Point) = Punkt, an dem das Lfz Verbindung mit dir aufnimmt. Holding = Warteraum, in dem das Lfz kreist, bis es gebraucht wird.'],
    ['Staffelung (Deconfliction)', /staffelung|deconflict/i, 'Trennung von Lfz untereinander und von eigenem Feuer – nach Höhe, Raum oder Zeit. Für dich zentral: Lfz dürfen nicht durch die Flugbahn von Artillerie oder Mörsern fliegen.'],
    ['BDA', /\bbda\b|wirkungsaufklärung|battle damage/i, 'Battle Damage Assessment: Feststellen, was der Angriff bewirkt hat – zerstört, beschädigt oder ohne Wirkung. Gehört in die Meldung nach dem Angriff.'],
    ['CDE (Kollateralschaden)', /\bcde\b|kollateral/i, 'Collateral Damage Estimation: Abschätzung, welchen Schaden an Zivilpersonen und zivilen Objekten ein Waffeneinsatz verursachen kann. Sie bestimmt Wirkmittel, Angriffsrichtung und Zünderwahl.'],
    ['HVT und HPT', /\bhvt\b|\bhpt\b|high[- ]value|high[- ]payoff/i, 'HVT = Ziel, das für den Gegner wichtig ist. HPT = Ziel, dessen Ausschaltung dem eigenen Auftrag besonders viel bringt. Priorisiert wird nach HPT.'],
    ['Koordinaten und TLE', /\bmgrs\b|koordinate|lat\/long|\btle\b|zielortungsfehler/i, 'Koordinaten gibt es als MGRS (Gitter wie auf der Militärkarte) oder als Länge/Breite (Lat/Long); Format und Kartenbezug (WGS 84) müssen bei dir und beim Lfz übereinstimmen. TLE (Target Location Error) sagt, wie genau eine Zielkoordinate ist – für GPS-Waffen muss sie sehr genau sein, inklusive Zielhöhe.'],
    ['KR Rot und KR Blau', /\bkr\b|kräfte rot|kräfte blau/i, 'KR = Kräfte. KR Blau sind eigene bzw. verbündete Kräfte, KR Rot gegnerische Kräfte.'],
    /* ---- Maße ---- */
    ['NM (Seemeile)', /\bnm\b|seemeile/i, 'Nautische Meile = 1852 m, Standardmaß für Entfernungen in der Luftfahrt; 10 NM sind gut 18 km.'],
    ['Knoten (kn)', /\bkn\b|knoten/i, 'Seemeilen pro Stunde: 100 kn sind rund 185 km/h, 450 kn rund 830 km/h.'],
    ['Höhe in Fuß (ft)', /\bft\b|\bfuß\b/i, '1 ft = 0,305 m; 1000 ft ≈ 300 m, 10 000 ft ≈ 3 km. Die Luftfahrt gibt Höhen fast immer in Fuß an.'],
    ['MSL und AGL', /\bmsl\b|\bagl\b|über nn|über grund/i, 'MSL = Höhe über dem Meeresspiegel, AGL = Höhe über Grund. Im Gebirge liegen Tausende Fuß dazwischen – immer klären, welche gemeint ist.'],
    ['Pfund (lb)', /\blb\b|pfund/i, '1 lb = 0,454 kg. Bomben werden nach Gesamtgewicht benannt: 500 lb ≈ 227 kg, davon ist nur knapp die Hälfte Sprengstoff.'],
    ['Kaliber', /kaliber/i, 'Innendurchmesser des Rohrs in Millimetern, z. B. 125 mm (Panzerkanone) oder 152 mm (Haubitze). Größeres Kaliber heißt schwereres Geschoss und mehr Wirkung.'],
    /* ---- Waffen und Wirkung ---- */
    ['JDAM und GPS/INS', /\bjdam\b|gps\/ins|trägheitsnavigation|gps-gelenkt|gps-waffe/i, 'JDAM ist ein Heckkit mit Steuerflossen und GPS/INS-Navigation, das eine normale Bombe zur gelenkten Bombe macht (z. B. GBU-38 = Mk 82 + JDAM). INS ist die Trägheitsnavigation mit Kreiseln, GPS korrigiert ihre Drift. Die Waffe fliegt auf eingegebene Koordinaten – wetterunabhängig, aber nur so genau wie die Koordinate.'],
    ['Laserlenkung (SAL)', /paveway|\blgb\b|lasergelenkt|semi-?aktiv|halbaktive laser|\bsal\b/i, 'Halbaktive Laserlenkung: Ein Suchkopf im Bug sieht den reflektierten Laserpunkt und steuert darauf zu. Jemand – Lfz, Drohne oder du am Boden – muss das Ziel bis zum Einschlag beleuchten, mit dem richtigen Lasercode.'],
    ['Laser-Zielbeleuchter', /zielbeleuchter|designator|laserbeleucht|lasermarkier|mit dem laser beleucht/i, 'Sendet codierte Laserpulse auf das Ziel; die Waffe fliegt auf den reflektierten Punkt. Sichtlinie, Lasercode und Winkel zum Anflug (Sicherheitszone) müssen passen.'],
    ['Lasercode', /lasercode|laser code|\bprf-code/i, 'Meist vierstellige Zahl (z. B. 1688), die das Pulsmuster des Lasers festlegt. Laser und Suchkopf bzw. Spotsucher müssen denselben Code haben.'],
    ['Zünder', /zünder|\bfmu-|\bdsu-|\bjpf\b|\bfuze/i, 'Zünder lösen die Sprengladung aus: Aufschlagzünder (sofort beim Auftreffen), Verzögerung (erst nach dem Eindringen, z. B. in Gebäude) und Annäherungszünder (Airburst, einige Meter über Grund). FMU-139 und FMU-152 (JPF) sitzen meist im Heck, der Annäherungssensor DSU-33 im Bug. Was möglich ist, bestimmt die Beladung – im Check-in erfragen.'],
    ['Airburst', /airburst|annäherungszünder|luftdetonation/i, 'Detonation einige Meter über dem Boden: Die Splitter treffen von oben auch in Gräben und Deckungen. Gut gegen ungeschützte Infanterie, schwach gegen Panzer und Gebäude.'],
    ['Verzögerung und Penetrator', /verzögerung|penetrator|blu-109|bunkerbrech/i, 'Bei Verzögerung dringt die Bombe erst in Beton, Erde oder ein Gebäude ein und detoniert dann innen. Penetratoren wie BLU-109 haben dafür einen besonders dicken Stahlmantel.'],
    ['Splitter und Druckwelle', /splitter|druckwelle|sprengwirkung|blast/i, 'Sprengmunition wirkt durch Druckwelle und Splitter. Splitter fliegen weit – deshalb gibt es Sicherheitsabstände für eigene Truppen.'],
    ['Danger Close (RED)', /danger close|risk[- ]estimate|sicherheitsabstand/i, 'Die Risk-Estimate Distance ist die Entfernung, innerhalb der eigene Truppen mit einer bestimmten Wahrscheinlichkeit verletzt werden. Sind sie näher dran, ist der Einsatz „Danger Close“ und braucht die ausdrückliche Zustimmung des Bodenführers.'],
    ['CEP (Streukreis)', /\bcep\b|streukreis/i, 'Circular Error Probable: Radius, in dem die Hälfte aller Waffen einschlägt. Kleiner CEP heißt genauer.'],
    ['DMPI', /\bdmpi\b/i, 'Desired Mean Point of Impact: der genaue Punkt, auf den die Waffe zielen soll.'],
    ['Hohlladung und Tandem', /hohlladung|\bheat\b|tandem/i, 'Hohlladung: Die Sprengladung formt einen Kupferkegel zu einem extrem schnellen Metallstrahl, der Panzerstahl durchschlägt. Tandemladung: Eine Vorladung löst zuerst die Reaktivpanzerung aus, die Hauptladung trifft dann den Stahl dahinter.'],
    ['Wuchtgeschoss (KE)', /wuchtgeschoss|apfsds|\bke\b|unterkaliber/i, 'Schlanker Pfeil aus Wolfram oder Uran, der allein durch seine Geschwindigkeit (über 1,5 km/s) Panzerung durchschlägt – die Hauptmunition von Kampfpanzern gegen Panzer.'],
    ['Fire-and-forget, LOBL, LOAL', /fire[- ]and[- ]forget|\blobl\b|\bloal\b/i, 'Fire-and-forget: Der Suchkopf führt die Waffe selbst ins Ziel, nach dem Abschuss ist nichts mehr nötig. LOBL = Ziel vor dem Start aufgeschaltet; LOAL = die Waffe startet zuerst und schaltet im Flug auf (z. B. auf deinen Laserpunkt).'],
    ['Wärmebildsuchkopf (IIR)', /\biir\b|wärmebildsuchkopf|bildgebend/i, 'Imaging Infrared: Der Suchkopf erkennt das Ziel im Wärmebild und steuert selbst darauf zu.'],
    ['Radarsuchkopf (MMW)', /millimeterwell|\bmmw\b/i, 'Millimeterwellen-Radarsuchkopf: erkennt Fahrzeuge mit eigenem kleinem Radar, auch durch Rauch und schlechtes Wetter.'],
    ['Bewegtziel', /bewegtziel|\bmovers?\b/i, 'Fahrendes Fahrzeug. Sicher treffen es nur Waffen, die bis zum Einschlag nachgeführt werden (Laser, Wärmebild- oder Radarsuchkopf); reine GPS-Waffen fliegen auf die alte Position.'],
    ['SDB', /\bsdb\b|gbu-39|gbu-53/i, 'Small Diameter Bomb: kleine, sehr genaue Gleitbombe (GBU-39) mit wenig Sprengstoff – geringer Kollateralschaden, große Reichweite. GBU-53 (SDB II) sucht zusätzlich selbst fahrende Ziele.'],
    ['Bombenkörper Mk 82/83/84', /\bmk ?8[234]\b/i, 'Mk 82 (500 lb), Mk 83 (1000 lb) und Mk 84 (2000 lb) sind die Bombenkörper; mit Lenkkits werden daraus z. B. GBU-12, GBU-38 oder GBU-54.'],
    ['Gleitwaffe und Stand-off', /gleitwaffe|gleitbombe|stand-off|standoff/i, 'Gleitwaffe: Bombe ohne eigenen Antrieb, die mit Flügeln weit gleitet. Stand-off heißt: Einsatz von außerhalb der gegnerischen Flugabwehr.'],
    ['Marschflugkörper', /marschflugkörper|cruise missile/i, 'Flugkörper mit eigenem Triebwerk, der wie ein kleines unbemanntes Flugzeug tief und lange fliegt, z. B. Taurus oder Kalibr.'],
    ['Streumunition', /streumunition|submunition|bomblet|\bcbu-/i, 'Behälter mit vielen kleinen Sprengkörpern, die über eine Fläche verteilt werden – gegen Fahrzeugansammlungen. Blindgänger gefährden später eigene Truppen und Zivilisten.'],
    ['Ungelenkte Raketen', /\bhydra\b|ungelenkt|\bnar\b/i, 'Ungelenkte Raketen (z. B. Hydra, 70 mm) werden in Salven geschossen und streuen; APKWS (AGR-20) macht daraus eine lasergelenkte Rakete.'],
    ['Bordkanone und Maschinenkanone', /bordkanone|gau-8|\bm230\b|maschinenkanone|\bmk\b(?!\s?8)/i, 'Automatische Kanone von 20 bis 57 mm, z. B. GAU-8 (30 mm, A-10), M230 (30 mm, Apache) oder 30 mm am BMP-2. Wirkt gegen leichte Fahrzeuge, Infanterie und tief fliegende Hubschrauber und Drohnen.'],
    ['Lenkflugkörper (LFK)', /\blfk\b|lenkflugkörper|kanonen-lfk|rohr-lenkflugkörper/i, 'LFK = Lenkflugkörper. Kanonen- bzw. Rohr-LFK werden aus der Panzerkanone verschossen (z. B. 9M119 Refleks, rund 5 km) und können auch tief fliegende Hubschrauber treffen.'],
    ['Thermobarische Munition', /thermobar/i, 'Verteilt eine Brennstoffwolke und zündet sie: sehr starke, lange Druckwelle, besonders verheerend in Gebäuden, Gräben und Bunkern (z. B. TOS-1A).'],
    /* ---- Sensoren und Pods ---- */
    ['Zielbehälter (Pod)', /\bpod\b|zielbehälter|targeting pod/i, 'Behälter unter dem Lfz mit Tag- und Wärmebildkamera, Laser zum Messen und Markieren und Laserspotsucher. Details im Pod-Trainer.'],
    ['Wärmebild (FLIR, WBG)', /wärmebild|\bflir\b|\bwbg\b|thermal/i, 'Die Kamera sieht Temperaturunterschiede statt Licht – nachts und durch leichten Rauch nutzbar. „White hot“ zeigt Warmes hell, „black hot“ dunkel. Motoren, Auspuff und Menschen fallen auf, frisch abgestellte Fahrzeuge bleiben eine Weile warm.'],
    ['Tagsicht (EO/TV)', /\btv\b|\bccd\b|\beo\b|tagsicht|tageslicht/i, 'Optik bzw. Kamera für sichtbares Licht – bei Dunkelheit, Dunst oder Rauch schnell am Ende. Pods und moderne Fahrzeuge kombinieren sie deshalb mit einem Wärmebildgerät.'],
    ['Laserentfernungsmesser', /entfernungsmesser|\blrf\b|rangefinder/i, 'Misst mit einem kurzen Laserpuls die Entfernung; daraus berechnet das System die Zielkoordinate. Ein Laserwarner am Ziel kann das bemerken.'],
    ['Laserspotsucher (LST)', /laserspotsucher|spotsucher|\blst\b|spot tracker/i, 'Empfänger im Pod oder Lfz, der einen Laserpunkt mit dem eingestellten Code sucht und anzeigt – so findet der Pilot deinen Laser.'],
    ['IR-Pointer und NVG', /ir-pointer|ir-markier|\bnvg\b|nachtsichtbrille|restlichtverstärker/i, 'IR-Pointer: unsichtbarer Infrarot-Zeigelaser, nur mit Nachtsichtgerät (NVG) zu sehen – er zeigt und markiert, lenkt aber keine Waffe. NVG bzw. Restlichtverstärker verstärken vorhandenes Licht; Wärmebildgeräte arbeiten anders (siehe Wärmebild).'],
    ['FMV, VDL und ROVER', /\bfmv\b|\bvdl\b|\brover\b|video ?downlink|full motion/i, 'FMV ist das Live-Video aus Pod oder Drohne. Per Video-Downlink (VDL) kommt es zum Boden, wo du es z. B. mit ROVER siehst – sehr hilfreich beim Talk-on.'],
    ['Sichtfeld (FOV)', /\bfov\b|sichtfeld|\bzoom/i, 'Enges Sichtfeld = starke Vergrößerung, kleiner Ausschnitt; weites Sichtfeld = Überblick. Beim Talk-on erst weit, dann eng.'],
    ['ISR und NTISR', /\bisr\b|ntisr/i, 'ISR = Aufklärung und Überwachung. NTISR (nicht-traditionelle ISR): Kampfflugzeuge nutzen ihren Pod zur Aufklärung, wenn sie gerade nicht angreifen.'],
    ['SAR und GMTI', /\bsar\b|synthetic aperture|\bgmti\b|\bmti\b/i, 'SAR erzeugt aus der Bewegung des Lfz ein fotoähnliches Radarbild des Bodens, auch durch Wolken und nachts. GMTI ist ein Radarmodus, der nur fahrende Ziele zeigt.'],
    ['UAS (Drohne)', /\buas\b|\buav\b|drohne|mq-9/i, 'Unbemanntes Luftfahrzeug mit Bodenstation. Größere Systeme wie die MQ-9 bleiben viele Stunden über dem Raum, haben einen Pod mit Laser und tragen teils Waffen; kleine Drohnen dienen Aufklärung und Artilleriebeobachtung oder greifen selbst an.'],
    /* ---- Flugabwehr, Bedrohung, EloKa ---- */
    ['SAM und Wirkbereich (WEZ)', /\bsam\b|fla-rakete|flugabwehrrakete|wirkbereich|\bwez\b/i, 'SAM = Boden-Luft-Flugkörper. Der Wirkbereich (WEZ) ist der Raum, in dem ein System Lfz bekämpfen kann. Er hängt von Höhe, Zielart und Gelände ab und wird auf Karten meist als Ring gezeichnet.'],
    ['NATO-Bezeichnungen', /\bsa-\d|\bat-\d|nato-name|nato-bezeichnung/i, 'Die NATO gibt russischen Waffen eigene Namen: SA-xx für Fla-Raketensysteme (z. B. SA-15 Gauntlet = russisch Tor), AT-xx für Panzerabwehr-Lenkflugkörper. Russisch heißen sie nach Index (z. B. 9K330) oder Namen.'],
    ['TEL, TELAR, TLAR', /\btel\b|telar|\btlar\b/i, 'TEL: Fahrzeug, das Flugkörper transportiert und startet, aber kein eigenes Feuerleitradar hat. TELAR bzw. TLAR: Start- und Radarfahrzeug in einem – kann ohne weiteres Radar selbstständig Ziele suchen und bekämpfen.'],
    ['Such- und Feuerleitradar', /suchradar|feuerleitradar|zielverfolgung|zielbeleuchtungsradar|rundsuch|zielerfassungsradar/i, 'Das Suchradar (Rundsuche) entdeckt Ziele auf große Entfernung. Das Feuerleit- bzw. Zielverfolgungsradar verfolgt dann ein Ziel genau und lenkt den Flugkörper. Der Wechsel von Suche zu Verfolgung ist auf dem RWR die höchste Warnstufe.'],
    ['Lenkarten von Flugkörpern', /kommandolenkung|halbaktiv|radarsuchkopf|ir-suchkopf|infrarotsuchkopf|ir-gelenkt|infrarotgelenkt/i, 'Kommandolenkung: Die Bodenstation steuert den Flugkörper per Funk. Halbaktive Radarlenkung: Ein Bodenradar beleuchtet das Ziel, der Suchkopf folgt dem Echo. Aktiver Radarsuchkopf: Der Flugkörper hat sein eigenes Radar. Infrarot: Der Suchkopf folgt der Wärme – kein Radar, also keine RWR-Warnung.'],
    ['RWR (Radarwarnempfänger)', /\brwr\b|radarwarn/i, 'Zeigt im Lfz an, welches Radar das Lfz anstrahlt, aus welcher Richtung und ob es nur sucht oder schon verfolgt. Gegen infrarotgelenkte MANPADS warnt er nicht.'],
    ['Raketenwarner (MAWS)', /\bmaws\b|raketenwarn|flugkörperwarn/i, 'Erkennt einen anfliegenden Flugkörper an seinem Abgasstrahl (UV bzw. IR) – warnt auch vor MANPADS, die der RWR nicht sieht.'],
    ['MANPADS', /manpads/i, 'Schultergestützte Fla-Rakete mit Infrarot-Suchkopf (z. B. Igla, Verba, Stinger). Kein Radar, deshalb keine RWR-Warnung – nur der Raketenwarner sieht den Start.'],
    ['Täuschkörper und DIRCM', /flares?\b|chaff|düppel|täuschkörper|dircm/i, 'Flares (Leuchtkörper) lenken infrarotgelenkte Flugkörper ab, Chaff (Düppel) täuscht Radare. DIRCM ist ein Laser-Störer, der den Infrarot-Suchkopf einer anfliegenden Rakete blendet.'],
    ['SEAD und DEAD', /\bsead\b|\bdead\b/i, 'SEAD = Unterdrückung der feindlichen Luftverteidigung, z. B. Radare zum Abschalten zwingen; DEAD = ihre Zerstörung.'],
    ['Anti-Radar-Flugkörper', /anti-radar|\bharm\b|\barm\b/i, 'Flugkörper, der auf die Abstrahlung eines Radars zufliegt (z. B. HARM). Schaltet das Radar ab, verliert er sein Ziel – deshalb strahlen Fla-Radare oft nur kurz.'],
    ['EloKa (EW)', /\beloka\b|\bew\b|elektronische kampf/i, 'Elektronische Kampfführung: gegnerische Abstrahlungen erfassen und orten, stören oder täuschen – und eigene Systeme davor schützen.'],
    ['Störsender', /störsend|störer|\bjamm/i, 'Überlagert gegnerische Radar-, Funk- oder GPS-Frequenzen mit Rauschen oder falschen Signalen, sodass der Empfänger nichts oder Falsches sieht.'],
    ['Peilung und Ortung', /peil|ortung|geolocation/i, 'Peilen mehrere Stellen denselben Sender, schneiden sich die Linien – dort steht er. So werden Radare, Störsender und auch dein Funkgerät gefunden.'],
    ['EMCON', /emcon|emissionsbeschränkung/i, 'Vorgaben, welche Sender (Radar, Funk, Datenlink) wann strahlen dürfen – damit man nicht geortet wird.'],
    /* ---- Landstreitkräfte, Fahrzeuge ---- */
    ['Kampfpanzer, SPz, SPW', /schützenpanzer|\bspz\b|\bspw\b|transportpanzer|kampfpanzer|\bkpz\b/i, 'Kampfpanzer (KPz): schwer gepanzert, große Kanone, kämpft gegen Panzer. Schützenpanzer (SPz, z. B. BMP): trägt Infanterie und kämpft mit Maschinenkanone und Panzerabwehr-Lenkflugkörper. Schützenpanzerwagen bzw. Transportpanzer (SPW, z. B. BTR): leichter gepanzert, vor allem für den Transport, oft auf Rädern.'],
    ['Reaktivpanzerung (ERA)', /reaktivpanzer|\bera\b|kontakt-[15]|relikt/i, 'Kästen mit Sprengstoff außen am Panzer: Trifft eine Hohlladung, detonieren sie und stören den Metallstrahl. Kontakt-1 (älter, nur gegen Hohlladung), Kontakt-5 und Relikt (auch gegen Wuchtgeschosse). Tandem-Gefechtsköpfe überwinden sie.'],
    ['Gitter- und Käfigpanzerung', /gitterpanzer|stabgitter|käfig|\bslat\b|dachgitter|cope cage/i, 'Stabgitter bzw. Käfige vor den Seiten und über dem Turm sollen Hohlladungen und Drohnen vor der eigentlichen Panzerung zur Detonation bringen oder deren Zünder beschädigen.'],
    ['Aktives Schutzsystem', /aktives schutzsystem|\baps\b|\barena\b|afganit|trophy/i, 'Erkennt anfliegende Geschosse per Radar und bekämpft sie kurz vor dem Fahrzeug (z. B. Arena, Afganit, Trophy).'],
    ['Laserwarner', /laserwarn|shtora|schtora/i, 'Meldet, wenn das Fahrzeug von einem Laser getroffen wird (Entfernungsmesser oder Zielbeleuchter). Viele Systeme lösen dann automatisch Nebel aus oder drehen den Turm in die Richtung – dein Laser kann also bemerkt werden.'],
    ['Nebelwurfanlage', /nebelwurf|nebelgranat|aerosol/i, 'Wurfbecher verschießen Nebel- bzw. Aerosolgranaten, die Sicht und Laser blockieren und Wärmebild zumindest teilweise.'],
    ['Wanne und Turm', /\bwanne\b|turmheck|heckkasten|turmdach/i, 'Die Wanne ist der untere Fahrzeugkörper mit Laufwerk und Motor; der Turm sitzt drehbar darauf. Längenangaben in der App gelten für die Wanne ohne Rohr.'],
    ['Laufwerk', /laufrolle|antriebsrad|leitrad|stützrolle|laufwerk/i, 'Laufrollen tragen das Fahrzeug, das Antriebsrad mit Zähnen treibt die Kette, das Leitrad am anderen Ende spannt sie, Stützrollen oben tragen die Kette. Anzahl, Größe und Abstand der Laufrollen sind wichtige Erkennungsmerkmale.'],
    ['Rundblickgerät des Kommandanten', /rundblick|panoramaperiskop|kommandantenzielgerät|hunter[- ]killer/i, 'Unabhängig vom Turm schwenkbar: Der Kommandant sucht das nächste Ziel, während der Richtschütze noch kämpft („Hunter-Killer“).'],
    ['Waffenstation', /waffenstation|\brws\b/i, 'MG oder Granatmaschinenwaffe auf dem Dach, die von innen per Kamera bedient wird – die Besatzung muss dafür nicht aus der Luke.'],
    ['VDV (Luftlandetruppen)', /\bvdv\b|luftlande/i, 'VDV sind die russischen Luftlandetruppen; ihre Fahrzeuge (BMD, BTR-D) sind leichter gebaut und können aus Flugzeugen abgesetzt werden.'],
    /* ---- Artillerie ---- */
    ['Steilfeuer', /steilfeuer|indirekte[sn]? feuer|flachfeuer/i, 'Steilfeuer (indirektes Feuer): Artillerie und Mörser schießen im hohen Bogen auf Ziele, die sie selbst nicht sehen; ein Beobachter leitet das Feuer. Flachfeuer: direkt auf ein sichtbares Ziel, z. B. aus der Panzerkanone.'],
    ['Selbstfahrlafette und gezogen', /selbstfahrlafette|\bsfl\b|\bgezogene?[snr]?\b/i, 'Selbstfahrlafette: Geschütz auf eigenem Fahrgestell, schnell in und aus der Stellung. Gezogenes Geschütz: wird von einem Lkw gezogen; der Stellungsbezug dauert länger.'],
    ['Feuerstellung und Stellungswechsel', /feuerstellung|stellungswechsel|shoot[- ]and[- ]scoot|stellungsraum/i, 'Die Feuerstellung ist der Ort, von dem aus geschossen wird. Moderne Artillerie wechselt nach wenigen Schüssen die Stellung („shoot and scoot“), um der Gegenbatterie zu entgehen – dein Zeitfenster ist kurz.'],
    ['Ortungsradar und Gegenbatterie', /ortungsradar|gegenbatterie|counter-?battery|zoopark|\bcobra\b/i, 'Ein Artillerieortungsradar (z. B. Zoopark, COBRA) verfolgt anfliegende Geschosse und rechnet zurück, wo sie abgefeuert wurden. Darauf folgt Gegenbatteriefeuer auf die feuernde Artillerie.'],
    ['Mehrfachraketenwerfer', /raketenwerfer|mehrfachraketen|\bmrl\b|\bmlrs\b/i, 'Feuert viele Raketen in wenigen Sekunden auf eine Fläche (BM-21 Grad z. B. 40 Raketen) – großer Flächeneffekt, danach meist sofort Stellungswechsel.'],
    ['Mörser', /mörser/i, 'Steilfeuerwaffe der Kampftruppe mit kurzer Reichweite (beim 120-mm-Mörser meist bis rund 7 km) und sehr schneller Feuerbereitschaft.'],
    ['Beobachter und Feuerleitstelle', /beobachter|feuerleitstelle|\bvb\b|\bfo\b/i, 'Der vorgeschobene Beobachter (VB) sieht das Ziel und fordert und leitet das Feuer; die Feuerleitstelle rechnet die Schießwerte für die Geschütze.'],
    ['Gipfelhöhe (MAX ORD)', /gipfelhöhe|max ord/i, 'Höchster Punkt der Geschossbahn. Für dich wichtig, damit Lfz nicht in die Flugbahn von Artillerie oder Mörsern geraten.'],
    /* ---- Funk ---- */
    ['UHF und VHF', /\buhf\b|\bvhf\b/i, 'Militärischer UHF-Flugfunk liegt bei 225–400 MHz (AM), der VHF-Truppenfunk bei 30–88 MHz (FM). Mit dem Lfz sprichst du meist auf UHF, mit der eigenen Truppe auf VHF. Details im Funk-Trainer.'],
    ['Frequenzsprung', /have ?quick|saturn|sincgars|frequenzsprung/i, 'Das Funkgerät wechselt viele Male pro Sekunde die Frequenz nach gemeinsamem Schlüssel und gemeinsamer Uhrzeit – schwer zu stören und zu peilen.'],
    ['SATCOM', /satcom|satellitenfunk|tacsat/i, 'Funk über einen Satelliten in rund 36 000 km Höhe – Verbindung über Hunderte bis Tausende km ohne Relais; die Antenne muss freie Sicht zum Satelliten haben.']
  ];

  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const find = text => T.filter(t => t[1].test(text));
  const body = list => list.map(t => `<p><b>${esc(t[0])}:</b> ${esc(t[2])}</p>`).join('');

  const css = document.createElement('style');
  css.textContent = `.jt-terms{margin-top:12px;padding:10px 12px;background:var(--surface2,rgba(128,128,128,.10));border:1px solid var(--line,rgba(128,128,128,.35));border-radius:8px;font-size:.92rem;line-height:1.45;text-align:left;color:inherit}
.jt-terms .jt-th,.jt-terms summary{font-family:var(--font-d,inherit);font-weight:700;font-size:.82rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#667)}
.jt-terms summary{cursor:pointer}
.jt-terms p{margin:5px 0 0}`;
  document.head.appendChild(css);

  function enhance(){
    const main = document.querySelector('main') || document.body;
    main.querySelectorAll('.fb:not([data-terms])').forEach(fb => {
      fb.setAttribute('data-terms', '1');
      const list = find(main.innerText || '');
      if (!list.length) return;
      const html = `<div class="jt-terms"><div class="jt-th">Hintergrund</div>${body(list)}</div>`;
      /* Liegt die Knopfzeile (Weiter, Melden) im Kasten, kommt der Hintergrund davor */
      const last = fb.lastElementChild;
      if (last && last.querySelector && last.querySelector('button') && !last.matches('p, .v')) last.insertAdjacentHTML('beforebegin', html);
      else fb.insertAdjacentHTML('beforeend', html);
    });
    const sh = document.getElementById('sheet');
    if (sh && !sh.hidden){
      const box = sh.querySelector('.wrap') || sh;
      if (!box.querySelector(':scope > .jt-terms')){
        const list = find(box.innerText || '');
        if (list.length) box.insertAdjacentHTML('beforeend', `<details class="jt-terms"><summary>Hintergrund: ${list.length} Fachbegriffe erklärt</summary>${body(list)}</details>`);
      }
    }
  }
  let queued = false;
  const run = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; enhance(); }); };
  new MutationObserver(run).observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['hidden']});
  run();
  window.__jtTerms = {T, find};
})();
