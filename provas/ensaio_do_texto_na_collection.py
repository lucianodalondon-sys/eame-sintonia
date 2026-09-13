#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COL-E7-01 — O ENSAIO DO TEXTO A ATRAVESSAR A COLLECTION REAL.

    python3 provas/ensaio_do_texto_na_collection.py

A pergunta é a que ficou aberta quando a `SCRAP-MORNING-01` mediu E1–E6 a
passar e E7 a parar:

    A EVIDÊNCIA TEXTUAL ATRAVESSA A COLLECTION SEM PERDER A ESPÉCIE —
    E, SE NÃO ATRAVESSA, ONDE É QUE A ESPÉCIE SE PERDE?

O QUE ISTO NÃO FAZ, E É METADE DA PROVA
----------------------------------------
Não faz rede, não corre SCRAP, não escreve no checkout. A entrada é CONTROLADA
e equivalente à que o SCRAP produz — a mesma forma de unidade de colheita que
`coleta/scrap_colheita.py::unidade()` monta — e o código que corre sobre ela é
o código REAL da Collection: `leis/retorno_da_coleta.py`, `coleta/ingresso.py`,
`admissao/admissao.py`.

    UM ENVELOPE É DADOS. LEVAR DADOS NÃO É MERGEAR CÓDIGO.

⚠️ O ARMAZÉM É DESCARTÁVEL, E ISSO É LEI E NÃO CUIDADO.
A primeira versão da sonda do lado do SCRAP passou `raiz=RAIZ` ao ingresso e
escreveu CINCO observações dentro do checkout que estava a ler.

    UMA PROVA QUE ESCREVE NA ÁRVORE QUE LÊ MEDE A ÁRVORE QUE ELA MUDOU.

OS QUATRO CASOS, E POR QUE SÃO ESTES
-------------------------------------
Cada um é uma espécie que um produtor REAL desta árvore põe hoje no mesmo campo
`TEXT` — e o ensaio pergunta se ela chega do outro lado ainda a ser ela:

    CASE 1  AUTHOR_TEXT     `bluesky_feed_autor` -> `record.text`
    CASE 2  NATIVE_CAPTION  a legenda que a plataforma serve, com a tradução ao lado
    CASE 3  TRANSCRIPT/ASR  `adaptador_youtube` -> `it['transcript']`
    CASE 4  UNKNOWN         envelope legado, que só tem `TEXT`

    REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0
"""
import json
import os
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                              # noqa: E402,F401

import admissao as adm                                       # noqa: E402
import ingresso as ing                                       # noqa: E402
import proveniencia as pv                                    # noqa: E402
import retorno_da_coleta as rdc                              # noqa: E402
import social_envelope as env                                # noqa: E402

RUN_ID = 'COL-E7-ENSAIO'
FONTE = 'IT-T9-001'


# ── A ENTRADA CONTROLADA, NA FORMA EXACTA QUE O SCRAP PRODUZ ───────────────
#: `coleta/scrap_colheita.py::DO_SCRAP_PARA_A_PORTA`, medido em
#: `claude/sintonia-scrap-release-candidate-v1` @ de38f816. A linha do texto é a
#: que esta missão acrescenta — e está aqui em vez de na branch do SCRAP porque
#: a branch do SCRAP não se toca.
DO_SCRAP_PARA_A_PORTA = {
    'URL': 'SOURCE_URL',
    'COUNTRY_SCOPE': 'COUNTRY_SCOPE',
    'SOURCE_LOCATION': 'SOURCE_LOCATION',
    'LANGUAGE': 'ITEM_LANGUAGE',
    'PUBLISHED_AT': 'PUBLISHED_AT',
    'COLLECTED_AT': 'OBSERVED_AT',
}
DESCONHECIDO = 'UNKNOWN'


def _limpo(v):
    s = str(v or '').strip()
    return None if not s or s in (DESCONHECIDO, rdc.NAO_SEI) else v


def unidade_de_colheita(objeto):
    """Um objeto social na língua da porta — a unidade de COLHEITA do SCRAP."""
    fora = {'ESPECIE': rdc.COLHEITA, 'RUN_ID': RUN_ID, 'SOURCE_ID': FONTE,
            'DOCUMENT_ID': rdc.NAO_SEI}
    for de, para in DO_SCRAP_PARA_A_PORTA.items():
        v = _limpo(objeto.get(de))
        if v is not None:
            fora[para] = v
    # ⚠️ A LINHA QUE FALTAVA, E O ENSAIO INTEIRO É SOBRE ELA.
    # A evidência textual sobe para o topo da unidade com espécie e linhagem —
    # pelo dono do contrato, e não por um mapeamento escrito aqui à mão.
    fora[pv.CAMPO_DAS_UNIDADES] = pv.unidades_do_envelope(objeto)
    fora['OBSERVACAO'] = objeto
    fora['PAYLOAD'] = {'ONDE': '', 'ESTADO': rdc.PAYLOAD_NAO_SE_APLICA}
    return fora


def envelope_da_corrida(objetos):
    return {'RUN_ID': RUN_ID, 'EXECUTOR_ID': 'coleta/scrap_colheita.py',
            'EXECUTOR_VERSION': 'ensaio', 'ESTADO': rdc.SUCCESS,
            'COLHEITA': [unidade_de_colheita(o) for o in objetos],
            'SUPORTE': [], 'ERROS': []}


# ══════════════════════════════════════════════════════════════════════════
# OS QUATRO CASOS
# ══════════════════════════════════════════════════════════════════════════
def caso_1_autor():
    """O que o autor escreveu, lido do campo que a API serve."""
    return env.envelope(
        platform='BLUESKY', native_id='at://did:plc:x/app.bsky.feed.post/1',
        url='https://bsky.app/profile/caasrl.bsky.social/post/1',
        content_type='POST', route='bsky:app.bsky.feed.getAuthorFeed',
        executor='social_rotas.bluesky_feed_autor', run_id=RUN_ID,
        country_scope='IT', source_account='caasrl.bsky.social',
        published_at='2026-09-01T10:00:00Z', language='it',
        text='convegno sulla ricerca in campo, articolo pubblicato',
        text_kind=pv.AUTHOR_TEXT, text_kind_basis=pv.DECLARED_BY_ROUTE,
        text_relation=pv.ORIGINAL, text_language='it',
        text_derivation=pv.LIDO_DO_CAMPO)


def caso_2_legenda():
    """A legenda da plataforma, E a tradução dela ao lado — as duas na mesma."""
    original = pv.unidade_de_texto(
        texto='convegno sulla sperimentazione in campo, studio pubblicato',
        kind=pv.NATIVE_CAPTION, kind_basis=pv.DECLARED_BY_PROVIDER,
        relation=pv.ORIGINAL, language='it', unit_id='TU-1',
        source_artifact='https://www.youtube.com/watch?v=ABC',
        derivation_method=pv.LIDO_DO_CAMPO)
    traducao = pv.unidade_de_texto(
        texto='conference on field trials, study published',
        kind=pv.NATIVE_CAPTION, kind_basis=pv.DECLARED_BY_PROVIDER,
        relation=pv.TRANSLATED, language='en', unit_id='TU-2',
        translated_from='TU-1',
        source_artifact='https://www.youtube.com/watch?v=ABC',
        derivation_method=pv.TRADUCAO_DO_PROVEDOR, tool='youtube:captions')
    return env.envelope(
        platform='YOUTUBE', native_id='ABC',
        url='https://www.youtube.com/watch?v=ABC', content_type='VIDEO',
        route='youtube-data-api-v3:captions.download',
        executor='youtube_oficial.legendas', run_id=RUN_ID, country_scope='IT',
        source_account='UCxyz', published_at='2026-09-02T10:00:00Z',
        language='it',
        # ⚠️ A TRADUÇÃO VEM PRIMEIRO NA LISTA, DE PROPÓSITO.
        # Se a regra de escolha fosse «o primeiro», este caso passaria a inglês
        # e ninguém veria. É o ataque nº 15 escrito como entrada.
        text_units=[traducao, original])


def caso_3_transcricao():
    """A FALA — transcrita por terceiro, sem língua e sem relação declaradas."""
    return env.envelope(
        platform='YOUTUBE', native_id='DEF',
        url='https://www.youtube.com/watch?v=DEF', content_type='VIDEO',
        route='apify:pintostudio~youtube-transcript-scraper',
        executor='adaptador_youtube.youtube_legenda_paga', run_id=RUN_ID,
        country_scope='IT', published_at='2026-09-03T10:00:00Z',
        # O actor não devolve língua nenhuma — medido na C6, `NÃO SEI` em 48 de
        # 48. O que ele devolve é um campo chamado `transcript`, e é só isso que
        # se declara: a espécie, pela rota; a relação, por ninguém.
        text='welcome back to issue 18 of the periodical',
        text_kind=pv.TRANSCRIPT, text_kind_basis=pv.DECLARED_BY_ROUTE,
        text_relation=pv.TEXTO_DESCONHECIDO,
        text_derivation=pv.ASR_DO_PROVEDOR,
        text_tool='apify:pintostudio~youtube-transcript-scraper')


def caso_4_desconhecido():
    """O envelope legado: só tem `TEXT`, e ninguém disse o que ele é."""
    e = env.envelope(
        platform='TELEGRAM', native_id='canal/42',
        url='https://t.me/canal/42', content_type='POST',
        route='telegram:t.me/s/{canal}', executor='social_rotas.telegram_canal',
        run_id=RUN_ID, country_scope='IT', published_at='2026-09-04T10:00:00Z',
        language='it', text='un testo qualunque senza parole conosciute')
    # Reescrito à mão para a forma ANTIGA: sem `TEXT_UNITS`, como os envelopes
    # que já estão em disco. A ponte do legado tem de o ver e NÃO o promover.
    e.pop(pv.CAMPO_DAS_UNIDADES)
    return e


CASOS = (
    ('CASE_1_AUTHOR_TEXT', caso_1_autor, pv.AUTHOR_TEXT, pv.ORIGINAL, 'it'),
    ('CASE_2_NATIVE_CAPTION', caso_2_legenda, pv.NATIVE_CAPTION, pv.ORIGINAL, 'it'),
    ('CASE_3_TRANSCRIPT', caso_3_transcricao, pv.TRANSCRIPT,
     pv.TEXTO_DESCONHECIDO, pv.TEXTO_DESCONHECIDO),
    ('CASE_4_UNKNOWN', caso_4_desconhecido, pv.TEXTO_DESCONHECIDO,
     pv.TEXTO_DESCONHECIDO, pv.TEXTO_DESCONHECIDO),
)


def atravessar(objeto, banco):
    """Corre a cadeia REAL da Collection sobre um objeto. → as arestas."""
    fora = []

    def caso(nome, ok, porque=''):
        fora.append({'ARESTA': nome, 'OK': bool(ok), 'PORQUE': porque})

    envelope = envelope_da_corrida([objeto])
    mal = rdc.conferir(envelope, banco)
    caso('E1_o_contrato_da_collection_aceita_o_envelope', not mal, '; '.join(mal[:3]))

    itens = rdc.so_o_que_entra(envelope)
    caso('E2_a_lei_deixa_passar_a_colheita', len(itens) == len(envelope['COLHEITA']),
         '%d de %d' % (len(itens), len(envelope['COLHEITA'])))

    recibo = {'RUN_ID': RUN_ID, 'PLATFORM': objeto.get('PLATFORM'),
              'ACTOR': 'provas/ensaio_do_texto_na_collection.py',
              'ACTOR_VERSION': 'ensaio', 'SOURCE_COUNTRY': 'IT',
              'STARTED_AT': '2026-09-13T00:00:00Z'}
    # ⚠️ UMA ARESTA, UM `try`. Um `except` que abrace várias reescreve o nome da
    # aresta onde se perdeu — e o nome da aresta é a resposta inteira.
    try:
        r = ing.receber(itens, corrida=recibo, armazem=ing.ArmazemLocal(banco),
                        memoria=None, raiz=banco)
    except Exception as e:                                       # noqa: BLE001
        caso('E3_o_ingresso_aceita_a_unidade', False,
             '%s: %s' % (type(e).__name__, str(e)[:200]))
        return fora
    aceitou = len(r['ACEITES']) == len(itens)
    caso('E3_o_ingresso_aceita_a_unidade', aceitou,
         '' if aceitou else json.dumps([x.get('DETALHE') for x in r['RECUSAS']])[:200])
    caso('E4_o_raw_foi_preservado', bool(r.get('RAW')),
         '' if r.get('RAW') else 'o ingresso nao devolveu recibo de RAW')

    unidade = (r.get('PARA_A_PORTA') or [None])[0]
    caso('E5_a_fronteira_devolve_a_unidade_canonica', unidade is not None,
         '' if unidade is not None else 'o ingresso nao entregou unidade')
    if unidade is None:
        return fora

    try:
        d = adm.decidir(unidade, 'T9', corrida=RUN_ID)
        caso('E6_a_admissao_julga_a_unidade', True,
             '%s · regra=%s' % (d.resultado, d.regra))
    except Exception as e:                                       # noqa: BLE001
        caso('E6_a_admissao_julga_a_unidade', False,
             '%s: %s' % (type(e).__name__, str(e)[:200]))

    # ── E7 · O TEXTO ATRAVESSA, E ATRAVESSA COM ESPÉCIE ────────────────────
    # ⚠️ NÃO BASTA HAVER TEXTO. A versão antiga desta aresta perguntava só
    # `bool(unidade.get('texto'))` — e com essa pergunta `texto = TEXT` teria
    # passado, com a espécie apagada e ninguém a ver.
    #
    #     UMA ARESTA QUE SÓ PERGUNTA PELO VALOR NÃO MEDE O CONTRATO.
    tem = bool(str(unidade.get('texto') or '').strip())
    especie = unidade.get('texto_especie')
    caso('E7_a_unidade_leva_texto_COM_ESPECIE_para_quem_julga',
         tem and especie in pv.TEXT_KINDS,
         'texto=%s · especie=%r · relacao=%r · lingua=%r'
         % ('SIM' if tem else 'NAO', especie, unidade.get('texto_relacao'),
            unidade.get('texto_lingua')))
    return fora, unidade


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 78)
    banco = tempfile.mkdtemp(prefix='col-e7-ensaio-')
    print('ARMAZEM_DESCARTAVEL = %s' % banco)
    print('ESCRITAS_NO_CHECKOUT = 0')

    perdidas, falhas = [], 0
    for nome, fabrica, kind_esperado, rel_esperada, lingua_esperada in CASOS:
        print('\n%s' % ('─' * 78))
        print('%s' % nome)
        saida = atravessar(fabrica(), banco)
        arestas, unidade = (saida if isinstance(saida, tuple) else (saida, None))
        primeira = None
        for c in arestas:
            print('   %-56s %s%s' % (c['ARESTA'], 'PASSA' if c['OK'] else 'PARA',
                                     ('  · ' + c['PORQUE']) if c['PORQUE'] else ''))
            if not c['OK'] and primeira is None:
                primeira = c['ARESTA']
        if primeira:
            perdidas.append((nome, primeira))
            falhas += 1
            continue
        # ── A ESPÉCIE CHEGOU A SER ELA MESMA? ─────────────────────────────
        obtido = (unidade.get('texto_especie'), unidade.get('texto_relacao'),
                  unidade.get('texto_lingua'))
        esperado = (kind_esperado, rel_esperada, lingua_esperada)
        ok = obtido == esperado
        print('   %-56s %s  · esperado=%s obtido=%s'
              % ('ESPECIE_PRESERVADA', 'PASSA' if ok else 'PARA',
                 esperado, obtido))
        if not ok:
            perdidas.append((nome, 'ESPECIE_PRESERVADA'))
            falhas += 1

    print('\n%s' % ('=' * 78))
    for nome, aresta in perdidas:
        print('PERDEU_EM  %-24s %s' % (nome, aresta))
    print('FIRST_LOST_EDGE = %s'
          % (perdidas[0][1] if perdidas else 'NENHUMA — o texto atravessa com especie'))
    print('TEXT_KIND_LOSS = %d' % falhas)
    print('REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
