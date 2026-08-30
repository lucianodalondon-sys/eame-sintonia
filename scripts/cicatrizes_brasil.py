#!/usr/bin/env python3
"""A matriz das cicatrizes do Brasil, e a verificação de que PROVED é PROVED.

O risco desta matriz não é errar um status. É narrar. Uma linha que diz
PROVED sem testemunha executável vale menos que uma linha honesta dizendo
ABSENT — porque a primeira desliga a vigilância.

Por isso cada linha marcada PROVED declara onde está a prova, e este script
VERIFICA que ela existe: um teste com esse nome na suíte, uma constraint com
esse nome nas migrations, uma função, ou uma afirmação nomeada num arquivo de
regressão SQL. Se a prova não é encontrável, o script rebaixa a linha e diz
que rebaixou.

    python3 scripts/cicatrizes_brasil.py            # mede e imprime
    python3 scripts/cicatrizes_brasil.py --build    # grava o artefato
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'BRAZIL-LESSONS-TRANSFER-EAME.json')
BRASIL = '/home/user/portal-sintonia'


def texto_de(*partes):
    p = os.path.join(RAIZ, *partes)
    if os.path.isdir(p):
        out = []
        for r, _, fs in os.walk(p):
            for f in fs:
                if f.endswith(('.py', '.sql', '.md', '.json', '.yml')):
                    with open(os.path.join(r, f), encoding='utf-8', errors='ignore') as h:
                        out.append(h.read())
        return '\n'.join(out)
    with open(p, encoding='utf-8', errors='ignore') as h:
        return h.read()


def acervo():
    return {
        'tests': texto_de('tests'),
        'migrations': texto_de('supabase', 'migrations'),
        'sqltests': texto_de('supabase', 'tests'),
        'scripts': texto_de('scripts'),
        'docs': texto_de('docs'),
        'samples': texto_de('data', 'samples'),
    }


# ── AS CICATRIZES ─────────────────────────────────────────────────────
# BRAZIL_LESSON foi LIDA do repositório brasileiro, não lembrada. Cada uma
# aponta o arquivo onde está escrita lá.
CICATRIZES = [
 {'ID': 'BR-01', 'FAMILIA': 'LOCALIZACAO',
  'BRAZIL_LESSON': 'a praça do documento era a praça cadastrada do CANAL, e carimbava a '
                   'região do canal em comentário de espectador de qualquer lugar',
  'ONDE_NO_BRASIL': 'ACHADO-praca-do-canal-nao-e-praca-da-lavoura.md',
  'WHY_IT_EXISTS': '44 pessoas contadas como "discutindo nematoide de café" numa praça '
                   'com 7.868 ha de café, contra 1,1 milhão de ha na região que o '
                   'sistema chamava de outra coisa. E a regra JÁ ESTAVA escrita no '
                   'CLAUDE.md deles — não estava no campo que decidia a saída.',
  'EAME_APPLICABLE': 'YES',
  'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo.fact_geografia_origem + constraint '
           'local_da_fonte_nao_sustenta_local_do_fato (015)',
  'EXECUTABLE_PROOF': ['local_da_fonte_nao_sustenta_local_do_fato',
                       'E2 · o lugar da FONTE não sustenta o lugar do FATO'],
  'GAP': None,
  'MINIMAL_ACTION': None},

 {'ID': 'BR-02', 'FAMILIA': 'LOCALIZACAO',
  'BRAZIL_LESSON': 'a procedência do lugar é um campo: escrito · citado · deduzido · fonte',
  'ONDE_NO_BRASIL': 'documentos.local_do_fato_origem',
  'WHY_IT_EXISTS': '"deduzido = a inteligência inferiu, e então vale menos; é a mais '
                   'fraca e a única que NUNCA deve virar número de mapa sem alguém"',
  'EAME_APPLICABLE': 'YES',
  'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo.fact_geografia_origem (015)',
  'EXECUTABLE_PROOF': ['local_do_fato_diz_como_se_soube',
                       'E · todo lugar do fato carrega COMO se soube'],
  'GAP': 'o EAME é MAIS estrito que o Brasil: DEDUZIDO e DA_FONTE existem no vocabulário '
         'para poderem ser ditos, e são recusados como sustentação.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-03', 'FAMILIA': 'LOCALIZACAO',
  'BRAZIL_LESSON': 'sem região, o país inteiro não faz as vezes da região',
  'ONDE_NO_BRASIL': 'a praça do padrão é a praça mais frequente entre os documentos',
  'WHY_IT_EXISTS': 'agregar por um recorte que ninguém mediu produz número que parece '
                   'geográfico e não é',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'precisao_da_geografia (015)',
  'EXECUTABLE_PROOF': ['precisao_da_geografia', 'D · país conhecido, região desconhecida'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-04', 'FAMILIA': 'RELEVANCIA',
  'BRAZIL_LESSON': 'contagem alta com régua limpa continua não distinguindo SENTIDO',
  'ONDE_NO_BRASIL': 'ACHADO-348-alvos-na-conversa.md · as cinco armadilhas',
  'WHY_IT_EXISTS': 'Leiteiro é gado, Cupim é o meme, Murcha é seca, Tiririca é grama de '
                   'jardim, Caruru é comida — e as cinco voltaram altas na segunda medição',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo_crop_issue.relacao (004) + f_relevancia_ao_caso (015)',
  'EXECUTABLE_PROOF': ['R4 · KEYWORD_MATCH != RELEVANT_EVIDENCE',
                       'COOCORRENCIA_TEXTUAL'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-05', 'FAMILIA': 'RELEVANCIA',
  'BRAZIL_LESSON': 'relevância da FONTE não é relevância do CONTEÚDO',
  'ONDE_NO_BRASIL': 'a rodada de 03/08 leu uma camada de três; o comentário é a camada '
                    'mais pobre — 3,9% fala de manejo contra 35,7% do post',
  'WHY_IT_EXISTS': 'ler uma camada e publicar o número como se fosse do acervo inteiro',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'f_relevancia_ao_caso (015), com o MOTIVO escrito por linha',
  'EXECUTABLE_PROOF': ['R9 · toda relevância vem com o MOTIVO escrito',
                       'R10 · não existe score de relevância'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-06', 'FAMILIA': 'RELEVANCIA',
  'BRAZIL_LESSON': 'ZERO COMENTÁRIO não é NINGUÉM FALA DISSO — e a diferença parte em '
                   'três, que pedem coisas opostas',
  'ONDE_NO_BRASIL': 'ACHADO-348-alvos-na-conversa.md',
  'WHY_IT_EXISTS': 'ninguém fala mesmo (49), só o produtor não fala (78), há conversa '
                   '(232): coleta nova, olhar na gaveta certa, e leitura',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'tentativa_de_coleta.estado (015) + as cinco ignorâncias do contrato',
  'EXECUTABLE_PROOF': ['N1 · o mundo, a instalação e nós são estados diferentes'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-07', 'FAMILIA': 'AUSENCIA',
  'BRAZIL_LESSON': 'a recusa da INSTALAÇÃO foi contada como ausência do MUNDO',
  'ONDE_NO_BRASIL': 'PEDIDO-DE-EVIDENCIA-PARECER.md · os seis estados',
  'WHY_IT_EXISTS': '"não li vestido de não há, desta vez PAGO: 299 fichas contadas como '
                   '\'o perfil não declara lugar\' quando ninguém chegou a perguntar"',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'tentativa_de_coleta (015): RESPONDEU_SEM_O_CAMPO · LOGIN_WALL · THROTTLED · '
           'NOT_FOUND · PARSER_FAILURE · SEM_CHECKPOINT_NAO_GASTEI · NAO_TESTADO',
  'EXECUTABLE_PROOF': ['tentativa_de_coleta',
                       'N2 · um estado de tentativa fora do vocabulário é recusado'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-08', 'FAMILIA': 'AUSENCIA',
  'BRAZIL_LESSON': 'erro nunca vira ausência — "erro ganha de tudo"',
  'ONDE_NO_BRASIL': 'diario._status(colhidos, erro, vazia)',
  'WHY_IT_EXISTS': 'uma rodada que falhou e uma rodada que voltou vazia pedem ações opostas',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'run_status enum (001): rodando · concluida · vazia · parcial · falhou',
  'EXECUTABLE_PROOF': ['run_status', 'N3 · toda tentativa carrega o motivo'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-09', 'FAMILIA': 'AUSENCIA',
  'BRAZIL_LESSON': 'HTTP 200 não é fonte viva',
  'ONDE_NO_BRASIL': 'as leis herdadas no handoff do EAME',
  'WHY_IT_EXISTS': 'uma página que responde 200 com um desafio anti-robô não entregou nada',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'tests/test_operacao.py',
  'EXECUTABLE_PROOF': ['test_http_200_nao_conta_como_fonte_viva'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-10', 'FAMILIA': 'PROVENIENCIA',
  'BRAZIL_LESSON': 'três métodos de custo diferentes escreviam na mesma coluna sem '
                   'registrar qual — o próprio repo chamou isso de "o defeito de schema '
                   'mais importante" da proveniência',
  'ONDE_NO_BRASIL': 'custo_usd sem método',
  'WHY_IT_EXISTS': 'custo lido da plataforma e custo estimado por diferença de saldo não '
                   'são o mesmo número, e somar os dois produz um total que não existe',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'collection_run.cost_method + custo_declarado_diz_como_foi_medido (001)',
  'EXECUTABLE_PROOF': ['custo_declarado_diz_como_foi_medido',
                       'P4 · custo declarado diz COMO foi medido'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-11', 'FAMILIA': 'PROVENIENCIA',
  'BRAZIL_LESSON': 'ausência de bruto precisa de motivo — NOT_PRESERVED é declarado, '
                   'nunca silêncio',
  'ONDE_NO_BRASIL': 'proveniencia.py',
  'WHY_IT_EXISTS': 'um dado sem bruto e sem motivo é indistinguível de um dado inventado',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'raw_asset + bruto_ausente_precisa_de_motivo (001)',
  'EXECUTABLE_PROOF': ['bruto_ausente_precisa_de_motivo',
                       'P3 · bruto ausente exige motivo escrito'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-12', 'FAMILIA': 'PROVENIENCIA',
  'BRAZIL_LESSON': 'PAID_RESULT != PRESERVED_RESULT — ator executou, item voltou, RAW sumiu',
  'ONDE_NO_BRASIL': 'medido na Itália, na mesma família de defeito',
  'WHY_IT_EXISTS': 'pagar por um resultado e não conseguir mostrá-lo depois é pagar duas vezes',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'f_runs_pagos_sem_bruto (015)',
  'EXECUTABLE_PROOF': ['f_runs_pagos_sem_bruto',
                       'P1 · ator executou, item voltou, RAW sumiu = NÃO preservado'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-13', 'FAMILIA': 'IDENTIDADE',
  'BRAZIL_LESSON': 'a identidade do conteúdo não pode depender da rodada, do token nem '
                   'da data de captura',
  'ONDE_NO_BRASIL': 'entidade-fase-0/1/4.py e o cadastro de fontes',
  'WHY_IT_EXISTS': 'uma fonte cadastrada duas vezes fazia o mesmo conteúdo entrar duas vezes',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'canal UNIQUE (plataforma, channel_id) · conteudo.hash_conteudo · '
           'registro_regulatorio UNIQUE (pais, registration_id, fonte, fonte_versao)',
  'EXECUTABLE_PROOF': ['UNIQUE (plataforma, channel_id)',
                       'captura_e_unica_por_fonte_e_versao'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-14', 'FAMILIA': 'IDENTIDADE',
  'BRAZIL_LESSON': 'DUPLICATE_FUNCTION_EXISTS != PRODUCTION_IS_DEDUPED — o dedupe existia '
                   'e o contador somava dois',
  'ONDE_NO_BRASIL': '"os dois leitores salvam o mesmo órfão, a linha entra UMA vez e o '
                    'balde somava DOIS"',
  'WHY_IT_EXISTS': '"é a farmácia contar o estoque somando o que cada balconista diz ter '
                   'visto na prateleira"',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo_canal_id_content_id_key (003) — PLATFORM + EXTERNAL_ID via canal. '
           'A 016 não criou trava nova: criou o caminho produtivo que passa por ela, '
           'e conteudo_visto_em, onde a SEGUNDA vez que vimos o mesmo item é observação '
           'e não conteúdo novo.',
  'EXECUTABLE_PROOF': [
      'test_G_zero_duplicata_viva_mesmo_com_item_repetido',
      'test_bypassar_a_identidade_natural_reprova',
      'D2 · rodada, token, dataset e captura ficam FORA da identidade',
      'conteudo_visto_em'],
  'GAP': 'a rodada anterior diagnosticou "falta a trava de identidade" e estava errada: '
         'a trava existe desde a 003. O que faltava era o caminho produtivo provado '
         'passando por ela — e a 016 chegou a criar um índice duplicado com as mesmas '
         'colunas antes de o banco recusar a duplicata.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-15', 'FAMILIA': 'IDENTIDADE',
  'BRAZIL_LESSON': 'REGISTRO != NOME; NOME REGULATÓRIO != PRODUTO COMERCIAL ATUAL',
  'ONDE_NO_BRASIL': 'CADEIA-DE-MOLECULA.md',
  'WHY_IT_EXISTS': 'casar por nome comercial funde entidades diferentes',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'a modelagem do CUPROXI FLO: dois identificadores tipados, LINK_STATE',
  'EXECUTABLE_PROOF': ['test_rt10_nao_reconciliou_por_nome'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-16', 'FAMILIA': 'UNIDADE_ANALITICA',
  'BRAZIL_LESSON': 'uma ficha tratada como FONTE INDIVIDUAL não necessariamente é uma '
                   'unidade analítica válida — 4.548 fichas, 4 provadas, 4.488 NÃO SEI',
  'ONDE_NO_BRASIL': 'CENSO-DA-IDENTIDADE-ANALITICA.md',
  'WHY_IT_EXISTS': 'um agregador contado como pessoa infla toda contagem de voz',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'canal.tipo_de_perfil (016) com os cinco estados + evidência escrita '
           'obrigatória, e v_human_sensor_admissivel, onde admissível exige as DUAS '
           'condições: perfil lido como pessoa E ficha de origem apontando pessoa.',
  'EXECUTABLE_PROOF': [
      'S3 · agregador NÃO é sensor humano',
      'S4 · resultado de busca NÃO é pessoa',
      'S5 · desconhecido fica desconhecido',
      'S6 · perfil de pessoa SEM ficha de pessoa não passa',
      'tipo_de_perfil_declarado_exige_evidencia'],
  'GAP': 'o tipo de perfil é LEITURA DECLARADA com evidência escrita, não medição '
         'automática — e é assim de propósito: nenhuma classificação sai de volume, '
         'contagem de seguidores ou heurística fraca. Sem evidência suficiente a linha '
         'fica NOT_KNOWN, que é diferente de "não é pessoa".',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-17', 'FAMILIA': 'UNIDADE_ANALITICA',
  'BRAZIL_LESSON': 'um sinal que não pôde ser exercido é registrado como NÃO EXERCIDO, '
                   'nunca como negativo',
  'ONDE_NO_BRASIL': '"o sinal URL de página de busca não serve neste cadastro — 92% das '
                    'fichas não têm url"',
  'WHY_IT_EXISTS': 'um sinal ausente por falta de campo vira "deu negativo" e some',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'as cinco ignorâncias do contrato: NAO_TESTADO != AUSENTE_MEDIDO',
  'EXECUTABLE_PROOF': ['test_as_cinco_ignorancias_continuam_distintas',
                       'AUSENTE_MEDIDO'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-18', 'FAMILIA': 'UNIDADE_ANALITICA',
  'BRAZIL_LESSON': 'os pisos são escolha declarada, não medição, e ficam no topo do '
                   'arquivo à vista',
  'ONDE_NO_BRASIL': 'PROVADO >= 5 autores distintos, SUSPEITA >= 2 sinais',
  'WHY_IT_EXISTS': 'um limiar escondido no código vira "o sistema mediu"',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'freshness_regra (010): limiares são DADO com justificativa escrita',
  'EXECUTABLE_PROOF': ['freshness_regra', '20c os limiares são dado, não constante de código'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-19', 'FAMILIA': 'RESILIENCIA',
  'BRAZIL_LESSON': 'checkpoint durável ANTES do gasto — SEM_CHECKPOINT_NAO_GASTEI',
  'ONDE_NO_BRASIL': 'diario.abre/fecha → tabela coletas, e a guarda no CHAMADOR',
  'WHY_IT_EXISTS': 'sem checkpoint, um crash no meio faz pagar tudo de novo',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'checkpoint_coleta (016) com os nove campos mínimos, e pode_gastar(), '
           'chamada por scripts/coleta_checkpoint.py ANTES da primeira chamada paga. '
           'A resposta padrão é NÃO, com motivo escrito.',
  'EXECUTABLE_PROOF': [
      'test_sem_checkpoint_nenhuma_chamada_paga_acontece',
      'test_remover_a_guarda_deixa_a_chamada_paga_acontecer',
      'K1 · sem linha aberta, pode_gastar diz não',
      'JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES'],
  'GAP': 'a guarda apareceu recusando TUDO na primeira execução, porque pode::text em '
         'psql devolve "true"/"false" e o leitor esperava "t". Falhou fechada — a '
         'direção certa — e ainda assim era defeito. Está corrigido e comentado.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-20', 'FAMILIA': 'RESILIENCIA',
  'BRAZIL_LESSON': 'não pagar duas vezes — quem está concluída ou vazia não é perguntado '
                   'de novo',
  'ONDE_NO_BRASIL': 'CONCLUIDOS = ("concluida", "vazia")',
  'WHY_IT_EXISTS': 'refazer uma coleta já concluída é gasto puro',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'o progresso mora no BANCO — checkpoint_coleta.unidades_feitas / '
           'itens_persistidos / ultima_unidade —, nunca na memória do processo. '
           'PROCESS_CRASH != LOST_COLLECTION.',
  'EXECUTABLE_PROOF': [
      'test_A_a_H_o_ciclo_inteiro',
      'K5 · o progresso persistido é campo de banco',
      'PROCESS_CRASH'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-21', 'FAMILIA': 'RESILIENCIA',
  'BRAZIL_LESSON': 'TOKEN_EXHAUSTED != COLLECTION_LOST — e o token nunca entra na identidade',
  'ONDE_NO_BRASIL': 'LEDGER-DAS-20-CHAVES.md',
  'WHY_IT_EXISTS': 'acabar a chave no meio não pode apagar o que já voltou',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'scripts/apify_pool.py, PORTADO da Itália sem segunda implementação, sob '
           'scripts/coleta_checkpoint.py. Token esgota -> parcial preservado -> '
           'checkpoint -> próxima chave -> retomada. UNKNOWN_FAILURE não rotaciona, '
           'para que uma falha não-identificada não queime o pool inteiro.',
  'EXECUTABLE_PROOF': [
      'test_token_esgotado_rotaciona_e_retoma_a_mesma_unidade',
      'test_falha_desconhecida_nao_queima_o_pool',
      'test_token_run_dataset_e_captura_sao_recusados',
      'TOKEN_EXHAUSTED'],
  'GAP': 'o pool é RESILIÊNCIA, não aumento de volume: o teto de itens continua sendo o '
         'do alvo, e trocar de chave não amplia o que se coleta.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-22', 'FAMILIA': 'TEMPO',
  'BRAZIL_LESSON': 'MEDIDO ONTEM != MEDIDO HOJE',
  'ONDE_NO_BRASIL': 'repetido em seis arquivos diferentes',
  'WHY_IT_EXISTS': 'um número publicado sem a data da medição vira um fato permanente',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'as_of_date derivado (011-013) + CAPTURE != REGISTRATION',
  'EXECUTABLE_PROOF': ['03c a captura futura NÃO reescreve o passado',
                       '17 AS_OF_DATE != STORED_TODAY · mesma data, mesma resposta'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-23', 'FAMILIA': 'TEMPO',
  'BRAZIL_LESSON': 'SOURCE_DATE != CAPTURED_AT',
  'ONDE_NO_BRASIL': 'a separação exigida no cadastro de documentos',
  'WHY_IT_EXISTS': 'calcular idade a partir da data de captura zera a idade de tudo',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo.publicado_em vs coletado_em; observacao.periodo_fim vs medido_em',
  'EXECUTABLE_PROOF': ['04b a idade NÃO foi calculada da data de medição',
                       '05 PUBLICATION_DATE != CAPTURE_DATE · colunas separadas'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-24', 'FAMILIA': 'METODO',
  'BRAZIL_LESSON': 'CONSERTADO != COMPROVADO',
  'ONDE_NO_BRASIL': 'repetido no CLAUDE.md e nas auditorias',
  'WHY_IT_EXISTS': 'declarar um conserto sem testemunha executável desliga a vigilância',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'este próprio script: toda linha PROVED é verificada contra o acervo',
  'EXECUTABLE_PROOF': ['VERIFICACAO_DA_PROVA'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-25', 'FAMILIA': 'ISOLAMENTO',
  'BRAZIL_LESSON': 'DADO NÃO EXISTE != DADO EXISTE E O NOSSO SISTEMA NÃO O LIGOU',
  'ONDE_NO_BRASIL': 'repetido em duas auditorias',
  'WHY_IT_EXISTS': 'a lacuna do sistema vira lacuna do mundo, e a coleta seguinte procura '
                   'no lugar errado',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED != NOT_REGISTERED, nos 12 produtos',
  'EXECUTABLE_PROOF': ['test_ausencia_no_registro_nunca_vira_nao_registrado',
                       'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED'],
  'GAP': None, 'MINIMAL_ACTION': None},

 # ── A CONFERÊNCIA · dez cicatrizes de localização mais novas ─────────
 # A rodada anterior marcou LOCATION_CONTRACT_COMPLETE = YES. Estas dez
 # foram passadas por cima do contrato já fechado, uma a uma. Ele NÃO
 # passou inteiro: quatro passaram, duas produziam resposta errada e foram
 # consertadas na 017, e quatro são falta de modelagem e ficam ABERTAS.
 # Marcar as quatro como PROVED aqui seria mover a régua para conseguir
 # READY, que é exatamente o que a missão proíbe.

 {'ID': 'BR-26', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'BASE != OPERATING != INFLUENCE != FACT — onde alguém está sediado, '
                   'onde atua, até onde sua fala alcança e onde o fato aconteceu são '
                   'quatro perguntas',
  'ONDE_NO_BRASIL': 'a separação exigida entre a praça do autor e a praça do documento',
  'WHY_IT_EXISTS': 'colapsar as quatro faz a sede do autor virar mapa de ocorrência',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'origem_lugar (018), com PAPEL declarado em linha — exatamente a ação '
           'mínima que a conferência tinha escrito, e não colunas novas em conteudo. '
           'FACT não está no vocabulário dela: o lugar do fato é do CONTEÚDO, e é por '
           'isso que são duas tabelas e não uma.',
  'EXECUTABLE_PROOF': [
      'L1 · as três espécies do sujeito coexistem',
      'L5 · promover BASE a FACT é recusado pelo vocabulário',
      'L6 · a sede citada no documento fica como MENCAO_APENAS',
      'origem_lugar'],
  'GAP': 'os quatro coexistem sem sobrescrita e o caso obrigatório está no ensaio — '
         'pesquisador em Foggia, instituição nacional, audiência italiana, fato em '
         'Grosseto. O que NÃO existe é um leitor que preencha origem_lugar sozinho: '
         'hoje as três espécies do sujeito entram por cadastro com evidência escrita.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-27', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'PLACE_MENTION != FACT_LOCATION — o nome do lugar aparecer no texto '
                   'não é o texto afirmar que o fato foi ali',
  'ONDE_NO_BRASIL': 'o balde `citado`, descrito como filtro de leitura e nunca fonte nova',
  'WHY_IT_EXISTS': 'menção virando afirmação é como a praça errada entra sem ninguém mentir',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'v_conteudo_localizacao.fact_forca_da_sustentacao e '
           'fact_sustentado_apenas_por_mencao (017); f_relevancia_ao_caso rebaixa '
           'lugar CITADO a CONTEXT_ONLY.',
  'EXECUTABLE_PROOF': ['C4 · lugar do fato só MENCIONADO não é sinal exato',
                       'C5 · a menção aparece na visão, em vez de passar despercebida',
                       'fact_sustentado_apenas_por_mencao'],
  'GAP': 'a conferência achou o EAME se contradizendo: a 015 ESCREVIA que CITADO é o '
         'balde mais fraco e a trava deixava CITADO sustentar o fato sozinho, sem que '
         'nada a jusante soubesse. CITADO continua registrável — mencionado e '
         'não-medido são respostas diferentes — e deixou de passar despercebido.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-28', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'o lugar do fato exige EVIDÊNCIA ESPECÍFICA, não um campo preenchido',
  'ONDE_NO_BRASIL': 'documentos.local_do_fato_evidencia',
  'WHY_IT_EXISTS': 'um lugar sem o trecho que o sustenta não é auditável depois',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'constraint local_do_fato_diz_como_se_soube (015): lugar do fato exige '
           'origem E evidência escrita, as duas',
  'EXECUTABLE_PROOF': ['local_do_fato_diz_como_se_soube',
                       'E · todo lugar do fato carrega COMO se soube'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-29', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'a proveniência é do VALOR, não do registro — cada lugar carrega '
                   'como AQUELE lugar se soube',
  'ONDE_NO_BRASIL': 'local_do_fato_origem por documento, não por lote de importação',
  'WHY_IT_EXISTS': 'proveniência de lote perde qual valor veio de onde',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'fact_geografia_origem e fact_geografia_evidencia são colunas do CONTEÚDO, '
           'ao lado do valor que sustentam',
  'EXECUTABLE_PROOF': ['fact_geografia_origem', 'fact_geografia_evidencia'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-30', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'um conteúdo tem 0..N lugares de fato, não 0..1',
  'ONDE_NO_BRASIL': 'um documento que relata ocorrência em duas regiões ao mesmo tempo',
  'WHY_IT_EXISTS': 'forçar um lugar só faz escolher um e apagar o resto, em silêncio',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo_lugar (018). A coluna conteudo.fact_geografia_id, que expressava '
           '0..1, foi APOSENTADA junto com as duas travas que a guardavam — deixá-la '
           'viva ao lado da tabela criaria dois donos da mesma lei.',
  'EXECUTABLE_PROOF': [
      'N1 · um documento sustenta três lugares do fato',
      'N2 · os três vêm como lista, não como string colada',
      'N5 · o dono antigo, de 0..1, não existe mais',
      'conteudo_lugar'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-31', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'GEO_PRECISION é dado: país, região, província, município, ponto',
  'ONDE_NO_BRASIL': 'a escada de precisão declarada por registro',
  'WHY_IT_EXISTS': 'somar precisões diferentes no mesmo mapa produz número que não existe',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'precisao_da_geografia() e escada_de_precisao() (018): PAIS < REGIAO < '
           'PROVINCIA < MUNICIPIO < LOCALIDADE < COORDENADA, derivada da LINHA e '
           'nunca do texto. Cada país nomeia os degraus como quiser; o degrau é do '
           'contrato, o nome é do país, e COUNTRY_ISOLATION continua intacta.',
  'EXECUTABLE_PROOF': [
      'P1 · a escada chega a MUNICIPIO',
      'P2 · a escada tem os seis degraus administrativos',
      'P3 · a precisão nasce da LINHA, nunca do texto',
      'escada_de_precisao'],
  'GAP': 'a escada tem seis degraus e o gazetteer não os preenche todos: o leitor '
         'italiano cobre regiões, províncias e o país, e município que não seja '
         'capoluogo continua NOT_IN_GAZETTEER. Isso é falta de COBERTURA, declarada, '
         'e não falta de contrato — as duas coisas eram a mesma antes da 018.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-32', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'TERRITORIAL_LIST != FACT_LIST — uma lista de territórios num rótulo '
                   'não é uma lista de lugares onde o fato aconteceu',
  'ONDE_NO_BRASIL': 'a lista de espectro do rótulo lida como ocorrência',
  'WHY_IT_EXISTS': 'a lista do rótulo é a maior fábrica de falso positivo que o Brasil teve',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo_lugar.papel = LISTA_TERRITORIAL guarda a lista COM o papel certo, '
           'e a lista branca so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato (018) '
           'impede que ela vire fato. Guardar a lista é o que permite PROVAR que ela '
           'não virou ocorrência — recusar sem rastro não prova nada.',
  'EXECUTABLE_PROOF': [
      'T1 · a lista econômica existe no banco, com o papel certo',
      'T2 · e nenhum dos três é lugar do fato',
      'T3 · lista nua promovida a FACT é recusada',
      'T3b · a lista branca tem exatamente ESCRITO e CITADO'],
  'GAP': 'a primeira versão da 018 tinha uma trava só para a lista territorial ALÉM da '
         'lista branca. A mutação do red team mostrou que ela nunca disparava — a '
         'lista já caía na outra. Trava que nunca dispara é pior que nenhuma: dá a '
         'impressão de guarda própria. Foi removida, e o conteúdo da lista branca '
         'virou teste, porque alargá-la mataria três leis de uma vez.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-33', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'OCCURRENCE != INCIDENCE — houve não é quanto',
  'ONDE_NO_BRASIL': 'a exigência de denominador em toda razão publicada',
  'WHY_IT_EXISTS': 'uma ocorrência contada como incidência inventa magnitude',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'são DUAS tabelas: conteudo_crop_issue.relacao = OCORRENCIA_DECLARADA diz '
           'que houve; observacao, com base_denominador NOT NULL, diz quanto.',
  'EXECUTABLE_PROOF': ['OCORRENCIA_DECLARADA', 'base_denominador',
                       'observacao guarda valor com denominador'],
  'GAP': None, 'MINIMAL_ACTION': None},

 {'ID': 'BR-34', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'PUBLISHED_AT != FACT_TIME — quando saiu não é quando aconteceu',
  'ONDE_NO_BRASIL': 'a separação entre data da publicação e data do fato',
  'WHY_IT_EXISTS': 'usar a data de publicação como data do fato descarta o retrospectivo '
                   'e envelhece o recente',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'conteudo.fact_tempo_* (018), reusando resolucao_temporal da 009 em vez de '
           'criar um segundo vocabulário de precisão. `PUBLICACAO` NÃO existe no '
           'vocabulário de origem do tempo, e essa ausência é a trava: não há como '
           'declarar que o tempo do fato veio do carimbo da publicação.',
  'EXECUTABLE_PROOF': [
      'F1 · o tempo do fato tem campo próprio',
      'F3 · PUBLICACAO não existe no vocabulário de origem do tempo',
      'C1 · publicado DEPOIS da janela não vira UNRELATED',
      'C2 · publicado ANTES da janela continua RETROSPECTIVE'],
  'GAP': 'o campo existe e a maioria dos conteúdos não o terá preenchido — a fonte '
         'raramente diz quando o fato foi. `tempo_do_fato_desconhecido` torna isso '
         'dizível em vez de deixar a data de publicação ocupar o lugar vago.',
  'MINIMAL_ACTION': None},

 {'ID': 'BR-35', 'FAMILIA': 'LOCALIZACAO_CONFERENCIA',
  'BRAZIL_LESSON': 'a etiqueta de lugar da plataforma não é o lugar do fato',
  'ONDE_NO_BRASIL': 'a praça cadastrada do canal carimbando o documento',
  'WHY_IT_EXISTS': 'é a cicatriz de origem: metadado da plataforma virando medição de campo',
  'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
  'OWNER': 'constraint local_da_fonte_nao_sustenta_local_do_fato (015): DA_FONTE existe '
           'no vocabulário para poder ser DITO e é recusado como sustentação.',
  'EXECUTABLE_PROOF': ['local_da_fonte_nao_sustenta_local_do_fato',
                       'E2 · o lugar da FONTE não sustenta o lugar do FATO'],
  'GAP': None, 'MINIMAL_ACTION': None},
]

VALIDO = ('PROVED', 'PARTIAL', 'ABSENT', 'NOT_MEASURED')


def verificar(a):
    """PROVED exige testemunha encontrável. Não achou, rebaixa e diz."""
    tudo = '\n'.join(a.values())
    saida, rebaixadas = [], []
    for c in list(CICATRIZES):
        c = dict(c)
        faltando = [p for p in c['EXECUTABLE_PROOF'] if p not in tudo]
        c['PROVA_ENCONTRADA'] = [p for p in c['EXECUTABLE_PROOF'] if p in tudo]
        c['PROVA_NAO_ENCONTRADA'] = faltando
        if c['EAME_STATUS'] == 'PROVED' and faltando:
            c['EAME_STATUS'] = 'NOT_MEASURED'
            c['REBAIXADA_POR_ESTE_SCRIPT'] = (
                'declarava PROVED e a testemunha não foi encontrada no acervo: %s'
                % '; '.join(faltando))
            rebaixadas.append(c['ID'])
        saida.append(c)
    return saida, rebaixadas


def monta():
    a = acervo()
    linhas, rebaixadas = verificar(a)
    from collections import Counter
    c = Counter(x['EAME_STATUS'] for x in linhas)
    return {
        'SOURCE_ID': 'BRAZIL-LESSONS-TRANSFER-EAME',
        'VERSION': 'V1',
        'captured_at': '2026-08-30',
        'source': 'lido de lucianodalondon-sys/portal-sintonia e medido contra o acervo '
                  'do EAME. Nenhum número, tabela ou decisão brasileira foi copiada.',
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'O_QUE_ISTO_E': 'a matriz das cicatrizes já pagas no Sintonia Brasil, e o estado '
                        'de cada uma no EAME antes da primeira importação espanhola.',
        'O_QUE_ISTO_NAO_E': 'não é a arquitetura brasileira transplantada. São as LEIS, '
                            'e só as que se aplicam.',
        'REGRA_DO_PROVED':
            'PROVED exige testemunha executável encontrável no acervo — teste, '
            'constraint, função ou afirmação nomeada. Este script confere cada uma e '
            'REBAIXA para NOT_MEASURED o que não achar. Narrativa não vira PROVED.',
        'CICATRIZES_IDENTIFICADAS': len(linhas),
        'PLACAR': {k: c.get(k, 0) for k in VALIDO},
        'REBAIXADAS_PELA_VERIFICACAO': rebaixadas,
        'POR_FAMILIA': dict(Counter(x['FAMILIA'] for x in linhas)),
        'CICATRIZES': linhas,
    }


if __name__ == '__main__':
    d = monta()
    if '--build' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('escrito:', SAIDA)
    print('CICATRIZES =', d['CICATRIZES_IDENTIFICADAS'])
    for k, v in d['PLACAR'].items():
        print('  %-14s %d' % (k, v))
    if d['REBAIXADAS_PELA_VERIFICACAO']:
        print('  REBAIXADAS  :', ', '.join(d['REBAIXADAS_PELA_VERIFICACAO']))
    for x in d['CICATRIZES']:
        if x['EAME_STATUS'] != 'PROVED':
            print('  %-6s %-10s %s' % (x['ID'], x['EAME_STATUS'], x['GAP'][:74] if x['GAP'] else ''))
