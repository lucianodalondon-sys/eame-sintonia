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
for _p in ('pedido', 'coleta', 'leis', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

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
    """O YAML sem a prosa. Um `#` dentro de aspas não é comentário."""
    fora = []
    for linha in texto.splitlines():
        corte, aspas = None, None
        for i, c in enumerate(linha):
            if aspas:
                if c == aspas:
                    aspas = None
            elif c in '"\'':
                aspas = c
            elif c == '#':
                corte = i
                break
        fora.append(linha[:corte] if corte is not None else linha)
    return '\n'.join(fora)


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


def medir(desvios=None):
    ready = superficie_ready()
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
            for fase in fases:
                vistos.add(fase)
                capacidades, canonico = capacidades_do_ramo(fase, alvos, ready, corpo, opcoes)
                v1 = bool(capacidades)
                entradas.append({
                    'WORKFLOW': nome, 'FASE': fase, 'ALVOS': alvos,
                    'CAPACIDADES': sorted(capacidades),
                    'V1': v1, 'CANONICO': canonico,
                    'ESTADO': ('ACTIVE_V1_CANONICAL' if v1 and canonico else
                               'ACTIVE_V1_BYPASS' if v1 else 'NOT_IN_V1'),
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
            v1 = bool(capacidades)
            entradas.append({
                'WORKFLOW': nome, 'FASE': '(passo sem ramo)', 'ALVOS': soltos,
                'CAPACIDADES': sorted(capacidades),
                'V1': v1, 'CANONICO': canonico,
                'ESTADO': ('ACTIVE_V1_CANONICAL' if v1 and canonico else
                           'ACTIVE_V1_BYPASS' if v1 else 'NOT_IN_V1'),
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
    for k in ('ACTIVE_V1_CANONICAL', 'ACTIVE_V1_BYPASS', 'NOT_IN_V1'):
        print('%-26s %d' % (k, contagem.get(k, 0)))
    activos = [e for e in entradas if e['V1']]
    print('%-26s %d' % ('ACTIVE_V1_ENTRYPOINTS', len(activos)))
    bypasses = [e for e in entradas if e['ESTADO'] == 'ACTIVE_V1_BYPASS']
    print('%-26s %d' % ('ACTIVE_V1_BYPASSES', len(bypasses)))
    for b in bypasses:
        print('   · %s/%s corre %s · alcança %s'
              % (b['WORKFLOW'], b['FASE'], ', '.join(b['ALVOS']),
                 ', '.join(b['CAPACIDADES'])))
    # ── §13 · O FALLBACK ESCONDIDO ────────────────────────────────────────
    # Um entrypoint V1 que alcança uma capacidade SEM passar pelo orquestrador
    # chega ao portão, ao roteador e à guarda de gasto por fora. É isso, e só
    # isso, que conta como fallback escondido — e não «tem apify no nome».
    escondidos = [e for e in entradas if e['V1'] and not e['CANONICO']]
    print('%-26s %d' % ('ACTIVE_V1_HIDDEN_FALLBACKS', len(escondidos)))
    for h in escondidos:
        print('   · %s/%s alcança %s por fora dos donos'
              % (h['WORKFLOW'], h['FASE'], ', '.join(h['CAPACIDADES'])))
    # ── OS DESVIOS QUE ADQUIREM E SE ANUNCIAM ─────────────────────────────
    # Eles saltam o `COLLECT` e dizem-no na saída. Não entram na conta de
    # fallback ESCONDIDO por isso mesmo: estão declarados, no dono, em código.
    total = sum(len(v) for v in desvios.values())
    print('%-26s %d' % ('DESVIOS_DECLARADOS_ALCANCAVEIS', total))
    for wf, ds in sorted(desvios.items()):
        for c, porque in sorted(ds.items()):
            print('   · %s pode disparar `%s` — %s' % (wf, c, porque[:52]))
    if os.environ.get('RC01_JSON'):
        print(json.dumps(entradas, ensure_ascii=False, indent=1))
    return 0 if not bypasses and not escondidos else 1


if __name__ == '__main__':
    sys.exit(main())
