#!/usr/bin/env python3
"""
IT-CASE-DURUM-FUSARIUM-001 — a primeira convergência regional real da Itália.

Um caso factual congelado. **Toscana, não Itália.** A cultura é a maior do país, mas a
evidência é de uma região que responde por **3,7 %** dela, e essa frase tem de sobreviver
a qualquer resumo posterior deste arquivo.

O QUE O CASO É
--------------
No mesmo `CROP × ISSUE × TIMING`, dois textos primários independentes se encontram:

  · o **boletim do Consorzio LaMMA** para Grosseto, de 23/04/2026, diz que o grano duro
    está entrando em floração, que o risco de fusariose é alto com a chuva prevista, e
    que convém tratar;
  · o **rótulo oficial** do MAXENTIS e do KOJAMI autoriza *"Frumento tenero e duro"*
    contra *"Fusarium (Fusarium spp., Microdochium spp.)"* e declara a janela
    *"tra gli stadi di primo nodo visibile (inizio levata) e fine fioritura per il
    controllo delle fusariosi del frumento"*.

Ninguém inferiu a coincidência: ela está escrita nos dois lados.

O QUE O CASO **NÃO** É
-----------------------
Não é oportunidade. Não é recomendação comercial. Não diz que houve venda, que há
estoque, que o produto estava disponível no ponto de venda, nem que alguém deveria ter
comprado. E **não é a Itália**: 57,9 % do trigo duro italiano nunca recebeu sonda de
campo, e as três regiões abertas nesta rodada (Sicília, Basilicata, Campânia) não moveram
a cobertura.

Por isso o rótulo máximo é `REGIONAL CONVERGENCE WORTH INVESTIGATING`.

A JANELA DE 2026 JÁ FECHOU
---------------------------
O caso é de **23/04/2026** e esta medição é de **30/08/2026**. A floração do trigo duro
toscano de 2026 passou há meses. Nada aqui é "agir agora": é uma convergência **provada
para o ciclo seguinte**, e chamá-la de janela aberta seria repetir o erro da flavescência,
que já custou uma correção nesta branch.

O DEFEITO QUE EU DECLARO CONTRA O MEU PRÓPRIO CASO
---------------------------------------------------
A perna do rótulo está preservada: o PDF está em `data/raw/IT/etichette/` com hash. **A
perna de campo não.** A página do LaMMA é rolante — mostra a edição corrente — e eu li a
de 23/04/2026 sem gravá-la. Pela regra que eu mesmo apliquei contra o boletim do Vêneto
hoje de manhã, testemunho de leitura não é evidência re-verificável.

Isso não derruba a substância do encontro; derruba a **auditabilidade** de metade dele. É
a razão de o veredito ser `CONVERGENCE_PARTIAL` e não `PROVED`, e é um defeito com
conserto de um passo: gravar o PDF do boletim.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001', 'IT-T4-001-portfolio-rotulo.json')
PRES = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LAMMA',
                    'IT-T3-LAMMA-grosseto-2026-04-23.json')
ANTE = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS',
                    'IT-CASE-DURUM-FUSARIUM-001-antecipacao.json')


def _opt(p):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-CASE-DURUM-FUSARIUM-001.json')

AS_OF = datetime.date(2026, 8, 30)
DATA_CASO = datetime.date(2026, 4, 23)


def _d(s):
    return datetime.datetime.strptime(s, '%d/%m/%Y').date()


def resposta_regulatoria():
    """Só produtos cuja autorização para grano duro esteja PROVADA no rótulo."""
    port = json.load(open(PORT, encoding='utf-8'))
    fora = []
    for p in port['PRODUCTS']:
        if 'DURUM_WHEAT' not in (p.get('CROP_TERMS_PRESENT') or []):
            continue
        alvos = ' '.join(i.get('SCIENTIFIC_NAME', '')
                         for i in (p.get('ISSUES_FROM_SOURCE') or []))
        if 'Fusarium' not in alvos:
            continue
        subs = (p.get('ACTIVE_SUBSTANCE') or '').upper()
        if 'FLUDIOXONIL' in subs:
            continue  # tratamento de semente: fusariose da SEMENTE, não da espiga
        e = _d(p['EXPIRY']) if p.get('EXPIRY') else None
        fora.append({
            'PRODUCT': p['PRODUCT'],
            'REGISTRATION_ID': p['REGISTRATION_ID'],
            'ACTIVE_SUBSTANCE': p['ACTIVE_SUBSTANCE'],
            'MODE_OF_ACTION': p.get('MODE_OF_ACTION_DECLARED') or 'NÃO DECLARADO NO RÓTULO',
            'DURUM_EVIDENCE': 'CROP_IN_AUTHORIZED_USE_TABLE — "Frumento tenero e duro"',
            'EXPIRY': p['EXPIRY'],
            'STATUS_DECLARED_BY_SOURCE': p['STATUS'],
            'IN_FORCE_AT_CASE_DATE': bool(e and e >= DATA_CASO),
            'IN_FORCE_AT_AS_OF': bool(e and e >= AS_OF),
            'LABEL_FILE': 'data/raw/IT/etichette/%s_*.pdf' % p['REGISTRATION_ID'],
            'RAW_EVIDENCE_STATE': 'PRESERVED',
        })
    return sorted(fora, key=lambda x: x['PRODUCT'])


def relogios(prods):
    vig_caso = [p['PRODUCT'] for p in prods if p['IN_FORCE_AT_CASE_DATE']]
    vig_hoje = [p['PRODUCT'] for p in prods if p['IN_FORCE_AT_AS_OF']]
    venc_hoje = [p['PRODUCT'] for p in prods if not p['IN_FORCE_AT_AS_OF']]
    return {
        'A_OBSERVATION_CLOCK': {
            'STATE': 'PROVED_BY_SOURCE_DATE',
            'FIELD_SIGNAL_DATE': '2026-04-23',
            'READ_ON': '2026-08-30',
            'PUBLISHER': 'Consorzio LaMMA — Regione Toscana / CNR',
            'GAP_BETWEEN_EVENT_AND_READING_DAYS': (AS_OF - DATA_CASO).days,
            'CAVEAT': ('a página é ROLLING_CURRENT_ISSUE: mostra a edição corrente e não '
                       'expõe arquivo. A data é a que a própria edição carrega, mas a '
                       'edição não foi gravada — ver PRESERVATION_DEFECT.'),
        },
        'B_AGRONOMIC_CLOCK': {
            'STATE': 'PROVED_ON_BOTH_SIDES',
            'CROP_PHASE_OBSERVED_IT': ('spigatura nelle classi precoci e medie a nord; a '
                                       'Nodica (Pisa) inizio fioritura nelle precoci e '
                                       'medie, botticella rigonfia nelle tardive'),
            'PROBLEM_WINDOW_LITERAL_IT': ('Dove la fase fenologica sta entrando in '
                                          'fioritura, considerate le piogge e le '
                                          'previsioni di piogge per i prossimi giorni, '
                                          'che comportano quindi un alto rischio '
                                          'fusariosi ... è opportuno effettuare un '
                                          'trattamento fitosanitario'),
            'PRODUCT_WINDOW_LITERAL_IT': ('Intervenire tra gli stadi di primo nodo '
                                          'visibile (inizio levata) e fine fioritura per '
                                          'il controllo delle fusariosi del frumento'),
            'PRODUCT_CONSTRAINT_IT': ('Eseguire massimo un trattamento per anno tra gli '
                                      'stadi di inizio levata e fine spigatura'),
            'WINDOWS_COINCIDE': True,
            'HOW_IT_WAS_ESTABLISHED': ('comparação entre dois textos primários. Nenhuma '
                                       'conversão de escala fenológica foi feita: os '
                                       'dois lados dizem "fioritura" com essa palavra.'),
            'WINDOW_STATE_AT_AS_OF': 'CLOSED_FOR_2026',
            'WHY': ('a floração do trigo duro toscano de 2026 passou há meses. '
                    'MONITORING WINDOW ≠ APPLICATION WINDOW, e janela passada não é '
                    'janela aberta.'),
        },
        'C_REGULATORY_PRODUCT_WINDOW': {
            'STATE': 'PROVED',
            'IN_FORCE_AT_CASE_DATE': vig_caso,
            'IN_FORCE_AT_AS_OF': vig_hoje,
            'EXPIRY_DATE_PASSED_AT_AS_OF': venc_hoje,
            'ANOMALY_NOTE': ('CUSTODIA ULTRA e BLAISE ULTRA têm data de vencimento em '
                             '15/08/2026, quinze dias antes desta medição, e a fonte '
                             'ainda declara "Autorizzato". EXPIRY ≠ WITHDRAWAL: isto NÃO '
                             'afirma retirada nem indisponibilidade — é a classe de '
                             'registro anômalo já conhecida, e fica declarada, não '
                             'resolvida.'),
        },
        'D_COMMERCIAL_CLOCK': {
            'STATE': 'NOT_KNOWN',
            'WHAT_WAS_LOOKED_FOR': ('qualquer evidência PÚBLICA de quando ainda existe '
                                    'decisão comercial aberta: catálogo com data, '
                                    'campanha datada, prazo de pedido, material de '
                                    'posicionamento'),
            'WHY_NOT_KNOWN': ('a camada comercial da ADAMA está BLOCKED (403 de '
                              'datacenter, classe do setor inteiro) e nenhuma fonte '
                              'pública substitui esse dado'),
            'FORBIDDEN_INFERENCE': ('estar na janela agronômica NÃO implica estar na '
                                    'janela comercial. A decisão de compra do agricultor '
                                    'e o ciclo de pedido do canal têm relógio próprio, '
                                    'que não é observável daqui.'),
        },
    }


def mapa_de_acoes():
    """Quem PODE OLHAR agora ≠ quem DEVE AGIR agora. Tudo em forma de pergunta."""
    return {
        'RULE': ('WHO CAN LOOK NOW ≠ WHO MUST ACT NOW. Nenhuma linha abaixo é instrução, '
                 'e nenhuma afirma decisão interna da ADAMA.'),
        'MARKET_DEVELOPMENT': {
            'CAN_LOOK_NOW': True,
            'QUESTION': ('a convergência que a Toscana mostrou se repete nas regiões que '
                         'concentram a cultura? Vale investigar Puglia (28,7 %), Sicília '
                         '(23,6 %) e Basilicata (9,8 %) — onde o sinal de campo não foi '
                         'lido, não onde ele foi negado.'),
            'WHY_NOW': 'a pergunta é de reconhecimento de território e não depende da janela',
        },
        'REGULATORY_PORTFOLIO': {
            'ALREADY_PROVED': ('cinco fungicidas foliares autorizam grano duro contra '
                               'Fusarium, com a janela declarada no próprio rótulo; '
                               'MAXENTIS e KOJAMI declaram FRAC 11+3'),
            'QUESTION': ('dois deles (CUSTODIA ULTRA, BLAISE ULTRA) têm data de '
                         'vencimento já passada com status ainda "Autorizzato". Qual é '
                         'o estado real desses dois registros?'),
            'LIMIT': 'EXPIRY ≠ WITHDRAWAL — a pergunta é essa, a resposta não está aqui',
        },
        'SCIENCE_TECHNICAL': {
            'CAN_LOOK_NOW': True,
            'MISSING_VALIDATION': ('o caso liga rótulo e boletim, e NÃO liga nenhum dos '
                                   'dois a eficácia medida em campo italiano. Faltaria: '
                                   'ensaio de fusariose de espiga em grano duro com '
                                   'azoxystrobin+prothioconazole em condição italiana'),
            'BLOCKED_BY': ('o recorte DURUM_FUSARIUM do OpenAlex (78 obras) continua '
                           'NOT_COLLECTED por 429 persistente nesta infraestrutura'),
            'NOTE': 'pesquisador é evidência de apoio, não condição para o caso existir',
        },
        'MARKETING': {
            'CAN_LOOK_NOW': False,
            'STATE': 'NOT_KNOWN',
            'WHY': ('não há base pública para dizer que exista algo a preparar agora. A '
                    'janela de 2026 fechou, a de 2027 não tem data conhecida, e o '
                    'material da ADAMA não é legível daqui.'),
        },
        'COMMERCIAL': {
            'CAN_LOOK_NOW': False,
            'STATE': 'NOT_KNOWN',
            'WHY': 'nenhuma evidência pública de janela comercial — ver relógio D',
            'NEEDS': 'input da ADAMA; não é derivável de fonte externa',
        },
        'SUPPLY': {
            'CAN_LOOK_NOW': False,
            'STATE': 'NO_STATEMENT_POSSIBLE',
            'WHY': ('exigiria dado interno. A premissa do produto proíbe: nenhuma saída '
                    'pode afirmar REVENUE, MARGIN, SALES, INVENTORY ou ROI REALIZED.'),
        },
    }


def main():
    prods = resposta_regulatoria()
    rel = relogios(prods)
    pres = _opt(PRES)
    ante = _opt(ANTE)
    caso = {
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-CASE-DURUM-FUSARIUM-001',
        'source': ('IT-T3-LAMMA (boletim fitossanitário de Grosseto, 23/04/2026) × '
                   'IT-T4-001-ETICHETTA (tabela de usos autorizados dos rótulos '
                   'ministeriais) × IT-T1-001 (área regional ISTAT)'),
        'CASE_LABEL': 'REGIONAL CONVERGENCE WORTH INVESTIGATING',
        'FORBIDDEN_LABEL': ('"opportunity" — e igualmente proibido elevar isto a "Italy '
                            'opportunity". O caso é da Toscana.'),
        'COUNTRY': 'IT', 'REGION': 'Toscana',
        'PROVINCE': 'Grosseto (e Pisa, com a mesma série)',
        'CROP': 'grano duro',
        'CROP_NATIONAL_THS_HA': 1177.4,
        'REGION_PCT_OF_NATIONAL_CROP': 3.7,
        'ISSUE': 'fusariosi (Fusarium spp., Microdochium spp.)',
        'PHASE_WINDOW': 'fioritura',
        'CASE_DATE': DATA_CASO.isoformat(),
        'AS_OF': AS_OF.isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'SOURCE_LOCATION': 'Toscana (campo) · Itália (rótulo)',
        'FACT_LOCATION': 'ITALY — Toscana',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_CONVERGENCE',

        'OBSERVED': [
            {'WHAT': ('SINTOMA DE FUSARIOSE OBSERVADO no grano duro — não saída de '
                      'modelo: "Si segnala la comparsa di sintomi lievi nel frumento '
                      'duro in alcune situazioni, mentre il tenero resta esente"'),
             'SOURCE': 'Consorzio LaMMA — Regione Toscana / CNR',
             'LOCATOR': 'seção "Bolletino Frumento del 2026-04-23" > subseção Fusariosi',
             'DATE': '2026-04-23', 'PRESERVED': True},
            {'WHAT': ('o duro está em floração no sul da província: "il duro si colloca '
                      'tra piena fioritura e inizio fioritura"'),
             'SOURCE': 'idem', 'LOCATOR': 'subseção Fenologia', 'DATE': '2026-04-23',
             'PRESERVED': True},
            {'WHAT': ('CORREÇÃO DO PRÓPRIO CASO. Eu havia escrito "alto risco de '
                      'fusariosi" para o grano duro. O texto preservado diz: "Il rischio '
                      'risulta elevato nelle classi precoci e medie del frumento TENERO '
                      'nel sud e IN ALCUNE SITUAZIONI DEL DURO". Alto para o tenero; '
                      'para o duro, em algumas situações. A generalização era minha.'),
             'SOURCE': 'idem', 'LOCATOR': 'subseção Fusariosi, "Rischio fusariosi da modello"',
             'DATE': '2026-04-23', 'PRESERVED': True,
             'LAW': 'SINTOMA OBSERVADO ≠ RISCO MODELADO'},
            {'WHAT': ('a mesma série cobre Pisa com grano duro separado do tenero, e NÃO '
                      'cobre Siena, que só recebe boletim de vite — a cultura coberta '
                      'varia por província'),
             'SOURCE': 'Consorzio LaMMA', 'LOCATOR': '<Provincia>_ftsnt.html',
             'DATE': '2026-04-23'},
        ],
        'PROVED': [
            {'WHAT': ('o rótulo oficial do MAXENTIS e do KOJAMI autoriza "Frumento tenero '
                      'e duro (invernale e primaverile)" contra Fusarium spp. e '
                      'Microdochium spp.'),
             'SOURCE': 'IT-T4-001-ETICHETTA — etichetta ministerial',
             'LOCATOR': 'seção DOSI ED EPOCHE DI IMPIEGO, coluna Coltura',
             'EVIDENCE_CLASS': 'CROP_IN_AUTHORIZED_USE_TABLE',
             'RAW_EVIDENCE_STATE': 'PRESERVED'},
            {'WHAT': ('o mesmo rótulo declara a janela de aplicação para fusariose: '
                      '"tra gli stadi di primo nodo visibile (inizio levata) e fine '
                      'fioritura"'),
             'SOURCE': 'idem', 'RAW_EVIDENCE_STATE': 'PRESERVED'},
            {'WHAT': 'as autorizações estavam vigentes na data do caso',
             'SOURCE': 'IT-T4-001 — campo data_scadenza_autorizzazione'},
        ],
        'DERIVED': [
            {'WHAT': ('as duas janelas coincidem em "fioritura", e a coincidência é '
                      'textual: os dois documentos usam a palavra'),
             'HOW': 'comparação literal, sem conversão de escala fenológica',
             'NOT': 'não é modelo, não é score, não é previsão'},
            {'WHAT': ('a Toscana representa 3,7 % do trigo duro italiano — o caso é '
                      'regional por construção'),
             'HOW': 'IT-T1-001 (ISTAT), 43,7 de 1.177,4 mil ha'},
        ],
        'NOT_KNOWN': [
            'se o tratamento foi feito, por quem, em que área ou com que resultado',
            'se houve venda, estoque, disponibilidade em ponto de venda ou recomendação '
            'comercial — o rótulo prova AUTORIZAÇÃO e nada além disso',
            'a janela comercial (relógio D)',
            'se a mesma convergência ocorre nas regiões que concentram a cultura: '
            '57,9 % do trigo duro italiano nunca recebeu sonda de campo',
            'quantas edições o LaMMA publica por ano — a página é rolante, sem arquivo',
            'eficácia em condição italiana: o recorte DURUM_FUSARIUM do OpenAlex '
            'continua NOT_COLLECTED',
        ],
        'ADAMA_REGULATORY_RESPONSE': prods,
        'ADAMA_RESPONSE_CRITERION': ('só entram produtos cuja autorização para grano duro '
                                     'esteja PROVADA na tabela de usos autorizados do '
                                     'rótulo, e cujo alvo declarado inclua Fusarium. O '
                                     'SEEDRON foi EXCLUÍDO de propósito: é tratamento de '
                                     'semente, e a fusariose dele é a transmitida pela '
                                     'semente, não a da espiga.'),
        'CLOCKS': rel,
        'ACTION_MAP': mapa_de_acoes(),
        'PRESERVATION': {
            'FIELD_LEG': 'PRESERVED' if pres.get('PRESERVED') == 'YES' else 'NOT_PRESERVED',
            'PRODUCT_LEG': 'PRESERVED',
            'FIELD_ARTIFACT': pres.get('FILE_NAME'),
            'FIELD_SHA256': pres.get('SHA256'),
            'FIELD_BYTES': pres.get('BYTES'),
            'FIELD_MIME': pres.get('MIME'),
            'FIELD_SOURCE_URL': pres.get('SOURCE_URL'),
            'FIELD_SOURCE_DATE': pres.get('SOURCE_DATE'),
            'FIELD_CAPTURED_AT': pres.get('CAPTURED_AT'),
            'RECHECK': ('hash reconferido a partir do DISCO e do REMOTO; duas coletas '
                        'separadas devolveram o mesmo byte'),
            'ROUTE_STATE': pres.get('ROUTE_STATE'),
            'HISTORY': ('em 30/08 de manhã este campo era NOT_PRESERVED e foi declarado '
                        'como defeito contra o próprio caso. A recuperação encontrou a '
                        'edição ainda exposta — a série de frumento é sazonal e a última '
                        'edição permanece —, então nada precisou ser reconstruído.'),
        },
        'ANTICIPATION_AUDIT': {
            'LAW': 'FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE',
            'PASSES': ante.get('AUDIT_PASSES'),
            'ITEMS_AVAILABLE_BY_CASE_DATE': len(ante.get('AVAILABLE_BY_CASE_DATE', [])),
            'ITEMS_AVAILABLE_ONLY_LATER': len(ante.get('AVAILABLE_ONLY_LATER', [])),
            'ARTIFACT': 'IT-CASE-DURUM-FUSARIUM-001-antecipacao.json',
            'MEANING': ('o alerta fecha com o boletim publicado NO dia e com rótulos de '
                        'vigência anterior. Nenhuma peça posterior sustenta o alerta.'),
        },
        'LIMITATION': ('este caso não prova vendas, estoque, disponibilidade comercial, '
                       'recomendação comercial nem situação nacional. É uma convergência '
                       'REGIONAL, na Toscana, com a janela de 2026 já fechada.'),
        'VERDICT': ('REAL_REGIONAL_CONVERGENCE_PROVED'
                    if (pres.get('PRESERVED') == 'YES' and ante.get('AUDIT_PASSES'))
                    else 'CONVERGENCE_PARTIAL'),
        'VERDICT_MUST_CARRY': {
            'COMMERCIAL_WINDOW': 'NOT_KNOWN',
            'SCOPE': 'TOSCANA / GROSSETO',
            'AGRONOMIC_WINDOW_2026': 'CLOSED at as_of 2026-08-30',
        },
        'VERDICT_DECOMPOSED': {
            'SUBSTANCE': ('PROVED — os três eixos CULTURA × PROBLEMA × MOMENTO se '
                          'encontram, cada um lido de fonte primária, e a coincidência é '
                          'textual e não inferida. A preservação AFINOU o eixo do '
                          'problema: sintoma observado no duro é evidência mais forte que '
                          'o risco modelado que eu tinha citado, e a magnitude do risco '
                          'foi corrigida para baixo.'),
            'PRESERVATION': ('DONE — perna de campo e perna de rótulo, ambas com hash '
                             'reconferível'),
            'SCOPE': ('REGIONAL — Toscana, 3,7 % da cultura. NÃO é Itália, e 57,9 % do '
                      'trigo duro nacional segue sem sonda. O escopo NUNCA foi o motivo '
                      'do PARTIAL, e continua sendo o limite do caso.'),
            'ANTICIPATION': 'PASSES — nenhuma evidência posterior sustenta o alerta',
        },
        'WHAT_THE_PROVED_VERDICT_MEANS': (
            'que o Sintonia TERIA enxergado uma convergência real enquanto ela existia, '
            'com fonte pública disponível no dia. NÃO que ainda exista oportunidade hoje: '
            'a janela agronômica de 2026 fechou, a janela comercial é NOT_KNOWN, e o '
            'caso é de uma província.'),
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'NATIONAL CONVERGENCE', 'ADAMA SHOULD ACT',
                                     'MARKET GAP'],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(caso, fh, ensure_ascii=False, indent=2)

    print('%s · %s' % (caso['CASE_ID'], caso['CASE_LABEL']))
    print('  %s / %s · %s · %s · %s' % (caso['REGION'], caso['PROVINCE'], caso['CROP'],
                                        caso['ISSUE'], caso['PHASE_WINDOW']))
    print('  resposta regulatoria PROVADA para grano duro: %d produtos' % len(prods))
    for p in prods:
        print('     %-15s %-32s exp %s  caso=%s hoje=%s'
              % (p['PRODUCT'], p['ACTIVE_SUBSTANCE'], p['EXPIRY'],
                 'ok' if p['IN_FORCE_AT_CASE_DATE'] else 'NAO',
                 'ok' if p['IN_FORCE_AT_AS_OF'] else 'VENC'))
    for k, v in rel.items():
        print('  %-28s %s' % (k, v['STATE']))
    print('  VEREDITO: %s' % caso['VERDICT'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
