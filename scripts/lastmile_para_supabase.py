#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERA O SQL DE IMPORTAÇÃO da missão LAST-MILE para o Supabase.

    python3 scripts/lastmile_para_supabase.py

Lê os artefatos JSON/CSV que a missão produziu e escreve
`supabase/importacoes/IT-LASTMILE-<data>.sql`, pronto para a cadeia canônica.

POR QUE GERAR ARQUIVO EM VEZ DE ESCREVER NO BANCO
--------------------------------------------------
As credenciais do Supabase existem **só** como segredo do GitHub Actions. Esta
sessão não as tem, e não deve tê-las. Então o trabalho é: produzir o arquivo,
versionar, e deixar o runner aplicar.

    O QUE VAI PARA O GIT É REPRODUZÍVEL. O QUE FOI DIGITADO NO BANCO, NÃO.

TRÊS COISAS QUE ESTE GERADOR RECUSA A FAZER
--------------------------------------------
1. **Não inventa `o_que_nao_prova`.** Se o registro não trouxe a ressalva, o
   gerador escreve uma que diz exatamente isso — que ela não veio — em vez de
   uma frase bonita. Ressalva inventada é pior que ressalva ausente: ela
   parece cuidado.

2. **Não converte `valor_texto` em número quando o parse é duvidoso.** O EC
   Agri-food publica «€237,00» e a vírgula é decimal italiana. O literal vai
   sempre; o numérico só quando o parse é seguro.

3. **Não deduz `classe_temporal`.** Registro sem classe declarada entra como
   `HISTORICAL`, que é o mais conservador — nunca como `CURRENT`. Chamar de
   corrente o que não se sabe é o erro que o azeite de Salerno de 2015 já
   cometeu no demo.
"""
import csv
import json
import os
import re
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LM = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
RES = os.path.join(ROOT, 'research', 'italy-lastmile')
ISTAT = os.path.join(ROOT, 'data', 'samples', 'IT-ISTAT-COLTIVAZIONI',
                     'istat_101_1015_coltivazioni_regioni_2024_2026.csv')
DESTINO = os.path.join(ROOT, 'supabase', 'importacoes')
HOJE = '2026-09-02'

SEM_RESSALVA = ('NAO_SEI — o registro de origem nao trouxe a ressalva. Isto e '
                'ausencia de declaracao, nao ausencia de limite.')

# ── de que natureza é a fonte, pelo endereço ──────────────────────────────
NATUREZA = [
    (r'istat|eurostat|europa\.eu/eurostat', 'ESTATISTICA_OFICIAL'),
    (r'ismea|bmti|agridata|borsa|mercat', 'MERCADO'),
    (r'arpa|meteo|copernicus|edo\.jrc|climate', 'AGROMETEOROLOGIA'),
    (r'fitosanitar|bollettin|difesa|agricoltura\.regione|arsac|alsia|laore|'
     r'edmundmach|fmach|enterisi', 'BOLETIM_FITOSSANITARIO'),
    (r'salute\.gov|eur-lex|europa\.eu/food|efsa|pesticid|ministero', 'REGULATORIO'),
    (r'openalex|doi|crea|unibo|univ|gire', 'CIENCIA'),
    (r'adama|basf|bayer|corteva|syngenta|fmc\.com|upl', 'CATALOGO_FABRICANTE'),
    (r'agronotizie|informatoreagrario|terraevita|freshplaza', 'IMPRENSA_TECNICA'),
    (r'fiera|eima|vinitaly|macfrut|convegno|congress', 'EVENTO'),
]


def q(v):
    """Literal SQL. None vira NULL. Nunca concatena aspas por acidente."""
    if v is None or v == '':
        return 'NULL'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def arr(vs):
    if not vs:
        return "'{}'"
    limpos = [str(v).replace('"', '').replace('\\', '') for v in vs if v]
    return "ARRAY[" + ','.join(q(v) for v in limpos) + "]::text[]" if limpos else "'{}'"


def natureza_de(url, nome=''):
    t = ((url or '') + ' ' + (nome or '')).lower()
    achou = [k for rx, k in NATUREZA if re.search(rx, t)]
    return achou or ['OUTRA']


def classe_de(v):
    """⚠️ Sem classe declarada → HISTORICAL. Nunca CURRENT por omissão."""
    c = (v or '').strip().upper()
    return c if c in ('CURRENT', 'OUTLOOK', 'HISTORICAL') else 'HISTORICAL'


def nivel_de(texto):
    t = (texto or '').lower()
    if 'provinc' in t:
        return 'PROVINCIAL'
    if any(w in t for w in ('areal', 'area ', 'zona', 'lago', 'litorale', 'comprensor')):
        return 'AREAL'
    if any(w in t for w in ('nord-', 'sud', 'isole', 'centro', 'macroarea')):
        return 'MACROAREA'
    if 'itali' in t and 'nazional' not in t and len(t) < 30:
        return 'NACIONAL'
    if 'nacional' in t or 'nazional' in t:
        return 'NACIONAL'
    if t.strip():
        return 'REGIONAL'
    return 'NAO_SEI'


def num(txt):
    """Só devolve número quando o parse é seguro. Na dúvida, NULL."""
    if txt is None:
        return None
    s = str(txt).strip()
    s = re.sub(r'[€$£\s]', '', s)
    if not re.fullmatch(r'-?\d{1,3}(\.\d{3})*(,\d+)?|-?\d+(\.\d+)?', s):
        return None
    if ',' in s:                       # vírgula decimal italiana
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def main():
    dados = json.load(open(os.path.join(RES, 'NEW-REAL-DATA.json'), encoding='utf-8'))
    fontes = json.load(open(os.path.join(RES, 'NEW-REAL-SOURCES.json'), encoding='utf-8'))
    rotas = [json.load(open(os.path.join(LM, f), encoding='utf-8'))
             for f in ('IT-ROTA-SEM_VPN.json', 'IT-ROTA-COM_VPN_IT.json')
             if os.path.exists(os.path.join(LM, f))]

    L = []
    A = L.append
    A('-- ═══════════════════════════════════════════════════════════════════\n')
    A('-- IMPORTAÇÃO · MISSÃO LAST-MILE ITÁLIA · %s\n' % HOJE)
    A('--\n')
    A('-- Gerado por `scripts/lastmile_para_supabase.py`. NÃO EDITAR À MÃO:\n')
    A('-- regerar é barato, e um arquivo editado à mão diverge da origem sem\n')
    A('-- deixar rastro.\n')
    A('--\n')
    A('-- Idempotente: todo insert tem `on conflict do nothing`. Rodar duas\n')
    A('-- vezes não duplica e não falha.\n')
    A('-- ═══════════════════════════════════════════════════════════════════\n')
    A('begin;\n\n')

    # ── 1 · fontes externas ───────────────────────────────────────────────
    vistas = {}
    A('-- ── FONTES EXTERNAS ────────────────────────────────────────────────\n')
    for s in fontes.get('FONTES', []):
        url = (s.get('URL') or '').strip().rstrip('/')
        if not url or url in vistas:
            continue
        vistas[url] = s
        nat = natureza_de(url, s.get('NOME'))
        A("insert into public.fonte_externa (nome, url_base, natureza, pais, "
          "periodicidade, formato, observacao) values (%s,%s,ARRAY[%s]::fonte_natureza[],"
          "'IT',%s,%s,%s) on conflict (url_base) do nothing;\n"
          % (q((s.get('NOME') or url)[:200]), q(url),
             ','.join(q(n) for n in nat),
             q(s.get('PERIODICIDADE')), q(s.get('FORMATO')),
             q((s.get('O_QUE_PUBLICA') or '')[:400])))
    A('\n')

    # ── 2 · testes de acesso, com a ROTA declarada ────────────────────────
    A('-- ── TESTES DE ACESSO ───────────────────────────────────────────────\n')
    A('-- ⚠️ cada linha declara a ROTA. Um 200 sem rota nao mede nada.\n')
    n_testes = 0
    for r in rotas:
        rota = 'IT_VPN' if 'COM_VPN' in (r.get('RODADA') or '') else 'BR_DIRETO'
        for it in r.get('ITENS', []):
            causa = it.get('CAUSA') or ''
            est = {'ABERTO': 'ABERTA', 'TCP_NAO_ABRE': 'BLOQUEIO_GEOGRAFICO',
                   'TLS_DO_SERVIDOR': 'TLS_DO_SERVIDOR', 'TLS_OU_WAF': 'TLS_DO_SERVIDOR',
                   'DETECCAO_DE_ROBO': 'DETECCAO_DE_ROBO',
                   'RESPONDE_MAS_RECUSA': 'FORA_DO_AR'}.get(causa, 'NAO_TESTADA')
            # ⚠️ TCP que nao abre so vira BLOQUEIO_GEOGRAFICO quando a OUTRA
            # rota abriu. Sem essa prova, e FORA_DO_AR — nao se declara
            # geografia por preguica.
            if est == 'BLOQUEIO_GEOGRAFICO' and rota == 'BR_DIRETO':
                outro = [x for rr in rotas if rr is not r
                         for x in rr.get('ITENS', []) if x['FONTE'] == it['FONTE']]
                if not (outro and str(outro[0].get('ESTADO', '')).startswith('HTTP 2')):
                    est = 'FORA_DO_AR'
            url = it['URL'].rstrip('/')
            evid = ('%s · %s · %s · %ss' % (it.get('ESTADO'), causa,
                                            (it.get('DETALHE') or '')[:120],
                                            it.get('SEGUNDOS')))
            cng = None if causa == 'TCP_NAO_ABRE' else it.get('VPN_RESOLVE')
            A("insert into public.fonte_externa (nome, url_base, natureza, pais) "
              "values (%s,%s,ARRAY[%s]::fonte_natureza[],'IT') "
              "on conflict (url_base) do nothing;\n"
              % (q(it['FONTE'][:200]), q(url),
                 ','.join(q(n) for n in natureza_de(url, it['FONTE']))))
            A("insert into public.fonte_acesso_teste (fonte_id, testada_em, rota, "
              "estado, segundos, erro_literal, evidencia, causa_nao_e_geografia) "
              "select id,%s,%s,%s,%s,%s,%s,%s from public.fonte_externa "
              "where url_base=%s on conflict do nothing;\n"
              % (q(r.get('QUANDO') or HOJE), q(rota), q(est),
                 it.get('SEGUNDOS') if it.get('SEGUNDOS') is not None else 'NULL',
                 q((it.get('DETALHE') or '')[:300]), q(evid), q(cng), q(url)))
            n_testes += 1
    A('\n')

    # ── 3 · estatística agrícola, do CSV do ISTAT ─────────────────────────
    n_est = 0
    if os.path.exists(ISTAT):
        A('-- ── ESTATISTICA AGRICOLA · ISTAT cubo 101_1015 Coltivazioni ───────\n')
        A("insert into public.fonte_externa (nome, url_base, natureza, pais, "
          "organismo, periodicidade, formato) values "
          "('ISTAT · esploradati (cubo 101_1015 Coltivazioni)',"
          "'https://esploradati.istat.it',ARRAY['ESTATISTICA_OFICIAL']::fonte_natureza[],"
          "'IT','Istituto Nazionale di Statistica','anual','SDMX') "
          "on conflict (url_base) do nothing;\n")
        with open(ISTAT, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                ano = int(row['year'])
                lit = row['area_it']
                niv = 'NACIONAL' if row['area_code'] == 'IT' else 'REGIONAL'
                base = ("(select id from public.fonte_externa where "
                        "url_base='https://esploradati.istat.it')")
                for col, ind, uni, deriv, form in (
                        ('superficie_totale_ha', 'SUPERFICIE_HA', 'ha', False, None),
                        ('produzione_raccolta_q', 'PRODUCAO_Q', 'quintais', False, None),
                        ('resa_calculada_t_ha', 'RENDIMENTO_T_HA', 't/ha', True,
                         'produzione_raccolta_q / 10 / superficie_totale_ha')):
                    v = (row.get(col) or '').strip()
                    if not v:
                        continue
                    # ⚠️ 2026 foi publicado em 28/07/2026, antes da colheita de
                    # oliveira, uva e milho. Nao pode ser HISTORICAL.
                    classe = 'OUTLOOK' if ano >= 2026 else 'HISTORICAL'
                    nao_prova = (
                        'area e producao publicadas. NAO diz nada sobre presenca de '
                        'praga, uso de defensivo, tamanho de mercado nem receita.')
                    if deriv:
                        nao_prova += (' E o rendimento e DERIVADO por nos sobre a area '
                                      'TOTAL: o campo de area em producao veio vazio em '
                                      '100% das linhas, entao para cultura perene este '
                                      'valor e um PISO, nao a produtividade do talhao.')
                    if ano >= 2026:
                        nao_prova += (' O ano 2026 foi publicado em 28/07/2026, antes da '
                                      'colheita de oliveira, uva e milho — nao e colheita '
                                      'observada.')
                    A("insert into public.estatistica_agricola (fonte_id, crop_literal, "
                      "geografia_literal, nivel, ano, indicador, valor, unidade, classe, "
                      "derivado_por_nos, formula_derivacao, source_url, dataset_codigo, "
                      "o_que_nao_prova) values (%s,%s,%s,%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                      "on conflict do nothing;\n"
                      % (base, q(row['crop_it']), q(lit), q(niv), ano, q(ind), v, q(uni),
                         q(classe), q(deriv), q(form), q(row['source_url']),
                         q(row['dataflow']), q(nao_prova)))
                    n_est += 1
        A('\n')

    # ── 4 · os registros da coleta, por bloco ─────────────────────────────
    A('-- ── REGISTROS DA COLETA ────────────────────────────────────────────\n')
    conta = Counter()
    for r in dados.get('REGISTROS', []):
        bloco = r.get('BLOCO') or ''
        url = (r.get('source_url') or '').strip()
        if not url:
            continue
        fonte = ("(select id from public.fonte_externa where url_base=%s "
                 "or %s like url_base||'%%' order by length(url_base) desc limit 1)"
                 % (q(url.rstrip('/')), q(url)))
        A("insert into public.fonte_externa (nome, url_base, natureza, pais) values "
          "(%s,%s,ARRAY[%s]::fonte_natureza[],'IT') on conflict (url_base) do nothing;\n"
          % (q((r.get('source_name') or url)[:200]), q(url.rstrip('/')),
             ','.join(q(n) for n in natureza_de(url, r.get('source_name')))))
        naoprova = r.get('o_que_nao_prova') or SEM_RESSALVA
        classe = classe_de(r.get('observation_class'))
        reg = r.get('region') or ''
        niv = nivel_de(reg)

        if bloco in ('mercado', 'ismea-mercado'):
            A("insert into public.mercado_observacao (fonte_id, crop_literal, praca, "
              "nivel, indicador, valor_texto, valor_numerico, unidade, qualidade, "
              "periodo_inicio, periodo_fim, classe, citacao_literal, source_url, "
              "publicado_em, o_que_nao_prova) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "coalesce(%s::date,'2026-01-01'),coalesce(%s::date,'2026-12-31'),%s,%s,%s,"
              "%s::date,%s) on conflict do nothing;\n"
              % (fonte, q(r.get('crop') or 'NAO_SEI'), q(reg or None), q(niv),
                 q((r.get('tipo') or 'PRECO')[:40]),
                 q(r.get('valor') or r.get('o_que')),
                 num(r.get('valor')) if num(r.get('valor')) is not None else 'NULL',
                 q(r.get('unidade') or 'NAO_SEI'), q(r.get('periodo')),
                 q(r.get('publication_date')), q(r.get('publication_date')),
                 q(classe), q((r.get('citacao_literal') or '')[:900]), q(url),
                 q(r.get('publication_date')), q(naoprova)))
            conta['mercado'] += 1
        elif bloco in ('clima', 'arpav-clima-veneto'):
            A("insert into public.clima_observacao (fonte_id, geografia_literal, nivel, "
              "variavel, valor, valor_texto, unidade, periodo_inicio, periodo_fim, "
              "classe, source_url, publicado_em, o_que_nao_prova) values "
              "(%s,%s,%s,'OUTRA',%s,%s,%s,coalesce(%s::date,'2026-08-01'),"
              "coalesce(%s::date,'2026-09-02'),%s,%s,%s::date,%s) on conflict do nothing;\n"
              % (fonte, q(reg or 'NAO_SEI'), q(niv),
                 num(r.get('valor')) if num(r.get('valor')) is not None else 'NULL',
                 q(r.get('valor') or r.get('o_que')), q(r.get('unidade')),
                 q(r.get('publication_date')), q(r.get('publication_date')),
                 q(classe), q(url), q(r.get('publication_date')),
                 q(naoprova if len(naoprova) > 30 else
                   naoprova + ' CLIMA E CONDICAO: nao e presenca de doenca, nao e '
                              'incidencia de praga, nao e perda de produtividade.')))
            conta['clima'] += 1
        elif bloco in ('fenologia', 'boletins-regioes-fechadas'):
            A("insert into public.boletim_fitossanitario (fonte_id, titulo, publicado_em, "
              "geografia_literal, nivel, crops_declaradas, crop_declarada, fase_declarada, "
              "citacao_literal, source_url, classe) values (%s,%s,"
              "coalesce(%s::date,'2026-09-02'),%s,%s,%s,true,%s,%s,%s,%s) "
              "on conflict do nothing;\n"
              % (fonte, q((r.get('o_que') or 'boletim')[:300]),
                 q(r.get('publication_date')), q(reg or 'NAO_SEI'), q(niv),
                 arr([r.get('crop')] if r.get('crop') else []),
                 q(r.get('valor')), q((r.get('citacao_literal') or '')[:900]),
                 q(url), q(classe)))
            conta['boletim'] += 1
        elif bloco == 'regulatorio':
            A("insert into public.sinal_regulatorio_futuro (fonte_id, tipo, "
              "substancia_literal, o_que, quando, decisao_tomada, citacao_literal, "
              "source_url, publicado_em, confianca, por_que_pode_importar, "
              "o_que_nao_prova) values (%s,'PRORROGACAO_DE_APROVACAO',%s,%s,%s::date,"
              "false,%s,%s,%s::date,%s,%s,%s) on conflict do nothing;\n"
              % (fonte, q((r.get('crop') or r.get('tipo') or 'NAO_SEI')[:120]),
                 q((r.get('o_que') or '')[:600]), q(r.get('periodo')),
                 q((r.get('citacao_literal') or '')[:900]), q(url),
                 q(r.get('publication_date')),
                 q((r.get('confidence') or 'MEDIA').upper()[:5]),
                 q('ver o_que; a conversao em oportunidade comercial NAO e automatica'),
                 q(naoprova)))
            conta['regulatorio'] += 1
        elif bloco == 'eventos':
            A("insert into public.evento_setorial (fonte_id, nome, data_inicio, "
              "data_fim, cidade, tema, crops, source_url) values (%s,%s,"
              "coalesce(%s::date,'2026-09-02'),%s::date,%s,%s,%s,%s) "
              "on conflict (nome, data_inicio) do nothing;\n"
              % (fonte, q((r.get('o_que') or 'evento')[:200]),
                 q(r.get('periodo')), q(None), q(reg or None),
                 q((r.get('tipo') or '')[:200]),
                 arr([r.get('crop')] if r.get('crop') else []), q(url)))
            conta['evento'] += 1
        else:
            # ⚠️ NAO E DESCARTE E NAO E DEPOSITO.
            # Estes registros tem destino que JA EXISTE no banco -- vozes vao
            # para pessoa+origem, concorrente para organizacao+conteudo,
            # catalogo para catalogo_produto, janela para issue_window. Essas
            # tabelas tem travas escritas para impedir erros especificos do
            # Brasil, e forcar 97 linhas nelas sem ler cada trava produziria
            # dado que passa no insert e mente na consulta.
            #
            #     DADO NA AREA DE ESPERA E DADO QUE CHEGOU E AINDA NAO FOI
            #     COLOCADO. DADO FORCADO NA TABELA ERRADA MENTE EM SILENCIO.
            #
            # O destino e OBRIGATORIO: nao se aceita registro sem saber para
            # onde ele vai.
            destino = {
                'vozes': 'pessoa_e_origem',
                'concorrente': 'organizacao_e_conteudo',
                'catalogo': 'catalogo_produto',
                'herbicida': 'issue_window',
                'peso-economico': 'estatistica_agricola',
                'istat-area-producao': 'estatistica_agricola',
            }.get(bloco, 'NAO_SEI')
            A("insert into public.lastmile_registro_pendente (missao, bloco, "
              "destino_pretendido, crop_literal, geografia_literal, o_que, "
              "valor_texto, unidade, periodo, classe, citacao_literal, source_url, "
              "publicado_em, confianca, o_que_nao_prova, exige_rota_italiana) values "
              "('LAST-MILE-2026-09-02',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::date,%s,%s,%s) "
              "on conflict do nothing;\n"
              % (q(bloco), q(destino), q(r.get('crop')), q(reg or None),
                 q((r.get('o_que') or '')[:900]), q(r.get('valor')),
                 q(r.get('unidade')), q(r.get('periodo')), q(classe),
                 q((r.get('citacao_literal') or '')[:900]), q(url),
                 q(r.get('publication_date')),
                 q((r.get('confidence') or '').upper()[:5] or None), q(naoprova),
                 q(bool(r.get('EXIGE_ROTA_ITALIANA')))))
            conta['espera_' + destino] += 1

    A('\ncommit;\n')

    os.makedirs(DESTINO, exist_ok=True)
    nome = 'IT-LASTMILE-%s.sql' % HOJE
    p = os.path.join(DESTINO, nome)
    open(p, 'w', encoding='utf-8').write(''.join(L))

    print('gravado: %s · %.0f KB' % (os.path.relpath(p, ROOT),
                                     os.path.getsize(p) / 1024))
    print('fontes externas: %d · testes de acesso: %d' % (len(vistas), n_testes))
    print('estatistica agricola: %d linhas' % n_est)
    print('por tabela:', dict(conta))


if __name__ == '__main__':
    main()
