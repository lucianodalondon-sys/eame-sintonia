#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CANAL E MERCADO — a prateleira de uma regiao, medida onde ela e declarada.

    py coleta/canal_mercado.py --coletar      baixa o bruto, preserva, carimba
    py coleta/canal_mercado.py --normalizar   cruza com o registro e escreve as tabelas
    py coleta/canal_mercado.py                as duas coisas, nesta ordem

POR QUE ESTE COLETOR EXISTE
---------------------------
O SINTONIA sabia ligar PROBLEMA -> PORTFOLIO. Nao sabia responder a pergunta seguinte,
que e a que o Field Sales faz primeiro: **onde esse portfolio efetivamente se move, e
onde nao se move.**

A resposta existe em fonte publica e obrigatoria, e ninguem tinha aberto: o D.Lgs
150/2012 art. 16 obriga todo titular de autorizacao de venda a declarar, uma vez por ano,
o que vendeu. O Veneto publica essa declaracao como open data CC BY 4.0, com
**numero de registrazione e provincia**. Cruzada com o registro do Ministero della Salute
(IT-T4-001), ela devolve, por territorio: quanto se vende, de que tipo, de que titular,
onde a ADAMA esta, e que parte do portfolio ativo NAO aparece ali.

AS LEIS QUE ESTE FICHEIRO OBEDECE, E ONDE ELAS DOEM
----------------------------------------------------
  · RAW ANTES DE PARSE. O ficheiro cru e escrito no collection-store, com sha256 no
    nome da versao, ANTES de qualquer leitura. Parse que acontece antes da gravacao
    produz numero sem documento por tras.
  · HTTP 200 NAO BASTA. A saude e decidida por SCHEMA e IDENTIDADE: cabecalho esperado,
    chave (provincia, numero de registro) presente, provincias dentro do conjunto do
    Veneto. Um 200 com pagina de erro reprova aqui.
  · LISTA VAZIA E FALHA. Zero linhas devolve FAILED, nunca "nenhuma venda".
  · VOLUME NAO E VALOR. O campo e kg/litro. Enxofre e cobre dominam o volume e custam
    pouco por quilo: quota em volume NAO e quota de mercado. O aviso viaja dentro de
    cada tabela gerada, nao so neste comentario.
  · AUSENCIA NA DECLARACAO NAO E AUSENCIA DE VENDA. Produto comprado fora da regiao e
    aplicado dentro nao aparece. Por isso a tabela de oportunidade se chama
    SEM_VENDA_DECLARADA, e nao "nao vendido".
  · EXTERNAL-ONLY (P-003). Nada aqui e dado interno da ADAMA. Sao declaracoes publicas
    de terceiros sobre produtos cujo titular e a ADAMA — e a distincao esta em D-027.

O QUE ESTE COLETOR NAO PROVA
----------------------------
quem comprou · qual revenda vendeu · preco · valor · cultura de destino · onde foi
aplicado · quota de mercado em valor. A fonte agrega por provincia: o nome do vendedor
e exatamente o campo que ela omite. Fechar isso exige outra porta — o catalogo de
metodos esta em research/veneto-clients/METODOS-PARA-LISTA-DE-COMPRADORES.md.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import proveniencia as pv  # noqa: E402

SOURCE_ID = 'IT-T10-001'
PAIS = 'italy'
REGIAO = 'Veneto'
PAGINA = 'https://www.arpa.veneto.it/dati-ambientali/open-data/fitosanitari'
ARQUIVO = ('https://www.arpa.veneto.it/dati-ambientali/open-data/file-e-allegati/'
           'vendite-fitosanitari/vendita_agrofarmaci_veneto_%d.csv/@@download/file')
REGISTRO = os.path.join(ROOT, 'data', 'collection-store', 'italy', 'IT-T4-001',
                        'MINSALUTE_FTS6_20260907', 'v1_9cd4d156369f',
                        'PROD_FTS_6_20260907.csv')
REGISTRO_SOURCE_ID = 'IT-T4-001'
STORE = os.path.join(ROOT, 'data', 'collection-store', PAIS, SOURCE_ID)
LEDGER = os.path.join(ROOT, 'data', 'collection-ledger', PAIS)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-VENETO-CANALE')
IMPORTACAO = os.path.join(ROOT, 'supabase', 'importacoes')

# As sete provincias do Veneto. Provincia fora deste conjunto e sinal de que a fonte
# mudou de escopo — nao de que apareceu uma provincia nova.
PROVINCIAS = ('BL', 'PD', 'RO', 'TV', 'VE', 'VI', 'VR')
CABECALHO_ESPERADO = ('provincia', 'n. reg.',
                      'prodotto fitosanitario venduto', 'quantita')

# TRES GERACOES DO MESMO FICHEIRO, e o contrato tem de ler as tres:
#   2015-2017  separador ';', decimal virgula, DUAS tabelas lado a lado (produto + SUBSTANCIA
#              ATIVA) e uma coluna a mais: a AZIENDA ULSS, que e geografia mais fina que a
#              provincia e e justamente quem licencia o vendedor;
#   2018-2022  separador ';', decimal virgula, uma tabela, sem ULSS;
#   2023-2025  separador ',', decimal ponto, cabecalho com ou sem 'di vendita'.
# Tratar o ponto de '1.173,00' como decimal divide o numero por mil; tratar a virgula de
# '30,00' como separador de milhar multiplica por cem. Por isso o decimal e decidido pelo
# SEPARADOR do ficheiro, nao por adivinhacao linha a linha.
# Estados administrativos que significam "existe autorizacao hoje".
ATIVO = ('autorizzato', 'ri-registrato')
ADAMA = re.compile(r'\bADAMA\b', re.I)

AVISO_VOLUME = ('quantidade e VOLUME FISICO (kg/l), nao valor. Enxofre e cobre dominam o '
                'volume do Veneto e custam pouco por quilo: quota em volume NAO e quota '
                'de mercado em valor. Quota em valor: NAO SEI.')
# O QUE FOI DEIXADO DE FORA, E POR QUE. Metade do que uma coleta aprende esta no descarte:
# sem isto, a proxima execucao repete o mesmo descarte sem saber que ele existiu.
MOTIVO_DA_RECUSA = {
    'RODAPE_DA_FONTE': 'linha de nota da propria fonte (base legal, aviso de carregamento) — nao e dado e nao e defeito',
    'SEM_NUMERO_DE_REGISTRO': 'linha sem numero de registrazione — sem a chave, nao cruza com o registro',
    'QUANTIDADE_ILEGIVEL': 'quantidade que nao converte para numero',
    'COLUNAS_DE_MENOS': 'linha com menos de 4 colunas',
}

AVISO_AUSENCIA = ('ausencia na declaracao NAO e ausencia de venda: produto comprado fora '
                  'da regiao e aplicado dentro nao aparece, e omissao de declarante e '
                  'possivel. Le-se "sem venda declarada", nunca "nao vendido".')


# ----------------------------------------------------------------- carimbos de data e lugar
def agora():
    """CAPTURED_AT em UTC com fuso explicito. Hora sem fuso e hora de lugar nenhum."""
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def egresso():
    """EGRESS_IP — por onde a requisicao saiu. Nao resolvendo, e NAO SEI, nunca em branco."""
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=15) as r:
            return r.read().decode().strip() or pv.NAO_SEI
    except Exception:
        return pv.NAO_SEI


def git_head():
    try:
        import subprocess
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                       text=True).strip()
    except Exception:
        return pv.NOT_PRESERVED


# ----------------------------------------------------------------- coleta
def baixar(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'SintoniaEAME/1.0 (coleta)'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), r.status


def assinatura(corpo):
    """Assinatura grosseira do conteudo. HTML devolvido no lugar de CSV reprova aqui."""
    cabeca = corpo[:400].lstrip().lower()
    if cabeca.startswith(b'<!doctype') or cabeca.startswith(b'<html'):
        return 'HTML'
    if b';' in cabeca or b',' in cabeca:
        return 'CSV'
    return 'DESCONHECIDO'


def _decodificar(corpo):
    """utf-8 primeiro; os ficheiros antigos da ARPAV sao cp1252 (o 'à' de Quantità)."""
    for cod in ('utf-8-sig', 'cp1252'):
        try:
            return corpo.decode(cod), cod
        except UnicodeDecodeError:
            continue
    return corpo.decode('utf-8', errors='replace'), 'utf-8/replace'


def _delimitador(texto):
    cabeca = '\n'.join(texto.splitlines()[:6])
    return ';' if cabeca.count(';') > cabeca.count(',') else ','


def _linha_do_cabecalho(linhas):
    """As geracoes antigas trazem uma ou duas linhas de TITULO antes do cabecalho."""
    for i, r in enumerate(linhas[:8]):
        campos = [_norm(c) for c in r]
        if any(c.startswith('provincia') for c in campos) and any('n. reg' in c for c in campos):
            return i
    return 0


def _norm(s):
    """Compara cabecalho sem acento e sem pontuacao: 'Quantita' e 'Quantità' sao o mesmo campo."""
    s = unicodedata.normalize('NFKD', (s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9 .]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def conferir(corpo):
    """SCHEMA + IDENTIDADE nas tres geracoes. Devolve (health, motivos, dados, provincias, rodape).

    A fonte termina com linhas de nota de rodape (a citacao da base legal e um aviso sobre
    o carregamento por ficheiro) e, nas geracoes antigas, COMECA com linhas de titulo. Nada
    disso e dado e nada disso e defeito: e separado, contado e preservado. Confundir moldura
    com linha ruim faz a saude da fonte mentir nos dois sentidos.
    """
    motivos = []
    if assinatura(corpo) != 'CSV':
        return 'FAILED', ['conteudo nao e CSV: %s' % assinatura(corpo)], [], [], []
    texto, codificacao = _decodificar(corpo)
    delim = _delimitador(texto)
    linhas = [r for r in csv.reader(io.StringIO(texto), delimiter=delim) if r]
    if len(linhas) < 2:
        return 'FAILED', ['lista vazia — e FALHA, nunca zero vendas'], [], [], []
    i = _linha_do_cabecalho(linhas)
    cab = [_norm(c) for c in linhas[i]]
    for esperado in CABECALHO_ESPERADO:
        if not any(esperado in c for c in cab):
            motivos.append('campo do contrato ausente no cabecalho: %r' % esperado)
    candidatas = [r for r in linhas[i + 1:] if len(r) >= 4]
    dados = [r for r in candidatas if r[0].strip() in PROVINCIAS]
    rodape = [r for r in candidatas if r[0].strip() not in PROVINCIAS]
    vistas = sorted({r[0].strip() for r in dados})
    faltando = [p for p in PROVINCIAS if p not in vistas]
    if faltando:
        motivos.append('provincia do Veneto sem nenhuma linha: %s' % faltando)
    chave = 1 if 'n. reg' in cab[1] else 2      # 2015-2017 tem a coluna AZIENDA ULSS no meio
    sem_chave = sum(1 for r in dados if len(r) <= chave or not r[chave].strip())
    if sem_chave:
        motivos.append('%d linhas sem numero de registro' % sem_chave)
    if len(rodape) > 5:
        motivos.append('%d linhas fora do conjunto de provincias — rodape demais para ser rodape'
                       % len(rodape))
    if not dados:
        return 'FAILED', motivos + ['nenhuma linha de dado'], [], vistas, rodape
    if any('campo do contrato ausente' in m for m in motivos):
        return 'FAILED', motivos, dados, vistas, rodape
    if codificacao != 'utf-8-sig':
        motivos.append('ficheiro em %s, nao utf-8 — lido, mas a fonte mudou de codificacao'
                       % codificacao)
    return ('DEGRADED' if motivos else 'HEALTHY'), motivos, dados, vistas, rodape


def esquema(corpo_ou_caminho):
    """Que geracao de ficheiro e esta. Devolve o mapa de colunas, medido e nao adivinhado."""
    if isinstance(corpo_ou_caminho, bytes):
        corpo = corpo_ou_caminho
    else:
        with open(corpo_ou_caminho, 'rb') as f:
            corpo = f.read()
    texto, codificacao = _decodificar(corpo)
    delim = _delimitador(texto)
    linhas = [r for r in csv.reader(io.StringIO(texto), delimiter=delim) if r]
    i = _linha_do_cabecalho(linhas)
    cab = [_norm(c) for c in linhas[i]]
    tem_ulss = len(cab) > 1 and 'ulss' in cab[1]
    subs = next((j for j, c in enumerate(cab) if 'sostanza attiva' in c), None)
    return {
        'CODIFICACAO': codificacao, 'DELIMITADOR': delim, 'DECIMAL_VIRGULA': delim == ';',
        'LINHA_DO_CABECALHO': i, 'CABECALHO': cab,
        'COL_PROVINCIA': 0, 'COL_ULSS': 1 if tem_ulss else None,
        'COL_REGISTRO': 2 if tem_ulss else 1,
        'COL_PRODUTO': 3 if tem_ulss else 2,
        'COL_QUANTIDADE': 4 if tem_ulss else 3,
        'COL_SUBSTANCIA': subs,
        'GERACAO': ('2015-2017 · com ULSS e tabela de substancia ativa' if tem_ulss
                    else '2018-2022 · ponto-e-virgula' if delim == ';'
                    else '2023-2025 · virgula'),
        'PRIMEIRA_LINHA_DE_DADO': i + 1,
    }


def coletar(ano):
    inicio = agora()
    ip = egresso()
    url = ARQUIVO % ano
    corpo, status = baixar(url)
    h = sha256(corpo)
    saude, motivos, dados, provincias, rodape = conferir(corpo)

    # RAW ANTES DE PARSE: o ficheiro cru vai para o disco antes de qualquer numero sair dele.
    doc_id = 'ARPAV_VENDITE_%d' % ano
    versao = 'v1_%s' % h[:12]
    destino = os.path.join(STORE, doc_id, versao)
    os.makedirs(destino, exist_ok=True)
    nome = 'vendita_agrofarmaci_veneto_%d.csv' % ano
    with open(os.path.join(destino, nome), 'wb') as f:
        f.write(corpo)
    caminho = os.path.relpath(os.path.join(destino, nome), ROOT).replace(os.sep, '/')
    fim = agora()

    run_id = 'IT-T10-%s' % datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H%M%S')
    obs = {
        'RUN_ID': run_id, 'SOURCE_ID': SOURCE_ID, 'SOURCE_URL': url,
        'DOCUMENT_ID': '%s:%d' % (doc_id, ano), 'DOCUMENT_VERSION_ID': versao,
        'RAW_SHA256': h, 'BYTES': len(corpo), 'MIME_ASSINATURA': assinatura(corpo),
        'HTTP_STATUS': status,
        'SOURCE_DATE': 'anno %d' % ano, 'SOURCE_DATE_ISO': '%d-12-31' % ano,
        'FACT_TIME': 'ano civil %d — a declaracao cobre as vendas do ano inteiro' % ano,
        'SOURCE_LOCATION': 'ARPAV (Padova) — publicacao regional',
        'FACT_LOCATION': 'Veneto, por provincia de venda',
        'CAPTURED_AT': fim, 'COLLECTION_RUN_STARTED_AT': inicio,
        'OBSERVATION_RESULT': 'BASELINE_DOCUMENT',
        'HEALTH_STATE': saude, 'HEALTH_REASONS': motivos,
        'CADENCE_STATE': 'UPDATED',
        'DECLARED_FREQUENCY': 'anual — declaracao ate 28/02 do ano seguinte (D.Lgs 150/2012 art. 16)',
        'OBSERVED_FREQUENCY': 'NAO SEI — primeira captura desta fonte nesta casa',
        'EXPECTED_NEXT_UPDATE': '%d-02-28' % (ano + 2),
        'RAW_OBJECT_CREATED': True, 'RAW_PATH': caminho, 'RAW_PRESERVED_BEFORE_PARSE': True,
        'DISCOVERY_DEGRADED': None, 'PARSE_ERROR': None,
        'LICENCA': 'CC BY 4.0',
        'EGRESS_IP': ip,
        'parse': {'LINHAS': len(dados), 'PROVINCIAS': provincias,
                  'REGISTROS_DISTINTOS': len({r[1].strip() for r in dados}),
                  'LINHAS_DE_RODAPE': len(rodape),
                  'EXCLUSION_REASON': 'RODAPE_DA_FONTE' if rodape else None,
                  'MOTIVO_DA_RECUSA': MOTIVO_DA_RECUSA['RODAPE_DA_FONTE'] if rodape else None,
                  'RODAPE_PRESERVADO': [' | '.join(c for c in r if c.strip()) for r in rodape]},
    }
    corrida = {
        'RUN_ID': run_id, 'STARTED_AT': inicio, 'FINISHED_AT': fim, 'IS_BASELINE': True,
        'nota_do_baseline': ('FIRST_RUN = BASELINE — esta execucao NAO pode dizer "mudou '
                            'desde o ano passado". Ela so estabelece o ponto de partida.'),
        'VPN_COUNTRY': pv.NAO_SEI, 'EGRESS_IP': ip,
        'COLLECTOR_VERSION': 'canal_mercado-v1', 'SOURCE_CONTRACT_VERSION': 'IT-T10-001-v1',
        'GIT_HEAD': git_head(),
        'contadores': {'SOURCES_ATTEMPTED': 1,
                       'HEALTHY': 1 if saude == 'HEALTHY' else 0,
                       'DEGRADED': 1 if saude == 'DEGRADED' else 0,
                       'FAILED': 1 if saude == 'FAILED' else 0,
                       'NEW_DOCUMENTS': 1, 'RAW_OBJECTS_CREATED': 1,
                       'ITEM_COUNT_RAW': len(dados)},
    }
    os.makedirs(LEDGER, exist_ok=True)
    for ficheiro, linha in (('observations.ndjson', obs), ('runs.ndjson', corrida)):
        with open(os.path.join(LEDGER, ficheiro), 'a', encoding='utf-8') as f:
            f.write(json.dumps(linha, ensure_ascii=False) + '\n')

    # O manifesto e escrito preservando as execucoes antigas COMO ELAS ESTAO.
    # `pv.gravar()` revalida a lista inteira, e as corridas anteriores a esta missao nao
    # passam no contrato de hoje: faltam campos e o STATUS delas e 'OK', que nao existe em
    # STATUS_RUN. Completar aquelas linhas seria inventar captura que nao houve, e traduzir
    # 'OK' para 'SUCCESS' seria interpretar execucao alheia. A divida fica visivel onde ja
    # esta — em tests/test_proveniencia.py — em vez de ser apagada por quem passou por aqui.
    meu = pv.novo_run(
        run_id, PLATFORM='open data regional (HTTP)', ACTOR='coleta/canal_mercado.py',
        ACTOR_VERSION='canal_mercado-v1', STARTED_AT=inicio, FINISHED_AT=fim,
        INPUT={'url': url, 'ano': ano, 'regiao': REGIAO}, COUNTRY='IT',
        MISSION='Canal e mercado regional', QUERY='venda declarada de fitossanitarios, %s %d' % (REGIAO, ano),
        DATASET_ID='%s:%s' % (SOURCE_ID, versao), ITEM_COUNT_RAW=len(dados),
        ITEM_COUNT_NORMALIZED=0, COST_USD=0, SOURCE_VERSION=versao,
        STATUS='SUCCESS' if saude != 'FAILED' else 'FAILED', ERROR='; '.join(motivos),
        CAPTURE_METHOD='gratuito', EVIDENCE_PATH=os.path.relpath(SAIDA, ROOT).replace(os.sep, '/'),
        RAW_EVIDENCE_PATH=caminho, RAW_EVIDENCE_STATE='PRESERVED', OUTPUT_WRITTEN_AT=fim)
    _anexar_ao_manifesto(meu, fim)

    print('COLETA %s · %s · %d linhas · sha %s · %s' % (saude, caminho, len(dados), h[:12], ip))
    if saude == 'FAILED':
        raise SystemExit('fonte reprovou no contrato: %s' % '; '.join(motivos))
    return {'RUN_ID': run_id, 'RAW_PATH': caminho, 'SHA256': h, 'BYTES': len(corpo),
            'ANO': ano, 'VERSAO': versao, 'HEALTH_STATE': saude, 'CAPTURED_AT': fim}


# ----------------------------------------------------------------- registro oficial
def ler_registro():
    """IT-T4-001 — o registro diz QUEM e o titular e QUE TIPO de produto e.

    Sem ele a declaracao de venda e uma lista de nomes comerciais: nao da para somar por
    empresa nem separar fungicida de herbicida.
    """
    reg = {}
    with open(REGISTRO, encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f, delimiter=';'):
            try:
                n = int(r['num_registrazione'])
            except (KeyError, ValueError):
                continue
            reg[n] = {
                'PRODUTO': (r.get('denominazione_prodotto') or '').strip(),
                'TITOLARE': _mojibake((r.get('ragione_sociale') or '').strip()),
                'TIPO': (r.get('attivita') or '').strip() or 'NAO DECLARADO',
                'SUBSTANCIAS': (r.get('sostanze_attive') or '').strip(),
                'ESTADO': (r.get('stato_amministrativo') or '').strip(),
                'VALIDADE': (r.get('data_scadenza_autorizzazione') or '').strip(),
                'FORMULACAO': (r.get('descrizione_formulazione') or '').strip(),
            }
    if not reg:
        raise SystemExit('registro vazio — e FALHA, nunca zero produtos')
    return reg


def _mojibake(s):
    """O registro oficial devolve latin-1 sobre utf-8 em alguns nomes (COOPERATIEF)."""
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def _quantidade(v, decimal_virgula=False):
    """O decimal e decidido pelo SEPARADOR do ficheiro, nunca por adivinhacao.

    ';'  -> convencao italiana: '1.173,00' e mil cento e setenta e tres.
    ','  -> '51401.35' e cinquenta e um mil, e nunca cinquenta e um milhoes.
    """
    v = (v or '').strip()
    if not v:
        return None
    if decimal_virgula:
        v = v.replace('.', '').replace(',', '.')
    try:
        return float(v)
    except ValueError:
        return None


# ----------------------------------------------------------------- normalizacao
def _ultima_coleta(ano):
    """Qual execucao produziu o bruto que estou lendo. Sem isto o RUN_ID vira 'NAO SEI'
    quando a normalizacao roda sozinha — e o dado perde o fio de volta para a fonte."""
    caminho = os.path.join(LEDGER, 'observations.ndjson')
    achado = None
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            for linha in f:
                try:
                    o = json.loads(linha)
                except ValueError:
                    continue
                if o.get('SOURCE_ID') == SOURCE_ID and o.get('SOURCE_DATE') == 'anno %d' % ano:
                    achado = o
    if not achado:
        return None
    return {'RUN_ID': achado['RUN_ID'], 'RAW_PATH': achado['RAW_PATH'],
            'SHA256': achado['RAW_SHA256'], 'BYTES': achado['BYTES'], 'ANO': ano,
            'VERSAO': achado['DOCUMENT_VERSION_ID'], 'HEALTH_STATE': achado['HEALTH_STATE'],
            'CAPTURED_AT': achado['CAPTURED_AT'],
            'NOTA': 'execucao recuperada do ledger — a normalizacao nao rodou junto com a coleta'}


def normalizar(ano, coleta_info=None):
    coleta_info = coleta_info or _ultima_coleta(ano)
    reg = ler_registro()
    bruto = _bruto_do_store(ano)
    esq, linhas, substancias, descartadas = _ler_linhas(bruto)
    orfaos = sum(1 for l in linhas if l['NUM_REGISTRAZIONE'] not in reg)

    total = sum(l['QUANTIDADE_KG_L'] for l in linhas)
    por_prov = _somar(linhas, lambda l: l['PROVINCIA'])
    por_reg = _somar(linhas, lambda l: l['NUM_REGISTRAZIONE'])
    por_prov_reg = _somar(linhas, lambda l: (l['PROVINCIA'], l['NUM_REGISTRAZIONE']))

    def tit(n):
        return reg[n]['TITOLARE'] if n in reg else 'NAO SEI'

    def tipo(n):
        return reg[n]['TIPO'] if n in reg else 'NAO SEI'

    def eh_adama(n):
        return bool(ADAMA.search(tit(n)))

    def ativo(n):
        return n in reg and reg[n]['ESTADO'].lower().startswith(ATIVO)

    # --- DIM TERRITORIO
    dim_territorio = [{
        'PROVINCIA': p, 'REGIAO': REGIAO, 'PAIS': 'IT', 'ANO': ano,
        'TOTAL_DECLARADO_KG_L': round(v, 2),
        'QUOTA_DA_REGIAO_PCT': round(100 * v / total, 2),
        'PRODUTOS_DISTINTOS': len({l['NUM_REGISTRAZIONE'] for l in linhas if l['PROVINCIA'] == p}),
        'TITULARES_DISTINTOS': len({tit(l['NUM_REGISTRAZIONE']) for l in linhas if l['PROVINCIA'] == p}),
    } for p, v in sorted(por_prov.items(), key=lambda x: -x[1])]

    # --- DIM PRODUTO (so o que foi efetivamente vendido)
    dim_produto = []
    for n, v in sorted(por_reg.items(), key=lambda x: -x[1]):
        nomes = {l['PRODUTO_NA_FONTE'] for l in linhas
                 if l['NUM_REGISTRAZIONE'] == n and l['PRODUTO_NA_FONTE']}
        base = reg.get(n, {})
        dim_produto.append({
            'NUM_REGISTRAZIONE': n,
            'PRODUTO': (sorted(nomes, key=len)[0] if nomes else base.get('PRODUTO') or 'NAO SEI'),
            'PRODUTO_NO_REGISTRO': base.get('PRODUTO', 'NAO SEI'),
            'TITOLARE': tit(n), 'TIPO': tipo(n),
            'SUBSTANCIAS': base.get('SUBSTANCIAS', 'NAO SEI'),
            'ESTADO_ADMINISTRATIVO': base.get('ESTADO', 'NAO SEI'),
            'VALIDADE': base.get('VALIDADE', 'NAO SEI'),
            'E_ADAMA': eh_adama(n), 'VENDIDO_KG_L': round(v, 2),
            'POR_PROVINCIA': {p: round(q, 2) for (p, nn), q in
                              sorted(por_prov_reg.items(), key=lambda x: -x[1]) if nn == n},
        })

    # --- DIM TITOLARE (a marca, que e o que a inteligencia de mercado pergunta)
    por_tit = {}
    for l in linhas:
        t = tit(l['NUM_REGISTRAZIONE'])
        d = por_tit.setdefault(t, {'KG_L': 0.0, 'REGISTROS': set(), 'PROV': {}, 'TIPOS': {}})
        d['KG_L'] += l['QUANTIDADE_KG_L']
        d['REGISTROS'].add(l['NUM_REGISTRAZIONE'])
        d['PROV'][l['PROVINCIA']] = d['PROV'].get(l['PROVINCIA'], 0.0) + l['QUANTIDADE_KG_L']
        tp = tipo(l['NUM_REGISTRAZIONE'])
        d['TIPOS'][tp] = d['TIPOS'].get(tp, 0.0) + l['QUANTIDADE_KG_L']
    ordem_tit = sorted(por_tit.items(), key=lambda x: -x[1]['KG_L'])
    dim_titolare = [{
        'TITOLARE': t, 'POSICAO_NA_REGIAO': i, 'ANO': ano,
        'KG_L': round(d['KG_L'], 2), 'QUOTA_VOLUME_PCT': round(100 * d['KG_L'] / total, 2),
        'PRODUTOS_DISTINTOS': len(d['REGISTROS']), 'E_ADAMA': bool(ADAMA.search(t)),
        'POR_PROVINCIA': {p: round(v, 2) for p, v in sorted(d['PROV'].items(), key=lambda x: -x[1])},
        'POR_TIPO': {k: round(v, 2) for k, v in sorted(d['TIPOS'].items(), key=lambda x: -x[1])},
    } for i, (t, d) in enumerate(ordem_tit, 1)]

    # --- FATO FORCA DE MARCA: provincia x titular x tipo, com quota e posicao dentro do tipo
    forca = {}
    for l in linhas:
        k = (l['PROVINCIA'], tit(l['NUM_REGISTRAZIONE']), tipo(l['NUM_REGISTRAZIONE']))
        forca[k] = forca.get(k, 0.0) + l['QUANTIDADE_KG_L']
    tot_prov_tipo = {}
    for (p, t, tp), v in forca.items():
        tot_prov_tipo[(p, tp)] = tot_prov_tipo.get((p, tp), 0.0) + v
    ranking = {}
    for (p, t, tp), v in sorted(forca.items(), key=lambda x: -x[1]):
        ranking.setdefault((p, tp), []).append(t)
    fato_forca = [{
        'ANO': ano, 'PROVINCIA': p, 'TITOLARE': t, 'TIPO': tp,
        'KG_L': round(v, 2),
        'QUOTA_NO_TIPO_E_PROVINCIA_PCT': round(100 * v / tot_prov_tipo[(p, tp)], 2),
        'POSICAO_NO_TIPO_E_PROVINCIA': ranking[(p, tp)].index(t) + 1,
        'CONCORRENTES_NO_TIPO_E_PROVINCIA': len(ranking[(p, tp)]),
        'E_ADAMA': bool(ADAMA.search(t)),
    } for (p, t, tp), v in sorted(forca.items(), key=lambda x: (x[0][0], -x[1]))]

    # --- FATO OPORTUNIDADE: portfolio ADAMA ativo SEM venda declarada naquela provincia
    adama_ativos = {n for n in reg if eh_adama(n) and ativo(n)}
    vendidos_prov = {}
    for l in linhas:
        vendidos_prov.setdefault(l['PROVINCIA'], set()).add(l['NUM_REGISTRAZIONE'])
    vendidos_regiao = {n for n in por_reg}
    fato_oport = []
    for p in [t['PROVINCIA'] for t in dim_territorio]:
        for n in sorted(adama_ativos, key=lambda x: -por_reg.get(x, 0)):
            if n in vendidos_prov.get(p, set()):
                continue
            fato_oport.append({
                'ANO': ano, 'PROVINCIA': p, 'NUM_REGISTRAZIONE': n,
                'PRODUTO': reg[n]['PRODUTO'], 'TITOLARE': reg[n]['TITOLARE'],
                'TIPO': reg[n]['TIPO'], 'VALIDADE': reg[n]['VALIDADE'],
                'ESTADO': 'SEM_VENDA_DECLARADA_NESTA_PROVINCIA',
                'VENDIDO_NO_RESTO_DA_REGIAO_KG_L': round(por_reg.get(n, 0.0), 2),
                'CLASSE': ('VENDE_NA_REGIAO_MAS_NAO_AQUI' if n in vendidos_regiao
                           else 'SEM_VENDA_DECLARADA_EM_TODA_A_REGIAO'),
            })

    # --- PACOTE DO RTV: o rollup legivel, provincia a provincia
    pacote = {}
    for t in dim_territorio:
        p = t['PROVINCIA']
        ad = [d for d in dim_titolare if d['E_ADAMA'] and p in d['POR_PROVINCIA']]
        tipos = {}
        for l in linhas:
            if l['PROVINCIA'] == p:
                tipos[tipo(l['NUM_REGISTRAZIONE'])] = tipos.get(tipo(l['NUM_REGISTRAZIONE']), 0.0) + l['QUANTIDADE_KG_L']
        top = [d for d in dim_titolare if p in d['POR_PROVINCIA']]
        top.sort(key=lambda d: -d['POR_PROVINCIA'][p])
        aqui = [o for o in fato_oport if o['PROVINCIA'] == p]
        pacote[p] = {
            'TOTAL_DECLARADO_KG_L': t['TOTAL_DECLARADO_KG_L'],
            'MIX_POR_TIPO': {k: round(v, 2) for k, v in sorted(tipos.items(), key=lambda x: -x[1])[:6]},
            'TOP_TITOLARI': [{'TITOLARE': d['TITOLARE'], 'KG_L': d['POR_PROVINCIA'][p],
                              'QUOTA_PCT': round(100 * d['POR_PROVINCIA'][p] / t['TOTAL_DECLARADO_KG_L'], 2)}
                             for d in top[:6]],
            'ADAMA_KG_L': round(sum(d['POR_PROVINCIA'][p] for d in ad), 2),
            'ADAMA_QUOTA_PCT': round(100 * sum(d['POR_PROVINCIA'][p] for d in ad) / t['TOTAL_DECLARADO_KG_L'], 2),
            'ADAMA_POR_TITULAR': {d['TITOLARE']: d['POR_PROVINCIA'][p] for d in ad},
            'ADAMA_TOP_PRODUTOS': [{'PRODUTO': x['PRODUTO'], 'REG': x['NUM_REGISTRAZIONE'],
                                    'TIPO': x['TIPO'], 'KG_L': x['POR_PROVINCIA'][p]}
                                   for x in dim_produto if x['E_ADAMA'] and p in x['POR_PROVINCIA']][:5],
            'OPORTUNIDADES': {
                'VENDE_NA_REGIAO_MAS_NAO_AQUI': len([o for o in aqui if o['CLASSE'] == 'VENDE_NA_REGIAO_MAS_NAO_AQUI']),
                'SEM_VENDA_EM_TODA_A_REGIAO': len([o for o in aqui if o['CLASSE'] == 'SEM_VENDA_DECLARADA_EM_TODA_A_REGIAO']),
                'PRIMEIRAS': [{'PRODUTO': o['PRODUTO'], 'TIPO': o['TIPO'],
                               'KG_L_NO_RESTO_DA_REGIAO': o['VENDIDO_NO_RESTO_DA_REGIAO_KG_L']}
                              for o in aqui[:5]],
            },
        }

    cab = {'FONTE_VENDA': SOURCE_ID, 'FONTE_REGISTRO': REGISTRO_SOURCE_ID, 'ANO': ano,
           'REGIAO': REGIAO, 'GERADO_EM': agora(), 'GERADO_POR': 'coleta/canal_mercado.py',
           'AVISO_VOLUME': AVISO_VOLUME}
    tabelas = {
        'DIM-TERRITORIO': dict(cab, LINHAS=len(dim_territorio), DADOS=dim_territorio),
        'DIM-TITOLARE': dict(cab, LINHAS=len(dim_titolare), DADOS=dim_titolare),
        'DIM-PRODUTO': dict(cab, LINHAS=len(dim_produto), DADOS=dim_produto),
        'FATO-VENDA-DECLARADA': dict(cab, LINHAS=len(linhas),
                                     ORFAOS_NO_REGISTRO=orfaos,
                                     DESCARTADAS=len(descartadas),
                                     O_QUE_FOI_DESCARTADO_E_POR_QUE=descartadas,
                                     DADOS=[dict(l, ANO=ano) for l in linhas]),
        'FATO-FORCA-DE-MARCA': dict(cab, LINHAS=len(fato_forca), DADOS=fato_forca),
        'FATO-OPORTUNIDADE': dict(cab, AVISO_AUSENCIA=AVISO_AUSENCIA,
                                  LINHAS=len(fato_oport), DADOS=fato_oport),
        'PACOTE-RTV-POR-PROVINCIA': dict(cab, AVISO_AUSENCIA=AVISO_AUSENCIA, PROVINCIAS=pacote),
    }
    os.makedirs(SAIDA, exist_ok=True)
    escritos = {}
    for nome, corpo in tabelas.items():
        caminho = os.path.join(SAIDA, nome + '.json')
        texto = json.dumps(corpo, ensure_ascii=False, indent=1)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto)
        escritos[nome] = {'LINHAS': corpo.get('LINHAS', len(pacote)),
                          'SHA256': sha256(texto.encode('utf-8')),
                          'BYTES': len(texto.encode('utf-8'))}

    manifesto = {
        'ARTIFACT_ID': 'IT-VENETO-CANAL-MANIFESTO-DAS-TABELAS', 'ANO': ano, 'REGIAO': REGIAO,
        'GERADO_EM': agora(), 'GERADO_POR': 'coleta/canal_mercado.py',
        'COLETA': coleta_info or 'NAO SEI — nao ha coleta desta fonte e ano no ledger',
        'FONTES': {
            SOURCE_ID: {'NOME': 'ARPAV — Vendite fitosanitari (open data)', 'PAGINA': PAGINA,
                        'LICENCA': 'CC BY 4.0',
                        'BASE_LEGAL': 'D.Lgs 150/2012 art. 16 — declaracao anual obrigatoria'},
            REGISTRO_SOURCE_ID: {'NOME': 'Ministero della Salute — banca dati prodotti fitosanitari',
                                 'SNAPSHOT': os.path.relpath(REGISTRO, ROOT).replace(os.sep, '/')},
        },
        'CHAVE_DO_CRUZAMENTO': 'num_registrazione (exata) + provincia',
        'QA': {'LINHAS_LIDAS': len(linhas),
               'DESCARTADAS': len(descartadas),
               'DESCARTE_POR_MOTIVO': {m: len([d for d in descartadas if d['EXCLUSION_REASON'] == m])
                                       for m in sorted({d['EXCLUSION_REASON'] for d in descartadas})},
               'ORFAOS_NO_REGISTRO': orfaos,
               'COBERTURA_DO_REGISTRO_PCT': round(100 * (1 - orfaos / max(len(linhas), 1)), 2),
               'TOTAL_KG_L': round(total, 2)},
        'AVISOS': [AVISO_VOLUME, AVISO_AUSENCIA,
                   'nenhuma linha aqui e dado interno da ADAMA (P-003 EXTERNAL-ONLY; ver D-027)'],
        'TABELAS': escritos,
        'O_QUE_NAO_PROVA': ['quem comprou', 'qual revenda vendeu', 'preco ou valor',
                            'cultura de destino', 'onde foi aplicado', 'quota em valor'],
    }
    with open(os.path.join(SAIDA, 'MANIFESTO-DAS-TABELAS.json'), 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=1)

    print('NORMALIZACAO · %d linhas · %d descartadas · %d titulares · %d produtos · '
          '%d oportunidades · orfaos %d'
          % (len(linhas), len(descartadas), len(dim_titolare), len(dim_produto),
             len(fato_oport), orfaos))
    return manifesto


def emitir_sql(ano):
    """Gera a importacao para o Supabase a partir das tabelas — deterministica.

    NAO EXECUTA: as credenciais sao secrets do GitHub Actions e nao existem na sessao de
    coleta. O ficheiro fica em supabase/importacoes/ para o aplicador da cadeia canonica.
    """
    def ler(nome):
        with open(os.path.join(SAIDA, nome + '.json'), encoding='utf-8') as f:
            return json.load(f)

    def txt(v):
        if v is None or v == '':
            return 'null'
        return "'" + str(v).replace("'", "''") + "'"

    venda = ler('FATO-VENDA-DECLARADA')
    forca = ler('FATO-FORCA-DE-MARCA')
    oport = ler('FATO-OPORTUNIDADE')
    manifesto = ler('MANIFESTO-DAS-TABELAS')
    coleta = manifesto.get('COLETA')
    run_id = coleta.get('RUN_ID', pv.NAO_SEI) if isinstance(coleta, dict) else pv.NAO_SEI

    linhas = ['-- ' + '=' * 69,
              '-- IT_VENETO_CANAL_IMPORT_V1 — venda declarada, forca de marca e oportunidade',
              '--',
              '-- Gerado por coleta/canal_mercado.py --sql. Deterministico.',
              '-- Requer a migration 022_canal_prateleira_e_comprador.sql aplicada.',
              '--',
              '-- NAO EXECUTADO nesta sessao: as credenciais do Supabase sao secrets do',
              '-- GitHub Actions e nao existem aqui.',
              '--',
              '-- AVISO QUE VIAJA COM O DADO: ' + AVISO_VOLUME,
              '-- ' + AVISO_AUSENCIA,
              '-- ' + '=' * 69,
              'begin;',
              '',
              '-- 1 · VENDA DECLARADA (%d linhas)' % venda['LINHAS']]
    for d in venda['DADOS']:
        linhas.append(
            'insert into public.canal_venda_declarada '
            '(fonte_source_id, run_id, ano, regiao, provincia, num_registrazione, '
            'produto_na_fonte, quantidade) values '
            '(%s, %s, %d, %s, %s, %d, %s, %s) on conflict do nothing;'
            % (txt(SOURCE_ID), txt(run_id), ano, txt(REGIAO), txt(d['PROVINCIA']),
               d['NUM_REGISTRAZIONE'], txt(d['PRODUTO_NA_FONTE']), repr(d['QUANTIDADE_KG_L'])))
    linhas += ['', '-- 2 · FORCA DE MARCA (%d linhas)' % forca['LINHAS']]
    for d in forca['DADOS']:
        linhas.append(
            'insert into public.canal_forca_de_marca '
            '(ano, regiao, provincia, titolare, tipo, quantidade, quota_volume_pct, '
            'posicao, concorrentes, e_adama) values '
            '(%d, %s, %s, %s, %s, %s, %s, %d, %d, %s) on conflict do nothing;'
            % (ano, txt(REGIAO), txt(d['PROVINCIA']), txt(d['TITOLARE']), txt(d['TIPO']),
               repr(d['KG_L']), repr(d['QUOTA_NO_TIPO_E_PROVINCIA_PCT']),
               d['POSICAO_NO_TIPO_E_PROVINCIA'], d['CONCORRENTES_NO_TIPO_E_PROVINCIA'],
               'true' if d['E_ADAMA'] else 'false'))
    linhas += ['', '-- 3 · OPORTUNIDADE (%d linhas)' % oport['LINHAS']]
    for d in oport['DADOS']:
        linhas.append(
            'insert into public.canal_oportunidade '
            '(ano, regiao, provincia, num_registrazione, produto, titolare, tipo, '
            'validade, classe, kg_no_resto_da_regiao) values '
            '(%d, %s, %s, %d, %s, %s, %s, %s, %s, %s) on conflict do nothing;'
            % (ano, txt(REGIAO), txt(d['PROVINCIA']), d['NUM_REGISTRAZIONE'],
               txt(d['PRODUTO']), txt(d['TITOLARE']), txt(d['TIPO']), txt(d['VALIDADE']),
               txt(d['CLASSE']), repr(d['VENDIDO_NO_RESTO_DA_REGIAO_KG_L'])))
    linhas += ['', 'commit;', '']

    os.makedirs(IMPORTACAO, exist_ok=True)
    destino = os.path.join(IMPORTACAO, 'IT-VENETO-CANAL-%s.sql' % agora()[:10])
    with open(destino, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas))
    print('SQL · %s · %d comandos' % (os.path.relpath(destino, ROOT),
                                      venda['LINHAS'] + forca['LINHAS'] + oport['LINHAS']))
    return destino


def serie(anos):
    """Puxa e mede varios anos. A serie e o que transforma uma foto em tendencia.

    ⚠️ O TITULAR E O DE HOJE, PROJETADO PARA TRAS. O registro que uso para dizer de quem e
    cada produto e o snapshot de 2026. Produto que mudou de dono entre 2015 e hoje aparece,
    em todos os anos, sob o dono ATUAL. Isso mede a evolucao do PORTFOLIO DE HOJE no tempo —
    e NAO mede que marca estava na prateleira naquele ano. Sao perguntas diferentes, e trocar
    uma pela outra produz uma serie confiante e errada.
    """
    reg = ler_registro()
    linhas_serie, por_ano = [], {}
    for ano in anos:
        try:
            bruto = _bruto_do_store(ano)
        except SystemExit:
            print('  %d · sem bruto preservado — pulado' % ano)
            continue
        total, prov, tit, tipo, adama_prod, ulss = 0.0, {}, {}, {}, {}, {}
        esq, registros, substancias, descartes = _ler_linhas(bruto)
        lidas, descartadas = len(registros), len(descartes)
        for l in registros:
            q = l['QUANTIDADE_KG_L']
            total += q
            prov[l['PROVINCIA']] = prov.get(l['PROVINCIA'], 0.0) + q
            if l['ULSS']:
                k = '%s-%s' % (l['PROVINCIA'], l['ULSS'])
                ulss[k] = ulss.get(k, 0.0) + q
            base = reg.get(l['NUM_REGISTRAZIONE'])
            nome_t = base['TITOLARE'] if base else 'NAO SEI (registro nao conhece %d)' % l['NUM_REGISTRAZIONE']
            tipo_t = base['TIPO'] if base else 'NAO SEI'
            tit[nome_t] = tit.get(nome_t, 0.0) + q
            tipo[tipo_t] = tipo.get(tipo_t, 0.0) + q
            if base and ADAMA.search(nome_t):
                kk = (l['NUM_REGISTRAZIONE'], base['PRODUTO'], tipo_t)
                adama_prod[kk] = adama_prod.get(kk, 0.0) + q
        adama = sum(v for k, v in tit.items() if ADAMA.search(k))
        por_ano[ano] = {
            'ANO': ano, 'LINHAS': lidas, 'DESCARTADAS': descartadas,
            'TOTAL_KG_L': round(total, 2),
            'ADAMA_KG_L': round(adama, 2),
            'ADAMA_QUOTA_PCT': round(100 * adama / total, 2) if total else 0,
            'TITULARES': len(tit), 'PRODUTOS_ADAMA_VENDIDOS': len(adama_prod),
            'POR_PROVINCIA': {k: round(v, 2) for k, v in sorted(prov.items())},
            'POR_TIPO': {k: round(v, 2) for k, v in sorted(tipo.items(), key=lambda x: -x[1])[:8]},
            'TOP_TITULARES': [{'TITOLARE': k, 'KG_L': round(v, 2),
                               'QUOTA_PCT': round(100 * v / total, 2)}
                              for k, v in sorted(tit.items(), key=lambda x: -x[1])[:15]],
            'ADAMA_POR_PRODUTO': [{'NUM_REGISTRAZIONE': n, 'PRODUTO': nm, 'TIPO': tp,
                                   'KG_L': round(v, 2)}
                                  for (n, nm, tp), v in sorted(adama_prod.items(), key=lambda x: -x[1])],
        }
        por_ano[ano]['ESQUEMA'] = {k: esq[k] for k in ('GERACAO', 'CODIFICACAO', 'DELIMITADOR',
                                                       'DECIMAL_VIRGULA', 'COL_ULSS', 'COL_SUBSTANCIA')}
        if ulss:
            por_ano[ano]['POR_ULSS'] = {k: round(v, 2) for k, v in sorted(ulss.items())}
        if substancias:
            agr = {}
            for s in substancias:
                agr[s['SUBSTANCIA']] = agr.get(s['SUBSTANCIA'], 0.0) + s['QUANTIDADE_KG']
            por_ano[ano]['SUBSTANCIA_ATIVA_KG'] = {k: round(v, 2) for k, v in
                                                   sorted(agr.items(), key=lambda x: -x[1])}
            por_ano[ano]['SUBSTANCIAS_DISTINTAS'] = len(agr)
        linhas_serie.append(por_ano[ano])
        print('  %d · %10.0f kg/l · ADAMA %9.0f (%5.2f%%) · %d titulares'
              % (ano, total, adama, 100 * adama / total if total else 0, len(tit)))

    corpo = {
        'ARTIFACT_ID': 'IT-VENETO-SERIE-POR-ANO', 'REGIAO': REGIAO,
        'GERADO_EM': agora(), 'GERADO_POR': 'coleta/canal_mercado.py --serie',
        'FONTE_VENDA': SOURCE_ID, 'FONTE_REGISTRO': REGISTRO_SOURCE_ID,
        'ANOS': sorted(por_ano),
        'AVISO_VOLUME': AVISO_VOLUME,
        'AVISO_TITULAR_RETROATIVO': (
            'o titular de cada produto e o do registro de HOJE (snapshot 2026-09-07), aplicado '
            'a todos os anos. Produto que mudou de dono aparece sob o dono ATUAL em 2015. '
            'A serie mede a evolucao do portfolio de hoje, NAO a marca que estava na '
            'prateleira naquele ano.'),
        'ANOS_MEDIDOS': linhas_serie,
    }
    with open(os.path.join(SAIDA, 'SERIE-POR-ANO.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


def _ler_linhas(caminho):
    """Le o bruto preservado segundo o esquema MEDIDO do proprio ficheiro.

    Devolve (esquema, registros, substancias, descartadas). Cada descarte carrega o motivo:
    o que ficou de fora, e por que, e metade do que a coleta aprendeu.
    """
    with open(caminho, 'rb') as f:
        corpo = f.read()
    esq = esquema(corpo)
    texto, _ = _decodificar(corpo)
    linhas = [r for r in csv.reader(io.StringIO(texto), delimiter=esq['DELIMITADOR']) if r]
    virgula = esq['DECIMAL_VIRGULA']
    cp, cu, cr, cd, cq = (esq['COL_PROVINCIA'], esq['COL_ULSS'], esq['COL_REGISTRO'],
                          esq['COL_PRODUTO'], esq['COL_QUANTIDADE'])
    cs = esq['COL_SUBSTANCIA']
    registros, substancias, descartadas = [], [], []

    def recusar(numero, r, motivo):
        descartadas.append({'LINHA_NO_FICHEIRO': numero, 'EXCLUSION_REASON': motivo,
                            'MOTIVO_DA_RECUSA': MOTIVO_DA_RECUSA[motivo],
                            'CONTEUDO': ' | '.join(c.strip() for c in r if c.strip())[:300]})

    for numero, r in enumerate(linhas[esq['PRIMEIRA_LINHA_DE_DADO']:],
                               start=esq['PRIMEIRA_LINHA_DE_DADO'] + 1):
        if len(r) <= cq:
            recusar(numero, r, 'COLUNAS_DE_MENOS')
            continue
        if r[cp].strip() not in PROVINCIAS:
            recusar(numero, r, 'RODAPE_DA_FONTE')
            continue
        q = _quantidade(r[cq], virgula)
        try:
            n = int(r[cr])
        except ValueError:
            recusar(numero, r, 'SEM_NUMERO_DE_REGISTRO')
            continue
        if q is None:
            recusar(numero, r, 'QUANTIDADE_ILEGIVEL')
            continue
        registros.append({'PROVINCIA': r[cp].strip(),
                          'ULSS': r[cu].strip() if cu is not None and len(r) > cu else None,
                          'NUM_REGISTRAZIONE': n, 'PRODUTO_NA_FONTE': r[cd].strip(),
                          'QUANTIDADE_KG_L': q})
        # A segunda tabela (2015-2017) vive nas colunas da direita da MESMA linha.
        if cs is not None and len(r) > cs + 1:
            nome = r[cs].strip()
            qs = _quantidade(r[cs + 1], virgula)
            if nome and qs is not None:
                substancias.append({'PROVINCIA': r[cs - 2].strip() if cs >= 2 else None,
                                    'SUBSTANCIA': nome, 'QUANTIDADE_KG': qs})
    return esq, registros, substancias, descartadas


def _anexar_ao_manifesto(run, captured_at):
    """Anexa UMA execucao ao RUN-MANIFEST sem tocar nas outras.

    A execucao nova passa pelo contrato inteiro (`pv.novo_run` + `pv.checar_token`).
    As antigas ficam intactas: nao se conserta proveniencia alheia por reescrita.
    """
    pv.checar_token(run)
    with open(pv.MANIFESTO, encoding='utf-8') as f:
        corpo = json.load(f)
    corpo['RUNS'] = [r for r in corpo.get('RUNS', []) if r.get('RUN_ID') != run['RUN_ID']]
    corpo['RUNS'].append(run)
    corpo['captured_at'] = captured_at
    with open(pv.MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


def _somar(linhas, chave):
    fora = {}
    for l in linhas:
        k = chave(l)
        fora[k] = fora.get(k, 0.0) + l['QUANTIDADE_KG_L']
    return fora


def _bruto_do_store(ano):
    """O bruto SEMPRE vem do store, nunca da rede: normalizar duas vezes tem de dar igual."""
    base = os.path.join(STORE, 'ARPAV_VENDITE_%d' % ano)
    if not os.path.isdir(base):
        raise SystemExit('sem bruto preservado para %d — rode --coletar primeiro' % ano)
    versoes = sorted(os.listdir(base))
    caminho = os.path.join(base, versoes[-1])
    ficheiros = [f for f in os.listdir(caminho) if f.endswith('.csv')]
    return os.path.join(caminho, ficheiros[0])


def main():
    p = argparse.ArgumentParser(description='Canal e mercado — venda declarada por provincia')
    p.add_argument('--ano', type=int, default=2025)
    p.add_argument('--coletar', action='store_true')
    p.add_argument('--normalizar', action='store_true')
    p.add_argument('--sql', action='store_true',
                   help='gera a importacao para o Supabase (nao executa)')
    p.add_argument('--serie', type=str, default='',
                   help='puxa e mede varios anos, ex.: --serie 2015-2025')
    a = p.parse_args()
    if a.serie:
        ini, fim = (int(x) for x in a.serie.split('-'))
        anos = list(range(ini, fim + 1))
        for ano in anos:
            try:
                coletar(ano)
            except SystemExit as e:
                print('  %d · COLETA REPROVOU: %s' % (ano, e))
        print('SERIE:')
        serie(anos)
        return
    fazer_tudo = not (a.coletar or a.normalizar or a.sql)
    info = None
    if a.coletar or fazer_tudo:
        info = coletar(a.ano)
    if a.normalizar or fazer_tudo:
        normalizar(a.ano, info)
    if a.sql or fazer_tudo:
        emitir_sql(a.ano)


if __name__ == '__main__':
    main()
