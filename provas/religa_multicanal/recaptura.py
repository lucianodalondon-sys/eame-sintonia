#!/usr/bin/env python
"""P3 — DUAS CORRIDAS SEGUIDAS SOBRE A MESMA ENTRADA NAO CRIAM RAW NOVO.

    O DESPERDICIO NAO E O FICHEIRO A MAIS: E O PEDIDO A MAIS.

O revisor do SCRAP deixou este ponto como «o mais facil de todos e eu nao o corri», e tinha razao nas
duas partes: e barato, e ninguem o tinha corrido. O criterio dele, literal:

    2 corridas seguidas nao criam RAW novo para bytes iguais.

Este medidor corre-o SEM REDE e SEM BANCO. O transporte e um leitor local que devolve sempre os mesmos
bytes e CONTA quantas vezes foi chamado; a Sala fica de fora (`pousar=False`). O que se mede e o
comportamento do livro `ALVOS-JA-COLHIDOS.ndjson` entre duas chamadas a `onda_linha.correr` com a
MESMA pasta-mae.

O QUE ESTE MEDIDOR NAO DIZ, e importa nao confundir com o que ele diz:

  · nao mede de-duplicacao de `raw_asset` no banco. A guarda desta casa e por ALVO PEDIDO
    (LINHA, URL) dentro de uma janela de 24 h, e nao por sha256 de bytes. Apagar uma captura repetida
    seria violar a D157 — cada captura e uma observacao. O que se evita e o PEDIDO.
  · logo, duas corridas fora da janela de 24 h VOLTAM a pedir, e isso e correcto, nao defeito.
  · o `CAPTURAS_REPETIDAS_BYTES` que a onda escreve e por FONTE e por CORRIDA. Nao e uma medida
    entre corridas, e nao deve ser lido como tal.

SAIDA: provas/religa_multicanal/RECAPTURA.json
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in (RAIZ / "ferramentas" / "big_collection", RAIZ):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import onda_linha as OL                                            # noqa: E402

ACT = "7445139302390382592"
# A FORMA E COPIADA DE tests/test_d24_video_de_pessoa.py, que e o HTML medido na pagina a valer.
# ⚠️ O `data-sources` leva aspas ESCAPADAS (`&quot;`), como a plataforma serve. A minha primeira versao
# usou aspas cruas e o extractor devolveu 0 cartoes — a prova mediu vazio por causa do molde, nao do
# codigo. Nao reinventar o molde: copiar o que ja esta medido.
PAGINA = (
    '<span>urn:li:activity:%s</span>'
    '<a href="https://www.linkedin.com/posts/acme-bollettino-vite-activity-%s-eYKi">ver</a>'
    '<video data-sources="[{&quot;src&quot;:&quot;https://dms.licdn.com/x/mp4-640p&quot;}]"'
    ' data-captions-url="https://dms.licdn.com/x/video-auto-caption-webvtt"'
    ' data-digitalmedia-asset-urn="urn:li:digitalmediaAsset:D4E05AQHdUfZSb0GSFA"'
    ' data-language="it"></video>' % (ACT, ACT)
)
LEGENDA = "1\n00:00:01,000 --> 00:00:03,000\nperonospora della vite: trattamento in settimana\n"


def leitor_local():
    """Transporte de mentira: bytes fixos por tipo de endereco, e CONTA os pedidos. ZERO rede.

    A legenda e um endereco diferente da pagina, e por isso o leitor distingue os dois — devolver a
    pagina como legenda faria a prova medir outra coisa."""
    chamadas = []

    def buscar(url, aceitar=None):
        chamadas.append(url)
        corpo = LEGENDA if str(url).endswith((".srt", ".vtt", "webvtt")) else PAGINA
        return {"STATUS": 200, "BYTES": corpo.encode("utf-8"), "ERRO": None,
                "CONTENT_TYPE": "text/html"}
    buscar.chamadas = chamadas
    return buscar


def _raw_no_livro(saida: Path) -> list:
    f = saida / OL.RAW_F
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def medir() -> dict:
    base = Path(tempfile.mkdtemp(prefix="recaptura-"))
    guardado = dict(os.environ)
    try:
        # LINKEDIN, e nao BUSCA. ⚠️ A linha BUSCA constroi TRANSPORTE REAL PROPRIO
        # (`linha_busca.transporte_real`) e ignora o `buscar` injectado: a primeira versao desta prova
        # usou BUSCA e foi a rede a valer, levando HTTP 403 do DuckDuckGo. O LINKEDIN respeita a
        # injeccao de ponta a ponta (so cai no transporte real se `buscar is None`).
        cand = [{"SOURCE_ID": "IT-T9-026", "TERRITORIO": "IT", "UNIVERSO": "T9",
                 "ALVO": {"PAGINA": "https://www.linkedin.com/company/acme/"}}]
        saida = base / "CICLO" / "LINKEDIN"

        b1 = leitor_local()
        rc1 = OL.correr("LINKEDIN", cand, saida, buscar=b1, pousar=False)
        raw1 = _raw_no_livro(saida)

        b2 = leitor_local()
        rc2 = OL.correr("LINKEDIN", cand, saida, buscar=b2, pousar=False)
        raw2 = _raw_no_livro(saida)

        estado2 = json.loads((saida / OL.ESTADO_F).read_text(encoding="utf-8"))
        vistos_antes = [f.get("ALVOS_VISTOS_ANTES") for f in estado2.get("FONTES", [])]

        novos = len(raw2) - len(raw1)
        shas1 = {r["SHA256"] for r in raw1}
        shas2 = {r["SHA256"] for r in raw2}
        # ⚠️ TRAVA CONTRA VERDE POR VAZIO. A 1.a versao desta prova deu PASS com 0 RAW nas duas
        # corridas: a linha falhou, nada foi colhido, e «0 novos» saiu de «0 total». Zero novo sobre
        # zero colhido nao prova guarda nenhuma — prova que a prova nao mediu.
        #
        #     UMA PROVA QUE PASSA POR NAO TER OLHADO NADA NAO E UMA PROVA QUE PASSOU.
        # ⚠️ O CRITERIO NAO E «ZERO PEDIDOS NA 2.a CORRIDA», e a minha primeira versao exigia isso e
        # deu FAIL a codigo correcto. A DESCOBERTA tem de ser pedida: sem ler a pagina da organizacao
        # nao se sabe que alvos existem hoje, e adivinhar seria pior que pedir. A guarda e por ALVO, e
        # o que ela promete e nao PEDIR O ALVO outra vez — que e o pedido caro, e o unico que se
        # multiplica por seis quando falha.
        #
        #     A GUARDA POUPA O PEDIDO DO ALVO, NAO O PEDIDO QUE DESCOBRE QUE O ALVO EXISTE.
        vistos = sum(int(v or 0) for v in vistos_antes)
        if not raw1:
            veredito = ("FAIL_MEDIU_VAZIO · a 1.a corrida colheu 0 RAW, logo nao ha recaptura a medir. "
                        "Corrigir a entrada da prova, NAO assinar PASS.")
        elif novos == 0 and vistos >= 1 and len(b2.chamadas) < len(b1.chamadas):
            veredito = ("PASS · a 2.a corrida nao criou RAW (%d), marcou %d alvo(s) VISTO_ANTES e baixou "
                        "de %d para %d pedido(s): poupou o pedido do alvo e da legenda dele"
                        % (novos, vistos, len(b1.chamadas), len(b2.chamadas)))
        else:
            veredito = ("FAIL · a 2.a corrida criou %d RAW, marcou %d VISTO_ANTES e fez %d pedido(s) "
                        "contra %d da 1.a" % (novos, vistos, len(b2.chamadas), len(b1.chamadas)))
        return {
            "PROVA": "P3 · duas corridas seguidas sobre a MESMA entrada local",
            "CRITERIO": "2 corridas seguidas nao criam RAW novo para bytes iguais",
            "REDE": "NENHUMA — transporte local, bytes fixos",
            "BANCO": "NENHUM — pousar=False",
            "RC_CORRIDA_1": rc1,
            "RC_CORRIDA_2": rc2,
            "RAW_DEPOIS_DA_1": len(raw1),
            "RAW_DEPOIS_DA_2": len(raw2),
            "RAW_NOVO_NA_2": novos,
            "SHA_DISTINTOS": len(shas1 | shas2),
            "BYTES_IGUAIS": shas1 == shas2 and len(shas1) == 1,
            "PEDIDOS_NA_1": len(b1.chamadas),
            "PEDIDOS_NA_2": len(b2.chamadas),
            "ALVOS_VISTOS_ANTES_NA_2": vistos_antes,
            "PEDIDOS_POUPADOS_NA_2": len(b1.chamadas) - len(b2.chamadas),
            "PORQUE_SOBRA_1_PEDIDO": ("a DESCOBERTA da pagina da organizacao. Sem ela nao se sabe que "
                                      "alvos existem hoje. A guarda e por ALVO, e o alvo nao foi pedido."),
            "TEXTO_ORIGEM_NO_LIVRO": sorted({str(r.get("TEXTO_ORIGEM")) for r in raw2}),
            "TEXTO_CARACTERES_NO_LIVRO": sorted({r.get("TEXTO_CARACTERES") for r in raw2}
                                                - {None}) or "campo ausente",
            "VEREDITO": veredito,
            "O_QUE_ISTO_NAO_MEDE": [
                "de-duplicacao de raw_asset por sha256 no banco: a guarda e por ALVO PEDIDO, nao por bytes",
                "corridas fora da janela de 24 h, que VOLTAM a pedir — e isso e correcto",
                "CAPTURAS_REPETIDAS_BYTES da onda, que e por FONTE e por CORRIDA, nao entre corridas",
            ],
        }
    finally:
        os.environ.clear()
        os.environ.update(guardado)


def main() -> int:
    r = medir()
    fora = Path(__file__).with_name("RECAPTURA.json")
    fora.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k in ("RAW_DEPOIS_DA_1", "RAW_DEPOIS_DA_2", "RAW_NOVO_NA_2", "PEDIDOS_NA_1", "PEDIDOS_NA_2",
              "BYTES_IGUAIS", "VEREDITO"):
        print("%-22s %s" % (k, r[k]))
    return 0 if r["VEREDITO"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
