import sys
import os
import time
import socket
import threading
import subprocess
import re
import uvicorn

PORT = 8080
KEY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ssh_key")

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

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    print(f"[*] Starting BharatYatra AI server on 127.0.0.1:{PORT}...", flush=True)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=PORT, log_level="warning")

def run_tunnel():
    print("[*] Waiting for server to be ready on port 8080...", flush=True)
    for _ in range(30):
        if is_port_open(PORT):
            break
        time.sleep(0.5)
    
    if not is_port_open(PORT):
        print(f"[-] Error: Server did not start on port {PORT}.", flush=True)
        return

    print("[*] Server is running! Establishing public internet tunnel...", flush=True)

    ssh_opts = [
        "-i", KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=NUL",
        "-o", "ServerAliveInterval=20",
        "-o", "ServerAliveCountMax=5"
    ]

    tunnel_configs = [
        {
            "name": "Localhost.run",
            "cmd": ["ssh"] + ssh_opts + ["-R", f"80:127.0.0.1:{PORT}", "nokey@localhost.run"],
            "url_pattern": re.compile(r'https://[a-zA-Z0-9.-]+\.lhr\.life')
        },
        {
            "name": "Pinggy",
            "cmd": ["ssh", "-p", "443"] + ssh_opts + [f"-R0:127.0.0.1:{PORT}", "a.pinggy.io"],
            "url_pattern": re.compile(r'https://[a-zA-Z0-9.-]+\.a\.pinggy\.link')
        }
    ]

    for cfg in tunnel_configs:
        print(f"[*] Connecting to {cfg['name']}...", flush=True)
        try:
            proc = subprocess.Popen(
                cfg["cmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
                bufsize=1
            )

            url_found = None
            start_time = time.time()
            
            while time.time() - start_time < 20:
                line = proc.stdout.readline()
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue

                line_clean = line.strip()
                if line_clean:
                    print(f"    {line_clean}", flush=True)
                
                # Check for URL
                match = cfg["url_pattern"].search(line_clean)
                if match:
                    url_found = match.group(0)
                    break
                generic_match = re.search(r'https://[a-zA-Z0-9.-]+(?:\.pinggy\.link|\.lhr\.life)', line_clean)
                if generic_match:
                    url_found = generic_match.group(0)
                    break

            if url_found:
                print("\n" + "=" * 65, flush=True)
                print("🎉 SUCCESS! YOUR APP IS NOW PUBLICLY AVAILABLE ONLINE!", flush=True)
                print("=" * 65, flush=True)
                print(f"👉 PUBLIC URL: {url_found}", flush=True)
                print("=" * 65, flush=True)
                print("Anyone can open this link on their phone or laptop right now!\n", flush=True)
                
                with open("PUBLIC_URL.txt", "w", encoding="utf-8") as f:
                    f.write(url_found)

                # Keep reading output so buffer does not block
                for line in proc.stdout:
                    pass
                proc.wait()
                return
            else:
                proc.terminate()
        except Exception as e:
            print(f"[-] {cfg['name']} error: {e}", flush=True)

    print("[-] Could not establish public tunnel.", flush=True)

if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    run_tunnel()
