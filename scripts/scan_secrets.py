import os
import re

PATTERNS = [
    (r'(?i)(api[_-]?key|secret|token|password|auth|bearer|credential)\s*[:=]\s*[\'\"][^\'\"]{4,}[\'\"]', 'API Key / Secret Assignment'),
    (r'ghp_[0-9a-zA-Z]{36}', 'GitHub Personal Access Token'),
    (r'AIza[0-9A-Za-z-_]{35}', 'Google API Key'),
    (r'sk-[0-9a-zA-Z]{20,}', 'OpenAI Secret Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'-----BEGIN (?:RSA )?PRIVATE KEY-----', 'Private Key Header'),
]

print("="*60)
print("SCANNING WORKSPACE FOR SENSITIVE DATA AND CREDENTIALS")
print("="*60)

found_any = False
scanned_count = 0

for root, dirs, files in os.walk('.'):
    # Skip .git if present
    if '.git' in dirs:
        dirs.remove('.git')
    for f in files:
        fpath = os.path.join(root, f)
        # Skip binary PDFs
        if f.lower().endswith('.pdf'):
            continue
            
        scanned_count += 1
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
                for line_idx, line in enumerate(lines, 1):
                    for pat, desc in PATTERNS:
                        matches = re.findall(pat, line)
                        if matches:
                            print(f"[!] Warning in {fpath} line {line_idx} ({desc}): {line.strip()[:100]}")
                            found_any = True
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

print(f"\nScanned {scanned_count} non-binary files.")
if not found_any:
    print("✓ CLEAN: No exposed credentials, API keys, passwords, or secrets detected.")
else:
    print("⚠ ACTION REQUIRED: Credentials detected above.")
