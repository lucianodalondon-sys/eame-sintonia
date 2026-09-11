#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O ORQUESTRADOR — quem responde «qual caminho executar para este pedido».

    py orquestrador/orquestrador.py "colete materiais de pesquisadores"
    py orquestrador/orquestrador.py "colete concorrentes" --so-a-porta   # so a peneira
    py orquestrador/orquestrador.py "colete materiais novos de pesquisadores da Espanha" --so-plano

ELE NAO COLETA. Nao abre pagina, nao chama API, nao raspa nada. Ele escolhe o
executor e coordena — e essa separacao e a razao de existir: quando o executor
for trocado por outro melhor, quem pediu continua a pedir a mesma coisa.

O QUE ELE ACRESCENTA E O RECIBO
--------------------------------
O censo encontrou o achado mais util desta missao: o `RUN-MANIFEST.json` ja tem
os campos certos — RUN_ID, ACTOR, ACTOR_VERSION, STARTED_AT, FINISHED_AT, INPUT,
COST_USD, ITEM_COUNT_RAW, STATUS, ERROR — e **cinco reguas ja o leem**. So que
nenhum executor o escreve. Por isso metade das corridas guardadas diz
`NOT_PRESERVED` no tempo e na versao: foram preenchidas a mao, depois, de
memoria.

Nao se inventa aqui um recibo novo. Faz-se o orquestrador ASSINAR o que ja
existe, em toda corrida, sem depender de ninguem se lembrar.

    O QUE NAO TEM RECIBO NAO ACONTECEU. Uma coleta sem recibo nao se consegue
    auditar, nao se consegue repetir, e nao se consegue cobrar — e daqui a tres
    meses ninguem sabe dizer se aquele numero veio de uma corrida boa ou de uma
    que falhou a meio.

ERRO NAO E REJEICAO
-------------------
Se o executor rebentar, o estado e ERRO e o recibo guarda a mensagem. Nao e
`REJEITADO`: rejeitado quer dizer «olhei e nao serve», e aqui ninguem chegou a
olhar. Confundir os dois faz uma falha de rede parecer um julgamento sobre a
fonte, e a fonte leva a culpa pela ferramenta.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from pedido import Pedido, de_uma_frase, PedidoInvalido, ERRO, COLHIDO  # noqa: E402
from receitas import resolver, Plano  # noqa: E402
import admissao as adm  # noqa: E402
import proveniencia as pv  # noqa: E402
import ingresso as ing  # noqa: E402  — a porta de entrada da coleta
import retorno_da_coleta as rdc  # noqa: E402 — a lei do retorno (COL-LAW-505)

PRONTOS = RAIZ / "data" / "samples" / "PRONTO-PARA-INTELIGENCIA"


def o_envelope(e: dict, run_id: str = "") -> tuple[dict, str]:
    """O QUE A CORRIDA DEVOLVEU, LIDO DA DECLARACAO — e nunca adivinhado.

        SO COLHEITA ENTRA NO INGRESSO.  (COL-LAW-505)

    ⚠️ AQUI VIVIA A HEURISTICA, E ELA CUSTOU 253 FALSOS POSITIVOS:

        lista = d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list) and v
             and isinstance(v[0], dict)), [])

    «uma lista, ou o primeiro campo do ficheiro que seja lista de fichas». Com
    isso, 163 linhas de um manifesto de descarga, 74 fichas de conta, 12 fichas
    de pessoa e 4 passos de um plano entraram na cadeia como material observado.
    E o contraexemplo que fecha o assunto: o `CLASSIFICADO-V1.json` DECLARA um
    contentor `ITEMS` com `ITEM_COUNT = 0`, e a heuristica SALTAVA-O por estar
    vazio para agarrar a lista de catalogo ao lado.

        UMA HEURISTICA QUE PREFERE UMA LISTA CHEIA A UMA LISTA CERTA
        NAO ESTA A LER O RETORNO: ESTA A ADIVINHAR.

    Esta funcao deixou de classificar. O que sobra dela e legitimo e continua a
    ser dela: ENCONTRAR a declaracao, e dizer alto quando o sitio declarado nao
    existe. Quem classifica e `leis/retorno_da_coleta.py`, e a lei nao esta
    copiada aqui — esta importada.
    """
    ident = e.get("id") or "NAO SEI"
    versao = versao_do_executor((e.get("roda") or [""])[0])
    retorno = e.get("retorno") or {}
    notas = []

    # ── 1 · A CORRIDA DECLAROU? Essa e a unica origem de COLHEITA ──────────
    caminho = retorno.get("ENVELOPE")
    if caminho:
        alvo = RAIZ / caminho
        if alvo.is_file():
            try:
                envelope = json.loads(alvo.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as ex:
                notas.append(f"«{caminho}» nao deu para ler: {type(ex).__name__}")
            else:
                if run_id and not str(envelope.get("RUN_ID") or "").strip():
                    envelope["RUN_ID"] = run_id
                return envelope, " · ".join(notas)
        notas.append(f"«{caminho}» e o envelope declarado e nao existe: ou a "
                     f"corrida nao correu aqui, ou ela nao declarou o que fez.")

    # ── 2 · O LEGADO, QUE SO PODE DECLARAR SUPORTE ─────────────────────────
    legado = retorno.get("LEGADO")
    if legado:
        for onde in legado:
            if not (RAIZ / onde).exists():
                notas.append(f"«{onde}» esta declarado e nao existe nesta arvore.")
        return rdc.envelope_do_legado(run_id or "NAO SEI", ident, versao,
                                      legado, str(RAIZ)), " · ".join(notas)

    # ── 3 · NINGUEM DECLAROU NADA ──────────────────────────────────────────
    #     UM RETORNO SEM DECLARACAO NAO E UM RETORNO VAZIO:
    #     E UM RETORNO QUE NAO SE DECLAROU.
    for onde in e.get("larga_em") or []:
        if not (RAIZ / onde).exists():
            notas.append(f"«{onde}» nao existe nesta arvore: o executor declara "
                         f"que larga ai, e nao ha nada.")
    return rdc.envelope_de_quem_nao_declarou(
        run_id or "NAO SEI", ident, versao,
        "este executor nao declara o que devolve (sem ENVELOPE nem LEGADO em "
        "`retorno`). Antes, era aqui que a heuristica adivinhava."), \
        " · ".join(notas)


def a_colheita(e: dict, run_id: str = "") -> tuple[list, str]:
    """So o que a lei deixa atravessar. Mesma assinatura de sempre, outra fonte.

    Quem chama isto continua a receber `(itens, notas)`. O que mudou e de onde
    vem a lista: era um palpite sobre a forma do JSON, e agora e o resultado de
    `conferir()` + `so_o_que_entra()` sobre um envelope declarado.
    """
    envelope, notas = o_envelope(e, run_id)
    mal = rdc.conferir(envelope, str(RAIZ))
    if mal:
        # UM ENVELOPE QUE QUEBRA O CONTRATO NAO ENTREGA NADA. Recusar item a
        # item deixaria passar metade de um retorno que ja se sabe mal formado.
        return [], " · ".join(filter(None, [notas] + ["ENVELOPE_INVALIDO: " + m
                                                     for m in mal]))
    return rdc.so_o_que_entra(envelope), notas


def pela_entrada(itens: list, recibo: dict, memoria=None) -> dict:
    """Leva a colheita a PORTA DE ENTRADA da coleta, que a preserva como RAW.

    Ela nao julga nada: quem julga e a admissao, logo a seguir. Aqui responde-se
    so «posso preservar esta observacao?», e o que nao passa sai com nome —
    `INGRESS_SEM_CONTEUDO`, `INGRESS_CONTRATO_QUEBRADO` — que NAO e o mesmo que
    ser rejeitado na admissao, nem que ter dado erro, nem que nao ter corrido.

        RECUSA NA PORTA != REJEITADO NA ADMISSAO != ERRO != NAO CORREU.

    O armazem e LOCAL de proposito. Preservar nao pode depender de haver rede
    nem credencial: um coletor que corre offline continua a ter de deixar
    rasto.

    ⚠️ A `memoria` E O BANCO, E ELA NAO CHEGAVA AQUI. A frase acima dizia
    «quando houver banco, ele entra por `memoria=` sem esta funcao mudar» — e
    era falsa por uma unica razao: esta funcao nao tinha por onde o receber.
    `ing.receber` sempre aceitou `memoria=`; quem o chamava e que nao o
    passava, e por isso `collection_run` e `raw_asset` nunca viam uma corrida
    da rota canonica.

        UM PARAMETRO OPCIONAL QUE NINGUEM CONSEGUE PASSAR
        NAO E OPCIONAL: E INEXISTENTE.

    Continua a ser opcional de verdade: sem banco ligado, `memoria=None`, e a
    preservacao em disco acontece na mesma.
    """
    armazem = ing.ArmazemLocal(RAIZ)
    r = ing.receber(itens, corrida=recibo, armazem=armazem, memoria=memoria,
                    raiz=str(RAIZ))
    bruto = r.get("RAW") or {}
    return {
        "PRESERVADOS": len(r["ACEITES"]),
        "RECUSADOS": len(r["RECUSAS"]),
        "PORQUE_RECUSADOS": [x["PORQUE"] for x in r["RECUSAS"]],
        "RUN_STATE": bruto.get("RUN_STATE", "NAO_CORREU"),
        # O banco NAO foi medido nesta corrida, e dizer 0 seria dizer que se
        # olhou e nao havia. Nao se olhou.
        "BANCO": (bruto.get("MEMORIA") or {}).get("COMO_FOI_MEDIDO",
                                                  "NAO MEDIDO — sem banco ligado"),
    }


def pela_porta(itens: list, universo: str, run_id: str) -> dict:
    """Leva cada item a porta de admissao e guarda TODAS as decisoes.

    TODAS, e nao so as que passaram: o «nao» sem testemunha e trabalho perdido
    duas vezes — perde-se o item e perde-se a informacao de que aquela fonte
    entrega lixo.
    """
    # ── A TRAVESSIA DE LINGUA, UMA VEZ, PELO DONO DELA ─────────────────────
    # A unidade chega na lingua do contrato comum (`SOURCE_ID`) e a admissao le
    # a dela (`source_id`). Esta rota NAO traduzia — e por isso a primeira
    # unidade italiana a chegar aqui ouviu «nao da para dizer de onde veio»
    # com a origem declarada no proprio item.
    #
    # A traducao nao se escreve aqui: `coleta/ingresso.py::para_a_porta` e o
    # unico dono, e este e um dos tres sitios que passaram a usa-lo.
    prontos, decisoes = [], []
    for x in itens:
        try:
            prontos.append(ing.para_a_porta(x))
        except ing.AliasEmConflito as ex:
            # DOIS NOMES, DOIS VALORES. Nao se escolhe em silencio e nao se
            # rebenta a corrida: o item vai a porta declarado como ilegivel, e
            # ela responde ERRO — que NAO e rejeicao. `erro_de_leitura` e o
            # campo que a propria admissao ja usa para isto.
            prontos.append(dict(x, erro_de_leitura=str(ex)))
    decisoes = [adm.decidir(x, universo, corrida=run_id) for x in prontos]
    itens = prontos
    if decisoes:
        adm.escrever(decisoes)

    aceites = []
    for x, d in zip(itens, decisoes):
        if d.resultado == adm.SIM:
            aceites.append(adm.pronto_para_inteligencia(x, d))
    if aceites:
        PRONTOS.mkdir(parents=True, exist_ok=True)
        corpo = json.dumps({"RUN_ID": run_id, "ITENS": aceites},
                           ensure_ascii=False, indent=2)
        (PRONTOS / f"{run_id}.json").write_text(corpo + "\n", encoding="utf-8")

    conta: dict = {}
    for d in decisoes:
        conta[d.resultado] = conta.get(d.resultado, 0) + 1
    return {"itens": len(itens), "por_resultado": conta, "prontos": len(aceites),
            "ficheiro": (PRONTOS / f"{run_id}.json").relative_to(RAIZ).as_posix()
                        if aceites else ""}

# O caminho do RUN-MANIFEST NAO vive aqui. Deixar a constante para tras seria
# deixar a porta destrancada: a proxima pessoa escreve `MANIFESTO.write_text` e
# o contrato volta a ser contornado sem ninguem reparar. O dono e
# `regras/proveniencia.py`, e o caminho e dele.


def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versao_do_executor(caminho: str) -> str:
    """A versao e o commit que tocou o ficheiro pela ultima vez.

    NOT_PRESERVED era o que estava escrito nas corridas antigas — quer dizer
    «ninguem apontou». Com o commit ao lado, da para voltar exatamente ao codigo
    que produziu aquele numero.
    """
    r = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%h",
                        "--", caminho], capture_output=True, text=True)
    return (r.stdout.strip() or "NOT_PRESERVED") if r.returncode == 0 else "NOT_PRESERVED"


def novo_run_id(p: Pedido) -> str:
    pais = (p.filtros.get("pais") or "XX").upper()
    return f"{pais}-{p.alvo}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')}"


def guardar_recibo(recibo: dict) -> None:
    """Entrega a corrida a quem e dono da procedencia. Nao escreve o ficheiro.

    ⚠️ ESTA FUNCAO ESCREVIA O MANIFESTO DIRECTAMENTE, e por isso o contrato nunca
    passava por aqui. O resultado esta medido no proprio ficheiro: das 20
    corridas, DEZ nao trazem `DATASET_ID`, `SOURCE_VERSION`, `RAW_EVIDENCE_PATH`
    nem `RAW_EVIDENCE_STATE`. Todas as dez sairam deste `write_text`.

        EXECUTAR A CORRIDA NAO E SER A AUTORIDADE SOBRE A PROCEDENCIA DELA.

    O orquestrador sabe o que correu, e continua a dize-lo. Quem escreve e
    `regras/proveniencia.py`, que e a peca que conhece a lei do manifesto — e
    que agora recusa palavra fora do contrato e confessa em `NOT_PRESERVED` o
    campo que nao veio, em vez de o deixar simplesmente ausente.
    """
    faltaram = pv.acrescentar(recibo)
    if faltaram:
        print("  · manifesto: %d campo(s) do contrato ficaram NOT_PRESERVED: %s"
              % (len(faltaram), ", ".join(faltaram)))


def correr(p: Pedido, so_plano: bool = False, seco: bool = False,
           so_a_porta: bool = False, memoria=None) -> dict:
    """Do pedido ao recibo. Devolve o recibo, sempre — mesmo quando falha."""
    plano = resolver(p)

    if so_plano or not plano.da_para_correr:
        return {
            "RUN_ID": novo_run_id(p),
            "STATUS": "PLANO" if so_plano else "SEM_CAMINHO",
            "PEDIDO": p.para_json(),
            "MISSION": p.assunto,
            "COUNTRY": p.filtros.get("pais", "NAO SEI"),
            "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
            "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
            "ERROR": "" if so_plano else plano.porque_nao(),
            "_plano": plano,
        }

    e = plano.executores[0]
    caminho = e["roda"][0]

    # ── A CORRIDA NASCE AQUI, ANTES DE QUALQUER COISA CORRER ────────────────
    # ⚠️ O `RUN_ID` NASCIA OITO LINHAS DEPOIS DE O EXECUTOR JA TER CORRIDO.
    # O executor ia a fonte, trazia bytes, e so entao esta casa decidia como se
    # chamava a corrida que os trouxe. Enquanto o executor era mudo isso
    # passava despercebido; no dia em que um executor precisa de DIZER em nome
    # de que corrida colheu, deixa de passar.
    #
    #     PROVENIENCIA E PROSPECTIVA. Quem so a decide depois do facto
    #     nao a regista: reconstroi-a — e reconstrucao nao e testemunho.
    #
    # O nome nao mudou, nem o formato: mudou QUANDO se pergunta.
    run_id = novo_run_id(p)

    # o comando nasce do PEDIDO, nao de quem chama o orquestrador
    comando = list(e["roda"])
    valores = {**(e.get("filtros_por_omissao") or {}), **p.filtros}
    for nome in e.get("argumentos_de_filtros") or []:
        v = valores.get(nome)
        if v:
            comando.append(str(v))
    # OPT-IN, e declarado no registo. O executor que nao pede a corrida
    # continua a ser chamado com exactamente os mesmos argumentos de antes —
    # acrescentar isto a todos mudaria a linha de comando de quatro executores
    # que nunca a pediram.
    if e.get("recebe_run_id"):
        comando.append("--run-id=%s" % run_id)
    inicio = agora()
    saida, erro, codigo = "", "", 0

    if seco or so_a_porta:
        # ensaio: prova o caminho inteiro sem gastar rede nem dinheiro.
        # `--so-a-porta` vai mais longe: nao colhe, mas leva a colheita QUE JA
        # EXISTE a peneira. E o que permite reprocessar quando a regra muda —
        # sem isto, mudar a regra obrigaria a coletar tudo outra vez, e ninguem
        # o faria; a regra nova valeria so para o que viesse depois.
        saida, codigo = ("(nao se colheu: so se levou a colheita a porta)"
                         if so_a_porta else
                         "(ensaio seco: o executor nao foi chamado)"), 0
    else:
        try:
            r = subprocess.run([sys.executable, *comando], cwd=str(RAIZ),
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=1800)
            saida, erro, codigo = r.stdout[-4000:], r.stderr[-2000:], r.returncode
        except Exception as ex:                                # noqa: BLE001
            erro, codigo = f"{type(ex).__name__}: {ex}", 1

    recibo = {
        "RUN_ID": run_id,
        # O CONTRATO FALA `SUCCESS`/`FAILED`. Isto dizia `OK`, e as tres
        # corridas com `STATUS: OK` no manifesto sao dai. Duas palavras
        # para o mesmo estado sao o mesmo defeito da autoria, um andar
        # abaixo. `ESTADO_DOS_ITENS` continua a falar COLHIDO/ERRO —
        # esse e outro campo e outra pergunta.
        "STATUS": "SUCCESS" if codigo == 0 else "FAILED",
        "PEDIDO": p.para_json(),
        "MISSION": p.assunto,
        "COUNTRY": p.filtros.get("pais", "NAO SEI"),
        "PLATFORM": ", ".join(e["rotas"]),
        "ACTOR": caminho,
        "ACTOR_VERSION": versao_do_executor(caminho),
        "CAPTURE_METHOD": e["custo"],
        "INPUT": p.filtros or {},
        "QUERY": p.em_uma_frase(),
        "COMANDO": " ".join(comando),
        "STARTED_AT": inicio,
        "FINISHED_AT": agora(),
        # Custo ZERO quando o executor nao foi chamado: uma passagem so pela
        # peneira nao abre ligacao nenhuma. Escrever «NAO SEI» aqui seria pior
        # que impreciso — o portao do padrao conta os «NAO SEI» como divida, e
        # eu estaria a inventar divida sobre uma corrida que nao gastou nada.
        "COST_USD": (0 if (seco or so_a_porta or e["custo"] == "gratuito")
                     else "NAO SEI"),
        "ITEM_COUNT_RAW": "NAO SEI",
        "ITEM_COUNT_NORMALIZED": "NAO SEI",
        "ERROR": erro.strip(),
        "ESTADO_DOS_ITENS": COLHIDO if codigo == 0 else ERRO,
        "FONTES_DO_ASSUNTO": len(plano.fontes_do_assunto),
        "FONTES_SEM_CAMINHO": len(plano.sem_caminho),
        "SAIDA": saida.strip()[-1500:],
        "_plano": plano,
    }

    # ── E A COLHEITA VAI A PORTA ────────────────────────────────────────────
    # O caminho so esta fechado aqui. Antes desta parte, o executor corria,
    # largava o que trouxe numa pasta, e ninguem ia buscar: a peneira existia e
    # nada passava por ela.
    envelope, notas = o_envelope(e, run_id)
    itens, notas = a_colheita(e, run_id)
    recibo["COLHEITA_ENCONTRADA"] = len(itens)
    recibo["COLHEITA_NAO_ENCONTRADA"] = notas
    # O RETORNO FICA ESCRITO NO RECIBO, e nao so a contagem: quem audita
    # precisa de saber que ESPECIE veio, e nao apenas quantas linhas.
    recibo["RETORNO"] = {
        "ESTADO": envelope.get("ESTADO"),
        "COLHEITA": len(envelope.get("COLHEITA") or []),
        "SUPORTE": [x.get("ESPECIE") for x in (envelope.get("SUPORTE") or [])],
        "ERROS": envelope.get("ERROS") or [],
        "PORQUE_ZERO_COLHEITA": envelope.get("PORQUE_ZERO_COLHEITA"),
    }

    # ── E A COLHEITA ENTRA PELA PORTA, ANTES DE ALGUEM A JULGAR ─────────────
    # ⚠️ ATE AQUI, O QUE O EXECUTOR LARGAVA IA DIRECTO A ADMISSAO. A etapa RAW
    # existia, estava provada contra Postgres, e nunca corria: o item era
    # julgado sem nunca ter sido PRESERVADO, e sem passar pelo contrato comum
    # que `leis/artefato.py` escreveu exactamente para isto.
    #
    #     OBSERVAR NAO E PRESERVAR. PRESERVAR NAO E JULGAR.
    #
    # A porta responde «posso preservar esta observacao como RAW?». A admissao,
    # logo a seguir, responde outra pergunta: «isto pode entrar no universo?».
    # Sao duas perguntas, e agora sao duas etapas.
    if itens and (so_a_porta or not seco):
        recibo["INGRESSO"] = pela_entrada(itens, recibo, memoria=memoria)
    if itens and (so_a_porta or not seco):
        r = pela_porta(itens, p.alvo, recibo["RUN_ID"])
        recibo["ADMISSAO"] = r
        recibo["ITEM_COUNT_RAW"] = r["itens"]
        recibo["ITEM_COUNT_NORMALIZED"] = r["prontos"]
        recibo["ESTADO_DOS_ITENS"] = ("PRONTO_PARA_INTELIGENCIA" if r["prontos"]
                                      else "NA_PORTA")
    return recibo


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_plano = "--so-plano" in sys.argv
    so_a_porta = "--so-a-porta" in sys.argv
    seco = "--seco" in sys.argv and not so_a_porta
    # --filtro fase=posts --filtro plataforma=youtube
    extras = {}
    for i, a in enumerate(sys.argv):
        if a == "--filtro" and i + 1 < len(sys.argv) and "=" in sys.argv[i + 1]:
            k, v = sys.argv[i + 1].split("=", 1)
            extras[k.strip()] = v.strip()
    frase = " ".join(args) or "colete materiais de pesquisadores"

    try:
        p = de_uma_frase(frase)
        p.filtros.update(extras)
    except PedidoInvalido as ex:
        print(f"PEDIDO RECUSADO: {ex}")
        return 2

    recibo = correr(p, so_plano=so_plano, seco=seco, so_a_porta=so_a_porta)
    plano = recibo.pop("_plano")
    print(plano.em_palavras())
    print()

    if recibo["STATUS"] == "PLANO":
        print("(so o plano foi pedido; nada correu)")
        return 0
    if recibo["STATUS"] == "SEM_CAMINHO":
        print(f"NAO CORREU · {recibo['ERROR']}")
        return 1

    if not seco:
        guardar_recibo({k: v for k, v in recibo.items() if k != "SAIDA"})
    print(f"CORRIDA {recibo['STATUS']} · {recibo['RUN_ID']}")
    print(f"  executor {recibo['ACTOR']} @ {recibo['ACTOR_VERSION']}")
    print(f"  de {recibo['STARTED_AT']} a {recibo['FINISHED_AT']}")
    if recibo["ERROR"]:
        print(f"  ERRO (nao e rejeicao): {recibo['ERROR'][:300]}")
    print(f"  colheita encontrada: {recibo.get('COLHEITA_ENCONTRADA', 0)} item(ns)")
    if recibo.get("COLHEITA_NAO_ENCONTRADA"):
        print(f"  NAO ENCONTREI O QUE ELE LARGOU: {recibo['COLHEITA_NAO_ENCONTRADA']}")
    a = recibo.get("ADMISSAO")
    if a and a["itens"]:
        print("  pela porta de admissao: "
              + " · ".join(f"{k} {v}" for k, v in sorted(a["por_resultado"].items())))
        if a["ficheiro"]:
            print(f"  prontos para a inteligencia: {a['prontos']} -> {a['ficheiro']}")
    if seco:
        print("  (ensaio seco: nada foi coletado e nada foi escrito no manifesto)")
    return 0 if recibo["STATUS"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
