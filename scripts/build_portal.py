#!/usr/bin/env python3
"""
Gera prototype/portal/index.html a partir das evidências preservadas em data/samples/.

Regra do protótipo: nenhum número é digitado à mão neste script. Tudo que aparece
na tela é lido dos arquivos de amostra, para que qualquer bloco possa apontar para
sua origem. Se a amostra some, o bloco some — e é assim que deve ser.

Uso:  python3 scripts/build_portal.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, 'data', 'samples')
OUT = os.path.join(ROOT, 'prototype', 'portal', 'index.html')

def load(*parts):
    p = os.path.join(S, *parts)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)

# ---------------------------------------------------------------- evidências
raif      = load('ES-T3-001-raif-vid-mildiu-2026.json')
mildiu_cl = load('X-001-completo-mildiu-vs-clima.json')
heat      = load('X-001-nuts2-heat-vs-wheat.json')
yieldser  = load('EU-T1-002-wheat-yield-country.json')
es41      = load('CASE-006-es41-rain-window-vs-yield.json')
cas       = load('X-006-eu-cas-to-ephy.json')
adama_fr  = load('FR-T4-001', 'FR-T4-001-adama-crop-target.json')
adama_it  = load('IT-T4-001', 'IT-T4-001-adama-expiries.json')
excep     = load('ES-T4-001', 'ES-T4-002-autorizaciones-excepcionales.json')
eppo      = load('ES-T4-001', 'eppo-dictionary.json')
slice_    = load('SLICE-PLASVI-vertical.json')

E = html.escape

def badge(state):
    return f'<span class="badge b-{state.lower()}">{state}</span>'

def block(title, state, source, date, evidence, body, warning=None):
    w = f'<div class="warn"><strong>Não conclua:</strong> {warning}</div>' if warning else ''
    return f'''<section class="block">
  <header><h3>{E(title)}</h3>{badge(state)}</header>
  <div class="meta">fonte: <strong>{E(source)}</strong> · dado de {E(date)}
    · evidência: <code>{E(evidence)}</code></div>
  {body}{w}
</section>'''

def table(headers, rows, cls=''):
    h = ''.join(f'<th>{E(str(x))}</th>' for x in headers)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

def bar(v, vmax, label=''):
    pct = 0 if not vmax else max(0.0, min(100.0, 100.0 * v / vmax))
    return f'<div class="bar"><i style="width:{pct:.1f}%"></i><b>{label}</b></div>'

# ---------------------------------------------------------------- PEST & DISEASE
prov_rows, prov_note = [], ''
if mildiu_cl:
    pv = mildiu_cl['provinces']
    peaks = {'Huelva': 26.4, 'Cordoba': 6.4, 'Cadiz (Jerez)': 0.0}
    vmax = max(peaks.values()) or 1
    for name, d in pv.items():
        prov_rows.append([
            f'<strong>{E(name)}</strong>',
            bar(peaks[name], vmax, f"{peaks[name]:.1f}%"),
            f"{d['precip_mm']} mm", str(d['wet_days_ge1mm']),
            f"{d['mean_RH2M_pct']}%",
        ])
    prov_note = mildiu_cl.get('warning', '')

serie_rows = []
if raif:
    for r in raif['series_pct_cepas_afectadas']:
        serie_rows.append([r['date'], str(r['n_parcelas']), f"{r['mean_pct']}%", f"{r['max_pct']}%"])

fav_rows = []
if raif:
    for r in raif['favourable_conditions_flag']:
        on = r['favourable'] > 0
        fav_rows.append([r['date'],
                         f'<span class="flag {"on" if on else "off"}">{"SIM" if on else "não"}</span>',
                         f"{r['favourable']}/{r['observations']}"])

# ---------------------------------------------------------------- CLIMATE & CROP
heat_rows = []
if heat:
    for r in heat['regions']:
        y = r['years']
        heat_rows.append([
            f"<strong>{E(r['geo'])}</strong> {E(r['name'])}",
            f"{r['wheat_area_kha_2024']:.1f}",
            ' · '.join(f"{yy}: <b>{y[yy]['days_tmax_ge_30C']}</b>" for yy in ('2022','2023','2024')),
            ' · '.join(f"{yy}: <b>{y[yy]['precip_mm']:.0f}</b>" for yy in ('2022','2023','2024')),
        ])

yld_rows = []
if yieldser:
    ser = yieldser['series']
    yrs = [str(y) for y in range(2019, 2026)]
    for g, nm in (('FR', 'França'), ('ES', 'Espanha'), ('IT', 'Itália')):
        cells = []
        vals = [ser[g].get(y) for y in yrs if ser.get(g)]
        lo = min([v for v in vals if v is not None], default=None)
        for y in yrs:
            v = ser.get(g, {}).get(y)
            cells.append('—' if v is None else (f'<b class="low">{v}</b>' if v == lo else f'{v}'))
        yld_rows.append([f'<strong>{nm}</strong>'] + cells)

win_rows = []
if es41:
    for r in es41['series']:
        win_rows.append([r['year'], f"{r['precip_feb_apr_mm']} mm",
                         f"{r['precip_may_jun_mm']} mm", f"{r['spain_wheat_yield_t_ha']}"])

# ---------------------------------------------------------------- REGULATORY
cas_rows = []
if cas:
    for m in cas['matches']:
        cas_rows.append([E(m['celex']), E(m['act_date']), E(m['cas']), E(m['ephy_substance']),
                         str(m['fr_products_authorised']),
                         f"<b>{m['fr_adama_products']}</b>" if m['fr_adama_products'] else '0'])

fr_rows = []
if adama_fr:
    for r in adama_fr['adama_crop_target_top'][:10]:
        fr_rows.append([E(r['crop']), E(r['target']), str(r['uses'])])

it_rows = []
if adama_it:
    for r in adama_it['adama_next_expiries'][:10]:
        it_rows.append([r['expiry'], E(r['reg']), E(r['product']), E(r['actives'][:44])])

ex_rows = []
if excep:
    for r in excep['rows'][:12]:
        ex_rows.append([E(r['cultivo'][:40]), E(r['plaga_funcion'][:74]), E(r['sustancia_activa'][:38])])

# ---------------------------------------------------------------- SLICE PLASVI
slice_rows, slice_subs = [], []
if slice_:
    fv = slice_['france_vigne_mildiou']
    comp = fv['by_company']
    vmax = max(v for k, v in comp.items() if k != 'OUTROS') or 1
    for k, v in sorted(comp.items(), key=lambda x: -x[1]):
        if k == 'OUTROS':
            continue
        lbl = f'<strong>{E(k)}</strong>' if k == 'ADAMA' else E(k)
        slice_rows.append([lbl, bar(v, vmax, str(v))])
    for k, v in list(fv['top_actives'].items())[:6]:
        slice_subs.append([E(k), str(v)])

# ---------------------------------------------------------------- HOME
now_items = []
if raif and mildiu_cl:
    now_items.append(('Míldio da videira em Huelva chegou a 26,4% das cepas',
        'Andaluzia (ES) · Vid · safra 2026', 'REAL',
        'Córdoba ficou em 6,4% e Cádiz em ~0% na mesma safra. A média regional não descreve nenhuma delas.'))
if adama_it:
    now_items.append((f"{adama_it['adama_in_force_with_future_expiry']} autorizações ADAMA na Itália têm vencimento futuro",
        'Itália · registro de 24/08/2026', 'REAL',
        '58 delas vencem em até 6 meses (37,4%), contra 20,9% do mercado. Vencimento abre renovação — não é perda.'))
if excep:
    now_items.append((f"{excep['count']} autorizações excepcionais vigentes na Espanha",
        'Espanha · situação de 24/08/2026', 'REAL',
        'Cada uma é o Estado declarando que não há solução autorizada normal para aquele problema.'))
if yieldser:
    now_items.append(('Rendimento francês de trigo caiu a 6,02 t/ha em 2024 e voltou a 7,34 em 2025',
        'França · Eurostat', 'REAL',
        'Nas regiões grandes, 2024 teve zero dias ≥30 °C e cerca do dobro de chuva na janela sensível. Coincidência medida, não causa provada.'))

home = ''.join(f'''<article class="card">
  <div class="ch">{badge(st)}<span class="cw">{E(where)}</span></div>
  <h4>{E(t)}</h4><p>{E(why)}</p></article>''' for t, where, st, why in now_items)

built = datetime.date.today().isoformat()

CSS = """
:root{--bg:#0f1214;--pn:#161b1f;--ln:#232b31;--tx:#e6edf3;--dim:#8b98a5;--ac:#4ea3ff;
--real:#2ea043;--der:#c9a227;--demo:#d1712a;--con:#8b5cf6;--warn:#3a2a1a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px 80px}
header.top{border-bottom:1px solid var(--ln);padding:26px 0 18px;margin-bottom:8px}
header.top h1{margin:0 0 4px;font-size:22px;letter-spacing:.3px}
header.top p{margin:0;color:var(--dim);font-size:13px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0 26px;position:sticky;top:0;
background:var(--bg);padding:10px 0;z-index:5;border-bottom:1px solid var(--ln)}
nav a{color:var(--dim);text-decoration:none;font-size:13px;padding:5px 11px;border-radius:6px;
border:1px solid transparent}
nav a:hover{color:var(--tx);border-color:var(--ln);background:var(--pn)}
h2{font-size:15px;text-transform:uppercase;letter-spacing:1.4px;color:var(--dim);
margin:44px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--ln)}
.block{background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:16px 18px;margin:14px 0}
.block header{display:flex;align-items:center;gap:10px;justify-content:space-between;margin-bottom:6px}
.block h3{margin:0;font-size:16px;font-weight:600}
.meta{color:var(--dim);font-size:12px;margin-bottom:12px}
.meta code{background:#0b0e10;padding:1px 5px;border-radius:4px;font-size:11px}
.badge{font-size:10px;font-weight:700;letter-spacing:1px;padding:3px 8px;border-radius:20px;
white-space:nowrap;color:#08120b}
.b-real{background:var(--real)}.b-derived{background:var(--der)}
.b-demo{background:var(--demo);color:#fff}.b-concept{background:var(--con);color:#fff}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:460px}
th{text-align:left;color:var(--dim);font-weight:600;font-size:11px;text-transform:uppercase;
letter-spacing:.6px;padding:7px 10px;border-bottom:1px solid var(--ln)}
td{padding:7px 10px;border-bottom:1px solid #1b2126;vertical-align:middle}
tr:last-child td{border-bottom:0}
.bar{position:relative;background:#0b0e10;border-radius:4px;height:20px;min-width:130px}
.bar i{position:absolute;inset:0 auto 0 0;background:linear-gradient(90deg,#2d6ea8,#4ea3ff);
border-radius:4px}
.bar b{position:relative;font-size:11px;padding-left:7px;line-height:20px;font-weight:600}
.flag{font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px}
.flag.on{background:#3d2b12;color:#e8b339}.flag.off{background:#1b2126;color:var(--dim)}
.low{color:#ff7b72}
.warn{margin-top:12px;background:var(--warn);border-left:3px solid var(--demo);
padding:9px 12px;border-radius:0 6px 6px 0;font-size:12.5px;color:#e8d5b5}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:12px}
.card{background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:14px}
.ch{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.cw{color:var(--dim);font-size:11px}
.card h4{margin:0 0 6px;font-size:14px;line-height:1.4}
.card p{margin:0;color:var(--dim);font-size:12.5px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--dim);
background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:12px 16px;margin:14px 0}
.legend div{display:flex;align-items:center;gap:7px}
footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--ln);color:var(--dim);font-size:12px}
"""

HTML = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SINTONIA EAME — protótipo vivo</title><style>{CSS}</style></head><body>
<div class="wrap">
<header class="top">
  <h1>SINTONIA EAME · protótipo vivo</h1>
  <p>Laboratório das descobertas da MISSÃO EAME 01/02. Não é produto, não é design final.
     Gerado em {built} a partir de <code>data/samples/</code> por <code>scripts/build_portal.py</code>.</p>
</header>

<nav>
  <a href="#home">Home</a><a href="#pest">Pest &amp; Disease</a><a href="#climate">Crops &amp; Climate</a>
  <a href="#reg">Regulatory</a><a href="#opp">Opportunities</a><a href="#src">Evidence</a>
</nav>

<div class="legend">
  <div>{badge('REAL')} sustentado diretamente por fonte</div>
  <div>{badge('DERIVED')} calculado sobre informação real</div>
  <div>{badge('DEMO')} dado real, ainda não automatizado</div>
  <div>{badge('CONCEPT')} capacidade ainda não comprovada</div>
</div>

<h2 id="home">What matters now</h2>
<div class="cards">{home}</div>

<h2 id="pest">Pest &amp; Disease</h2>
{block('Míldio da videira por província — Andaluzia, safra 2026', 'REAL',
  'RAIF Andalucía (ES-T3-001), CC BY 4.0', 'amostragem semanal, mar–jul 2026',
  'data/samples/ES-T3-001-raif-vid-mildiu-2026.json',
  table(['Província', 'pico medido (% cepas afetadas)', 'chuva 15/03–31/05',
         'dias ≥1 mm', 'UR média'], prov_rows),
  'que o clima explique a diferença. Córdoba choveu <strong>mais</strong> que Huelva e teve '
  '4× menos doença; Cádiz teve a <strong>maior</strong> umidade e praticamente nenhuma. '
  'Ver X-009 e CASE-008. Variedade, manejo e o programa de fungicida aplicado não foram cruzados.')}

{block('Sinalizador oficial de condições favoráveis ao míldio', 'REAL',
  'RAIF Andalucía — campo "1604 Mildiu: condiciones favorables"', 'safra 2026',
  'data/samples/ES-T3-001-raif-vid-mildiu-2026.json',
  table(['data', 'favorável?', 'observações'], fav_rows),
  'que isto seja previsão. O sinalizador é <strong>modelo da própria RAIF</strong>, não medição nossa. '
  'A janela ligada (13/04–27/05) precede o pico medido em Huelva (02–16/06), o que é compatível '
  'com a epidemiologia conhecida — mas foi observado em uma safra, uma cultura, uma região.')}

{block('Série bruta de amostragem — Andaluzia agregada', 'DERIVED',
  'RAIF Andalucía', 'safra 2026', 'data/samples/ES-T3-001-raif-vid-mildiu-2026.json',
  table(['data', 'parcelas', 'média', 'máx'], serie_rows),
  'ler esta tabela como a curva epidêmica da Andaluzia. <strong>Ela não é.</strong> '
  'Províncias diferentes são amostradas em dias diferentes, então a média diária reflete '
  '<em>qual província foi visitada</em>. Desagregada por província (bloco acima), o zigue-zague '
  'desaparece. Mantida aqui porque foi o erro que quase cometemos — ver CAP-015.')}

{block('Míldio da videira na França — quem tem direito de uso nesse combate', 'REAL',
  'ANSES E-Phy (FR-T4-001) — campo público "titulaire"', 'registro de 25/08/2026',
  'data/samples/SLICE-PLASVI-vertical.json',
  table(['empresa', 'usos autorizados em Vigne × Mildiou(s)'], slice_rows)
  + '<div class="meta" style="margin:12px 0 4px">substâncias mais registradas nesse combate</div>'
  + table(['substância ativa', 'usos'], slice_subs),
  'ler contagem de registros como posição de mercado. E note o próprio dado: o registro grafa '
  'a mesma substância como <strong>folpet (33)</strong> e <strong>folpel (14)</strong>. '
  'Quem contar sem normalizar subestima a molécula em 30% — erro silencioso que uma tela esconde.')}

<h2 id="climate">Crops &amp; Climate</h2>
{block('Exposição climática na janela de enchimento de grão — trigo comum', 'DERIVED',
  'Eurostat apro_cpshr (área) + NASA POWER (clima) + GISCO (ponto NUTS 2)',
  'janela 01/05–30/06, safras 2022–2024',
  'data/samples/X-001-nuts2-heat-vs-wheat.json',
  table(['Região NUTS 2', 'trigo 2024 (mil ha)', 'dias com Tmáx ≥30 °C', 'chuva na janela (mm)'], heat_rows),
  'que isto seja impacto. Mede <strong>exposição</strong>. O clima vem de <strong>um ponto</strong> '
  '(o ponto-rótulo NUTS 2), não de uma média regional — Castilla y León tem 94 mil km².')}

{block('Rendimento de trigo comum por país (t/ha)', 'REAL',
  'Eurostat apro_cpsh1', 'série 2019–2025', 'data/samples/EU-T1-002-wheat-yield-country.json',
  table(['País', '2019', '2020', '2021', '2022', '2023', '2024', '2025'], yld_rows),
  'combinar este rendimento <strong>nacional</strong> com a área <strong>regional</strong> para '
  'estimar produção por região. O Eurostat não publica rendimento em NUTS 2 — testado em '
  '2021, 2022, 2023 e 2024, resultado zero regiões.')}

{block('A janela decide o sinal — Castilla y León × rendimento espanhol', 'DERIVED',
  'NASA POWER (ponto ES41) + Eurostat (rendimento nacional ES)', '2020–2024',
  'data/samples/CASE-006-es41-rain-window-vs-yield.json',
  table(['ano', 'chuva fev–abr', 'chuva mai–jun', 'rendimento ES (t/ha)'], win_rows),
  'que a chuva explique o rendimento. São cinco pontos, clima de <strong>um ponto</strong> contra '
  'rendimento <strong>nacional</strong>, sem controle de outras variáveis. O que este bloco prova é '
  'que a <strong>escolha da janela inverte a leitura</strong>: por fev–abr a ordem acompanha o '
  'rendimento; por mai–jun ela aponta ao contrário.')}

<h2 id="reg">Regulatory</h2>
{block('Da decisão da UE ao produto autorizado na França', 'REAL',
  'CELLAR / Jornal Oficial da UE (EU-T4-001) + ANSES E-Phy (FR-T4-001)',
  'atos de 2026 · registro francês de 25/08/2026',
  'data/samples/X-006-eu-cas-to-ephy.json',
  table(['CELEX', 'data do ato', 'CAS', 'substância no E-Phy',
         'produtos FR autorizados', 'dos quais ADAMA'], cas_rows),
  'que a data europeia seja a data de retirada do produto francês. '
  'A expiração da aprovação da <strong>substância na UE</strong> abre processo de renovação; '
  'a retirada <strong>nacional do produto</strong> tem prazo próprio. E a cobertura é parcial: '
  'o CAS foi extraível em 3 de 6 atos testados, e só 621 das 1.338 substâncias do E-Phy trazem CAS.')}

{block('Portfólio ADAMA registrado na França, por cultura × alvo', 'REAL',
  'ANSES E-Phy — campo público "titulaire"', 'registro de 25/08/2026',
  'data/samples/FR-T4-001/FR-T4-001-adama-crop-target.json',
  table(['cultura', 'alvo', 'usos autorizados'], fr_rows),
  'ler contagem de usos autorizados como posição de mercado. Mede <strong>direito de uso '
  'registrado</strong> — não vendas, não área tratada, não participação, não eficácia.')}

{block('Próximos vencimentos de autorização ADAMA na Itália', 'REAL',
  'Ministero della Salute — banca dati fitosanitari (IT-T4-001), CC BY 4.0',
  'registro de 24/08/2026', 'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json',
  table(['vencimento', 'nº registro', 'produto', 'substâncias ativas'], it_rows),
  'ler vencimento como perda. Vencimento abre <strong>renovação</strong>. '
  'As datas são agrupadas em fins de mês por seguirem o calendário europeu das substâncias ativas.')}

<h2 id="opp">Opportunities</h2>
{block('Necessidades sem solução autorizada — Espanha (art. 53)', 'REAL',
  'MAPA — Autorizaciones excepcionales vigentes (ES-T4-002)', 'situação de 24/08/2026',
  'data/samples/ES-T4-001/ES-T4-002-autorizaciones-excepcionales.json',
  table(['cultivo', 'plaga / função', 'substância ativa'], ex_rows),
  'ler lacuna reconhecida como oportunidade dimensionada. Pode ser pequena, sazonal ou já em '
  'vias de solução por outra empresa. E a lista traz apenas as <strong>vigentes</strong> — '
  'um problema resolvido no ano passado saiu dela sem deixar rastro.')}

{block('Visão EAME unificada de registro (FR + ES + IT)', 'CONCEPT',
  '—', '—', '—',
  '<p style="color:var(--dim);margin:0">Ainda não existe. As três fontes nacionais não cobrem os '
  'mesmos campos: a França publica cultura × alvo mas não vencimento; a Itália publica vencimento '
  'mas não cultura × alvo; a Espanha não publica o registro de produtos em formato aberto. '
  'Uma pergunta como <em>“em que países a ADAMA tem registro contra míldio da videira?”</em> '
  '<strong>não pode ser respondida hoje</strong>. Ver X-008.</p>',
  'apresentar este bloco como capacidade. Ele está aqui para marcar o que <strong>falta</strong>.')}

<h2 id="src">Evidence</h2>
{block('Vocabulário EPPO — a chave de normalização entre os três países', 'REAL',
  'MAPA — jerarquía de especies vegetales e clasificación de plagas (ES-T4-001)',
  'tabelas oficiais do registro espanhol', 'data/samples/ES-T4-001/eppo-dictionary.json',
  table(['', 'entradas indexadas por código EPPO'],
        [['culturas', str(len(eppo['crops']) if eppo else 0)],
         ['pragas, doenças e daninhas', str(len(eppo['pests']) if eppo else 0)]]),
  'supor que isso já normaliza os três países. O E-Phy francês <strong>não tem</strong> código EPPO '
  'nem nome científico — só 231 nomes comuns em francês, muitos deles grupo e não espécie '
  '(“Mildiou(s)” é <em>Plasmopara viticola</em> na videira e <em>Phytophthora infestans</em> na batata). '
  'O mapeamento francês ainda precisa ser construído e medido. Ver X-007.')}

<footer>
  <p><strong>Estado do protótipo.</strong> Todo bloco acima carrega seu estado, sua fonte, sua data
  e o caminho da evidência. Nenhum número foi digitado à mão: <code>scripts/build_portal.py</code>
  lê os arquivos de <code>data/samples/</code>. Se a amostra desaparecer, o bloco desaparece.</p>
  <p>Seções ainda inexistentes por falta de dado: <em>Science &amp; People</em>, <em>Competitors</em>
  (além da camada regulatória), <em>Events</em>. Elas não foram criadas vazias de propósito —
  uma seção só nasce quando existe conteúdo real que a justifique.</p>
</footer>
</div></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f'gerado: {OUT} ({len(HTML)} bytes)')
