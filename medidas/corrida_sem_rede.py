#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O LANCADOR INSTRUMENTADO — corre a porta canonica e MEDE a rede.

    NAO DEPENDER DO PORTAO PARA IMPEDIR A REDE.
    E NAO CONFIAR NA INTENCAO: INSTRUMENTAR.

PORQUE ISTO NAO E `--seco` OUTRA VEZ
-------------------------------------
`--so-a-porta` diz que nao chama o executor. Acreditar nisso e a mesma classe
de erro que ja custou uma medicao a esta casa: um ensaio que se dizia seco
deixou sair SETE pedidos de `robots.txt`, porque quem travou o coletor nao
travou a leitura de robots ao lado.

    UMA ETAPA QUE PROMETE NAO IR A REDE
    NAO E UMA MEDICAO DE QUE NAO FOI.

Aqui a saida e tapada e CONTADA. Se alguma etapa tentar sair, a tentativa fica
escrita com o endereco e com a pilha de chamadas — e a corrida para. Nao se
recolhe outra vez; reporta-se porque foi preciso.

O QUE CONTA COMO REDE, E O QUE NAO CONTA
-----------------------------------------
⚠️ LOOPBACK NAO E EGRESSO. A ligacao ao Postgres canonico (127.0.0.1) e a
bancada, nao a internet — trava-la nao tornava a prova mais honesta, tornava-a
impossivel. Fica MEDIDA e SEPARADA, com o porto, para que ninguem tenha de
acreditar em mim: quem ler o JSON ve exactamente a que se ligou.

    EGRESSO = socket para fora desta maquina.
    LOOPBACK = bancada, contado a parte, nunca somado ao egresso.

E OS FILHOS?
------------
Um `subprocess` novo nasce com um interpretador limpo e NAO herda estes
remendos. Por isso `subprocess.Popen` tambem e instrumentado: nao para
impedir, mas para que nenhum processo filho saia do censo em silencio. Um
filho por contar e um buraco do tamanho de todo o trabalho dele.

Uso:
    py medidas/corrida_sem_rede.py --saida=X.json -- <argumentos do orquestrador>
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import traceback

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

#: Os enderecos que sao BANCADA e nao internet.
LOOPBACK = {"127.0.0.1", "::1", "localhost", "0.0.0.0"}

CENSO = {
    "EGRESS_ATTEMPTS": [],     # tentativas de sair desta maquina
    "LOOPBACK_CONNECTS": [],   # ligacoes a bancada local
    "DNS_LOOKUPS": [],         # resolucoes de nome — indicio de intencao de sair
    "SUBPROCESSOS": [],        # filhos lancados, que nao herdam este remendo
}


class RedeProibida(RuntimeError):
    """Uma etapa tentou sair para a internet numa corrida declarada seca."""


def _pilha():
    """Quem chamou — sem as linhas deste ficheiro, que so fariam ruido."""
    fora = []
    for l in traceback.format_stack()[:-2]:
        if "corrida_sem_rede.py" in l:
            continue
        fora.append(" ".join(l.split()))
    return fora[-6:]


def _e_loopback(host):
    return str(host) in LOOPBACK or str(host).startswith("127.")


def instrumentar():
    """Poe os remendos. Devolve nada: o efeito e global, e e esse o ponto."""
    connect_real = socket.socket.connect
    connect_ex_real = socket.socket.connect_ex
    getaddrinfo_real = socket.getaddrinfo
    popen_real = subprocess.Popen.__init__

    def _decide(endereco, nome_da_chamada):
        host = endereco[0] if isinstance(endereco, (tuple, list)) and endereco else endereco
        porto = endereco[1] if isinstance(endereco, (tuple, list)) and len(endereco) > 1 else None
        registo = {"HOST": str(host), "PORTO": porto, "CHAMADA": nome_da_chamada,
                   "PILHA": _pilha()}
        if _e_loopback(host):
            CENSO["LOOPBACK_CONNECTS"].append(registo)
            return True
        CENSO["EGRESS_ATTEMPTS"].append(registo)
        return False

    def connect(self, endereco):
        if not _decide(endereco, "socket.connect"):
            raise RedeProibida(
                "REDE_PROIBIDA: tentou ligar a %r numa corrida instrumentada "
                "como seca. Nada foi recolhido." % (endereco,))
        return connect_real(self, endereco)

    def connect_ex(self, endereco):
        if not _decide(endereco, "socket.connect_ex"):
            raise RedeProibida("REDE_PROIBIDA: connect_ex a %r" % (endereco,))
        return connect_ex_real(self, endereco)

    def getaddrinfo(host, port, *a, **kw):
        # ⚠️ RESOLVER UM NOME NAO E LIGAR — e nao se trava por isso. Mas e a
        # INTENCAO de sair, e uma intencao que nao aparece no censo e uma
        # etapa que ninguem sabe que queria ir.
        if not _e_loopback(host):
            CENSO["DNS_LOOKUPS"].append({"HOST": str(host), "PORTO": port,
                                         "PILHA": _pilha()})
        return getaddrinfo_real(host, port, *a, **kw)

    def popen_init(self, args, *a, **kw):
        CENSO["SUBPROCESSOS"].append({
            "ARGV": [str(x) for x in (args if isinstance(args, (list, tuple)) else [args])][:12],
            "HERDA_O_REMENDO": False,
            "PILHA": _pilha()})
        return popen_real(self, args, *a, **kw)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
    subprocess.Popen.__init__ = popen_init


def main(argv):
    saida = None
    resto = []
    for a in argv:
        if a.startswith("--saida="):
            saida = a.split("=", 1)[1]
        else:
            resto.append(a)
    if resto and resto[0] == "--":
        resto = resto[1:]

    instrumentar()

    # A porta canonica corre DENTRO deste processo, para herdar os remendos.
    # Chama-la por `subprocess` daria um interpretador limpo — e a medicao
    # media o nada.
    sys.argv = ["orquestrador/orquestrador.py"] + resto
    codigo, erro = 0, None
    try:
        from orquestrador import orquestrador as orq
        codigo = orq.main()
    except RedeProibida as ex:
        codigo, erro = 3, "%s: %s" % (type(ex).__name__, ex)
        print("\n" + str(ex))
    except SystemExit as ex:                                    # noqa: BLE001
        codigo = int(ex.code or 0)
    except Exception as ex:                                     # noqa: BLE001
        codigo, erro = 1, "%s: %s" % (type(ex).__name__, ex)
        traceback.print_exc()

    censo = {
        "ARGUMENTOS": resto,
        "CODIGO_DE_SAIDA": codigo,
        "ERRO": erro,
        "NETWORK_ALLOWED": False,
        "NETWORK_REQUESTS": len(CENSO["EGRESS_ATTEMPTS"]),
        "EGRESS_ATTEMPTS": CENSO["EGRESS_ATTEMPTS"],
        "DNS_LOOKUPS_FORA": len(CENSO["DNS_LOOKUPS"]),
        "DNS_DETALHE": CENSO["DNS_LOOKUPS"][:20],
        "LOOPBACK_CONNECTS": len(CENSO["LOOPBACK_CONNECTS"]),
        "LOOPBACK_PORTOS": sorted({c["PORTO"] for c in CENSO["LOOPBACK_CONNECTS"]
                                   if c["PORTO"]}),
        "SUBPROCESSOS": len(CENSO["SUBPROCESSOS"]),
        "SUBPROCESSOS_DETALHE": CENSO["SUBPROCESSOS"][:20],
        "AVISO_DOS_FILHOS": "um subprocesso nasce com interpretador limpo e NAO "
                            "herda estes remendos; por isso sao contados, e a "
                            "corrida so e seca se esta lista estiver vazia ou "
                            "se cada filho for justificado por escrito",
    }
    print("\n=== CENSO DA REDE ===")
    for k in ("NETWORK_REQUESTS", "DNS_LOOKUPS_FORA", "LOOPBACK_CONNECTS",
              "LOOPBACK_PORTOS", "SUBPROCESSOS", "CODIGO_DE_SAIDA"):
        print("  %-22s %s" % (k, censo[k]))
    for t in CENSO["EGRESS_ATTEMPTS"][:5]:
        print("  !! EGRESSO %s:%s" % (t["HOST"], t["PORTO"]))
    for s in CENSO["SUBPROCESSOS"][:5]:
        print("  .. filho: %s" % " ".join(s["ARGV"])[:110])

    if saida:
        with open(saida, "w", encoding="utf-8") as fh:
            json.dump(censo, fh, indent=1, ensure_ascii=False)
        print("  escrito: %s" % saida)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
