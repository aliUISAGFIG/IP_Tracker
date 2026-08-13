# QR Code IP & GPS Tracker

> ⚠️ Hinweis: Dieses Projekt wurde ausschließlich zu Bildungszwecken und für autorisiertes Penetration Testing entwickelt. Jegliche Verwendung ohne ausdrückliche Zustimmung des Ziels ist illegal.

## Beschreibung

Ein Python-basierter Webserver, der über einen QR-Code die IP-Adresse, den geografischen Standort (GPS) und Geräteinformationen von Besuchern erfasst. Nach dem Scan wird der Benutzer zu einer Website weitergeleitet.

## Funktionen

- IP-Erfassung: Erfasst die öffentliche IP-Adresse des Besuchers
- GPS-Geolocation: Nutzt die GPS-Schnittstelle des Smartphones für Standortdaten
- Geräteinformationen: Erfasst User-Agent, Betriebssystem, Bildschirmauflösung und Sprache
- Adressauflösung: Konvertiert GPS-Koordinaten in eine lesbare Adresse
- Logging: Speichert erfasste Daten in einer Textdatei (`captured_ips.txt`)
- Weiterleitung: Weiterleitung nach Abschluss des Tests

## Technologien

- Python
- Flask – Python Web-Framework
- qrcode – QR-Code-Generierung
- ngrok – Exposition des lokalen Servers über das Internet
- OpenStreetMap Nominatim API – Reverse-Geocoding
- ip-api.com – IP-basierte Geolocation als Fallback

## Projektstruktur
QRTracker/
├── qr_tracker_v3.py       # Hauptserver (Flask)
├── make_qr_v3.py          # QR-Code-Generator
├── captured_ips.txt       # Log-Datei
├── tracker_qr_v3.png      # Generierter QR-Code
└── ngrok.exe              # Tunnel-Tool (optional)

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Abhängigkeiten installieren
pip install flask qrcode[pil]

### Schritt 2: Ngrok einrichten

1. Registrieren Sie sich bei ngrok.
2. Laden Sie ngrok.exe herunter und platzieren Sie es im Projektordner.
3. Authentifizieren Sie sich:
ngrok config add-authtoken IHRE_TOKEN_HIER

### Schritt 3: Server starten
python qr_tracker_v3.py

Der Server läuft standardmäßig auf:
http://0.0.0.0:5000

### Schritt 4: Ngrok-Tunnel starten
ngrok http 5000

Kopieren Sie anschließend die öffentliche HTTPS-URL.

Beispiel:
https://xxxx.ngrok-free.app

### Schritt 5: QR-Code generieren

Öffnen Sie make_qr_v3.py und tragen Sie Ihre Ngrok-URL ein:
TRACK_URL = "https://IHRE_NGROK_URL.ngrok-free.app/track"

Führen Sie anschließend aus:
python make_qr_v3.py

Der QR-Code wird als:
tracker_qr_v3.png

gespeichert.

## Funktionsweise

1. Der QR-Code enthält die URL des Testservers.
2. Beim Scannen wird die Webseite geöffnet.
3. Der Browser kann nach Zustimmung des Benutzers Standortzugriff erhalten.
4. Im autorisierten Test können IP-, Standort- und Geräteinformationen protokolliert werden.
5. Anschließend erfolgt die konfigurierte Weiterleitung.

## Beispiel-Log-Ausgabe
[2026-08-13 10:47:23]
IP: 151.101.45.12
GPS_Source: gps
Lat: 52.5200
Lon: 13.4050
Accuracy: 5m
IP_Country: Germany
IP_City: Berlin
Platform: iPhone
Lang: de-DE
Screen: 390x844

## Rechtlicher Hinweis

Dieses Tool darf nur in folgenden Kontexten verwendet werden:

- Autorisierte Penetration Tests
- Capture The Flag (CTF) Wettbewerbe
- Sicherheitsforschung mit Einwilligung
- Bildungszwecke in kontrollierten Umgebungen

Unautorisierte Erfassung von Standort-, IP- oder Gerätedaten Dritter ist nicht zulässig.

## Autor

Entwickelt als Teil eines Auswahlverfahrens für eine Position im Bereich Cybersecurity / Ethical Hacking.

---

*Erstellt mit Python & Flask*
