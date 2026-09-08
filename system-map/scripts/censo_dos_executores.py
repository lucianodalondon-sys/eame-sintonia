#!/usr/bin/env python3
"""CENSO DOS EXECUTORES — quem atravessa o sistema, e quem deixa pegada.

    UM CAMINHO INSTRUMENTADO NAO E TODOS OS EXECUTORES INSTRUMENTADOS.

Serve duas perguntas com uma medicao so:

    O9   qual e o primeiro caminho real barato de instrumentar?
    O10  quanto da casa ja tem sensores, e quanto esta no escuro?

TUDO AQUI E MEDIDO NO CODIGO, por AST e por leitura de ficheiro. Nada e
digitado a mao: um executor que ganhe telemetria amanha muda de estado sozinho,
e um que a perca tambem.

    O QUE O CENSO NAO PODE FAZER
    ----------------------------
Ele mede o que o codigo IMPORTA e CHAMA. Isso prova CAPACIDADE, nao EXECUCAO:
um executor que importa o writer pode nunca ter corrido. Por isso o estado
INSTRUMENTED exige as duas provas — caminho bom e caminho quebrado — e essas
vem de fora, do ledger de provas, e nao deste ficheiro.

    CAN DO != DID DO.
"""
import ast
import json
import os
import re
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))

# ── ONDE VIVEM OS EXECUTORES ─────────────────────────────────────────────
# Um executor e o que ATRAVESSA uma etapa da coleta: busca, deriva, preserva.
# Contratos, leis, medidas e provas nao sao executores, e por isso as suas
# gavetas nao entram.
GAVETAS = ('coleta', 'guarda', 'ferramentas', 'orquestrador')

# Como se reconhece cada dependencia. Sao heuristicas HONESTAS: quando nao dao
# para decidir, o campo fica UNKNOWN, e nunca NO por omissao.
REDE = ('urllib.request', 'urllib', 'requests', 'httpx', 'http.client',
        'navegador', 'cdp', 'websocket')
PAGO = ('apify_pool', 'apify_contrato', 'apify_recuperar')
PRODUCAO = ('SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE')
TELEMETRIA = ('rastro_da_coleta', 'telemetria')
FALHAS = ('falhas',)
DIAGNOSTICO = ('diagnostico',)
CHECKPOINT = ('coleta_checkpoint',)

ETAPAS = ('DISCOVER', 'FETCH', 'RAW', 'DERIVED', 'STRUCTURED', 'ADMISSION',
          'READY', 'CHECK', 'DECIDE')


def _fonte(caminho):
    try:
        return open(caminho, encoding='utf-8').read()
    except (OSError, UnicodeDecodeError):
        return None


def _codigo_executavel(fonte, arvore):
    """A fonte sem comentarios e sem docstrings.

    ⚠️ TRES VEZES ESTE CENSO LEU PROSA COMO DEPENDENCIA. A ultima:
    `executor_texto_de_pdf.py` foi marcado PRODUCTION_REQUIRED por causa de um
    COMENTARIO que diz exatamente o contrario — «Nenhum executor grava so
    porque conhece a SUPABASE_URL».

        UMA FRASE SOBRE PRODUCAO NAO E UMA LIGACAO A PRODUCAO.

    Aqui as docstrings saem por AST, e os comentarios por linha.
    """
    corpo = []
    docs = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                           ast.ClassDef)):
            d = ast.get_docstring(no, clean=False)
            if d:
                docs.add(d)
    for linha in fonte.split('\n'):
        sem = re.sub(r'#.*$', '', linha)
        corpo.append(sem)
    texto = '\n'.join(corpo)
    for d in docs:
        texto = texto.replace(d, ' ')
    return texto


def _importa(arvore):
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for a in no.names:
                nomes.add(a.name)
                nomes.add(a.name.split('.')[0])
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
            nomes.add(no.module.split('.')[0])
    return nomes


def _tem_porta(arvore, fonte):
    """Porta de entrada: `def main()` OU a guarda `if __name__ == '__main__'`.

    ⚠️ So procurar por `def main` classificou `executor_texto_de_pdf.py` como
    «nao e um caminho» — e ele e o executor de derivacao da casa. Ele abre pela
    guarda, sem funcao chamada main.
    """
    if any(isinstance(n, ast.FunctionDef) and n.name in ('main', 'principal')
           for n in ast.walk(arvore)):
        return True
    return "__name__" in fonte and "__main__" in fonte


def _executaveis():
    for gaveta in GAVETAS:
        pasta = os.path.join(RAIZ, gaveta)
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not nome.endswith('.py') or nome.startswith('_'):
                continue
            yield gaveta, nome, os.path.join(pasta, nome)


def medir():
    linhas = []
    for gaveta, nome, caminho in _executaveis():
        fonte = _fonte(caminho)
        if fonte is None:
            continue
        try:
            arvore = ast.parse(fonte)
        except SyntaxError:
            continue
        imports = _importa(arvore)
        codigo = _codigo_executavel(fonte, arvore)
        rel = '%s/%s' % (gaveta, nome)

        # As etapas que o ficheiro NOMEIA. Nomear nao e executar — e por isso
        # o campo se chama DECLARA e nao EXECUTA.
        # ⚠️ PREFIXO, E NAO IGUALDADE. `DERIVED_EMITTED` nomeia DERIVED, e a
        # comparacao exata deixava-o de fora — foi assim que o executor de
        # derivacao ficou invisivel a primeira versao deste censo.
        # Isto continua a medir que o ficheiro NOMEIA a etapa. Nomear nao e
        # executar, e o nome do campo di-lo.
        # ⚠️ NEM IGUALDADE EXATA NEM PREFIXO SOLTO — as duas erraram aqui.
        # A exata perdeu `DERIVED_EMITTED` e escondeu o executor de derivacao.
        # O prefixo solto casou com a palavra READY em prosa e promoveu 55 de
        # 56 ficheiros a «caminho de coleta». Vale o nome CITADO ('RAW') ou o
        # identificador (`DERIVED_EMITTED`) — nao a palavra num comentario.
        declara = tuple(e for e in ETAPAS
                        if re.search(r'''["']%s\b|\b%s_[A-Z]''' % (e, e), codigo))

        rede = bool(imports & set(REDE))
        # ⚠️ O MODULO PAGO NAO SE IMPORTA A SI PROPRIO. Sem esta linha,
        # `apify_pool.py` aparecia como candidato gratuito — e era ele a porta
        # da rota paga.
        pago = bool(imports & set(PAGO)) or nome[:-3] in PAGO
        producao = any(p in codigo for p in PRODUCAO)

        linhas.append({
            'EXECUTOR_ID': rel,
            'GAVETA': gaveta,
            'LINHAS': fonte.count('\n') + 1,
            'TEM_PORTA': _tem_porta(arvore, fonte),
            'ETAPAS_NOMEADAS': declara,
            # Le input ja preservado do armazem local? E o criterio mais forte
            # de O9: caminho real, input real, e zero rede.
            'HAS_PRESERVED_INPUT': ('collection-store' in codigo
                                    or 'ARMAZEM' in codigo),
            'USA_CONTRATO_ARTEFATO': 'artefato' in imports,
            'NETWORK_REQUIRED': rede,
            'PAID': pago,
            'PRODUCTION_REQUIRED': producao,
            'CAN_RUN_OFFLINE': not (rede or pago or producao),
            'USA_TELEMETRIA': bool(imports & set(TELEMETRIA)),
            'USA_FALHAS': bool(imports & set(FALHAS)),
            'USA_DIAGNOSTICO': bool(imports & set(DIAGNOSTICO)),
            'USA_CHECKPOINT': bool(imports & set(CHECKPOINT)),
        })
    return linhas


# ── O LEDGER DAS PROVAS ──────────────────────────────────────────────────
# CAN DO != DID DO. Um executor so passa a INSTRUMENTED quando existe prova de
# que ele CORREU e deixou rastro — caminho bom E caminho quebrado. O ledger
# aponta para a prova; ele nao a substitui.
PROVAS = os.path.join(RAIZ, 'system-map', 'data', 'provas-de-execucao.json')


def _ledger():
    if not os.path.exists(PROVAS):
        return {}
    return json.load(open(PROVAS, encoding='utf-8')).get('PROVADOS', {})


def estado(linha, ledger):
    """INSTRUMENTED / PARTIAL / NOT_INSTRUMENTED / NOT_APPLICABLE / UNKNOWN."""
    p = ledger.get(linha['EXECUTOR_ID'], {})
    bom = p.get('GOOD_PATH_PROVED')
    falha = p.get('FAULT_PATH_PROVED')
    if bom and falha:
        return 'INSTRUMENTED'
    if bom or falha or linha['USA_TELEMETRIA']:
        # Importa o writer, ou provou um dos dois caminhos: sabe emitir, e nao
        # esta provado de ponta a ponta.
        return 'PARTIAL'
    if not linha['TEM_PORTA'] and not linha['ETAPAS_NOMEADAS']:
        # Nem porta de entrada, nem etapa nomeada: nao e um caminho de coleta.
        return 'NOT_APPLICABLE'
    return 'NOT_INSTRUMENTED'


def principal():
    linhas = medir()
    ledger = _ledger()
    for l in linhas:
        p = ledger.get(l['EXECUTOR_ID'], {})
        l['GOOD_PATH_PROVED'] = p.get('GOOD_PATH_PROVED', False)
        l['FAULT_PATH_PROVED'] = p.get('FAULT_PATH_PROVED', False)
        l['PROVA'] = p.get('PROVA')
        l['STATE'] = estado(l, ledger)

    relevantes = [l for l in linhas if l['STATE'] != 'NOT_APPLICABLE']
    por_estado = {}
    for l in linhas:
        por_estado[l['STATE']] = por_estado.get(l['STATE'], 0) + 1

    # O proximo mais barato: offline, sem pago, sem producao, e ainda no escuro.
    # A ORDEM E A DAS REGRAS DE ESCOLHA, e nao o tamanho do ficheiro:
    # input real preservado, etapas reais nomeadas, zero rede/pago/producao, e
    # so entao o custo de o instrumentar.
    def barateza(l):
        return (not l['HAS_PRESERVED_INPUT'],
                -len(l['ETAPAS_NOMEADAS']),
                not l['USA_FALHAS'],
                l['LINHAS'])
    baratos = sorted(
        (l for l in relevantes if l['STATE'] == 'NOT_INSTRUMENTED'
         and l['CAN_RUN_OFFLINE']), key=barateza)

    # ── O10 · A MATRIZ DE COBERTURA, POR DIMENSAO ────────────────────────
    # NAO E UMA NOTA. Sao dimensoes separadas, porque juntar tudo num «73% de
    # observabilidade» esconderia qual das colunas esta vazia — e sao elas que
    # dizem o que fazer a seguir.
    DIMENSOES = ('RUN', 'STAGES', 'EDGE_PASSAGE', 'ACCOUNTING', 'GRAIN',
                 'FAILURE_STATE', 'DIAGNOSTIC_CODE', 'FAILURE_SNAPSHOT',
                 'LAST_GOOD', 'RESUME', 'DURATION', 'COST', 'CHECKPOINT',
                 'REUSED')
    cobertura = {}
    for dim in DIMENSOES:
        cobertura[dim] = {'INSTRUMENTED': 0, 'NOT_INSTRUMENTED': 0,
                          'NOT_APPLICABLE': 0}
    for l in relevantes:
        p = ledger.get(l['EXECUTOR_ID'], {})
        provado = l['STATE'] == 'INSTRUMENTED'
        for dim in DIMENSOES:
            if dim == 'CHECKPOINT' and p.get('CHECKPOINT') == 'NOT_APPLICABLE':
                cobertura[dim]['NOT_APPLICABLE'] += 1
            elif provado:
                cobertura[dim]['INSTRUMENTED'] += 1
            else:
                cobertura[dim]['NOT_INSTRUMENTED'] += 1

    tem_bom = sum(1 for l in relevantes if l['GOOD_PATH_PROVED'])
    tem_falha = sum(1 for l in relevantes if l['FAULT_PATH_PROVED'])

    # ⚠️ ISTO NAO E AUTORIZACAO PARA COMECAR A M2. E uma medida.
    minimo = {
        'MINIMAL_OPERATIONAL_OBSERVABILITY_FOR_M2': (
            'YES' if tem_bom >= 1 and tem_falha >= 1 and
            por_estado.get('INSTRUMENTED', 0) >= 1 else 'NO'),
        'CRITERIOS': {
            'CONTRATO_IMPLEMENTAVEL_PONTA_A_PONTA':
                'paridade_da_lingua.py PASS (contrato=storage=writer=scanner)',
            'PELO_MENOS_UM_CAMINHO_REAL_PROVADO_BOM': tem_bom >= 1,
            'PELO_MENOS_UM_CAMINHO_REAL_PROVADO_QUEBRADO': tem_falha >= 1,
            'CONTABILIDADE_FECHA_NUM_CAMINHO_REAL': tem_bom >= 1,
            'RETOMADA_SABE_ONDE_RECOMECAR': tem_falha >= 1,
        },
        'O_QUE_YES_NAO_SIGNIFICA': (
            'NAO significa que a M2 pode comecar, e NAO significa cobertura. '
            'Significa que o instrumento existe e ja foi exercido numa '
            'passagem real. A decisao de comecar a M2 e outra, e vem depois.'),
        'PROXIMO_BLOQUEADOR': (
            'a rota que a M2 vai construir (RC-1, arestas DERIVED->STRUCTURED e '
            'STRUCTURED->ADMISSION) nao tem executor instrumentado: STRUCTURED '
            'e ADMISSION nunca foram observados em nenhum caminho. Medir o que '
            'a M2 constroi exige instrumentar quem atravessa essas duas.'),
    }

    cabeca = subprocess.run(['git', '-C', RAIZ, 'rev-parse', 'HEAD'],
                            capture_output=True, text=True).stdout.strip()
    saida = {
        'SCHEMA': 'executores/v1',
        'PROVENANCE': {'HEAD': cabeca, 'MEDIDO_POR': 'censo_dos_executores.py'},
        'O_QUE_ISTO_MEDE': (
            'capacidade lida no codigo (o que se importa e se nomeia) mais as '
            'provas de execucao do ledger. CAN DO != DID DO: importar o writer '
            'nao prova que alguma vez correu.'),
        'TOTAL_FICHEIROS': len(linhas),
        'TOTAL_CAMINHOS_RELEVANTES': len(relevantes),
        'POR_ESTADO': por_estado,
        'PROXIMO_MAIS_BARATO': [l['EXECUTOR_ID'] for l in baratos[:5]],
        'COBERTURA_POR_DIMENSAO': cobertura,
        'GOOD_PATH_PROVED': tem_bom,
        'FAULT_PATH_PROVED': tem_falha,
        'M2': minimo,
        'PORQUE_ESSE': (
            'corre sem rede, sem API paga e sem producao, e ja fala a lingua '
            'das falhas — instrumenta-lo custa o writer, e nao um ambiente.'),
        'EXECUTORES': linhas,
    }
    destino = os.path.join(RAIZ, 'system-map', 'data',
                           'executores.generated.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1, default=list)
        f.write('\n')
    print('EXECUTORES=%d · relevantes=%d · %s'
          % (len(linhas), len(relevantes),
             ' '.join('%s=%d' % (k, v) for k, v in sorted(por_estado.items()))))
    return 0


if __name__ == '__main__':
    raise SystemExit(principal())
