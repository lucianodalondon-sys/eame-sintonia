#!/usr/bin/env python3
"""O CONTRATO DA GESTAO DA COLETA — quem decide O QUE, e quem decide COMO.

    O GESTOR DECIDE O QUE E QUANDO.
    O ORQUESTRADOR DECIDE COMO E POR ONDE.
    O GESTOR NAO CHAMA EXECUTOR.

Esta separacao nao e burocracia. Sem ela, a pergunta «vale a pena ir buscar
isto outra vez?» acaba escrita dentro de um coletor — e a partir dai a decisao
de coletar vive espalhada por vinte ficheiros, cada um com a sua regra, e
ninguem consegue mudar a politica num sitio so. E a G-05 outra vez, uma camada
acima.

O QUE ISTO E
------------
Um CONTRATO. Vocabulario e leis. Nao ha IA aqui, nao ha decisao automatica, e
nao ha nada que corra sozinho.

    CONTRATO NAO E IMPLEMENTACAO.
    E IMPLEMENTACAO NAO E ATIVACAO.

AS SEIS PERGUNTAS DO GESTOR
---------------------------
    O QUE          que necessidade e esta?
    QUANDO         com que frequencia ela precisa de ser satisfeita?
    PRIORIDADE     entre as que faltam, qual primeiro?
    JA TEMOS?      o que ja esta em casa satisfaz?
    ESTA VELHO?    o que temos ainda vale?
    VALE A PENA?   o que se ganha justifica o que custa?

E NENHUMA DELAS E «POR ONDE SE VAI LA». Essa e do orquestrador.

⚠️ O QUE ESTE CONTRATO RECUSA
-----------------------------
    JA TEMOS  !=  ESTA ATUALIZADO
    VELHO     !=  INUTIL
    FALTA     !=  URGENTE
    CARO      !=  IMPOSSIVEL

Um documento de 2019 pode ser exactamente o que se precisa, se a pergunta for
sobre 2019. «Velho» so quer dizer alguma coisa em relacao a uma necessidade
que declara a sua propria janela.
"""

CONTRATO = 'GESTAO_DA_COLETA/v1'

# ─────────────────────────────────────────────────────────────────────────
# O QUE SE PRECISA — e a necessidade e DECLARADA, nao deduzida do que ja veio
# ─────────────────────────────────────────────────────────────────────────
# ⚠️ Deduzir a necessidade do que ja se coletou faz o sistema querer sempre
# mais do mesmo. Uma necessidade que ninguem escreveu nao existe.
CAMPOS_DA_NECESSIDADE = (
    'REQUIREMENT_ID',
    'O_QUE',              # a pergunta que este dado responde
    'JANELA',             # de quando ate quando o dado precisa de ser
    'FRESCURA_EXIGIDA',   # quanto tempo depois ele deixa de servir
    'GRAO',               # documento, observacao, artigo, comentario...
    'PORQUE_IMPORTA',     # sem isto, e recolha por recolha
    'POLICY_VERSION',
)

# Quanto do que se precisa ja esta em casa.
SATISFACAO = (
    'SATISFIED',          # temos, e serve
    'PARTIALLY_SATISFIED',   # temos parte, e o resto tem nome
    'STALE',              # temos, e ja passou da frescura exigida
    'NOT_SATISFIED',      # nao temos
    'UNKNOWN',            # ninguem mediu. NAO e NOT_SATISFIED
    'NOT_APPLICABLE',     # esta necessidade nao se aplica, com razao escrita
)

# ⚠️ UNKNOWN != NOT_SATISFIED.
# «Nao temos» e uma medida. «Ninguem foi ver» e outra. Achatar as duas faz o
# sistema ir buscar o que ja tem, e faz o mapa parecer mais vazio do que e.

CAMPOS_DA_FALTA = (
    'GAP_ID', 'REQUIREMENT_ID', 'SATISFACTION_STATE',
    'O_QUE_FALTA',        # em unidades do GRAO da necessidade
    'DESDE_QUANDO',
    'MEDIDO_EM',
    'COMO_FOI_MEDIDO',    # sem isto, a falta e uma impressao
)

# A prioridade e DECLARADA e tem de dizer de onde veio. Um numero magico que
# ninguem sabe explicar acaba sempre a ser ignorado ou obedecido cegamente, e
# as duas coisas sao mas.
CAMPOS_DA_PRIORIDADE = (
    'PRIORITY', 'PRIORITY_BASIS', 'QUEM_DECIDIU', 'QUANDO', 'POLICY_VERSION',
)
PRIORIDADES = ('P1_BLOQUEIA_OUTRAS', 'P2_NECESSARIA', 'P3_DESEJAVEL',
               'P4_OPORTUNISTA', 'UNKNOWN')

# ─────────────────────────────────────────────────────────────────────────
# A DECISAO — e ela e um ARTEFATO, nao um estado de espirito
# ─────────────────────────────────────────────────────────────────────────
# Uma decisao que nao fica escrita nao pode ser avaliada depois. E sem isso,
# nao ha aprendizagem nenhuma: so opiniao a repetir-se.
CAMPOS_DA_DECISAO = (
    'DECISION_ID', 'GAP_ID', 'DECISION', 'PORQUE',
    'QUEM_DECIDIU', 'QUANDO', 'POLICY_VERSION',
    'CUSTO_ESPERADO', 'GANHO_ESPERADO',
)
DECISOES = (
    'COLLECT_NOW',
    'COLLECT_LATER',
    'DO_NOT_COLLECT',     # com razao escrita
    'NEEDS_HUMAN',        # a politica nao cobre este caso
    'DEFER_UNKNOWN',      # falta medir antes de decidir
)

# O que aconteceu DEPOIS. ⚠️ Sem isto, o gestor nunca sabe se decidiu bem.
CAMPOS_DO_RESULTADO = (
    'DECISION_ID', 'RUN_ID', 'OUTCOME',
    'CUSTO_REAL', 'GANHO_REAL', 'MEDIDO_EM',
)
RESULTADOS = (
    'GAP_CLOSED', 'GAP_REDUCED', 'GAP_UNCHANGED',
    'FAILED', 'NOT_RUN', 'UNKNOWN',
)

# ─────────────────────────────────────────────────────────────────────────
# A FRONTEIRA — e ela e o coracao deste ficheiro
# ─────────────────────────────────────────────────────────────────────────
GESTOR_DECIDE = ('O_QUE', 'QUANDO', 'PRIORIDADE', 'JA_TEMOS', 'ESTA_VELHO',
                 'VALE_A_PENA')
ORQUESTRADOR_DECIDE = ('COMO', 'QUAL_ROTA', 'QUAL_EXECUTOR')

GESTOR_NAO_PODE = (
    'chamar executor',
    'escolher rota',
    'abrir rede',
    'escrever em producao',
)
PORQUE_A_FRONTEIRA = (
    'sem ela, «vale a pena ir buscar isto outra vez?» acaba escrita dentro de '
    'um coletor. A partir dai a decisao de coletar vive espalhada, cada '
    'ficheiro com a sua regra, e ninguem consegue mudar a politica num sitio '
    'so. E a G-05 outra vez, uma camada acima.'
)

LEIS = (
    'O GESTOR DECIDE O QUE E QUANDO; O ORQUESTRADOR DECIDE COMO E POR ONDE',
    'O GESTOR NAO CHAMA EXECUTOR',
    'JA TEMOS != ESTA ATUALIZADO',
    'VELHO != INUTIL',
    'FALTA != URGENTE',
    'CARO != IMPOSSIVEL',
    'UNKNOWN != NOT_SATISFIED',
    'DECISAO SEM RESULTADO MEDIDO NAO ENSINA NADA',
)

SEM_IA_VIVA = (
    'este contrato nao decide nada sozinho. Nao ha modelo, nao ha pontuacao '
    'automatica, e nao ha nada que corra sem alguem mandar. CONTRATO NAO E '
    'IMPLEMENTACAO, E IMPLEMENTACAO NAO E ATIVACAO.'
)


def main():
    print('CONTRATO %s' % CONTRATO)
    print('satisfacao %d · decisoes %d · resultados %d · prioridades %d'
          % (len(SATISFACAO), len(DECISOES), len(RESULTADOS),
             len(PRIORIDADES)))
    print('gestor decide: %s' % ', '.join(GESTOR_DECIDE))
    print('orquestrador decide: %s' % ', '.join(ORQUESTRADOR_DECIDE))
    for l in LEIS:
        print('  · %s' % l)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
