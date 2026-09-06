#!/bin/sh
# Monta a ferramenta a partir de css + js + payload. Nada e digitado a mao no HTML.
set -e
cd "$(dirname "$0")/../.."
python3 - <<'PY'
import json
css = open('v1/casco/estilo.css',encoding='utf-8').read()
js  = open('v1/casco/app.js',encoding='utf-8').read()
pay = open('v1/dados/CASCO-PAYLOAD.json',encoding='utf-8').read()
p = json.loads(pay)
shell = open('v1/casco/shell.html',encoding='utf-8').read()
html = (shell.replace('/*CSS*/', css)
             .replace('/*PAYLOAD*/', pay)
             .replace('/*JS*/', js)
             .replace('{VERSION}', p['VERSION'])
             .replace('{BUILT_AT}', p['BUILT_AT'])
             .replace('{AUTHORITY}', p['SOURCE_AUTHORITY'])
             .replace('{RULESET}', p['RULESET_VERSION'])
             .replace('{LICENSE}', p['LICENSE']))
open('v1/casco/label-intelligence.html','w',encoding='utf-8').write(html)
print(f"  v1/casco/label-intelligence.html ({len(html)/1024:.0f} KB)")
PY
