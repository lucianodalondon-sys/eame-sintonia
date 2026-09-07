#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MUDAR UMA PECA DE GAVETA — e levar os ficheiros dela junto.

    py system-map/scripts/mudar_gaveta.py C-ADAMA-ES Z-GUARDA

A lei diz que a pasta tem de bater com o mapa. Uma lei so sobrevive se for FACIL
de obedecer: se mudar uma peca de zona obrigar a lembrar de mover ficheiros, de
reescrever workflows, de acertar testes e de recarimbar o mapa, mais cedo ou mais
tarde alguem faz metade — e as duas verdades separam-se outra vez.

Este ficheiro faz a metade que se esquece:

    1. move os ficheiros para a gaveta da zona nova (`git mv`)
    2. reescreve toda a chamada que apontava para o caminho velho
    3. muda a peca de zona no ficheiro declarado
    4. recusa-se a continuar se alguma referencia ficar para tras

O que ele NAO faz: decidir se a mudanca esta certa. Isso e de gente, e a pergunta
continua a mesma — *isto vai buscar alguma coisa? decide o que entra? guarda?*
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DECL = RAIZ / "system-map" / "data" / "architecture.declared.json"

# Nao se toca em registo do passado: um relatorio de ontem tem de continuar a
# dizer o que dizia ontem.
NAO_TOCAR = ('build/', 'handoff/', 'research/', 'data/', '.git/', 'node_modules/',
             'system-map/data/', 'italia-portale/client/system-map/')
EXT = {'.yml', '.yaml', '.sh', '.py', '.mjs', '.js', '.md', '.json', '.html'}


def git(*a):
    r = subprocess.run(['git', '-C', str(RAIZ), *a], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    peca_id, zona_nova = sys.argv[1], sys.argv[2]

    D = json.loads(DECL.read_text(encoding='utf-8'))
    zonas = {z['id']: z for z in D['TERRITORIES']}
    peca = next((c for c in D['COMPONENTS'] if c['id'] == peca_id), None)
    if not peca:
        print(f"peca desconhecida: {peca_id}", file=sys.stderr); return 1
    if zona_nova not in zonas:
        print(f"zona desconhecida: {zona_nova}", file=sys.stderr); return 1

    gaveta = zonas[zona_nova].get('folder')
    antiga = zonas.get(peca['territory'], {}).get('folder')
    print(f"«{peca['name']}»")
    print(f"  {peca['territory']} ({antiga or 'sem gaveta'}/)"
          f"  ->  {zona_nova} ({gaveta or 'sem gaveta'}/)")

    # ── 1 · mover ────────────────────────────────────────────────────────────
    mudados = {}
    novos = []
    for f in peca['files']:
        if any(ch in f for ch in '*?['):
            novos.append(re.sub(r'^[^/]+/', f'{gaveta}/', f) if gaveta and antiga
                         and f.startswith(antiga + '/') else f)
            continue
        p = pathlib.Path(f)
        if not gaveta or p.parent.as_posix() == gaveta or not (RAIZ / f).exists():
            novos.append(f); continue
        destino = f"{gaveta}/{p.name}"
        (RAIZ / gaveta).mkdir(exist_ok=True)
        git('mv', f, destino)
        mudados[f] = destino
        novos.append(destino)
    peca['files'] = novos
    peca['territory'] = zona_nova
    if peca.get('exclude'):
        peca['exclude'] = [mudados.get(x, x) for x in peca['exclude']]
    print(f"  1 · {len(mudados)} ficheiro(s) movido(s)")

    # ── 2 · reescrever as chamadas, inteiras e partidas ──────────────────────
    n_ref = n_fich = 0
    for p in RAIZ.rglob('*'):
        rel = p.relative_to(RAIZ).as_posix()
        if not p.is_file() or p.suffix not in EXT or rel.startswith(NAO_TOCAR):
            continue
        try:
            t = t0 = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        for velho, novo in mudados.items():
            t = t.replace(velho, novo)
            # caminho partido em pedacos: ('regras', 'x.py') -> ('guarda', 'x.py')
            vp, nome = velho.split('/', 1)
            t = re.sub(rf"(\(\s*|,\s*)['\"]{re.escape(vp)}['\"]\s*,\s*['\"]{re.escape(nome)}['\"]",
                       lambda m: f"{m.group(1)}'{novo.split('/')[0]}', '{nome}'", t)
        if t != t0:
            p.write_text(t, encoding='utf-8')
            n_fich += 1
            n_ref += sum(t0.count(v) for v in mudados)
    print(f"  2 · {n_ref} chamada(s) reescritas em {n_fich} ficheiro(s)")

    DECL.write_text(json.dumps(D, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
    print("  3 · mapa declarado atualizado")

    # ── 4 · nada pode ficar para tras ────────────────────────────────────────
    sobrou = []
    for velho in mudados:
        vp, nome = velho.split('/', 1)
        saida = subprocess.run(['git', '-C', str(RAIZ), 'grep', '-n', '-F', velho],
                               capture_output=True, text=True,
                               encoding='utf-8', errors='replace').stdout
        sobrou += [l for l in saida.splitlines() if not l.startswith(NAO_TOCAR)]
    if sobrou:
        print(f"\n  4 · ATENCAO: {len(sobrou)} referencia(s) ao caminho velho ficaram:")
        for l in sobrou[:10]:
            print(f"      {l[:120]}")
        return 1
    print("  4 · nenhuma referencia ao caminho velho ficou para tras")

    mau = [f for f in peca['files'] if not any(c in f for c in '*?[')
           and not (RAIZ / f).exists()]
    if mau:
        print(f"\n  FALHA: ficheiro declarado e ausente: {mau}")
        return 1

    print("\nAgora corra:")
    print("  py system-map/scripts/generate_system_map.py --stamp")
    print("  py system-map/scripts/validate_system_map.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
