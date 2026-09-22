#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PONTE DO CURATOR, PROVADA EM RUNTIME — nos dois sentidos.

    UM CENSO HISTORICO VERDE COM PONTE FUTURA MORTA E UMA FALHA, NAO UM PASSE.

O censo diz o que ja aconteceu. Isto diz o que ACONTECE quando o bot escreve
uma linha nova: se ela atravessa ate ao portao, ou se morre a meio do cano.
Sao coisas diferentes, e so a segunda prova que o encanamento esta ligado.

O caminho inteiro, medido a cada degrau:

    o bot escreve READY no livro dele
      -> a ponte le o HEAD do bot (nao um commit escrito a mao)
      -> reconcilia por SOURCE_ID, com a prova
      -> escreve no livro canonico por acrescimo
      -> traz a PROVA junto com o estado
      -> collection_gate ve, e decide sozinho

E O SENTIDO NEGATIVO, QUE E TAO IMPORTANTE COMO O POSITIVO: uma fonte que o
bot bloqueia, ou que o bot promove SEM prova de canario, tem de NAO atravessar.
Uma ponte que deixa passar tudo nao e uma ponte — e um buraco na parede.

    SOURCE_CURATOR_READY != COLLECTION_ELIGIBLE

O bot alimenta conhecimento. Quem decide a elegibilidade e `collection_gate`,
lendo a regua. Nada aqui escreve elegibilidade, e nada aqui toca no bot: o
supervisor dele continua a correr, e o livro dele so se le, congelado.

BANCADA DESCARTAVEL. O livro canonico REAL nunca e tocado por este ficheiro:
copia-se para uma pasta temporaria e e la que tudo acontece (molde:
test_ready_split.py). Zero rede.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))

import collection_gate as CG        # noqa: E402
import lifecycle as LC              # noqa: E402
import ready_split as RS            # noqa: E402
import reconciliar_livros as R      # noqa: E402

SAIDA = RAIZ / "curadoria" / "PONTE-CURADOR-PROOF-V1.json"

# As tres fontes da prova. Nomes fora do espaco real (T99) para que, se algum
# dia escaparem para um livro a serio, se vejam a olho.
POSITIVA = "IT-T99-001"      # o bot prova os 4 passos  -> tem de atravessar
BLOQUEADA = "IT-T99-002"     # o bot bloqueia           -> NAO pode atravessar
SEM_PROVA = "IT-T99-003"     # o bot promove sem prova  -> NAO pode atravessar


def agora_mais(segundos: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=segundos)).isoformat()


def _linha(sid, de, para, quando, ref=None, reason="prova da ponte"):
    return {"SOURCE_ID": sid, "PREVIOUS_STATE": de, "NEW_STATE": para,
            "REASON": reason, "EVIDENCE_REF": ref, "OBSERVED_AT": quando,
            "OWNER": LC.OWNER_CURATOR, "VERSION": LC.CONTRATO}


def _prova_de_canario(ref, sid, item, alvos=9):
    """Uma prova com os QUATRO passos — a mesma forma que o worker escreve."""
    return {"EVIDENCE_REF": ref, "SOURCE_ID": sid, "ETAPA": "CANARY",
            "OBSERVED_AT": agora_mais(1),
            "DADOS": {"PASS": True, "CLASSE": "OK", "DETAIL_GATE_PASSED": True,
                      "ALVOS_DESCOBERTOS": alvos, "DETAIL_ENUMERATED": alvos,
                      "ITEM_ABERTO": {"URL": item, "HTTP": 200, "BYTES": 64000,
                                      "HTML_KIND": "CONTENT",
                                      "CAPA_OU_MATERIA": "MATERIA_PROVAVEL",
                                      "LINKS": 40, "PARAGRAPH_CHARACTERS": 4200,
                                      "NON_WHITESPACE_CHARACTERS": 9000}}}


def _contrato(sid, index):
    return {"SOURCE_ID": sid, "CANONICAL_ENTRY_URL": index,
            "ACQUISITION": {"STRATEGY": "HTML_LINK_DISCOVERY", "INDEX_URL": index,
                            "MAX_TARGETS": 10},
            "SOURCE_CONTRACT_VERSION": "v1", "SOURCE_CONTRACT_HASH": "h99" + sid[-3:]}


def livro_do_bot_com_trabalho_novo(base: dict | None) -> tuple[dict, dict, dict]:
    """O snapshot REAL do bot + tres linhas novas, DEPOIS do corte.

    Nao se inventa um bot: parte-se do livro verdadeiro dele e acrescenta-se o
    que ele escreveria a seguir. Assim o que se prova e o cano, com a carga
    real la dentro.
    """
    base = json.loads(json.dumps(base or {"DATASET": "LIFECYCLE-LEDGER-V1",
                                          "CONTRATO": LC.CONTRATO, "LEI": "t",
                                          "TRANSICOES": []}))
    t0, t1 = agora_mais(0), agora_mais(2)
    ref_ok = "EV-%s-CANARY-NOVA" % POSITIVA
    base["TRANSICOES"] += [
        _linha(POSITIVA, None, LC.CANARY_PENDING, t0),
        _linha(POSITIVA, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, t1, ref_ok,
               "canario resolveu, abriu um item real e passou o gate de detalhe"),
        _linha(BLOQUEADA, None, LC.CAPABILITY_BLOCK, t1, "CARACT:sem adaptador",
               "aquisicao impossivel com o que a casa tem"),
        _linha(SEM_PROVA, None, LC.CANARY_PENDING, t0),
        _linha(SEM_PROVA, LC.CANARY_PENDING, LC.READY_FOR_COLLECTION, t1,
               "MISSAO-04:curadoria/READY-FOR-COLLECTION-V1.json@959ae46a",
               "promovida citando um ficheiro de missao, nao um canario"),
    ]
    evid = {ref_ok: _prova_de_canario(
        ref_ok, POSITIVA, "https://www.exemplo-agro.it/notizie/peronospora-vite-settembre-2026/")}
    contratos = {POSITIVA: _contrato(POSITIVA, "https://www.exemplo-agro.it/notizie/"),
                 SEM_PROVA: _contrato(SEM_PROVA, "https://www.exemplo2-agro.it/news/")}
    return base, evid, contratos


def correr() -> dict:
    tmp = tempfile.TemporaryDirectory()
    banco = Path(tmp.name)
    antes_livro, antes_evid, antes_contr = LC.LIVRO, RS.EVIDENCIA, RS.CONTRATOS
    antes_saida, antes_evid_a = R.SAIDA, R.EVIDENCIA_A
    try:
        # 1. bancada: copia do estado REAL desta arvore.
        shutil.copy(antes_livro, banco / "LEDGER.json")
        shutil.copy(antes_evid, banco / "EVIDENCE.json")
        if antes_contr.exists():
            shutil.copy(antes_contr, banco / "CONTRATOS.json")
        LC.LIVRO = banco / "LEDGER.json"
        RS.EVIDENCIA = R.EVIDENCIA_A = banco / "EVIDENCE.json"
        RS.CONTRATOS = banco / "CONTRATOS.json"
        R.SAIDA = banco / "RECONCILIACAO.json"

        ctx = R.carregar_contexto()
        if not ctx["C"]:
            raise SystemExit("o livro do bot nao se le por git show %s" % R.REF_C)

        # 2. o portao ANTES — a pergunta feita a quem manda.
        elegiveis_antes = set(CG.elegiveis())
        estado_antes = {s: LC.estado_de(s) for s in (POSITIVA, BLOQUEADA, SEM_PROVA)}

        # 3. o bot escreve trabalho NOVO, depois do corte.
        livro_c, evid_c, contr_c = livro_do_bot_com_trabalho_novo(ctx["C"])
        ctx["C"] = livro_c
        ctx["EVIDENCIA_C"] = dict(ctx.get("EVIDENCIA_C") or {}, **evid_c)
        ctx["CONTRATOS_C"] = dict(ctx.get("CONTRATOS_C") or {}, **contr_c)
        # o contrato tem de existir DESTE lado: sem rota, nao ha primeiro passo.
        contratos_locais = RS._contratos()
        contratos_locais.update(contr_c)
        RS.CONTRATOS.write_text(
            json.dumps({"DATASET": "italy_contracts_curator",
                        "FONTES": list(contratos_locais.values())},
                       ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        # 4. a ponte atravessa.
        doc = R.censo(ctx)
        aplicado = R.aplicar(doc, ctx)

        # 5. o portao DEPOIS — e ele que decide, nao nos.
        elegiveis_depois = set(CG.elegiveis())
        linhas = {l["SOURCE_ID"]: l for l in doc["LINHAS"]}
        veredito = {s: CG.avaliar(s) for s in (POSITIVA, BLOQUEADA, SEM_PROVA)}

        # 6. idempotencia: a MESMA leva outra vez nao mexe em nada.
        ctx2 = R.carregar_contexto()
        ctx2["C"], ctx2["EVIDENCIA_C"] = livro_c, ctx["EVIDENCIA_C"]
        ctx2["CONTRATOS_C"] = ctx["CONTRATOS_C"]
        doc2 = R.censo(ctx2)
        segunda = R.aplicar(doc2, ctx2)

        p = {
            "DATASET": "PONTE-CURADOR-PROOF-V1",
            "LEI": ("o trabalho novo do bot atravessa ate ao portao; o bloqueado e o "
                    "promovido sem prova NAO atravessam; a elegibilidade e sempre "
                    "decidida por collection_gate."),
            "GERADO_EM": LC.agora(),
            "BANCADA": "copia descartavel — o livro canonico real nao foi tocado",
            "BOT": {"BRANCH": R.BRANCH_C, "HEAD_LIDO_AGORA": R.REF_C,
                    "HEAD_DESCOBERTO_NAO_ESCRITO_A_MAO": R.REF_C == R.ref_do_bot(),
                    "SNAPSHOT": doc["BOT_SNAPSHOT"]},
            "SENTIDO_POSITIVO": {
                "SOURCE_ID": POSITIVA,
                "ESTADO_ANTES": estado_antes[POSITIVA],
                "ESTADO_DEPOIS": LC.estado_de(POSITIVA),
                "FINAL_DA_RECONCILIACAO": linhas[POSITIVA]["FINAL_STATE"],
                "PROVA_VEIO_JUNTO": ((RS._evidencias().get(
                    "EV-%s-CANARY-NOVA" % POSITIVA) or {}).get("IMPORTADO_DE") or {}).get("LIVRO"),
                "READY_RULE_NO_PORTAO": veredito[POSITIVA]["READY_RULE"],
                "COLLECTION_ELIGIBLE": veredito[POSITIVA]["COLLECTION_ELIGIBLE"],
                "PORQUE": veredito[POSITIVA]["PORQUE"],
                "ATRAVESSOU": (veredito[POSITIVA]["COLLECTION_ELIGIBLE"] is True
                               and POSITIVA in elegiveis_depois
                               and POSITIVA not in elegiveis_antes),
            },
            "SENTIDO_NEGATIVO": [
                {"SOURCE_ID": s, "ESTADO_DEPOIS": LC.estado_de(s),
                 "FINAL_DA_RECONCILIACAO": linhas[s]["FINAL_STATE"],
                 "COLLECTION_ELIGIBLE": veredito[s]["COLLECTION_ELIGIBLE"],
                 "MOTIVO": veredito[s]["MOTIVO"], "PORQUE": veredito[s]["PORQUE"],
                 "NAO_ATRAVESSOU": veredito[s]["COLLECTION_ELIGIBLE"] is False
                                   and s not in elegiveis_depois}
                for s in (BLOQUEADA, SEM_PROVA)
            ],
            "PORTAO": {
                "COLLECTION_ELIGIBLE_ANTES": len(elegiveis_antes),
                "COLLECTION_ELIGIBLE_DEPOIS": len(elegiveis_depois),
                "ENTRARAM": sorted(elegiveis_depois - elegiveis_antes),
                "SAIRAM": sorted(elegiveis_antes - elegiveis_depois),
            },
            "EVIDENCIA": aplicado["EVIDENCIA"],
            "TELEMETRIA_DA_PONTE": doc["TELEMETRIA_DA_PONTE"],
            "IDEMPOTENCIA": {
                "SEGUNDA_LEVA_APENDE": segunda["APENDIDAS"],
                "SEGUNDA_LEVA_IMPORTA_PROVAS": segunda["EVIDENCIA"]["PROVAS_IMPORTADAS"],
                "NO_OP": (segunda["APENDIDAS"] == 0
                          and segunda["EVIDENCIA"]["PROVAS_IMPORTADAS"] == 0),
            },
        }
        p["LEGACY_LEAK"] = doc["TELEMETRIA_DA_PONTE"]["LEGACY_LEAK"]
        p["PONTE_VIVA"] = (p["SENTIDO_POSITIVO"]["ATRAVESSOU"]
                           and all(n["NAO_ATRAVESSOU"] for n in p["SENTIDO_NEGATIVO"])
                           and p["IDEMPOTENCIA"]["NO_OP"]
                           and p["LEGACY_LEAK"] == 0)
        return p
    finally:
        LC.LIVRO, RS.EVIDENCIA, RS.CONTRATOS = antes_livro, antes_evid, antes_contr
        R.SAIDA, R.EVIDENCIA_A = antes_saida, antes_evid_a
        tmp.cleanup()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = correr()
    if "--escrever" in argv:
        SAIDA.write_text(json.dumps(p, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    pos, portao = p["SENTIDO_POSITIVO"], p["PORTAO"]
    print("BOT_HEAD_LIDO_AGORA        %s (descoberto: %s)"
          % (p["BOT"]["HEAD_LIDO_AGORA"], p["BOT"]["HEAD_DESCOBERTO_NAO_ESCRITO_A_MAO"]))
    print("POSITIVA %s  %s -> %s | regua %s | ELIGIVEL %s | ATRAVESSOU %s"
          % (pos["SOURCE_ID"], pos["ESTADO_ANTES"], pos["ESTADO_DEPOIS"],
             pos["READY_RULE_NO_PORTAO"], pos["COLLECTION_ELIGIBLE"], pos["ATRAVESSOU"]))
    for n in p["SENTIDO_NEGATIVO"]:
        print("NEGATIVA %s  %-22s | %-22s | NAO_ATRAVESSOU %s"
              % (n["SOURCE_ID"], n["ESTADO_DEPOIS"], n["MOTIVO"], n["NAO_ATRAVESSOU"]))
    print("PORTAO  ANTES %d  DEPOIS %d  ENTRARAM %s"
          % (portao["COLLECTION_ELIGIBLE_ANTES"], portao["COLLECTION_ELIGIBLE_DEPOIS"],
             portao["ENTRARAM"]))
    print("PROVAS_IMPORTADAS          %d" % p["EVIDENCIA"]["PROVAS_IMPORTADAS"])
    print("IDEMPOTENCIA_NO_OP         %s" % p["IDEMPOTENCIA"]["NO_OP"])
    print("LEGACY_LEAK                %d" % p["LEGACY_LEAK"])
    print("PONTE_VIVA                 %s" % p["PONTE_VIVA"])
    return 0 if p["PONTE_VIVA"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
