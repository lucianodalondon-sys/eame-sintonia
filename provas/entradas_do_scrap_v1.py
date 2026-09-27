#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-RC-01 §11 §13 — QUEM PODE DISPARAR A RELEASE V1, E POR ONDE ELE PASSA.

    python3 provas/entradas_do_scrap_v1.py

    LEGACY EXISTS != ACTIVE V1 ENTRYPOINT.

A pergunta não é «quantos scripts existem». É esta:

    ESTE CAMINHO É ALCANÇÁVEL POR UM ENTRYPOINT V1
    SEM PASSAR PELOS DONOS?

COMO SE DECIDE O QUE É V1, SEM ESCREVER UMA LISTA À MÃO
--------------------------------------------------------
⚠️ A PRIMEIRA VERSÃO DESTA SONDA DERIVOU V1 DO **NOME DA FASE**: uma fase
estava em `serve_fases` de alguma receita, logo era V1. Ela acusou um bypass
que não existe — `sintonia-scrap.yml` tem uma fase `contratos` que lê o INPUT
SCHEMA de um ator, e `comunicacao-publica` tem outra fase `contratos` que é
outra coisa, do mesmo nome e de outro dono.

    DUAS PORTAS COM O MESMO NOME NÃO SÃO A MESMA PORTA.

O que decide não é como o ramo se chama: é **que capacidade ele consegue pôr a
correr**. Isso lê-se no código do alvo, e a superfície V1 vem de
`provas/superficie_do_scrap_v1.py`, que a mede no runtime.

    entrypoint que alcança capacidade READY da V1   →  ACTIVE_V1
    entrypoint que não alcança nenhuma              →  NOT_IN_V1

E o caminho mede-se pelo COMANDO que o ramo corre, não pelo nome do ramo:

    corre `orquestrador/orquestrador.py`  →  CANONICAL
    corre outra coisa                     →  BYPASS

§13 — OS FALLBACKS ESCONDIDOS
------------------------------
A pergunta não é «tem `apify` no nome». É se um entrypoint V1 consegue chegar à
porta paga ou a um adaptador SEM passar por `scrap_executor.COLLECT`.

    NÃO SE PROÍBEM FERRAMENTAS PELO NOME.

⚠️ A PROSA NÃO É O RAMO
------------------------
Os comentários destes YAML explicam por que o bypass foi fechado, e citam o
ficheiro que já não se corre. Uma sonda que lesse a prosa encontraria a frase
que explica a regra e chamar-lhe-ia violação da regra.

    UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
    E CHAMA-LHE VIOLAÇÃO DA REGRA.

Por isso tudo o que se mede aqui corre sobre o YAML SEM COMENTÁRIOS.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('pedido', 'coleta', 'leis', 'system-map/scripts', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import censo_da_coleta as _censo           # noqa: E402
import generate_system_map as _dono_da_prosa  # noqa: E402
import receitas as rec                     # noqa: E402
import scrap_capacidades as cap            # noqa: E402
import superficie_do_scrap_v1 as sup       # noqa: E402

#: A porta paga — a única primitiva que faz nascer execução cobrada.
PORTA_PAGA = 'coletor'
#: O executor canônico do SCRAP. Quem o chama passou pelo portão, pelo
#: roteador, pela política e pela guarda de gasto.
EXECUTOR = 'COLLECT'

FLUXOS = os.path.join(RAIZ, '.github', 'workflows')
ORQUESTRADOR = 'orquestrador/orquestrador.py'

#: Um ficheiro do repositório invocado numa linha de comando. O interpretador
#: escreve-se de quatro maneiras nesta casa (`py`, `python`, `python3`, `$PY`),
#: então não se procura o interpretador: procura-se o ALVO.
ALVO = re.compile(
    r'\b((?:coleta|orquestrador|pedido|regras|ferramentas|medidas|guarda'
    r'|provas|system-map/scripts)/[A-Za-z0-9_./-]+\.py)\b')

#: O `case` do shell: `fase-a|fase-b)` abre um ramo, `;;` fecha-o.
RAMO = re.compile(r'^\s*([a-z0-9][a-z0-9|_-]*)\)\s*$', re.M)


def sem_comentarios(texto):
    """O YAML sem a prosa — e o dono desta operação NÃO é este ficheiro.

    ⚠️ HAVIA AQUI UMA SEGUNDA IMPLEMENTAÇÃO. `system-map/scripts/censo_da_coleta.py`
    já corta prosa de YAML, Python e shell há missões, e a razão dele está
    escrita lá: a C10.4C mediu um censo a declarar que um módulo APOSENTADO
    chamava três módulos vivos, tudo a partir do docstring que explicava a
    aposentadoria.

        DUAS IMPLEMENTAÇÕES DO MESMO CONTRATO NÃO SÃO DUAS VERSÕES DA VERDADE:
        SÃO DUAS VERDADES.

    Então esta função passa a ser uma chamada ao dono, e continua a existir só
    para que quem lê esta prova saiba onde ela mora.

    ⚠️ O DONO MUDOU DE SÍTIO. `867f2f1d` tirou `_linhas_de_comando` do
    `censo_da_coleta.py` e esta chamada ficou a apontar para o vazio (o
    setUpClass do RC01 rebentava com AttributeError). O corte de prosa que a
    cadeia do mapa usa hoje é `generate_system_map.sem_comentarios`. Medido na
    M5G: `medir()` devolve o MESMO resultado com a função antiga e com esta.
    """
    return _dono_da_prosa.sem_comentarios(texto)


def superficie_ready():
    """→ {capacidade} — as que a §4 classificou READY no runtime."""
    linhas = sup.medir()
    return {l['CAPABILITY'] for l in linhas if l['V1'] == sup.READY}


#: ── POR QUE NÃO HÁ AQUI UMA LISTA DE «ESTES FICAM DE FORA» ────────────────
#: Houve uma, escrita à mão, com um motivo por workflow. Depois mediu-se o que
#: ela mudava: NADA — os mesmos 4 canônicos e os mesmos 19 fora, com ela e sem
#: ela. E um dos motivos que ela dava estava ERRADO: dizia que
#: `scrap-evidencia.yml` corre `social_scrap.py` para colher, quando o que ele
#: corre é `evidencia-publicar` e `evidencia-recuperar`, que leem o acervo e
#: não adquirem nada.
#:
#:     UMA LISTA À MÃO QUE NÃO MUDA NENHUM NÚMERO NÃO ESTÁ A DECIDIR:
#:     ESTÁ A LEMBRAR-SE. E LEMBRA-SE MAL.
#:
#: Então o que decide é só a travessia declarada, abaixo. Um workflow fica
#: `NOT_IN_V1` porque não põe nenhuma capacidade READY a correr — e isso lê-se,
#: não se afirma.

#: O subcomando que faz `coleta/social_scrap.py` colher. Os outros do mesmo
#: ficheiro leem o que já está em casa, medem um portão ou correm um censo — e
#: contá-los como coleta poria a colher um ramo que não colhe.
#:
#:     UM FICHEIRO COM DEZ SUBCOMANDOS NÃO É DEZ VEZES A MESMA PORTA.
COLHE = 'coletar'

# ── AS SEIS CLASSES DA §6, E POR QUE SAO SEIS E NAO TRES ───────────────────
# A versao anterior desta sonda tinha tres: canonico, bypass, e «legado». O
# balde do legado juntava coisas que nao sao a mesma: uma ferramenta que MEDE
# uma rota, um passo que reprocessa o que ja esta em casa, e uma capacidade que
# a politica fecha. Chamar as tres de legado faz o numero fechar e a leitura
# mentir.
#
#     NAO SE CHAMA REPROCESSAMENTO LOCAL DE BYPASS DE AQUISICAO.
#     NAO SE CHAMA FERRAMENTA DE MEDICAO DE ROTA DE PRODUCAO.
CANONICAL_V1 = 'CANONICAL_V1'
LEGACY_NOT_IN_V1 = 'LEGACY_NOT_IN_V1'
MEASUREMENT_ONLY = 'MEASUREMENT_ONLY'
LOCAL_REPROCESSING = 'LOCAL_REPROCESSING'
FAIL_CLOSED = 'FAIL_CLOSED'
DESCONHECIDO = 'UNKNOWN'
BYPASS = 'ACTIVE_V1_BYPASS'

#: Quem diz se um ficheiro SAI PARA FORA tem dono, e nao e esta prova:
#: `system-map/scripts/censo_da_coleta.py::SAI_PARA_FORA`. Um passo que nao sai
#: para fora nao adquire — le o que ja esta em casa.
#:
#:     LER O ACERVO NAO E IR AO MUNDO.


def _sai_para_fora(alvos):
    for rel in alvos:
        caminho = os.path.join(RAIZ, rel)
        if not os.path.isfile(caminho):
            continue
        with open(caminho, encoding='utf-8', errors='replace') as f:
            if _censo.SAI_PARA_FORA.search(_dono_da_prosa.sem_comentarios(f.read())):
                return True
    return False


def classificar(alvos, ready_alcancadas, todas_alcancadas, canonico,
                desvios_da_fase, fechadas):
    """A classe desta entrada, pela cadeia DECLARADA. → uma das seis.

    ⚠️ A ORDEM DAS PERGUNTAS E O QUE FAZ AS SEIS SEREM SEIS. Alcancar uma
    capacidade — de QUALQUER estado — quer dizer que este ramo ADQUIRE, e um
    ramo que adquire nunca e reprocessamento local, por mais que o ficheiro que
    ele corre nao abra socket nenhum sozinho.

        QUEM DELEGA A IDA AO MUNDO CONTINUA A IR AO MUNDO.

    Foi esse o defeito da primeira versao: `yt-legenda-paga` corre
    `social_scrap.py coletar`, que colhe pela rota PAGA do YouTube — e aparecia
    como LOCAL_REPROCESSING porque aquele ficheiro delega o transporte.
    """
    if todas_alcancadas:
        if ready_alcancadas:
            return CANONICAL_V1 if canonico else BYPASS
        # Adquire, mas o que ela alcanca nao esta na superficie V1.
        return CANONICAL_V1 if canonico else LEGACY_NOT_IN_V1
    if desvios_da_fase:
        # O proprio dono declara que estas ADQUIREM e saltam o `COLLECT`, e
        # elas dizem-no na saida. Sao medicao, e nao porta de producao.
        return MEASUREMENT_ONLY
    if fechadas:
        return FAIL_CLOSED
    if not alvos:
        return DESCONHECIDO
    if not _sai_para_fora(alvos):
        return LOCAL_REPROCESSING
    return LEGACY_NOT_IN_V1

#: O que vem logo a seguir ao caminho do script: ou uma expressão do GitHub —
#: e aí o subcomando é «o que o menu oferecer» — ou uma palavra. A barra de
#: continuação de linha e as aspas ficam pelo caminho, que é onde a primeira
#: versão desta sonda se perdeu: ela partia por espaços, e `"${{ inputs.fase
#: }}"` são TRÊS pedaços, nenhum deles igual a `${{ inputs.fase`.
#:
#:     PARTIR POR ESPAÇOS PARTE TAMBÉM O QUE NÃO ERA PARA PARTIR.
PRIMEIRO_ARG = re.compile(
    r'^[\s\\]*(?:"\s*)?(?:\$\{\{[^}]*inputs\.([a-z_]+)[^}]*\}\}|([A-Za-z0-9_-]+))')


def _subcomandos(corpo, rel, opcoes):
    """→ {subcomandos} que este corpo consegue passar ao script.

    ⚠️ TODAS as ocorrências, e não a primeira: o caminho do ficheiro aparece
    também sob `paths:` do gatilho, e ler só a primeira lia um filtro de
    trigger como se fosse uma linha de comando.

        UM CAMINHO NUM FILTRO DE GATILHO NÃO É UM COMANDO.

    E um subcomando que vem do menu não é UM subcomando: são todos os que o
    menu oferece, porque quem dispara escolhe qual.
    """
    fora = set()
    for pedaco in corpo.split(rel)[1:]:
        m = PRIMEIRO_ARG.match(pedaco)
        if not m:
            continue
        if m.group(1):
            fora |= set(opcoes.get(m.group(1)) or ())
        elif m.group(2):
            fora.add(m.group(2))
    return fora


def opcoes_do_fluxo(caminho):
    """→ {input: [opções]} do `workflow_dispatch`, quando ele as declara."""
    try:
        import yaml
    except ImportError:                                           # noqa: BLE001
        return {}
    try:
        with open(caminho, encoding='utf-8') as f:
            d = yaml.safe_load(f) or {}
    except Exception:                                             # noqa: BLE001
        return {}
    for chave in (True, 'on'):
        gatilhos = d.get(chave)
        if isinstance(gatilhos, dict):
            ins = (gatilhos.get('workflow_dispatch') or {}).get('inputs') or {}
            return {k: (v or {}).get('options') or []
                    for k, v in ins.items()}
    return {}


def desvios_declarados(subcomandos):
    """→ {subcomando: porquê} — os desvios que o PRÓPRIO dono já declara.

    `coleta/social_scrap.py::FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY` é o dono
    desta lista, e ele imprime `DESVIO_DECLARADO` quando uma delas corre.
    Reescrevê-la aqui seria uma segunda verdade sobre a mesma coisa.

        UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
    """
    import social_scrap as _ss
    return {c: p for c, p in _ss.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY.items()
            if c in subcomandos}


def capacidades_do_script(rel, fase, corpo='', opcoes=None):
    """→ {capacidade} que ESTE script põe a correr para ESTA fase.

    Lê a tabela DECLARADA de cada executor, e não o texto do ficheiro: um nome
    de capacidade citado num comentário ou numa prova não é uma capacidade que
    alguém consiga pôr a correr.

        CITAR UMA CAPACIDADE NÃO É ALCANÇÁ-LA.

    Um script sem tabela de fases declarada devolve conjunto vazio — ele não
    dispacha capacidade nenhuma, e inventar uma para o número fechar seria o
    contrário de medir.
    """
    if rel.endswith('scrap_colheita.py'):
        import scrap_colheita as _sc
        linha = _sc.FASES.get(fase)
        return {linha[1]} if linha else set()
    if rel.endswith('social_scrap.py'):
        import social_scrap as _ss
        linha = _ss.FASES_CANONICAS.get(fase)
        if linha:
            return {linha[1]}
        # ⚠️ NEM TODO RAMO QUE CORRE ESTE FICHEIRO COLHE. `bruto` lê o que já
        # está em casa; `censo`, `portao` e `ledger` medem. Só `coletar` é que
        # chega ao `COLLECT` — e alcança então TODAS as fases da tabela dele,
        # porque a fase vai como argumento e quem dispara escolhe.
        if COLHE not in _subcomandos(corpo, rel, opcoes or {}):
            return set()
        return {l[1] for l in _ss.FASES_CANONICAS.values()}
    return set()


def capacidades_do_ramo(fase, alvos, ready, corpo='', opcoes=None):
    """→ ({capacidades READY}, canônico?). Segue a cadeia DECLARADA."""
    if ORQUESTRADOR in alvos:
        import pedido as _pd
        p = _pd.de_uma_frase('colete concorrentes')
        p.filtros.update({'fase': fase, 'fonte': 'IT-T9-001'})
        try:
            e = rec.resolver(p).executores[0]
        except Exception:                                         # noqa: BLE001
            return set(), True
        alvo = (e.get('roda') or [None])[0] or ''
        return capacidades_do_script(alvo, fase, corpo, opcoes) & ready, True
    fora = set()
    for rel in alvos:
        fora |= capacidades_do_script(rel, fase, corpo, opcoes)
    return fora & ready, False


def ramos(texto):
    """→ [(fases, corpo)] de cada ramo de `case` no YAML já sem comentários."""
    fora = []
    for m in RAMO.finditer(texto):
        corpo = texto[m.end():]
        fim = corpo.find(';;')
        fora.append((m.group(1).split('|'), corpo[:fim if fim >= 0 else 400]))
    return fora


def capacidades_fechadas(fase, alvos, fail_closed):
    """→ as capacidades FAIL_CLOSED que este ramo pediria, se pedisse."""
    fora = set()
    for rel in alvos:
        fora |= capacidades_do_script(rel, fase)
    return fora & fail_closed


def superficie_por_estado():
    """→ (READY, FAIL_CLOSED) medidos pela superfície, e não escritos aqui."""
    linhas = sup.medir()
    return ({l['CAPABILITY'] for l in linhas if l['V1'] == sup.READY},
            {l['CAPABILITY'] for l in linhas if l['V1'] == sup.FAIL_CLOSED})


def bypasses_de_politica(entradas):
    """Ramos manualmente disparaveis que alcancam um ator PROIBIDO pela matriz.

    ⚠️ A pergunta e do dono da politica, e nao desta prova: para cada ator que
    um ficheiro alcancavel configura, `social_matriz.actor_proibido()` responde.

        SPEND_AUTHORIZATION != ROUTE_POLICY.
    """
    import social_matriz as mz
    fora = []
    for e in entradas:
        for rel in e['ALVOS']:
            for plat, ator in atores_de(rel):
                proibido, _p = mz.actor_proibido(plat, ator)
                if proibido and not _tem_portao_de_politica(plat, ator):
                    fora.append((e['WORKFLOW'], e['FASE'], ator))
    return fora


def atores_de(rel):
    """→ [(plataforma, ator)] que este ficheiro CONFIGURA, pela tabela dele.

    Le a tabela declarada — `ATORES` — e nao o texto. Um ator citado num
    comentario nao e um ator configurado.
    """
    if not rel.endswith('sensor_coleta.py'):
        return []
    import importlib
    import sys as _s
    _s.path.insert(0, os.path.join(RAIZ, 'regras'))
    try:
        mod = importlib.import_module('sensor_coleta')
    except Exception:                                             # noqa: BLE001
        return []
    fora = []
    for rotulo, ator in (getattr(mod, 'ATORES', {}) or {}).items():
        plat = rotulo.split('_')[0]
        fora.append((plat, ator))
    return fora


_PORTAO = {}


def _tem_portao_de_politica(plat, ator):
    """A porta paga RECUSA mesmo este ator? Mede-se CORRENDO, nao lendo.

    ⚠️ A primeira versao procurava a string `actor_proibido` no ficheiro do
    coletor. Isso mede que alguem ESCREVEU a guarda, e nao que ela MORDE — e
    esta casa ja pagou essa diferenca em duas missoes.

        LER A ARVORE PROVA QUE A PECA EXISTE.
        SO CORRER PROVA QUE A ARESTA EXISTE.

    Entao chama-se a porta paga com este ator e ve-se o que sai. Zero rede:
    a recusa acontece antes de qualquer transporte, e se NAO acontecer o
    `subprocess` falso conta o POST que teria saido.
    """
    if (plat, ator) in _PORTAO:
        return _PORTAO[(plat, ator)]
    import subprocess
    import coletor as ct
    posts = []

    class _Conta(object):
        def __call__(self, cmd, **k):
            if '-X' in cmd and cmd[cmd.index('-X') + 1].upper() == 'POST':
                posts.append(cmd[-1])
            raise AssertionError('a prova nao deixa esta chamada seguir')

    real = subprocess.run
    subprocess.run = _Conta()
    try:
        ct.executar(ator, {}, token='TOKEN_DE_PROVA', run_id='entradas',
                    platform=plat, country='IT', mission='RC01', query='q',
                    source_version='p', evidence_path='/dev/null', wait=1,
                    salvar_raw=False)
    except ct.RotaNaoPermitida:
        _PORTAO[(plat, ator)] = True
    except Exception:                                             # noqa: BLE001
        # Qualquer outra recusa NAO conta como portao de politica: ela pode
        # desaparecer no dia em que alguem der dinheiro ou credencial.
        _PORTAO[(plat, ator)] = False
    else:
        _PORTAO[(plat, ator)] = False
    finally:
        subprocess.run = real
    return _PORTAO[(plat, ator)] and not posts


def medir(desvios=None):
    ready, fail_closed = superficie_por_estado()
    #: TODAS as capacidades declaradas, para responder «este ramo adquire?»
    #: sem confundir «adquire» com «adquire algo que esta na V1».
    TUDO = set(cap.DECLARADAS)
    desvios = {} if desvios is None else desvios
    entradas = []
    for nome in sorted(os.listdir(FLUXOS)):
        if not nome.endswith(('.yml', '.yaml')):
            continue
        caminho = os.path.join(FLUXOS, nome)
        with open(caminho, encoding='utf-8') as f:
            limpo = sem_comentarios(f.read())
        opcoes = opcoes_do_fluxo(caminho)
        vistos = set()
        # Os desvios que o próprio `social_scrap.py` declara, quando este
        # workflow consegue disparar algum deles.
        sub = _subcomandos(limpo, 'coleta/social_scrap.py', opcoes)
        desvios[nome] = desvios_declarados(sub)
        for fases, corpo in ramos(limpo):
            alvos = sorted(set(ALVO.findall(corpo)))
            if not alvos:
                continue
            sub_do_ramo = _subcomandos(corpo, 'coleta/social_scrap.py', opcoes)
            desvios_da_fase = desvios_declarados(sub_do_ramo)
            for fase in fases:
                vistos.add(fase)
                fechadas = capacidades_fechadas(fase, alvos, fail_closed)
                capacidades, canonico = capacidades_do_ramo(fase, alvos, ready, corpo, opcoes)
                todas, _c = capacidades_do_ramo(fase, alvos, TUDO, corpo, opcoes)
                entradas.append({
                    'WORKFLOW': nome, 'FASE': fase, 'ALVOS': alvos,
                    'CAPACIDADES': sorted(capacidades),
                    'ALCANCA': sorted(todas),
                    'V1': bool(capacidades), 'CANONICO': canonico,
                    'ESTADO': classificar(alvos, capacidades, todas, canonico,
                                          desvios_da_fase, fechadas),
                })
        # ── O QUE CORRE FORA DE QUALQUER `case` ─────────────────────────────
        # Um `run:` solto também é um entrypoint. Ignorá-lo porque não tem
        # ramo mediria só os workflows que usam `case`.
        soltos = sorted(set(ALVO.findall(limpo)))
        for fases, corpo in ramos(limpo):
            for a in ALVO.findall(corpo):
                if a in soltos:
                    soltos.remove(a)
        if soltos:
            capacidades, canonico = capacidades_do_ramo('', soltos, ready, limpo, opcoes)
            todas, _c = capacidades_do_ramo('', soltos, TUDO, limpo, opcoes)
            entradas.append({
                'WORKFLOW': nome, 'FASE': '(passo sem ramo)', 'ALVOS': soltos,
                'CAPACIDADES': sorted(capacidades),
                'ALCANCA': sorted(todas),
                'V1': bool(capacidades), 'CANONICO': canonico,
                'ESTADO': classificar(soltos, capacidades, todas, canonico,
                                      desvios[nome],
                                      capacidades_fechadas('', soltos, fail_closed)),
            })
    return entradas


def main():
    desvios = {}
    entradas = medir(desvios)
    print(__doc__.strip().splitlines()[0])
    print('=' * 100)
    print('%-26s %-18s %-20s %s' % ('WORKFLOW', 'FASE', 'ESTADO', 'CORRE'))
    print('-' * 100)
    for e in entradas:
        print('%-26s %-18s %-20s %s'
              % (e['WORKFLOW'][:26], e['FASE'][:18], e['ESTADO'],
                 ', '.join(a.split('/')[-1] for a in e['ALVOS'])[:34]))
    contagem = {}
    for e in entradas:
        contagem[e['ESTADO']] = contagem.get(e['ESTADO'], 0) + 1
    print('=' * 100)
    for k in (CANONICAL_V1, BYPASS, MEASUREMENT_ONLY, LOCAL_REPROCESSING,
              FAIL_CLOSED, LEGACY_NOT_IN_V1, DESCONHECIDO):
        print('%-32s %d' % (k, contagem.get(k, 0)))
    activos = [e for e in entradas if e['ESTADO'] == CANONICAL_V1]
    bypasses = [e for e in entradas if e['ESTADO'] == BYPASS]
    print('-' * 100)
    print('%-32s %d' % ('ACTIVE_V1_ENTRYPOINTS', len(activos)))
    print('%-32s %d' % ('ACTIVE_V1_CANONICAL', len(activos)))
    print('%-32s %d' % ('ACTIVE_V1_BYPASSES', len(bypasses)))
    for b in bypasses:
        print('   · %s/%s corre %s · alcanca %s'
              % (b['WORKFLOW'], b['FASE'], ', '.join(b['ALVOS']),
                 ', '.join(b['CAPACIDADES'])))
    escondidos = [e for e in entradas if e['V1'] and not e['CANONICO']]
    print('%-32s %d' % ('ACTIVE_V1_HIDDEN_FALLBACKS', len(escondidos)))
    # ── §6 · UM BOTAO MANUAL ACTIVO AINDA E EXECUTAVEL ────────────────────
    # Um ramo que um humano pode disparar hoje e que consegue chegar a um ator
    # que a politica proibe. Nao se pergunta pelo NOME do ficheiro: pergunta-se
    # ao dono da politica, ator a ator.
    #
    #     DIZER «E LEGADO» NUM DOCUMENTO NAO DESLIGA UM BOTAO.
    manuais = bypasses_de_politica(entradas)
    print('%-32s %d' % ('MANUALLY_TRIGGERABLE_POLICY_BYPASSES', len(manuais)))
    for m in manuais:
        print('   · %s pode disparar %s · ator %s' % m)
    print('%-32s %d' % ('DESVIOS_DECLARADOS_ALCANCAVEIS',
                        sum(len(v) for v in desvios.values())))
    for wf, ds in sorted(desvios.items()):
        for c, porque in sorted(ds.items()):
            print('   · %s pode disparar `%s` — %s' % (wf, c, porque[:52]))
    if os.environ.get('RC01_JSON'):
        print(json.dumps(entradas, ensure_ascii=False, indent=1))
    return 0 if not (bypasses or escondidos or manuais) else 1


if __name__ == '__main__':
    sys.exit(main())
