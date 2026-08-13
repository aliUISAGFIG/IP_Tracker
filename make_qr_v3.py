import qrcode

# ==========================================
# آدرس ngrok خودت رو اینجا بذار + /track
# ==========================================
TRACK_URL = "https://handstand-sandpit-hardware.ngrok-free.dev/track"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(TRACK_URL)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("tracker_qr_v3.png")
print("[+] QR Code saved as tracker_qr_v3.png")
print("[+] URL inside QR:", TRACK_URL)
