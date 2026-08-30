#!/usr/bin/env python3
"""
PROVENIÊNCIA — o RUN_ID deixa de ser um rótulo e passa a resolver.

O defeito que este arquivo fecha: até 2026-08-29 o `RUN_ID` agrupava registros entre si e
não resolvia para nada fora do repositório. Dado um vídeo, não havia como responder
"que execução produziu isto, com que ator, que entrada e que custo".

A cadeia que passa a existir:

    CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW

Três decisões carregadas aqui:

1. **CAMPO DESCONHECIDO É `NOT_PRESERVED`, NUNCA AUSENTE.**
   Execução antiga que não capturou `ACTOR_VERSION` declara `NOT_PRESERVED`. Isso é
   diferente de `NAO_SEI` (a fonte não informa) e muito diferente da chave sumir.

2. **NUNCA GRAVAR TOKEN.** `INPUT` guarda a consulta e os parâmetros; credencial jamais.
   Há teste que varre o manifesto atrás de padrão de token.

3. **TEMPO É MEDIDO, NÃO INFERIDO.** `STARTED_AT`/`FINISHED_AT` vêm da execução. Sem eles,
   nenhuma afirmação de ordem entre camadas é permitida — ver `pode_afirmar_ordem()`.

4. **TODA EXECUÇÃO TEM DONO.** Ver abaixo — foi a quarta decisão, e ela veio de um risco
   que já se materializou.

O DONO DO DADO — por que este campo nasceu
--------------------------------------------
Duas missões passaram a rodar em paralelo nos mesmos runners: EARLY SIGNAL e CREATOR MAP.
Elas podem e devem compartilhar máquina. O que não podem compartilhar é **dataset**.

O risco não é teórico. Medido em 2026-08-30: o `RUN-MANIFEST.json` da branch do Creator
Map tinha **23 execuções** — as 12 do Early Signal, as 10 históricas espanholas e 1 do
Creator Map, todas na mesma lista plana, sem nenhum campo dizendo de quem era cada uma.
Duas missões escrevendo o mesmo arquivo global já tinham produzido, horas antes, um
`CONFLICT` de rebase que prendeu 29 candidatos pagos fora do repositório.

    RUNNER COMPARTILHADO = OK. DATASET MISTURADO = NÃO.

`DATASET_OWNER` responde "de quem é esta execução" antes de qualquer reconciliação. Sem
ele, a pergunta "quantas execuções o Early Signal fez?" não tem resposta derivável — só
uma contagem que mistura donos e parece certa.

POR QUE O DONO É DERIVADO DA MISSÃO, E POR QUE ELE NUNCA DERRUBA UMA COLETA
-----------------------------------------------------------------------------
`novo_run()` deriva o dono de `MISSION` por um mapa **declarado** neste arquivo. Missão
desconhecida NÃO levanta exceção: sai como `UNDECLARED_OWNER` e o portão fica vermelho.

A escolha é deliberada e vem da lei mais cara desta casa: **DINHEIRO GASTO ≠ DADO
PRESERVADO**. Fazer uma execução paga estourar no meio por causa de uma regra de metadado
perderia o dado que acabou de ser comprado. Um portão vermelho custa uma linha de
correção; uma execução perdida custa a coleta inteira.
"""
import json
import os
import re
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')

NAO_SEI = 'NÃO SEI'
NOT_PRESERVED = 'NOT_PRESERVED'

FRAGMENTOS = os.path.join(ROOT, 'data', 'runs')

# ── DONOS DE DATASET ─────────────────────────────────────────────────────────────
# Mapa DECLARADO: missão -> dono. Acrescentar missão nova aqui é o ato explícito que o
# contrato exige. Enquanto ela não estiver aqui, o dono sai UNDECLARED_OWNER e o portão
# recusa — nunca um dono errado por adivinhação.
UNDECLARED_OWNER = 'UNDECLARED_OWNER'
DONOS = {
    'EARLY_SIGNAL_EAME': ('13-PILOTO-SENSORES-TECNICOS',),
    'CREATOR_MAP_EAME': ('14-MAPA-DE-CREATORS-EAME',),
    # As execuções da rodada de voz espanhola são anteriores à separação de donos. Elas
    # ganham um dono PRÓPRIO em vez de serem empurradas para dentro do Early Signal:
    # atribuí-las a ele inflaria a contagem daquela missão com trabalho que não é dela.
    'VOICE_ES': ('10A-ES', '10B-ES'),
}


def dono_da_missao(mission):
    """MISSION -> DATASET_OWNER. Desconhecida vira UNDECLARED_OWNER, nunca um palpite."""
    for dono, missoes in DONOS.items():
        if mission in missoes:
            return dono
    return UNDECLARED_OWNER


# Campos obrigatórios de todo manifesto de execução.
CAMPOS_RUN = [
    # De quem é esta execução. Primeiro campo de propósito: quem lê o manifesto precisa
    # saber o dono antes de contar qualquer coisa.
    'DATASET_OWNER',
    'RUN_ID', 'PLATFORM', 'ACTOR', 'ACTOR_VERSION', 'STARTED_AT', 'FINISHED_AT',
    'INPUT', 'COUNTRY', 'MISSION', 'QUERY', 'DATASET_ID',
    'ITEM_COUNT_RAW', 'ITEM_COUNT_NORMALIZED', 'COST_USD', 'SOURCE_VERSION',
    'STATUS', 'ERROR', 'CAPTURE_METHOD', 'EVIDENCE_PATH', 'RAW_EVIDENCE_PATH',
    'RAW_EVIDENCE_STATE',
    # Hora em que o coletor GRAVOU a saída. É medida de verdade, mas NÃO é a hora da
    # execução na plataforma — por isso vive em campo próprio e nunca é usada como
    # STARTED_AT/FINISHED_AT. Passar hora de escrita por hora de execução seria
    # exatamente o erro que a auditoria derrubou.
    'OUTPUT_WRITTEN_AT',
]

STATUS_RUN = ['SUCCESS', 'PARTIAL', 'FAILED', 'NOT_PRESERVED']
# Estado da evidência bruta. `NOT_PRESERVED` é uma confissão, não um sinônimo de ausência
# de dado: quer dizer que a resposta crua existiu e não foi guardada.
ESTADOS_RAW = ['PRESERVED', 'NOT_PRESERVED', 'NOT_APPLICABLE']

TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9._\-]{20,}')


def run_vazio():
    """Todo campo presente, todo valor em NOT_PRESERVED."""
    return {c: NOT_PRESERVED for c in CAMPOS_RUN}


def novo_run(run_id, **campos):
    """Monta um manifesto completo. Campo não informado fica NOT_PRESERVED, nunca some."""
    r = run_vazio()
    r['RUN_ID'] = run_id
    for k, v in campos.items():
        if k not in CAMPOS_RUN:
            raise KeyError('campo fora do contrato de RUN: %s' % k)
        r[k] = v
    # O dono é derivado da MISSÃO quando o chamador não o declara. Isso mantém as duas
    # missões existentes funcionando sem tocar no código delas — e uma missão nova, ainda
    # não registrada em DONOS, sai UNDECLARED_OWNER em vez de estourar a coleta paga.
    if r['DATASET_OWNER'] in (NOT_PRESERVED, None, ''):
        r['DATASET_OWNER'] = dono_da_missao(r.get('MISSION'))
    checar_token(r)
    return r


def checar_token(run):
    """Um manifesto nunca pode carregar credencial."""
    achado = TOKEN.search(json.dumps(run, ensure_ascii=False))
    if achado:
        raise ValueError('credencial no manifesto de execução — nunca gravar token')
    return True


def carregar(owner=None):
    """Runs do manifesto global. `owner` filtra por dono — e é isso que separa missões."""
    if not os.path.exists(MANIFESTO):
        return {}
    with open(MANIFESTO, encoding='utf-8') as f:
        d = json.load(f)
    runs = {r['RUN_ID']: r for r in d.get('RUNS', [])}
    if owner is None:
        return runs
    return {k: v for k, v in runs.items() if v.get('DATASET_OWNER') == owner}


def resolver(run_id):
    """RUN_ID -> manifesto. É isto que faltava: o rótulo agora resolve."""
    return carregar().get(run_id)


# ══════════════════════════════════════════ FRAGMENTOS: um arquivo por execução
# O PONTO PRIMÁRIO DE ESCRITA DEIXA DE SER O ARQUIVO GLOBAL.
#
# Dois runners editando `RUN-MANIFEST.json` ao mesmo tempo já produziu, medido, um
# `CONFLICT (content)` que parou um rebase no meio e prendeu 29 candidatos PAGOS fora do
# repositório. A causa não é o git: é dois processos reescrevendo o MESMO arquivo inteiro.
#
# Agora cada execução escreve o SEU arquivo, sob a pasta do SEU dono:
#
#     data/runs/EARLY_SIGNAL_EAME/<RUN_ID>.json
#     data/runs/CREATOR_MAP_EAME/<RUN_ID>.json
#
# Dois donos nunca tocam o mesmo caminho, então não existe escrita concorrente para
# resolver. O índice global passa a ser DERIVADO desses fragmentos — nunca o lugar onde
# duas missões escrevem juntas.
#
#     ARQUIVO POR EXECUÇÃO É O QUE TORNA A CONCORRÊNCIA IMPOSSÍVEL, EM VEZ DE GERENCIADA.

def caminho_fragmento(run):
    dono = run.get('DATASET_OWNER') or UNDECLARED_OWNER
    seguro = re.sub(r'[^A-Za-z0-9._-]', '_', str(run['RUN_ID']))[:120]
    return os.path.join(FRAGMENTOS, dono, '%s.json' % seguro)


def gravar_fragmento(run):
    """Escreve UM run, de forma atômica. Não lê nem reescreve nada de ninguém.

    A escrita é `tempfile` + `os.replace` porque `os.replace` é atômico: ou o arquivo
    antigo está lá inteiro, ou o novo está lá inteiro. Um processo morto no meio nunca
    deixa meio JSON — que é o estado que fez a leitura estourar com
    `Expecting property name enclosed in double quotes`.
    """
    faltando = set(CAMPOS_RUN) - set(run)
    if faltando:
        raise KeyError('fragmento incompleto, faltam: %s' % sorted(faltando))
    checar_token(run)
    destino = caminho_fragmento(run)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(destino), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(run, f, ensure_ascii=False, indent=1)
        os.replace(tmp, destino)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return os.path.relpath(destino, ROOT).replace('\\', '/')


def carregar_fragmentos(owner=None):
    """Todos os fragmentos em disco, opcionalmente de um dono só."""
    fora = {}
    if not os.path.isdir(FRAGMENTOS):
        return fora
    for dono in sorted(os.listdir(FRAGMENTOS)):
        if owner is not None and dono != owner:
            continue
        pasta = os.path.join(FRAGMENTOS, dono)
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not nome.endswith('.json'):
                continue
            try:
                with open(os.path.join(pasta, nome), encoding='utf-8') as f:
                    r = json.load(f)
            except (OSError, ValueError):
                continue                       # fragmento ilegível não contamina os outros
            # O dono do FRAGMENTO é a pasta, não o campo: se os dois discordarem, quem
            # manda é onde o arquivo está. Assim um campo editado à mão não move uma
            # execução de dataset sem mover o arquivo.
            r['DATASET_OWNER'] = dono
            fora[r['RUN_ID']] = r
    return fora


def donos_presentes():
    """Que donos existem em disco, e quantas execuções cada um tem."""
    contas = {}
    for r in carregar_fragmentos().values():
        contas[r['DATASET_OWNER']] = contas.get(r['DATASET_OWNER'], 0) + 1
    return dict(sorted(contas.items()))


def isolamento(owner_a, owner_b):
    """PROVA EXECUTÁVEL de que dois donos não se contaminam.

    Responde a pergunta que o contrato exige: uma execução do CREATOR MAP pode aparecer
    como execução do EARLY SIGNAL, ou virar órfã dele? A resposta tem de vir de leitura
    real dos dois conjuntos, nunca de afirmação.
    """
    a, b = carregar_fragmentos(owner_a), carregar_fragmentos(owner_b)
    cruzados_a = [k for k, v in a.items() if v['DATASET_OWNER'] != owner_a]
    cruzados_b = [k for k, v in b.items() if v['DATASET_OWNER'] != owner_b]
    interseccao = sorted(set(a) & set(b))
    return {
        'OWNER_A': owner_a, 'RUNS_A': len(a),
        'OWNER_B': owner_b, 'RUNS_B': len(b),
        'SHARED_RUN_IDS': interseccao,
        'A_CONTAMINATED_BY_OTHER_OWNER': cruzados_a,
        'B_CONTAMINATED_BY_OTHER_OWNER': cruzados_b,
        'ISOLATED': not interseccao and not cruzados_a and not cruzados_b,
    }


def reconciliar(captured_at):
    """Índice global DERIVADO dos fragmentos. Nunca o contrário.

    O global continua existindo porque o portão e o `resolver()` leem dele. O que mudou é
    a direção: ele é uma VISTA dos fragmentos, reconstruível a qualquer momento, e não o
    lugar onde duas missões escrevem juntas.
    """
    runs = carregar_fragmentos()
    return gravar([runs[k] for k in sorted(runs)], captured_at=captured_at)


def gravar(runs, *, captured_at):
    """Persiste o manifesto. `runs` é lista de dicionários já no contrato."""
    for r in runs:
        faltando = set(CAMPOS_RUN) - set(r)
        if faltando:
            raise KeyError('manifesto incompleto, faltam: %s' % sorted(faltando))
        checar_token(r)
        if r['STATUS'] not in STATUS_RUN:
            raise ValueError('STATUS fora do contrato: %s' % r['STATUS'])
        if r['RAW_EVIDENCE_STATE'] not in ESTADOS_RAW:
            raise ValueError('RAW_EVIDENCE_STATE fora do contrato: %s' % r['RAW_EVIDENCE_STATE'])
    corpo = {
        'SOURCE_ID': 'RUN-MANIFEST',
        'source': 'manifesto de execuções de coleta do SINTONIA EAME',
        'SOURCE_LOCATION': 'interno — metadado de coleta',
        'FACT_LOCATION': 'n/a — descreve execução, não fato do mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'captured_at': captured_at,
        'PARA_QUE_SERVE': (
            'dado um registro qualquer, o RUN_ID leva a esta tabela e a tabela diz que ator '
            'rodou, com que entrada, quando, quanto custou e onde está a evidência bruta. '
            'Sem isto o RUN_ID só agrupa registros entre si.'),
        'CAMPO_DESCONHECIDO': (
            'NOT_PRESERVED significa que o campo existiu na execução e não foi capturado. '
            'É confissão, não ausência de dado — e é diferente de NÃO SEI, que é a fonte '
            'não informar.'),
        'NUNCA_GRAVAR_TOKEN': 'INPUT guarda consulta e parâmetros. Credencial, jamais.',
        'DONO_DO_DADO': (
            'toda execução declara DATASET_OWNER. Runner compartilhado entre missões é '
            'permitido; dataset misturado não é. Contar execuções sem filtrar por dono '
            'mistura missões e produz um número que parece certo.'),
        'ESCRITA_PRIMARIA': (
            'este arquivo é DERIVADO de data/runs/<DONO>/<RUN_ID>.json. Ele não é o ponto '
            'de escrita concorrente — cada execução escreve o próprio fragmento, e dois '
            'donos nunca tocam o mesmo caminho.'),
        'RUNS_BY_OWNER': _por_dono(runs),
        'RUNS': runs,
    }
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


def _por_dono(runs):
    c = {}
    for r in runs:
        d = r.get('DATASET_OWNER') or UNDECLARED_OWNER
        c[d] = c.get(d, 0) + 1
    return dict(sorted(c.items()))


# ---------------------------------------------------------------- ordem entre camadas
def pode_afirmar_ordem(run_a, run_b):
    """`X BEFORE Y` só é dizível quando as duas execuções têm hora medida.

    A auditoria de 2026-08-29 derrubou a afirmação "o YouTube veio antes do LinkedIn":
    as duas rotas saíram do mesmo orçamento sem carimbo que as separasse, e o horário de
    commit do git NÃO mede hora de coleta — mede hora de escrita.
    """
    for r in (run_a, run_b):
        if not r:
            return False, 'execução sem manifesto'
        for c in ('STARTED_AT', 'FINISHED_AT'):
            if r.get(c) in (NOT_PRESERVED, NAO_SEI, None, ''):
                return False, '%s sem %s medido' % (r.get('RUN_ID'), c)
    return True, ''


def ordem(run_a, run_b):
    """Devolve BEFORE / AFTER / OVERLAPS, ou NAO_DIZIVEL com o motivo."""
    ok, motivo = pode_afirmar_ordem(run_a, run_b)
    if not ok:
        return 'NAO_DIZIVEL', motivo
    if run_a['FINISHED_AT'] <= run_b['STARTED_AT']:
        return 'BEFORE', ''
    if run_b['FINISHED_AT'] <= run_a['STARTED_AT']:
        return 'AFTER', ''
    return 'OVERLAPS', ''


if __name__ == '__main__':
    import sys
    runs = carregar()
    print('execuções no manifesto:', len(runs))
    for rid, r in sorted(runs.items()):
        print('  %-34s %-9s %-8s raw=%s' % (rid, r['PLATFORM'], r['STATUS'],
                                            r['RAW_EVIDENCE_STATE']))
    if '--campos' in sys.argv:
        for c in CAMPOS_RUN:
            print(' ', c)
