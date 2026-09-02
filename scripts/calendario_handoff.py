#!/usr/bin/env python3
"""Monta o contrato de dado do calendario agronomico para o Claude Design.

O exemplo real nao e escrito a mao: e LIDO do banco depois das migrations
010-012 e da fixture ES. Se o motor mudar de resposta, o contrato muda junto
ou o teste quebra. Contrato que descreve um payload que o codigo nao produz
e pior do que nenhum contrato.

Uso:  python3 scripts/calendario_handoff.py "postgresql://..." [saida.json]
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'samples',
                     'AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1.json')
AS_OF = '2026-08-30'


def consulta(dsn, sql):
    r = subprocess.run(['psql', dsn, '-tAc', sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('psql falhou: ' + r.stderr.strip()[:400])
    return r.stdout.strip()


def caso(dsn, crop, issue):
    return json.loads(consulta(dsn, (
        "select public.f_case_temporal_context('ES', '%s', '%s', null, date '%s')"
        % (crop, issue, AS_OF))))


def enum(dsn, nome):
    return consulta(dsn, "select string_agg(e, ',' order by o) from ("
                         "select unnest(enum_range(null::%s))::text e, "
                         "row_number() over () o) x" % nome).split(',')


def monta(dsn):
    olive = caso(dsn, 'OLIVE', 'REPILO')
    maize = caso(dsn, 'MAIZE', 'AMARANTHUS_PALMERI')
    linhas = [dict(zip(('issue', 'issue_class', 'product_line'), l.split('|')))
              for l in consulta(dsn, "select issue||'|'||coalesce(issue_class,'NOT_KNOWN')"
                                     "||'|'||product_line from public.v_product_line_semantics "
                                     "order by issue").splitlines() if l]
    return {
        "SOURCE_ID": "AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1",
        "VERSION": "V1",
        "captured_at": AS_OF,
        "source": "supabase/migrations/010-012 + supabase/fixtures/es_calendario_mvp.sql, "
                  "lidos de um Postgres 16 montado do zero",
        "SOURCE_LOCATION": "interno",
        "FACT_LOCATION": "ES",
        "ORIGINAL_LANGUAGE": "pt",

        "O_QUE_ISTO_E":
            "o contrato de dado do calendario agronomico. Diz o que o Design RECEBE "
            "e o que cada valor significa. Nao diz como desenhar.",

        "DIVISAO_DE_RESPONSABILIDADE": {
            "ESTA_BRANCH_ENTREGA": [
                "semantica dos quatro relogios", "schema e constraints",
                "consultas e views", "isolamento por pais",
                "estados de ignorancia distinguiveis", "payload compacto do caso",
                "regressoes executadas contra Postgres real"],
            "CLAUDE_DESIGN_ENTREGA": [
                "timeline", "matriz temporal", "interacao",
                "ADAMA Design System", "versao compacta do caso"],
            "NAO_DUPLICAR":
                "nenhum HTML, nenhum pixel e nenhuma cor sai daqui. Cor e do Design System."
        },

        "OS_QUATRO_RELOGIOS": [
            {"CLOCK": "A", "NOME": "CROP_PHASE",
             "PERGUNTA": "onde a cultura esta",
             "DONO": "public.crop_calendar",
             "PAYLOAD_KEY": "current_crop_phase",
             "NAO_E": "nao e janela de produto e nao e pressao de praga"},
            {"CLOCK": "B", "NOME": "ISSUE_WINDOW",
             "PERGUNTA": "quando o problema importa",
             "DONO": "public.issue_window",
             "PAYLOAD_KEY": "current_issue_window_state",
             "NAO_E": "nao e pressao atual de campo. Pressao mora em public.observacao"},
            {"CLOCK": "C", "NOME": "PRODUCT_REGISTERED_WINDOW",
             "PERGUNTA": "ate quando o rotulo autoriza usar",
             "DONO": "public.registro_uso_janela (filho de registro_uso)",
             "PAYLOAD_KEY": "product_window_state",
             "NAO_E": "nao e necessidade de aplicar e nao e disponibilidade comercial"},
            {"CLOCK": "D", "NOME": "EVIDENCE_FRESHNESS",
             "PERGUNTA": "que idade tem a evidencia, para este proposito",
             "DONO": "funcao sobre public.observacao — de proposito nao tem tabela",
             "PAYLOAD_KEY": "observation_freshness",
             "NAO_E": "nao e qualidade do dado e nao e confianca"}
        ],
        "A_LEI":
            "CROP_STAGE != ISSUE_RELEVANCE_WINDOW != REGISTERED_PRODUCT_WINDOW != "
            "EVIDENCE_FRESHNESS. Quatro relogios, quatro colunas, quatro respostas. "
            "Uma unica coluna chamada WINDOW seria a mentira mais barata deste produto.",

        "WINDOW_STATE": [
            {"VALOR": "ACTIVE", "SIGNIFICA": "a data de hoje cai dentro da janela declarada",
             "NAO_SIGNIFICA": "que ha necessidade de agir"},
            {"VALOR": "UPCOMING", "SIGNIFICA": "a janela comeca depois do as_of_date",
             "NAO_SIGNIFICA": "que ja se sabe o dia exato"},
            {"VALOR": "CLOSED", "SIGNIFICA": "o as_of_date passou do fim declarado",
             "NAO_SIGNIFICA": "que nao ha nada a fazer — ver CLOSED != NO_ACTION"},
            {"VALOR": "OUTSIDE_MONTH_RANGE",
             "SIGNIFICA": "a janela e por MES e o mes de hoje esta fora dela",
             "NAO_SIGNIFICA": "CLOSED. Uma janela mensal recorrente volta"},
            {"VALOR": "OBSERVED",
             "SIGNIFICA": "a fase foi estabelecida por fenologia medida, nao por data",
             "NAO_SIGNIFICA": "previsao"},
            {"VALOR": "NOT_KNOWN",
             "SIGNIFICA": "a resolucao guardada nao permite decidir o estado",
             "NAO_SIGNIFICA": "CLOSED. Este e o erro que o contrato mais teme"},
            {"VALOR": "NO_DATA",
             "SIGNIFICA": "nao ha linha registrada para este par",
             "NAO_SIGNIFICA": "que a janela nao existe no campo"}
        ],
        "NAO_EXISTE_CLOSING":
            "CLOSING exigiria um limiar de N dias que ninguem acordou. Enquanto nao "
            "houver decisao, inventar o estado seria inventar o limiar junto.",

        "TEMPORAL_RESOLUTION": [
            {"VALOR": "DATE_EXACT", "EXIBIR_COMO": "intervalo de datas"},
            {"VALOR": "WEEK", "EXIBIR_COMO": "semana"},
            {"VALOR": "MONTH", "EXIBIR_COMO": "meses — nunca um dia dentro do mes"},
            {"VALOR": "PHENOLOGY_STAGE", "EXIBIR_COMO": "faixa BBCH, nunca convertida em data"},
            {"VALOR": "SEASON", "EXIBIR_COMO": "a estacao, com o texto original da fonte"},
            {"VALOR": "APPROXIMATE", "EXIBIR_COMO": "a frase literal da fonte, entre aspas"},
            {"VALOR": "NOT_KNOWN", "EXIBIR_COMO": "ausencia declarada"}
        ],
        "REGRA_DE_PRECISAO":
            "a resolucao nunca sobe para caber na interface. 'primavera' nao vira "
            "2027-03-21, 'outubro/novembro' nao vira 2026-10-01, BBCH 10-85 nao vira data. "
            "Se o desenho precisa de um ponto no eixo, o desenho muda — o dado nao.",

        "CALENDAR_TYPE": [
            {"VALOR": "TYPICAL_CALENDAR", "RECORRE": True,
             "SIGNIFICA": "o que costuma acontecer"},
            {"VALOR": "OFFICIAL_RECOMMENDED_CALENDAR", "RECORRE": True,
             "SIGNIFICA": "o que a autoridade recomenda"},
            {"VALOR": "OBSERVED_CAMPAIGN", "RECORRE": False,
             "SIGNIFICA": "o que foi medido numa campanha nomeada. Nunca projeta para o ano seguinte"},
            {"VALOR": "DERIVED_FROM_MULTIYEAR_DATA", "RECORRE": True,
             "SIGNIFICA": "derivado de serie plurianual, e o payload diz que e derivado"}
        ],

        "PHASE_KNOWN_BY": [
            {"VALOR": "BY_OBSERVED_PHENOLOGY",
             "SIGNIFICA": "a fase saiu de fenologia medida em campo",
             "PRECEDENCIA": "vence BY_DATE quando os dois existem, porque e medicao"},
            {"VALOR": "BY_DATE",
             "SIGNIFICA": "a fase saiu de um calendario por data",
             "PRECEDENCIA": "e expectativa, nao medicao"}
        ],

        "PRODUCT_TARGET_SCOPE": [
            {"VALOR": "ISSUE_LEVEL", "SIGNIFICA": "o rotulo nomeia este alvo"},
            {"VALOR": "CROP_LEVEL",
             "SIGNIFICA": "o rotulo registra o produto para a cultura sem nomear este alvo",
             "POR_QUE_APARECE": "some-lo ao perguntar por um issue viraria 'nao ha produto', "
                                "que e outra afirmacao"}
        ],

        "REGISTRATION_EXPIRY_STATE": [
            {"VALOR": "WITHIN_EXPIRY_DATE", "SIGNIFICA": "a data de caducidade ainda nao chegou"},
            {"VALOR": "EXPIRY_DATE_PASSED",
             "SIGNIFICA": "a data de caducidade registrada ja passou no as_of_date",
             "NAO_SIGNIFICA": "que o produto foi retirado do mercado. EXPIRY != WITHDRAWAL"},
            {"VALOR": "NOT_KNOWN", "SIGNIFICA": "o registro nao declara data de caducidade"}
        ],

        "EVIDENCE_FRESHNESS": [
            {"VALOR": "CURRENT", "SIGNIFICA": "dentro do limiar mais estreito do proposito"},
            {"VALOR": "RECENT", "SIGNIFICA": "dentro do limiar intermediario"},
            {"VALOR": "SEASONAL", "SIGNIFICA": "mesma campanha, ja nao descreve o campo de hoje"},
            {"VALOR": "STALE_FOR_PURPOSE",
             "SIGNIFICA": "medi a idade contra a regua e ela passou de todos os limiares"},
            {"VALOR": "NO_RULE_FOR_PURPOSE",
             "SIGNIFICA": "ninguem cadastrou limiar para este proposito",
             "NAO_SIGNIFICA": "STALE. Sem regua nao ha como condenar a evidencia"},
            {"VALOR": "AGE_NOT_KNOWN",
             "SIGNIFICA": "nao ha data de observacao para calcular idade"}
        ],
        "FRESHNESS_DEPENDE_DO_PROPOSITO":
            "o mesmo dado tem frescor diferente conforme a pergunta. Um levantamento de "
            "2022 e CURRENT para SCIENCE_CONTEXT e STALE_FOR_PURPOSE para FIELD_DECISION. "
            "O payload sempre diz qual proposito foi usado, em freshness_purpose.",

        "CINCO_IGNORANCIAS_QUE_NAO_PODEM_COLAPSAR": {
            "NAO_SEI": "nao sei",
            "NOT_COLLECTED": "nao foi coletado",
            "NOT_KNOWN": "o dado guardado nao sustenta a resposta",
            "AUSENTE_MEDIDO": "procurei e nao ha",
            "NAO_TESTADO": "nao procurei",
            "NO_CALENDARIO": "NO_DATA (nao ha linha) e NOT_KNOWN (ha linha, sem precisao "
                             "para decidir) sao as duas que aparecem neste payload, e sao diferentes"
        },

        "PRODUCT_LINE_SEMANTICS": {
            "REGRA": "semantica, nunca cor. NOT_MAPPED e resposta valida.",
            "MAPA_MEDIDO_DO_BANCO": linhas
        },

        "COMPONENT_DATA_CONTRACTS": [
            {"COMPONENT": "WindowChip",
             "CAMPOS": ["state", "temporal_resolution", "original_text"],
             "REGRA_DURA": "o chip nunca mostra state sozinho. Sem a resolucao ao lado, "
                           "NOT_KNOWN e CLOSED viram a mesma coisa aos olhos do leitor."},
            {"COMPONENT": "CropPhaseMarker",
             "CAMPOS": ["phase", "known_by", "calendar_type", "source"],
             "REGRA_DURA": "known_by e obrigatorio. Fase medida e fase esperada nao podem "
                           "ter a mesma aparencia."},
            {"COMPONENT": "ProductWindowRow",
             "CAMPOS": ["product", "state", "temporal_resolution", "target_scope",
                        "registration_expiry_state", "phi_days", "original_text"],
             "REGRA_DURA": "uma linha ACTIVE nunca pode ser lida como recomendacao. "
                           "O texto original do rotulo viaja junto e nao vai para hover."},
            {"COMPONENT": "FieldEvidenceAge",
             "CAMPOS": ["value", "unit", "denominator", "age_days", "freshness",
                        "freshness_purpose"],
             "REGRA_DURA": "valor, denominador e idade sao inseparaveis — o erro que este "
                           "projeto ja cometeu duas vezes. E o proposito da regua viaja com o estado."},
            {"COMPONENT": "NextWindowList",
             "CAMPOS": ["origin", "what", "when", "source"],
             "REGRA_DURA": "'when' e texto, nao data. Se vier 'a partir de abril', e isso "
                           "que aparece. Lista vazia e resposta, nao erro de carregamento."},
            {"COMPONENT": "TemporalUnknownCounter",
             "CAMPOS": ["temporal_unknown_count"],
             "REGRA_DURA": "o numero de relogios sem resposta e informacao de primeira classe "
                           "e nao pode ser escondido quando for alto."}
        ],

        "PARTIAL_TEMPORAL_EVIDENCE":
            "um caso com temporal_unknown_count > 0 continua sendo um caso. A regra de "
            "exibicao e mostrar o que se sabe e nomear o que falta, nunca esconder o caso "
            "nem completar o buraco com conhecimento geral.",

        "EMPTY_STATES": [
            "next_relevant_window = [] significa: nao ha nada declarado RECORRENTE para "
            "esta cultura. Nao significa que nao havera proxima janela.",
            "product_window_state = [] significa: nenhum uso registrado com janela "
            "cadastrada. Nao significa que nao ha produto registrado.",
            "current_issue_window_state.state = NO_DATA significa: nao ha linha. Nao "
            "significa que o problema nao tem janela no campo."
        ],

        "O_QUE_NUNCA_VEM_NESTE_PAYLOAD": [
            "recomendacao de aplicar",
            "necessidade atual de campo (current_field_need e NOT_KNOWN por contrato)",
            "disponibilidade comercial (NOT_KNOWN por contrato)",
            "cor, hex, token visual",
            "caminho de storage, bucket, RAW, custo, chave",
            "data derivada de resolucao imprecisa"
        ],

        "AS_OF_DATE":
            "'hoje' nunca esta gravado. Todo estado e derivado de as_of_date na hora da "
            "pergunta. Uma demo congelada em 2026-08-30 reproduz exatamente, hoje e daqui "
            "a um ano.",

        "ISOLAMENTO_DE_PAIS":
            "toda funcao temporal exige p_pais. ES nunca recebe fase da Franca, janela da "
            "Italia ou produto de outro pais. Perguntar pela Franca num acervo so-ES "
            "devolve vazio — nunca a resposta da Espanha.",

        "EXEMPLO_REAL_LIDO_DO_BANCO": {
            "COMO_FOI_GERADO": "psql contra Postgres 16 com 001-012 e a fixture ES, "
                               "as_of_date " + AS_OF,
            "CASO_OLIVE_REPILO": olive,
            "CASO_MAIZE_AMARANTHUS_PALMERI": maize
        },

        "DIVERGENCIA_HONESTA_A_RESOLVER": {
            "ONDE": "ES-CASE-001 (olivar x repilo), produto NEPTUNE",
            "O_CARTAO_DIZ": "CLOSED",
            "O_MOTOR_DIZ": "NOT_KNOWN",
            "POR_QUE": "o CLOSED do cartao e raciocinio humano somando 'primera aplicacion "
                       "antes de la floracion' com um prazo de seguranca de 120 dias. O "
                       "motor recusa deduzir isso do dado guardado, porque a resolucao "
                       "APPROXIMATE nao sustenta nem ACTIVE nem CLOSED.",
            "QUEM_ESTA_CERTO": "os dois, sobre coisas diferentes. O humano concluiu; a "
                               "maquina se recusou a concluir sem dado. Registrar a "
                               "divergencia e mais util do que forcar acordo.",
            "O_QUE_RESOLVERIA": "ler a data de floracao do olival na fonte e guarda-la "
                                "como fenologia observada. Ai o motor teria como decidir.",
            "STATUS": "ABERTO — nao resolvido nesta rodada e nao mascarado"
        },

        "REFERENCIAS": [
            "supabase/migrations/010_calendario_agronomico.sql",
            "supabase/migrations/011_calendario_consultas.sql",
            "supabase/migrations/012_contexto_temporal_do_caso.sql",
            "supabase/fixtures/es_calendario_mvp.sql",
            "supabase/tests/regressoes_calendario.sql",
            "data/samples/DISPLAY-LAYER-V1.json",
            "data/samples/DESIGN-DATA-CONTRACT-V1.json"
        ]
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    saida = sys.argv[2] if len(sys.argv) > 2 else SAIDA
    d = monta(sys.argv[1])
    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('escrito:', saida)
