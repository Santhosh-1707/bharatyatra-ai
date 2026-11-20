import os
import socket
import uvicorn

# Load .env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_file):
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("\n" + "=" * 70)
    print("🇮🇳  BharatYatra AI - India Tourism & Local Guides Platform")
    print("=" * 70)
    print(f"💻 Local Browser Demo URL:   http://localhost:{port}")
    print(f"📲 Mobile Phone (LAN/Wi-Fi): http://{local_ip}:{port}")
    print(f"📋 Live Leads Dashboard:    http://localhost:{port}/api/enquiries")
    print(f"📊 Platform Stats Endpoint:  http://localhost:{port}/api/stats")
    print("=" * 70)
    print("✨ Demo Presentation Tips for Your Team:")
    print("   1. Open http://localhost:8000 on your presentation screen or projector.")
    print("   2. Try clicking quick chips (e.g. Kashmir Valley, Thar Desert, Kerala).")
    print("   3. Show the dynamic Cost Breakdown widget & click 'Copy WhatsApp Summary'.")
    print("   4. Tap 'Enquire' on any guide to show the 1-tap WhatsApp deep-link.")
    print("   5. Click '📋 Leads' in top right to show real-time SQLite lead persistence!")
    print("=" * 70 + "\n")
    
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=True)
