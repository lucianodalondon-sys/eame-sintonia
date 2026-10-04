#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FRONTEIRA ENTRE A COLETA E A INTELIGENCIA — medida, e nao afirmada.

    python3 provas/a_fronteira_da_coleta.py

POR QUE ISTO EXISTE
-------------------
Tres sitios desta arvore dizem coisas DIFERENTES sobre o mesmo READY, e
nenhum deles estava errado por descuido — cada um foi escrito num momento em
que era verdade, e ninguem tinha um medidor para os confrontar:

    BIBLIA-CANONICA-DA-COLETA.md · COL-LAW-043
        READY e canonico, o contrato de saida e FIXO e tem 12 campos.
        IT: PARTIAL.

    docs/operacao/CENSO-DOS-CONTRATOS-DE-ARTEFATO.md:110
        «E este o READY desta casa (...) ja tem consumidor.»

    coleta/derivacao_forward.py · GAPS
        «READY_NAO_TEM_DONO — nenhuma peca decide que um derivado esta
        PRONTO.»

O primeiro esta certo. Os outros dois exageram, em direccoes opostas: um diz
que ha consumidor e nao ha nenhum; o outro diz que nao ha dono e ha um, com
nome e linha.

    DECLARADO != IMPLEMENTADO != PRODUZIDO != CONSUMIDO.

Sao quatro perguntas, e achata-las em «existe / nao existe» e como se perdeu
a conta. Esta prova responde as quatro, separadas, e deixa de ser preciso
acreditar em qualquer dos tres textos.

O QUE ELA GUARDA (e faz falhar)
-------------------------------
    F1  a lei existe e declara os campos
    F2  o codigo devolve EXACTAMENTE esses campos — nem mais, nem menos
    F3  ha UM dono, e nao dois: ninguem constroi o registo READY fora dele
    F4  a porta recusa o que nao passou

O QUE ELA MEDE E RELATA, SEM FALHAR
-----------------------------------
    quem PRODUZ o registo (runtime? CLI? so teste?)
    quem CONSOME o registo
    quantas outras saidas existem a competir com esta

Nao falha por nao haver consumidor. Isso e um buraco DECLARADO, e o trabalho
desta prova e MEDI-LO — nao fingir que uma lacuna arquitectural e um bug de
codigo. Fazer esta prova ficar verde a inventar um consumidor seria a mesma
doenca que ela veio diagnosticar.

    UM BURACO MEDIDO E UMA DIVIDA COM NOME.
    UM BURACO PINTADO DE VERDE E UMA MENTIRA COM TESTE.
"""
import io
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao  # noqa: E402
# O DONO DA SALA. Perguntar ao disco onde o READY operacional vive era
# perguntar ao inquilino que ja se mudou. Ver `a_sala_canonica()`.
import sala_de_espera as espera  # noqa: E402

BIBLIA = os.path.join(RAIZ, "BIBLIA-CANONICA-DA-COLETA.md")
# Onde a medicao desta fronteira fica escrita, para o mapa a derivar.
OBSERVADA = os.path.join(RAIZ, "system-map", "data", "fronteira.observada.json")
LEI = "COL-LAW-043"

# ── O VOCABULARIO DA MEDICAO DA SALA ────────────────────────────────────────
# Tres palavras, e a casa ja as usa: `NOT_MEASURED` em
# `coleta/scrap_capacidades.py:103`, e a separacao `NOT_MEASURED != NOT_RELEVANT
# · ERROR != REJECTED` escrita em `leis/relevancia_da_fonte.py:96`. Nao se
# inventa um quarto nome para o mesmo facto.
#
#     NOT_OBSERVED != DOES_NOT_EXIST.  UNKNOWN != NO.  ERROR != ZERO.
SIM = "SIM"
NAO_MEDIDO = "NOT_MEASURED"
ERRO_DE_CONSULTA = "ERROR"

# Onde a coleta vive. `italia-portale/` e portal, `system-map/` e instrumento.
PASTAS_DA_COLETA = ('coleta', 'guarda', 'admissao', 'leis', 'medidas', 'motor',
                    'fontes', 'candidatas', 'ferramentas', 'orquestrador',
                    'portoes', 'pacote', 'pedido', 'regras', 'superficie')

fora = []


def caso(nome, ok, detalhe=""):
    fora.append((nome, bool(ok), detalhe))
    return bool(ok)


def campos_da_lei():
    """Os campos que a BIBLIA declara para o contrato de saida.

    Lidos do bloco de codigo da COL-LAW-043 — e nao copiados para ca. Copiar
    faria os dois divergirem em silencio, que e o defeito que esta casa mais
    repete.
    """
    txt = io.open(BIBLIA, encoding="utf-8").read()
    i = txt.find("## " + LEI)
    if i < 0:
        return None
    bloco = re.search(r"```\n(.*?)\n```", txt[i:i + 6000], re.S)
    if not bloco:
        return None
    nomes = re.findall(r"[A-Z][A-Z_]+", bloco.group(1))
    return [n for n in nomes if n != "READY_FOR_INTELIGENCIA"]


def campos_do_codigo():
    """Os campos que o dono devolve DE FACTO — chamando-o, e nao lendo-o."""
    item = {"id": "fronteira-1", "texto": "um ensaio publicado com DOI",
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
    d = admissao.decidir(item, "T5", corrida="prova-da-fronteira")
    if d.resultado != admissao.SIM:
        return None, d
    return admissao.pronto_para_inteligencia(item, d), d


def _grep(padrao, pastas):
    r = subprocess.run(
        # `-E`: sem ele o `grep` le expressao BASICA, onde `\(` significa
        # ABRIR GRUPO em vez de «um parentese». O primeiro censo devolveu 0
        # produtores por causa disso — e zero por engano de sintaxe e
        # exactamente o «UNKNOWN vestido de ZERO» que esta casa persegue.
        ["grep", "-rnE", "--include=*.py", "--include=*.mjs", "--include=*.js",
         "--include=*.yml", "--include=*.sh", padrao] + list(pastas),
        cwd=RAIZ, capture_output=True, text=True)
    # ⚠️ O CODIGO DE SAIDA DO `grep` NAO PODE SER IGNORADO.
    # 0 = achou · 1 = nao achou · 2+ = NAO CONSEGUIU PROCURAR (pasta que nao
    # existe, padrao invalido, grep ausente). A primeira versao devolvia `[]`
    # nos tres casos, e um censo que nao conseguiu procurar imprimia
    # «PRODUTORES 0 · CONSUMIDORES 0» com a mesma cara de quem procurou.
    #
    #     NAO ACHOU != NAO CONSEGUIU PROCURAR.
    #     UNKNOWN VESTIDO DE ZERO E A MENTIRA MAIS BARATA QUE HA.
    #
    # Este proprio ficheiro ja escreveu, num comentario, que uma sintaxe errada
    # lhe devolveu 0 produtores — e o conserto de entao foi o `-E`, nao olhar
    # para o codigo de saida. A classe ficou aberta ate um red team a apontar.
    # Rebenta, e diz o que nao conseguiu fazer.
    if r.returncode > 1:
        raise SystemExit(
            "RECUSADO: o grep nao conseguiu procurar (codigo %d) — padrao %r, "
            "pastas %s. Um censo que nao mediu nao pode imprimir zero.\n%s"
            % (r.returncode, padrao, list(pastas), r.stderr.strip()[:300]))
    return [l for l in r.stdout.splitlines() if l.strip()]


# ── A SALA DE HOJE, PERGUNTADA AO DONO DELA ────────────────────────────────
#
# ⚠️ ESTA MEDICAO OLHAVA PARA O BACKEND APOSENTADO, E PUBLICAVA-O COMO VERDADE.
#
#     produzido = os.path.isdir('data/samples/PRONTO-PARA-INTELIGENCIA')
#     ...
#     "READY_PRODUZIDO": produzido
#
# Essa pasta e a morada do backend FICHEIRO, que a propria Sala declara
# `CANONICO = False` e que `admissao/sala_de_espera.py::caminho_da_corrida`
# comenta com todas as letras: «Isto e endereco do backend nao canonico. Quem
# quiser saber onde o READY operacional vive pergunta a `estado_operacional()`».
# Esta prova nao perguntava. Media o disco, e do disco vazio concluia:
#
#     GAP = READY_NUNCA_PRODUZIDO
#     «NUNCA foi produzido um READY»
#
# O salto e de tres degraus, e cada um e uma lei desta casa:
#
#     nao olhei para a Sala canonica          -> NAO MEDI
#     a pasta da V1 nao existe                -> NAO MEDI A SALA, MEDI OUTRA COISA
#     logo nunca chegou nada                  -> INFERENCIA, e nao medicao
#
#     MEDIR UM BACKEND APOSENTADO NAO PROVA O ESTADO DO ACTUAL.
#     NOT_OBSERVED != DOES_NOT_EXIST.
#
# ⚠️ E O QUE ESTA FUNCAO **NAO** PODE RESPONDER, E POR QUE ISSO FICA DITO.
# A API canonica sabe dizer QUEM ESPERA AGORA (`listar_pendentes`). Nao ha
# nesta casa API que responda «alguma vez chegou alguma coisa» — quem foi
# `retirar()` sai da fila e deixa de aparecer. Por isso zero pendentes NAO vira
# `NAO`, nem aqui nem em lado nenhum:
#
#     «NINGUEM ESPERA AGORA» NAO E «NINGUEM CHEGOU NUNCA».
#
# Consultar a tabela por fora para responder ao historico seria criar um
# segundo dono da Sala. ONE CONCEPT -> ONE OWNER: prefere-se a resposta mais
# curta e verdadeira a resposta mais completa e fabricada.
def a_sala_canonica() -> dict:
    """O que a SALA CANONICA responde agora. Nunca o que a pasta da V1 sugere.

    Quatro desfechos, e nenhum deles e o silencio:

        A  canonica e com gente a espera  -> SIM, com o numero
        B  canonica e vazia agora         -> NOT_MEASURED (ver o aviso acima)
        C  sem backend canonico / sem DSN -> NOT_MEASURED
        D  a consulta rebentou            -> ERROR
    """
    try:
        e = espera.estado_operacional()
    except Exception as erro:                                   # noqa: BLE001
        # Nem o estado se conseguiu perguntar. Isso e ERRO, e nao um zero.
        return {"SALA_BACKEND": "NAO SEI", "SALA_CANONICO": False,
                "SALA_DISPONIVEL": False,
                "SALA_PORQUE": "%s: %s" % (type(erro).__name__, erro),
                "SALA_MEDICAO": ERRO_DE_CONSULTA, "SALA_PENDENTES": None,
                "READY_PRODUZIDO": ERRO_DE_CONSULTA}
    base = {"SALA_BACKEND": e.get("BACKEND"),
            "SALA_CANONICO": bool(e.get("CANONICO")),
            "SALA_DISPONIVEL": bool(e.get("DISPONIVEL")),
            "SALA_PORQUE": e.get("PORQUE")}

    # ── C · NAO HA SALA CANONICA NESTE AMBIENTE ────────────────────────────
    # Sem DSN, `backend()` devolve o FICHEIRO — disponivel, e NAO canonico. Ler
    # o vazio DESSE backend como estado da Sala e exactamente o defeito que
    # esta funcao veio fechar, uma camada acima.
    #
    #     AUSENCIA DE MEDICAO NAO PODE VIRAR VEREDITO.
    if not base["SALA_DISPONIVEL"] or not base["SALA_CANONICO"]:
        base.update({"SALA_MEDICAO": NAO_MEDIDO, "SALA_PENDENTES": None,
                     "READY_PRODUZIDO": NAO_MEDIDO})
        return base

    # ── A / B / D · a Sala canonica esta de pe: pergunta-se-lhe ────────────
    try:
        pendentes = espera.listar_pendentes()
    except Exception as erro:                                   # noqa: BLE001
        # ⚠️ AQUI MORRIA O ZERO SILENCIOSO. Uma ligacao que falha devolvia a
        # mesma cara de uma fila vazia, e a fila vazia ja era lida como «nunca
        # chegou nada». Duas mentiras encadeadas a partir de um cabo de rede.
        base.update({"SALA_MEDICAO": ERRO_DE_CONSULTA, "SALA_PENDENTES": None,
                     "READY_PRODUZIDO": ERRO_DE_CONSULTA,
                     "SALA_ERRO": "%s: %s" % (type(erro).__name__, erro)})
        return base
    n = len(pendentes or [])
    base.update({"SALA_MEDICAO": "MEDIDA", "SALA_PENDENTES": n,
                 "READY_PRODUZIDO": SIM if n else NAO_MEDIDO})
    return base


# ── PRODUZIR NAO E CONSUMIR ─────────────────────────────────────────────────
#
# Este diagnostico vivia numa linha dentro de `main()`:
#
#     GAP = None if consumidores else "READY_SEM_CONSUMIDOR"
#
# e essa linha tinha o eixo errado. O docstring la em cima ja dizia
# «DECLARADO != IMPLEMENTADO != PRODUZIDO != CONSUMIDO — sao quatro perguntas,
# e achata-las e como se perdeu a conta». O printout respeitava isso. O JEXPORT
# JSON nao: achatava PRODUZIDO e CONSUMIDO num so campo, e pelo eixo errado.
#
#     A PROVA DIZIA A LEI QUE O SEU PROPRIO JSON QUEBRAVA.
#
# O que o red team de 2026-09-11 (C-MADRUGADA-CR1) mediu, com o medidor real:
#
#     mundo montado                          GAP que saia
#     nada produzido, 0 consumidores         READY_SEM_CONSUMIDOR
#     READY PRODUZIDO, 0 consumidores        READY_SEM_CONSUMIDOR   <- o ALVO
#     nada produzido, 1 consumidor falso     None                   <- «sao»
#     READY produzido + consumidor           None
#
# Duas leituras erradas de uma so linha: o ALVO da arquitetura saia com o
# diagnostico do defeito, e um consumidor SEM producao nenhuma limpava o gap.
# `READY CONSUMER = 0` e estado desejado enquanto a Inteligencia nao comecou —
# esta escrito na seccao 24 do know-how. Um consumidor HOJE nao e saude: e um
# bypass da fronteira.
#
#     UM MEDIDOR QUE NAO DISTINGUE O ALVO DO DEFEITO NAO MEDE: OPINA.
#
# Agora sao dois eixos e quatro respostas. A funcao e pura de proposito: o
# diagnostico passa a ser testavel sem escrever um unico ficheiro no
# repositorio — ver tests/test_fronteira_mede_producao.py.
# ⚠️ E O PRIMEIRO EIXO DEIXOU DE SER UM BOOLEANO, PORQUE ELE NUNCA TEVE DOIS
# ESTADOS. `produzido: bool` so sabia dizer SIM e NAO, e o NAO carregava tres
# mundos diferentes colados: «medi e nao ha», «nao consegui medir» e «a
# consulta rebentou». Colados, os tres saiam com o veredito do primeiro — e o
# primeiro era o unico que esta casa nunca conseguiu medir.
#
#     UM BOOLEANO E UMA RESPOSTA QUE JA DECIDIU QUE NAO HA TERCEIRA HIPOTESE.
def o_estado_da_fronteira(ready_produzido, consumidores) -> tuple:
    """(GAP, PORQUE), a partir do que a SALA respondeu — e nunca de um palpite.

    `ready_produzido` vem de `a_sala_canonica()` e vale `SIM`, `NOT_MEASURED`
    ou `ERROR`. Nao ha `NAO`: a API canonica responde «quem espera agora», e
    ninguem a espera agora nao e ninguem chegou nunca.
    """
    consumidores = list(consumidores or [])
    if ready_produzido == ERRO_DE_CONSULTA:
        # ERRO != ZERO. Uma consulta que rebentou nao diz nada sobre a fila, e
        # em particular nao diz que ela esta vazia.
        return "SALA_ERRO_DE_CONSULTA", (
            "a Sala canonica foi perguntada e a consulta rebentou. ISTO NAO E "
            "ZERO e NAO E UM BLOQUEIO: e uma medicao que nao se conseguiu "
            "fazer, e o que ela mede continua por saber. "
            + ("E ja ha quem leia esta saida: %s." % ", ".join(consumidores)
               if consumidores else "Repita com o backend canonico de pe."))
    if ready_produzido != SIM:
        # ⚠️ AQUI VIVIA `READY_NUNCA_PRODUZIDO`, e ele dizia mais do que a
        # medicao dava. Nao se troca o nome por delicadeza: troca-se porque
        # este medidor nao tem como provar «nunca», e um gap com nome de
        # veredito faz o mapa inteiro pintar um bloqueio por cima de um NAO SEI.
        #
        #     AUSENCIA DE MEDICAO NAO E MEDICAO DE AUSENCIA.
        return "SALA_NAO_MEDIDA", (
            "o contrato existe, tem dono e o codigo devolve exactamente os "
            "campos da lei — e a SALA CANONICA nao foi medida nesta execucao. "
            "NAO SE SABE se ja chegou material: nao se sabe que sim, e "
            "tambem nao se sabe que nao. "
            + ("E ja ha quem leia uma saida cuja producao ninguem provou: %s."
               % ", ".join(consumidores) if consumidores else
               "Para medir, ponha o backend canonico de pe e repita."))
    if consumidores:
        return "CONSUMIDOR_ANTES_DA_INTELIGENCIA", (
            "ha READY produzido E ha quem o leia (%s). Enquanto a Inteligencia "
            "nao comecou, READY CONSUMER = 0 e o estado desejado: quem le hoje "
            "esta a atravessar a fronteira antes de ela abrir."
            % ", ".join(consumidores))
    # READY produzido, ninguem le: e EXACTAMENTE o alvo de fechamento.
    return None, None


def main():
    print("A FRONTEIRA DA COLETA — declarada, implementada, produzida, consumida")
    print("=" * 70)

    # ── F1 · A LEI ───────────────────────────────────────────────────────
    lei = campos_da_lei()
    caso("F1_a_lei_declara_o_contrato_de_saida",
         bool(lei) and len(lei) >= 5,
         "%s declara %d campos" % (LEI, len(lei or [])))

    # ── F2 · O CODIGO ────────────────────────────────────────────────────
    registo, decisao = campos_do_codigo()
    if registo is None:
        caso("F2_o_codigo_devolve_exactamente_os_campos_da_lei", False,
             "a porta nao admitiu o item da prova: %s" % (decisao.resultado,))
        codigo = []
    else:
        codigo = list(registo.keys())
        so_na_lei = sorted(set(lei or []) - set(codigo))
        so_no_codigo = sorted(set(codigo) - set(lei or []))
        caso("F2_o_codigo_devolve_exactamente_os_campos_da_lei",
             not so_na_lei and not so_no_codigo,
             "%d campos, iguais aos da lei" % len(codigo) if not (so_na_lei or so_no_codigo)
             else "so na lei: %s · so no codigo: %s" % (so_na_lei, so_no_codigo))

    # ── F3 · UM DONO, E NAO DOIS ─────────────────────────────────────────
    #
    #     ONE CONCEPT -> ONE OWNER.
    #
    # Qualquer sitio que monte um dicionario com `ESTADO:
    # PRONTO_PARA_INTELIGENCIA` sem passar pelo dono e um SEGUNDO dono a
    # nascer — e dois donos para um conceito e a maneira mais rapida de os
    # dois divergirem.
    #
    # ⚠️ A PRIMEIRA VERSAO DESTE CASO ERA LARGA DEMAIS e acusou o
    # orquestrador. Ele escreve `PRONTO_PARA_INTELIGENCIA` na linha 262 —
    # mas como ESTADO DA CORRIDA num recibo («como e que esta corrida
    # acabou»), e nao como o registo do contrato. Um dono a mais nao se
    # deteta pela palavra: deteta-se por quem CONSTROI O REGISTO, e o
    # registo reconhece-se pelo campo `ESTADO` com aquele valor.
    #
    #     MENCIONAR O NOME DE UM ESTADO != SER DONO DO CONTRATO.
    #
    # `pedido/pedido.py` declara-o como estado legal de um pedido, pela
    # mesma razao, e tambem nao e um segundo dono.
    # Tres formas de escrever a mesma coisa, e nao uma. Um red team mostrou
    # que a versao anterior so via o literal de dicionario
    # (`"ESTADO": "PRONTO..."`), e deixava passar `r["ESTADO"] = "PRONTO..."`,
    # `d.update(ESTADO=...)` e um `setdefault`.
    #
    # ⚠️ E CONTINUA A NAO SER PROVA DE AUSENCIA. Quem quiser mesmo montar um
    # segundo dono consegue escapar a qualquer regex — com uma constante, com
    # uma chave montada por concatenacao. Isto apanha o descuido, que e o que
    # acontece de facto; nao apanha o disfarce, e nao promete apanhar.
    outros = [l for l in _grep(
                  r'ESTADO.{0,4}[:=].{0,4}.PRONTO_PARA_INTELIGENCIA'
                  r'|ESTADO[[:space:]]*=[[:space:]]*.PRONTO_PARA_INTELIGENCIA',
                  PASTAS_DA_COLETA)
              if not l.startswith('admissao/admissao.py')]
    caso("F3_so_o_dono_constroi_o_registo_READY",
         not outros,
         "o unico construtor e admissao.pronto_para_inteligencia()"
         if not outros else "tambem constroem: %s" % [l.split(':')[0] for l in outros])

    # ── F4 · A PORTA RECUSA O QUE NAO PASSOU ─────────────────────────────
    mau = {"id": "sem-texto"}
    dm = admissao.decidir(mau, "T5", corrida="prova-da-fronteira")
    recusou = False
    try:
        admissao.pronto_para_inteligencia(mau, dm)
    except ValueError:
        recusou = True
    caso("F4_nao_ha_READY_sem_SIM_na_porta", recusou and dm.resultado != admissao.SIM,
         "a porta respondeu %s, e o contrato recusou-se a emitir" % dm.resultado)

    # ═════════════════════════════════════════════════════════════════════
    # O CENSO — medido e relatado, e NAO transformado em falha
    # ═════════════════════════════════════════════════════════════════════
    # QUEM CHAMA O DONO — e uma CHAMADA, nao uma mencao. `leis/artefato.py`
    # fala dele num docstring, e um docstring nao produz registo nenhum.
    # Este proprio ficheiro tambem sai da conta: um medidor que se conta a
    # si proprio inflaciona o que veio medir.
    # ⚠️ E UMA CHAMADA SO SE O FICHEIRO TAMBEM IMPORTAR O DONO.
    # `leis/artefato.py:43` escreve `admissao.pronto_para_inteligencia()`
    # num DOCSTRING — a explicar que o READY desta casa ja existe. O texto
    # casa com o padrao e nao produz registo nenhum. A diferenca entre uma
    # chamada e uma frase sobre a chamada nao se ve no regex; ve-se no
    # `import`. Quem nao importa o modulo nao o pode chamar.
    candidatos = sorted({
        l.split(':')[0] for l in
        _grep(r'\.pronto_para_inteligencia[[:space:]]*\(',
              list(PASTAS_DA_COLETA) + ['provas', 'tests', '.github'])
        if not l.startswith(('admissao/admissao.py',
                             'provas/a_fronteira_da_coleta.py'))})
    produtores = []
    for c in candidatos:
        try:
            fonte = io.open(os.path.join(RAIZ, c), encoding='utf-8').read()
        except OSError:
            continue
        if re.search(r'^\s*(import\s+admissao|from\s+admissao\s+import'
                     r'|import\s+admissao\s+as)', fonte, re.M):
            produtores.append(c)
    runtime = [l for l in produtores if not l.startswith(('provas/', 'tests/'))]
    consumidores = _grep('PRONTO-PARA-INTELIGENCIA',
                         list(PASTAS_DA_COLETA) + ['provas', 'tests', '.github'])
    destino = os.path.join(RAIZ, 'data', 'samples', 'PRONTO-PARA-INTELIGENCIA')

    print()
    print("  CENSO DA FRONTEIRA")
    print("  " + "-" * 66)
    print("  CONTRATO          %s · %d campos" % (LEI, len(lei or [])))
    print("  DONO              admissao/admissao.py :: pronto_para_inteligencia()")
    print("  PRODUTORES        %d chamada(s) ao dono, %d fora de provas/tests:"
          % (len(produtores), len(runtime)))
    for l in produtores:
        print("                      %-38s %s" % (
            l, "(so CLI, nenhum workflow)" if l in runtime else "(prova/teste)"))
    # ⚠️ ESTA PASTA E DO BACKEND NAO CANONICO, e a linha diz isso agora.
    # Ela continua a ser medida e continua a ser publicada — o que deixou de
    # acontecer e ela RESPONDER pela Sala. Apagar a medicao seria trocar uma
    # resposta errada por nenhuma; o que ela prova (existe ou nao existe a
    # morada da V1) continua a ser um facto util, com o nome certo.
    print("  MORADA DA V1      data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json"
          "  (backend FICHEIRO, NAO canonico)")
    # Isto e agora SO o que o nome diz: a morada da V1 existe neste disco?
    # Deixou de se chamar `produzido`, porque nunca o foi.
    morada_da_v1_existe = os.path.isdir(destino)
    print("  MORADA DA V1 EXISTE? %s" % ("SIM" if morada_da_v1_existe else "NAO"))
    lê = sorted({c.split(':')[0] for c in consumidores
                 if not c.startswith(('orquestrador/', 'provas/a_fronteira'))})

    # ── E A SALA DE HOJE, PERGUNTADA A QUEM E DONO DELA ───────────────────
    sala = a_sala_canonica()
    print("  SALA BACKEND      %s · canonico=%s · disponivel=%s"
          % (sala["SALA_BACKEND"], sala["SALA_CANONICO"], sala["SALA_DISPONIVEL"]))
    print("  SALA MEDICAO      %s%s" % (
        sala["SALA_MEDICAO"],
        "" if sala["SALA_PENDENTES"] is None
        else " · %d a espera" % sala["SALA_PENDENTES"]))
    print("  SALA PORQUE       %s" % (sala.get("SALA_ERRO") or sala["SALA_PORQUE"]))
    print("  READY PRODUZIDO   %s" % sala["READY_PRODUZIDO"])
    gap, porque = o_estado_da_fronteira(sala["READY_PRODUZIDO"], lê)
    print("  CONSUMIDORES      %d  %s" % (len(lê), lê or "— ninguem le esta saida"))
    # ── A MEDICAO FICA ESCRITA, PARA O MAPA A PODER DESENHAR ─────────────
    #
    # O mapa nao tinha cartao nenhum para a fronteira: desenhava a porta de
    # admissao e calava o que vem depois dela. A faixa «A ESPERA» existia — e
    # e definida como «o que ja passou por toda a coleta e ainda nao entrou na
    # inteligencia», que e READY palavra por palavra — mas estava ocupada pelos
    # donos do RAW e do DERIVED, que sao etapas 5 e 6 das nove.
    #
    #     A SALA DE ESPERA EXISTIA NO MAPA, COM OS INQUILINOS ERRADOS,
    #     E O INQUILINO CERTO NAO TINHA CARTAO.
    #
    # Nao se cria `ready.py` para ter cartao — o C-FINAL ja recusou isso, e com
    # razao. Cria-se um cartao DERIVADO DESTA MEDICAO, como o do derivado
    # nasce do censo das derivacoes. O que ele mostra e o que se mediu aqui,
    # incluindo o buraco.
    io.open(OBSERVADA, "w", encoding="utf-8").write(json.dumps({
        # ⚠️ A VERSAO SOBE PORQUE UM CAMPO MUDOU DE TIPO E DE SENTIDO.
        # `READY_PRODUZIDO` era `true`/`false` e passou a `SIM`/`NOT_MEASURED`/
        # `ERROR`. Quem le `bool(READY_PRODUZIDO)` contra a v2 le `True` para
        # `"NOT_MEASURED"` — o contrario do que o campo diz. Deixar o numero
        # da versao quieto seria esconder isso de quem vier a seguir.
        "SCHEMA": "fronteira-observada/v2",
        "O_QUE_ISTO_E": (
            "O estado medido da fronteira COLETA -> INTELIGENCIA. Escrito por "
            "quem mediu, para o mapa nao ter de acreditar em texto nenhum. "
            "A SALA e perguntada ao dono dela (admissao/sala_de_espera.py) e "
            "nunca a pasta do backend aposentado."),
        "GERADO_POR": "provas/a_fronteira_da_coleta.py",
        "LEI": LEI,
        "CAMPOS_DO_CONTRATO": lei or [],
        "CAMPOS_DO_CODIGO": codigo,
        "LEI_E_CODIGO_BATEM": bool(lei) and set(lei or []) == set(codigo),
        "DONO": "admissao/admissao.py :: pronto_para_inteligencia()",
        "PRODUTORES": produtores,
        "PRODUTORES_EM_RUNTIME": runtime,
        "CONSUMIDORES": lê,
        # ⚠️ ESTES DOIS FICAM, E DEIXARAM DE RESPONDER PELA SALA.
        # Eles dizem uma coisa verdadeira e pequena: onde vive o backend
        # FICHEIRO e se essa morada existe nesta arvore. O que eles NUNCA
        # puderam dizer — e diziam — e se o READY operacional foi produzido.
        #
        #     ONDE OLHEI != O QUE CONCLUI.
        "DESTINO": "data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json",
        "DESTINO_BACKEND": espera.BACKEND_FICHEIRO,
        "DESTINO_CANONICO": False,
        "DESTINO_EXISTE": morada_da_v1_existe,
        # ── E A SALA, PERGUNTADA AO DONO ──────────────────────────────────
        "SALA_DONO": "admissao/sala_de_espera.py",
        "SALA_BACKEND": sala["SALA_BACKEND"],
        "SALA_CANONICO": sala["SALA_CANONICO"],
        "SALA_DISPONIVEL": sala["SALA_DISPONIVEL"],
        "SALA_PORQUE": sala.get("SALA_ERRO") or sala["SALA_PORQUE"],
        "SALA_MEDICAO": sala["SALA_MEDICAO"],
        "SALA_PENDENTES": sala["SALA_PENDENTES"],
        # SIM · NOT_MEASURED · ERROR — e nunca `false` por o disco estar vazio.
        # `NAO` nao esta no vocabulario de proposito: a API canonica responde
        # «quem espera AGORA», e ninguem a espera agora nao e ninguem chegou
        # nunca. Ver `a_sala_canonica()`.
        "READY_PRODUZIDO": sala["READY_PRODUZIDO"],
        "READY_PRODUZIDO_VALORES": [SIM, NAO_MEDIDO, ERRO_DE_CONSULTA],
        "GAP": gap,
        "GAP_PORQUE": porque,
    }, ensure_ascii=False, indent=1) + "\n")

    print()
    print("  O QUE ISTO QUER DIZER, sem exagerar para nenhum dos lados:")
    print("    · READY TEM dono e TEM contrato. Dizer «READY_NAO_TEM_DONO» e")
    print("      dizer mais do que se mediu.")
    # ⚠️ ESTAS DUAS LINHAS ERAM FIXAS, e diziam «o destino nem sequer existe»
    # em qualquer maquina, medisse-se a Sala ou nao. Uma frase que nao depende
    # da medicao nao e um resultado: e uma legenda.
    if sala["SALA_MEDICAO"] == "MEDIDA":
        print("    · A SALA CANONICA foi medida (%s): %d a espera agora."
              % (sala["SALA_BACKEND"], sala["SALA_PENDENTES"]))
        if not sala["SALA_PENDENTES"]:
            print("      Zero A ESPERA nao e zero CHEGOU: quem ja foi retirado")
            print("      sai da fila e nao aparece aqui. O historico nao se le")
            print("      por esta porta, e por isso nao se afirma.")
    elif sala["SALA_MEDICAO"] == ERRO_DE_CONSULTA:
        print("    · A SALA CANONICA foi perguntada e a consulta REBENTOU.")
        print("      ERRO != ZERO: nao se sabe o que ha la dentro.")
    else:
        print("    · A SALA CANONICA NAO FOI MEDIDA aqui (backend=%s, "
              "canonico=%s)." % (sala["SALA_BACKEND"], sala["SALA_CANONICO"]))
        print("      NAO SE SABE se ja chegou material. Dizer «nunca chegou»")
        print("      seria transformar a falta de medicao num veredito.")
    print("    · A rota forward (DERIVED -> STRUCTURED -> ADMISSION) termina em")
    print("      ADMISSION e NAO chega aqui: o dono recebe `item`, e a rota")
    print("      produz `derived_artifact`. Sao duas coisas, e liga-las e uma")
    print("      DECISAO DE ARQUITETURA — nao um remendo de codigo.")
    print()
    print("    MEDIR UM BACKEND APOSENTADO NAO PROVA O ESTADO DO ACTUAL.")
    print("    NOT_OBSERVED != DOES_NOT_EXIST.")

    # ── A MUTACAO · o F2 tem de morder ───────────────────────────────────
    #
    # O F2 e a unica coisa que impede a lei e o codigo de divergirem em
    # silencio, que e como esta casa ja perdeu contratos antes. Se ELE
    # estiver cego, o verde dele nao vale nada.
    #
    # Tira-se um campo ao registo que o dono devolveu e pergunta-se se a
    # comparacao com a lei ainda reprova. Nada e escrito no disco: a mutacao
    # e sobre o dicionario em memoria.
    if registo is not None:
        mutante = dict(registo)
        mutante.pop("FACT_LOCATION", None)
        morde = sorted(set(lei or []) - set(mutante)) == ["FACT_LOCATION"]
        caso("F2b_MUTACAO_um_campo_a_menos_e_apanhado", morde,
             "sem FACT_LOCATION, a comparacao com a lei acusa a falta")

    print()
    print("=" * 70)
    for nome, ok, det in fora:
        print("  %s  %-52s %s" % ("PASS" if ok else "FAIL", nome, det))
    mal = [n for n, ok, _ in fora if not ok]
    print("=" * 70)
    print("FRONTEIRA_DA_COLETA=%s" % ("PASS" if not mal else "FAIL"))
    print("  o que isto prova: existe UM contrato de saida, com UM dono, e o")
    print("  codigo devolve exactamente o que a lei declara.")
    print("  o que isto NAO prova: que alguem o produza em runtime ou o")
    print("  consuma. Nao prova porque nao e verdade, e medir a falta e o")
    print("  trabalho — nao pinta-la de verde.")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
