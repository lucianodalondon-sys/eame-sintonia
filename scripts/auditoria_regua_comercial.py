#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDITORIA DA RÉGUA COMERCIAL · mede as 37 oportunidades. NÃO altera o motor.

    python3 scripts/auditoria_regua_comercial.py

O QUE ESTE ARQUIVO É, E O QUE NÃO É
------------------------------------
É uma LEITURA DE FORA sobre `OPPORTUNITIES.json`. Não toca em
`v21_oportunidades.py`, não entra em `v21_cadeia.sh`, não reescreve nenhuma
coleção do pacote e não muda portão, score, arquétipo, red team, status, dado
nem evidência. Roda depois do pacote pronto e devolve um arquivo à parte.

    MEDIR NÃO É MEXER. QUEM MEXE ANTES DE MEDIR NÃO SABE O QUE MUDOU.

A PERGUNTA QUE ELE RESPONDE
---------------------------
O motor prioriza aquilo que a ADAMA chamaria de OPORTUNIDADE COMERCIAL?
Não é a mesma pergunta que o motor faz. O motor pergunta «esta convergência é
defensável?». A auditoria pergunta «esta convergência VENDE alguma coisa,
para qual problema, onde, e por que agora?».

MEDIDO ≠ JULGADO — e por isso são dois blocos separados em cada ficha
--------------------------------------------------------------------
`MEASURED` sai do próprio pacote, por join de ID. Reproduz sozinho.
`REVIEWED` é leitura humana do texto da fonte, e cada campo carrega o ID da
evidência que o justifica. Sem esse ID, o campo não entra.

    JULGAMENTO SEM O ID DA EVIDÊNCIA AO LADO É OPINIÃO COM CARA DE MEDIÇÃO.

A CLASSIFICAÇÃO É SOMBRA
------------------------
`SHADOW_CLASS` não é `OPPORTUNITY_STATE`. Não substitui o estado canônico,
não vai para o pacote de design e não vai à tela. Existe para ser comparada
com o estado do motor — a diferença entre as duas colunas é o achado.
"""
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip')
NO_ZIP = 'ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'AUDITORIA-REGUA-COMERCIAL-37.json')

# Lados do balcão. O rótulo e o registro são a ADAMA falando de si mesma: eles
# provam PORTFÓLIO, nunca CORROBORAÇÃO. Contá-los como família independente é
# fazer a própria empresa testemunhar a favor do próprio caso.
#
#     ROTULO NAO CORROBORA SINAL: ELE RESPONDE «COM O QUE».
LADO_ADAMA = {'LABEL_USE_RELATIONSHIP', 'REGULATORY_PRODUCT',
              'ACTIVE_INGREDIENT', 'COMMERCIAL_PRODUCT'}

# O registro ministerial publica os 163; o catálogo comercial público publica
# os 51. Só o segundo responde «o que a ADAMA vende hoje».
#
#     AUTORIZACAO NAO E CATALOGO, E CATALOGO NAO E ROTULO.
CAT_COMERCIAL = 'PRODUCTS-COMMERCIAL.json'
CAT_REGULATORIO = 'PRODUCTS-REGULATORY.json'


def _pacote(arq):
    """SEMPRE do zip versionado — esta auditoria tem um alvo datado.

    ⚠️ A primeira versão lia o diretório reconstruído quando ele existisse, e a
    ideia parecia boa: quem clona o repositório não deveria ter de rodar a
    cadeia inteira para ler um número. Mas o diretório é o pacote de HOJE, e as
    37 fichas de julgamento abaixo foram escritas contra o pacote de ONTEM.
    Quando o motor V1.1 passou a emitir 43 casos, este arquivo quebrou com
    `KeyError` num ID que nunca foi julgado — e quebrar foi o melhor que podia
    acontecer: pior seria auditar um pacote e imprimir o veredito de outro.

        UMA AUDITORIA DATADA LÊ O PACOTE QUE ELA AUDITOU.
        SEGUIR O PACOTE NOVO NÃO É ATUALIZAR-SE: É TROCAR DE ASSUNTO.

    O zip `build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` é versionado e é o
    estado do motor V1 no commit desta auditoria. É esse, e só esse.
    """
    with zipfile.ZipFile(ZIP) as z:
        with z.open(NO_ZIP + arq) as fh:
            return json.load(io.TextIOWrapper(fh, encoding='utf-8')), 'ZIP'


def _le(arq):
    return _pacote(arq)[0]['RECORDS']


def _num(x):
    """O número de registro é a chave; a grafia dele não é."""
    return re.sub(r'\D', '', str(x or '')).lstrip('0').zfill(6)


# ─────────────────────────────────────────────────────────────────────────────
# O JULGAMENTO, DECLARADO — cada linha carrega o ID que a sustenta
# ─────────────────────────────────────────────────────────────────────────────
# A · GATILHO_EXTERNO   SIM | PARCIAL | NAO
#     SIM exige que o documento de terceiro nomeie o alvo E aponte na direção
#     de agir. «Sospendere», «non necessari interventi» e «vigora la proibizione»
#     são sinal corrente e gatilho comercial NEGATIVO.
#
#         O MOTOR LE QUE A PRAGA APARECE. ELE NAO LE SE O TEXTO MANDA TRATAR.
#
# E · TEMPO             ACT_NOW | PREPARE_NOW | FUTURE | UNKNOWN
#     Janela de aplicação defensável. A data do boletim diz se o sinal é de
#     hoje; ela não diz quando se aplica.
# G · PERGUNTA_DE_VENDA SIM | PARCIAL | NAO
#     «O QUE vender, PARA QUAL problema, ONDE, e POR QUE AGORA» — as quatro.
JULGADO = {
 'OPP_20D89B04F64D': dict(  # O1 · pera × ticchiolatura · Emilia-Romagna
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-001',
   PORQUE='os oito boletins que sustentam o caso nao recomendam nada contra '
          'ticchiolatura: o texto de intervencao fala de maculatura bruna, '
          'colpo di fuoco e peronospora da vinha. SCAB entrou pela lista '
          'PESTS_AND_DISEASES_CITED, que e inventario do documento, nao '
          'recomendacao. O rotulo existe e a data e de ontem; a NECESSIDADE '
          'declarada nao e esta.'),
 'OPP_2BDE8FC566CE': dict(  # O5 · fenpropidina · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_FENPROPIDIN',
   PORQUE='data europeia de 2027-05-15 sobre substancia que UM produto ADAMA '
          'contem. E preparacao de portfolio e de supply. Nao ha problema '
          'agronomico, nao ha geografia italiana e nao ha janela.'),
 'OPP_314CBAE48A5C': dict(  # O4 · tomate · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='pecas pagas de concorrente que ALCANCARAM a Italia, sem alvo '
          'agronomico e sem janela. Le-se como presenca de comunicacao alheia '
          'numa cultura onde a ADAMA tem rotulo — nao como necessidade.'),
 'OPP_31C59C08CBAB': dict(  # O6 · videira · ciencia
   A='PARCIAL', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-037',
   PORQUE='45 trabalhos e 31 sinais na mesma cultura, e nenhum alvo. Sem alvo '
          'nao ha par cultura x problema, e sem par nao ha o que vender.'),
 'OPP_3965565ACFCC': dict(  # O5 · folpete · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_FOLPET',
   PORQUE='a data europeia e 2039-10-31 — 4.807 dias. Treze anos nao sao '
          'preparacao: sao ausencia de prazo. E o caso melhor pontuado em '
          'portfolio de todo o motor.'),
 'OPP_3F736F0A9467': dict(  # O1 · videira × peronospora
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-037',
   PORQUE='os boletins dizem «In generale non necessari interventi» e «a defesa '
          'antiperonosporica pode ser suspensa nas vinhas com invaiatura '
          'completa». O sinal e corrente e a direcao dele e PARAR.'),
 'OPP_4C39CCC05EEB': dict(  # O3 · arroz × Echinochloa
   A='PARCIAL', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-RES-025',
   PORQUE='a resistencia documentada de Echinochloa crus-galli em Italia e '
          'AOS INIBIDORES DA ACCASE (grupo A), e a IT-RES-026 acrescenta '
          'resistencia multipla A+B. O motor cita MODOS_DE_ACAO=[A] como '
          'relevancia ADAMA. O modo de acao que ele oferece e o modo de acao '
          'a que a planta resiste — o caso esta invertido.'),
 'OPP_568684853264': dict(  # O6 · oliveira · ciencia
   A='PARCIAL', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-001',
   PORQUE='sem alvo, e o unico produto de rotulo (MORAINE) nao esta no '
          'catalogo comercial publico. Falta o que vender e falta para que.'),
 'OPP_56F19FD9F62B': dict(  # O1 · maca × cimice
   A='SIM', E='ACT_NOW', G='PARCIAL', CLASSE='SALES_PREPARE',
   ID_EVIDENCIA='IT-PHEN-019',
   PORQUE='«In questa fase la strategia di difesa dovra essere puntuale, specie '
          'su varieta autunnali di melo» — o documento manda agir, diz quando '
          'tratar (de manha) e alerta para o intervalo de seguranca. Ha rotulo '
          'verificado e produto de catalogo (MAVRIK SMART). O que falta e ONDE: '
          'a fonte tem GEOGRAPHIC_SCOPE=NAO_SEI e REGION_REPRESENTS=false.'),
 'OPP_576D71D702F0': dict(  # O2 · milho · mercado
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-MKT-023',
   PORQUE='o gatilho e uma cotacao semanal de milho forrageiro (243,39 EUR/t, '
          'semana 27/07-02/08) mais area do ISTAT. O motor le a data de '
          'publicacao como corrente e devolve ACT_NOW. Preco de cereal nao '
          'abre janela de aplicacao de defensivo.'),
 'OPP_5D03565DB4C3': dict(  # O4 · trigo · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='24 pecas de concorrente em cereal, a mais recente de 18/02/2026. '
          'Ha portfolio comercial forte na cultura (MAXENTIS, MAGANIC), mas '
          'nao ha alvo nem janela — e leitura de mercado, nao de necessidade.'),
 'OPP_68984FFD5ABF': dict(  # O1 · videira × Scaphoideus
   A='PARCIAL', E='PREPARE_NOW', G='PARCIAL', CLASSE='SALES_PREPARE',
   ID_EVIDENCIA='IT-WIN-001',
   PORQUE='a defesa 2026 fechou («a defesa contra Scaphoideus titanus pode '
          'considerar-se concluida»), mas a obrigacao de tratamento contra a '
          'flavescenza recorre por norma e a proxima janela e conhecida em '
          'forma («2 tratamentos, 1a janela 08-19/06»). Ha rotulo verificado e '
          'produto de catalogo. E preparacao de campanha 2027, com data.'),
 'OPP_6B7D9CC9188B': dict(  # O4 · citricos · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='comunicacao de concorrente em citricos, sem alvo e sem janela.'),
 'OPP_6BA350CA1538': dict(  # O2 · soja · peso economico
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-CAN-4C1E4AE512',
   PORQUE='so peso economico, sem observacao de mercado corrente e sem data. '
          'E contexto de cultura, nao evento.'),
 'OPP_6E18A133EE14': dict(  # O5 · bupirimato · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_BUPIRIMATE',
   PORQUE='2027-01-31, 151 dias — e a data mais proxima das sete de O5, e a '
          'que melhor merece preparacao de portfolio. Continua sem problema '
          'agronomico e sem geografia italiana.'),
 'OPP_75C37DED9160': dict(  # O1 · maca × carpocapsa · Veneto
   A='SIM', E='PREPARE_NOW', G='SIM', CLASSE='SALES_READY',
   ID_EVIDENCIA='IT-CAN-D9582B1FD6',
   PORQUE='boletim frutticolo do Veneto, corrente, declara terceiro voo de '
          'Cydia pomonella terminado com «danni in aumento anche in frutteti a '
          'gestione integrata» — isto e, a solucao em uso esta a falhar, dito '
          'pelo servico oficial. Regiao declarada e representada, rotulo '
          'ministerial verificado no par maca x carpocapsa, e dois produtos do '
          'catalogo comercial no par (LAMDEX EXTRA, MAVRIK SMART). Fecha as '
          'quatro perguntas. A unica fragilidade e corroboracao: um publicador.'),
 'OPP_84D116CA45B1': dict(  # O4 · arroz · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='tres pecas de concorrente em arroz, sem alvo e sem janela.'),
 'OPP_886307860F79': dict(  # O5 · mesotriona · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_MESOTRIONE',
   PORQUE='2032-05-31, 2.098 dias. Seis anos de antecedencia nao e urgencia '
          'nem preparacao: e cadastro.'),
 'OPP_88CC35C57C7B': dict(  # O5 · imazamox · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_IMAZAMOX',
   PORQUE='2027-06-30, 301 dias, com quatro produtos ADAMA. Preparacao '
          'regulatoria legitima; nao e venda.'),
 'OPP_89C265BDADCE': dict(  # O4 · videira · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='42 pecas de concorrente em videira — o maior volume competitivo do '
          'pacote. Sem alvo e sem janela, e leitura de disputa, nao de venda. '
          'A janela que a ficha exibe (2027-05-31) e data de ato, nao de '
          'aplicacao.'),
 'OPP_8E210567B01F': dict(  # O4 · milho · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='69 pecas de concorrente em milho, a mais recente de 19/03/2026.'),
 'OPP_8EA4F5C0D3F4': dict(  # O2 · cevada · mercado
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-MKT-022',
   PORQUE='cotacao semanal de cevada forrageira (205,60 EUR/t). Mesmo defeito '
          'do milho: data de publicacao lida como corrente vira ACT_NOW.'),
 'OPP_9AB924CA36C8': dict(  # O2 · beterraba · peso economico
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-CAN-4C1E4AE512',
   PORQUE='so peso economico, sem data.'),
 'OPP_9C600748BB1B': dict(  # O1 · milho × piralide · FVG
   A='SIM', E='PREPARE_NOW', G='SIM', CLASSE='SALES_PREPARE',
   ID_EVIDENCIA='IT-PHEN-048',
   PORQUE='a ERSA declara limiar («posturas superiores a 3 por cada 100 '
          'plantas»), inicio do voo da 3a geracao e pico esperado nos dias '
          'seguintes. Regiao declarada E representada — o unico O1 regional '
          'com REGION_REPRESENTS=true e alvo. Rotulo verificado e produto de '
          'catalogo (LAMDEX EXTRA). O que rebaixa e o tempo: o boletim e de '
          '12/08 e o proprio texto restringe o dano as semeaduras tardias.'),
 'OPP_AF16E6A6B8B3': dict(  # O2 · videira · mercado
   A='NAO', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-CAN-3312E852F3',
   PORQUE='peso economico e cotacao. A janela 2027-05-31 que a ficha exibe vem '
          'de PREPARATION_WINDOW = «ate 2027-05-31, quando historicamente sai '
          'o ato» — data administrativa, nao janela de aplicacao.'),
 'OPP_B19061BA418B': dict(  # O4 · oliveira · concorrente
   A='PARCIAL', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='24 pecas de concorrente e um unico produto de rotulo (MORAINE), '
          'fora do catalogo comercial publico. Sem o que vender.'),
 'OPP_B362181E3A45': dict(  # O2 · arroz · peso economico
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-CAN-4C1E4AE512',
   PORQUE='so peso economico, sem data.'),
 'OPP_B9206ACFC797': dict(  # O5 · 2,4-D · UE · o cartao que absorveu 38
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='RFF_2_4_D',
   PORQUE='a identidade deterministica colapsa em UM cartao todos os fatos '
          'regulatorios sem cultura unica: 38 fusoes, 250 apoios, zero cultura '
          'de rotulo e PRODUCT_LINK_STATE=RELATED_PORTFOLIO. Nao e uma '
          'oportunidade: e a gaveta das outras 38.'),
 'OPP_C37A1FD2742E': dict(  # O1 · videira × tignoletta
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-017',
   PORQUE='o apoio de campo e uma tabela de capturas e o proprio registro diz '
          '«NAO SEI — o documento e tabela de capturas e modelo, sem texto de '
          'recomendacao». Captura nao e limiar, e limiar nao e dano.'),
 'OPP_DA4B5954F72A': dict(  # O1 · maca × ticchiolatura · Emilia-Romagna
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-002',
   PORQUE='mesmo defeito da pera: nos boletins de Emilia-Romagna o texto de '
          'intervencao para macieira e glomerella e colpo di fuoco, nao '
          'ticchiolatura. E o caso de score 11 — o mais alto do motor.'),
 'OPP_E1A1D73F07BF': dict(  # O4 · maca · concorrente
   A='PARCIAL', E='UNKNOWN', G='PARCIAL', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='cinco pecas de concorrente contra 143 rotulos ADAMA na cultura — a '
          'maior cobertura de portfolio do pacote. Leitura de posicao, nao de '
          'necessidade.'),
 'OPP_E6200AA0FA63': dict(  # O5 · florasulame · UE
   A='PARCIAL', E='FUTURE', G='NAO', CLASSE='STRATEGIC_OPPORTUNITY',
   ID_EVIDENCIA='RFF_FLORASULAM',
   PORQUE='2030-12-31, 1.581 dias.'),
 'OPP_EA2AE1EFB775': dict(  # O1 · tomate × peronospora · Veneto
   A='SIM', E='ACT_NOW', G='PARCIAL', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-CAN-03C08A9CCB',
   PORQUE='o gatilho e bom e raro: chuvas de 17-23/08 criaram «condizioni '
          'ideali per lo sviluppo di nuove infezioni» e o boletim RECOMENDA '
          'tratar os lotes com colheita prevista em 25-30 dias — necessidade, '
          'geografia regional e janela, tudo declarado. O que falta e o '
          'portfolio: nenhum produto do catalogo comercial publico tem rotulo '
          'no par tomate x peronospora. Existe no registro ministerial; nao '
          'existe no catalogo. E exatamente a distincao 51 x 163.'),
 'OPP_EE1E2A3869EE': dict(  # O2 · oliveira · peso economico
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-CAN-4C1E4AE512',
   PORQUE='so peso economico, e o unico rotulo (MORAINE) esta fora do catalogo '
          'comercial. Nao ha o que vender nem por que agora.'),
 'OPP_F139E05A9F3A': dict(  # O1 · tomate × oidio · FVG
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-045',
   PORQUE='o boletim ORTIVE da ERSA recomenda contra oidio em RADICCHIO, nao '
          'em tomate. O par tomate x oidio nasce do produto cartesiano entre a '
          'lista de culturas e a lista de alvos do mesmo documento. E nao ha '
          'produto do catalogo comercial no par.'),
 'OPP_F6EEF5B32F65': dict(  # O1 · milho × diabrotica · Lombardia
   A='NAO', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-PHEN-022',
   PORQUE='o documento e uma PROIBICAO: «durante a floracao vigora a proibicao '
          'de intervencao fitoiatrica com inseticidas, para tutela das abelhas». '
          'O motor leu proibicao de tratamento como pressao de campo, e deu 10.'),
 'OPP_FBA64D2CA10D': dict(  # O4 · hortalicas · concorrente
   A='PARCIAL', E='UNKNOWN', G='NAO', CLASSE='TO_VALIDATE',
   ID_EVIDENCIA='IT-COMP-ACT-002',
   PORQUE='cinco pecas de concorrente e um unico rotulo, um glifosato '
          '(GLIPHOGAN TOP CL) fora do catalogo comercial publico.'),
}

CLASSES = ('SALES_READY', 'SALES_PREPARE', 'STRATEGIC_OPPORTUNITY', 'TO_VALIDATE')


def geografia_se_sustenta(escopo, sinais):
    """A geografia do caso cabe dentro da geografia de quem a sustenta?

    Isto NÃO é o portão A do motor. O portão A soma os `REGION_IDS` de todos
    os apoios — inclusive os do rótulo ministerial, que é nacional — e depois
    reprova o caso regional por «geografias que nao se contem». A autorização
    nacional CONTÉM a região: ela é o que torna o caso regional vendável.

        CONTER NAO E CONTRADIZER. QUEM SOMA O ROTULO A GEOGRAFIA DO SINAL
        TRANSFORMA A PROPRIA AUTORIZACAO EM OBJECAO.

    Aqui só o sinal de campo responde pela geografia.
    """
    if not sinais:
        return 'NOT_APPLICABLE', ('o caso nao se apoia em observacao de campo: '
                                  'a geografia dele e a do ato ou da peca, e '
                                  'nao ha promocao de ambito a medir')
    if escopo == 'PROVINCIAL':
        return True, 'a alegacao e tao estreita quanto o apoio'
    if escopo == 'REGIONAL':
        ok = [s for s in sinais if s.get('GEOGRAPHIC_SCOPE') == 'REGIONAL'
              and s.get('REGION_REPRESENTS') is not False]
        return bool(ok), ('ha boletim de ambito regional que fala PELA regiao'
                          if ok else
                          'so ha apoio provincial sustentando alegacao regional')
    ok = [s for s in sinais if s.get('REGION_REPRESENTS') is not False]
    return bool(ok), ('ha apoio que fala pelo proprio ambito' if ok else
                      'todo apoio e provincial e a alegacao e mais ampla')


def medir():
    opp = _le('OPPORTUNITIES.json')
    com = _le(CAT_COMERCIAL)
    rel = [r for r in _le('PRODUCT-RELATIONSHIPS.json') if r.get('CLIENT_SAFE')]
    sinal = {s['ID']: s for s in _le('CURRENT-FIELD-SIGNALS.json')}

    # catálogo comercial → número de registro → par de rótulo
    com_por_num = defaultdict(list)
    for c in com:
        n = _num(c.get('MATCHED_REGULATORY_ID') or c.get('REGISTRATION_NUMBER_ON_PAGE'))
        if n != '000000':
            com_por_num[n].append(c['NAME'])

    lab_crop, lab_par = defaultdict(list), defaultdict(list)
    for r in rel:
        for c in (r.get('CROP_IDS') or []):
            lab_crop[c].append(r)
            for i in (r.get('ISSUE_IDS') or []):
                lab_par[(c, i)].append(r)

    def comerciais(regs):
        out = set()
        for r in regs:
            out |= set(com_por_num.get(_num(r.get('REGISTRATION_NUMBER')), []))
        return sorted(out)

    fichas = []
    for o in opp:
        crop, alvo = o.get('CROP'), o.get('TARGET')
        b = comerciais(lab_crop.get(crop, []))
        c = comerciais(lab_par.get((crop, alvo), [])) if (crop and alvo) else []
        fam_ext = sorted(set(o.get('EVIDENCE_FAMILIES') or []) - LADO_ADAMA)
        # o registro ministerial publica todos os rótulos: não é publicador de sinal
        pubs = sorted(s for s in (o.get('SOURCE_IDS') or [])
                      if s != 'SRC_FITOSANITARI_SALUTE_GOV_IT')
        sin = [sinal[e] for e in o['EVIDENCE_IDS'] if e in sinal]
        geo_ok, geo_porque = geografia_se_sustenta(o.get('GEOGRAPHIC_SCOPE'), sin)
        j = JULGADO[o['ID']]
        fichas.append({
            'ID': o['ID'],
            'ARCHETYPE': o['ARCHETYPE'],
            'CROP': crop, 'TARGET': alvo,
            'MOTOR': {'OPPORTUNITY_STATE': o['OPPORTUNITY_STATE'],
                      'STATUS': o['STATUS'],
                      'OPPORTUNITY_SCORE': o['OPPORTUNITY_SCORE'],
                      'PRODUCT_LINK_STATE': o['PRODUCT_LINK_STATE'],
                      'BLOCKING_GATES': o.get('BLOCKING_GATES') or []},
            'MEASURED': {
                'B_ENCAIXE_COMERCIAL': 'SIM' if b else 'NAO',
                'B_PRODUTOS_DO_CATALOGO_NA_CULTURA': b,
                'C_ROTULO_CULTURA_X_ALVO': ('NOT_APPLICABLE' if not alvo
                                            else ('SIM' if c else 'NAO')),
                'C_PRODUTOS_DO_CATALOGO_NO_PAR': c,
                'D_ONDE': {'PROVINCIAL': 'PROVINCIAL', 'REGIONAL': 'REGIONAL',
                           'NACIONAL': 'NATIONAL', 'EUROPEU': 'EU'
                           }.get(o.get('GEOGRAPHIC_SCOPE'), 'UNKNOWN'),
                'D_GEOGRAFIA': o.get('GEOGRAPHY'),
                'D_GEOGRAFIA_SE_SUSTENTA': geo_ok,
                'D_POR_QUE': geo_porque,
                'F_FAMILIAS_EXTERNAS': fam_ext,
                'F_N_FAMILIAS_EXTERNAS': len(fam_ext),
                'F_PUBLICADORES_EXTERNOS': pubs,
                'F_N_PUBLICADORES': len(pubs),
                'SIGNAL_DATE': o.get('SIGNAL_DATE'),
                'SIGNAL_AGE_DAYS': o.get('SIGNAL_AGE_DAYS'),
                'WINDOW_STATE': o.get('WINDOW_STATE'),
            },
            'REVIEWED': {
                'A_GATILHO_EXTERNO': j['A'],
                'E_QUANDO': j['E'],
                'G_PERGUNTA_DE_VENDA': j['G'],
                'EVIDENCE_ID': j['ID_EVIDENCIA'],
                'WHY': j['PORQUE'],
                'LAW': 'leitura do texto da fonte, com o ID do apoio ao lado. '
                       'Nao sai do pacote sozinha e nao e reproduzivel por '
                       'maquina — por isso vive separada de MEASURED.',
            },
            'SHADOW_CLASS': j['CLASSE'],
        })
    return fichas


def coerencia(fichas):
    """Uma classificação que se contradiz não é classificação: é preferência."""
    erros = []
    for f in fichas:
        cl, m, r = f['SHADOW_CLASS'], f['MEASURED'], f['REVIEWED']
        if cl not in CLASSES:
            erros.append(f"{f['ID']}: classe desconhecida {cl}")
        if cl in ('SALES_READY', 'SALES_PREPARE'):
            if m['B_ENCAIXE_COMERCIAL'] != 'SIM':
                erros.append(f"{f['ID']}: {cl} sem produto de catalogo comercial")
            if m['C_ROTULO_CULTURA_X_ALVO'] == 'NAO':
                erros.append(f"{f['ID']}: {cl} sem rotulo no par cultura x alvo")
            if r['A_GATILHO_EXTERNO'] == 'NAO':
                erros.append(f"{f['ID']}: {cl} sem gatilho externo")
        if cl == 'SALES_READY':
            if r['G_PERGUNTA_DE_VENDA'] != 'SIM':
                erros.append(f"{f['ID']}: SALES_READY que nao responde as quatro")
            if r['E_QUANDO'] in ('UNKNOWN',):
                erros.append(f"{f['ID']}: SALES_READY sem tempo defensavel")
            if not m['D_GEOGRAFIA_SE_SUSTENTA'] or m['D_ONDE'] == 'UNKNOWN':
                erros.append(f"{f['ID']}: SALES_READY sem geografia que se sustente")
    return erros


def defeitos_do_motor():
    """Dois defeitos são reproduzíveis aqui mesmo, sem tocar no motor."""
    # 1 · o red team de O4 dispara na PRÓPRIA frase fixa do arquétipo
    texto_o4 = ('ANUNCIO ALCANCOU NAO E ANUNCIO MIRAVA, e COMUNICACAO NAO E '
                'PARTICIPACAO DE MERCADO. NAO prova investimento, share nem '
                'resultado.')
    auto = bool(re.search(r'share|participac|quota',
                          json.dumps({'WHAT_IT_DOES_NOT_PROVE': texto_o4},
                                     ensure_ascii=False), re.I))
    # 2 · o portão A conta o rótulo nacional como geografia concorrente
    opp = _le('OPPORTUNITIES.json')
    o4 = [o for o in opp if o['ARCHETYPE'] == 'O4_COMPETITIVE_OPENING']
    o4_derrubados = [o['ID'] for o in o4 if any(
        'comunicacao de concorrente virou participacao' in g
        for g in (o.get('BLOCKING_GATES') or []))]
    porta_a = [o['ID'] for o in opp if any(
        'A_GEOGRAFIA · apoios em geografias que nao se contem' in g
        for g in (o.get('BLOCKING_GATES') or []))]
    return {
        'D1_RED_TEAM_O4_DISPARA_NO_PROPRIO_TEXTO': {
            'REPRODUZIDO': auto,
            'O_QUE_E': 'red_team() roda a regex share|participac|quota sobre '
                       'json.dumps(o), e `o` ja contem WHAT_IT_DOES_NOT_PROVE, '
                       'que e a frase FIXA do arquetipo O4 e diz «COMUNICACAO '
                       'NAO E PARTICIPACAO DE MERCADO». A regex casa com o '
                       'proprio aviso.',
            'EFEITO': 'nenhum dos %d casos O4 pode ser confirmado, por '
                      'construcao.' % len(o4),
            'CASOS': o4_derrubados,
            'LEI': 'O AVISO CONTRA UM ERRO NAO E O ERRO. QUEM MEDE O PROPRIO '
                   'TEXTO MEDE A SI MESMO.',
        },
        'D2_PORTAO_A_TRATA_ROTULO_NACIONAL_COMO_GEOGRAFIA_CONCORRENTE': {
            'O_QUE_E': 'portoes() junta REGION_IDS de TODOS os apoios. O sinal '
                       'de campo e regional; o rotulo ministerial e GEO_ITALY. '
                       'Sao duas geografias, o caso e regional, e o portao '
                       'fecha por «geografias que nao se contem».',
            'EFEITO': 'autorizacao nacional — que e justamente o que torna o '
                      'caso regional vendavel — passa a derrubar o caso.',
            'CASOS': porta_a,
            'LEI': 'ROTULO NACIONAL CONTEM A REGIAO. CONTER NAO E CONTRADIZER.',
        },
    }


def main():
    fichas = medir()
    erros = coerencia(fichas)
    if erros:
        print('AUDITORIA INCOERENTE — nada foi gravado:', file=sys.stderr)
        for e in erros:
            print('  ·', e, file=sys.stderr)
        return 1

    por_classe = Counter(f['SHADOW_CLASS'] for f in fichas)
    confirmadas = [f for f in fichas
                   if f['MOTOR']['OPPORTUNITY_STATE'] == 'OPPORTUNITY_CONFIRMED']
    cab, de_onde = _pacote('OPPORTUNITIES.json')
    saida = {
        'COLLECTION': 'AUDITORIA-SOMBRA-REGUA-COMERCIAL',
        'SCHEMA_VERSION': 'V1',
        'SOURCE_OF_TRUTH': 'leitura externa sobre DESIGN-INGEST/OPPORTUNITIES.json',
        'PACOTE_LIDO_DE': de_onde,
        'BUILD_ID_AUDITADO': cab['BUILD_ID'],
        'LAW': 'SOMBRA. Nao e OPPORTUNITY_STATE, nao entra no pacote de design, '
               'nao vai a tela e nao entra em v21_cadeia.sh. Existe para ser '
               'comparada com o estado do motor.',
        'MEASURED_VS_REVIEWED': 'MEASURED sai do pacote por join de ID e '
                                'reproduz sozinho. REVIEWED e leitura do texto '
                                'da fonte e carrega o ID que a justifica.',
        'COUNT_TOTAL': len(fichas),
        'BY_SHADOW_CLASS': dict(por_classe),
        'CONFIRMADAS_PELO_MOTOR': {
            'COUNT': len(confirmadas),
            'BY_SHADOW_CLASS': dict(Counter(f['SHADOW_CLASS'] for f in confirmadas)),
        },
        'DEFEITOS_REPRODUZIDOS': defeitos_do_motor(),
        'RECORDS': fichas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=1)

    print('BUILD_ID auditado:', saida['BUILD_ID_AUDITADO'])
    print('total', len(fichas))
    for c in CLASSES:
        print(f'  {c:<24}{por_classe.get(c, 0)}')
    print('\ndas 9 confirmadas pelo motor:')
    for c in CLASSES:
        n = saida['CONFIRMADAS_PELO_MOTOR']['BY_SHADOW_CLASS'].get(c, 0)
        print(f'  {c:<24}{n}')
    print('\nfamilias externas por caso:',
          dict(Counter(f['MEASURED']['F_N_FAMILIAS_EXTERNAS'] for f in fichas)))
    print('gravado em', os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
