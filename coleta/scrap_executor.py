#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O SINTONIA SCRAP COMO EXECUTOR — os seis verbos de `COL-LAW-013`.

    import scrap_executor as scrap
    scrap.CAPABILITIES()
    scrap.CHECK('YOUTUBE', 'youtube.search')     # nao gasta nada
    scrap.COLLECT(platform=..., capability=..., run_id=...)

ESTE FICHEIRO NAO E UM ORQUESTRADOR, E A DIFERENCA NAO E DE TAMANHO
--------------------------------------------------------------------
`orquestrador/orquestrador.py` continua a ser o dono unico da orquestracao, e
esta ACIMA disto. `COL-LAW-011`, e nao se reabre sem contraexemplo.

    COLLECTION_REQUEST
            ↓
    ORQUESTRADOR CANONICO        ← decide missao, dominio, universo, prioridade
            ↓
    SINTONIA SCRAP EXECUTOR      ← este ficheiro: executa a capacidade pedida
            ↓
    SCRAP ADAPTER ROUTER
            ↓
    ADAPTERS → PROVIDERS

O que este executor NAO decide, e nao ha excecao:

    qual missao global executar · que dominios coletar · que universo atender
    admissao · julgamento · prioridade global · a regra epistemologica da Collection

    COLETAR != ADMITIR != JULGAR. Ele faz o primeiro, e so o primeiro.

E NAO CRIA `COLLECTION_REQUEST`
--------------------------------
Um executor que fabrica o proprio pedido deixou de ser executor. Ha um teste
que le este ficheiro a procura disso, porque um comentario nao o impediria.

O VERBO QUE MAIS IMPORTA E O `CHECK`
-------------------------------------
`CHECK` responde «consigo chegar la agora?» SEM GASTAR. E ele que permite ao
orquestrador escolher a rota mais barata capaz — `COL-LAW-018` — em vez de
descobrir o custo depois de o ter pago.

    UM `CHECK` QUE GASTA NAO E UM CHECK. E UMA COLETA COM OUTRO NOME.

O AMBIENTE E DEVOLVIDO, NAO ESCOLHIDO
--------------------------------------
`CHECK` diz onde a capacidade corre — `ONLINE`, `LOCAL`, `EITHER`, `HYBRID` ou
`UNKNOWN` — e, quando e LOCAL ou HYBRID, por que. Quem decide executar la e
quem coordena; este ficheiro so informa.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_capacidades as cap    # noqa: E402
import scrap_registo as reg        # noqa: E402
import scrap_fornecedores as forn  # noqa: E402
# A POLITICA e CONSULTADA aqui, nunca decidida. `CAPABILITIES` mostra o
# eixo dela ao lado dos outros dois; quem responde continua a ser ela.
import social_matriz as mz         # noqa: E402

EXECUTOR_ID = 'SINTONIA_SCRAP'
EXECUTOR_VERSION = '1.0.0'

#: `COL-LAW-016`: o orquestrador conhece tres escopos. A semantica do cursor de
#: cada fonte e assunto INTERNO deste executor, e nao sobe.
ESCOPOS = ('PONTUAL', 'INCREMENTAL', 'TOTAL')

#: Onde este executor larga o que traz. `COL-LAW-013` chama-lhe OUTPUT.
LARGA_EM = (
    'data/samples/COMPETITOR-PUBLIC-COMM',
    'data/raw/REEL-MIDIA',
    'data/samples/REEL-TRANSCRICOES',
)

# ── OS ESTADOS DO `CHECK` ─────────────────────────────────────────────────
PODE = 'CAN_COLLECT_NOW'
SEM_ROTA = 'DECLARED_WITHOUT_ROUTE'
NAO_DECLARADA = 'CAPABILITY_NOT_DECLARED'
SEM_PROMESSA = 'CAPABILITY_STATE_PROMISES_NOTHING'
AMBIENTE_ERRADO = 'WRONG_EXECUTION_ENVIRONMENT'
#: O veredicto do `CHECK` em modo de ensaio: NAO promete resultado, e pode ser
#: medida. Nunca se confunde com `PODE` — sao duas perguntas e duas respostas.
ELEGIVEL_PARA_ENSAIO = 'TRIAL_ELIGIBLE'
#: `BLOCKED` recusa tambem em ensaio, e o §14 desta missao diz porque.
ENSAIO_RECUSADO = 'TRIAL_REFUSED_BY_CAPABILITY_STATE'

# ══════════════════════════════════════════════════════════════════════════
# O MODO DE EXECUÇÃO — O TERCEIRO EIXO, E O ÚNICO QUE FALTAVA
# ══════════════════════════════════════════════════════════════════════════
# Este executor já separava dois eixos e tratava-os como donos diferentes:
#
#     CAPABILITY_STATE    o que MEDIMOS que sabemos fazer   `scrap_capacidades`
#     ROUTE_POLICY        que porta é PERMITIDA             `leis/social_matriz`
#
# Faltava o terceiro, e a falta produzia um ciclo fechado. Uma capacidade
# `NOT_EXECUTED` não promete resultado; `CHECK` recusa-a; para deixar de ser
# `NOT_EXECUTED` ela tem de correr uma vez; e como o executor a recusa, ela
# corre por um script lateral — que depois alguém «integra».
#
#     UMA FERRAMENTA QUE RECUSA TUDO O QUE AINDA NÃO PROVOU FAZ NASCER TODA
#     CAPACIDADE NOVA FORA DELA.
#
# Não é hipótese. Duas capacidades estão nesse ciclo HOJE, com adaptador ligado
# e política permitida: `bluesky.author.incremental` e
# `mastodon.account.incremental`. E o `piloto` do `social_scrap.py` — que a
# C10.6D mediu a saltar o boundary — é o script lateral que o ciclo já produziu.
#
# O terceiro eixo é este, e ele NÃO é uma autorização:
#
#     NORMAL   «vou colher, e espero resultado»
#     TRIAL    «vou MEDIR se consigo, e NÃO espero resultado»
#
# A ÚNICA diferença entre os dois, em todo o caminho, é o portão epistemológico
# da CAPABILITY_STATE. Política, roteamento, adaptador, fornecedor, gasto e
# taxonomia de falha são idênticos — e as sentinelas desta missão existem para
# que continuem a ser.
#
#     TRIAL NÃO SOBRESCREVE POLICY.
#     TRIAL NÃO AUTORIZA GASTO.
#     TRIAL PASSADO != CAPACIDADE PROVADA.
NORMAL = 'NORMAL'
TRIAL = 'TRIAL'
MODOS = (NORMAL, TRIAL)

#: Os estados que um ensaio NÃO pode medir, e porquê.
#:
#: `BLOCKED` fica de fora, e a razão é um achado desta missão, não uma cautela.
#: A prova que escreve `BLOCKED` em `facebook.content` —
#: `docs/sintonia-scrap/AP-DISCOVERY-VS-CAPTURA-V1.md` — mediu UMA rota
#: (`gallery-dl` deslogado) a partir de UM host, e o próprio documento arruma
#: essa linha na tabela «o que só o runner local pode fechar». A matriz, ao
#: lado, declara `FACEBOOK/FETCH_POST` ALLOWED por duas OUTRAS rotas.
#:
#:     `BLOCKED` NA CAPACIDADE ESTÁ A DESCREVER UMA ROTA NUM AMBIENTE.
#:
#: Enquanto o estado disser duas coisas, deixá-lo entrar em ensaio seria ler o
#: estado misturado como se estivesse limpo. Fica registado como
#: `CAPABILITY_ROUTE_STATE_CONFLATION = YES` e NÃO foi corrigido aqui: separar
#: os eixos muda a declaração de cinco capacidades e é decisão de quem mede.
SEM_ENSAIO = ('BLOCKED',)


def CAPABILITIES(plataforma=None):
    """O que o SCRAP sabe fazer, com estado medido e ambiente declarado.

    `COL-LAW-014` pede capacidade declarada. Isto e a declaracao, e ela e
    honesta ate onde doi: quinze capacidades `PROVEN` e onze que nao prometem
    nada nenhuma.
    """
    reg.carregar_adaptadores()
    fonte = cap.da_plataforma(plataforma) if plataforma else cap.DECLARADAS
    saida = {}
    for nome, (plat, estado, alvo, porque, prova, grosso) in sorted(fonte.items()):
        r = reg.adaptador_de(plat, nome)
        saida[nome] = {
            'PLATFORM': plat,
            'CAPABILITY': nome,
            'CAPABILITY_STATE': estado,
            'EXECUTION_TARGET': alvo,
            'WHY_LOCAL': porque,
            'EVIDENCE': prova,
            'MATRIZ_CAPABILITY': grosso,
            'ADAPTER': r['ADAPTADOR'] if r else None,
            # ⚠️ ISTO DIZIA `bool(r and r['EXECUTA'])`, E MENTIA PARA ONZE DAS
            # CATORZE CAPACIDADES LIGADAS. Um adaptador cumpre o seu papel por
            # `executa=` OU por `rota=` — e quem sabe isso e `scrap_registo`,
            # que ja tem a funcao. Perguntar so por um dos dois papeis fazia a
            # introspecao da ferramenta dizer que o Telegram nao tem rota
            # enquanto o `CHECK`, na linha ao lado, dizia CAN_COLLECT_NOW.
            #
            #     DUAS RESPOSTAS PARA A MESMA PERGUNTA SAO DOIS DONOS.
            'HAS_ROUTE': reg.tem_caminho(plat, nome),
            'PROMISES_RESULT': cap.promete_resultado(nome),
            # ── OS TRES EIXOS, SEM EXECUTAR NADA ──────────────────────────
            # `PROMISES_RESULT` responde pelo eixo da CAPACIDADE.
            # `POLICY_DECISION` responde pelo eixo da POLITICA — e le, nao
            # decide: quem decide e `leis/social_matriz.py`.
            # `TRIAL_ELIGIBLE` responde pelo eixo do MODO.
            #
            # Nenhum dos tres abre ligacao, e por isso os tres cabem aqui.
            'POLICY_DECISION': (mz.decisao(plat, grosso)['DECISAO']
                                if grosso else None),
            'TRIAL_ELIGIBLE': (estado not in SEM_ENSAIO
                               and reg.tem_caminho(plat, nome)),
            'PRODUCTION_READY': (cap.promete_resultado(nome)
                                 and reg.tem_caminho(plat, nome)),
        }
    return saida


def CHECK(plataforma, capacidade, *, ambiente=None, modo=NORMAL):
    """Consigo chegar la agora, SEM GASTAR? → o veredicto, sempre.

    Nao faz nenhuma requisicao, nao abre nenhum modelo, nao chama nenhuma rota
    paga. Le o que esta declarado e o que esta registado, e responde.

    `modo=TRIAL` muda UMA coisa e mais nada: a pergunta deixa de ser «promete
    resultado?» e passa a ser «da para MEDIR?». Tudo o resto — declaracao,
    rota, ambiente, credencial — corre igual e pela mesma ordem.

        DUAS PERGUNTAS DIFERENTES NAO PODEM DAR A MESMA RESPOSTA.

    Por isso o veredicto passa a trazer os dois campos SEMPRE, nos dois modos:

        PRODUCTION_READY   da para colher a serio, com direito a esperar objeto
        TRIAL_ELIGIBLE     da para medir uma vez, sem direito a esperar nada

    Um `CAN = True` que nao diga qual dos dois e um `CAN = True` que mente para
    metade de quem o le.
    """
    if modo not in MODOS:
        raise ValueError('modo de execucao desconhecido: %r. Os dois sao %s'
                         % (modo, ', '.join(MODOS)))
    reg.carregar_adaptadores()
    plat = (plataforma or '').upper()
    alvo, porque = cap.onde(capacidade)
    estado_medido = cap.estado(capacidade)
    veredicto = {
        'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION,
        'PLATFORM': plat,
        'CAPABILITY': capacidade,
        'CAPABILITY_STATE': estado_medido,
        'EXECUTION_MODE': modo,
        'EXECUTION_TARGET': alvo,
        'WHY_LOCAL': porque,
        'EVIDENCE': cap.prova(capacidade),
        'COST_TO_CHECK_USD': 0.0,
        'CAN': False,
        'PRODUCTION_READY': False,
        'TRIAL_ELIGIBLE': False,
        'STATE': None,
        'WHY': None,
    }
    if not cap.existe(capacidade):
        veredicto['STATE'] = NAO_DECLARADA
        veredicto['WHY'] = ('capacidade nao declarada. Isto nao e uma falha: e '
                            'a resposta certa para o que ninguem mediu.')
        return veredicto
    # ── O PORTAO EPISTEMOLOGICO, E A UNICA LINHA QUE O MODO MUDA ───────────
    promete = cap.promete_resultado(capacidade)
    if not promete and modo == NORMAL:
        veredicto['STATE'] = SEM_PROMESSA
        veredicto['WHY'] = ('estado medido %s. Existir adaptador para ela nao a '
                            'transforma em sucesso.' % estado_medido)
        return veredicto
    if modo == TRIAL and estado_medido in SEM_ENSAIO:
        veredicto['STATE'] = ENSAIO_RECUSADO
        veredicto['WHY'] = ('estado medido %s. A prova que o escreveu mediu uma '
                            'ROTA num AMBIENTE, e enquanto o estado disser duas '
                            'coisas o ensaio nao o pode ler como se dissesse '
                            'uma.' % estado_medido)
        return veredicto
    r = reg.adaptador_de(plat, capacidade)
    if not reg.tem_caminho(plat, capacidade):
        veredicto['STATE'] = SEM_ROTA
        veredicto['WHY'] = ('declarada e sem rota ligada nesta linhagem. '
                            'Declarar sem executar e honesto; executar sem '
                            'declarar e que nao e.')
        veredicto['ADAPTER'] = r['ADAPTADOR'] if r else None
        return veredicto
    veredicto['ADAPTER'] = r['ADAPTADOR']
    veredicto['MATRIZ_CAPABILITY'] = cap.da_matriz(capacidade)
    if ambiente and alvo not in (ambiente, cap.EITHER):
        veredicto['STATE'] = AMBIENTE_ERRADO
        veredicto['WHY'] = ('esta capacidade corre em %s e foi pedida em %s%s'
                            % (alvo, ambiente, ' — %s' % porque if porque else ''))
        return veredicto
    # ── A SONDA GRATUITA ──────────────────────────────────────────────────
    # `CHECK` responde «consigo chegar la AGORA», e uma rota oficial sem
    # credencial no ambiente nao chega a lado nenhum. Ler uma variavel de
    # ambiente custa zero — e e exatamente por custar zero que esta pergunta
    # pertence ao CHECK e nao ao COLLECT.
    #
    #     DESCOBRIR QUE FALTA A CHAVE DEPOIS DE CHAMAR A API E DESCOBRIR
    #     TARDE. O `CHECK` existe para que `COL-LAW-018` — a rota mais barata
    #     capaz vem primeiro — seja decidivel ANTES de gastar.
    #
    # A sonda NUNCA devolve o valor do segredo. Devolve (bool, estado), e o
    # estado e escrito pelo adaptador, nunca derivado da credencial.
    sonda = reg.sonda_de(plat, capacidade)
    if sonda is not None:
        ok, porque_nao = sonda()
        if not ok:
            veredicto['STATE'] = porque_nao or 'CREDENTIAL_MISSING'
            veredicto['WHY'] = ('a rota existe e a configuracao dela nao esta completa neste ambiente')
            return veredicto
    veredicto['CAN'] = True
    veredicto['PRODUCTION_READY'] = promete
    veredicto['TRIAL_ELIGIBLE'] = True
    if promete:
        veredicto['STATE'] = PODE
        veredicto['WHY'] = ('declarada, com rota, configurada, e o estado medido '
                            'promete resultado')
    else:
        # Chegou aqui em TRIAL com um estado que nao promete. Dizer `PODE` seria
        # prometer o que a medicao nao prometeu.
        #
        #     TRIAL_ELIGIBLE != PRODUCTION_READY.
        veredicto['STATE'] = ELEGIVEL_PARA_ENSAIO
        veredicto['WHY'] = ('declarada, com rota, configurada — e o estado medido '
                            '%s NAO promete resultado. Da para MEDIR uma vez; nao '
                            'da para contar com ela.' % estado_medido)
    return veredicto


# ══════════════════════════════════════════════════════════════════════════
# A DURABILIDADE É DAQUI, E NÃO DE CADA ADAPTADOR
# ══════════════════════════════════════════════════════════════════════════
# A C10.6B provou o estado durável na cadeia de Reel — e provou-o LÁ: o
# adaptador do Instagram abria a RUN, ligava o checkpoint e passava o relator.
# A C10.6C mediu o que isso significava para as outras doze capacidades wired:
#
#     WIRED_CAPABILITIES = 13 · COM DURABILIDADE = 3 · SEM = 10
#
#     UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A.
#
# O ponto mais alto que conhece a execução REAL e não inventa semântica de
# plataforma é este. `COLLECT` é por onde toda capacidade passa: ele mede o
# `CHECK`, decide se há caminho, e despacha. O que ele NÃO sabe é o que cada
# plataforma faz lá dentro — e por isso não é ele que nomeia os degraus delas.
#
# O QUE ESTE FICHEIRO PASSA A FAZER, E SÓ ISSO
# ----------------------------------------------
#     abre a RUN            antes de qualquer trabalho, quando há banco
#     abre o CHECKPOINT     só quando o adaptador declara unidade de trabalho
#     escreve a etapa CHECK que ele PRÓPRIO atravessou — não a de ninguém
#     entrega o RELATOR     a quem souber usá-lo
#     fecha a RUN           com o estado que mediu
#
# O que ele nunca faz: nomear uma etapa que não correu aqui.
#
#     NÃO SE FABRICA ETAPA. QUEM NÃO ATRAVESSOU NÃO RELATA.
#
# Sem `banco`, tudo corre exactamente como antes. Um executor que só funcionasse
# com Postgres seria um executor novo.
def _aceita(fn, nome):
    """A função aceita este parâmetro? Medido na assinatura, nunca suposto."""
    import inspect
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return True
    return nome in sig.parameters


def _estado_da_corrida(objetos, trace, ck):
    """O status canônico desta execução, lido do que voltou.

    `vazia` não é `falhou`: uma busca que correu e não achou nada correu.
    A precedência é a da migration 001 — `falhou > vazia > parcial > concluida`.
    """
    import falhas as fx
    # ⚠️ O VEREDITO DA UNIDADE, QUANDO O ADAPTADOR O SABE DIZER, VENCE.
    # Um objeto ter voltado nao quer dizer que a unidade ficou feita — o Reel
    # pode trazer midia e nao trazer texto. Este ficheiro nao sabe ler
    # `TRANSCRIPT_STATE`, e adivinhar seria inventar semantica de plataforma.
    canonico = (trace or {}).get('CANONICAL_STATE')
    if canonico:
        if canonico not in fx.ESTADOS:
            raise ValueError('o adaptador devolveu um estado que `leis/falhas.py` '
                             'nao declara: %r' % canonico)
        if fx.e_falha(canonico):
            return ck.CORRIDA_PARCIAL if objetos else ck.CORRIDA_FALHOU
        if canonico in ('ZERO_RESULTS', 'NOT_APPLICABLE'):
            return ck.CORRIDA_VAZIA
        return ck.CORRIDA_CONCLUIDA if objetos else ck.CORRIDA_VAZIA
    estado = (trace or {}).get('RESULT') or (trace or {}).get('RESULTADO')
    if estado in ('OK', 'PROVED', None) or not estado:
        return ck.CORRIDA_CONCLUIDA if objetos else ck.CORRIDA_VAZIA
    if estado in fx.ESTADOS and not fx.e_falha(estado):
        return ck.CORRIDA_CONCLUIDA if objetos else ck.CORRIDA_VAZIA
    return ck.CORRIDA_PARCIAL if objetos else ck.CORRIDA_FALHOU


def COLLECT(*, platform, capability, run_id, scope='PONTUAL', banco=None,
            modo=NORMAL, **kwargs):
    """Vai buscar. → (objetos, trace). NUNCA levanta por rota recusada.

    Recusa e bloqueio sao RESULTADO DE MEDICAO, nao ausencia de resultado — e
    por isso descem como estado, com trace, e nao como excecao.

    `banco` liga a durabilidade comum: RUN prospectiva, checkpoint quando a
    capacidade tem unidade retomável, e rastro de etapa. Sem ele, nada muda.

    `modo=TRIAL` mede uma capacidade que ainda nao promete resultado. Ele muda
    o portao do `CHECK` e MAIS NADA: a politica, o roteador, o adaptador, o
    fornecedor, a autorizacao de gasto e a taxonomia de falha sao os mesmos
    objetos, chamados pelas mesmas linhas.

        A UNICA DIFERENCA ENTRE NORMAL E TRIAL E O PORTAO EPISTEMOLOGICO.

    E o que ele NAO faz e tao importante quanto: um ensaio que devolve objetos
    nao promove estado nenhum. Quem promove `NOT_EXECUTED` para `PROVEN` e
    gente, com prova citada, num commit que se le.
    """
    if scope not in ESCOPOS:
        raise ValueError('escopo fora de COL-LAW-016: %r. Os tres sao %s'
                         % (scope, ', '.join(ESCOPOS)))
    if modo not in MODOS:
        raise ValueError('modo de execucao desconhecido: %r. Os dois sao %s'
                         % (modo, ', '.join(MODOS)))
    plat = (platform or '').upper()
    registo = reg.adaptador_de(plat, capability)
    execucao = relator = None
    if banco is not None:
        import coleta_checkpoint as ck
        # ── A UNIDADE VEM DO ADAPTADOR, QUE E QUEM SABE O QUE ELA E ────────
        # Este ficheiro nao sabe o que e uma unidade de trabalho do Instagram
        # nem do YouTube. Perguntar e a unica forma de nao inventar.
        unidade = None
        decl = (registo or {}).get('UNIDADE')
        if decl is not None:
            unidade = decl(**kwargs)
        execucao, porque = ck.abrir_execucao(
            banco, run_id=run_id, platform=plat, actor=EXECUTOR_ID,
            actor_version=EXECUTOR_VERSION, unidade=unidade)
        if execucao is None:
            # O checkpoint recusou. NAO houve execucao — e dizer que houve, e
            # que ela falhou, seria inventar uma corrida que ninguem correu.
            trace = forn.Percurso(capability).selar(resultado=porque)
            trace.update({'EXECUTOR_ID': EXECUTOR_ID, 'RUN_ID': run_id,
                          'SCOPE': scope, 'CHECKPOINT_STATE': porque,
                          'RUN_STATE_PERSISTED': 'NOT_STARTED'})
            return [], trace
        relator = execucao.relator

    # ── A ETAPA `CHECK` E DESTE FICHEIRO, PORQUE E AQUI QUE ELA CORRE ──────
    linha = relator.abrir('CHECK') if relator is not None else None
    pronto = CHECK(platform, capability, modo=modo)
    if relator is not None:
        # ⚠️ UM PORTÃO QUE RECUSA NÃO FALHOU. ELE FEZ O SEU TRABALHO.
        # `FAIL` aqui diria que o próprio CHECK rebentou. O que aconteceu foi
        # outra coisa: ele correu, mediu, e a resposta foi «não dá». O
        # vocabulário já tem a palavra para isso — `SKIPPED` é «decidido não
        # correr, com razão escrita», e a razão vai escrita ao lado.
        #
        # E há uma prova disso no próprio schema: `falha_tem_codigo` exige
        # `diagnostic_code` em toda linha `FAIL`, e o registry de
        # `leis/diagnostico.py` não tem código para `CHECK`. Não tem porque
        # `CHECK` não falha — ele responde.
        relator.fechar(linha, 'PASS' if pronto['CAN'] else 'SKIPPED',
                       passed=1 if pronto['CAN'] else 0,
                       not_run=0 if pronto['CAN'] else 1,
                       output_grain='CAPABILITY', output_count=1,
                       cardinalidade='1:1',
                       canonical_state=(None if pronto['CAN']
                                        else _canonico(pronto['STATE'])),
                       error_message=None if pronto['CAN'] else pronto['STATE'])
    if not pronto['CAN']:
        percurso = forn.Percurso(capability)
        trace = percurso.selar(resultado=pronto['STATE'])
        trace.update({'EXECUTOR_ID': EXECUTOR_ID, 'RUN_ID': run_id,
                      'SCOPE': scope, 'CHECK': pronto,
                      'EXECUTION_MODE': modo,
                      'CAPABILITY_STATE_BEFORE': pronto['CAPABILITY_STATE'],
                      'CAPABILITY_STATE_AFTER': pronto['CAPABILITY_STATE']})
        if execucao is not None:
            import coleta_checkpoint as ck
            import falhas as fx
            # «NÃO TENHO CREDENCIAL» É FALHA. «ESTA ROTA NÃO É PERMITIDA» NÃO É:
            # é a política a funcionar, e uma corrida que a respeitou não falhou.
            canon = _canonico(pronto['STATE'])
            falhou = fx.e_falha(canon) if canon in fx.ESTADOS else True
            execucao.falhar_checkpoint('CHECK/%s' % pronto['STATE'])
            execucao.fechar(ck.CORRIDA_FALHOU if falhou else ck.CORRIDA_VAZIA,
                            error='CHECK: %s' % pronto['STATE'])
            trace['RUN_STATE_PERSISTED'] = 'YES'
            trace['RUN_STATUS'] = (ck.CORRIDA_FALHOU if falhou
                                   else ck.CORRIDA_VAZIA)
        return [], trace
    executa = reg.executor_de(plat, capability)
    if relator is not None:
        # O relator so desce para quem o saiba receber. Enfia-lo num chamador
        # que nao o declara seria `TypeError` — e um executor que so funciona
        # com implementacoes instrumentadas ja nao e o executor de todas.
        alvo = executa or _rota_para(plat, capability)
        if alvo is not None and _aceita(alvo, 'etapa'):
            kwargs = dict(kwargs, etapa=relator)
    try:
        objetos, trace = _despachar(plat, capability, run_id, executa, kwargs)
    except Exception as e:                                        # noqa: BLE001
        if execucao is not None:
            import coleta_checkpoint as ck
            for l_, nome_, _t in list(relator.abertas):
                relator.fechar(l_, 'FAIL', canonical_state='UNKNOWN_ERROR',
                               error_class=type(e).__name__, error_message=str(e))
            execucao.falhar_checkpoint('%s: %s' % (type(e).__name__, e))
            execucao.fechar(ck.CORRIDA_FALHOU, error='%s: %s' % (type(e).__name__, e))
        raise
    # ── O MODO SOBE SEMPRE, NOS DOIS MODOS ────────────────────────────────
    # Um trace que so nomeia o modo quando ele e TRIAL obriga quem le a deduzir
    # o NORMAL pela ausencia — e ausencia nao e valor.
    #
    #     CAMPO AUSENTE != NORMAL. CAMPO AUSENTE != ZERO.
    #
    # `CAPABILITY_STATE_AFTER` e igual ao BEFORE por construcao: este ficheiro
    # nao escreve em `scrap_capacidades.py`, e a igualdade e a prova disso a
    # viajar dentro do proprio artefato.
    #
    #     TRIAL PASSADO != CAPACIDADE PROVADA.
    trace.update({'EXECUTOR_ID': EXECUTOR_ID, 'EXECUTOR_VERSION': EXECUTOR_VERSION,
                  'RUN_ID': run_id, 'SCOPE': scope, 'CHECK': pronto,
                  'EXECUTION_MODE': modo,
                  'CAPABILITY_STATE_BEFORE': pronto['CAPABILITY_STATE'],
                  'CAPABILITY_STATE_AFTER': cap.estado(capability)})
    forn.conferir(trace)
    if execucao is not None:
        import coleta_checkpoint as ck
        estado = _estado_da_corrida(objetos, trace, ck)
        # ── PERSIST FIRST, THEN ADVANCE CHECKPOINT ──────────────────────────
        if estado in (ck.CORRIDA_CONCLUIDA, ck.CORRIDA_VAZIA):
            trace['CHECKPOINT_ADVANCE'] = execucao.avancar(
                itens=len(objetos or []), unidade=str(kwargs.get('ident')
                                                      or capability))
        else:
            execucao.falhar_checkpoint(str(trace.get('RESULT') or estado))
        execucao.fechar(estado, item_count_raw=len(objetos or []))
        trace.update({'RUN_STATE_PERSISTED': 'YES',
                      'CHECKPOINT_ID': execucao.checkpoint_id,
                      'RUN_STATUS': estado})
    return objetos, trace


def _canonico(estado):
    """O estado do `CHECK` na língua de `leis/falhas.py`, ou None.

    Nem todo estado de prontidão é uma falha canônica — e traduzir à força
    poria um nome que o dono nunca declarou dentro do rastro.
    """
    import falhas as fx
    return estado if estado in fx.ESTADOS else 'ROUTE_UNAVAILABLE'


def _rota_para(plat, capability):
    r = reg.adaptador_de(plat, capability)
    return (r or {}).get('ROTA')


def _despachar(plat, capability, run_id, executa, kwargs):
    if executa is not None:
        # Capacidade que a matriz de rotas nao conhece — a cadeia de Reel e a
        # unica hoje. Ela monta o proprio trace porque nao ha porta a medir.
        return executa(run_id=run_id, **kwargs)
    if True:
        # O CAMINHO CANONICO. Passa pelo roteador, e o roteador mede o portao
        # do `robots`, a trava da sessao e a trava do gasto ANTES de chamar
        # qualquer coisa. Saltar isto para «ir direto a API» seria mais curto
        # e seria uma segunda porta — e a segunda porta e sempre a que ninguem
        # mede.
        import social_rotas as sr
        grossa = cap.da_matriz(capability)
        objetos, registo = sr.executar(platform=plat, capability=grossa,
                                       run_id=run_id, **kwargs)
        return objetos, forn.do_registo(capability, registo)


def STATE(plataforma=None):
    """Onde parei. O cursor e SEMPRE interno — `COL-LAW-016`.

    O orquestrador conhece `PONTUAL`, `INCREMENTAL` e `TOTAL`, e mais nada. Que
    o cursor do LinkedIn seja um `urn:li:activity:` e o do YouTube um
    `page token` e assunto desta casa.
    """
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'SCOPES_KNOWN_BY_ORCHESTRATOR': ESCOPOS,
        'CURSOR_SEMANTICS_ARE_INTERNAL': True,
        'CHECKPOINT_BACKEND': 'coleta/coleta_checkpoint.py',
        'CURSORS': 'NOT_IMPLEMENTED',
        'WHY': ('C1 desenha o contrato e nao liga o checkpoint por capacidade. '
                'Ligar sem ter rota para a maioria delas seria guardar a '
                'posicao de uma corrida que nunca aconteceu.'),
    }


def OUTPUT():
    """Onde larguei, e em que forma."""
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'LARGA_EM': LARGA_EM,
        'ARTIFACT_CONTRACT': 'leis/artefato.py',
        'RAW_IS_NOT_DERIVED': ('RAW != DERIVED != STRUCTURED != ADMISSION != READY. '
                               'O SCRAP entrega RAW e derivados com pai declarado; '
                               'nao admite e nao julga.'),
        'TEXT_KINDS': ('CAPTION', 'TRANSCRIPT'),
        'TRANSLATION': 'NOT_RUN',
        'TRANSLATION_WHY': ('a casa tem a lei da traducao escrita e conferida e '
                            'nao tem motor nenhum. Ausente fica NOT_RUN — nunca '
                            'uma copia do original a fingir de traducao.'),
    }


def TRACE(trace):
    """O que aconteceu, com fornecedor, troca, motivo e custo.

    Nao inventa campo: confere o que ja veio e recusa a historia incompleta.
    """
    forn.conferir(trace)
    return {
        'EXECUTOR_ID': EXECUTOR_ID,
        'EXECUTOR_VERSION': EXECUTOR_VERSION,
        'RUN_ID': trace.get('RUN_ID'),
        'CAPABILITY': trace.get('CAPABILITY'),
        'PROVIDER_REQUESTED': trace.get('PROVIDER_REQUESTED'),
        'PROVIDER_USED': trace.get('PROVIDER_USED'),
        'WHY_FALLBACK': trace.get('WHY_FALLBACK'),
        'RESULT': trace.get('RESULT'),
        'PROVIDER_STEPS': trace.get('PROVIDER_STEPS'),
        'PAID_PROVIDER_USED': trace.get('PAID_PROVIDER_USED', False),
        'EXECUTION_TARGET': (trace.get('CHECK') or {}).get('EXECUTION_TARGET'),
        'WHY_LOCAL': (trace.get('CHECK') or {}).get('WHY_LOCAL'),
    }
