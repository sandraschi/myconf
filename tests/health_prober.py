import subprocess
import sys
import os


def run_test(name, script_path):
    print(f"\n--- RUNNING TEST: {name} ---")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    return True


def probe_docker_health():
    print("\n--- PROBING DOCKER STACK ---")
    try:
        proc = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}: {{.Status}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        containers = proc.stdout.strip().split("\n")
        required = ["myconf-web-1", "myconf-agent-1", "myconf-livekit-1", "myconf-redis-1"]

        running_names = [c.split(":")[0] for c in containers]
        all_ok = True
        for name in required:
            if name in running_names:
                status = [c for c in containers if c.startswith(name)][0]
                print(f"✅ {status}")
            else:
                print(f"❌ {name} is NOT running.")
                all_ok = False
        return all_ok
    except Exception as e:
        print(f"❌ Docker probe failed: {e}")
        return False


def main():
    print("AG-Visio Industrial Health Prober (SOTA-2026)")

    tests_dir = os.path.dirname(__file__)

    success = True
    success &= run_test("Reductionist Logic", os.path.join(tests_dir, "logic_test.py"))
    success &= run_test("LiveKit Connectivity", os.path.join(tests_dir, "livekit_test.py"))
    success &= run_test("MCP Server Integrity", os.path.join(tests_dir, "mcp_test.py"))
    success &= probe_docker_health()

    if success:
        print("\n🏆 GLOBAL HEALTH STATUS: OPERATIONAL")
    else:
        print("\n🚨 GLOBAL HEALTH STATUS: DEGRADED")
        sys.exit(1)


if __name__ == "__main__":
    main()
