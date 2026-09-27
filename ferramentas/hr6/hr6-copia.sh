#!/usr/bin/env bash
set -e
VIVO=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
RAMO=C:/Users/London1/orca/workspaces/eame-sintonia/reparo-fontes-v1
C=/c/hr6
rm -rf $C; mkdir -p $C
git -C $RAMO archive HEAD | tar -x -C $C
cd $VIVO; git status --short | grep "^ M" | awk '{print $2}' > $C/SUJOS.txt
while read f; do cp "$VIVO/$f" "$C/$f"; done < $C/SUJOS.txt
cd $C
for f in $(cat SUJOS.txt); do sha256sum "$f"; done > SHA-SUJOS.txt
echo "vivo $(git -C $VIVO rev-parse --short HEAD) · ramo $(git -C $RAMO rev-parse --short HEAD) · sujos $(wc -l < SUJOS.txt)"
git -C $VIVO status --short | grep -v "^ M" | head
