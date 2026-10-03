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
import sys

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
# `apify_contrato` e `apify_recuperar` sairam do repositorio em 2026-09-09 por
# estarem mortos. Procurar por eles nao faria mal, mas manteria viva no censo
# uma lista que ja nao descreve a arvore — e uma heuristica que nomeia
# fantasmas convida a proxima pessoa a recria-los.
PAGO = ('apify_pool', 'contrato_ator')
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


# ── OS PAPEIS, E A EVIDENCIA DE CADA UM ──────────────────────────────────
# ⚠️ 54 CAMINHOS RELEVANTES != 54 EXECUTORES. Publicar `TOTAL_EXECUTORS = 54`
# repetiria o erro do 42: um denominador que ninguem mediu, a dar autoridade a
# uma fracao. Cada papel abaixo pede EVIDENCIA no codigo, e quem nao a tiver
# fica UNKNOWN — que e uma resposta, e nao uma falha.
#
# Uma peca PODE ter mais de um papel: o orquestrador tambem preserva, o
# preservador tambem mede. Nao se forca exclusividade — mas cada papel que
# aparece tem de ter a sua propria evidencia.
def _papeis(rel, codigo, imports, etapas):
    achados = []
    if 'orquestrador/' in rel or 'orquestrad' in codigo.lower()[:4000]:
        if 'subprocess' in imports or 'executa' in codigo:
            achados.append('ORCHESTRATOR')
    if rel.startswith('guarda/') and ('sha256' in codigo or 'Armazem' in codigo):
        achados.append('PRESERVATION_OWNER')
    if 'coleta_checkpoint' in imports:
        achados.append('CHECKPOINT_OWNER')
    if 'rastro_da_coleta' in imports and 'registrar(' in codigo:
        achados.append('TELEMETRY_EMITTER')
    if rel.startswith('coleta/') and etapas and (
            'urllib' in imports or 'requests' in imports
            or 'subprocess' in imports or 'collection-store' in codigo):
        achados.append('EXECUTOR')
    if 'ferramentas/' in rel:
        achados.append('ADAPTER')
    return tuple(achados) or ('UNKNOWN',)


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
            'PAPEIS': _papeis(rel, codigo, imports, declara),
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


def medir_tudo():
    """O censo inteiro, como dado. NAO escreve ficheiro e NAO imprime.

    ⚠️ ISTO NAO E ARRUMACAO — E UMA TRAVA, E ELA CUSTOU UM SUSTO.
    Enquanto uma funcao so media E escrevia, uma mutacao que trocava o veredito
    da paridade para testar o portao GRAVOU `PARIDADE: UNKNOWN` dentro de
    `executores.generated.json`. O artefato commitado passou a dizer que a
    prova nao tinha corrido — por causa de um teste.

        UM TESTE QUE PERSISTE A PROPRIA MENTIRA E PIOR DO QUE TESTE NENHUM:
        ELE DEIXA-A LA DEPOIS DE ACABAR.

    Com a medicao separada da escrita, a mutacao nao alcanca o disco.
    """
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

    # ── O DENOMINADOR, SEPARADO ──────────────────────────────────────────
    def com_papel(nome):
        return sum(1 for l in relevantes if nome in l['PAPEIS'])
    denominadores = {
        'TOTAL_FILES_SCANNED': len(linhas),
        'TOTAL_RELEVANT_PATHS': len(relevantes),
        'TOTAL_EXECUTORS_PROVEN': sum(
            1 for l in relevantes if l['STATE'] == 'INSTRUMENTED'),
        'TOTAL_EXECUTORS_BY_ROLE': com_papel('EXECUTOR'),
        'TOTAL_ORCHESTRATORS': com_papel('ORCHESTRATOR'),
        'TOTAL_ADAPTERS': com_papel('ADAPTER'),
        'TOTAL_PRESERVATION_OWNERS': com_papel('PRESERVATION_OWNER'),
        'TOTAL_CHECKPOINT_OWNERS': com_papel('CHECKPOINT_OWNER'),
        'TOTAL_TELEMETRY_EMITTERS': com_papel('TELEMETRY_EMITTER'),
        'TOTAL_UNKNOWN': com_papel('UNKNOWN'),
        'A_LEI': ('CAMINHO RELEVANTE != EXECUTOR PROVADO. O numero grande e de '
                  'caminhos varridos; o pequeno e do que foi provado a correr.'),
    }

    tem_bom = sum(1 for l in relevantes if l['GOOD_PATH_PROVED'])
    tem_falha = sum(1 for l in relevantes if l['FAULT_PATH_PROVED'])

    # ── DUAS PERGUNTAS, E ELAS TINHAM UM NOME SO ─────────────────────────
    # O campo anterior chamava-se MINIMAL_OPERATIONAL_OBSERVABILITY_FOR_M2 e
    # dizia YES — e o MESMO artefato nomeava um bloqueador logo abaixo. Duas
    # afirmacoes que nao podem responder a mesma pergunta.
    #
    #     O INSTRUMENTO EXISTIR != A ROTA ALVO SER OBSERVAVEL.
    #
    # Sao perguntas diferentes com respostas diferentes, e agora tem nomes
    # diferentes.
    # ⚠️ A UNIAO GLOBAL DE ETAPAS DAVA FALSO VERDE.
    # A versao anterior somava as ETAPAS_OBSERVADAS de TODOS os caminhos e
    # perguntava se STRUCTURED e ADMISSION estavam nessa soma. Bastaria a rota
    # A observar STRUCTURED e a rota B observar ADMISSION — nenhuma delas a
    # rota da M2 — para o portao abrir.
    #
    #     GLOBAL STAGE OBSERVATION != TARGET ROUTE OBSERVATION.
    #
    # A identidade da rota NAO foi inventada: ela ja existe no ledger, no bloco
    # FORWARD de cada caminho, com `ROUTE_CLASS_ID` e `SOURCE_ID` provados
    # sobre uma unidade de trabalho real. O portao pergunta a UMA rota, e exige
    # que O MESMO bloco carregue as duas etapas.
    rota_m2 = ('STRUCTURED', 'ADMISSION')
    ROTA_M2_CLASS = 'RC-1'

    rotas_forward = []
    for caminho, v in ledger.items():
        f = v.get('FORWARD')
        if not (v.get('FORWARD_INSTRUMENTED') and f):
            continue
        rotas_forward.append({
            'CAMINHO': caminho,
            'FRONTEIRA': f.get('FRONTEIRA'),
            'ROUTE_CLASS_ID': f.get('ROUTE_CLASS_ID'),
            'SOURCE_ID': f.get('SOURCE_ID'),
            'ETAPAS_OBSERVADAS': sorted(f.get('ETAPAS_OBSERVADAS') or []),
            # ⚠️ E AS ARESTAS, QUE FALTAVAM AO PORTAO.
            # Exigir as tres etapas e necessario e nao chega: tres etapas na
            # mesma rota podem ser tres acontecimentos soltos. A aresta e o que
            # prova que o artefato ATRAVESSOU de uma para a seguinte.
            #
            #     DECLARED EDGE != OBSERVED EDGE.
            #
            # E ela e MEDIDA no banco por `rastro.o_que_a_rota_observou()`, que
            # so a conta com as duas pontas — nunca lida de um `edge_from`
            # solto, que e apenas a intencao de quem escreveu a linha.
            'ARESTAS_OBSERVADAS': [tuple(a) for a in
                                   (f.get('ARESTAS_OBSERVADAS') or [])],
            # E a declaracao de que tudo isso foi UMA execucao encadeada.
            'END_TO_END': bool(f.get('END_TO_END')),
            'RUN_UNICO': f.get('RUN_UNICO'),
            'PROVA': f.get('PROVA'),
            'PROVA_DA_ROTA_NUMA_CORRIDA_SO':
                f.get('PROVA_DA_ROTA_NUMA_CORRIDA_SO'),
        })

    # A rota da M2 e a que atravessa a classe RC-1 pelo fluxo forward.
    candidatas = [r for r in rotas_forward
                  if r['ROUTE_CLASS_ID'] == ROTA_M2_CLASS]
    # Uma rota SO fecha o portao se ELA PROPRIA observar as duas etapas.
    # `any` sobre rotas, `all` sobre etapas — nunca o contrario.
    # ⚠️ TRES EXIGENCIAS, E ELAS NAO SE SUBSTITUEM.
    # Duas sessoes chegaram a este portao ao mesmo tempo e cada uma trouxe
    # metade da trava. Guardam-se as duas, porque medem coisas diferentes:
    #
    #   ETAPAS      as tres correram nesta rota
    #   ARESTAS     e foram PERCORRIDAS, nao so desenhadas —
    #               UMA SETA DESENHADA NAO E UM CAMINHO PERCORRIDO
    #   END_TO_END  e tudo isso numa UNICA execucao encadeada —
    #               SAME ROUTE CLASS != SAME EXECUTION FLOW, e
    #               TWO COMPATIBLE PROOFS != ONE END-TO-END EXECUTION
    #
    # `any` sobre rotas, `all` sobre etapas e arestas — nunca o contrario.
    arestas_m2 = (('DERIVED', 'STRUCTURED'), ('STRUCTURED', 'ADMISSION'))
    rota_completa = next(
        (r for r in candidatas
         if r.get('END_TO_END')
         and all(e in r['ETAPAS_OBSERVADAS'] for e in rota_m2)
         and all(a in r['ARESTAS_OBSERVADAS'] for a in arestas_m2)), None)
    # A ORDEM E A DA ROTA, e nao alfabetica: DERIVED -> STRUCTURED ->
    # ADMISSION e uma sequencia, e ler «ADMISSION, STRUCTURED» inverte o
    # caminho na cabeca de quem le.
    # O que falta E DA ROTA COMPLETA se ela existir; senao, da melhor
    # candidata — nunca da uniao, que foi o defeito que isto fechou.
    melhor = rota_completa or (max(candidatas,
                                   key=lambda r: len(set(rota_m2) &
                                                     set(r['ETAPAS_OBSERVADAS'])),
                                   default=None))
    vistas = set((melhor or {}).get('ETAPAS_OBSERVADAS') or [])
    vistas_arestas = set((melhor or {}).get('ARESTAS_OBSERVADAS') or [])
    faltam = [] if rota_completa else [e for e in rota_m2 if e not in vistas]
    arestas_faltam = ([] if rota_completa else
                      [list(a) for a in arestas_m2 if a not in vistas_arestas])
    # ⚠️ «NAO FALTA NENHUMA ETAPA» E «AS ETAPAS ESTAO NA MESMA VIAGEM» SAO
    # DUAS COISAS. Sem esta distincao o relato dizia NO com `faltam=[]`, e um
    # portao que reprova sem dizer porque e um portao que ninguem consegue
    # discutir.
    composta = (not rota_completa) and not faltam and not arestas_faltam

    # ── E UMA TERCEIRA PERGUNTA, QUE TAMBEM ESTAVA ESCONDIDA NAS OUTRAS ──
    #
    #     REPLAY DE ARQUIVO INSTRUMENTADO != ESTRADA CANONICA INSTRUMENTADA.
    #
    # Ate O9R o ledger dizia `FORWARD_INSTRUMENTED: false` para todos, e isso
    # era medido e verdadeiro. Publicar so `TELEMETRY_INFRASTRUCTURE_PROVED`
    # deixava a distincao a viver numa nota — e nota nao e campo. Este campo e
    # DERIVADO do ledger, e nunca digitado: quem quiser move-lo tem de provar
    # um caminho forward, com fronteira e prova que existam em disco.
    forward = {k: v.get('FORWARD') for k, v in ledger.items()
               if v.get('FORWARD_INSTRUMENTED')}
    forward_provado = sorted(forward)

    # ⚠️ CLAIMED CRITERION MUST BE CONSUMED CRITERION.
    # Este portao LISTAVA «paridade_da_lingua.py PASS» entre os criterios e
    # NAO a consumia: o veredito saia so de `tem_bom` e `tem_falha`. Com o
    # contrato, o banco, o writer e o scanner em desacordo, ele continuaria a
    # dizer YES — a afirmar uma coisa que nao tinha medido.
    #
    # Nao se inventou prova nova: consome-se a que ja existe, e ela e um
    # artefato reproduzivel com codigo de saida proprio.
    paridade = subprocess.run(
        [sys.executable, os.path.join(RAIZ, 'provas', 'paridade_da_lingua.py')],
        capture_output=True, text=True)
    paridade_passa = paridade.returncode == 0

    instrumento = {
        'TELEMETRY_INFRASTRUCTURE_PROVED': (
            'YES' if (paridade_passa and tem_bom >= 1 and tem_falha >= 1)
            else 'NO'),
        'O_QUE_MEDE': (
            'o instrumento — contrato, storage, writer e scanner — aguenta uma '
            'passagem real, boa e quebrada. Mede UMA coisa so.'),
        'CRITERIOS': {
            'CONTRATO_IMPLEMENTAVEL_PONTA_A_PONTA': paridade_passa,
            'ONDE_SE_MEDE_ISSO': 'provas/paridade_da_lingua.py (consumida, e '
                                 'nao citada: o codigo de saida dela entra no '
                                 'veredito)',
            'CAMINHO_REAL_PROVADO_BOM': tem_bom >= 1,
            'CAMINHO_REAL_PROVADO_QUEBRADO': tem_falha >= 1,
            'CONTABILIDADE_FECHA': tem_bom >= 1,
            'RETOMADA_SABE_ONDE_RECOMECAR': tem_falha >= 1,
        },
        'O_QUE_NAO_MEDE': (
            'nao mede cobertura, e nao mede a rota da M2. O fluxo forward '
            'canonico tem campo proprio, mesmo aqui ao lado — juntar os dois '
            'foi exatamente o erro que O10R desfez.'),
    }

    caminho_forward = {
        'CANONICAL_FORWARD_PATH_PROVED': 'YES' if forward_provado else 'NO',
        'O_QUE_MEDE': (
            'se algum executor tem a sua ESTRADA CANONICA FORWARD instrumentada '
            '— raw_asset real no banco, dono canonico da escrita, e a passagem '
            'a chegar ao rastro — e nao apenas um replay do corpo historico.'),
        'A_LEI': 'LEGACY_REPLAY_INSTRUMENTED != CANONICAL_FORWARD_INSTRUMENTED',
        'QUAIS': forward_provado,
        'FRONTEIRAS': sorted({(v or {}).get('FRONTEIRA')
                              for v in forward.values() if v}),
        'PROVAS': sorted({(v or {}).get('PROVA')
                          for v in forward.values() if v}),
        'O_QUE_NAO_MEDE': (
            'nao diz que a cadeia forward esta COMPLETA. O caminho provado '
            'termina em DERIVED, e termina ai porque STRUCTURED e ADMISSION '
            'nao tem dono forward ligado. UM CAMINHO INSTRUMENTADO NAO E TODOS '
            'OS EXECUTORES INSTRUMENTADOS.'),
    }

    rota = {
        # ⚠️ O VEREDITO VEM DE `rota_completa`, E NAO DE `faltam`.
        # Uma mutacao apanhou isto: com a rota A a observar STRUCTURED e a rota
        # B a observar ADMISSION, `faltam` — calculado sobre a UNIAO das
        # candidatas — dava vazio, e o portao abria. Era o mesmo falso verde,
        # um nivel mais fundo: o denominador tinha sido corrigido e o veredito
        # continuava a ler a soma.
        #
        #     UMA ROTA COM AS DUAS != DUAS ROTAS COM UMA CADA.
        'M2_ROUTE_OBSERVABILITY_READY': ('YES' if rota_completa else 'NO'),
        'O_QUE_MEDE': ('se a rota que a M2 vai construir — DERIVED -> '
                       'STRUCTURED -> ADMISSION — ja emite telemetria.'),
        'ROTAS_FORWARD_CONHECIDAS': rotas_forward,
        'PORQUE_NAO_A_UNIAO_GLOBAL': (
            'GLOBAL STAGE OBSERVATION != TARGET ROUTE OBSERVATION. Duas rotas '
            'diferentes a observar uma etapa cada nao fazem uma rota que '
            'observa as duas. O portao le UM bloco FORWARD, e exige que ELE '
            'carregue STRUCTURED e ADMISSION.'),
        'ETAPAS_DA_ROTA_M2_NUNCA_OBSERVADAS': faltam,
        # ⚠️ TRES ETAPAS SOLTAS NAO SAO UMA ROTA.
        # A aresta e o que prova que o artefato atravessou de uma etapa para a
        # seguinte. Ela e MEDIDA no banco — so conta com as duas pontas — e
        # nunca lida de um `edge_from` solto, que e a intencao de quem escreveu
        # a linha e nao o caminho que ela percorreu.
        'ARESTAS_DA_ROTA_M2_NUNCA_OBSERVADAS': arestas_faltam,
        'A_LEI_DA_ARESTA': 'DECLARED EDGE != OBSERVED EDGE',
        'ONDE_A_ARESTA_E_MEDIDA':
            'medidas/rastro_da_coleta.o_que_a_rota_observou() · '
            'provas/a_rota_m2_atravessa.py',
        # ⚠️ A PROJECAO MOSTRA O QUE O PORTAO CONSUMIU, e nao menos.
        # Ela omitia `END_TO_END` e `RUN_UNICO`: o artefato dizia YES e nao
        # deixava ver por que exigencias ele passou. Um veredito que esconde o
        # seu criterio nao se consegue discutir.
        'ROTA_MEDIDA': ({'SOURCE_ID': (melhor or {}).get('SOURCE_ID'),
                         'END_TO_END': (melhor or {}).get('END_TO_END'),
                         'RUN_UNICO': (melhor or {}).get('RUN_UNICO'),
                         'ROUTE_CLASS_ID': (melhor or {}).get('ROUTE_CLASS_ID'),
                         'ETAPAS_OBSERVADAS': sorted(vistas),
                         'ARESTAS_OBSERVADAS': sorted(vistas_arestas),
                         'PROVA': (melhor or {}).get(
                             'PROVA_DA_ROTA_NUMA_CORRIDA_SO')
                         or (melhor or {}).get('PROVA')}
                        if melhor else None),
        'PORQUE_NAO': (
            ('as etapas %s nunca correram nesta rota.' % ', '.join(faltam))
            if faltam else
            ('as tres etapas aparecem, mas NAO numa unica execucao encadeada. '
             'SAME ROUTE CLASS != SAME EXECUTION FLOW, e TWO COMPATIBLE PROOFS '
             '!= ONE END-TO-END EXECUTION. Falta uma prova que atravesse as '
             'tres no mesmo run, com a saida de cada etapa a alimentar a '
             'seguinte.') if composta else None),
        'FALTA_E2E': composta,
        'O_PORTAO_CORRETO': (
            'nao e «observar a rota antes de ela existir» — e «a rota nasce '
            'instrumentada». O instrumento esta provado e disponivel; a M2 '
            'pode CONSTRUIR, e nao pode FECHAR sem a rota emitir.'),
        'M2_CONSTRUCTION_CAN_BEGIN': (
            'YES' if instrumento['TELEMETRY_INFRASTRUCTURE_PROVED'] == 'YES'
            else 'NO'),
        'M2_CANNOT_CLOSE_UNTIL_INSTRUMENTED': True,
        'INVARIANTES_DA_M2': (
            'o primeiro caminho corrivel ja emite telemetria; STRUCTURED e '
            'ADMISSION nao podem ser marcados observados antes de correrem; '
            'cada etapa fecha a contabilidade; a falha localiza onde parou; '
            'downstream NOT_RUN e nunca ERROR em cascata; a identidade da '
            'fonte e da rota vem do dono ou fica UNKNOWN; nenhum READY antes '
            'da COL-LAW-043; o System Map atualiza por scanner.'),
    }
    minimo = {'TELEMETRY_INFRASTRUCTURE': instrumento,
              'CANONICAL_FORWARD_PATH': caminho_forward,
              'M2_ROUTE': rota}

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
        'DENOMINADORES': denominadores,
        'PORQUE_ESSE': (
            'corre sem rede, sem API paga e sem producao, e ja fala a lingua '
            'das falhas — instrumenta-lo custa o writer, e nao um ambiente.'),
        'EXECUTORES': linhas,
    }
    return saida


def principal():
    saida = medir_tudo()
    destino = os.path.join(RAIZ, 'system-map', 'data',
                           'executores.generated.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1, default=list)
        f.write('\n')
    print('EXECUTORES=%d · relevantes=%d · %s'
          % (saida['TOTAL_FICHEIROS'], saida['TOTAL_CAMINHOS_RELEVANTES'],
             ' '.join('%s=%d' % (k, v)
                      for k, v in sorted(saida['POR_ESTADO'].items()))))
    return 0


if __name__ == '__main__':
    raise SystemExit(principal())
