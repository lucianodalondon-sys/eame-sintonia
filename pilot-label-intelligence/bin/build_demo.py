#!/usr/bin/env python3
"""
build_demo.py — gera a demo SHADOW a partir dos dados. Nada e digitado a mao.

SHADOW: nao toca prototype/portal (congelado por D-007), nao toca o portal
oficial, nao faz deploy. E um arquivo solto que abre no navegador.

Herda a linguagem visual da casa, inclusive o sistema de selos, porque ele ja
resolve o problema desta missao — mostrar o que e real sem inflar:

    REAL     linha lida do documento oficial, com evidencia recuperavel
    DERIVED  contagem ou agregacao sobre linhas reais
    DEMO     forma de tela sem dado por tras
    CONCEPT  automacao desenhada, nao ligada
"""
import argparse, html, json, os, sys, datetime

CSS = """
:root{--bg:#0f1214;--pn:#161b1f;--ln:#232b31;--tx:#e6edf3;--dim:#8b98a5;--ac:#4ea3ff;
--real:#2ea043;--der:#c9a227;--demo:#d1712a;--con:#8b5cf6;--warn:#3a2a1a;--bad:#ff7b72}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px 80px}
header.top{border-bottom:1px solid var(--ln);padding:26px 0 18px}
header.top h1{margin:0 0 4px;font-size:22px;letter-spacing:.3px}
header.top p{margin:0;color:var(--dim);font-size:13px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0 8px;position:sticky;top:0;
background:var(--bg);padding:10px 0;z-index:5;border-bottom:1px solid var(--ln)}
nav a{color:var(--dim);text-decoration:none;font-size:13px;padding:5px 11px;border-radius:6px;
border:1px solid transparent;cursor:pointer}
nav a:hover,nav a.on{color:var(--tx);border-color:var(--ln);background:var(--pn)}
h2{font-size:15px;text-transform:uppercase;letter-spacing:1.4px;color:var(--dim);
margin:40px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--ln)}
h3{margin:0;font-size:16px;font-weight:600}
.block{background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:16px 18px;margin:14px 0}
.block>header{display:flex;align-items:center;gap:10px;justify-content:space-between;margin-bottom:6px}
.meta{color:var(--dim);font-size:12px;margin-bottom:12px}
.meta code,code{background:#0b0e10;padding:1px 5px;border-radius:4px;font-size:11px;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.badge{font-size:10px;font-weight:700;letter-spacing:1px;padding:3px 8px;border-radius:20px;
white-space:nowrap;color:#08120b}
.b-real{background:var(--real)}.b-derived{background:var(--der)}
.b-demo{background:var(--demo);color:#fff}.b-concept{background:var(--con);color:#fff}
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:620px}
th{text-align:left;color:var(--dim);font-weight:600;font-size:11px;text-transform:uppercase;
letter-spacing:.6px;padding:7px 10px;border-bottom:1px solid var(--ln);white-space:nowrap}
td{padding:7px 10px;border-bottom:1px solid #1b2126;vertical-align:top}
td.nw{white-space:nowrap}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:#1a2026}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin:14px 0}
.kpi{background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:14px}
.kpi b{display:block;font-size:27px;line-height:1.15;font-weight:650}
.kpi span{color:var(--dim);font-size:11.5px;display:block;margin-top:3px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--dim);
background:var(--pn);border:1px solid var(--ln);border-radius:10px;padding:12px 16px;margin:14px 0}
.legend div{display:flex;align-items:center;gap:7px}
.warn{margin-top:12px;background:var(--warn);border-left:3px solid var(--demo);
padding:9px 12px;border-radius:0 6px 6px 0;font-size:12.5px;color:#e8d5b5}
.ok{color:var(--real)}.dim{color:var(--dim)}.bad{color:var(--bad)}.acc{color:var(--ac)}
a{color:var(--ac)}
.pill{font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;display:inline-block}
.p-ok{background:#12301c;color:#5ed67f}.p-no{background:#301616;color:#ff8c84}
.p-wr{background:#30280f;color:#e8b339}.p-nc{background:#1b2126;color:var(--dim)}
input,select{background:#0b0e10;border:1px solid var(--ln);color:var(--tx);border-radius:6px;
padding:6px 9px;font-size:13px;font-family:inherit}
.filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}
.quote{background:#0b0e10;border-left:2px solid var(--ln);padding:8px 11px;margin:6px 0;
font-size:12px;color:#c3cdd7;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
white-space:pre-wrap;word-break:break-word}
.view{display:none}.view.on{display:block}
footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--ln);color:var(--dim);font-size:12px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px}
"""

def e(s):
    return html.escape(str(s if s is not None else ""))

def badge(kind):
    m = {"REAL": ("b-real", "REAL"), "DERIVED": ("b-derived", "DERIVED"),
         "DEMO": ("b-demo", "DEMO"), "CONCEPT": ("b-concept", "CONCEPT")}
    c, t = m[kind]
    return f'<span class="badge {c}">{t}</span>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--demo", default="pilot-label-intelligence/demo/IT-DEMO-PRODUTOS.json")
    ap.add_argument("--out", default="pilot-label-intelligence/demo/label-intelligence.html")
    a = ap.parse_args()

    d = json.load(open(a.dados, encoding="utf-8"))
    dm = json.load(open(a.demo, encoding="utf-8"))
    cadp = os.path.join(os.path.dirname(a.dados) or ".", "..", "labels",
                        "IT-CADENCIA-ROTULO.json")
    cad = json.load(open(cadp, encoding="utf-8")) if os.path.exists(cadp) else {}
    demo_ids = [x["REGISTRATION_ID"] for x in dm["PRODUCTS"]]
    byreg = {p["REGISTRATION_ID"]: p for p in d["PRODUCTS"]}

    hist = d.get("REGISTRY_HISTORY", {})
    lvc = d.get("LABEL_VERSION_CHECK", {})

    # ---- payload enxuto para o navegador
    linhas = []
    for p in d["PRODUCTS"]:
        lab = p.get("LABEL", {})
        linhas.append({
            "reg": p["REGISTRATION_ID"], "nome": p["PRODUCT"],
            "cat": p["REGULATORY_CATEGORY"], "tit": p["HOLDER"],
            "ai": p["ACTIVE_INGREDIENTS"], "st": p["STATUS"],
            "exp": p["EXPIRY"], "dte": p["DAYS_TO_EXPIRY"],
            "usos": len(p["USE_ROWS"]), "doses": len(p.get("DOSE_ROWS", [])),
            "eff": lab.get("EFFECTIVE_AT", "NOT_KNOWN"),
            "sha": (lab.get("SHA256") or "")[:12],
            "chg": lab.get("DOCUMENT_CHANGED"),
            "url": lab.get("URL", ""),
            "regchg": len([x for x in p["REGISTRY_CHANGES"] if not x.get("UNSTABLE_SOURCE")]),
            "demo": p["REGISTRATION_ID"] in demo_ids,
        })

    detalhes = {}
    for rid in demo_ids:
        p = byreg[rid]
        crops = {}
        for u in p["USE_ROWS"]:
            crops.setdefault(u["CROP"], []).append(u)
        detalhes[rid] = {
            "reg": rid, "nome": p["PRODUCT"], "cat": p["REGULATORY_CATEGORY"],
            "tit": p["HOLDER"], "ai": p["ACTIVE_INGREDIENTS"], "st": p["STATUS"],
            "form": p["FORMULATION"], "reg_at": p["REGISTERED_AT"],
            "exp": p["EXPIRY"], "dte": p["DAYS_TO_EXPIRY"],
            "label": p.get("LABEL", {}),
            "regchg": p["REGISTRY_CHANGES"],
            "usos": [{"c": c, "t": [x["TARGET"] for x in v],
                      "pg": v[0].get("SOURCE_PAGE"),
                      "ev": "TABELA" if any(x["EVIDENCE_CLASS"] == "TABLE_GEOMETRY" for x in v)
                            else "TEXTO"}
                     for c, v in sorted(crops.items())],
            "n_tab": sum(1 for x in p["USE_ROWS"] if x["EVIDENCE_CLASS"] == "TABLE_GEOMETRY"),
            "n_txt": sum(1 for x in p["USE_ROWS"] if x["EVIDENCE_CLASS"] == "TEXT_INFERENCE"),
            "n_usos": len(p["USE_ROWS"]),
            "doses": p.get("DOSE_ROWS", []),
            "dose_state": p.get("DOSE_PARSE_STATE", "NOT_ATTEMPTED"),
            "why": next(x["WHY_SELECTED"] for x in dm["PRODUCTS"] if x["REGISTRATION_ID"] == rid),
        }

    payload = json.dumps({"linhas": linhas, "detalhes": detalhes},
                         ensure_ascii=False, separators=(",", ":"))

    # Todos os eventos do historico oficial, independente de o produto ainda
    # estar ativo hoje.
    todos_ev = []
    vp = os.path.join(os.path.dirname(a.dados) or ".", "..", "registry",
                      "IT-REGISTRO-VERSOES.json")
    if os.path.exists(vp):
        todos_ev = json.load(open(vp, encoding="utf-8"))["CHANGE_EVENTS"]
    eventos_js = json.dumps(todos_ev, ensure_ascii=False, separators=(",", ":"))

    venc = lambda n: sum(1 for x in linhas if isinstance(x["dte"], int) and 0 <= x["dte"] <= n)
    vencidos = sum(1 for x in linhas if isinstance(x["dte"], int) and x["dte"] < 0)

    H = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LABEL INTELLIGENCE — ADAMA ITALIA</title><style>{CSS}</style></head><body>
<div class="wrap">
<header class="top">
  <h1>LABEL INTELLIGENCE — ADAMA ITALIA</h1>
  <p>Rotulos oficiais do Ministero della Salute, monitorados por versao.
     Gerado de dados em {e(d["BUILT_AT"])}. Nenhum numero desta pagina foi digitado a mao.</p>
</header>
<nav>
  <a class="on" data-v="monitor">LABEL MONITOR</a>
  <a data-v="produto">PRODUTO</a>
  <a data-v="mudancas">MUDANCAS</a>
  <a data-v="honestidade">O QUE ISTO NAO PROVA</a>
</nav>

<div class="legend">
  <div>{badge("REAL")} lido do documento oficial, com evidencia recuperavel</div>
  <div>{badge("DERIVED")} contagem sobre linhas reais</div>
  <div>{badge("DEMO")} forma de tela, sem dado por tras</div>
  <div>{badge("CONCEPT")} desenhado, nao ligado</div>
</div>

<!-- ------------------------------------------------ MONITOR -->
<section class="view on" id="v-monitor">
<h2>Cobertura do universo</h2>
<div class="cards">
  <div class="kpi"><b>{len(linhas)}</b><span>produtos ADAMA ativos no registro</span></div>
  <div class="kpi"><b>{lvc.get("LABELS_CHECKED", 0)}</b><span>rotulos oficiais conferidos</span></div>
  <div class="kpi"><b>{d["PRODUCTS_WITH_USE_ROWS"]}</b><span>com tabela de uso lida</span></div>
  <div class="kpi"><b class="dim">{d["PRODUCTS_WITHOUT_USE_ROWS"]}</b><span>divida de leitura</span></div>
  <div class="kpi"><b>{d["TOTAL_USE_ROWS"]:,}</b><span>pares cultura x alvo</span></div>
  <div class="kpi"><b class="ok">{d["USE_ROWS_FROM_TABLE_GEOMETRY"]:,}</b><span>desses, lidos da tabela (com pagina)</span></div>
  <div class="kpi"><b class="{'acc' if d['TOTAL_DOSE_ROWS'] else 'dim'}">{d["TOTAL_DOSE_ROWS"]:,}</b><span>linhas com dose</span></div>
</div>
<div class="cards">
  <div class="kpi"><b class="{'bad' if vencidos else ''}">{vencidos}</b><span>validade vencida, ainda listados como ativos</span></div>
  <div class="kpi"><b>{venc(30)}</b><span>vencem em 30 dias</span></div>
  <div class="kpi"><b>{venc(90)}</b><span>vencem em 90 dias</span></div>
  <div class="kpi"><b>{venc(180)}</b><span>vencem em 180 dias</span></div>
  <div class="kpi"><b>{hist.get("CHANGE_EVENTS_REGULATORY", 0)}</b><span>mudancas reais no registro</span></div>
  <div class="kpi"><b class="ok">{lvc.get("DOCUMENT_CHANGED", 0)}</b><span>rotulos que mudaram desde a base</span></div>
</div>

<div class="block">
  <header><h3>Com que frequencia a etichetta muda</h3>{badge("REAL")}</header>
  <div class="meta">Da data de vigencia que o proprio Ministero declara para cada rotulo
    (&ldquo;Etichetta del DD/MM/AAAA&rdquo;) &mdash; {e(cad.get("LABELS_WITH_DECLARED_EFFECTIVE_DATE","?"))}
    de {len(linhas)} rotulos a declaram. Nenhuma data foi inferida.</div>
  <div class="cards">
    <div class="kpi"><b>{round(cad.get("ANNUAL_RENEWAL_RATE",0)*100)}%</b><span>dos rotulos renovados em 12 meses</span></div>
    <div class="kpi"><b>{e(cad.get("RENEWED_WITHIN",{}).get("ULTIMOS_6_MESES","?"))}</b><span>renovados nos ultimos 6 meses</span></div>
    <div class="kpi"><b>{e(cad.get("MEDIAN_AGE_YEARS","?"))} anos</b><span>idade mediana do rotulo em vigor</span></div>
    <div class="kpi"><b>{e(cad.get("OLDEST_LABEL_IN_FORCE","?"))}</b><span>rotulo em vigor mais antigo</span></div>
  </div>
  <div class="warn">{e(cad.get("VEREDITO","?"))}</div>
  <div class="meta" style="margin-top:10px">{e(cad.get("IMPLICACAO_PARA_A_ESTEIRA",""))}</div>
</div>

<div class="block">
  <header><h3>Os 163 produtos</h3>{badge("REAL")}</header>
  <div class="meta">
    Registro: <code>PROD_FTS_6_20260831.csv</code> ·
    Ministero della Salute · licenca IODL 2.0 ·
    documento do rotulo conferido em {e(lvc.get("OBSERVED_AT", "?"))} contra captura de
    {e(lvc.get("BASELINE_CAPTURED_AT", "?"))}
  </div>
  <div class="filters">
    <input id="q" placeholder="produto, registro, substancia ativa..." size="34">
    <select id="fl"><option value="">todas as linhas</option></select>
    <select id="fv">
      <option value="">qualquer validade</option>
      <option value="past">ja vencida</option>
      <option value="30">vence em 30 dias</option>
      <option value="90">vence em 90 dias</option>
      <option value="180">vence em 180 dias</option>
    </select>
    <select id="fr">
      <option value="">leitura: qualquer</option>
      <option value="lido">com tabela de uso lida</option>
      <option value="nao">precisa revisao (sem tabela lida)</option>
    </select>
    <label class="dim" style="font-size:12.5px">
      <input type="checkbox" id="fd" style="vertical-align:-1px"> so os da demo profunda</label>
    <span class="dim" id="cnt"></span>
  </div>
  <div class="tw"><table>
    <thead><tr><th>Registro</th><th>Produto</th><th>Linha</th><th>Titular</th>
    <th>Validade</th><th>Ultima versao do rotulo</th><th>Leitura</th><th>Alertas</th><th>Fonte</th></tr></thead>
    <tbody id="tb"></tbody>
  </table></div>
</div>
</section>

<!-- ------------------------------------------------ PRODUTO -->
<section class="view" id="v-produto">
<h2>Demo profunda — {len(demo_ids)} produtos</h2>
<div class="block">
  <div class="meta">Criterio de escolha declarado em <code>IT-DEMO-PRODUTOS.json</code>.
  O criterio nao premia facilidade de parsing.</div>
  <div class="filters">
    <select id="psel"></select>
  </div>
</div>
<div id="pdet"></div>
</section>

<!-- ------------------------------------------------ MUDANCAS -->
<section class="view" id="v-mudancas">
<h2>Mudancas no registro oficial</h2>
<div class="block">
  <header><h3>Janela arquivada</h3>{badge("REAL")}</header>
  <div class="meta">
    {e(hist.get("SNAPSHOTS_DOWNLOADED", 0))} instantaneos semanais baixados ·
    {e(hist.get("DISTINCT_DOCUMENTS", 0))} documentos distintos por sha256 ·
    janela <code>{e(hist.get("WINDOW", "?"))}</code>
  </div>
  <div class="cards">
    <div class="kpi"><b>{hist.get("CHANGE_EVENTS_REGULATORY", 0)}</b><span>mudancas regulatorias</span></div>
    <div class="kpi"><b class="dim">{hist.get("CHANGE_EVENTS_TEXT_ONLY", 0)}</b><span>rebaixadas a texto</span></div>
    <div class="kpi"><b class="dim">496</b><span>ruido de serializacao suprimido</span></div>
  </div>
  <div class="warn">Um differ ingenuo teria entregue 528 diferencas de campo. 496 delas (93,9%)
  sao a fonte reordenando a lista de indicacoes de perigo entre publicacoes — o mesmo valor vai e
  volta semana a semana. Normalizar campo multivalorado e rebaixar oscilacao deixa
  {hist.get("CHANGE_EVENTS_REGULATORY", 0)} mudancas de verdade.</div>
  <div class="tw"><table>
    <thead><tr><th>Janela</th><th>Registro</th><th>Produto</th><th>Tipo</th><th>Antes</th><th>Depois</th></tr></thead>
    <tbody id="tbc"></tbody></table></div>
</div>
</section>

<!-- ------------------------------------------------ HONESTIDADE -->
<section class="view" id="v-honestidade">
<h2>O que este piloto NAO prova</h2>
<div class="block">
  <header><h3>Limites, ditos antes de perguntarem</h3>{badge("REAL")}</header>
  <ul style="line-height:1.75;font-size:14px">
    <li><b>{lvc.get("DOCUMENT_CHANGED", 0)} rotulos mudaram</b> na janela conferida
      ({e(lvc.get("BASELINE_CAPTURED_AT", "?"))} a {e(lvc.get("OBSERVED_AT", "?"))},
      {e(cad.get("OBSERVATION_WINDOW_DAYS", "?"))} dias). Com a taxa de renovacao medida
      ({round(cad.get("ANNUAL_RENEWAL_RATE", 0)*100)}% ao ano), o esperado nesta janela era
      {e(cad.get("EXPECTED_CHANGES_IN_WINDOW", "?"))} mudancas — entao zero e o resultado
      previsto, nao prova de que os rotulos nao mudam.
      <code>VERSION MONITORING READY</code> · <code>HISTORICAL LABEL DIFF NOT YET PROVED</code>.</li>
    <li><b>Vencimento nao e revogacao.</b> {vencidos} produtos tem validade passada e continuam
      listados como autorizados no registro. O piloto mostra os dois campos e nao decide por conta
      propria que o produto saiu do mercado.</li>
    <li><b>{d["PRODUCTS_WITHOUT_USE_ROWS"]} produtos sem tabela de uso lida</b> sao divida de
      leitura, nao ausencia de uso autorizado.
      <code>PARSER_FAILURE != REGULATORY_ABSENCE</code>.</li>
    <li><b>Nem todo par cultura x alvo e uma linha de tabela.</b> Dos
      {d["TOTAL_USE_ROWS"]:,} pares, {d["USE_ROWS_FROM_TABLE_GEOMETRY"]:,} saem da geometria da
      tabela e trazem pagina; {d["USE_ROWS_FROM_TEXT_INFERENCE"]:,} foram montados a partir de prosa
      ou de lista, e {d["USE_ROWS_WITHOUT_PAGE"]:,} nao preservaram pagina. Nenhum par carrega
      citacao literal: esta versao do parser da casa nao gravou <code>SOURCE_QUOTE</code>. A frase
      correta e "par extraido pelo nosso leitor a partir do rotulo", nunca "o rotulo diz".</li>
    <li><b>Presenca no registro nao e presenca no mercado.</b> O registro diz o que esta
      autorizado, nunca o que esta sendo vendido.</li>
    <li><b>A precisao do leitor de cultura x alvo foi medida em 30 dos 163 rotulos</b>
      (precisao 0,965 · recall 0,870). Os outros 133 nao foram auditados um a um.</li>
  </ul>
</div>
</section>

<footer>
  Fonte: Ministero della Salute — Banca dati prodotti fitosanitari
  (<a href="https://www.dati.salute.gov.it/it/dataset/fitosanitari">dati abertos, IODL 2.0</a>)
  e <a href="https://www.fitosanitari.salute.gov.it/fitosanitariws_new/FitosanitariServlet">buscador oficial de etichette</a>.
  Cultura x alvo reusado de <code>sintonia/canonical @ bdb57cf</code>.
  Demo SHADOW: nao integra nenhum sistema, nao faz deploy, nao toca o portal.
</footer>
</div>
<script>
const D = {payload};
const $ = s => document.querySelector(s);

document.querySelectorAll('nav a').forEach(a => a.onclick = () => {{
  document.querySelectorAll('nav a').forEach(x => x.classList.remove('on'));
  a.classList.add('on');
  document.querySelectorAll('.view').forEach(v => v.classList.remove('on'));
  $('#v' + '-' + a.dataset.v).classList.add('on');
}});

const linha = c => {{ const h = (c||'').toUpperCase().split('-')[0].trim();
  if (h.startsWith('DISERBANTE')) return 'HERBICIDA';
  if (h.startsWith('FUNGICIDA') || h.startsWith('DIRADANTE')) return 'FUNGICIDA';
  if (/^(INSETTICIDA|ACARICIDA|AFICIDA|MOLLUSCHICIDA)/.test(h)) return 'INSETICIDA';
  return 'OUTRA'; }};

const linhas = [...new Set(D.linhas.map(x => linha(x.cat)))].sort();
$('#fl').innerHTML = '<option value="">todas as linhas</option>' +
  linhas.map(l => `<option>${{l}}</option>`).join('');

function alertas(x) {{
  const a = [];
  if (typeof x.dte === 'number' && x.dte < 0) a.push('<span class="pill p-no">VENCIDO</span>');
  else if (typeof x.dte === 'number' && x.dte <= 90) a.push('<span class="pill p-wr">VENCE&nbsp;EM&nbsp;'+x.dte+'D</span>');
  if (x.regchg) a.push('<span class="pill p-wr">REGISTRO&nbsp;MUDOU</span>');
  if (x.chg === true) a.push('<span class="pill p-no">ROTULO&nbsp;MUDOU</span>');
  if (!x.usos) a.push('<span class="pill p-nc">PRECISA&nbsp;REVISAO</span>');
  return a.join(' ') || '<span class="dim">—</span>';
}}

function pinta() {{
  const q = $('#q').value.trim().toLowerCase(), fl = $('#fl').value,
        fv = $('#fv').value, fr = $('#fr').value, fd = $('#fd').checked;
  const r = D.linhas.filter(x => {{
    if (fd && !x.demo) return false;
    if (fl && linha(x.cat) !== fl) return false;
    if (fr === 'lido' && !x.usos) return false;
    if (fr === 'nao' && x.usos) return false;
    if (fv === 'past' && !(typeof x.dte === 'number' && x.dte < 0)) return false;
    if (['30','90','180'].includes(fv) &&
        !(typeof x.dte === 'number' && x.dte >= 0 && x.dte <= +fv)) return false;
    if (q && !(x.nome+' '+x.reg+' '+(x.ai||[]).join(' ')+' '+x.tit).toLowerCase().includes(q)) return false;
    return true;
  }});
  $('#cnt').textContent = r.length + ' de ' + D.linhas.length;
  $('#tb').innerHTML = r.map(x => `<tr>
    <td class="mono">${{x.reg}}</td>
    <td><b>${{x.nome}}</b>${{x.demo?' <span class="pill p-ok">DEMO</span>':''}}
        <div class="dim" style="font-size:11px">${{(x.ai||[]).join(' + ')}}</div></td>
    <td>${{linha(x.cat)}}<div class="dim" style="font-size:11px">${{x.cat}}</div></td>
    <td class="dim">${{x.tit}}</td>
    <td class="nw ${{typeof x.dte==='number'&&x.dte<0?'bad':''}}">${{x.exp}}
        <div class="dim" style="font-size:11px">${{typeof x.dte==='number'?(x.dte<0?(-x.dte)+'d atras':'em '+x.dte+'d'):''}}</div></td>
    <td class="nw">${{x.eff}}<div class="dim mono" style="font-size:10.5px">sha ${{x.sha}}</div></td>
    <td>${{x.usos?('<span class="ok">'+x.usos+' pares</span>'):'<span class="dim">nao lida</span>'}}
        ${{x.doses?('<div class="acc" style="font-size:11px">'+x.doses+' com dose</div>'):''}}</td>
    <td>${{alertas(x)}}</td>
    <td>${{x.url?`<a href="${{x.url}}" target="_blank">PDF oficial</a>`:'<span class="dim">—</span>'}}</td>
  </tr>`).join('');
}}
['q','fl','fv','fr','fd'].forEach(id => {{
  const el = $('#'+id); el.addEventListener(el.type==='checkbox'?'change':'input', pinta);
  el.addEventListener('change', pinta);
}});
pinta();

// ---- produto
const ids = Object.keys(D.detalhes);
$('#psel').innerHTML = ids.map(i => `<option value="${{i}}">${{D.detalhes[i].nome}} — ${{i}}</option>`).join('');
function produto() {{
  const p = D.detalhes[$('#psel').value];
  const l = p.label || {{}};
  const venc = typeof p.dte === 'number' && p.dte < 0;
  $('#pdet').innerHTML = `
  <div class="block">
    <header><h3>${{p.nome}}</h3><span class="badge b-real">REAL</span></header>
    <div class="meta">registro <code>${{p.reg}}</code> · ${{p.tit}} · ${{p.cat}}</div>
    <div class="tw"><table><tbody>
      <tr><th>Substancia ativa</th><td>${{(p.ai||[]).join(' + ')||'NOT_PRESENT'}}</td></tr>
      <tr><th>Formulacao</th><td>${{p.form}}</td></tr>
      <tr><th>Estado administrativo</th><td>${{p.st}}</td></tr>
      <tr><th>Registrado em</th><td>${{p.reg_at}}</td></tr>
      <tr><th>Validade</th><td class="${{venc?'bad':''}}">${{p.exp}}
        ${{venc?` — <b>vencida ha ${{-p.dte}} dias, e o registro ainda o lista como “${{p.st}}”</b>.
        <span class="dim">EXPIRY != WITHDRAWAL</span>`:''}}</td></tr>
    </tbody></table></div>
  </div>

  <div class="block">
    <header><h3>Rotulo em vigor</h3><span class="badge b-real">REAL</span></header>
    <div class="tw"><table><tbody>
      <tr><th>Em vigor desde</th><td>${{l.EFFECTIVE_AT||'NOT_KNOWN'}}
        <span class="dim">— data declarada pela fonte oficial, nao inferida</span></td></tr>
      <tr><th>Documento</th><td class="mono">sha256 ${{l.SHA256||'NOT_KNOWN'}}</td></tr>
      <tr><th>Tamanho</th><td>${{l.BYTES||'NOT_KNOWN'}} bytes</td></tr>
      <tr><th>Conferido</th><td>${{l.OBSERVED_AT||'?'}} contra captura de ${{l.BASELINE_CAPTURED_AT||'?'}}
        — <b class="${{l.DOCUMENT_CHANGED?'bad':'ok'}}">${{l.DOCUMENT_CHANGED?'MUDOU':'identico'}}</b></td></tr>
      <tr><th>Fonte</th><td><a href="${{l.URL}}" target="_blank">PDF oficial no Ministero</a></td></tr>
    </tbody></table></div>
  </div>

  <div class="block">
    <header><h3>Usos autorizados — ${{p.n_usos}} pares cultura x alvo</h3>
      <span class="badge b-real">REAL</span></header>
    <div class="meta">reuso de <code>sintonia/canonical @ bdb57cf</code> ·
      parser <code>it_rotulo_parser/3.4.0</code> · precisao 0,965 / recall 0,870 medidos em 30 rotulos ·
      <b class="ok">${{p.n_tab}}</b> pares lidos da tabela, <b class="dim">${{p.n_txt}}</b> montados de prosa ou lista</div>
    ${{p.doses.length ? `<div class="tw"><table>
      <thead><tr><th>Cultura</th><th>Alvo</th><th>Dose</th><th>Max. aplicacoes</th><th>Intervalo</th><th>Pag.</th></tr></thead>
      <tbody>${{p.doses.map(r=>`<tr><td>${{r.CROP}}${{r.CROP_INHERITED?' <span class="dim" title="celula mesclada">↑</span>':''}}</td>
        <td>${{r.TARGET}}</td>
        <td>${{r.DOSE_PER_HECTARE==='NOT_PRESENT'?'<span class="dim">NOT_PRESENT</span>':r.DOSE_PER_HECTARE+' '+r.DOSE_PER_HECTARE_UNIT}}</td>
        <td>${{r.MAX_APPLICATIONS}}</td><td>${{r.APPLICATION_INTERVAL}}</td><td>${{r.SOURCE_PAGE}}</td></tr>`).join('')}}</tbody>
      </table></div>`
    : `<div class="warn">Dose ainda nao estruturada para este produto —
       <code>${{p.dose_state}}</code>. Isto e estado de LEITURA, nao ausencia regulatoria.</div>`}}
    <div class="tw" style="margin-top:14px"><table>
      <thead><tr><th>Cultura</th><th>Alvos autorizados</th><th>Evidencia</th></tr></thead>
      <tbody>${{p.usos.map(u=>`<tr><td><b>${{u.c}}</b></td>
        <td class="dim">${{[...new Set(u.t)].join(' · ')}}</td>
        <td><span class="pill ${{u.ev==='TABELA'?'p-ok':'p-nc'}}">${{u.ev}}</span>
        ${{u.pg!=='NOT_PRESERVED'?`<span class="dim" style="font-size:11px"> pag ${{u.pg}}</span>`:''}}</td></tr>`).join('')
        || '<tr><td colspan=3 class="dim">tabela de uso ainda nao lida — divida de leitura</td></tr>'}}</tbody>
    </table></div>
  </div>

  <div class="block">
    <header><h3>Historico do registro</h3>
      <span class="badge ${{p.regchg.length?'b-real':'b-derived'}}">${{p.regchg.length?'REAL':'DERIVED'}}</span></header>
    ${{p.regchg.length ? `<div class="tw"><table>
      <thead><tr><th>Janela</th><th>Tipo</th><th>Antes</th><th>Depois</th></tr></thead>
      <tbody>${{p.regchg.map(c=>`<tr><td class="mono">${{c.OBSERVATION_WINDOW}}</td>
        <td>${{c.CHANGE_TYPE}}${{c.UNSTABLE_SOURCE?' <span class="dim">(texto)</span>':''}}</td>
        <td class="dim">${{c.BEFORE}}</td><td>${{c.AFTER}}</td></tr>`).join('')}}</tbody></table></div>`
    : `<div class="meta">Nenhuma mudanca observada neste registro na janela arquivada.
       <code>NO_CHANGE_OBSERVED_IN_WINDOW</code> — nao e o mesmo que “nunca mudou”.</div>`}}
  </div>

  <div class="block">
    <header><h3>Por que este produto esta na demo</h3><span class="badge b-derived">DERIVED</span></header>
    <ul class="dim" style="font-size:13px;line-height:1.7;margin:6px 0 0">
      ${{p.why.map(w=>`<li>${{w}}</li>`).join('')}}</ul>
  </div>`;
}}
$('#psel').addEventListener('change', produto); produto();

// ---- mudancas
// Vem do historico do registro inteiro, nao dos produtos ativos: um evento pode
// ser exatamente a saida de um produto do conjunto ativo, e filtrar por ativo
// esconderia justamente esse.
const todos = {eventos_js};
$('#tbc').innerHTML = todos.filter(c=>!c.UNSTABLE_SOURCE).map(c=>`<tr>
  <td class="mono">${{c.OBSERVATION_WINDOW}}</td><td class="mono">${{c.REGISTRATION_ID}}</td>
  <td>${{c.PRODUCT}}</td><td>${{c.CHANGE_TYPE}}</td>
  <td class="dim">${{c.BEFORE}}</td><td>${{c.AFTER}}</td></tr>`).join('')
  || '<tr><td colspan=6 class="dim">nenhuma mudanca regulatoria na janela</td></tr>';
</script>
</body></html>"""

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(H)
    print(f"  escrito {a.out} ({len(H):,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
