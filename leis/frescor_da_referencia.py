#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O FRESCOR DA REFERENCIA — quao velho pode estar o que a Intelligence consulta.

    python3 leis/frescor_da_referencia.py --json                 # todas as fontes do livro
    python3 leis/frescor_da_referencia.py --json --hoje=2026-10-02

D117.4 (dono, 27/09):

    guardar a data da EDICAO e a data da ULTIMA CHECAGEM BEM-SUCEDIDA;
    14 dias sem checagem -> PODE_ESTAR_DESATUALIZADO;
    30 dias sem checagem -> as autorizacoes passam a «a confirmar».
    CONTA-SE DESDE A ULTIMA CHECAGEM — nao desde a edicao.

D117.6: a obrigacao de CONSULTAR a versao e tratar a desatualizacao e do
contrato da ferramenta de Intelligence. Esta peca e o que ela consulta: uma
funcao pura (`estado_frescor`) e a leitura do livro que lhe da os dois tempos
(`checagens_do_livro`). Um dono so para «quando foi a ultima checagem ok»: o
corredor da coleta (`coleta/italy_recurrent_collect.mjs`) pergunta AQUI para
decidir a cadencia, e nao le o livro por conta propria.

PORQUE A CONTA E DESDE A CHECAGEM, E NAO DESDE A EDICAO
-------------------------------------------------------
Uma edicao de 14/09 checada ontem e reencontrada igual esta EM DIA: a fonte
nao publicou nada novo, e nos sabemos disso porque olhamos. Uma edicao de
ontem que ninguem voltou a olhar ha 20 dias PODE estar velha. A idade do
documento nao diz se o sabemos atual; a idade do OLHAR diz.

    EDICAO VELHA != DADO DESATUALIZADO.
    CHECAGEM VELHA  = NAO SABEMOS SE MUDOU.

O QUE CONTA COMO CHECAGEM BEM-SUCEDIDA
--------------------------------------
Uma observacao do livro com `HEALTH_STATE = HEALTHY` — inclui `SEEN_AGAIN`
(olhou-se e nada mudou: e checagem, e das boas). NAO conta `FAILED`: bater na
porta e cair nao e olhar. Sem nenhuma, a resposta e `NAO_SEI`, e as
autorizacoes ficam «a confirmar» — ausencia de checagem nunca vira «em dia».

O QUE ELE NAO FAZ
-----------------
Nao vai a rede, nao escreve no livro, nao decide cadencia (isso e
`regras/cadencia_da_referencia.mjs`), nao esconde o numero: devolve a idade
AO LADO do estado, para quem mostrar poder por a data ao lado do numero.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAO_SEI = "NAO SEI"

# Os limiares da D117.4. Dias INTEIROS desde a ultima checagem ok.
DIAS_PODE_ESTAR_DESATUALIZADO = 14
DIAS_AUTORIZACOES_A_CONFIRMAR = 30

EM_DIA = "EM_DIA"
PODE_ESTAR_DESATUALIZADO = "PODE_ESTAR_DESATUALIZADO"
ESTADO_NAO_SEI = "NAO_SEI"
ESTADOS_FRESCOR = (EM_DIA, PODE_ESTAR_DESATUALIZADO, ESTADO_NAO_SEI)

AUTORIZACOES_VALEM_NA_EDICAO = "VALEM_NA_EDICAO"
AUTORIZACOES_A_CONFIRMAR = "A_CONFIRMAR"

SAUDAVEL = "HEALTHY"


def _dia(v):
    """`AAAA-MM-DD` (ou um instante ISO) -> date. None/vazio -> None."""
    if v is None or str(v).strip() in ("", NAO_SEI, "UNKNOWN", "None"):
        return None
    return _dt.date.fromisoformat(str(v).strip()[:10])


def estado_frescor(edicao_data, ultima_checagem_ok, hoje) -> dict:
    """A regra 14/30, pura. Devolve sempre os mesmos campos.

    `edicao_data`        a data da edicao que a fonte provou (ex.: 2026-09-14).
    `ultima_checagem_ok` o dia (ou instante) da ultima checagem bem-sucedida.
    `hoje`               o dia de referencia — entra por argumento: uma funcao
                         pura nao le o relogio.
    """
    h = _dia(hoje)
    if h is None:
        raise ValueError("hoje e obrigatorio: sem data de referencia nao ha idade")
    ed = _dia(edicao_data)
    ck = _dia(ultima_checagem_ok)
    base = {
        "EDICAO_DATA": ed.isoformat() if ed else NAO_SEI,
        "ULTIMA_CHECAGEM_OK": ck.isoformat() if ck else NAO_SEI,
        "HOJE": h.isoformat(),
        "LIMIARES": {"PODE_ESTAR_DESATUALIZADO": DIAS_PODE_ESTAR_DESATUALIZADO,
                     "AUTORIZACOES_A_CONFIRMAR": DIAS_AUTORIZACOES_A_CONFIRMAR},
        "CONTA_DESDE": "ULTIMA_CHECAGEM_OK",
    }
    if ck is None:
        return dict(base, DIAS_DESDE_A_CHECAGEM=NAO_SEI, ESTADO_FRESCOR=ESTADO_NAO_SEI,
                    AUTORIZACOES=AUTORIZACOES_A_CONFIRMAR,
                    PORQUE="nenhuma checagem bem-sucedida conhecida: nao se sabe se "
                           "a edicao ainda e a atual")
    dias = (h - ck).days
    if dias < 0:
        # Checagem «no futuro» e relogio partido, nao frescura.
        return dict(base, DIAS_DESDE_A_CHECAGEM=dias, ESTADO_FRESCOR=ESTADO_NAO_SEI,
                    AUTORIZACOES=AUTORIZACOES_A_CONFIRMAR,
                    PORQUE="a checagem e posterior a hoje: relogio inconsistente, "
                           "nao prova frescura")
    if dias >= DIAS_AUTORIZACOES_A_CONFIRMAR:
        return dict(base, DIAS_DESDE_A_CHECAGEM=dias, ESTADO_FRESCOR=PODE_ESTAR_DESATUALIZADO,
                    AUTORIZACOES=AUTORIZACOES_A_CONFIRMAR,
                    PORQUE="%d dias sem checagem ok (>= %d): autorizacoes a confirmar"
                           % (dias, DIAS_AUTORIZACOES_A_CONFIRMAR))
    if dias >= DIAS_PODE_ESTAR_DESATUALIZADO:
        return dict(base, DIAS_DESDE_A_CHECAGEM=dias, ESTADO_FRESCOR=PODE_ESTAR_DESATUALIZADO,
                    AUTORIZACOES=AUTORIZACOES_VALEM_NA_EDICAO,
                    PORQUE="%d dias sem checagem ok (>= %d)"
                           % (dias, DIAS_PODE_ESTAR_DESATUALIZADO))
    return dict(base, DIAS_DESDE_A_CHECAGEM=dias, ESTADO_FRESCOR=EM_DIA,
                AUTORIZACOES=AUTORIZACOES_VALEM_NA_EDICAO,
                PORQUE="checada com sucesso ha %d dia(s)" % dias)


def checagens_do_livro(observacoes) -> dict:
    """`{SOURCE_ID: {"ULTIMA_CHECAGEM_OK": instante, "EDICAO_DATA": dia}}`.

    ULTIMA_CHECAGEM_OK = o maior `CAPTURED_AT` entre as observacoes HEALTHY.
    EDICAO_DATA        = a maior `SOURCE_DATE_ISO` entre as observacoes HEALTHY
                         (a edicao mais recente que a fonte provou). Sem ela: NAO SEI.
    Fonte so com FAILED aparece com os dois em NAO SEI — foi tentada, nao olhada.
    """
    fora = {}
    for o in observacoes:
        sid = o.get("SOURCE_ID")
        if not sid:
            continue
        linha = fora.setdefault(sid, {"ULTIMA_CHECAGEM_OK": None, "EDICAO_DATA": None})
        if o.get("HEALTH_STATE") != SAUDAVEL:
            continue
        cap = o.get("CAPTURED_AT")
        if cap and (linha["ULTIMA_CHECAGEM_OK"] is None or str(cap) > linha["ULTIMA_CHECAGEM_OK"]):
            linha["ULTIMA_CHECAGEM_OK"] = str(cap)
        ed = o.get("SOURCE_DATE_ISO")
        try:
            ed = _dia(ed)
        except ValueError:
            ed = None   # data de fonte ilegivel nao e edicao
        if ed and (linha["EDICAO_DATA"] is None or ed.isoformat() > linha["EDICAO_DATA"]):
            linha["EDICAO_DATA"] = ed.isoformat()
    return fora


def frescor_das_fontes(observacoes, hoje) -> dict:
    return {sid: dict(estado_frescor(c["EDICAO_DATA"], c["ULTIMA_CHECAGEM_OK"], hoje),
                      ULTIMA_CHECAGEM_OK_INSTANTE=c["ULTIMA_CHECAGEM_OK"] or NAO_SEI)
            for sid, c in sorted(checagens_do_livro(observacoes).items())}


def ler_livro(caminho):
    """O livro NDJSON. Ausente -> FileNotFoundError (nao e «zero checagens»)."""
    if not os.path.isfile(caminho):
        raise FileNotFoundError("livro de observacoes ausente: %s" % caminho)
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def hoje_em_roma() -> str:
    from zoneinfo import ZoneInfo
    return _dt.datetime.now(ZoneInfo("Europe/Rome")).date().isoformat()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    hoje = next((a.split("=", 1)[1] for a in argv if a.startswith("--hoje=")), None) or hoje_em_roma()
    raiz = os.environ.get("ITALY_OPS_ROOT") or RAIZ
    livro = next((a.split("=", 1)[1] for a in argv if a.startswith("--livro=")), None) \
        or os.path.join(raiz, "data", "collection-ledger", "italy", "observations.ndjson")
    fontes = frescor_das_fontes(ler_livro(livro), hoje)
    if "--json" in argv:
        print(json.dumps({"CONTRATO": "FRESCOR_DA_REFERENCIA/v1", "HOJE": hoje,
                          "LIVRO": os.path.relpath(livro, raiz), "FONTES": fontes},
                         ensure_ascii=False))
    else:
        for sid, f in fontes.items():
            print("%-13s %-25s edicao %-10s checagem %-10s %s dias · autorizacoes %s"
                  % (sid, f["ESTADO_FRESCOR"], f["EDICAO_DATA"], f["ULTIMA_CHECAGEM_OK"],
                     f["DIAS_DESDE_A_CHECAGEM"], f["AUTORIZACOES"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
