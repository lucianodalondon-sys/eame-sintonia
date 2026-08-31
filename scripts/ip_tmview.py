#!/usr/bin/env python3
"""
CAMADA IP / BRAND — cliente do TMview (TMDN/EUIPO), rota pública.

POR QUE TMVIEW E NÃO OS QUATRO PORTAIS
  medido em 2026-08-30, com curl e User-Agent de navegador:
    consultas2.oepm.es   (OEPM · ES)  -> 403
    data.inpi.fr         (INPI · FR)  -> 403
    uibm.gov.it          (UIBM · IT)  -> não conecta
    tmdn.org/tmview      (TMview)     -> 200
  O TMview é o agregador oficial da EUIPO sobre os registros nacionais. Uma
  requisição cobre ES + IT + FR + EUIPO, e cada resultado traz `tmOfficeURL`
  apontando de volta para a ficha no portal do país de origem — a evidência
  continua rastreável até a fonte primária, mesmo quando ela recusa o robô.

  ⚠️ TMVIEW É ESPELHO, NÃO É O REGISTRO. Atraso de sincronização entre o
  escritório nacional e o TMview é possível e NÃO foi medido nesta rodada.
  Ausência aqui é NOT_OBSERVED_IN_TMVIEW, nunca "não existe a marca".

O CONTRATO, DESCOBERTO NO PRÓPRIO FRONTEND
  POST https://www.tmdn.org/tmview/api/search/results   (JSON)
    offices   ["ES","IT","FR","EM"]      EM = EUIPO
    appName   ["SYNGENTA"]               nome do TITULAR/requerente
    basicSearch "..."                    nome da MARCA
    fNiceClass ["5"]                     classe de Nice
    page / pageSize
  Os nomes vieram de `index.e1860496.js` da própria página — `e.appName`,
  `e.basicSearch`, `f="fNiceClass"`. Nenhuma autenticação foi contornada.

⚠️ A ARMADILHA QUE ESTA RODADA ENCONTROU, E QUE VIROU TRAVA
  A API **ignora em silêncio** parâmetro cujo nome ela não conhece. Pedir
  `applicantName`, `applicant`, `owner` ou `fApplicantName` devolve HTTP 200 e
  **1.068.402 resultados** — a Espanha inteira — com cara de busca bem-sucedida.
  Um piloto que não percebesse isso teria publicado "1 milhão de marcas da
  Syngenta". Por isso `buscar()` roda uma consulta de CONTROLE sem o filtro e
  RECUSA o resultado quando o total filtrado é igual ao total sem filtro.
  O portão custa uma requisição por escritório e paga o preço de nunca
  confundir "sem filtro" com "sem resultado".

CLASSE DE NICE É DECLARAÇÃO, NÃO INFERÊNCIA
  Classe 1 (produtos químicos para agricultura) e classe 5 são MARCADAS, não
  usadas para descartar. A missão proíbe inferir produto fitossanitário só
  porque uma marca apareceu — e a classe é o que o requerente declarou querer
  proteger, não o que ele vai lançar.

⚠️ CLASSE 5 NÃO É "CLASSE DOS PESTICIDAS" — E ISSO CUSTOU UM ERRO NESTA RODADA
  A classe 5 de Nice cobre `preparações farmacêuticas, veterinárias, higiênicas
  … e pesticidas` na MESMA classe. A primeira versão deste script tratou
  classe 5 como sinal agro e carimbou `GINECANES` e `BEPANTHENSENSICALMSOS`,
  da Bayer, como relevantes para defensivo. São remédio.
  Medido nas 9.661 marcas coletadas:
      SO_CLASSE_5   4.496   ambíguo — pode ser farma, veterinário ou pesticida
      SO_CLASSE_1   1.413   químico agrícola declarado
      CLASSE_1_E_5  2.119   as duas — o padrão do defensivo agrícola
      FORA          1.615
  E a concentração do ruído tem dono: **2.551 das 4.496 ambíguas são da Bayer**,
  que tem divisão farmacêutica. Por isso a marcação tem TRÊS estados e não dois,
  e `SO_CLASSE_5` nunca é apresentada como sinal agro sozinha.

USO
    python3 scripts/ip_tmview.py --amostra          # roda a amostra do piloto
    python3 scripts/ip_tmview.py --titular SYNGENTA --office ES
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = 'https://www.tmdn.org/tmview/api/search/results'
HEAD = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.tmdn.org',
    'Referer': 'https://www.tmdn.org/tmview/',
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'),
}
OFFICES = {'ES': 'OEPM · España', 'IT': 'UIBM · Italia',
           'FR': 'INPI · France', 'EM': 'EUIPO · marca da União Europeia'}
# As duas classes que a agroquímica toca. MARCAM, não filtram — e não valem
# o mesmo: a 1 é específica de agricultura, a 5 é compartilhada com farmácia.
CLASSES_AGRO = {
    1: 'produtos químicos para a agricultura, horticultura e silvicultura',
    5: 'farmacêuticos, veterinários, higiênicos E pesticidas — classe COMPARTILHADA',
}
RELEVANCIA = {
    'CLASSE_1_E_5': 'as duas classes declaradas — o padrão do defensivo agrícola',
    'SO_CLASSE_1': 'químico agrícola declarado, sem a classe 5',
    'SO_CLASSE_5': 'AMBÍGUO: a classe 5 cobre farmacêutico e veterinário além de '
                   'pesticida. Sozinha NÃO é sinal agro',
    'FORA_DAS_CLASSES_AGRO': 'nem 1 nem 5',
    'NOT_KNOWN': 'a fonte não declarou classe',
}
PAGINA = 100
PAUSA = 1.0  # segundos entre requisições — a rota é pública e gratuita


class FiltroIgnorado(RuntimeError):
    """A API aceitou o pedido e devolveu o universo inteiro. Resultado inválido."""


def _post(payload, tentativas=3):
    corpo = json.dumps(payload).encode('utf-8')
    for n in range(tentativas):
        try:
            req = urllib.request.Request(API, data=corpo, headers=HEAD)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if n == tentativas - 1:
                raise
            time.sleep(2 ** n)
            del e
    raise RuntimeError('inalcançável')


def total_do_escritorio(office):
    """Quantas marcas o escritório tem, SEM filtro. É a régua do portão."""
    return _post({'page': '1', 'pageSize': '1', 'offices': [office]})['totalResults']


def buscar(office, titular=None, marca=None, controle=None, limite=None):
    """
    Marcas de um escritório. `controle` é o total sem filtro; quando o total
    filtrado bate com ele, o filtro foi ignorado e a busca é RECUSADA.
    """
    if not titular and not marca:
        raise ValueError('sem filtro não há busca: informe titular ou marca')
    base = {'page': '1', 'pageSize': str(PAGINA), 'offices': [office]}
    if titular:
        base['appName'] = [titular]
    if marca:
        base['basicSearch'] = marca

    primeira = _post(base)
    total = primeira['totalResults']

    if controle is None:
        controle = total_do_escritorio(office)
    if total == controle and total > 0:
        raise FiltroIgnorado(
            f'{office}: o filtro devolveu {total}, exatamente o total do escritório '
            f'sem filtro. A API ignorou o parâmetro. Resultado descartado.')

    marcas, pagina = list(primeira.get('tradeMarks', [])), 1
    while len(marcas) < total and (limite is None or len(marcas) < limite):
        pagina += 1
        time.sleep(PAUSA)
        base['page'] = str(pagina)
        lote = _post(base).get('tradeMarks', [])
        if not lote:
            break
        marcas.extend(lote)
    return total, marcas[:limite] if limite else marcas


# ── o registro por marca: 14 campos, e campo ausente vira NOT_KNOWN ──────
CAMPOS = ['ST13', 'TM_NAME', 'TM_OFFICE', 'APPLICATION_NUMBER', 'REGISTRATION_NUMBER',
          'APPLICATION_DATE', 'REGISTRATION_DATE', 'TM_STATUS', 'TM_TYPE',
          'NICE_CLASS', 'APPLICANT_NAME', 'TERRITORY_PROTECTION',
          'SOURCE_URL', 'AGROCHEMICAL_RELEVANCE']


def classificar_relevancia(classes):
    """
    Três estados, não dois. A classe 5 sozinha NÃO promove uma marca a sinal
    agro: ela é a mesma classe do remédio. Ver o bloco de aviso no topo.
    """
    nc = set(classes or [])
    if not nc:
        return 'NOT_KNOWN'
    if 1 in nc and 5 in nc:
        return 'CLASSE_1_E_5'
    if 1 in nc:
        return 'SO_CLASSE_1'
    if 5 in nc:
        return 'SO_CLASSE_5'
    return 'FORA_DAS_CLASSES_AGRO'


# a força do sinal agro, do mais forte ao mais fraco
SINAL_AGRO_FORTE = ('CLASSE_1_E_5', 'SO_CLASSE_1')


def registro(tm, titular_buscado):
    """Um resultado do TMview vira um registro do piloto. Nada some."""
    def d(v):
        if v is None or v == [] or v == '':
            return 'NOT_KNOWN'
        return v

    classes = tm.get('niceClass') or []
    agro = sorted(set(classes) & set(CLASSES_AGRO))
    relevancia = classificar_relevancia(classes)
    r = {
        'ST13': d(tm.get('ST13')),
        'TM_NAME': d(tm.get('tmName')),
        'TM_OFFICE': d(tm.get('tmOffice')),
        'APPLICATION_NUMBER': d(tm.get('applicationNumber')),
        'REGISTRATION_NUMBER': d(tm.get('registrationNumber')),
        'APPLICATION_DATE': (tm.get('applicationDate') or 'NOT_KNOWN')[:10],
        'REGISTRATION_DATE': (tm.get('registrationDate') or 'NOT_KNOWN')[:10],
        'TM_STATUS': d(tm.get('tradeMarkStatus')),
        'TM_TYPE': d(tm.get('tradeMarkType')),
        'NICE_CLASS': d(classes),
        'APPLICANT_NAME': d(tm.get('applicantName')),
        'TERRITORY_PROTECTION': d(tm.get('tProtection')),
        'SOURCE_URL': d(tm.get('tmOfficeURL')),
        # marcação, não filtro: diz o que o requerente DECLAROU proteger
        'AGROCHEMICAL_RELEVANCE': relevancia,
        'NICE_CLASS_AGRO': agro or [],
        # o casamento titular↔concorrente é do crosswalk, não desta camada
        'TITULAR_BUSCADO': titular_buscado,
        'IDENTIDADE_TITULAR': 'PARTIAL',
    }
    assert all(c in r for c in CAMPOS), 'contrato de campos encolheu'
    return r


def resumir(total, regs):
    """O bloco por concorrente×escritório, com a conta de relevância aberta."""
    por = {}
    for r in regs:
        k = r['AGROCHEMICAL_RELEVANCE']
        por[k] = por.get(k, 0) + 1
    return {
        'ESTADO': 'OK',
        'TOTAL_DECLARADO_PELA_API': total,
        'RECUPERADAS': len(regs),
        'POR_RELEVANCIA': por,
        'SINAL_AGRO_FORTE': sum(por.get(k, 0) for k in SINAL_AGRO_FORTE),
        'AMBIGUAS_SO_CLASSE_5': por.get('SO_CLASSE_5', 0),
        'MARCAS': regs,
    }


def reclassificar(caminho):
    """
    Recalcula a relevância sobre o artefato já coletado, sem repetir a coleta.
    As classes de Nice foram preservadas marca a marca; a régua mudou, o dado
    não. Reclassificar é derivação, e não uma segunda captura.
    """
    with open(caminho, encoding='utf-8') as f:
        art = json.load(f)
    mudou = 0
    for offs in art['POR_CONCORRENTE'].values():
        for o, v in offs.items():
            if v.get('ESTADO') != 'OK':
                continue
            for m in v['MARCAS']:
                nc = m.get('NICE_CLASS')
                nova = classificar_relevancia(nc if isinstance(nc, list) else [])
                if m.get('AGROCHEMICAL_RELEVANCE') != nova:
                    mudou += 1
                m['AGROCHEMICAL_RELEVANCE'] = nova
            offs[o] = resumir(v['TOTAL_DECLARADO_PELA_API'], v['MARCAS'])
    # `layer` neste repositório significa CAMADA REGULATÓRIA, com vocabulário
    # fechado em tests/test_evidence.py::LAYERS. Este artefato não é regulatório;
    # usar a mesma chave criava um segundo significado para o mesmo nome.
    if 'layer' in art:
        art['CAMADA_DO_PILOTO'] = art.pop('layer')
    art['CLASSES_AGRO'] = CLASSES_AGRO
    art['RELEVANCIA'] = RELEVANCIA
    art['RECLASSIFICADO_EM'] = time.strftime('%Y-%m-%d')
    art['MOTIVO_DA_RECLASSIFICACAO'] = (
        'a primeira régua tratava classe 5 como sinal agro. A classe 5 de Nice '
        'cobre farmacêutico e veterinário junto com pesticida, e carimbou remédio '
        'da Bayer como defensivo. Dado inalterado, régua corrigida, derivação '
        f'refeita: {mudou} marcas mudaram de estado.')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
    return mudou


def main():
    argv = sys.argv[1:]
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if '--reclassificar' in argv:
        alvo = os.path.join(raiz, 'data', 'samples', 'COMPETITOR-IP-TMVIEW.json')
        print(f'{reclassificar(alvo)} marcas mudaram de estado · {alvo}')
        return

    if '--titular' in argv:
        titular = argv[argv.index('--titular') + 1]
        office = argv[argv.index('--office') + 1] if '--office' in argv else 'ES'
        total, marcas = buscar(office, titular=titular)
        print(f'{office} · titular {titular!r} · {total} marcas')
        for tm in marcas[:20]:
            r = registro(tm, titular)
            print(f"  {r['APPLICATION_DATE']}  {r['TM_NAME']:<28} "
                  f"{r['TM_STATUS']:<12} nice={r['NICE_CLASS']}  {r['AGROCHEMICAL_RELEVANCE']}")
        return

    if '--amostra' not in argv:
        print(__doc__)
        return

    amostra_path = os.path.join(raiz, 'data', 'samples', 'COMPETITOR-PILOT-AMOSTRA.json')
    with open(amostra_path, encoding='utf-8') as f:
        amostra = json.load(f)
    concorrentes = amostra['AMOSTRA_DO_PILOTO']

    controles = {}
    for o in OFFICES:
        controles[o] = total_do_escritorio(o)
        print(f'controle {o}: {controles[o]} marcas no escritório inteiro')
        time.sleep(PAUSA)

    saida, falhas = {}, []
    for c in concorrentes:
        saida[c] = {}
        for o in OFFICES:
            try:
                total, marcas = buscar(o, titular=c, controle=controles[o])
            except FiltroIgnorado as e:
                falhas.append(str(e))
                saida[c][o] = {'ESTADO': 'RECUSADO_FILTRO_IGNORADO', 'MOTIVO': str(e)}
                continue
            except Exception as e:  # noqa: BLE001 — a falha é dado, não some
                falhas.append(f'{c}/{o}: {type(e).__name__}: {e}')
                saida[c][o] = {'ESTADO': 'SOURCE_FAILED', 'MOTIVO': f'{type(e).__name__}: {e}'}
                continue
            regs = [registro(tm, c) for tm in marcas]
            saida[c][o] = resumir(total, regs)
            v = saida[c][o]
            print(f"  {c:<10} {o}  {len(regs):>4} marcas · {v['SINAL_AGRO_FORTE']:>4} "
                  f"sinal forte · {v['POR_RELEVANCIA'].get('SO_CLASSE_5', 0):>4} ambíguas")
            time.sleep(PAUSA)

    art = {
        'SOURCE_ID': 'COMPETITOR-IP-TMVIEW',
        'source': 'TMview — TMDN/EUIPO, agregador dos registros nacionais de marca',
        'SOURCE_LOCATION': 'www.tmdn.org/tmview',
        'FACT_LOCATION': 'ES · IT · FR · EU',
        'ORIGINAL_LANGUAGE': 'multi',
        'CAMADA_DO_PILOTO': 'IP / BRAND',
        'captured_at': time.strftime('%Y-%m-%d'),
        'access_note': f'POST {API} · offices + appName · sem autenticação',
        'ESCRITORIOS': OFFICES,
        'CONTROLE_SEM_FILTRO': controles,
        'PORTAO_DO_FILTRO': (
            'toda busca é comparada com o total do escritório sem filtro. Igualdade '
            'significa parâmetro ignorado pela API, e o resultado é RECUSADO. Foi '
            'assim que 1.068.402 marcas espanholas quase viraram "marcas da Syngenta".'),
        'CLASSES_AGRO': CLASSES_AGRO,
        'CLASSE_E_DECLARACAO': (
            'classe de Nice é o que o requerente declarou querer proteger. NÃO é '
            'prova de que existe produto fitossanitário, nem de que ele será lançado.'),
        'TMVIEW_E_ESPELHO': (
            'ausência aqui é NOT_OBSERVED_IN_TMVIEW. O atraso de sincronização entre '
            'escritório nacional e TMview não foi medido nesta rodada.'),
        'IDENTIDADE_TITULAR': (
            'appName casa TEXTO de titular. `SYNGENTA LIMITED` ter vindo numa busca '
            'por `SYNGENTA` não prova relação societária com o titular do registro '
            'espanhol. Todo registro sai PARTIAL; quem promove é o crosswalk.'),
        'FALHAS': falhas,
        'POR_CONCORRENTE': saida,
    }
    destino = os.path.join(raiz, 'data', 'samples', 'COMPETITOR-IP-TMVIEW.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
    print('\ngravado:', destino)
    if falhas:
        print('falhas registradas:', len(falhas))


if __name__ == '__main__':
    main()
