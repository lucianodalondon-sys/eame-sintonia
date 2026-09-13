#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-RC-01 §15 — A MUTAÇÃO DIZ SE A RELEASE ESTÁ MESMO GUARDADA.

    python3 provas/mutacao_da_release_v1.py

Trinta e duas sentinelas verdes só provam que elas passaram. A pergunta é:

    SE EU PARTIR A RELEASE, ALGUMA FICA VERMELHA?

Um mutante que sobrevive acusa a BATERIA, e não o código.

Muta-se uma CÓPIA da árvore. A árvore real não é tocada.

    APIFY_RUNS = 0 · REAL_NETWORK = 0 · COST_USD = 0
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: As baterias que guardam a Release. A da SR-02 entra porque metade das
#: classes de mutante da §15 são sobre a compra, e o dono delas é ela.
BATERIAS = ('tests.test_scrap_rc01_release_candidate',
            'tests.test_scrap_sr02_autorizacao_de_gasto',
            'tests.test_scrap_flow01_caminho_canonico')

WF = '.github/workflows/sintonia-scrap.yml'
LEI = 'leis/autorizacao_de_gasto.py'
REL = 'leis/relevancia_da_fonte.py'
ADP = 'coleta/scrap_colheita.py'
DONO = 'coleta/coletor.py'
EXE = 'coleta/scrap_executor.py'
ROT = 'coleta/social_rotas.py'
SUP = 'provas/superficie_do_scrap_v1.py'
REC = 'pedido/receitas.py'
AZ = 'leis/autorizacao_de_gasto.py'
CDP = 'ferramentas/cdp.py'
HTTP = 'coleta/scrap_http.py'
IGA = 'coleta/adaptador_instagram.py'

#: Cada mutante é uma das dez classes que a §15 nomeia, escrita como uma
#: mudança que MUDA COMPORTAMENTO — renomear uma variável não é um mutante.
#:
#:     UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
MUTACOES = [
    # ── 1 · REMOVE RELEVANCE GATE ─────────────────────────────────────────
    ('M1 · a autorização deixa de perguntar à relevância', LEI,
     "        if v['VEREDITO'] != rel.AUTORIZA:",
     "        if False:",
     'nenhuma compra normal sem o sim da relevância'),

    ('M2 · o portão da relevância deixa de bloquear', REL,
     "        'BLOQUEIA_A_CORRIDA': bool(gastos) and not pode_gastar,",
     "        'BLOQUEIA_A_CORRIDA': False,",
     'pago, agendado e total bloqueiam com o livro vazio'),

    # ── 2 · REMOVE SPEND GUARD ────────────────────────────────────────────
    ('M3 · a guarda de gasto sai da primitiva paga', DONO,
     "    recibo = az.conferir_e_consumir(\n"
     "        autorizacao, motivo=motivo, proposito=proposito,\n"
     "        source_id=source_id, teto_usd=teto_usd,\n"
     "        orcamento_autorizado=_autorizado,\n"
     "        ledger=None if _orc is None else _orc.identidade)",
     "    recibo = {'CAN_START_PAID_EXECUTION': True}",
     'nenhum POST nasce sem autorização consumida'),

    # ── 3 · ACCEPT FABRICATED AUTHORIZATION ───────────────────────────────
    ('M4 · o selo deixa de ser exigido na construção', LEI,
     "        if self._selo is not _SELO:",
     "        if False:",
     'uma autorização escrita à mão não nasce'),

    ('M5 · o consumo aceita qualquer objeto', LEI,
     "    if not isinstance(autorizacao, Autorizacao) or autorizacao._selo is not _SELO:",
     "    if False:",
     'um dicionário com a forma certa não é autorização'),

    # ── 4 · REPEAT PAID POST ──────────────────────────────────────────────
    # ⚠️ A ANCORA DESTE MUTANTE JA FOI ROUBADA UMA VEZ, e por um comentario.
    # Ela era `"    reg['GASTAS'] += 1"` — quatro espacos — e a NIGHT-SHIFT-01
    # escreveu, no mesmo ficheiro, um comentario que CITA a linha:
    #
    #     #     reg['GASTAS'] += 1
    #
    # O texto do comentario contem a ancora como sub-cadeia. `replace(..., 1)`
    # trocou a PRIMEIRA ocorrencia — o comentario — e o codigo ficou intacto. O
    # mutante nao mudou nada e o relatorio chamou-lhe SOBREVIVENTE.
    #
    #     UM COMENTARIO QUE CITA O CODIGO ROUBA A ANCORA DE QUEM MUTA O CODIGO.
    #
    # A ancora passa a ser de DUAS LINHAS, e a segunda e codigo que nenhum
    # comentario desta casa repete. `_ancora_unica()` guarda o resto.
    ('M6 · a autorização deixa de se gastar', LEI,
     "        reg['GASTAS'] += 1\n"
     "    recibo = autorizacao.para_o_manifesto()",
     "    recibo = autorizacao.para_o_manifesto()",
     'uma autorização de UMA execução não paga duas'),

    # ── 5 · BYPASS ORCHESTRATOR ───────────────────────────────────────────
    ('M7 · o canário passa a chamar o adapter direto', WF,
     '            canario-bluesky)\n'
     '              PYTHONIOENCODING=utf-8 $PY orquestrador/orquestrador.py \\',
     '            canario-bluesky)\n'
     '              PYTHONIOENCODING=utf-8 $PY coleta/scrap_colheita.py \\',
     'o disparador do canário chama o orquestrador'),

    ('M8 · o executor do SCRAP sai da receita', REC,
     '        "roda": ["coleta/scrap_colheita.py"],',
     '        "roda": ["coleta/social_scrap.py", "coletar"],',
     'a receita serve a fase do canário pelo adapter'),

    # ── 6 · BYPASS SOCIAL POLICY ──────────────────────────────────────────
    # ⚠️ DUAS VERSÕES DESTE MUTANTE SOBREVIVERAM POR SEREM EQUIVALENTES, E ISSO
    # MEDIU-SE: destrancar `permitir_pago` no roteador não muda nada, porque a
    # linha seguinte recusa pelo motivo de gasto e escreve o MESMO estado; e
    # aceitar `rotas[0]` quando não há permitida não muda nada, porque o
    # `CHECK` já parou a capacidade antes.
    #
    #     UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO ACUSA A BATERIA:
    #     ACUSA A DEFESA EM PROFUNDIDADE QUE ELE NÃO CONSEGUIU ATRAVESSAR.
    #
    # Este muda: com ele, `YOUTUBE/FETCH_TRANSCRIPT` passa a ter como rota
    # padrão uma `PERMITIDA = NAO`.
    ('M9 · a política aceita rota NÃO permitida', 'leis/social_matriz.py',
     "    viaveis = [x for x in rotas if x['PERMITIDA'] in ('SIM', 'CONDICIONAL')\n"
     "               and x['ESTADO'] not in ('ROUTE_NOT_ALLOWED',)]",
     "    viaveis = list(rotas)",
     'nenhuma rota NÃO permitida vira rota padrão'),

    # ── 7 · PROMOTE DECLARED TO READY WITHOUT EDGE ────────────────────────
    # O mesmo cuidado: tirar a aresta do classificador da superfície era
    # equivalente, porque o `CHECK` já responde `DECLARED_WITHOUT_ROUTE`. Quem
    # guarda a lei é o `CHECK`, e é nele que o mutante tem de morder.
    ('M10 · o CHECK deixa de exigir rota ligada', EXE,
     "    if not reg.tem_caminho(plat, capacidade):",
     "    if False:",
     'capacidade declarada sem rota não pode correr'),

    # ── 8 · PROMOTE EDGE TO FLOW WITHOUT RUN ──────────────────────────────
    ('M11 · a superfície passa a prometer fluxo observado', SUP,
     "READY = 'READY'",
     "READY = 'FLOW_OBSERVED'",
     'os estados são os cinco que a missão nomeia'),

    # ── 9 · TURN UNKNOWN INTO SUCCESS ─────────────────────────────────────
    ('M12 · capacidade não declarada passa a poder correr', EXE,
     "    if not cap.existe(capacidade):",
     "    if False and not cap.existe(capacidade):",
     'UNKNOWN não vira sucesso'),

    ('M13 · o portão epistemológico deixa de recusar', EXE,
     "    if not promete and modo == NORMAL:",
     "    if False:",
     'estado que não promete resultado não colhe em NORMAL'),

    # ── 10 · REINTRODUCE HIDDEN PAID FALLBACK ─────────────────────────────
    ('M14 · o ramo do canário ganha um segundo caminho', WF,
     '                --filtro handle="${{ inputs.handle }}" ;;',
     '                --filtro handle="${{ inputs.handle }}" \\\n'
     '                || PYTHONIOENCODING=utf-8 $PY coleta/social_scrap.py \\\n'
     '                     coletar janela ;;',
     'nenhum fallback escondido num entrypoint V1'),

    # ── E OS QUE ESTA MISSÃO ACRESCENTOU ──────────────────────────────────
    ('M15 · o adapter passa a derivar a fonte do alvo', ADP,
     "    if not fonte:",
     "    fonte = fonte or extra.get('handle')\n"
     "    if not fonte:",
     'HANDLE NÃO É SOURCE_ID'),

    ('M16 · a lista de filtros por fase deixa de recusar', ADP,
     "    if sobra:",
     "    if False:",
     'um filtro fora da lista da fase recusa a corrida'),

    ('M17 · a fase do canário troca de capacidade', ADP,
     "    'canario-bluesky': ('BLUESKY', 'bluesky.author.incremental', {'limit': 1},\n"
     "                        rc.COLHEITA),",
     "    'canario-bluesky': ('INSTAGRAM', 'instagram.profile.discovery', {},\n"
     "                        rc.COLHEITA),",
     'a fase do canário pede a capacidade do canário'),

    ('M18 · o alvo em falta deixa de parar a corrida', ADP,
     "    if falta:",
     "    if False:",
     'sem o alvo a fase do canário não começa'),

    ('M19 · o bruto deixa de dizer que não está preservado',
     'coleta/social_envelope.py',
     "        'PRESERVATION': NOT_PRESERVED,",
     "        'PRESERVATION': 'PRESERVED',",
     'RAW_REFERENCE para arquivo que some não é proveniência'),

    # A linha que corre é a do RETORNO DO PORTÃO — a outra só é alcançada por
    # capacidades que chegam a executar, e nesta árvore todas essas já são
    # `PROVEN`, o que tornava o mutante invisível. Medido, não suposto.
    # ⚠️ E ESTE MUTANTE APONTAVA PARA O SITIO ERRADO — foi o guarda de ancora
    # ambigua desta madrugada que o descobriu, no minuto em que nasceu.
    # `'CAPABILITY_STATE_AFTER': pronto['CAPABILITY_STATE']` aparece DUAS vezes
    # em `scrap_executor.py`, e as duas sao ramos de RECUSA — a capacidade nem
    # correu. `replace(..., 1)` mutava a primeira, e o mutante nunca tocou no
    # caminho de que a lei fala.
    #
    #     TRIAL PASSADO != CAPACIDADE PROVADA e uma lei sobre o que CORREU.
    #     MUTAR O RAMO QUE RECUSA NAO TESTA A LEI DE QUEM PASSOU.
    #
    # O sitio certo e o do SUCESSO, e ele le o estado do dono
    # (`cap.estado(capability)`) em vez do que o CHECK trouxe — expressao que
    # aparece uma unica vez no ficheiro, e e a que `test_rt32` vigia.
    ('M20 · o portão promove o estado da capacidade', EXE,
     "                  'CAPABILITY_STATE_AFTER': cap.estado(capability)})",
     "                  'CAPABILITY_STATE_AFTER': 'PROVEN'})",
     'TRIAL PASSADO != CAPACIDADE PROVADA'),

    # ══════════════════════════════════════════════════════════════════════
    # OS QUE A CONTINUACAO ACRESCENTOU — politica, ledger, especie, tecto
    # ══════════════════════════════════════════════════════════════════════
    ('M21 · a politica sai da porta paga', DONO,
     "    if _proibida:",
     "    if False:",
     'dinheiro autorizado nao abre rota proibida'),

    ('M22 · a matriz deixa de reconhecer o ator proibido', 'leis/social_matriz.py',
     "    if proibidas and not permitidas:",
     "    if False:",
     'a matriz responde pelo ator que ela nomeia'),

    ('M23 · a politica vem DEPOIS da guarda de gasto', DONO,
     "        raise RotaNaoPermitida(\n"
     "            'ROUTE_NOT_ALLOWED · %s. Nenhum POST foi criado, e nenhuma '\n"
     "            'autorizacao foi consumida.' % _porque)",
     "        pass",
     'a rota proibida nao consome a autorizacao'),

    ('M24 · o orcamento deixa de ser conferido contra a autorizacao', LEI,
     "        if declarado > humano + 1e-9:",
     "        if False:",
     'FINANCIAL_BUDGET.AUTHORIZED <= AUTORIZACAO.MAX_USD'),

    ('M25 · a autorizacao deixa de se prender a um ledger', LEI,
     "        elif reg['LEDGER'] != ledger:",
     "        elif False:",
     'um limite conferido contra um ledger que muda nao foi conferido'),

    ('M26 · a autorizacao volta a poder ser reescrita', LEI,
     "        if getattr(self, '_fechada', False):",
     "        if False:",
     'uma autorizacao que muda depois de concedida nao foi conferida'),

    ('M27 · o consumo volta para dentro do objecto', LEI,
     "        return _registo(self._id)['GASTAS']",
     "        return 0",
     'copiar uma autorizacao nao e receber uma autorizacao'),

    ('M28 · a especie da fase deixa de decidir o terminal', ADP,
     "    if especie != rc.COLHEITA:",
     "    if False:",
     'so COLHEITA atravessa o ingresso'),

    ('M29 · o teto de itens deixa de descer', ADP,
     "                      **{aceites[k]: v for k, v in nomeados.items()})",
     "                      )",
     'o teto do pedido chega a rota'),

    ('M30 · o conteudo do LinkedIn volta a prometer resultado',
     'coleta/scrap_capacidades.py',
     "    'linkedin.direct_post': ('LINKEDIN', BLOCKED, ONLINE, None, _C11, 'FETCH_POST'),",
     "    'linkedin.direct_post': ('LINKEDIN', PROVEN, ONLINE, None, _C11, 'FETCH_POST'),",
     'uma rota que funciona nao e uma rota permitida'),

    # ── 11 · UMA ROTA QUE NAO CORREU VOLTA A PODER OBSERVAR ───────────────
    ('M31 · o esqueleto de uma rota recusada volta a ser colheita', ADP,
     "    if objetos and trace.get('COST_STATE') == NAO_CORREU:",
     "    if False:",
     'uma rota que nao correu nao observou nada'),

    # ── 12 · UMA FALHA QUE SABE VOLTA A CHEGAR COMO UMA QUE NAO SABE ──────
    ('M32 · o dono da ferramenta deixa de declarar o estado', CDP,
     "        self.estado = estado",
     "        self.estado = None",
     'sem navegador, o estado diz qual e'),

    ('M33 · o adaptador deixa de traduzir o estado declarado', IGA,
     "        if declarado:\n"
     "            # A frase viaja em `DETALHE` e nao em `NATIVE_REASON`: o segundo e",
     "        if False:\n"
     "            # A frase viaja em `DETALHE` e nao em `NATIVE_REASON`: o segundo e",
     'uma falha que sabe nao chega como uma que nao sabe'),

    ('M34 · a frase perde-se e so ficam os nomes', HTTP,
     "        if rel.get('DETALHE'):",
     "        if False:",
     'um estado sem a frase manda a pessoa certa para o sitio errado'),

    ('M35 · o roteador volta a escrever a chave a None', ROT,
     "        for campo in ('NATIVE_REASON', 'RECOVERY_ACTION'):\n"
     "            if e.rel.get(campo):\n"
     "                registro[campo] = e.rel[campo]",
     "        registro['NATIVE_REASON'] = e.rel.get('NATIVE_REASON')\n"
     "        registro['RECOVERY_ACTION'] = e.rel.get('RECOVERY_ACTION')",
     'uma chave escrita a None nao e uma chave ausente'),

    # ── 13 · CONFERIR E CONSUMIR VOLTAM A SER DOIS ACTOS ──────────────────
    ('M36 · a trava sai da porta paga', AZ,
     "_TRAVA = threading.Lock()",
     "class _Solta(object):\n"
     "    def __enter__(self): return self\n"
     "    def __exit__(self, *a): return False\n"
     "_TRAVA = _Solta()",
     'duas corridas ao mesmo tempo nao pagam duas vezes'),
]


def _copia(destino):
    pesadas = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
               '.tmp', 'build'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'))
        else:
            shutil.copy2(o, a)
    for nome in ('.git', 'data'):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _correr(arvore):
    p = subprocess.run([sys.executable, '-m', 'unittest'] + list(BATERIAS),
                       cwd=arvore, capture_output=True, text=True, timeout=1200)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    print('SCRAP-RC-01 · MUTAÇÃO DA RELEASE CANDIDATE')
    print('=' * 78)
    base = tempfile.mkdtemp(prefix='rc01-mut-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _copia(arvore)
        codigo, saida = _correr(arvore)
        if codigo != 0:
            print('A CÓPIA JÁ NASCE VERMELHA — a mutação não mediria nada.')
            print(saida[-2500:])
            return 3
        print('cópia limpa: baterias VERDES\n')

        sobreviventes = []
        for nome, rel, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-56s ALVO_AUSENTE' % nome[:56])
                sobreviventes.append((nome, 'ALVO_AUSENTE — a mutação não foi aplicada'))
                continue
            # ── UMA ÂNCORA AMBÍGUA MUTA O SÍTIO ERRADO ────────────────────
            # ⚠️ MEDIDO NA NIGHT-SHIFT-01: M6 apontava para uma linha que um
            # comentário do mesmo ficheiro CITAVA. `replace(..., 1)` trocou o
            # comentário, o código ficou igual, e o relatório disse
            # «SOBREVIVE» — acusando a bateria de um buraco que ela não tinha.
            #
            #     UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
            #     E UM QUE MUDA O NÚMERO ERRADO É PIOR: ELE MENTE COM CONFIANÇA.
            #
            # Contar é a única defesa que não depende de alguém reparar.
            quantas_vezes = original.count(velho)
            if quantas_vezes != 1:
                print('%-56s ALVO_AMBIGUO (%d ocorrências)'
                      % (nome[:56], quantas_vezes))
                sobreviventes.append(
                    (nome, 'ALVO_AMBIGUO — a âncora aparece %d vezes, e a '
                           'mutação iria ao sítio errado' % quantas_vezes))
                continue
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(original.replace(velho, novo, 1))
            try:
                codigo, saida = _correr(arvore)
            finally:
                with open(alvo, 'w', encoding='utf-8') as f:
                    f.write(original)
            morta = codigo != 0
            quantas = saida.count('FAIL: ') + saida.count('ERROR: ')
            print('%-56s %s (%d sentinelas)'
                  % (nome[:56], 'MORTA  ' if morta else 'SOBREVIVE', quantas))
            if not morta:
                sobreviventes.append((nome, garantia))

        print('=' * 78)
        print('MUTANTS   = %d' % len(MUTACOES))
        print('SURVIVORS = %d' % len(sobreviventes))
        for nome, porque in sobreviventes:
            print('  SOBREVIVEU · %s — ninguém guarda: %s' % (nome, porque))
        return 0 if not sobreviventes else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
