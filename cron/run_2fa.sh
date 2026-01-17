#!/bin/sh

SEED=$(cat /data/seed.txt)
NOW=$(date +%s)
COUNTER=$((NOW / 30))

python - <<EOF
import hmac, hashlib, struct
key = bytes.fromhex("$SEED")
msg = struct.pack(">Q", $COUNTER)
h = hmac.new(key, msg, hashlib.sha1).digest()
o = h[-1] & 0x0F
code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
print(str(code).zfill(6))
EOF
