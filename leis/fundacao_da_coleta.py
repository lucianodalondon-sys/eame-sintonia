#!/usr/bin/env python3
"""COLLECTION_FOUNDATION_CLOSED != SIM  ->  INTELLIGENCE_IMPLEMENTATION_BLOCKED.

A direcao do projeto e uma so, e ela e sequencial:

    COLETA -> PRESERVACAO -> PROVENIENCIA -> PERSISTENCIA
           -> ADMISSION/READY -> COLLECTION_FOUNDATION_CLOSED
           -> e SO ENTAO inteligencia.

Este ficheiro existe porque uma regra que vive so num relatorio nao segura
nada. A tentacao de comecar a inteligencia antes da fundacao nao aparece como
uma decisao anunciada — aparece como um ficheiro pequeno que «so calcula um
score», e quando alguem repara ja ha um consumidor.

    O QUE FALTA NAO E MODELO. E FUNDACAO.

O QUE ESTA CONGELADO
--------------------
Implementacao, escrita e ativacao de: Field Voices, Opportunity, signals,
scoring, recommendations e a ligacao de inteligencia no portal.

O QUE NAO ESTA
--------------
LER essas areas. Um contrato futuro que ninguem pode ler e um contrato que se
quebra por ignorancia. Ler, medir, documentar e desenhar continua permitido —
o que nao se faz e IMPLEMENTAR.

    LER NAO E IMPLEMENTAR.
    DESENHAR NAO E ATIVAR.

COMO ISTO DEIXA DE VALER
------------------------
Nao por alguem achar que ja da. `COLLECTION_FOUNDATION_CLOSED` vira SIM quando
os criterios do mapa de fechamento estiverem satisfeitos ou com blocker
explicito — e quem muda esta constante muda junto o mapa que a sustenta.

E ele NAO significa «coletamos todas as fontes». Significa: toda CLASSE DE
ESTRADA necessaria tem arquitetura e donos fechados, ou um blocker escrito.
"""
import os

MAPA = os.path.join('docs', 'operacao', 'MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md')
# O ESTADO GERADO, nao a prosa. Quem quiser saber se a fundacao fechou le este
# ficheiro, produzido por `system-map/scripts/censo_das_estradas_it.py` — nunca
# uma tabela escrita a mao.
#
#     SISTEMA REAL -> CENSO -> ESTADO GERADO -> DOCUMENTO.
ESTADO = os.path.join('system-map', 'data', 'estradas-it.generated.json')

# O estado medido em 2026-09-08, quando o censo passou a CALCULAR em vez de
# repetir: ZERO estradas com arquitetura fechada. O mapa anterior publicava
# duas, porque uma pessoa as escreveu.
#
#     OWNER EXISTS NAO E OWNER CONNECTED.
COLLECTION_FOUNDATION_CLOSED = False

AREAS_CONGELADAS = (
    'FIELD_VOICES', 'OPPORTUNITY', 'SIGNALS', 'SCORING',
    'RECOMMENDATIONS', 'PORTAL_INTELLIGENCE_WIRING',
)

BLOQUEIO = 'INTELLIGENCE_IMPLEMENTATION_BLOCKED'
PERMITIDO_LER = 'INTELLIGENCE_READ_ALLOWED'


def pode_implementar_inteligencia():
    """→ (pode, motivo). O padrao e NAO, e isso e a trava — nao um aviso."""
    if COLLECTION_FOUNDATION_CLOSED:
        return True, 'COLLECTION_FOUNDATION_CLOSED=SIM — a fundacao fechou'
    return False, (
        '%s · a fundacao da coleta ainda nao fechou. Ler, medir e desenhar '
        'continua permitido (%s); implementar, escrever e ativar, nao. '
        'O que falta esta em %s.' % (BLOQUEIO, PERMITIDO_LER, MAPA))


if __name__ == '__main__':
    pode, motivo = pode_implementar_inteligencia()
    print('COLLECTION_FOUNDATION_CLOSED = %s' % ('SIM' if COLLECTION_FOUNDATION_CLOSED else 'NAO'))
    print('INTELLIGENCE_IMPLEMENTATION  = %s' % ('LIBERADA' if pode else BLOQUEIO))
    print()
    print(motivo)
