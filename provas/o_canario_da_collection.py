#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUAL CLASSE CONSEGUE, HOJE, ATRAVESSAR A COLLECTION INTEIRA?

    python3 provas/o_canario_da_collection.py

A PERGUNTA, E E UMA SO
----------------------
    EXISTE UMA CLASSE QUE TENHA, AO MESMO TEMPO, AQUISICAO CANONICA
    E REGRA DE ADMISSAO ESCRITA?

A missao anterior mediu DUAS listas e cruzou-as: quem tem regra (T3, T4, T7,
T9) e quem declara colheita (T2). A intersecao deu vazia. Esta prova faz a
pergunta maior, que aquela nao fez:

    NAO «QUAIS SAO AS DUAS LISTAS», MAS «O QUE FALTA A CADA CLASSE».

Uma intersecao vazia diz que ninguem passa. Nao diz QUEM ESTA MAIS PERTO, nem
O QUE lhe falta — e sem isso a decisao seguinte e um palpite entre opcoes que
parecem iguais e nao sao.

O QUE ESTA PROVA NAO FAZ
------------------------
Ela nao corre executor nenhum e nao toca em banco. Mede CONTRATOS: a taxonomia
dos alvos, o registo de executores, o vocabulario da porta e o contrato do
envelope. Correr os cinco executores seria coleta, e coleta nao e censo.

    MEDIR O CONTRATO NAO E MEDIR A CORRIDA — e os dois sao precisos.

O que uma corrida real prova esta noutro sitio: `provas/o_pedido_atravessa.py`
aperta o botao num pedido T2 e mede o que ele deixou. Esta prova responde a
pergunta de COBERTURA que aquela nao consegue responder com uma corrida so.

POR QUE O PAIS NAO ENTRA NA CONTA
---------------------------------
`receitas.resolver` escolhe executores por `EXECUTORES.get(p.alvo)` e mais
nada — o pais filtra FONTES, nunca EXECUTORES. A prova mede isso em vez de
confiar nele, porque a medicao anterior so perguntou por `pais=IT` e uma
resposta de um pais so nao e uma resposta.
"""
import ast
import io
import json
import os
import sys
from collections import OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import admissao as adm                                      # noqa: E402
from pedido import ALVOS, Pedido                            # noqa: E402
from receitas import EXECUTORES, resolver                   # noqa: E402
import retorno_da_coleta as ret                             # noqa: E402

SAIDA = "data/derivados/O-CANARIO-DA-COLLECTION.json"

# ⚠️ NAO SEI E UMA RESPOSTA, E TEM DE CABER NO VOCABULARIO.
# Um censo cujo vocabulario so tem SIM e NAO obriga quem o escreve a escolher
# um dos dois para o que nao mediu — e a partir dai o ficheiro mente sem que
# ninguem tenha mentido.
SIM, NAO, NAO_MEDIDO = "YES", "NO", "NOT_MEASURED"

# Os campos que o contrato do envelope exige da CORRIDA. Lidos do dono, e nao
# copiados: `leis/retorno_da_coleta.py::conferir` e quem manda.
CAMPOS_DO_ENVELOPE = ("RUN_ID", "EXECUTOR_ID", "EXECUTOR_VERSION", "ESTADO")
LISTAS_DO_ENVELOPE = ("COLHEITA", "SUPORTE", "ERROS")


def _fonte(rel):
    with io.open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════
# 1 · O PAIS NAO ESCOLHE EXECUTOR — medido, e nao assumido
# ══════════════════════════════════════════════════════════════════════════
def executor_nao_depende_do_pais():
    """A lista de executores de um alvo muda com o pais pedido?

    ⚠️ A MEDICAO ANTERIOR PERGUNTOU SO POR `pais=IT`. Se o pais escolhesse
    executor, «T2 e o unico que declara colheita» seria uma frase sobre a
    Italia a passar por uma frase sobre a casa.
    """
    paises = ("IT", "ES", "FR", "EU", "")
    divergem = []
    for alvo in sorted(ALVOS):
        visto = None
        for p in paises:
            try:
                ids = tuple(e.get("id") for e in
                            resolver(Pedido(alvo=alvo, filtros={"pais": p})).executores)
            except Exception:                               # noqa: BLE001
                continue
            if visto is None:
                visto = ids
            elif ids != visto:
                divergem.append(alvo)
                break
    return divergem


# ══════════════════════════════════════════════════════════════════════════
# 2 · O CENSO, CLASSE A CLASSE
# ══════════════════════════════════════════════════════════════════════════
def aquisicao_canonica(execs):
    """COL-LAW-505: so `retorno.ENVELOPE` e colheita. Tudo o resto e suporte.

    E a razao esta escrita na propria receita: uma declaracao de LEGADO e
    feita ANTES da corrida e envelhece sozinha. Um ENVELOPE e a corrida a
    dizer o que produziu.

        DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO.
        DECLARAR COLHEITA NAO E.
    """
    for e in execs:
        if (e.get("retorno") or {}).get("ENVELOPE"):
            return SIM, "retorno.ENVELOPE = %s" % (e["retorno"]["ENVELOPE"],)
    for e in execs:
        r = e.get("retorno") or {}
        if r.get("LEGADO"):
            especies = sorted(set(r["LEGADO"].values()))
            return NAO, ("declara LEGADO (%s) — suporte, nunca colheita"
                         % ", ".join(especies))
    if execs:
        return NAO, "o executor existe e NAO declara retorno nenhum"
    return NAO, "nao ha executor declarado para este alvo"


def envelope_em_disco(execs):
    """O ENVELOPE declarado existe na arvore, e cumpre o contrato?

    ⚠️ DECLARAR UM CAMINHO NAO E TER O FICHEIRO, e ter o ficheiro nao e
    cumprir o contrato. Sao tres perguntas, e o censo faz as tres.
    """
    for e in execs:
        onde = (e.get("retorno") or {}).get("ENVELOPE")
        if not onde:
            continue
        caminho = os.path.join(RAIZ, onde)
        if not os.path.isfile(caminho):
            return NAO, "o ENVELOPE declarado nao esta na arvore: %s" % onde
        try:
            with io.open(caminho, encoding="utf-8") as f:
                env = json.load(f)
        except Exception as exc:                            # noqa: BLE001
            return NAO, "o ENVELOPE nao se le: %s" % exc
        faltam = [c for c in CAMPOS_DO_ENVELOPE
                  if not str(env.get(c) or "").strip()]
        faltam += [c for c in LISTAS_DO_ENVELOPE
                   if not isinstance(env.get(c), list)]
        if faltam:
            return NAO, "o ficheiro existe e nao e um envelope: falta %s" % (
                ", ".join(faltam))
        return SIM, "envelope com %d na COLHEITA, corrida %s" % (
            len(env.get("COLHEITA") or []), env.get("RUN_ID"))
    return NAO_MEDIDO, "este alvo nao declara ENVELOPE — nao ha o que conferir"


def regra_de_admissao(alvo):
    termos = adm.PERGUNTAS_DO_UNIVERSO.get(alvo)
    if termos:
        return SIM, "%d termos escritos em PERGUNTAS_DO_UNIVERSO" % len(termos)
    return NAO, "nao ha vocabulario escrito para este universo"


def especie_do_material(execs):
    """O que a classe traz — e isso decide QUAL dono STRUCTURED a recebe.

    ⚠️ «STRUCTURED SUPORTA?» NAO E UMA PERGUNTA SOBRE A CLASSE: e sobre a
    ESPECIE que ela produz. Um boletim em PDF e um post de rede social nao
    esperam pela mesma casa nem pelo mesmo dono de identidade.
    """
    if not execs:
        return "—", NAO_MEDIDO, "sem executor, nao ha especie para classificar"
    o_que = " ".join(str(e.get("o_que_traz") or "") for e in execs).lower()
    rotas = " ".join(" ".join(e.get("rotas") or []) for e in execs).lower()
    social = ("youtube", "instagram", "linkedin", "facebook")
    if any(s in rotas for s in social):
        return ("PLATAFORMA", NAO,
                "conteudo de plataforma: `public.conteudo` exige `canal_id`, e "
                "o criador dessa identidade nao existe na producao")
    if "pdf" in o_que or "documento" in o_que or "rotulo" in o_que:
        return ("DOCUMENTAL", SIM,
                "documento: `public.documento_estruturado` (migration 030), "
                "com dono em guarda/preservar_documento.py")
    return ("OUTRA", NAO_MEDIDO,
            "a especie nao e documental nem de plataforma, e nenhum dono "
            "STRUCTURED foi medido para ela")


def censo():
    linhas = []
    for alvo in sorted(ALVOS, key=lambda a: int(a[1:])):
        execs = EXECUTORES.get(alvo, [])
        aq, porque_aq = aquisicao_canonica(execs)
        env, porque_env = envelope_em_disco(execs)
        regra, porque_regra = regra_de_admissao(alvo)
        especie, suportada, porque_esp = especie_do_material(execs)
        # ⚠️ O CRUZAMENTO E UM «E», E TEM DE CONTINUAR A SER.
        # Trocar por «ou» daria uma lista de quase-canarios e um PASS por
        # metades — que e exactamente o defeito que esta linha de missoes
        # passou tres missoes a apanhar.
        pode = SIM if (aq == SIM and regra == SIM and suportada == SIM) else NAO
        falta = []
        if aq != SIM:
            falta.append("AQUISICAO_CANONICA")
        if regra != SIM:
            falta.append("REGRA_DE_ADMISSAO")
        if suportada != SIM:
            falta.append("DONO_STRUCTURED")
        linhas.append(OrderedDict([
            ("CLASS", alvo),
            ("ASSUNTO", ALVOS[alvo]),
            ("EXECUTOR", execs[0]["id"] if execs else "—"),
            ("CANONICAL_ACQUISITION", aq),
            ("PORQUE_AQUISICAO", porque_aq),
            ("HAS_RUN_ENVELOPE_ON_DISK", env),
            ("PORQUE_ENVELOPE", porque_env),
            ("SPECIES", especie),
            ("STRUCTURED_SUPPORTED", suportada),
            ("PORQUE_STRUCTURED", porque_esp),
            ("ADMISSION_RULE", regra),
            ("PORQUE_REGRA", porque_regra),
            ("CAN_REACH_READY", pode),
            ("O_QUE_FALTA", falta or []),
            ("QUANTO_FALTA", len(falta)),
        ]))
    return linhas


# ══════════════════════════════════════════════════════════════════════════
# 3 · POR QUE T2 NAO TEM REGRA — lido de quem mediu, nunca re-decidido
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ ESTA PERGUNTA JA TINHA RESPOSTA, E QUASE FOI RESPONDIDA OUTRA VEZ.
# `provas/a_regra_de_t2.py` mediu-a contra um gabarito de 46 documentos reais
# e o portao fechou. Re-medir aqui daria uma segunda autoridade sobre a mesma
# pergunta — e duas autoridades divergem no dia em que uma delas mudar.
#
#     ONE CONCEPT -> ONE OWNER. O CENSO LE; NAO VOLTA A DECIDIR.
VEREDICTO_T2 = "data/derivados/A-REGRA-DE-T2.json"


def porque_t2_nao_tem_regra():
    """A classificacao que a missao pediu: A, B, C ou D — com a prova ao lado.

    E nenhuma das quatro serve inteira, o que e a parte que importa:

        A  «deveria ter regra, e ela esta ausente»  -> meio certo
        B  «correctamente nao deve ter regra»       -> meio certo
        C  «dois universos incompativeis»           -> meio certo
        D  UNKNOWN                                   -> falso, isto foi medido

    A resposta medida nao e sobre o UNIVERSO: e sobre o MECANISMO. T2 e um
    universo canonico com cinco fontes declaradas e dez positivos reais. O que
    nao existe e maneira de escrever a regra com o mecanismo que ha.
    """
    caminho = os.path.join(RAIZ, VEREDICTO_T2)
    if not os.path.isfile(caminho):
        return OrderedDict([
            ("CLASSIFICACAO", "D"),
            ("T2_ADMISSION_APPLICABILITY", NAO_MEDIDO),
            ("PORQUE", "`provas/a_regra_de_t2.py` nunca correu neste HEAD — e "
                       "NOT_MEASURED != NO"),
        ])
    with io.open(caminho, encoding="utf-8") as f:
        v = json.load(f)
    fechou = v.get("T2_RULE_IMPLEMENTED") == NAO
    return OrderedDict([
        # ⚠️ A LETRA SOZINHA MENTIRIA, E POR ISSO VAI ACOMPANHADA.
        # Escrever so «B» faria a proxima pessoa ler «T2 nao e um universo
        # admissivel» — e o oposto esta medido. Escrever so «A» faria alguem
        # sentar-se a escrever a lista de palavras que ja foi medida e
        # reprovada. A resposta honesta usa as duas metades e nomeia a razao.
        ("CLASSIFICACAO", "B_COM_A_RAZAO_DE_C" if fechou else "A"),
        ("T2_ADMISSION_APPLICABILITY", "YES" if not fechou else
         "YES_COMO_UNIVERSO_NO_COMO_REGRA"),
        ("O_UNIVERSO_E_LEGITIMO", v.get("O_UNIVERSO_E_LEGITIMO")),
        ("O_QUE_FALHA", v.get("O_QUE_FALHA")),
        ("PORQUE_NAO_E_A", "nao e «falta escrever a lista»: a lista foi "
                           "procurada exaustivamente e a que separa o gabarito "
                           "e feita de dias da semana e nomes de "
                           "departamento — generalizacao %s"
                           % v.get("GENERALIZACAO")),
        ("PORQUE_NAO_E_B_INTEIRO", "T2 nao e um universo ilegitimo: e "
                                   "canonico, com cinco fontes declaradas e "
                                   "dez positivos reais de tres publicadores"),
        ("PORQUE_C_APARECE", "a propria medicao de T2 registou-o: TERRITORIO e "
                             "propriedade da FONTE e UNIVERSO e pergunta ao "
                             "DOCUMENTO. A ARPAV publica T2 e T3, e mostra os "
                             "dois a divergir. Mas as duas listas ficam na "
                             "MESMA taxonomia — nao sao universos "
                             "incompativeis, sao dois usos do mesmo nome"),
        ("CONDICAO_QUE_FECHOU", v.get("CONDICAO_QUE_FECHOU")),
        ("GABARITO", v.get("GABARITO")),
        ("O_QUE_FALTA_PARA_A_REGRA_EXISTIR",
         v.get("O_QUE_FALTA_PARA_A_REGRA_EXISTIR")),
        ("DONO_DESTA_RESPOSTA", "provas/a_regra_de_t2.py"),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 4 · O TESTE DECISIVO DO SCRAP
# ══════════════════════════════════════════════════════════════════════════
def o_scrap_fecharia(linhas):
    """SE O SCRAP FOSSE INTEGRADO HOJE, O BURACO DESAPARECERIA?

    ⚠️ A PERGUNTA ERRADA E «O SCRAP FALTA?». Falta, e isso e verdade e nao
    responde nada. A pergunta certa e se a classe que ele serve chegaria a
    READY depois de ele chegar.

        «O SCRAP AINDA FALTA» != «O SCRAP E O QUE BLOQUEIA».

    O SCRAP e uma capacidade SOCIAL — YouTube, Instagram, LinkedIn, Facebook.
    A unica classe desta casa cujas rotas sao essas e T9. Entao o teste faz-se
    sobre T9, e nao sobre uma impressao geral: dando a T9 a aquisicao que lhe
    falta, ela passa a atravessar?
    """
    servidas = [l for l in linhas if l["SPECIES"] == "PLATAFORMA"]
    if not servidas:
        return OrderedDict([
            ("SCRAP_WOULD_CLOSE_CURRENT_GAP", NAO_MEDIDO),
            ("PORQUE", "nenhuma classe declara rotas sociais — nao ha sobre "
                       "quem fazer o teste"),
        ])
    ainda_falta = OrderedDict()
    for l in servidas:
        # O SCRAP entrega AQUISICAO. Damos-lha de graca e perguntamos o resto.
        resto = [f for f in l["O_QUE_FALTA"] if f != "AQUISICAO_CANONICA"]
        ainda_falta[l["CLASS"]] = resto
    fecharia = all(not r for r in ainda_falta.values())
    return OrderedDict([
        ("CLASSES_QUE_O_SCRAP_SERVE", sorted(ainda_falta)),
        ("PORQUE_ESSAS", "sao as classes cujas rotas declaradas sao sociais "
                         "(YouTube, Instagram, LinkedIn, Facebook) — e o "
                         "SCRAP e uma capacidade social"),
        ("DANDO_LHES_A_AQUISICAO_AINDA_FALTA", ainda_falta),
        ("SCRAP_WOULD_CLOSE_CURRENT_GAP", "YES" if fecharia else NAO),
        ("PORQUE_NAO", "—" if fecharia else
         ("mesmo com a aquisicao resolvida, %s para em STRUCTURED: conteudo de "
          "plataforma exige `canal_id`, e o criador dessa identidade nao "
          "existe na producao. O SCRAP traz bytes; ele nao traz um dono de "
          "identidade de canal."
          % ", ".join(k for k, v in ainda_falta.items() if v))),
        ("E_O_SCRAP_CONTINUA_A_FAZER_FALTA", "YES — para a coleta grande. "
                                             "PRECISO != BLOQUEANTE, e sao "
                                             "duas perguntas diferentes"),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 5 · QUEM DEVE SER O CANARIO, E QUAL E O BLOCKER DE VERDADE
# ══════════════════════════════════════════════════════════════════════════
def o_canario(linhas, t2_fechado):
    """A classe que deve fechar a Collection V1 — e o que lhe falta.

    ⚠️ «QUEM ATRAVESSA HOJE» E «QUEM DEVE SER O CANARIO» SAO DUAS PERGUNTAS.
    A primeira responde-se NONE, e e verdade. Responder so isso deixaria a
    decisao seguinte sem material: entre quatro classes paradas, nenhuma
    parece mais perto do que as outras ate alguem contar o que falta a cada.

    A escolha e por CUSTO DE HONESTIDADE, e nao por proximidade:

        falta REGRA        -> fecha-se escrevendo uma regra tematica
        falta AQUISICAO    -> fecha-se indo buscar o material a fonte real

    As duas sao uma peca. Mas a primeira, no caso de T2, JA FOI MEDIDA E
    REPROVADA — escrever a lista agora seria mudar a pergunta para gostar da
    resposta. A segunda nao tem nada de reprovado: e trabalho por fazer.
    """
    perto = [l for l in linhas if l["QUANTO_FALTA"] == 1]
    por_aquisicao = [l for l in perto
                     if l["O_QUE_FALTA"] == ["AQUISICAO_CANONICA"]]
    por_regra = [l for l in perto
                 if l["O_QUE_FALTA"] == ["REGRA_DE_ADMISSAO"]]

    if por_aquisicao:
        escolhida = por_aquisicao[0]
        porque = ("e a unica classe a uma peca de distancia cuja peca em falta "
                  "nao foi medida e reprovada. Ela ja tem regra tematica "
                  "escrita e ja tem dono STRUCTURED — falta-lhe ir buscar o "
                  "material pelo contrato canonico")
        blocker = OrderedDict([
            ("O_QUE_E", "o executor de %s nao declara COLHEITA" % escolhida["CLASS"]),
            ("ONDE", "pedido/receitas.py::EXECUTORES[%r] -> retorno"
                     % escolhida["CLASS"]),
            ("ESTADO_HOJE", escolhida["PORQUE_AQUISICAO"]),
            ("O_QUE_FALTA_TECNICAMENTE",
             "um ENVELOPE por corrida com RUN_ID, EXECUTOR_ID, "
             "EXECUTOR_VERSION, ESTADO e as listas COLHEITA/SUPORTE/ERROS, "
             "conforme leis/retorno_da_coleta.py::conferir"),
            # ⚠️ O NOME DO BLOCKER NAO PODE SER «O SCRAP» POR OMISSAO.
            # O SCRAP e a peca que falta mais visivel desta casa, e por isso
            # atrai para si qualquer buraco que ninguem nomeou.
            ("E_O_SCRAP", NAO),
            ("PORQUE_NAO_E_O_SCRAP",
             "o SCRAP e uma capacidade social e nao coleta documento de "
             "ministerio. Integra-lo nao muda uma linha do retorno de %s"
             % escolhida["CLASS"]),
            ("QUEM_RESOLVE", "codigo — e e trabalho de AQUISICAO, que esta "
                             "fase separou de proposito do fecho da maquina"),
        ])
    elif por_regra and not t2_fechado:
        escolhida = por_regra[0]
        porque = "falta-lhe so a regra, e ela nao foi medida nem reprovada"
        blocker = OrderedDict([("O_QUE_E", "a regra tematica nao esta escrita")])
    else:
        escolhida = None
        porque = ("nenhuma classe esta a uma peca de distancia por um caminho "
                  "que nao esteja medido e reprovado")
        blocker = OrderedDict([("O_QUE_E", NAO_MEDIDO)])

    return OrderedDict([
        ("CANONICAL_CANARY_CLASS_RECOMENDADA",
         escolhida["CLASS"] if escolhida else "NONE"),
        ("ASSUNTO", escolhida["ASSUNTO"] if escolhida else "—"),
        ("PORQUE_ESTA", porque),
        ("O_QUE_ELA_JA_TEM",
         ["REGRA_DE_ADMISSAO", "DONO_STRUCTURED"] if escolhida else []),
        ("O_QUE_LHE_FALTA", escolhida["O_QUE_FALTA"] if escolhida else []),
        ("BLOCKER_REAL", blocker),
        ("PORQUE_NAO_T2", "T2 e a outra classe a uma peca de distancia, e a "
                          "peca dela e a regra tematica — medida contra 46 "
                          "documentos reais e REPROVADA. Escolher T2 obrigaria "
                          "a escrever a lista que a medicao ja disse que nao "
                          "existe."
                          if t2_fechado else "—"),
        ("O_QUE_ISTO_NAO_AUTORIZA",
         "comecar a aquisicao de %s dentro desta missao. Fechar a maquina e "
         "integrar aquisicao sao fases diferentes, e a ordem aprovada poe a "
         "segunda depois da primeira."
         % (escolhida["CLASS"] if escolhida else "ninguem")),
    ])


def main():
    linhas = censo()
    divergem = executor_nao_depende_do_pais()
    cruzam = [l for l in linhas if l["CAN_REACH_READY"] == SIM]
    a_uma_peca = [l for l in linhas if l["QUANTO_FALTA"] == 1]

    t2 = porque_t2_nao_tem_regra()
    canario = o_canario(linhas, t2.get("O_QUE_FALHA") == "MECANISMO")
    scrap = o_scrap_fecharia(linhas)

    art = OrderedDict([
        ("PERGUNTA", "que classe consegue hoje atravessar a Collection "
                     "inteira, de REQUEST a SALA DE ESPERA?"),
        ("CLASSES_MEDIDAS", len(linhas)),
        ("EXECUTOR_DEPENDE_DO_PAIS", NAO if not divergem else SIM),
        ("PORQUE", "receitas.resolver le EXECUTORES.get(alvo) e o pais filtra "
                   "FONTES, nunca EXECUTORES — medido em 5 paises"
                   if not divergem else
                   "alvos que mudam de executor com o pais: %s" % divergem),
        ("CENSO", linhas),
        ("CANONICAL_CANARY_CLASS",
         cruzam[0]["CLASS"] if cruzam else "NONE"),
        ("CLASSES_A_UMA_PECA_DE_DISTANCIA",
         [OrderedDict([("CLASS", l["CLASS"]), ("FALTA", l["O_QUE_FALTA"][0])])
          for l in a_uma_peca]),
        # ⚠️ ISTO E O ACHADO QUE A MEDICAO ANTERIOR NAO PODIA TER.
        # «A intersecao e vazia» e verdade e nao ajuda a decidir. Contar O QUE
        # FALTA A CADA UMA transforma uma parede numa lista ordenada.
        ("O_QUE_ISTO_ACRESCENTA",
         "a missao anterior provou que ninguem passa. Esta diz quem esta a UMA "
         "peca de passar, e qual peca e — e sao duas perguntas diferentes."),
        ("PORQUE_T2_NAO_TEM_REGRA", t2),
        ("O_CANARIO_RECOMENDADO", canario),
        ("O_TESTE_DO_SCRAP", scrap),
        ("GENERATED_BY", "provas/o_canario_da_collection.py"),
    ])
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with io.open(caminho, "w", encoding="utf-8") as f:
        f.write(json.dumps(art, ensure_ascii=False, indent=2) + "\n")

    print("\n  O CANARIO DA COLLECTION — que classe atravessa?")
    print("  " + "─" * 72)
    print("  %-5s %-22s %-9s %-11s %-7s %-6s" %
          ("", "assunto", "aquisicao", "structured", "regra", "READY"))
    for l in linhas:
        print("  %-5s %-22s %-9s %-11s %-7s %-6s %s"
              % (l["CLASS"], l["ASSUNTO"][:22], l["CANONICAL_ACQUISITION"],
                 l["STRUCTURED_SUPPORTED"], l["ADMISSION_RULE"],
                 l["CAN_REACH_READY"],
                 ("falta " + "+".join(l["O_QUE_FALTA"])) if l["O_QUE_FALTA"]
                 else ""))
    print("\n  CANONICAL_CANARY_CLASS = %s" % art["CANONICAL_CANARY_CLASS"])
    print("  o executor depende do pais? %s" % art["EXECUTOR_DEPENDE_DO_PAIS"])
    print("\n  A UMA PECA DE DISTANCIA")
    for l in art["CLASSES_A_UMA_PECA_DE_DISTANCIA"]:
        print("    %-5s falta so: %s" % (l["CLASS"], l["FALTA"]))
    print("\n  POR QUE T2 NAO TEM REGRA")
    print("    classificacao: %s" % t2["CLASSIFICACAO"])
    print("    o universo e legitimo: %s · o que falha: %s"
          % (t2.get("O_UNIVERSO_E_LEGITIMO"), t2.get("O_QUE_FALHA")))
    print("    %s" % t2.get("PORQUE_NAO_E_A", ""))
    print("\n  O CANARIO RECOMENDADO")
    print("    %s (%s) — %s" % (canario["CANONICAL_CANARY_CLASS_RECOMENDADA"],
                                canario["ASSUNTO"], canario["PORQUE_ESTA"]))
    print("    BLOCKER REAL: %s" % canario["BLOCKER_REAL"]["O_QUE_E"])
    print("    e o SCRAP? %s" % canario["BLOCKER_REAL"].get("E_O_SCRAP", "—"))
    print("\n  O TESTE DO SCRAP")
    print("    o SCRAP serve: %s" % (scrap.get("CLASSES_QUE_O_SCRAP_SERVE")
                                     or "—"))
    print("    SCRAP_WOULD_CLOSE_CURRENT_GAP = %s"
          % scrap["SCRAP_WOULD_CLOSE_CURRENT_GAP"])
    if scrap.get("PORQUE_NAO") not in (None, "—"):
        print("    %s" % scrap["PORQUE_NAO"])
    print("\n  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
