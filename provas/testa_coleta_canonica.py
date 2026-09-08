#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVAS PONTA A PONTA DA COLETA CANONICA.

    py provas/testa_coleta_canonica.py

Sete casos, e cada um existe porque a alternativa ja custou caro nesta casa ou
custa caro em qualquer casa. Nao sao testes de cobertura: sao as sete maneiras
conhecidas de este caminho mentir.

    1  o pedido em portugues chega ate ao fim
    2  item fora do universo: o bruto fica, a rejeicao fica escrita com motivo
    3  prova insuficiente da NAO_SEI, e nunca NAO
    4  falha de ferramenta da ERRO, e nunca REJEITADO
    5  o mesmo bruto vale para dois universos, com decisoes independentes
    6  trocar de executor nao muda uma linha em quem pede
    7  nada aponta para o que foi removido
"""

import ast
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

from pedido import de_uma_frase, Pedido, PedidoInvalido  # noqa: E402
from receitas import resolver  # noqa: E402
import orquestrador as orq  # noqa: E402
import admissao as adm  # noqa: E402

FALHAS = []


def prova(nome, ok, detalhe=""):
    print(f"  {'PASS' if ok else 'FALHA':5s}  {nome}" + (f"  — {detalhe}" if not ok and detalhe else ""))
    if not ok:
        FALHAS.append(nome)


# ── 1 · o pedido atravessa o caminho todo ───────────────────────────────────
p = de_uma_frase("colete materiais de pesquisadores")
prova("1_pedido_em_portugues_vira_alvo", p.alvo == "T7", f"deu {p.alvo}")
plano = resolver(p)
prova("1_plano_encontra_executor", plano.da_para_correr)
recibo = orq.correr(p, seco=True)
prova("1_corrida_devolve_recibo_com_versao",
      recibo["STATUS"] == "OK" and recibo["ACTOR_VERSION"] != "NOT_PRESERVED",
      str(recibo.get("ACTOR_VERSION")))
prova("1_recibo_diz_quem_correu_e_quando",
      all(recibo.get(k) for k in ("ACTOR", "STARTED_AT", "FINISHED_AT", "QUERY")))

item_bom = {"id": "e2e-1", "texto": "Ensaio de campo com DOI publicado",
            "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
d = adm.decidir(item_bom, "T7", corrida=recibo["RUN_ID"])
prova("1_item_bom_passa_a_porta", d.resultado == adm.SIM, d.motivo)
saida = adm.pronto_para_inteligencia(item_bom, d)
prova("1_saida_e_o_contrato_da_fronteira",
      saida["ESTADO"] == "PRONTO_PARA_INTELIGENCIA")
prova("1_a_saida_nao_cita_scraper_nem_api",
      not any(x in json.dumps(saida).lower()
              for x in ("scraper", "apify", "playwright", ".py", "requests")))

# ── 2 · fora do universo: o bruto fica, o nao fica escrito ──────────────────
# ESTE CASO MUDOU DE FORMA, e a mudanca e o ponto.
# Ele dizia «Promocao de tratores com desconto» e esperava NAO. Passava — mas
# passava pelo motivo errado: a porta dava NAO por NENHUMA palavra ter casado.
# Isso e ausencia de evidencia a fazer de evidencia de ausencia, e com um lexico
# incompleto transforma cada buraco do vocabulario numa rejeicao.
# Agora o item traz prova POSITIVA de pertencer a outro universo — fala de
# lancamento e campanha, que e T9 — e por isso o NAO em T7 e legitimo.
fora = {"id": "e2e-2",
        "texto": "lancio del prodotto: nuova campagna commerciale",
        "source_id": "IT-T9-004", "fact_time": "2026-05-03"}
d2 = adm.decidir(fora, "T7", corrida="e2e")
prova("2_item_de_outro_universo_e_NAO_com_prova",
      d2.resultado == adm.NAO and "achado_noutro" in d2.evidencia,
      f"{d2.resultado} · {d2.motivo[:70]}")
prova("2_a_rejeicao_tem_motivo_escrito", len(d2.motivo) > 30)
prova("2_a_rejeicao_diz_a_regra_e_a_versao", bool(d2.regra) and bool(d2.versao))
prova("2_o_bruto_nao_foi_destruido",
      fora.get("texto") == "lancio del prodotto: nuova campagna commerciale")

# ── 3 · sem prova nao vira nao ──────────────────────────────────────────────
sem_data = {"id": "e2e-3", "texto": "Ensaio com DOI", "source_id": "IT-T7-002"}
d3 = adm.decidir(sem_data, "T7")
prova("3_falta_de_prova_da_NAO_SEI", d3.resultado == adm.NAO_SEI, d3.resultado)
prova("3_NAO_SEI_nao_e_NAO", d3.resultado != adm.NAO)

sem_origem = {"id": "e2e-3b", "texto": "Ensaio", "fact_time": "2026-01-01"}
prova("3_item_sem_origem_da_NAO_SEI",
      adm.decidir(sem_origem, "T7").resultado == adm.NAO_SEI)

# ── 4 · falha de ferramenta nao e rejeicao ──────────────────────────────────
quebrado = {"id": "e2e-4", "erro_de_leitura": "TimeoutError",
            "source_id": "IT-T7-003", "fact_time": "2026-01-01"}
d4 = adm.decidir(quebrado, "T7")
prova("4_falha_de_ferramenta_da_ERRO", d4.resultado == adm.ERRO, d4.resultado)
prova("4_ERRO_nao_e_REJEITADO", d4.resultado != adm.NAO)
prova("4_o_erro_guarda_a_mensagem", "TimeoutError" in json.dumps(d4.evidencia))

# ── 5 · o mesmo bruto, dois universos, decisoes independentes ───────────────
ambiguo = {"id": "e2e-5",
           "texto": "Universidade apresenta ensaio de campo no lancamento do produto",
           "source_id": "IT-T7-004", "fact_time": "2026-02-02"}
dA = adm.decidir(ambiguo, "T7")
dB = adm.decidir(ambiguo, "T9")
prova("5_decisoes_sao_por_par_item_universo", dA.universo != dB.universo)
prova("5_ambos_avaliados_sem_se_atropelarem",
      dA.resultado in adm.RESULTADOS and dB.resultado in adm.RESULTADOS)
prova("5_relevancia_nao_e_booleano_no_item", "relevante" not in ambiguo)

# ── 6 · trocar o executor nao mexe em quem pede ─────────────────────────────
import receitas  # noqa: E402
antes = receitas.EXECUTORES["T7"][0]
receitas.EXECUTORES["T7"] = [dict(antes, id="outro-executor",
                                  roda=["coleta/outro_qualquer.py"])]
p6 = de_uma_frase("colete materiais de pesquisadores")   # o pedido e IGUAL
plano6 = resolver(p6)
prova("6_o_pedido_nao_mudou", p6.para_json() == p.para_json())
prova("6_o_plano_aponta_para_o_executor_novo",
      plano6.executores[0]["id"] == "outro-executor")
receitas.EXECUTORES["T7"] = [antes]

# ── 7 · nada aponta para o que foi removido ─────────────────────────────────
import subprocess  # noqa: E402
REMOVIDOS = (".github/workflows/adama-es-gate.yml",)
restos = []
for r in REMOVIDOS:
    saida_git = subprocess.run(["git", "-C", str(RAIZ), "grep", "-l", "-F", r],
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace").stdout
    # NAO CONTA quem guarda o proprio caminho por dever de oficio: o ficheiro
    # guardado (que E o caminho), a documentacao que explica a mudanca, o mapa
    # gerado (que descreve o repositorio) — e este teste, que tem de escrever o
    # nome para o poder procurar. Sem esta linha, o teste encontrava-se a si
    # mesmo e reprovava para sempre.
    restos += [l for l in saida_git.splitlines()
               if not l.startswith(("guarda/es/", "docs/", "AGENTS.md",
                                    "provas/testa_coleta_canonica.py",
                                    "system-map/data/", "italia-portale/client/"))]
prova("7_nada_aponta_para_o_que_saiu", not restos, ", ".join(restos[:3]))


# ══ A ITALIA NAO PODE RECEBER O VOCABULARIO DE OUTRO PAIS ══════════════════
# Doze provas. Nasceram de um achado medido: a porta de admissao decidia sobre
# item ITALIANO com 28 palavras em PORTUGUES. Contra o unico texto italiano real
# desta arvore, UMA casava. Vinte das 28 mudam em italiano.
#
#     A BUSCA FOI CORRIGIDA E A PORTA FICOU PARA TRAS.
#
# O efeito e o pior possivel: nenhuma palavra casa, e o item nao vira NAO_SEI —
# vira «nao pertence a este universo». Uma peneira que fala outra lingua rejeita
# tudo, e com ar de quem julgou.
import re as _re
import sensor_medir as _sm

# marcas que so existem numa lingua. `evento`, `concorrente`, `decreto`, `fungo`
# e `registro` servem as duas e por isso NAO estao aqui: termo internacional
# legitimo nao e contaminacao.
SO_PORTUGUES = _re.compile(
    r'^(estudo|pesquisa|revista|artigo|universidade|instituto|publicacao|'
    r'lancamento|campanha|produto|anuncio|autorizacao|rotulo|bula|praga|'
    r'doenca|inseto|infestacao|sintoma)$')
SO_ESPANHOL = _re.compile(r'^(repilo|olivar|jornada|septoriosis|trigo)$')
SO_FRANCES = _re.compile(r'^(mildiou|septoriose|webinaire|vigne|ble)$')
SO_ITALIANO = _re.compile(
    r'^(studio|ricerca|rivista|articolo|universita|istituto|pubblicazione|'
    r'convegno|sperimentazione|tesi|lancio|campagna|prodotto|annuncio|novita|'
    r'fiera|autorizzazione|etichetta|foglietto|registrazione|gazzetta|'
    r'parassita|malattia|insetto|infestazione|sintomo|avversita|patogeno)$')

TODAS_DA_PORTA = [w for lista in adm.PERGUNTAS_DO_UNIVERSO.values() for w in lista]

# V1/V2 · a Italia nao recebe termo exclusivo de FR nem de ES
prova("V1_porta_sem_termo_so_frances",
      not [w for w in TODAS_DA_PORTA if SO_FRANCES.match(w)],
      "termo exclusivamente frances na porta que decide sobre item italiano")
prova("V2_porta_sem_termo_so_espanhol",
      not [w for w in TODAS_DA_PORTA if SO_ESPANHOL.match(w)],
      "termo exclusivamente espanhol na porta")

# V3 · termo internacional legitimo nao e falso positivo
prova("V3_termo_internacional_e_permitido",
      "doi" in TODAS_DA_PORTA and "orcid" in TODAS_DA_PORTA,
      "`doi` e `orcid` nao tem lingua e tem de continuar a valer")

# V4 · a porta fala italiano
italianas = [w for w in TODAS_DA_PORTA if SO_ITALIANO.match(w)]
prova("V4_a_porta_fala_italiano", len(italianas) >= 20,
      f"so {len(italianas)} palavras italianas na porta — antes eram 0")

# V5 · e continua a falar portugues, de proposito
prova("V5_o_portugues_nao_foi_apagado",
      bool([w for w in TODAS_DA_PORTA if SO_PORTUGUES.match(w)]),
      "ha item nesta casa que vem em portugues; traduzir teria apagado esses")

# V6 · a busca nao e a admissao
prova("V6_busca_nao_e_admissao",
      set(TODAS_DA_PORTA) != set(_sm.OBSERVACAO_CAMPO),
      "encontrar um material e decidir se ele serve sao perguntas diferentes")

# V7 · sem casamento nao vira NAO quando falta prova de leitura
_vazio = adm.decidir({"id": "v7", "source_id": "IT-X", "fact_time": "2026-01-01"}, "T7")
prova("V7_sem_texto_nao_vira_nao", _vazio.resultado != adm.NAO,
      f"item sem texto saiu {_vazio.resultado}; nao pode ser NAO")

# V8 · pais desconhecido nao vira Italia
prova("V8_pais_desconhecido_nao_vira_italia",
      "NAO SEI" in orq.novo_run_id(de_uma_frase("colete concorrentes"))
      or orq.novo_run_id(de_uma_frase("colete concorrentes")).startswith("XX-"),
      "pedido sem pais tem de ficar XX, nunca IT por omissao")

# V9 · o item italiano passa a porta
_it = {"id": "v9", "texto": "convegno sulla ricerca in campo, articolo pubblicato",
       "source_id": "IT-T7-001", "fact_time": "2026-05-02"}
prova("V9_item_italiano_passa_a_porta",
      adm.decidir(_it, "T7").resultado == adm.SIM,
      "um texto italiano de ciencia tem de ser reconhecido como ciencia")

# V10 · e o mesmo texto em portugues tambem
_pt = {"id": "v10", "texto": "artigo de pesquisa publicado na revista",
       "source_id": "BR-X", "fact_time": "2026-05-02"}
prova("V10_item_portugues_continua_a_passar",
      adm.decidir(_pt, "T7").resultado == adm.SIM)

# V11 · a versao da regra muda quando o vocabulario muda
prova("V11_versao_da_regra_existe", bool(adm.VERSAO_DA_REGRA),
      "sem versao nao da para reprocessar so o que a regra antiga decidiu")

# V12 · o consumidor consegue provar que vocabulario usou
_d = adm.decidir(_it, "T7")
prova("V12_a_decisao_diz_com_que_regua_decidiu",
      bool(_d.regra) and bool(_d.versao) and bool(_d.evidencia),
      "cada decisao tem de dizer a regra, a versao e a prova")


# ══ AUSENCIA DE MATCH NAO E PROVA ══════════════════════════════════════════
# A lei canonica desta casa: AUSENCIA DE EVIDENCIA NAO E EVIDENCIA DE AUSENCIA.
# A porta violava-a — devolvia NAO sempre que nenhuma palavra casava. Com um
# vocabulario incompleto, isso transforma cada buraco do lexico numa rejeicao
# com ar de julgamento, e a coleta encolhe sozinha sem ninguem decidir.
_nada = {"id": "L1", "texto": "un testo qualunque senza parole conosciute",
         "source_id": "IT-L1", "fact_time": "2026-01-01"}
_outro = {"id": "L2", "texto": "lancio del prodotto: nuova campagna",
          "source_id": "IT-L2", "fact_time": "2026-01-01"}

prova("L1_sem_match_nenhum_da_NAO_SEI",
      adm.decidir(_nada, "T7").resultado == adm.NAO_SEI,
      "nao achar palavra nenhuma prova que o lexico nao chegou, nao que o item "
      "nao pertence")
prova("L2_nao_exige_prova_positiva",
      adm.decidir(_outro, "T7").resultado == adm.NAO,
      "NAO so quando o item fala claramente de outro universo")
prova("L3_o_nao_diz_onde_o_item_pertence",
      "achado_noutro" in adm.decidir(_outro, "T7").evidencia,
      "um NAO tem de mostrar a prova que o sustenta")
prova("L4_a_versao_da_lei_subiu",
      adm.VERSAO_DA_REGRA != "1",
      "a lei mudou; sem subir a versao nao ha como reabrir o que a versao 1 "
      "rejeitou por ausencia")

# ══ AS CONTAS DA SEMANTICA TEM DE FECHAR ═══════════════════════════════════
# Os numeros «482 termos» e «68 termos» andaram a circular e nao somavam,
# porque se contava tudo o que parecia palavra em dezassete listas diferentes.
# Uma conta que nao fecha nao e uma medida: e um palpite com ar de numero.
_SEMANTICA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), 'system-map', 'data', 'semantica-it.generated.json')
if os.path.exists(_SEMANTICA):
    _S = json.load(open(_SEMANTICA, encoding='utf-8'))
    _c = _S['COUNTS']
    prova("T1_o_censo_semantico_fecha",
          _c.get('todas_as_contas_fecham') is True
          and sum(_c['por_papel'].values()) == _c['termos_ao_todo'],
          "a soma dos papeis tem de dar o total de termos; se nao der, "
          "perderam-se termos pelo caminho e ninguem se queixou")
else:
    prova("T1_o_censo_semantico_fecha", False,
          "falta system-map/data/semantica-it.generated.json — corre o censo")

# ══ O VOCABULARIO DE BUSCA QUE A ITALIA USA DE FACTO ════════════════════════
import sensor_coleta as sc  # noqa: E402

_LOTES_IT = ('C', 'D', 'E')
_fora_it = [c for L in _LOTES_IT for c in sc.LOTES[L] if not c.startswith('IT-')]
prova("T2_os_lotes_italianos_sao_so_italianos",
      not _fora_it,
      "os lotes C, D e E sao a rota italiana; um recorte estrangeiro aqui "
      "dentro entra sem ninguem reparar. Intrusos: %s" % (_fora_it or 'nenhum'))

# A regua que MEDE e trilingue de proposito — nao e o mesmo que a regua que
# BUSCA. Buscar em espanhol num projeto italiano gasta dinheiro a trazer o pais
# errado; reconhecer uma palavra espanhola num texto que ja se tem nao gasta
# nada e ate ajuda. Sao duas coisas, e o mapa tem de continuar a separa-las.
import sensor_medir as sm  # noqa: E402

prova("T3_medir_nao_e_buscar",
      sm is not sc and hasattr(sm, '_tem'),
      "a regua de classificacao e um modulo separado do sensor de busca; "
      "junta-las poria vocabulario espanhol dentro de uma busca paga")


# ══ A PORTA DAS TRASEIRAS DO ESCOPO ════════════════════════════════════════
# Os lotes A e B foram tirados do menu do GitHub quando se viu que levavam
# recortes espanhois e franceses. O menu escondeu o botao; o codigo continuou
# a aceitar `videos('A')` — e 'A' era ate o valor por omissao da linha de
# comando. ESCONDER O BOTAO NAO E PROTECAO. Estas tres provas verificam o
# portao no CODIGO, que e o unico sitio que nao depende de ninguem se lembrar.
import sensor_coleta as sc  # noqa: E402

_dentro_a, _fora_a = sc.recortes_no_escopo('A')
prova("T4_lote_estrangeiro_e_filtrado_pelo_codigo",
      _fora_a and all(not c.startswith('IT-') for c in _fora_a)
      and all(c.startswith('IT-') for c in _dentro_a),
      "chamar o lote A com pais IT tem de devolver so os recortes italianos, "
      "com os outros nomeados — nao silenciosamente")

prova("T5_o_valor_por_omissao_e_italiano",
      all(c.startswith('IT-') for c in sc.LOTES['C']),
      "quem esquece o argumento do lote apanha o lote por omissao; ele tem de "
      "ser 100% italiano")

prova("T6_o_conteudo_estrangeiro_nao_foi_apagado",
      any(not c.startswith('IT-') for c in sc.LOTES['A'])
      and all(sc.TERMOS.get(c) for c in sc.LOTES['A']),
      "filtrar nao e apagar: os recortes ES/FR e os seus termos continuam "
      "guardados para repetir coletas antigas")

prova("T7_correr_fora_do_escopo_exige_pedido_explicito",
      sc.recortes_no_escopo('A', permitir_fora=True)[0] == sc.LOTES['A'],
      "ha uma saida, mas so por pedido escrito (--fora-do-escopo), e fica no log")


# ══ O ESPANHOL DE voz.py NAO CHEGA A ITALIA ════════════════════════════════
# `medidas/voz.py` guarda vocabulario espanhol (VOCAB_ISSUE ES:5, VOCAB_TIPO
# ES:4). Isso estava marcado «fora do escopo» — uma opiniao, nao uma medida.
# Esta prova mede: nenhuma gaveta da rota italiana importa `voz`. Se um dia
# alguem a importar, esta prova cai no mesmo dia, e nao meses depois.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GAVETAS_IT = ['coleta', 'admissao', 'orquestrador', 'pedido', 'regras', 'leis']
_importam_voz = []
for _g in _GAVETAS_IT:
    for _dir, _, _fs in os.walk(os.path.join(_RAIZ, _g)):
        for _f in _fs:
            if not _f.endswith('.py'):
                continue
            _p = os.path.join(_dir, _f)
            try:
                _arv = ast.parse(open(_p, encoding='utf-8').read())
            except Exception:
                continue
            for _n in ast.walk(_arv):
                if isinstance(_n, ast.Import) and any(a.name == 'voz' for a in _n.names):
                    _importam_voz.append(os.path.relpath(_p, _RAIZ))
                if isinstance(_n, ast.ImportFrom) and _n.module == 'voz':
                    _importam_voz.append(os.path.relpath(_p, _RAIZ))

prova("T8_a_rota_italiana_nao_importa_voz",
      not _importam_voz,
      "voz.py tem vocabulario espanhol; se a rota italiana passar a importa-lo, "
      "esse espanhol entra na classificacao italiana. Importam hoje: %s"
      % (_importam_voz or 'ninguem'))


# ══ A SAIDA DE EMERGENCIA NAO PODE SER UM ATALHO ═══════════════════════════
# `--fora-do-escopo` existe para o caso raro de alguem querer mesmo repetir uma
# coleta antiga de Espanha ou Franca. Isso e legitimo numa ferramenta generica.
#
# O que NAO pode acontecer e a rota italiana conseguir aciona-lo. Uma porta de
# emergencia com a chave pendurada ao lado deixa de ser porta de emergencia.
#
#     UMA EXCECAO QUE QUALQUER CAMINHO CONSEGUE PEDIR NAO E EXCECAO: E A REGRA.
_FUGA = ('--fora-do-escopo', 'SINTONIA_FORA_DO_ESCOPO')


def _quem_diz(palavras, pastas, saltar=()):
    """Que ficheiros escrevem uma destas palavras?"""
    achados = []
    for g in pastas:
        base = os.path.join(_RAIZ, g)
        if os.path.isfile(base):
            alvos = [base]
        else:
            alvos = [os.path.join(d, f)
                     for d, _, fs in os.walk(base) for f in fs
                     if f.endswith(('.py', '.yml', '.yaml', '.sh'))]
        for p in alvos:
            rel = os.path.relpath(p, _RAIZ).replace('\\', '/')
            if rel in saltar:
                continue
            try:
                txt = open(p, encoding='utf-8').read()
            except Exception:
                continue
            if any(w in txt for w in palavras):
                achados.append(rel)
    return achados


# A ferramenta onde a saida vive, e as provas que a testam, sao os unicos
# sitios onde a palavra pode aparecer. Tudo o resto e um atalho.
_PERMITIDO = ('regras/sensor_coleta.py', 'provas/testa_coleta_canonica.py')

_botoes = _quem_diz(_FUGA, ['.github/workflows'], _PERMITIDO)
prova("T9_nenhum_botao_pede_fora_do_escopo",
      not _botoes,
      "um botao do GitHub que ja traz a excecao escrita e uma coleta "
      "estrangeira a um clique de distancia. Botoes que a pedem: %s"
      % (_botoes or 'nenhum'))

_rota = _quem_diz(_FUGA, ['coleta', 'admissao', 'orquestrador', 'pedido',
                          'leis', 'regras'], _PERMITIDO)
prova("T10_a_rota_italiana_nao_aciona_a_saida",
      not _rota,
      "nenhum ficheiro do caminho canonico pode pedir a excecao. Pedem: %s"
      % (_rota or 'nenhum'))

prova("T11_a_saida_so_atende_a_quem_a_escreve_por_fora",
      not sc.fora_do_escopo_pedido(),
      "numa corrida normal, sem ninguem escrever nada, a saida tem de estar "
      "fechada — e o valor por omissao tem de ser o cofre, nao a porta aberta")


# ══ O CORTE DO PDF, DESENHADO COMO CORTE ═══════════════════════════════════
# O maior buraco medido da Italia nao e de vocabulario: e que a evidencia mais
# rica esta fechada dentro de PDF e nunca vira texto. Se isso nao estiver no
# mapa, volta a ser descoberto do zero daqui a tres meses.
_CORPUS = os.path.join(_RAIZ, 'system-map', 'data', 'corpus-it.generated.json')
_MAPA = os.path.join(_RAIZ, 'system-map', 'data', 'state.generated.json')

if os.path.exists(_CORPUS):
    _C = json.load(open(_CORPUS, encoding='utf-8'))
    _B = _C['BRUTO_POR_LER']
    prova("T12_o_censo_do_corpo_fecha",
          sum(g['ficheiros'] for g in _C['POR_GAVETA'].values())
          == _C['TOTAIS']['FICHEIROS_ITALIANOS'],
          "as gavetas tem de somar o total de ficheiros; uma medicao que perde "
          "um ficheiro sem se queixar e pior que uma que falha alto")

    prova("T13_guardado_e_legivel_sao_dois_numeros",
          _B['PDF_COM_TEXTO_DERIVADO'] + _B['PDF_SEM_TEXTO_DERIVADO']
          == _B['FICHEIROS'],
          "quantos PDF tem texto e quantos nao tem tem de somar o total; sem "
          "isso volta-se a dizer «corpus» e a juntar o guardado com o legivel")

    prova("T14_os_caracteres_dentro_do_PDF_continuam_nao_medidos",
          isinstance(_B['CARACTERES'], str) and 'NAO MEDIDO' in _B['CARACTERES'],
          "62,7 MB de PDF NAO e prova de milhoes de caracteres. Megabyte nao e "
          "caractere: um PDF de 6 MB tanto pode ser cinquenta paginas escritas "
          "como uma unica fotografia digitalizada. Enquanto ninguem os abrir, "
          "o numero e NAO MEDIDO — e escreve-se assim")
else:
    for _t in ('T12_o_censo_do_corpo_fecha',
               'T13_guardado_e_legivel_sao_dois_numeros',
               'T14_os_caracteres_dentro_do_PDF_continuam_nao_medidos'):
        prova(_t, False, 'falta system-map/data/corpus-it.generated.json')

if os.path.exists(_MAPA):
    _M = json.load(open(_MAPA, encoding='utf-8'))
    _corte = [e for e in _M['EDGES'] if e.get('type') == 'DERIVA_TEXTO']
    prova("T15_o_corte_esta_desenhado_no_mapa",
          len(_corte) == 1 and _corte[0]['from'] == 'C-IT-PDF-BRUTO'
          and not _corte[0].get('evidence'),
          "o passo que abre o PDF nao existe; a seta tem de estar la e tem de "
          "estar CINZENTA, sem uma linha de codigo a prova-la. Buraco que nao "
          "se desenha volta a ser descoberto do zero")

    _bruto = [n for n in _M['NODES'] if n['id'] == 'C-IT-PDF-BRUTO']
    prova("T16_a_peca_do_bruto_nao_promete_milhoes",
          _bruto and not any('milhõe' in str(f).lower() and 'NÃO' not in str(f)
                             for f in _bruto[0].get('facts', [])),
          "a peca conta ficheiros e megabytes; se ela comecar a falar de "
          "milhoes de caracteres, voltou a juntar dois factos diferentes")
else:
    for _t in ('T15_o_corte_esta_desenhado_no_mapa',
               'T16_a_peca_do_bruto_nao_promete_milhoes'):
        prova(_t, False, 'falta system-map/data/state.generated.json')


# ══ COBERTURA NAO E PRECISAO ═══════════════════════════════════════════════
_RECALL = os.path.join(_RAIZ, 'system-map', 'data', 'recall-porta-it.generated.json')
if os.path.exists(_RECALL):
    _R = json.load(open(_RECALL, encoding='utf-8'))
    prova("T17_o_recall_diz_o_que_nao_prova",
          'NAO SEI' in _R.get('O_QUE_ISTO_NAO_DIZ', ''),
          "42 SIM em 49 e COBERTURA: quantos a peneira apanha. Sem alguem que "
          "leia italiano a marcar a mao o que devia passar, se as 42 estao "
          "CERTAS continua NAO SEI, e o ficheiro tem de dizer isso em voz alta")
else:
    prova("T17_o_recall_diz_o_que_nao_prova", False,
          'falta system-map/data/recall-porta-it.generated.json')


# ══ NENHUM PAIS FORA DA ITALIA FOI TOCADO ══════════════════════════════════
# O escopo desta missao e absoluto: so Italia. Espanha e Franca sao lidas para
# provar que nao vazam, e mais nada. Esta prova mede isso no proprio historico
# — a unica testemunha que nao depende de ninguem se lembrar.
import subprocess  # noqa: E402

_BASE = 'origin/main'
try:
    _mudados = subprocess.run(
        ['git', '-C', _RAIZ, 'diff', '--name-only', _BASE + '...HEAD'],
        capture_output=True, text=True, encoding='utf-8').stdout.split()
except Exception:
    _mudados = []

_OUTROS = ('data/samples/ES-', 'data/samples/FR-', 'coleta/es/',
           'data/collection-store/spain', 'data/collection-store/france')
_tocados = [f for f in _mudados
            if any(f.replace('\\', '/').startswith(p) for p in _OUTROS)]
# Se o git nao respondeu, esta prova passa por nao ter medido nada — e uma
# prova que passa por nao medir e pior do que nenhuma prova.
prova("T18_nenhum_pais_fora_da_italia_foi_alterado",
      bool(_mudados) and not _tocados,
      "Espanha e Franca sao so de leitura nesta missao. Ficheiros de outro "
      "pais alterados: %s" % (_tocados or 'nenhum'))


print()
if FALHAS:
    print(f"COLETA_CANONICA=FALHA · {len(FALHAS)} reprovada(s): {', '.join(FALHAS)}")
    raise SystemExit(1)
print("COLETA_CANONICA=PASS · o caminho do pedido ate a inteligencia esta fechado")
