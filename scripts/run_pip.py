import subprocess
import sys

print("Executing pip install pyarrow with real-time output...", flush=True)
cmd = [sys.executable, "-m", "pip", "install", "pyarrow", "--verbose", "--no-cache-dir"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

for line in process.stdout:
    print(line, end="", flush=True)

process.wait()
print(f"\nExited with code {process.returncode}", flush=True)
