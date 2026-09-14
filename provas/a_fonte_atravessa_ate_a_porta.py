#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FONTE PROVADA ATRAVESSA — DO RECIBO DA COLETA ATE A PORTA.

    python3 provas/a_fonte_atravessa_ate_a_porta.py

    QUE OS SETE HISTORICOS PASSEM A PODER SER RECONSTRUIDOS
    NAO E A PROVA. A PROVA E O FORWARD.

Esta prova NAO le o corpus de producao e NAO escreve nele. Ela monta uma
coleta inteira num sitio descartavel — fonte, corrida, recibo, bytes — e
segue A MESMA UNIDADE por todos os estagios, exigindo que a identidade que
sai no fim seja a que entrou no principio.

O QUE ELA TEM DE APANHAR
------------------------
Uma correcao que so funcione sobre os 7 ficheiros que ja ca estao seria uma
correcao sobre o passado. O buraco era FORWARD: e no forward que ele tem de
fechar.
"""
import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402
from coleta import italy_executor as ixec  # noqa: E402
from leis import artefato as art  # noqa: E402

SAIDA = "data/derivados/FONTE-ATRAVESSA-FORWARD-V1.json"

# A fonte da encenacao. NAO existe no catalogo real de proposito: se a prova
# passasse por o valor ja andar por ai, ela nao estaria a medir a travessia.
FONTE = "IT-T9-999"
OUTRA_FONTE = "IT-T9-888"
CORRIDA = "PROVA_RUN_FORWARD_0001"
OUTRA_CORRIDA = "PROVA_RUN_FORWARD_0002"


class TravessiaQuebrada(Exception):
    pass


def _livro(raiz, observacoes):
    """Escreve um recibo de coleta descartavel, no formato do de verdade."""
    p = os.path.join(raiz, ixec.LIVRO)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for o in observacoes:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return p


def _bytes(raiz, caminho_rel, conteudo):
    p = os.path.join(raiz, caminho_rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(conteudo)
    return p


def _observacao(**kw):
    base = {"RUN_ID": CORRIDA, "SOURCE_ID": FONTE,
            "SOURCE_URL": "https://exemplo.invalido/boletim",
            "CAPTURED_AT": "2026-09-12T00:00:00Z",
            "OBSERVATION_RESULT": "BASELINE_DOCUMENT",
            "RAW_OBJECT_CREATED": True}
    base.update(kw)
    return base


def _atravessa(raiz, caminho_rel, conteudo):
    """A unidade, estagio a estagio. Devolve o que cada um viu."""
    absoluto = _bytes(raiz, caminho_rel, conteudo)

    # RAW — refeito do disco, e a perguntar a fonte a quem a escreveu
    bruto = art.raw_do_disco(absoluto, raiz, COUNTRY_SCOPE="IT")
    achado = ixec.fonte_do_conteudo(bruto.SHA256, raiz=raiz)
    if achado["SOURCE_ID"]:
        from dataclasses import replace
        bruto = replace(bruto, SOURCE_ID=achado["SOURCE_ID"])

    # DERIVED — nasce do bruto, e herda a procedencia
    texto = os.path.join(raiz, "derivado.txt")
    with open(texto, "w", encoding="utf-8") as f:
        f.write("texto extraido")
    filho = art.derivado_de(
        bruto, texto, raiz, derivacao=art.TEXT_EXTRACTION,
        executor="prova-forward", executor_versao="1", pipeline_versao="1",
        run_id=CORRIDA, estado=art.TEXT_LAYER_PRESENT)

    # INGRESS — a traducao para a lingua de quem julga
    # ⚠️ OS DOIS CONJUNTOS, E NAO SO UM. A primeira versao desta prova passava
    # apenas `DO_COLETOR` e deixava de fora `DA_FICHA_PARA_A_PORTA`, onde vive
    # `ARTIFACT_TYPE`. Sem ele a porta nao sabe que especie de coisa esta a
    # julgar, cai em ESTAGIO_DESCONHECIDO e pergunta o tempo de um facto que
    # ainda nao foi extraido — uma regua que a producao NAO usa aqui.
    #
    #     UMA PROVA QUE ENTREGA MENOS DO QUE A PRODUCAO ENTREGA
    #     MEDE UM CAMINHO QUE NINGUEM PERCORRE.
    LEVADOS = ing.DO_COLETOR + ing.DA_FICHA_PARA_A_PORTA
    cru = {k: v for k, v in filho.para_json().items()
           if k in LEVADOS and v not in ing.NAO_E_AFIRMACAO}
    porta = ing.para_a_porta(cru)

    # ADMISSION — a porta, chamada a serio
    item = dict(porta, id="prova", texto="Lobesia botrana no vinhedo")
    decisao = adm.decidir(item, "T3")

    return {
        "SHA256": bruto.SHA256,
        "LEDGER": achado,
        "RAW": bruto.SOURCE_ID,
        "DERIVED": filho.SOURCE_ID,
        "INGRESS": porta.get("source_id"),
        "ADMISSION_REGRA": decisao.regra,
        "ADMISSION_SAIDA": decisao.resultado,
    }


# ══════════════════════════════════════════════════════════════════════════
# OS CENARIOS — o positivo, e todos os modos de mentir
# ══════════════════════════════════════════════════════════════════════════
def cenarios():
    fora = []

    def caso(nome, porque, fn):
        raiz = tempfile.mkdtemp(prefix="sintonia-forward-")
        try:
            fora.append(dict(fn(raiz), CASO=nome, PORQUE=porque))
        finally:
            shutil.rmtree(raiz, ignore_errors=True)

    # ── 1 · O POSITIVO ────────────────────────────────────────────────────
    def positivo(raiz):
        conteudo = b"%PDF-1.4 boletim da fonte nove"
        caminho = "data/collection-store/italy/sem-pista-nenhuma/doc.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, caminho, conteudo), raiz)
        _livro(raiz, [_observacao(RAW_SHA256=bruto.SHA256,
                                  RAW_PATH=caminho)])
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": FONTE, "TRILHA": t,
                "PASSA": (t["RAW"] == t["DERIVED"] == t["INGRESS"] == FONTE
                          and t["ADMISSION_REGRA"] != "origem")}
    caso("1 · a fonte provada atravessa os quatro estagios",
         "o caminho nao tem pista nenhuma da fonte; so o livro sabe", positivo)

    # ── 2 · SEM RECIBO, FICA UNKNOWN ──────────────────────────────────────
    def sem_recibo(raiz):
        conteudo = b"%PDF-1.4 ninguem colheu isto"
        caminho = "data/samples/IT-SOURCE-SAMPLES/IT-T3-008/amostra.pdf"
        _livro(raiz, [])
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": "UNKNOWN", "TRILHA": t,
                "PASSA": (not ing_prova(t["RAW"])
                          and t["ADMISSION_REGRA"] == "origem"
                          and t["ADMISSION_SAIDA"] == adm.NAO_SEI)}
    caso("2 · sem recibo continua UNKNOWN, e o caminho nao vota",
         "o caminho GRITA IT-T3-008 e tem de ser ignorado", sem_recibo)

    # ── 3 · O CAMINHO DISCORDA DO LIVRO ───────────────────────────────────
    def caminho_mente(raiz):
        conteudo = b"%PDF-1.4 o caminho diz uma coisa e o livro outra"
        caminho = "data/collection-store/italy/IT-T3-008/doc.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, caminho, conteudo), raiz)
        _livro(raiz, [_observacao(RAW_SHA256=bruto.SHA256, RAW_PATH=caminho)])
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": FONTE, "TRILHA": t,
                "O_CAMINHO_DIZIA": "IT-T3-008",
                "PASSA": t["RAW"] == FONTE}
    caso("3 · o livro vence o caminho, e vence por o caminho nao ter voto",
         "nao ha desempate porque nao ha empate: o caminho nunca e lido",
         caminho_mente)

    # ── 4 · SENTINELA NO LIVRO NAO E IDENTIDADE ───────────────────────────
    def sentinela(raiz):
        conteudo = b"%PDF-1.4 o livro confessa que nao sabe"
        caminho = "data/collection-store/italy/qualquer/doc.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, caminho, conteudo), raiz)
        linhas = [_observacao(RAW_SHA256=bruto.SHA256, SOURCE_ID=s)
                  for s in ("NAO SEI", "", None, "NÃO SEI", "NAO_SE_APLICA")]
        _livro(raiz, linhas)
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": "UNKNOWN", "TRILHA": t,
                "PASSA": not ing_prova(t["RAW"])}
    caso("4 · sentinela no livro nao vira identidade",
         "'NAO SEI' e uma string verdadeira; um `if v:` promove-a", sentinela)

    # ── 5 · DUAS FONTES PARA O MESMO CONTEUDO ─────────────────────────────
    def conflito(raiz):
        conteudo = b"%PDF-1.4 duas fontes publicaram isto"
        caminho = "data/collection-store/italy/qualquer/doc.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, caminho, conteudo), raiz)
        _livro(raiz, [_observacao(RAW_SHA256=bruto.SHA256),
                      _observacao(RAW_SHA256=bruto.SHA256,
                                  SOURCE_ID=OUTRA_FONTE)])
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": "UNKNOWN + CONFLITO", "TRILHA": t,
                "PASSA": (not ing_prova(t["RAW"])
                          and t["LEDGER"]["CONFLITO"] == sorted(
                              [FONTE, OUTRA_FONTE]))}
    caso("5 · duas fontes para o mesmo conteudo nao se desempatam",
         "escolher em silencio entre duas verdades fabrica uma terceira",
         conflito)

    # ── 6 · RETRY E NOVA CORRIDA ──────────────────────────────────────────
    def retry(raiz):
        conteudo = b"%PDF-1.4 visto tres vezes"
        caminho = "data/collection-store/italy/qualquer/doc.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, caminho, conteudo), raiz)
        _livro(raiz, [
            _observacao(RAW_SHA256=bruto.SHA256),                    # 1a vez
            _observacao(RAW_SHA256=bruto.SHA256),                    # retry
            _observacao(RAW_SHA256=bruto.SHA256, RUN_ID=OUTRA_CORRIDA),
        ])
        t = _atravessa(raiz, caminho, conteudo)
        return {"ESPERADO": FONTE, "TRILHA": t,
                "OBSERVACOES": t["LEDGER"]["OBSERVACOES"],
                "PASSA": (t["RAW"] == FONTE
                          and t["LEDGER"]["OBSERVACOES"] == 3
                          and not t["LEDGER"]["CONFLITO"])}
    caso("6 · retry e nova corrida nao mudam a fonte nem a perdem",
         "NEW RUN != RETRY, e nenhuma das duas re-identifica a fonte", retry)

    # ── 7 · O CONTEUDO E A CHAVE, E NAO O NOME ────────────────────────────
    def outro_nome(raiz):
        conteudo = b"%PDF-1.4 mesmos bytes, outro nome, outra pasta"
        onde_colheu = "data/collection-store/italy/pasta-a/original.pdf"
        onde_esta = "data/outro/sitio/RENOMEADO-999.pdf"
        bruto = art.raw_do_disco(_bytes(raiz, onde_colheu, conteudo), raiz)
        _livro(raiz, [_observacao(RAW_SHA256=bruto.SHA256,
                                  RAW_PATH=onde_colheu)])
        t = _atravessa(raiz, onde_esta, conteudo)
        return {"ESPERADO": FONTE, "TRILHA": t,
                "PASSA": t["RAW"] == FONTE}
    caso("7 · o ficheiro mudou de nome e de pasta, e a fonte sobreviveu",
         "a chave sao os bytes; se fosse o caminho, isto perdia a fonte",
         outro_nome)

    return fora


def ing_prova(v):
    return v not in ing.NAO_E_AFIRMACAO and v != "NÃO SEI"


def main():
    casos = cenarios()
    falhas = [c for c in casos if not c["PASSA"]]
    art_json = {
        "SCHEMA": "sintonia.source-id-forward-crossing/1",
        "O_QUE_ISTO_E": (
            "A travessia FORWARD do SOURCE_ID provado, do recibo da coleta "
            "ate a porta, numa coleta encenada e descartavel."),
        "PORQUE_NAO_BASTAVA_O_HISTORICO": (
            "Que os 7 documentos antigos passem a poder ser reconstruidos "
            "prova uma correcao sobre o passado. O buraco era forward."),
        "FORWARD_EXECUTED": "YES",
        "SOURCE_ID_PRESERVED": "YES" if not falhas else "NO",
        "CASOS": casos,
        "FALHARAM": [c["CASO"] for c in falhas],
        "GENERATED_BY": "provas/a_fonte_atravessa_ate_a_porta.py",
    }
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(art_json, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("\n  A FONTE ATRAVESSA — prova forward")
    print("  " + "─" * 66)
    for c in casos:
        t = c["TRILHA"]
        print("  %s %s" % ("·" if c["PASSA"] else "✗", c["CASO"]))
        print("      livro=%-10s RAW=%-10s DERIVED=%-10s ingresso=%-10s"
              % (t["LEDGER"]["SOURCE_ID"], t["RAW"], t["DERIVED"],
                 t["INGRESS"]))
        print("      porta: regra=%s · saida=%s"
              % (t["ADMISSION_REGRA"], t["ADMISSION_SAIDA"]))
    print("\n  " + "─" * 66)
    print("  FORWARD_EXECUTED = YES · SOURCE_ID_PRESERVED = %s"
          % art_json["SOURCE_ID_PRESERVED"])
    print("  escrito: %s\n" % SAIDA)
    if falhas:
        raise TravessiaQuebrada("falharam: %s" % [c["CASO"] for c in falhas])
    return 0


if __name__ == "__main__":
    sys.exit(main())
