#!/usr/bin/env python3
"""
REGISTRO LOCAL — os três registros oficiais na MESMA forma.

    python3 scripts/registro_local.py            # mede os três e imprime

Espanha, Itália e França publicam o registro nacional de produtos
fitossanitários inteiro, de graça, sem chave. Este módulo os lê e devolve o
MESMO registro para os três, para que o crosswalk seja o mesmo nos três — e
não três matchers diferentes que ninguém consegue comparar depois.

    REGISTRATION_ID · PRODUCT_NAME · ALT_NAMES · HOLDER · GRUPO
    STATUS · IN_FORCE · DATE_REGISTRATION · DATE_EXPIRY · COUNTRY

AS TRÊS PORTAS, MEDIDAS
  ES  POST servicio.mapa.gob.es/regfiweb/Exportaciones/ExportJsonProductos
      JSON · 3.084 produtos · 262 titulares
  IT  GET  dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_<AAAAMMDD>.csv
      CSV · 17.695 produtos · 576 titulares · CC BY 4.0
  FR  ZIP  data.gouv.fr — catálogo E-Phy (ANSES), recurso resolvido pela API
      CSV · 15.140 produtos · 1.335 titulares · Licence Ouverte

⚠️ O QUE OS TRÊS REGISTROS NÃO SÃO
  Não são o mesmo universo. ES traz 3.084 e IT traz 17.695 porque a Itália
  guarda o histórico revogado desde 1970 e a Espanha publica o conjunto
  corrente. Comparar os totais brutos entre países mede a política de
  publicação de cada ministério, não o tamanho do mercado.

⚠️ A ARMADILHA DO TITULAR ANTECESSOR — MEDIDA, E NÃO RESOLVIDA
  FR e IT carregam décadas de razões sociais que hoje pertencem a outros
  grupos: `CIBA GEIGY` (222 registros FR), `DOW ELANCO` (197), `MONSANTO`
  (182), `AVENTIS CROPSCIENCE ITALIA` (771 IT), `DU PONT DE NEMOURS ITALIANA`
  (467 IT). Dobrá-las nos grupos de hoje seria uma afirmação **societária**
  que este piloto não tem — a mesma recusa que separa `SHARDA CROPCHEM
  ESPAÑA` de `SHARDA EUROPE`.

  Consequência que precisa ser dita: **o agrupamento por titular subconta**
  o concorrente em FR e IT. Os antecessores conhecidos ficam listados em
  `ANTECESSORES_NAO_AGRUPADOS` e são CONTADOS no artefato, para que a
  subcontagem tenha tamanho em vez de virar nota de rodapé.
"""
import csv
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAISES = ('ES', 'IT', 'FR')

FONTES = {
    'ES': {'arquivo': 'data/raw/ES/ropf-export.json',
           'fonte': 'ROPF — Registro Oficial de Productos Fitosanitarios (MAPA)',
           'url': 'https://servicio.mapa.gob.es/regfiweb/Productos/Index',
           'licenca': 'dados públicos do MAPA'},
    'IT': {'arquivo': 'data/raw/IT/PROD_FTS_6_20260824.csv',
           'fonte': 'Banca dati dei prodotti fitosanitari — Ministero della Salute',
           'url': 'https://www.dati.salute.gov.it/it/dataset/fitosanitari/',
           'licenca': 'CC BY 4.0'},
    'FR': {'arquivo': 'data/raw/FR/ephy/produits_utf8.csv',
           'fonte': 'Catalogue E-Phy — ANSES, via data.gouv.fr',
           'url': 'https://www.data.gouv.fr/fr/datasets/575e9fac88ee38072a640390/',
           'licenca': 'Licence Ouverte'},
}

# ── os prefixos declarados, POR PAÍS ─────────────────────────────────────
#
# ES é mantido EXATAMENTE como estava na primeira rodada, para que os números
# já publicados da Espanha não se movam por efeito colateral desta.
# IT e FR usam o nome do grupo como prefixo, o que foi verificado contra a
# lista real de titulares de cada registro antes de ser escrito aqui.
GRUPOS = {
    'BAYER':    {'ES': ['BAYER CROPSCIENCE'], 'IT': ['BAYER'], 'FR': ['BAYER']},
    'SYNGENTA': {'ES': ['SYNGENTA'], 'IT': ['SYNGENTA'], 'FR': ['SYNGENTA']},
    'BASF':     {'ES': ['BASF'], 'IT': ['BASF'], 'FR': ['BASF']},
    'CORTEVA':  {'ES': ['CORTEVA'], 'IT': ['CORTEVA'], 'FR': ['CORTEVA']},
    'FMC':      {'ES': ['FMC '], 'IT': ['FMC'], 'FR': ['FMC']},
    'UPL':      {'ES': ['UPL IBERIA', 'UPL HOLDINGS'], 'IT': ['UPL'], 'FR': ['UPL']},
    'NUFARM':   {'ES': ['NUFARM'], 'IT': ['NUFARM'], 'FR': ['NUFARM']},
    'CERTIS BELCHIM': {'ES': ['CERTIS BELCHIM'], 'IT': ['CERTIS'], 'FR': ['CERTIS']},
    'ADAMA':    {'ES': ['ADAMA'], 'IT': ['ADAMA'], 'FR': ['ADAMA']},
}

# Razões sociais que são ANTECESSORAS conhecidas dos grupos de hoje e que
# NÃO são agrupadas. Estão aqui para serem CONTADAS, não para serem usadas.
ANTECESSORES_NAO_AGRUPADOS = {
    'CIBA GEIGY': 'linhagem que hoje se associa a SYNGENTA — não agrupado',
    'ZENECA': 'idem',
    'NOVARTIS': 'idem',
    'AVENTIS': 'linhagem que hoje se associa a BAYER — não agrupado',
    'RHONE POULENC': 'idem',
    'PEPRO': 'idem',
    'DOW ELANCO': 'linhagem que hoje se associa a CORTEVA — não agrupado',
    'DOW AGROSCIENCES': 'idem',
    'DU PONT': 'idem',
    'DUPONT': 'idem',
    'MONSANTO': 'linhagem que hoje se associa a BAYER — não agrupado',
    'CHEMINOVA': 'linhagem que hoje se associa a ADAMA — não agrupado',
}

# O que cada registro chama de "em vigor". Palavras diferentes, mesma pergunta.
IT_FORA_DE_VIGOR = {'Revocato', 'Scaduto'}


def _norm(s):
    """Caixa e espaços. Pontuação PRESERVADA: `S.A.` não é `S.A.U.`."""
    return ' '.join((s or '').upper().split())


def classificar(pais, titular):
    """Grupo declarado, ou None. Prefixo do país, nunca semelhança."""
    t = _norm(titular)
    for grupo, por_pais in GRUPOS.items():
        for p in por_pais.get(pais, []):
            if t.startswith(_norm(p)):
                return grupo
    return None


def antecessor(titular):
    """A linhagem antiga que este titular representa, se for uma conhecida."""
    t = _norm(titular)
    for nome, nota in ANTECESSORES_NAO_AGRUPADOS.items():
        if nome in t:
            return nome, nota
    return None, None


def _registro(**kw):
    kw.setdefault('ALT_NAMES', [])
    return kw


def carregar_es():
    with open(os.path.join(RAIZ, FONTES['ES']['arquivo']), encoding='utf-8') as f:
        d = json.load(f)
    out = []
    for r in d['rows']:
        out.append(_registro(
            COUNTRY='ES',
            REGISTRATION_ID=r['NumRegistro'],
            PRODUCT_NAME=r.get('Nombre'),
            HOLDER=r.get('Titular'),
            GRUPO=classificar('ES', r.get('Titular')),
            STATUS=r.get('Estado'),
            IN_FORCE=r.get('Estado') == 'Vigente',
            DATE_REGISTRATION=r.get('StrFechaInscripcion'),
            DATE_EXPIRY=r.get('StrFechaCaducidad')))
    return out, d.get('fecha')


def carregar_it():
    caminho = os.path.join(RAIZ, FONTES['IT']['arquivo'])
    with open(caminho, encoding='utf-8-sig', newline='') as f:
        linhas = list(csv.DictReader(f, delimiter=';'))
    out = []
    for r in linhas:
        estado = (r.get('stato_amministrativo') or '').strip()
        out.append(_registro(
            COUNTRY='IT',
            REGISTRATION_ID=(r.get('num_registrazione') or '').strip(),
            PRODUCT_NAME=r.get('denominazione_prodotto'),
            HOLDER=r.get('ragione_sociale'),
            GRUPO=classificar('IT', r.get('ragione_sociale')),
            STATUS=estado,
            IN_FORCE=estado not in IT_FORA_DE_VIGOR and estado != '',
            DATE_REGISTRATION=r.get('data_registrazione'),
            DATE_EXPIRY=r.get('data_scadenza_autorizzazione')))
    return out, os.path.basename(caminho)


def carregar_fr():
    caminho = os.path.join(RAIZ, FONTES['FR']['arquivo'])
    with open(caminho, encoding='utf-8', newline='') as f:
        linhas = list(csv.DictReader(f, delimiter=';'))
    out = []
    for r in linhas:
        # `seconds noms commerciaux` é o equivalente francês das denominações
        # comuns espanholas: o MESMO registro vendido sob outros nomes. Ele
        # multiplica a superfície de casamento com a marca, e por isso entra —
        # mas entra como ALT_NAME, sem virar produto separado.
        alt = [x.strip() for x in (r.get('seconds noms commerciaux') or '').split('|')
               if x.strip()]
        estado = (r.get('Etat d’autorisation') or '').strip()
        out.append(_registro(
            COUNTRY='FR',
            REGISTRATION_ID=(r.get('numero AMM') or '').strip(),
            PRODUCT_NAME=r.get('nom produit'),
            ALT_NAMES=alt,
            HOLDER=r.get('titulaire'),
            GRUPO=classificar('FR', r.get('titulaire')),
            STATUS=estado,
            IN_FORCE=estado == 'AUTORISE',
            DATE_REGISTRATION=r.get('Date de première autorisation'),
            DATE_EXPIRY=None,   # o E-Phy publica retirada, não caducidade
            TIPO=r.get('type produit')))
    return out, os.path.basename(caminho)


CARREGADORES = {'ES': carregar_es, 'IT': carregar_it, 'FR': carregar_fr}


def carregar(pais):
    if pais not in CARREGADORES:
        raise ValueError(f'país sem registro local declarado: {pais}')
    return CARREGADORES[pais]()


def medir(pais):
    rows, versao = carregar(pais)
    por_grupo, antecessores = {}, {}
    for r in rows:
        if r['GRUPO']:
            g = por_grupo.setdefault(r['GRUPO'], {'REGISTROS': 0, 'EM_VIGOR': 0,
                                                  'RAZOES_SOCIAIS': {}})
            g['REGISTROS'] += 1
            g['EM_VIGOR'] += bool(r['IN_FORCE'])
            rs = _norm(r['HOLDER'])
            g['RAZOES_SOCIAIS'][rs] = g['RAZOES_SOCIAIS'].get(rs, 0) + 1
        else:
            nome, nota = antecessor(r['HOLDER'])
            if nome:
                a = antecessores.setdefault(nome, {'REGISTROS': 0, 'NOTA': nota})
                a['REGISTROS'] += 1
    return {
        'PAIS': pais,
        'FONTE': FONTES[pais]['fonte'],
        'URL': FONTES[pais]['url'],
        'LICENCA': FONTES[pais]['licenca'],
        'VERSAO_DA_FONTE': versao,
        'REGISTROS': len(rows),
        'EM_VIGOR': sum(1 for r in rows if r['IN_FORCE']),
        'TITULARES_DISTINTOS': len({_norm(r['HOLDER']) for r in rows}),
        'POR_GRUPO': por_grupo,
        'ANTECESSORES_NAO_AGRUPADOS': antecessores,
        'SUBCONTAGEM_CONHECIDA': sum(a['REGISTROS'] for a in antecessores.values()),
    }


if __name__ == '__main__':
    for pais in PAISES:
        m = medir(pais)
        print(f"\n=== {pais} · {m['REGISTROS']} registros · "
              f"{m['EM_VIGOR']} em vigor · {m['TITULARES_DISTINTOS']} titulares")
        print(f"    fonte: {m['VERSAO_DA_FONTE']}")
        for g, v in sorted(m['POR_GRUPO'].items(), key=lambda kv: -kv[1]['EM_VIGOR']):
            print(f"      {v['EM_VIGOR']:>5} em vigor / {v['REGISTROS']:>5}  {g}")
        if m['ANTECESSORES_NAO_AGRUPADOS']:
            print(f"    antecessores NÃO agrupados: {m['SUBCONTAGEM_CONHECIDA']} registros")
            for n, v in sorted(m['ANTECESSORES_NAO_AGRUPADOS'].items(),
                               key=lambda kv: -kv[1]['REGISTROS'])[:6]:
                print(f"      {v['REGISTROS']:>5}  {n}")
