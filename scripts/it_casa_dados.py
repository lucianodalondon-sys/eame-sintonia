#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS DADOS DA CASA — a primeira dobra, montada a partir do que ja atravessou.

    python3 scripts/it_casa_dados.py

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A HOME tem de responder seis perguntas em trinta segundos. A tentacao e
responde-las com os numeros grandes que ja temos a mao: 9.574, 624, 607, 560.
Todos verdadeiros. Nenhum e uma decisao.

    UM NUMERO DE ACERVO NA PRIMEIRA DOBRA MEDE O NOSSO ESFORCO,
    NAO O QUE O CLIENTE TEM DE FAZER NA SEGUNDA-FEIRA.

Por isso este gerador so deixa passar numeros de DECISAO — quantos preparar,
quantos monitorar, quantas leituras se pode mostrar, onde temos olhos — e le-os
dos handoffs ja ingeridos, sem os recontar. Recontar aqui criaria um segundo
dono de cada contagem.

A LINGUA DA TELA E O ITALIANO, E ISSO NAO E COSMETICA. A inteligencia foi
investigada em portugues, e o portal ja tem um portao inteiro (audit/lang.mjs)
nascido de prosa de investigacao portuguesa a chegar ao cliente italiano. Aqui
cada frase que vai a tela viaja em par: IT e a que se le, PT e a que foi escrita.

    TRADUZIR A NOSSA PROSA E LOCALIZACAO. TRADUZIR O FACTO SERIA REESCREVE-LO.

Por isso so a NOSSA moldura — limites, leis, perguntas — e vertida. Numeros,
nomes de produto, numeros de registo, datas e estados administrativos ficam
exactamente como o registo os publica, em italiano de origem.

E DETERMINISTICO: sem relogio, sem aleatorio, chaves ordenadas. A data de
referencia sai dos artefactos, nunca da maquina que corre isto — um carimbo de
relogio faria duas corridas identicas produzirem ficheiros diferentes, e o
"rodei duas vezes e deu igual" deixaria de provar o que quer que seja.
"""
import hashlib
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = os.path.join(ROOT, 'italia-portale', 'client', 'upstream')
OUT = os.path.join(ROOT, 'italia-portale', 'client', 'italy-casa.js')


def ler(nome):
    p = os.path.join(UP, nome)
    with io.open(p, 'rb') as f:
        cru = f.read()
    return json.loads(cru.decode('utf-8')), 'sha256:' + hashlib.sha256(cru).hexdigest()


# ── A NOSSA MOLDURA, EM ITALIANO ────────────────────────────────────────────
# Chave = o texto portugues tal como o handoff a montante o escreveu; valor = o
# que se le na tela. Deixar isto explicito faz da traducao uma coisa auditavel:
# quem quiser conferir compara as duas colunas, em vez de procurar a frase
# italiana num ficheiro e confiar. Se o texto a montante mudar, a chave deixa de
# casar e o gerador PARA — nao renderiza portugues em silencio.
IT = {
 'temos olhos aqui':
   'qui abbiamo occhi',
 'há problema aqui':
   'qui c\'è un problema',
 'o concorrente tem ~10 meses a mais de janela autorizada na mesma dupla de substâncias':
   'il concorrente ha circa 10 mesi in più di finestra autorizzata sulla stessa coppia di sostanze',
 'quatro registros, todos vigentes: dois da ADAMA ITALIA S.R.L. vencendo em 31/05/2027 e dois da CAC CHEMICAL GMBH vencendo em 31/03/2028':
   'quattro registri, tutti vigenti: due di ADAMA ITALIA S.R.L. in scadenza il 31/05/2027 e due di CAC CHEMICAL GMBH in scadenza il 31/03/2028',
 'produtos cujo campo `sostanze_attive` nomeia AZOXYSTROBIN E PROTHIOCONAZOLE ao mesmo tempo':
   'prodotti il cui campo `sostanze_attive` nomina AZOXYSTROBIN e PROTHIOCONAZOLE insieme',
 'ato europeu e registro nacional NÃO são duas fontes independentes: o nacional deriva do europeu. Contá-los como duas confirmações infla a confiança de um fato que tem uma origem só.':
   'atto europeo e registro nazionale NON sono due fonti indipendenti: il nazionale deriva dall\'europeo. Contarli come due conferme gonfia la fiducia in un fatto che ha una sola origine.',
 'se a renovação de 31/05/2027 já está em curso, e se a diferença de janela importa comercialmente':
   'se il rinnovo del 31/05/2027 sia già in corso, e se lo scarto di finestra conti commercialmente',
 'REGRA METODOLÓGICA, não fato bruto: organização territorial Tier A/B sem especialidade declarada cobre todas as especialidades da sua cultura naquela região':
   'REGOLA METODOLOGICA, non dato grezzo: un\'organizzazione territoriale Tier A/B senza specialità dichiarata copre tutte le specialità della sua coltura in quella regione',
 'STRICT mais "Ri-registrato*" e "Rinnovato*"':
   'STRICT piu «Ri-registrato*» e «Rinnovato*»',
 'apenas estados administrativos que contêm "Autorizzato"':
   'solo gli stati amministrativi che contengono «Autorizzato»',
 'JULGAMENTO HUMANO, não fato do registro — é a lacuna DECK-015 (titular ≠ grupo empresarial)':
   'GIUDIZIO UMANO, non fatto del registro — è la lacuna DECK-015 (titolare non equivale a gruppo societario)',
 'NÃO SEI declarado. Uma autorização suspensa não está vigente nem revogada, e nenhum dos critérios acima diz o que fazer com ela. Não forçar para nenhum dos lados até existir regra dona.':
   'NON SO, dichiarato. Un\'autorizzazione sospesa non è né vigente né revocata, e nessuno dei criteri sopra dice cosa farne. Non si forza da nessuna parte finché non esiste una regola che ne risponda.',
 'data de validade sozinha não responde se um registro está utilizável: 223 autorizações estão REVOCATO com vencimento ainda no futuro':
   'la sola data di scadenza non dice se un registro sia utilizzabile: 223 autorizzazioni sono REVOCATO con scadenza ancora nel futuro',
 'motivo declarado em 1119 de 13216. Nos outros, por que foi revogado é NÃO SEI — e não se infere.':
   'motivo dichiarato in 1.119 su 13.216. Per gli altri, il perché della revoca è NON SO — e non si deduce.',
}


# Os tokens do vocabulario interno. Um enum na tela e JSON cru na cara do
# cliente: "NAO" nao e uma palavra italiana, e "NAO_SEI" lido por quem nao
# conhece a regua parece um erro de sistema em vez de uma resposta valida.
# O token fica no artefacto; o que se le e a frase.
ENUM_IT = {
 'NAO': 'no',
 'SIM': 'sì',
 'NAO_SEI': 'NON SO',
 'EXECUTAVEL_COM_ADAPTADOR': 'eseguibile con adattatore',
 'NAO_EXECUTAVEL': 'non eseguibile',
 'SEM_TRANSICAO_SUSTENTADA': 'nessuna transizione sostenuta',
 'PREPARAR->AGIR_AGORA': 'PREPARARE -> AGIRE ORA',
 'OFFICIAL': 'UFFICIALE',
 'SCIENTIFIC': 'SCIENTIFICA',
}


def enum(tok):
    v = ENUM_IT.get(tok)
    if v is None:
        raise SystemExit('token de vocabulario sem leitura italiana: %r' % tok)
    return v


def it(frase):
    """A frase italiana da tela, ou PARA.

    Traduzir por aproximacao seria pior do que nao traduzir: uma frase que
    ninguem escreveu a proposito acaba a explicar um facto ao cliente.
    """
    v = IT.get(frase)
    if v is None:
        raise SystemExit(
            'sem traducao italiana para uma frase que vai a tela:\n  %r\n'
            'acrescente-a ao dicionario IT em scripts/it_casa_dados.py.' % frase[:200])
    return v


def main():
    RF, h_rf = ler('IT-FUTURO-HANDOFF-LINHA-B-V1.json')
    SC, h_sc = ler('IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json')
    FO, h_fo = ler('IT-HANDOFF-LINHA-B-FONTES-V1.json')
    FI, h_fi = ler('IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json')
    HS, h_hs = ler('IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json')
    T3, h_t3 = ler('IT-TOP3-SENSORES-V1.json')

    # ── TOP_3: so entra quem sobreviveu ao atacante ──────────────────────────
    # O veredito e do atacante, nao do autor. Um sensor que o autor declarou
    # executavel e o atacante derrubou entra como DERRUBADO, com o porque — e
    # nunca como sensor. Fabricar o terceiro para manter o nome "TOP_3" seria
    # inventar observabilidade que ninguem provou.
    # A especificacao completa de cada sensor tem milhares de caracteres de prosa
    # tecnica portuguesa. Ela e o artefacto operacional da equipa e continua
    # inteira a montante; o que atravessa para a tela italiana e a leitura curta,
    # escrita a proposito. Despejar a especificacao aqui poria prosa de
    # investigacao portuguesa diante do cliente — o defeito que audit/lang.mjs
    # existe para apanhar — e nao a tornaria mais legivel.
    SENSOR_IT = {
        'ITFC-016': {
            'TITULO': 'Melo · antracnosi post-raccolta in Emilia-Romagna',
            'VARIAVEL': 'presenza o assenza di un\'indicazione di trattamento DOPO la raccolta '
                        'delle varietà precoci contro glomerella / complesso Colletotrichum, '
                        'nella sezione MELO dei bollettini interprovinciali.',
            'FONTE': 'Servizio Fitosanitario Emilia-Romagna — bollettini interprovinciali di '
                     'produzione integrata e biologica (API Plone, JSON, senza chiave).',
            'CADENZA': 'settimanale in stagione, da giugno alla fine della raccolta delle '
                       'varietà tardive; mensile fuori stagione. Mai giornaliera.',
            'SCATTA': 'quando un bollettino datato porta, nello stesso item di difesa della '
                      'sezione MELO, un termine di posteriorità alla raccolta, il bersaglio '
                      'e la sostanza — i tre insieme.',
            'INVALIDA': 'quando nel CRIS UNIBO compare un record datato che conclude che '
                        'l\'inoculo rilevante sverna in gemme e borse fiorali.',
            'ADATTATORE': 'tre pezzi: risolvere per anno il percorso della collezione Plone '
                          '(la rotta provata finisce in «-2026»), filtrare la sezione MELO e '
                          'leggere i PDF. La collezione 2027 non è ancora stata sondata.',
        },
        'ITFC-009': {
            'TITULO': 'Vite · black rot ed escoriosi su varietà resistenti',
            'CAIU_PORQUE': 'la clausola che sembrava piu solida — i bollettini di tre regioni — '
                           'non ha retto: il segnale isola il danno sul grappolo, e la fonte che '
                           'lo dichiara una volta l\'anno non e un bollettino ma la sessione '
                           'annuale di un convegno, con trascrizione da produrre.',
        },
        'ITFC-018': {
            'TITULO': 'Agrumi · dodina nelle linee tecniche siciliane',
            'CAIU_PORQUE': 'quello che sembrava un innesco di cambiamento è, una volta reso '
                           'osservabile, un innesco di conferma; e la fonte primaria — il '
                           'Servizio Fitosanitario della Regione Siciliana — non ha scheda nel '
                           'catalogo, quindi il suo accesso non è mai stato misurato. '
                           'NON SO, non «non esiste».',
        },
    }

    sensores, derrubados = [], []
    for r in T3['ROWS']:
        sid = r['SIGNAL_ID']
        t = SENSOR_IT[sid]
        vivo = r['EXECUTABILITY'] == 'EXECUTAVEL_COM_ADAPTADOR'
        linha = {
            'ID': sid,
            'TITULO': t['TITULO'],
            'EXECUTABILITY': enum(r['EXECUTABILITY']),
            'EXECUTABILITY_TOKEN': r['EXECUTABILITY'],
            'DECLARADA_PELO_AUTOR': enum(r['EXECUTABILITY_DECLARADA_PELO_AUTOR']),
            'AUTORIDADE': enum(r['SOURCE_AUTHORITY']),
            'TRANSICAO': enum(r['STATE_TRANSITION']),
            'TRANSICAO_TOKEN': r['STATE_TRANSITION'],
            'TRANSICAO_AUTORIZADA': enum(T3['TRANSICAO_AUTORIZADA_PELA_REGUA'][sid]),
        }
        if vivo:
            linha.update({'VARIAVEL': t['VARIAVEL'], 'FONTE': t['FONTE'],
                          'CADENZA': t['CADENZA'], 'SCATTA': t['SCATTA'],
                          'INVALIDA': t['INVALIDA'], 'ADATTATORE': t['ADATTATORE']})
        else:
            linha['CAIU_PORQUE'] = t['CAIU_PORQUE']
        (sensores if vivo else derrubados).append(linha)

    a01 = HS['ACHADOS']['01_AZOXISTROBINA_PROTIOCONAZOL']
    a02 = HS['ACHADOS']['02_AUTORIZACOES_ADAMA']
    a03 = HS['ACHADOS']['03_REVOGADO_X_SCADUTO']
    a06 = HS['ACHADOS']['06_COBERTURA_TERRITORIAL']

    casa = {
        'GERADO_POR': 'scripts/it_casa_dados.py',
        'DETERMINISTICO': 'SIM — sem relogio, sem aleatorio, chaves ordenadas',
        'DATA_DE_REFERENCIA': a03['DATA_DE_REFERENCIA_DO_FUTURO'],
        'HASHES_CONSUMIDOS': {
            'IT-FUTURO-HANDOFF-LINHA-B-V1.json': h_rf,
            'IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json': h_fi,
            'IT-HANDOFF-LINHA-B-FONTES-V1.json': h_fo,
            'IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json': h_sc,
            'IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json': h_hs,
            'IT-TOP3-SENSORES-V1.json': h_t3,
        },

        # ── as seis perguntas da primeira dobra ──────────────────────────────
        'RADAR_FUTURO': {
            'PREPARAR': RF['PREPARE'],
            'MONITORAR': RF['WATCH'],
            'AGIR_AGORA': RF['ACT_NOW'],
            'RENDERIZAVEIS': RF['RENDERABLE'],
            'TOTAL': RF['TOTAL'],
            'PORTFOLIO_LIMITED': RF['PORTFOLIO_LIMITED'],
            'LIMITE': ('nessuno di questi è un\'opportunità di oggi: AGIRE ORA è zero '
                       'per decisione della riga, non per mancanza di lettura'),
        },
        'SINAIS_DE_CAMPO': {
            'VISIVEIS': SC['RENDERABLE_CARD'] + SC['RENDERABLE_WITH_METHOD'],
            'CARTAO': SC['RENDERABLE_CARD'],
            'COM_METODO': SC['RENDERABLE_WITH_METHOD'],
            'LIMITE': 'le letture CON METODO viaggiano sempre con il modo in cui sono state lette',
        },
        'FONTES': {
            'COM_METODO': FO['RENDERABLE_WITH_METHOD'],
            'LIMITE': it(a06['O_QUE_O_MAPA_NUNCA_RESPONDE']),
            'LIMITE_PT': a06['O_QUE_O_MAPA_NUNCA_RESPONDE'],
            'RESPONDE': it(a06['O_QUE_O_MAPA_RESPONDE']),
            'RESPONDE_PT': a06['O_QUE_O_MAPA_RESPONDE'],
        },
        'COBERTURA': {
            'CELULAS': a06['CELULAS'],
            'COM_EXPANSAO_GOOD': a06['COM_EXPANSAO_TERRITORIAL']['GOOD'],
            'SEM_EXPANSAO_GOOD': a06['SEM_EXPANSAO_TERRITORIAL']['GOOD'],
            'A_EXPANSAO_E': it(a06['A_EXPANSAO_E']),
            'A_EXPANSAO_E_PT': a06['A_EXPANSAO_E'],
        },
        'EVIDENCIA': {
            'FITOSSANITARIO': FI['EVIDENCE_ONLY'],
            'LEI': FI['LEI_DA_FAMILIA'],
            'NUNCA_E_GRELHA': 'raggiungibile dalla scheda che lo cita, mai come scheda propria',
        },

        # ── o destaque ───────────────────────────────────────────────────────
        'DESTAQUE': {
            'TITULO': 'AZOXYSTROBIN + PROTHIOCONAZOLE',
            'FATO': it(a01['FATO']),
            'FATO_PT': a01['FATO'],
            'UNIVERSO': a01['UNIVERSO'],
            # PASSAVA CRU E CHEGAVA 'SIM' A UMA TELA ITALIANA. A traducao ja
            # existia em ENUM_IT ('SIM' -> 'si'); faltava a chamada. Um valor
            # de uma palavra e o que mais facilmente escapa a revisao: ninguem o
            # le como prosa. `enum()` e fail-closed e recusa o token que nao conhece.
            'E_UNIVERSO_FECHADO': enum(a01['E_UNIVERSO_FECHADO_NAO_AMOSTRA']),
            'CRITERIO': it(a01['CRITERIO_DO_FILTRO']),
            'CRITERIO_PT': a01['CRITERIO_DO_FILTRO'],
            'INTERPRETACAO': it(a01['INTERPRETACAO']),
            'INTERPRETACAO_PT': a01['INTERPRETACAO'],
            'DELTA_MESES': a01['DELTA_JANELA_MESES_APROX'],
            'ADAMA_ATE': '31/05/2027',
            'CONCORRENTE_ATE': '31/03/2028',
            'ITENS': a01['ITENS'],
            'FONTE': a01['FONTE_OFICIAL'],
            'TRAVA_DE_INDEPENDENCIA': it(a01['TRAVA_DE_INDEPENDENCIA']),
            'TRAVA_DE_INDEPENDENCIA_PT': a01['TRAVA_DE_INDEPENDENCIA'],
            'ACTIVATION_QUESTION': (
                'Portafoglio e Sviluppo Mercato: il rinnovo del 31/05/2027 è già in corso, '
                'e lo scarto di finestra conta commercialmente?'),
            'QUEM_DECIDE': it(a01['ACAO_QUE_SO_A_ADAMA_DECIDE']),
            'QUEM_DECIDE_PT': a01['ACAO_QUE_SO_A_ADAMA_DECIDE'],
            'DATA_DO_SNAPSHOT': a02['DATA_DO_SNAPSHOT'],
        },

        # ── com metodo: numero nenhum viaja sozinho ──────────────────────────
        'AUTORIZACOES': {
            'AMPLIADO_CINCO_RAZOES': a02['MATRIZ_CRITERIO_X_RECORTE']['AMPLIADO|ADAMA_CINCO_RAZOES_SOCIAIS']['VIGENTES_COM_VENCIMENTO_FUTURO'],
            'STRICT_CINCO_RAZOES': a02['MATRIZ_CRITERIO_X_RECORTE']['STRICT|ADAMA_CINCO_RAZOES_SOCIAIS']['VIGENTES_COM_VENCIMENTO_FUTURO'],
            'CRITERIO_AMPLIADO': it(a02['CRITERIOS']['AMPLIADO']),
            'CRITERIO_STRICT': it(a02['CRITERIOS']['STRICT']),
            'DATA_DO_SNAPSHOT': a02['DATA_DO_SNAPSHOT'],
            'AGRUPAR_AS_CINCO_E': it(a02['AGRUPAR_AS_CINCO_E']),
            'LIMITE': 'conteggio di registri, e nient\'altro. Non è quota di mercato.',
            'SEM_DONO': it(a02['ESTADOS_SEM_DONO']['REGRA']),
        },
        'REVOGADO_X_SCADUTO': {
            'REVOCATO': a03['REVOCATO'],
            'SCADUTO': a03['SCADUTO'],
            'REVOCATO_COM_VENCIMENTO_FUTURO': a03['REVOCATO_COM_VENCIMENTO_AINDA_FUTURO'],
            'DEMONSTRACAO': it(a03['DEMONSTRACAO']),
            'DEMONSTRACAO_PT': a03['DEMONSTRACAO'],
            'LIMITE': it(a03['LIMITE']),
            'LIMITE_PT': a03['LIMITE'],
        },

        'SENSORES': {
            'SOBREVIVERAM': sensores,
            'DERRUBADOS': derrubados,
            'REGRA': ('si mostra solo ciò che ha retto all\'attacco. Gli abbattuti compaiono '
                      'come abbattuti, con il perché — mai come sensore.'),
            'NADA_FOI_REJULGADO': T3['NADA_FOI_REJULGADO'],
        },

        'DO_NOT_SHOW': HS['DO_NOT_SHOW'],
        'LIMITACOES_DA_CAMADA_HUMANA': HS['LIMITATIONS'],
        'NAO_ENTRA_NA_CASA': {
            '05_PESSOAS_E_PAPEIS': ('P-012 (GDPR) esta aberta: a camada nomeia pessoas com '
                                    'afiliacao e ORCID. Nao entra em tela nenhuma antes de revisao.'),
            '04_SOCIAL_YOUTUBE': 'METHOD_ONLY no proprio handoff. Nao e destaque de HOME.',
            'RECENCIA_TERRITORIAL': ('a camada territorial foi produzida com a leitura de data '
                                     'defeituosa do achado 07. Mostra-se cobertura, nunca recencia.'),
        },
    }

    corpo = json.dumps(casa, ensure_ascii=False, indent=1, sort_keys=True)
    js = ('/* GERADO por scripts/it_casa_dados.py — nao editar a mao.\n'
          '   Os numeros vem dos handoffs ja ingeridos; aqui nao se reconta nada. */\n'
          'window.ITALY_CASA = ' + corpo + ';\n')
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('  escrito : %s' % os.path.relpath(OUT, ROOT))
    print('  sha256  : %s' % hashlib.sha256(js.encode('utf-8')).hexdigest())
    print('  PREPARAR %d · MONITORAR %d · AGIR_AGORA %d · CAMPO %d · FONTES %d'
          % (casa['RADAR_FUTURO']['PREPARAR'], casa['RADAR_FUTURO']['MONITORAR'],
             casa['RADAR_FUTURO']['AGIR_AGORA'], casa['SINAIS_DE_CAMPO']['VISIVEIS'],
             casa['FONTES']['COM_METODO']))
    print('  sensores sobreviventes %d · derrubados %d' % (len(sensores), len(derrubados)))


if __name__ == '__main__':
    main()
