#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO DA PROMOCAO — pode este deployment ficar atras do endereco fixo?

    A ROTA /system-map/ ESTAR CERTA NAO E O DEPLOYMENT ESTAR CERTO.
    /system-map/ = 200  NAO PROVA  / = correcto.

O projecto Vercel serve o PORTAL INTEIRO. Promover um deployment do System Map
promove o site todo com ele. Foi assim que a promocao directa deixou de ser uma
opcao: a linha do mapa tinha-se separado do portal ha trinta commits, e po-la
no alias teria levado o portal de volta para antes da Label Intelligence.

Este portao mede isso ANTES, e recusa. Ele nao promove: quem promove e a
Vercel, que continua a ser a unica autoridade de deploy.

    ELE E A SEGUNDA OPINIAO, NAO A SEGUNDA MAO.

O QUE ELE REPROVA
-----------------
  · a branch candidata nao esta na autoridade declarada no contrato;
  · o commit servido no candidato nao e o esperado;
  · o mapa servido foi gerado de OUTRA arvore que a implantada;
  · /system-map/ nao responde 200 no candidato;
  · alguma rota do portal PIORA do canonico actual para o candidato;
  · nao se conhece alvo de rollback.

O QUE ELE NAO REPROVA, DE PROPOSITO
-----------------------------------
  · FRESHNESS UNKNOWN. A leitura da cabeca remota e feita pelo browser e pode
    nao estar disponivel. O modo de falha ja e fail-safe — pinta UNKNOWN, nunca
    verde. Um endereco nao se recusa por causa disso.
  · MAP RULES CHECK e COLETA CHECK vermelhos. Sao divida herdada, medida e
    visivel na tela. INHERITED RED != NEW DEPLOY REGRESSION.

    UNKNOWN != PASS, e por isso UNKNOWN tambem nao e FAIL.

USO
---
    python3 system-map/scripts/portao_da_promocao.py \
        --candidato https://<deployment>.vercel.app \
        --commit    <sha esperado>

Sai 0 se a promocao esta autorizada, 1 se nao. Nenhum segredo e lido: fala so
HTTP publico com o candidato e com o canonico.
"""

import argparse
import json
import os
import re
import ssl
import time
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTRATO = os.path.join(RAIZ, "system-map", "CANONICAL-PUBLICATION.json")


def buscar(url, timeout=30, tentativas=3):
    """Devolve (status, corpo em bytes). Status None = NAO CONSEGUI MEDIR.

    404 e uma medicao: a rota nao existe. Um socket que cai nao e medicao
    nenhuma, e os dois nunca se confundem aqui — se se confundissem, uma rede
    ma faria o portao gritar por regressoes que nao existem, e um portao que
    grita a toa e desligado numa semana.

        NAO CONSEGUI MEDIR  !=  MEDI E ESTA MAU.

    Nao medir tambem nao autoriza: quem chama trata None como «nao provado».
    """
    pedido = urllib.request.Request(url, headers={"User-Agent": "sintonia-portao-da-promocao"})
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(pedido, timeout=timeout,
                                        context=ssl.create_default_context()) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except Exception:
            if tentativa == tentativas - 1:
                return None, b""
            time.sleep(2 * (tentativa + 1))
    return None, b""


def recursos_de(html):
    """Os ficheiros que uma pagina servida manda o browser ir buscar.

    So caminhos do proprio site: um CDN de terceiros nao e nosso e nao e prova
    de nada sobre este deployment.
    """
    texto = html.decode("utf-8", "replace")
    achados = re.findall(r'(?:src|href)\s*=\s*["\']([^"\'>]+)["\']', texto)
    fora = set()
    for a in achados:
        a = a.strip()
        if not a or a.startswith(("http://", "https://", "//", "data:", "#", "mailto:")):
            continue
        if not a.split("?")[0].lower().endswith((".js", ".css")):
            continue
        fora.add("/" + a.lstrip("./").lstrip("/"))
    return fora


class Portao:
    def __init__(self):
        self.linhas = []
        self.reprovou = False

    def diz(self, ok, nome, detalhe):
        # None = nao mensuravel: nao aprova e nao reprova, mas ve-se.
        etiqueta = "PASS" if ok is True else ("FAIL" if ok is False else "UNKNOWN")
        if ok is False:
            self.reprovou = True
        self.linhas.append((etiqueta, nome, detalhe))

    def imprimir(self):
        largura = max(len(n) for _, n, _ in self.linhas)
        print()
        print("  SINTONIA · PORTAO DA PROMOCAO — o endereco e do produto")
        print("  " + "-" * (largura + 60))
        for etiqueta, nome, detalhe in self.linhas:
            print(f"  {etiqueta:<8}{nome:<{largura}}  {detalhe}")
        print("  " + "-" * (largura + 60))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidato", required=True, help="URL do deployment candidato")
    p.add_argument("--commit", required=True, help="SHA que se espera estar servido")
    p.add_argument("--rollback", default="", help="id do deployment canonico actual")
    args = p.parse_args()

    contrato = json.load(open(CONTRATO, encoding="utf-8"))
    canonico = "https://" + contrato["CANONICAL_HOST"]
    rota = contrato["CANONICAL_ROUTE"]
    candidato = args.candidato.rstrip("/")

    g = Portao()

    # 1. o que o candidato diz de si — escrito pela propria build
    status, corpo = buscar(f"{candidato}{rota}deployment.generated.json")
    if status != 200:
        g.diz(False, "CANDIDATO_DECLARA_SE", f"{rota}deployment.generated.json -> HTTP {status}")
        g.imprimir()
        print("\n  PROMOCAO NAO AUTORIZADA — o candidato nao diz o que serve\n")
        return 1
    dep = json.loads(corpo)
    g.diz(True, "CANDIDATO_DECLARA_SE", f"build {dep.get('BUILD_ID')} · {dep.get('ENVIRONMENT')}")

    # 2. a branch candidata tem autoridade para ser candidata
    ramo = dep.get("SOURCE_BRANCH")
    autoridade = contrato["PROMOTION_AUTHORITY_BRANCHES"]
    g.diz(ramo in autoridade, "BRANCH_TEM_AUTORIDADE",
          f"{ramo} · autorizadas: {', '.join(autoridade)}")

    # 3. o commit servido e o esperado — READY nao chega, tem de ser ESTE
    servido = dep.get("DEPLOYED_COMMIT") or ""
    g.diz(servido == args.commit, "COMMIT_SERVIDO_E_O_ESPERADO",
          f"servido {servido[:10]} · esperado {args.commit[:10]}")

    # 4. o mapa servido pertence a arvore implantada (nao e copia de outra linha)
    pertence = dep.get("MAP_BELONGS_TO_DEPLOYED_TREE")
    g.diz(pertence is True, "MAPA_E_DESTA_ARVORE",
          f"{dep.get('MAP_BELONGS_PROOF') or 'sem prova declarada'}")

    # 5. a rota canonica abre no candidato
    status_mapa, _ = buscar(f"{candidato}{rota}")
    g.diz(status_mapa == 200, "ROTA_DO_MAPA_ABRE", f"{rota} -> HTTP {status_mapa}")

    # 6. NENHUMA rota do portal piora, e NENHUM recurso que o portal de hoje
    #    serve desaparece. Medir so o codigo HTTP da rota nao chega: o
    #    deployment do mapa sozinho devolvia 200 em /portale e ao mesmo tempo
    #    deixava de servir italy-label-intelligence.js. A rota respondia; a
    #    ferramenta tinha desaparecido.
    #
    #        A ROTA RESPONDER NAO E A PAGINA ESTAR INTEIRA.
    #
    #    Por isso a lista de recursos exigidos nao se escreve a mao: le-se do
    #    canonico servido, agora. O que o portal serve hoje e a regua do que o
    #    candidato tem de continuar a servir — e a regua actualiza-se sozinha.
    piores = []
    nao_medidas = []
    exigidos = set()
    for r in contrato["ROTAS_DO_PORTAL_QUE_NAO_PODEM_REGREDIR"]:
        sc, bc = buscar(f"{canonico}{r}")
        sn, bn = buscar(f"{candidato}{r}")
        antes_ok, depois_ok = (sc == 200), (sn == 200)
        if antes_ok and sn is None:
            nao_medidas.append(f"{r}: nao consegui medir o candidato")
        elif antes_ok and not depois_ok:
            piores.append(f"{r}: {sc} -> {sn}")
        elif antes_ok and depois_ok and len(bn) < len(bc) * 0.5:
            # metade do corpo a desaparecer nao e uma alteracao de texto.
            piores.append(f"{r}: corpo {len(bc)} -> {len(bn)} bytes")
        if antes_ok:
            exigidos |= recursos_de(bc)
    total_rotas = len(contrato["ROTAS_DO_PORTAL_QUE_NAO_PODEM_REGREDIR"])
    if piores:
        g.diz(False, "PORTAL_NAO_REGRIDE", "; ".join(piores))
    elif nao_medidas:
        g.diz(None, "PORTAL_NAO_REGRIDE", "; ".join(nao_medidas))
    else:
        g.diz(True, "PORTAL_NAO_REGRIDE", f"{total_rotas} rotas iguais ou melhores")

    perdidos, incertos = [], []
    for a in sorted(exigidos):
        st = buscar(f"{candidato}{a}")[0]
        if st is None:
            incertos.append(a)
        elif st != 200:
            perdidos.append(f"{a} ({st})")
    if perdidos:
        g.diz(False, "NENHUM_RECURSO_DESAPARECE",
              f"{len(perdidos)} em falta: {', '.join(perdidos[:4])}")
    elif incertos:
        g.diz(None, "NENHUM_RECURSO_DESAPARECE",
              f"{len(incertos)} nao medidos: {', '.join(incertos[:4])}")
    else:
        g.diz(True, "NENHUM_RECURSO_DESAPARECE",
              f"{len(exigidos)} recursos do canonico continuam servidos")

    # 7. sem alvo de rollback nao se toca no alias
    g.diz(bool(args.rollback), "ROLLBACK_TARGET_KNOWN", args.rollback or "nenhum indicado")

    # visivel, e fora da decisao: os vermelhos herdados e a frescura
    g.diz(None, "MAP_GATE_DESTA_BUILD", str(dep.get("SYSTEM_MAP_CHECK")))
    g.diz(None, "GATES_HERDADOS",
          "MAP RULES CHECK / COLETA CHECK — divida herdada, visivel na tela, "
          "fora desta decisao")

    # UNKNOWN numa CONDICAO nao e aprovacao. As duas ultimas linhas sao
    # informativas de proposito e ficam de fora desta conta.
    condicoes = [l for l in g.linhas if l[1] not in ("MAP_GATE_DESTA_BUILD", "GATES_HERDADOS")]
    por_provar = [n for e, n, _ in condicoes if e == "UNKNOWN"]

    g.imprimir()
    if por_provar and not g.reprovou:
        print("\n  PROMOCAO NAO AUTORIZADA — por provar: " + ", ".join(por_provar))
        print("  UNKNOWN NAO E PASS. Volte a correr quando a medicao for possivel.\n")
        return 1
    if g.reprovou:
        print("\n  PROMOCAO NAO AUTORIZADA\n")
        return 1
    print("\n  PROMOCAO AUTORIZADA — o alias pode passar a servir este deployment\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
