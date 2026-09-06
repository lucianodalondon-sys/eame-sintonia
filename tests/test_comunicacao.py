#!/usr/bin/env python3
"""
REGRESSÕES DA COMUNICAÇÃO PÚBLICA DO CONCORRENTE.

    py tests/test_comunicacao.py

POR QUE ESTE ARQUIVO EXISTE AGORA, ANTES DE EXISTIR CORPUS
------------------------------------------------------------
Porque a régua de identidade e a de classificação vão rodar sobre dado que ainda não
chegou, e o jeito de saber que elas estão certas hoje é dar a elas os casos que a
LEITURA REAL dos 15 sites âncora já produziu. Cada teste abaixo é um caso que aconteceu,
não um caso inventado — inclusive os que reprovam.

O teste mais importante é o negativo: provar que a régua RECUSA o que ela tem que
recusar. Uma régua que só é testada com o que ela aceita não é testada.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import comunicacao_classificar as cl      # noqa: E402
import comunicacao_identidade as ident    # noqa: E402
import comunicacao_universo as uni        # noqa: E402

FALHAS = []


def checa(nome, obtido, esperado):
    if obtido != esperado:
        FALHAS.append('%s\n     esperado: %r\n     obtido:   %r' % (nome, esperado, obtido))
        print('  FALHOU  %s' % nome)
    else:
        print('  ok      %s' % nome)


# ── o que NÃO é conta ───────────────────────────────────────────────────────────
print('\nURLs que passam pelo filtro de domínio e NÃO são conta:')
for url, esperado in [
    ('https://www.facebook.com/policy.php/', True),
    ('https://www.youtube.com/watch?v=iWTktO4WKQ0', True),
    ('https://youtube.com/playlist?list=PL6qwtP', True),
    ('https://www.facebook.com/SyngentaES/', False),
    ('https://www.youtube.com/user/nufarmespana', False),
]:
    checa('nao_e_conta(%s)' % url.split('/', 3)[-1][:34],
          bool(ident.nao_e_conta(url)), esperado)


# ── o handle é a conta; o host é a interface ────────────────────────────────────
print('\nidentificador — o subdomínio de idioma NÃO faz parte da conta:')
checa('it.linkedin.com/company/bayer-cropscience',
      ident.identificador('https://it.linkedin.com/company/bayer-cropscience'),
      'bayer-cropscience')
checa('au.linkedin.com/company/nufarm',
      ident.identificador('https://au.linkedin.com/company/nufarm'), 'nufarm')
checa('youtube.com/@BayerAgri',
      ident.identificador('https://www.youtube.com/@BayerAgri'), 'BayerAgri')
checa('acento percent-encoded volta inteiro',
      ident.identificador('https://www.youtube.com/c/BayerCropScienceEspa%C3%B1a'),
      'BayerCropScienceEspaña')


# ── escopo: o que promove e, principalmente, o que NÃO promove ──────────────────
print('\npaís — LOCAL_COUNTRY_PROVED só com marca de país no IDENTIFICADOR:')
checa('SyngentaFrance -> FR local', ident.escopo('SyngentaFrance', 'FR')[0],
      'LOCAL_COUNTRY_PROVED')
checa('syngentaitalia grudado -> IT local', ident.escopo('syngentaitalia', 'IT')[0],
      'LOCAL_COUNTRY_PROVED')
checa('nufarmespana grudado -> ES local', ident.escopo('nufarmespana', 'ES')[0],
      'LOCAL_COUNTRY_PROVED')
checa('Bayer4CropsES por troca de caixa -> ES local',
      ident.escopo('Bayer4CropsES', 'ES')[0], 'LOCAL_COUNTRY_PROVED')

print('\n  os NEGATIVOS — cada um é um erro que a régua tem que recusar:')
checa('basf_global nunca vira local', ident.escopo('basf_global', 'IT')[0], 'GLOBAL')
checa('basf puro nao vira espanhol', ident.escopo('basf', 'ES')[0], 'NOT_KNOWN')
checa('nufarm puro nao vira frances', ident.escopo('nufarm', 'FR')[0], 'NOT_KNOWN')
checa('bayer-cropscience nao vira italiano (o it. era do LinkedIn)',
      ident.escopo('bayer-cropscience', 'IT')[0], 'NOT_KNOWN')
checa('SyngentaFrance NAO e conta espanhola',
      ident.escopo('SyngentaFrance', 'ES')[0], 'OTHER')
# `cropses` termina em "es" — e "es" tem duas letras, então NÃO vale grudado. Se
# valesse, "credit", "surf" e "cropses" virariam país. Esta é a linha que impede isso.
checa('marca de 2 letras NAO vale grudada no fim',
      ident.escopo('bayer4cropses', 'ES')[0], 'NOT_KNOWN')


# ── a promoção por irmão exige identidade EXATA, não semelhança ─────────────────
print('\npromoção por irmão — mesmo identificador, caixa diferente:')
contas = [
    ident._linha('BAYER', 'ES', 'FACEBOOK', 'u', {}, 'Bayer4CropsES', 'PROVED',
                 'LOCAL_COUNTRY_PROVED', 'e', 'e'),
    ident._linha('BAYER', 'ES', 'INSTAGRAM', 'u', {}, 'bayer4cropses', 'PROVED',
                 ident.NAO_SEI, 'e', 'e'),
    # semelhança NÃO é identidade: basf_agroes e basf.agro.espana sao contas DIFERENTES
    ident._linha('BASF', 'ES', 'FACEBOOK', 'u', {}, 'BASF.Agro.Espana', 'PROVED',
                 'LOCAL_COUNTRY_PROVED', 'e', 'e'),
    ident._linha('BASF', 'ES', 'INSTAGRAM', 'u', {}, 'basf_agroes', 'PROVED',
                 ident.NAO_SEI, 'e', 'e'),
]
ident.promover_por_irmao(contas)
checa('instagram bayer4cropses promovido pelo irmao do facebook',
      contas[1]['COUNTRY_SCOPE'], 'LOCAL_COUNTRY_PROVED')
checa('basf_agroes NAO e promovido por basf.agro.espana (nao e o mesmo handle)',
      contas[3]['COUNTRY_SCOPE'], ident.NAO_SEI)


# ── a coleta exige as DUAS perguntas ────────────────────────────────────────────
print('\nautorização de coleta — PROVED e LOCAL_COUNTRY, nunca uma só:')
checa('PROVED + GLOBAL nao autoriza',
      ident._linha('BASF', 'IT', 'INSTAGRAM', 'u', {}, 'basf_global', 'PROVED',
                   'GLOBAL', 'e', 'e')['COLLECTION_AUTHORIZED'], 'NO')
checa('CANDIDATE + LOCAL nao autoriza',
      ident._linha('X', 'ES', 'FACEBOOK', 'u', {}, 'xES', 'CANDIDATE',
                   'LOCAL_COUNTRY_PROVED', 'e', 'e')['COLLECTION_AUTHORIZED'], 'NO')
checa('PROVED + LOCAL + COMPANY autoriza',
      ident._linha('X', 'ES', 'FACEBOOK', 'u', {}, 'xES', 'PROVED',
                   'LOCAL_COUNTRY_PROVED', 'e', 'e')['COLLECTION_AUTHORIZED'], 'YES')

# ── O ERRO SEMANTICO QUE A ABA ARBITRA PEGOU ───────────────────────────────────
# PRODUCT nao e um estado de pais. A pagina DEKALB France tem o pais PROVADO e mesmo
# assim fica fora do lote COMPANY x COUNTRY — pelo PAPEL, nunca pela localidade.
print('\nPAGE_ROLE e COUNTRY_SCOPE sao eixos diferentes:')
dekalb = ident._linha('BAYER', 'FR', 'FACEBOOK', 'u', {}, 'dekalbfr', 'PROVED',
                      'LOCAL_COUNTRY_PROVED', 'e', 'e', papel='PRODUCT_BRAND')
checa('DEKALB France tem o pais PROVADO',
      dekalb['COUNTRY_SCOPE'], 'LOCAL_COUNTRY_PROVED')
checa('e mesmo assim NAO entra no lote COMPANY x COUNTRY',
      dekalb['ELIGIBLE_FOR_COMPANY_LOCAL_BATCH'], 'NO')
checa('e o motivo escrito e o PAPEL, nao o pais',
      len([r for r in dekalb['EXCLUSION_REASONS'] if 'MARCA/PRODUTO' in r]), 1)
# A assercao precisa e "nenhuma razao acusa o COUNTRY_SCOPE" — e nao "a palavra pais
# nao aparece". A razao do PAPEL cita "a empresa no país" legitimamente, e cacar a
# palavra reprovava um texto correto.
checa('nenhum motivo de exclusao acusa o COUNTRY_SCOPE',
      [r for r in dekalb['EXCLUSION_REASONS'] if 'COUNTRY_SCOPE=' in r], [])

# O oposto: papel de marca E pais nao provado. As DUAS razoes ficam escritas.
corteva = ident._linha('CORTEVA', 'FR', 'YOUTUBE', 'u', {}, 'CortevaBiologicals',
                       'PROVED', ident.NAO_SEI, 'e', 'e', papel='PRODUCT_BRAND')
checa('duas reprovacoes produzem DUAS razoes, nao uma',
      len(corteva['EXCLUSION_REASONS']), 2)

# Nenhum artefato desta missao pode criar ranking de prova que ninguem mediu.
print('\nnenhum ranking de prova inventado:')
import re as _re
_fonte = io.open(os.path.join(ROOT, 'scripts', 'comunicacao_identidade.py'),
                 encoding='utf-8').read()
checa('nao existe "prova mais forte" no codigo',
      bool(_re.search(r'(mais forte|melhor prova|prova mais)', _fonte)), False)


# ── nenhuma empresa nos dois lados da lista ─────────────────────────────────────
print('\nuniverso — "vou coletar" e "não tentei" não podem se sobrepor:')
u = uni.montar()
checa('nenhuma empresa no lote E fora do lote',
      sorted(set(u['FIRST_BATCH_COMPANIES']) & set(u['OUT_OF_FIRST_BATCH'])), [])
# EMPTY_SET != PROVEN_NO. O crosswalk que alimenta o universo nao e versionado nesta
# arvore, entao `CELLS` sai vazio e o conjunto de estados sai vazio junto. Comparar
# `set()` com `{'NO'}` publicava um VERMELHO PERMANENTE que soava como "alguma casa
# nasce autorizada" quando o que havia era "nao ha casa nenhuma para julgar" — e como
# este ficheiro morre na importacao, o vermelho ficava invisivel nos dois harnesses.
if u['CELLS']:
    checa('nenhuma casa nasce autorizada',
          {c['COLLECTION_AUTHORIZED'] for c in u['CELLS']}, {'NO'})
else:
    # A ausencia tem de ser a razao DECLARADA. Se o crosswalk aparecer e as casas
    # continuarem zero, isto volta a reprovar.
    checa('nenhuma casa nasce autorizada — nao ha casas, e o motivo e o crosswalk ausente',
          os.path.exists(uni.CROSSWALK), False)


# ── classificação: o país do fato vem do TEXTO, nunca da conta nem da língua ────
print('\nclassificação — COUNTRY_OF_FACT só quando o texto nomeia o lugar:')
post_es = cl.classificar({
    'TITLE': 'Nuevo fungicida para el repilo del olivo',
    'TEXT': 'Jornada tecnica en Jaen sobre el control del repilo en el olivar.',
    'COUNTRY_SCOPE': 'ES'})
checa('cultura lida do texto', post_es['CROP'], ['OLIVE'])
checa('problema lido do texto', post_es['ISSUE'], ['REPILO'])
checa('pais do fato lido do texto', post_es['COUNTRY_OF_FACT'], 'ES')
checa('mais de um tipo ao mesmo tempo',
      sorted(post_es['COMMUNICATION_TYPES']),
      ['FIELD_EVENT', 'PRODUCT_COMMUNICATION'])

# O caso que a doutrina exige: conta espanhola, post que NÃO fala da Espanha.
post_berlim = cl.classificar({
    'TITLE': 'Resultados del grupo',
    'TEXT': 'Presentamos nuestros resultados anuales y nuestra inversion en I+D.',
    'COUNTRY_SCOPE': 'ES'})
checa('conta espanhola NAO faz o fato ser espanhol',
      post_berlim['COUNTRY_OF_FACT'], cl.NAO_SEI)
checa('tipo corporativo reconhecido',
      post_berlim['COMMUNICATION_TYPES'], ['CORPORATE_COMMUNICATION'])

sem_texto = cl.classificar({'TITLE': cl.NAO_SEI, 'TEXT': cl.NAO_SEI,
                            'COUNTRY_SCOPE': 'FR'})
checa('sem texto -> NOT_KNOWN, e nao OTHER',
      sem_texto['COMMUNICATION_TYPES'], [cl.NAO_SEI])
checa('sem texto -> TEXT_AVAILABLE=NO', sem_texto['TEXT_AVAILABLE'], 'NO')

post_fr = cl.classificar({
    'TITLE': 'Webinaire mildiou de la vigne',
    'TEXT': 'Rejoignez notre webinaire sur le mildiou de la vigne en Bourgogne.',
    'COUNTRY_SCOPE': 'FR'})
# "Rejoignez notre webinaire" NÃO é vaga de emprego. A primeira versão da tabela listava
# "rejoignez" sozinho e classificava este post como RECRUITMENT_HR — o verbo de convite é
# o mesmo para chamar para o webinário e para chamar para o time.
checa('convite a webinario NAO e vaga de emprego',
      sorted(post_fr['COMMUNICATION_TYPES']), ['WEBINAR'])
checa('vaga de verdade continua sendo lida',
      cl.classificar({'TITLE': '', 'TEXT': 'Rejoignez notre equipe en Occitanie.',
                      'COUNTRY_SCOPE': 'FR'})['COMMUNICATION_TYPES'],
      ['RECRUITMENT_HR'])
checa('cultura francesa', post_fr['CROP'], ['VINE'])
checa('problema frances', post_fr['ISSUE'], ['DOWNY_MILDEW'])
checa('regiao nomeada -> FR', post_fr['COUNTRY_OF_FACT'], 'FR')

checa('esta camada nunca cria ID de produto',
      post_es['FORESIGHT_PRODUCT_ID'], cl.NAO_SEI)


print('\n' + '=' * 60)
if FALHAS:
    print('%d FALHA(S):' % len(FALHAS))
    for f in FALHAS:
        print('  · %s' % f)
    raise SystemExit(1)
print('todas as regressoes passaram')
