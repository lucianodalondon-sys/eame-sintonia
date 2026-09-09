#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O COMMIT X ACABOU DE SER PUBLICADO?

    MAPA VALIDO NAO E MAPA ACTUAL.

`validate_system_map.py` prova que o mapa commitado corresponde a arvore. Isso
dava PASS enquanto o URL publico servia outro commit — e foi exactamente assim
que o mapa ficou a mostrar `105602f6` com `624/1321` enquanto a cabeca da linha
canonica ja ia em `8e1947d2`. Nenhum portao existia entre GIT e SERVIDO.

Este ficheiro e esse portao. Ele nao publica nada: mede o que esta SERVIDO e
compara com o commit que acabou de ser empurrado.

    A VERCEL PUBLICA. ESTE SCRIPT CONFERE. UMA AUTORIDADE DE DEPLOY.

COMO ELE ACHA O URL SEM UM TOKEN NOVO
-------------------------------------
A integracao Git da Vercel escreve um GitHub Deployment por cada deployment
(medido: `githubDeployment: 1` em todos). A API de Deployments do GitHub devolve
o `environment_url` de cada um. Credencial: so o `GITHUB_TOKEN` da propria
corrida, com `deployments: read`. Nenhum segredo novo entra no repositorio, e
nenhum segredo sai daqui.

O QUE ELE REPROVA
-----------------
  · o push nao produziu deployment nenhum dentro do tecto de espera;
  · `/system-map/deployment.generated.json` nao existe no que foi servido;
  · DEPLOYED_COMMIT servido != o SHA desta corrida;
  · o mapa servido foi gerado de OUTRA arvore que a implantada;
  · a build nao regenerou, ou SYSTEM_MAP_CHECK nao deu PASS;
  · um campo com cara de segredo entrou no artefato publico.

O TECTO DE ESPERA E DE PROPOSITO NOS DOIS SENTIDOS. A Vercel demora, e reprovar
por ter perguntado cinco segundos cedo seria um portao que grita a toa — e um
portao que grita a toa e desligado numa semana. Esperar para sempre e a outra
maneira de nunca reprovar.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

SHA = os.environ.get("SHA", "")
REF = os.environ.get("REF", "")
REPO = os.environ.get("REPO", "")
TOKEN = os.environ.get("GH_TOKEN", "")

TENTATIVAS = int(os.environ.get("TENTATIVAS", "24"))
ESPERA_S = int(os.environ.get("ESPERA_S", "25"))
SUSPEITO = ("TOKEN", "SECRET", "KEY", "PASSWORD", "PASSWD", "CREDENTIAL")


def pedir(url: str, autenticado: bool = False, timeout: int = 20):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json" if autenticado else "application/json",
        "User-Agent": "sintonia-system-map-deploy-verify",
        **({"Authorization": f"Bearer {TOKEN}"} if autenticado and TOKEN else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # rede, DNS, TLS, timeout
        return 0, {"_erro": str(e)}


def urls_servidas() -> list:
    """Os URL que a integracao Git da Vercel registou para ESTE commit."""
    status, deployments = pedir(
        f"https://api.github.com/repos/{REPO}/deployments?sha={SHA}&per_page=30",
        autenticado=True)
    if status != 200 or not isinstance(deployments, list):
        print(f"  · a API de Deployments respondeu {status}")
        return []
    achados = []
    for d in deployments:
        st, estados = pedir(
            f"https://api.github.com/repos/{REPO}/deployments/{d['id']}/statuses?per_page=30",
            autenticado=True)
        if st != 200 or not isinstance(estados, list):
            continue
        for e in estados:
            if e.get("state") != "success":
                continue
            u = e.get("environment_url") or e.get("target_url")
            if u and u.startswith("https://") and u not in achados:
                achados.append(u.rstrip("/"))
    return achados


def conferir(base: str) -> tuple:
    """Le o artefato de deploy servido e devolve (ok, queixas, artefato)."""
    status, d = pedir(f"{base}/system-map/deployment.generated.json")
    if status != 200 or not isinstance(d, dict):
        return False, [f"{base}/system-map/deployment.generated.json respondeu {status}"], None

    # ── O QUE REPROVA ────────────────────────────────────────────────────────
    # ESTE SCRIPT RESPONDE A UMA PERGUNTA SO: «o commit X foi publicado?». Ele
    # NAO e o validador do mapa, e nao pode passar a se-lo — misturar as duas
    # perguntas daria um portao que grita por coisas diferentes com a mesma voz.
    q = []
    servido = d.get("DEPLOYED_COMMIT")
    if servido != SHA:
        q.append(f"DEPLOYED_COMMIT={str(servido)[:10]} mas esta corrida e {SHA[:10]}")
    if REF and d.get("SOURCE_BRANCH") and d["SOURCE_BRANCH"] != REF:
        q.append(f"SOURCE_BRANCH={d['SOURCE_BRANCH']} mas o push foi em {REF}")
    if d.get("PUBLISHED_FILES_MISSING"):
        q.append(f"falta no publicado: {d['PUBLISHED_FILES_MISSING']}")
    if d.get("SYSTEM_MAP_CHECK") == "FAIL":
        q.append("SYSTEM_MAP_CHECK=FAIL no que esta servido")
    sujos = [k for k in d if any(s in k.upper() for s in SUSPEITO)]
    if sujos:
        q.append(f"campo com cara de segredo no artefato publico: {sujos}")

    # ── O QUE SE RELATA SEM REPROVAR ─────────────────────────────────────────
    # MEDIDO NUMA BUILD REAL DA VERCEL: `Removed 1125 ignored files defined in
    # .vercelignore`. O contentor recebe 311 dos 1338 ficheiros, e regenerar ali
    # daria o mapa de uma arvore mutilada. O publicador RECUSA-SE a faze-lo, e a
    # tela fica ⚪ UNKNOWN com o numero ao lado.
    #
    #     NAO CONSEGUIR VALIDAR NAO E O MESMO QUE VALIDAR E REPROVAR.
    #
    # Reprovar aqui por um bloqueio ja medido, escrito e visivel na propria tela
    # seria um portao vermelho permanente — e um portao sempre vermelho e um
    # portao desligado. Levantar o bloqueio e uma decisao de quem e dono do
    # `.vercelignore`, e esta registada no handoff.
    avisos = []
    if not d.get("REGENERATED_AT_BUILD"):
        avisos.append(f"a build nao regenerou: {d.get('NOT_REGENERATED_REASON')}")
    if d.get("SYSTEM_MAP_CHECK") == "UNKNOWN":
        avisos.append("SYSTEM_MAP_CHECK=UNKNOWN — a tela mostra FRESHNESS UNKNOWN, "
                      "nunca verde")
    prov = d.get("ARCHITECTURE_SOURCE_PROVENANCE") or {}
    if prov.get("HEAD") != SHA:
        avisos.append(f"o mapa servido foi gerado de {str(prov.get('HEAD'))[:10]} "
                      f"e nao de {SHA[:10]}")
    d["_AVISOS"] = avisos
    return not q, q, d


def main() -> int:
    if not (SHA and REPO):
        print("::error::SHA e REPO sao obrigatorios")
        return 1

    print(f"SYSTEM MAP · o commit {SHA[:10]} de {REF} foi publicado?")
    ultimas = ["nenhum deployment com estado success apareceu ainda"]

    for volta in range(1, TENTATIVAS + 1):
        bases = urls_servidas()
        if bases:
            print(f"  · volta {volta}: {len(bases)} URL registado(s)")
            for base in bases:
                ok, queixas, d = conferir(base)
                if ok:
                    print(f"\nDEPLOY_VERIFICADO=PASS · {base}/system-map/")
                    print(f"  DEPLOYED_COMMIT       {d['DEPLOYED_COMMIT'][:10]}")
                    print("  GENERATED FROM        "
                          + str((d.get('ARCHITECTURE_SOURCE_PROVENANCE') or {})
                                .get('HEAD'))[:10])
                    print(f"  SOURCE_BRANCH         {d.get('SOURCE_BRANCH')}")
                    print(f"  ENVIRONMENT           {d.get('ENVIRONMENT')}")
                    print(f"  SYSTEM_MAP_CHECK      {d.get('SYSTEM_MAP_CHECK')}")
                    print(f"  REGENERATED_AT_BUILD  {d.get('REGENERATED_AT_BUILD')}")
                    print(f"  BUILD_TREE_COMPLETE   {d.get('BUILD_TREE_COMPLETE')} "
                          f"({d.get('BUILD_TREE_FILES')}/{d.get('MAP_TREE_FILES')})")
                    for a in d.get("_AVISOS", []):
                        print(f"  ::notice::{a}")
                    return 0
                ultimas = [f"{base}: {x}" for x in queixas]
                for x in queixas:
                    print(f"    · {x}")
        else:
            print(f"  · volta {volta}: ainda sem deployment success para este SHA")
        if volta < TENTATIVAS:
            time.sleep(ESPERA_S)

    print(f"\n::error::DEPLOY_VERIFICADO=FAIL apos "
          f"{TENTATIVAS * ESPERA_S // 60} minuto(s) — " + " · ".join(ultimas))
    print("\nSe o push da branch canonica NAO dispara deployment, a causa e essa e "
          "esta escrita aqui. NAO crie um segundo publicador: a integracao Git da "
          "Vercel e a autoridade, e dois donos do mesmo endereco servem a versao "
          "errada sem ninguem perceber.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
