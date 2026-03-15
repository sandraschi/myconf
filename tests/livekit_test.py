import socket
import sys


def check_livekit_connectivity(host="localhost", port=15580):
    print(f"Probing LiveKit at {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"✅ LiveKit port {port} is OPEN and reachable.")
            return True
    except ConnectionRefusedError:
        print(f"❌ LiveKit port {port} CONNECTION REFUSED. Is the container running?")
    except socket.timeout:
        print(f"❌ LiveKit port {port} TIMEOUT. Check firewall settings.")
    except Exception as e:
        print(f"❌ Unexpected error probing LiveKit: {e}")
    return False


if __name__ == "__main__":
    if not check_livekit_connectivity():
        sys.exit(1)
