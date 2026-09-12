#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O ADAPTER DA ITALIA — quatro traducoes, e nenhuma quinta.

POR QUE ISTO EXISTE
-------------------
A Italia colhe desde 2026-09. O livro tem 144 observacoes, 6 corridas, e
documentos preservados em `data/collection-store/italy/`. E `raw_asset` tem
ZERO linhas italianas, porque a coleta italiana nunca passou por
`coleta/ingresso.py`.

Nao foi por falta de porta: a porta existe, esta provada e tem um dono do RAW.
Foi porque entre o coletor italiano e a porta havia tres desencontros medidos,
e nenhum deles e uma questao de opiniao:

    o coletor e NODE           e a rota canonica corre executores com `sys.executable`
    o livro e NDJSON           e a colheita le `glob("*.json")` + `json.loads`
    o livro e APPEND-ONLY      e traria as 144 observacoes, nao as desta corrida

Este ficheiro e a peca que faltava, e ele NAO e um segundo coletor. Ele nao vai
a fonte, nao decide o que colher, nao julga nada e nao guarda nada. Ele traduz.

    AS QUATRO TRADUCOES

      1  corre o coletor em Node, com o RUN_ID que o T-04 cunhou
      2  le do livro APENAS as observacoes dessa corrida
      3  converte NDJSON  ->  uma lista JSON na pasta de colheita
      4  renomeia RAW_PATH  ->  STORAGE_LOCATION

    E O QUE ELE NAO PODE FAZER

      inventar SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RUN_ID
              sha256 · captured_at — nem nenhum outro campo que a observacao
              nao trouxe.

Traduzir nome e forma e o trabalho de um adapter. **Preencher um campo que a
observacao nao trouxe e outra coisa, e esta proibido.** O que o coletor nao
disse chega a porta em falta, e a porta escreve `NAO SEI` — que e a resposta
honesta, e nao um buraco.

O QUE ELE DEVOLVE A QUEM O CHAMA
--------------------------------
Um ficheiro so, sempre no mesmo sitio, sempre reescrito:

    data/colheita/italia/colheita.json

Reescrito, e nao acumulado, de proposito. Esta pasta e o BALCAO entre o
executor e a porta — nao e arquivo. O arquivo e o livro append-only, que
continua intacto e que ninguem aqui toca. Se esta pasta acumulasse um ficheiro
por corrida, a corrida seguinte tornaria a entregar a colheita da anterior, e o
`I3` que este adapter existe para resolver voltava a entrar pela porta ao lado.

    UM BALCAO QUE GUARDA O QUE JA ENTREGOU
    NAO E UM BALCAO: E UM SEGUNDO ARQUIVO, E MENTE.

Uso:
    python3 coleta/italy_executor.py --run-id=<RUN_ID> [FONTE]

O `--run-id` e OBRIGATORIO e vem de quem coordena. Este adapter nao cunha
corrida — se o cunhasse, a corrida do orquestrador e a corrida do coletor eram
duas, e o `raw_asset` ficaria ligado a uma corrida que o manifesto nao conhece.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas no caminho

import retorno_da_coleta as rdc  # noqa: E402 — a lei do retorno, COL-LAW-505
# O dono unico da regra «isto e uma afirmacao ou uma confissao de
# ignorancia?». Reescreve-la aqui criaria um segundo dono, e dois donos
# de uma regra divergem em silencio.
from coleta import ingresso as ing  # noqa: E402

# ONDE O COLETOR ESCREVE O LIVRO. Nao e configuracao nova: `ITALY_OPS_ROOT` ja
# e a raiz que o coletor italiano le ha muito, e ler o livro noutro sitio que
# nao aquele onde ele foi escrito daria sempre zero observacoes — com cara de
# «a fonte nao tinha nada».
OPS_ROOT = os.environ.get("ITALY_OPS_ROOT") or RAIZ

COLETOR = os.path.join("coleta", "italy_pilot_collect.mjs")
LIVRO = os.path.join("data", "collection-ledger", "italy", "observations.ndjson")
BALCAO = os.path.join("data", "colheita", "italia")
COLHEITA = os.path.join(BALCAO, "colheita.json")
# ONDE A CORRIDA DECLARA O QUE PRODUZIU (COL-LAW-505). Nao substitui o
# `colheita.json`: aquele carrega as unidades, este diz O QUE ELAS SAO.
RETORNO = os.path.join(BALCAO, "RETORNO.json")

EXECUTOR_ID = "italia-recorrente"
EXECUTOR_VERSION = "adapter-v1"

# ── O QUE A OBSERVACAO TRAZ E A PORTA TRANSPORTA ────────────────────────────
# `coleta/ingresso.py::DO_COLETOR` tem treze campos. A observacao italiana
# responde a tres deles, e responde-lhes com o mesmo nome. Os outros dez nao se
# preenchem: `DOCUMENT_ID` e `DOCUMENT_VERSION_ID`, que a observacao TEM, nao
# cabem em nenhum — isso esta medido e registado, e e pergunta do B4, nao desta.
# ⚠️ O NOME DESTA CONSTANTE MENTE, e a trava do tradutor apanhou-o em
# 2026-09-11. Ela nao leva «a porta»: leva ao CONTRATO COMUM, e por isso
# mapeia MAIUSCULA para MAIUSCULA. Quem traduz para a lingua de quem julga e
# `coleta/ingresso.py::para_a_porta`, e so ele.
#
#     UM NOME QUE DIZ O DESTINO ERRADO FAZ O PROXIMO LEITOR PROCURAR
#     A TRADUCAO NO SITIO ERRADO.
#
# O nome fica registado como divida e nao se renomeia aqui: renomear uma
# constante publica no meio de uma missao de fronteira e mexer no que nao se
# veio medir.
DA_OBSERVACAO_PARA_O_CONTRATO = DA_OBSERVACAO_PARA_A_PORTA = {
    "SOURCE_ID": "SOURCE_ID",
    "SOURCE_URL": "SOURCE_URL",
    "FACT_TIME": "FACT_TIME",
}


def _relativo(caminho: str) -> str:
    """`./data/collection-store/...` -> `data/collection-store/...`.

    A porta junta o que receber a raiz do repositorio, e por isso o caminho tem
    de ser relativo a ela. O coletor escreve-o com o prefixo da raiz DELE
    (`ITALY_OPS_ROOT`, que por omissao e `.`). Normalizar um caminho e
    traducao; e a unica coisa que se faz ao valor.
    """
    if not caminho:
        return ""
    p = os.path.normpath(caminho)
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, RAIZ)
        except ValueError:
            return ""
    return p.replace("\\", "/")


def _tempo_do_fato(v) -> str:
    """`"UNKNOWN — o boletim nao data a observacao de campo"` NAO e um tempo.

    O coletor escreve a confissao dentro do proprio campo. Passa-la adiante
    como se fosse valor poria uma frase onde a porta espera um instante, e um
    campo preenchido com prosa parece medido. Esta casa ja tem sitio para nao
    saber: o campo fica por dizer, e a porta escreve `NAO SEI`.
    """
    s = str(v or "").strip()
    if not s or s.upper().startswith(("UNKNOWN", "NAO SEI", "NÃO SEI")):
        return ""
    return s


def traduzir(obs: dict) -> dict:
    """Uma observacao do livro, na lingua da porta. Traducao 4 (e so ela)."""
    # A OBSERVACAO VAI INTEIRA, e nao mutilada: a porta so LE os treze campos
    # que conhece, e o que sobra viaja como conteudo da observacao — que e o
    # que ela e. Deitar fora aqui o `DOCUMENT_ID` seria esta peca a decidir o
    # que a casa pode vir a saber.
    fora = {k: v for k, v in obs.items() if k != "RAW_PATH"}

    # E SO DEPOIS A TRADUCAO, que manda sobre o que copiou. `FACT_TIME` vinha
    # do coletor com uma confissao dentro (`UNKNOWN — ...`); deixa-la passar
    # poria prosa onde a porta espera um instante.
    for de, para in DA_OBSERVACAO_PARA_A_PORTA.items():
        v = obs.get(de)
        if para == "FACT_TIME":
            v = _tempo_do_fato(v)
        if v:
            fora[para] = v
        else:
            fora.pop(para, None)
    # O EXECUTOR PODE DIZER QUEM E: isto nao e um campo da observacao, e quem o
    # declara e quem corre. `DO_COLETOR` transporta-o de proposito.
    fora["EXECUTOR_ID"] = EXECUTOR_ID
    fora["EXECUTOR_VERSION"] = EXECUTOR_VERSION

    # ── TRADUCAO 4 · RAW_PATH -> STORAGE_LOCATION ──────────────────────────
    # ⚠️ SE ISTO FICAR VAZIO, A PORTA PRESERVA O JSON DA OBSERVACAO, e nao o
    # documento. Sao as duas respostas certas para duas perguntas diferentes —
    # uma observacao sem bytes E o proprio item — e por isso nao se inventa um
    # caminho: quando o coletor nao disse onde os bytes estao, nao se diz.
    caminho = _relativo(obs.get("RAW_PATH") or "")
    if caminho:
        fora["STORAGE_LOCATION"] = caminho

    return fora


def observacoes_da_corrida(run_id: str, raiz: str = None) -> list:
    """Traducao 2 e 3: do livro NDJSON, so esta corrida, como lista.

    O livro e append-only e guarda TODAS as corridas. Ler o ficheiro inteiro
    entregaria a porta as 144 observacoes de sempre — e cada corrida
    reapresentaria as anteriores como se fossem colheita sua.

        RELER O ARQUIVO NAO E COLHER.
    """
    p = os.path.join(raiz or OPS_ROOT, LIVRO)
    if not os.path.isfile(p):
        return []
    fora = []
    with open(p, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            try:
                o = json.loads(linha)
            except json.JSONDecodeError:
                # UMA LINHA PARTIDA NAO APAGA AS OUTRAS. O livro e append-only:
                # uma escrita interrompida deixa lixo no fim, e perder a colheita
                # inteira por causa dele seria trocar um estrago por outro maior.
                continue
            if isinstance(o, dict) and o.get("RUN_ID") == run_id:
                fora.append(o)
    return fora


def fonte_do_conteudo(sha256: str, raiz: str = None) -> dict:
    """Que fonte o LIVRO registou para ESTE conteudo. Nada mais.

    O livro e o dono da resposta, e por isso a pergunta faz-se aqui. Nao ha um
    segundo livro, nao ha indice paralelo de identidade, e esta funcao nao
    deduz coisa nenhuma: ela LE o que o coletor escreveu.

    PORQUE A CHAVE E O CONTEUDO, E NAO O CAMINHO
    ---------------------------------------------
    MEDIDO no livro de hoje, 144 observacoes:

        RAW_SHA256 presente .... 144 de 144
        RAW_PATH presente ......  35 de 144
        e um dos RAW_PATH e `C:/ea...` — absoluto, de outra maquina

    Juntar por caminho responderia «nao sei» a tres quartos do livro e mentiria
    no resto. O sha256 identifica os BYTES que se tem na mao, e os bytes sao a
    unica coisa que quem refaz o bruto tem com certeza.

        ⚠️ ISTO NAO E DERIVAR A FONTE DO SHA.
        O sha e a CHAVE para achar a linha; a fonte vem do CAMPO `SOURCE_ID`
        que o coletor escreveu nessa linha. Se o livro nao tiver a linha, a
        resposta e «nao sei» — nunca o sha, nunca o caminho, nunca o nome.

    DUAS FONTES PARA O MESMO CONTEUDO NAO SE DESEMPATAM AQUI
    --------------------------------------------------------
    Se o livro registou o mesmo conteudo sob fontes DIFERENTES, esta funcao
    NAO escolhe: devolve o conflito e nenhuma fonte.

        ESCOLHER EM SILENCIO ENTRE DUAS VERDADES
        E FABRICAR UMA TERCEIRA.

    Devolve sempre um dicionario, e `SOURCE_ID` e `None` quando nao ha
    resposta provada.
    """
    vazio = {"SOURCE_ID": None, "OBSERVACOES": 0, "CONFLITO": [],
             "PORQUE": "o livro nao tem observacao deste conteudo"}
    if not sha256 or not isinstance(sha256, str):
        return dict(vazio, PORQUE="sem sha256 nao ha o que procurar")
    p = os.path.join(raiz or OPS_ROOT, LIVRO)
    if not os.path.isfile(p):
        return dict(vazio, PORQUE="o livro nao existe neste sitio")

    fontes, quantas = set(), 0
    with open(p, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            try:
                o = json.loads(linha)
            except json.JSONDecodeError:
                continue          # uma linha partida nao apaga as outras
            if not isinstance(o, dict) or o.get("RAW_SHA256") != sha256:
                continue
            quantas += 1
            v = o.get("SOURCE_ID")
            # ⚠️ UMA SENTINELA NAO E UMA FONTE. `'NAO SEI'` e uma string
            # VERDADEIRA em Python, e um `if v:` ingenuo promove-a a
            # identidade. O dono desta regra e `ingresso.NAO_E_AFIRMACAO`.
            if v not in ing.NAO_E_AFIRMACAO and v != "NÃO SEI":
                fontes.add(v)

    if not fontes:
        return dict(vazio, OBSERVACOES=quantas,
                    PORQUE=("o livro viu este conteudo %d vez(es) e nao "
                            "declarou fonte provada em nenhuma" % quantas
                            if quantas else vazio["PORQUE"]))
    if len(fontes) > 1:
        return {"SOURCE_ID": None, "OBSERVACOES": quantas,
                "CONFLITO": sorted(fontes),
                "PORQUE": ("o livro registou este mesmo conteudo sob %d "
                           "fontes diferentes; desempatar aqui seria "
                           "inventar" % len(fontes))}
    return {"SOURCE_ID": fontes.pop(), "OBSERVACOES": quantas, "CONFLITO": [],
            "PORQUE": "campo SOURCE_ID do livro, em %d observacao(oes) "
                      "concordantes" % quantas}


def largar(itens: list, raiz: str = RAIZ) -> str:
    """Escreve a colheita no balcao. Devolve o caminho relativo."""
    destino = os.path.join(raiz, COLHEITA)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(itens, fh, ensure_ascii=False, indent=1)
    return COLHEITA.replace("\\", "/")


def declarar(itens: list, run_id: str, raiz: str = RAIZ) -> str:
    """O ENVELOPE — a corrida diz o que produziu, em vez de deixar adivinhar.

        DECLARADO, NAO ADIVINHADO.  (COL-LAW-505)

    Antes, o orquestrador abria o `colheita.json` e escolhia uma lista por
    heuristica. A lista deste adapter estava certa POR SORTE: e uma lista de
    topo, e a heuristica gostava dela. Os outros executores nao tiveram a mesma
    sorte — 253 linhas de indice e de catalogo entraram como material colhido.

        ESTAR CERTO POR SORTE NAO E ESTAR CERTO.
        E ESTAR ERRADO AINDA SEM CONSEQUENCIA.
    """
    unidades = []
    for x in itens:
        onde = x.get("STORAGE_LOCATION") or ""
        # ⚠️ A UNIDADE VAI INTEIRA, e nao mutilada. A primeira versao desta
        # funcao construia um dicionario NOVO com seis campos do contrato — e
        # deitava fora o `texto`, o `SOURCE_URL`, o `STORAGE_LOCATION` e tudo o
        # mais que `traduzir()` tinha acabado de preparar. A prova apanhou-o:
        # a admissao devolvia `NAO_SEI — o item veio sem texto nenhum`, e a
        # culpa era desta funcao, nao do dado.
        #
        #     DECLARAR O QUE UMA COISA E NAO E SUBSTITUI-LA PELA ETIQUETA.
        #
        # O contrato acrescenta-se POR CIMA do item; nunca no lugar dele.
        unidades.append({
            **x,
            "ESPECIE": rdc.COLHEITA,
            "SOURCE_ID": x.get("SOURCE_ID") or "",
            # `NAO SEI` ESCRITO E LEGITIMO; calado nao e. E nunca se deriva o
            # DOCUMENT_ID do sha nem do caminho — a lei recusa, e com razao.
            "DOCUMENT_ID": x.get("DOCUMENT_ID") or rdc.NAO_SEI,
            "SHA256": x.get("RAW_SHA256") or "",
            "RUN_ID": run_id,
            "PAYLOAD": {"ONDE": onde,
                        "ESTADO": rdc.estado_do_payload(onde, raiz)},
        })
    envelope = {
        "RUN_ID": run_id,
        "EXECUTOR_ID": EXECUTOR_ID,
        "EXECUTOR_VERSION": EXECUTOR_VERSION,
        # ZERO OBSERVACOES NAO E FALHA. Uma corrida que foi a fonte e nao
        # encontrou nada correu bem — `EMPTY_SUCCESS != ERROR`.
        "ESTADO": rdc.SUCCESS,
        "COLHEITA": unidades,
        "SUPORTE": [],
        "ERROS": [],
    }
    destino = os.path.join(raiz, RETORNO)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=1)
    return RETORNO.replace(os.sep, "/")


def colher(run_id: str, ops_root: str = None, raiz: str = RAIZ) -> dict:
    """Traducoes 2, 3 e 4 — sem correr o coletor.

    Esta funcao esta separada de `main` porque as duas metades respondem a
    perguntas diferentes: uma vai a fonte, a outra traduz o que a fonte deixou.
    Sem a separacao, provar a traducao obrigaria a haver rede.
    """
    brutas = observacoes_da_corrida(run_id, ops_root or OPS_ROOT)
    itens = [traduzir(o) for o in brutas]
    onde = largar(itens, raiz)
    envelope = declarar(itens, run_id, raiz)
    return {
        "RUN_ID": run_id,
        "OBSERVACOES_DESTA_CORRIDA": len(itens),
        "COM_BYTES_NO_ARMAZEM": sum(1 for x in itens if x.get("STORAGE_LOCATION")),
        "LARGOU_EM": onde,
        "DECLAROU_EM": envelope,
    }


def correr_coletor(run_id: str, fonte: str = "", raiz: str = RAIZ) -> dict:
    """Traducao 1: o Node corre, e recebe a corrida — nao a cunha."""
    comando = ["node", COLETOR, "--run-id=%s" % run_id]
    if fonte:
        comando.append("--fonte=%s" % fonte)
    try:
        r = subprocess.run(comando, cwd=raiz, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=1800)
        return {"CODIGO": r.returncode, "ERRO": r.stderr[-1500:].strip()}
    except Exception as ex:                                    # noqa: BLE001
        # NAO CORREU NAO E CORREU E FALHOU, e nenhum dos dois e «zero itens».
        return {"CODIGO": 1, "ERRO": "%s: %s" % (type(ex).__name__, ex)}


def main() -> int:
    args = sys.argv[1:]
    run_id = ""
    for a in args:
        if a.startswith("--run-id="):
            run_id = a.split("=", 1)[1].strip()
    if not run_id:
        print("uso: python3 coleta/italy_executor.py --run-id=<RUN_ID> [FONTE]",
              file=sys.stderr)
        print("     este adapter NAO cunha corrida: o RUN_ID vem do T-04.",
              file=sys.stderr)
        return 2
    fonte = next((a for a in args if not a.startswith("--")), "")

    r = correr_coletor(run_id, fonte)
    c = colher(run_id)
    c["COLETOR"] = r
    print(json.dumps(c, ensure_ascii=False, indent=1))
    # O coletor ter falhado NAO apaga o que ele conseguiu deixar no livro: a
    # colheita vai a porta na mesma, e o codigo de saida conta a verdade sobre
    # a ida a fonte.
    return 0 if r["CODIGO"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
