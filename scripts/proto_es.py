#!/usr/bin/env python3
"""Gera o prototipo da vista de caso da Espanha a partir do pacote CONGELADO.

Nao ha conteudo escrito a mao neste arquivo alem de rotulo de interface.
Todo dado vem de data/samples/SPAIN-HERO-CASES-V1.json e ES-ACTION-MAP-V2.json,
que o freeze verifica por sha256. Se o pacote mudar, a tela muda junto.
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
MAPA_KEY = {'ES-CASE-001': 'ES-CASE-001-OLIVO',
            'ES-CASE-002': 'ES-CASE-002-MILHO',
            'ES-CASE-003': 'ES-CASE-003-CEREAL'}
FUNCOES = ['REGULATORY', 'MARKET_DEVELOPMENT', 'SCIENCE', 'MARKETING', 'COMMERCIAL', 'SUPPLY']
ROTULO_FUNCAO = {'REGULATORY': 'Regulatory / Portfólio', 'MARKET_DEVELOPMENT': 'Market Development',
                 'SCIENCE': 'Science', 'MARKETING': 'Marketing', 'COMMERCIAL': 'Commercial',
                 'SUPPLY': 'Supply'}
# ordem deliberada: do estado que exige mais para o que exige menos
ORDEM_ACAO = ['ACT_NOW', 'VERIFY_NOW', 'PREPARE', 'PLAN', 'WAIT_FOR_INTERNAL_DATA', 'NO_ACTION']


def carrega(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def dados():
    pack = carrega('SPAIN-HERO-CASES-V1.json')
    v2 = carrega('ES-ACTION-MAP-V2.json')
    casos = []
    for c in pack['CASES']:
        mapa = v2[MAPA_KEY[c['CASE_ID']]]
        acoes = {f: mapa[f] for f in FUNCOES if isinstance(mapa.get(f), dict)}
        casos.append((c, acoes))
    return pack, v2, casos


def bloco_medida(rotulo, valor, apoio, idade):
    """A tripla que nao pode ser separada: valor, suporte amostral, idade.

    Existe como componente porque juntar os tres num numero so foi
    exatamente o erro que este projeto cometeu duas vezes.
    """
    return f'''<div class="triple">
        <span class="triple-label">{e(rotulo)}</span>
        <div class="triple-cells">
          <div class="cell"><span class="cell-k">valor</span><span class="cell-v">{e(valor)}</span></div>
          <div class="cell"><span class="cell-k">suporte amostral</span><span class="cell-v">{e(apoio)}</span></div>
          <div class="cell"><span class="cell-k">idade do dado</span><span class="cell-v">{e(idade)}</span></div>
        </div>
      </div>'''


def lista(itens, classe):
    li = ''.join(f'<li>{e(x)}</li>' for x in itens)
    return f'<ul class="{classe}">{li}</ul>'


def render_caso(c, acoes, idx):
    cid = c['CASE_ID']
    # a tripla do sinal, montada dos campos que o cartao ja separa
    if cid == 'ES-CASE-001':
        triplas = (bloco_medida('Cádiz · repilo visível', '8,01 %',
                                '141 leituras · 39 parcelas · rede estável',
                                'última observação 27/05/2026') +
                   bloco_medida('Huelva · repilo visível', '8,83 %',
                                '18 leituras · 7 parcelas · menor n da série',
                                'última observação 14/06/2026'))
    elif cid == 'ES-CASE-003':
        triplas = (bloco_medida('Castilla y León · ACCase (diclofop)', '74 % ainda suscetível',
                                'levantamento aleatório em área de cereal',
                                'coleta 2012–2013') +
                   bloco_medida('Cataluña · ACCase (diclofop)', '83 % resistente',
                                'mesmo levantamento',
                                'coleta 2012–2013') +
                   bloco_medida('Castilla y León · PSII (clortolurón)', '51 % resistente',
                                'mesmo levantamento', 'coleta 2012–2013'))
    else:
        triplas = (bloco_medida('Huesca · área de milho declarada', '37 236 ha',
                                '81 municípios · 10 fazem 47,7 %',
                                'campanha PAC 2025') +
                   bloco_medida('Avisos oficiais de Aragón', '3 em 14 meses',
                                'serviço fitossanitário regional',
                                'último 15/07/2026'))

    linhas = []
    for f in sorted(acoes, key=lambda x: (ORDEM_ACAO.index(acoes[x]['ACTION_TYPE']), x)):
        a = acoes[f]
        t = a['ACTION_TYPE']
        linhas.append(f'''<tr>
          <th scope="row">{e(ROTULO_FUNCAO[f])}</th>
          <td><span class="pill pill-{e(t.lower())}">{e(t.replace('_', ' '))}</span></td>
          <td class="acao">
            <p class="acao-t">{e(a['ACTION'])}</p>
            <p class="acao-w">{e(a['WHY'])}</p>
            <p class="acao-m"><span class="k">falta</span> {e(a['MISSING'])}</p>
            <p class="acao-e"><span class="k">evidência</span> {e(a['EVIDENCE'])}</p>
          </td>
        </tr>''')

    return f'''<article class="caso" id="{e(cid)}" data-caso="{e(cid)}" {'' if idx == 0 else 'hidden'}>
  <header class="caso-head">
    <p class="eyebrow"><span class="cid">{e(cid)}</span> · Espanha</p>
    <h2>{e(c['CROP'])} <span class="sep">×</span> {e(c['ISSUE'])}</h2>
    <p class="regiao">{e(c['REGION'])}</p>
    <p class="tipo"><span class="pill pill-{e(c['CASE_TYPE'].lower().replace(' ', '_'))}">{e(c['CASE_TYPE'])}</span></p>
  </header>

  <section class="sec">
    <h3>O que está acontecendo</h3>
    <p class="lede">{e(c['WHAT_IS_HAPPENING'])}</p>
    {triplas}
  </section>

  <section class="autoriza">
    <p class="autoriza-k">O que esta evidência autoriza hoje</p>
    <p class="autoriza-sim">{e(c['ACTION_NOW'])}</p>
    <p class="autoriza-nao"><span class="k">necessidade de campo agora</span> {e(c['CURRENT_FIELD_NEED'])}</p>
  </section>

  <section class="sec grid2">
    <div>
      <h3>Janela</h3>
      <dl class="dl">
        <dt>Na etiqueta</dt><dd>{e(c['APPLICATION_WINDOW'])}</dd>
        <dt>Estado</dt><dd>{e(c['WINDOW_STATUS'])}</dd>
        <dt>Tempo até a janela</dt><dd>{e(c['TIME_TO_WINDOW'])}</dd>
      </dl>
    </div>
    <div>
      <h3>Relógios</h3>
      <dl class="dl">
        <dt>Agronômico</dt><dd>{e(c['AGRONOMIC_CLOCK'])}</dd>
        <dt>Observação</dt><dd>{e(c['OBSERVATION_CLOCK'])}</dd>
        <dt>Comercial</dt><dd class="nao-sei">{e(c['COMMERCIAL_CLOCK'])}</dd>
      </dl>
    </div>
  </section>

  <section class="sec">
    <h3>Resposta</h3>
    <dl class="dl">
      <dt>ADAMA · registrada</dt><dd>{e(c['ADAMA_REGULATORY_RESPONSE'])}</dd>
      <dt>ADAMA · catálogo público</dt><dd class="nao-sei">{e(c['ADAMA_PUBLIC_RESPONSE'])}</dd>
      <dt>Concorrente · público</dt><dd class="nao-sei">{e(c['COMPETITOR_PUBLIC_RESPONSE'])}</dd>
      <dt>Consequência econômica</dt><dd class="nao-sei">{e(c['POSSIBLE_ECONOMIC_CONSEQUENCE'])}</dd>
    </dl>
  </section>

  <section class="sec">
    <h3>Ciência e pessoas</h3>
    <dl class="dl">
      <dt>Ciência</dt><dd>{e(c['SCIENCE'])}</dd>
      <dt>Pesquisadores</dt><dd>{e(c['RESEARCHERS'])}</dd>
      <dt>Rede técnica pública</dt><dd>{e(c['TECHNICAL_NETWORK'])}</dd>
      <dt>Voz pública</dt><dd class="nao-sei">{e(c['PUBLIC_CONTENT_VOICE'])}</dd>
    </dl>
  </section>

  <section class="sec tres">
    <div class="col fato">
      <h3>Fatos</h3>
      {lista(c['FACTS'], 'l-fato')}
    </div>
    <div class="col interp">
      <h3>Interpretações</h3>
      {lista(c['INTERPRETATIONS'], 'l-interp')}
    </div>
    <div class="col unk">
      <h3>Não sabemos</h3>
      {lista(c['UNKNOWNS'], 'l-unk')}
    </div>
  </section>

  <section class="sec">
    <h3>Mapa de ação <span class="h3n">6 funções · horizonte {e(c['ACTION_HORIZON'])}</span></h3>
    <div class="tw"><table class="acoes">
      <thead><tr><th scope="col">Função</th><th scope="col">Estado</th><th scope="col">O quê, por quê, o que falta</th></tr></thead>
      <tbody>{''.join(linhas)}</tbody>
    </table></div>
  </section>

  <section class="sec">
    <h3>Evidência</h3>
    {lista(c['EVIDENCE_PATHS'], 'l-ev')}
  </section>
</article>'''


CSS = '''
:root{
  --ground:#FBFAF8; --surface:#FFFFFF; --surface-2:#F5F2ED;
  --ink:#1D1B19; --ink-soft:#6B6560; --ink-faint:#8C857E;
  --rule:#E4DFD8; --rule-strong:#CFC7BD;
  --adama:#009845; --adama-deep:#00783F; --adama-warm:#978B87;
  --known:#00783F; --partial:#A8761F; --unknown:#5F5A55;
  --band:#F0EDE6; --band-rule:#00783F;
  --shadow:0 1px 2px rgba(29,27,25,.05), 0 8px 24px -16px rgba(29,27,25,.18);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#17160F; --surface:#1E1D16; --surface-2:#25231B;
    --ink:#EFEBE3; --ink-soft:#B3ABA0; --ink-faint:#8C857E;
    --rule:#332F26; --rule-strong:#464034;
    --adama:#3FBE74; --adama-deep:#5FCB8B; --adama-warm:#A79A94;
    --known:#5FCB8B; --partial:#D6A44A; --unknown:#B3ABA0;
    --band:#20211A; --band-rule:#3FBE74;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#17160F; --surface:#1E1D16; --surface-2:#25231B;
  --ink:#EFEBE3; --ink-soft:#B3ABA0; --ink-faint:#8C857E;
  --rule:#332F26; --rule-strong:#464034;
  --adama:#3FBE74; --adama-deep:#5FCB8B; --adama-warm:#A79A94;
  --known:#5FCB8B; --partial:#D6A44A; --unknown:#B3ABA0;
  --band:#20211A; --band-rule:#3FBE74;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"LL Brown", Archivo, Arial, Helvetica, sans-serif;
  font-size:15px; line-height:1.55; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:0 24px 96px}

/* ---------- topo ---------- */
.top{border-bottom:1px solid var(--rule); padding:34px 0 22px; margin-bottom:30px}
.brand{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap}
.brand-mark{
  font-size:19px; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
  color:var(--adama-deep);
}
.brand-sub{font-family:Aleo, Georgia, serif; font-size:14px; color:var(--ink-soft)}
.top-meta{
  margin-top:14px; display:flex; gap:22px; flex-wrap:wrap;
  font-family:Aleo, Georgia, serif; font-size:12.5px; color:var(--ink-faint);
  font-variant-numeric:tabular-nums;
}
.top-meta b{color:var(--ink-soft); font-weight:600}

/* ---------- layout ---------- */
.cols{display:grid; grid-template-columns:250px minmax(0,1fr); gap:44px; align-items:start}
@media (max-width:880px){ .cols{grid-template-columns:1fr; gap:26px} }

.rail{position:sticky; top:22px; display:flex; flex-direction:column; gap:9px}
@media (max-width:880px){ .rail{position:static} }
.rail-k{
  font-size:11px; letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-faint); margin:0 0 3px 2px;
}
.rail button{
  display:block; width:100%; text-align:left; cursor:pointer;
  background:var(--surface); color:var(--ink);
  border:1px solid var(--rule); border-left:3px solid var(--rule-strong);
  border-radius:2px; padding:12px 13px; font:inherit;
  transition:border-color .15s, background .15s;
}
.rail button:hover{border-left-color:var(--adama)}
.rail button:focus-visible{outline:2px solid var(--adama); outline-offset:2px}
.rail button[aria-current="true"]{border-left-color:var(--adama-deep); background:var(--surface-2)}
.rail .r-id{font-family:Aleo, Georgia, serif; font-size:11px; color:var(--ink-faint); display:block}
.rail .r-t{font-weight:600; font-size:14px; display:block; margin:2px 0 4px}
.rail .r-s{font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-soft)}

/* ---------- caso ---------- */
.caso-head{padding-bottom:20px; border-bottom:2px solid var(--ink); margin-bottom:26px}
.eyebrow{
  margin:0 0 8px; font-family:Aleo, Georgia, serif; font-size:12px;
  letter-spacing:.06em; color:var(--ink-faint);
}
.eyebrow .cid{color:var(--adama-deep); font-weight:700}
.caso-head h2{
  margin:0; font-size:clamp(26px,4vw,38px); line-height:1.12; font-weight:700;
  letter-spacing:-.018em; text-wrap:balance;
}
.caso-head h2 .sep{color:var(--adama-warm); font-weight:400}
.regiao{margin:10px 0 0; color:var(--ink-soft); max-width:62ch}
.tipo{margin:14px 0 0}

.sec{margin:34px 0}
.sec h3{
  margin:0 0 14px; font-size:12px; letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-soft); font-weight:700;
  padding-bottom:7px; border-bottom:1px solid var(--rule);
  display:flex; justify-content:space-between; align-items:baseline; gap:12px;
}
.h3n{font-family:Aleo, Georgia, serif; text-transform:none; letter-spacing:0;
  font-weight:400; font-size:12px; color:var(--ink-faint)}
.lede{margin:0 0 20px; font-size:17px; line-height:1.5; max-width:66ch; text-wrap:pretty}

/* ---------- a tripla ---------- */
.triple{margin:0 0 12px; border:1px solid var(--rule); border-radius:2px; background:var(--surface)}
.triple-label{
  display:block; padding:9px 14px; border-bottom:1px solid var(--rule);
  font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-soft); font-weight:600;
}
.triple-cells{display:grid; grid-template-columns:repeat(3,1fr)}
@media (max-width:640px){ .triple-cells{grid-template-columns:1fr} }
.cell{padding:12px 14px; border-right:1px solid var(--rule)}
.cell:last-child{border-right:0}
@media (max-width:640px){ .cell{border-right:0; border-bottom:1px solid var(--rule)} .cell:last-child{border-bottom:0} }
.cell-k{
  display:block; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-faint); margin-bottom:4px;
}
.cell-v{display:block; font-size:15px; font-variant-numeric:tabular-nums; line-height:1.35}
.triple-cells .cell:first-child .cell-v{font-size:20px; font-weight:700; letter-spacing:-.01em}

/* ---------- a banda de autorizacao ---------- */
.autoriza{
  margin:30px 0; padding:22px 24px; background:var(--band);
  border-left:3px solid var(--band-rule); border-radius:2px;
}
.autoriza-k{
  margin:0 0 10px; font-size:11px; letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-soft); font-weight:700;
}
.autoriza-sim{
  margin:0; font-family:Aleo, Georgia, serif; font-size:19px; line-height:1.4;
  max-width:60ch; text-wrap:pretty;
}
.autoriza-nao{margin:14px 0 0; font-size:14px; color:var(--ink-soft)}
.autoriza-nao .k, .acao-m .k, .acao-e .k{
  font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-faint); margin-right:7px;
}

/* ---------- listas de definicao ---------- */
.grid2{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:34px}
@media (max-width:760px){ .grid2{grid-template-columns:1fr; gap:26px} }
.dl{margin:0; display:grid; grid-template-columns:minmax(150px,auto) 1fr; gap:9px 20px}
@media (max-width:640px){ .dl{grid-template-columns:1fr; gap:3px 0} .dl dd{margin-bottom:12px} }
.dl dt{
  font-size:11px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--ink-faint); padding-top:3px;
}
.dl dd{margin:0; max-width:64ch}
.nao-sei{color:var(--unknown); font-weight:600}

/* ---------- tres colunas ---------- */
.tres{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:30px}
@media (max-width:900px){ .tres{grid-template-columns:1fr; gap:24px} }
.tres ul{margin:0; padding-left:18px; display:flex; flex-direction:column; gap:9px}
.tres li{font-size:14px; line-height:1.5}
.l-fato li::marker{color:var(--known)}
.l-interp li{font-style:italic; color:var(--ink-soft)}
.l-interp li::marker{color:var(--partial)}
.l-unk li::marker{color:var(--unknown)}
.col.unk ul li{color:var(--ink)}
.l-ev{margin:0; padding-left:18px; display:flex; flex-direction:column; gap:7px;
  font-family:Aleo, Georgia, serif; font-size:13px; color:var(--ink-soft)}

/* ---------- pills ---------- */
.pill{
  display:inline-block; padding:4px 10px; border-radius:2px;
  font-size:11px; letter-spacing:.09em; text-transform:uppercase; font-weight:700;
  border:1px solid currentColor;
}
.pill-act_now{color:var(--known)}
.pill-verify_now, .pill-verify_field_now{color:var(--partial)}
.pill-prepare, .pill-preparar{color:var(--ink-soft)}
.pill-plan, .pill-planejar, .pill-planejar_proximo_ciclo{color:var(--ink-soft)}
.pill-wait_for_internal_data{color:var(--unknown)}
.pill-no_action{color:var(--ink-faint)}

/* ---------- tabela de acoes ---------- */
.tw{overflow-x:auto}
.acoes{width:100%; border-collapse:collapse; min-width:640px}
.acoes th, .acoes td{
  text-align:left; vertical-align:top; padding:14px 16px 14px 0;
  border-bottom:1px solid var(--rule);
}
.acoes thead th{
  font-size:10.5px; letter-spacing:.11em; text-transform:uppercase;
  color:var(--ink-faint); font-weight:600; padding-bottom:9px;
  border-bottom:1px solid var(--rule-strong);
}
.acoes tbody th{width:170px; font-size:14px; font-weight:600}
.acoes td:nth-child(2){width:170px}
.acao{max-width:56ch}
.acao-t{margin:0 0 7px; font-weight:600}
.acao-w{margin:0 0 9px; color:var(--ink-soft); font-size:14px}
.acao-m, .acao-e{margin:0 0 5px; font-size:13px; color:var(--ink-soft)}
.acao-e{font-family:Aleo, Georgia, serif}

/* ---------- eame ---------- */
.eame{
  margin:56px 0 0; padding:24px; border:1px dashed var(--rule-strong);
  border-radius:2px; background:var(--surface);
}
.eame h3{
  margin:0 0 10px; font-size:12px; letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-soft); font-weight:700;
}
.eame p{margin:0 0 8px; color:var(--ink-soft); max-width:70ch}
.eame .zero{
  font-family:Aleo, Georgia, serif; font-size:30px; color:var(--unknown);
  font-variant-numeric:tabular-nums; margin:0 0 6px;
}

.pe{
  margin:44px 0 0; padding-top:20px; border-top:1px solid var(--rule);
  font-family:Aleo, Georgia, serif; font-size:12.5px; color:var(--ink-faint);
  max-width:78ch;
}
.pe code{font-family:ui-monospace, Menlo, Consolas, monospace; font-size:12px}
@media (prefers-reduced-motion:reduce){ *{transition:none !important; animation:none !important} }
'''


def render(pack, v2, casos):
    freeze = carrega('SPAIN-DEMO-CONTENT-V1.json')['FREEZE']
    rel = carrega('EAME-RELATIONSHIP-CONTRACT-V1.json')
    botoes = ''.join(
        f'''<button type="button" data-alvo="{e(c['CASE_ID'])}" aria-current="{'true' if i == 0 else 'false'}">
        <span class="r-id">{e(c['CASE_ID'])}</span>
        <span class="r-t">{e(c['CROP'])}</span>
        <span class="r-s">{e(c['CASE_TYPE'])}</span>
      </button>''' for i, (c, _) in enumerate(casos))
    artigos = ''.join(render_caso(c, a, i) for i, (c, a) in enumerate(casos))
    cont = v2['CONTAGEM']
    contagem = ' · '.join(f"{k.replace('_', ' ').lower()} {v}" for k, v in sorted(cont.items()))
    return f'''<title>Casos Sintonia Espanha</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=Aleo:ital,wght@0,400;0,600;1,400&display=swap">
<style>{CSS}</style>

<div class="wrap">
  <header class="top">
    <div class="brand">
      <span class="brand-mark">ADAMA · Sintonia</span>
      <span class="brand-sub">casos da Espanha, congelados em {e(freeze['VERSAO_DO_FREEZE'])}</span>
    </div>
    <div class="top-meta">
      <span><b>HEAD</b> {e(freeze['HEAD_CURTO'])}</span>
      <span><b>artefatos canônicos</b> {len(freeze['ARTEFATOS_CANONICOS'])}</span>
      <span><b>congelado em</b> {e(freeze['FREEZE_AT'])}</span>
      <span><b>mapa de ação</b> {e(contagem)}</span>
    </div>
  </header>

  <div class="cols">
    <nav class="rail" aria-label="Casos">
      <p class="rail-k">Três casos</p>
      {botoes}
    </nav>
    <main>
      {artigos}

      <section class="eame">
        <h3>Camada EAME · relações entre países</h3>
        <p class="zero">{rel['RELATIONS_COUNT']} relações</p>
        <p>{e(rel['POR_QUE_ZERO'])}</p>
        <p>{e(rel['O_QUE_FALTA_EM_UMA_LINHA'])}</p>
      </section>

      <p class="pe">Toda a página é gerada de <code>SPAIN-HERO-CASES-V1.json</code>,
      <code>ES-ACTION-MAP-V2.json</code> e <code>EAME-RELATIONSHIP-CONTRACT-V1.json</code>
      por <code>scripts/proto_es.py</code>. Nenhum texto de caso foi escrito na tela.
      O freeze verifica os artefatos por sha256: se um mudar, a página muda junto e
      <code>scripts/freeze_es.py</code> reprova.</p>
    </main>
  </div>
</div>

<script>
(function () {{
  var botoes = Array.prototype.slice.call(document.querySelectorAll('.rail button'));
  var casos = Array.prototype.slice.call(document.querySelectorAll('.caso'));
  function mostrar(id) {{
    casos.forEach(function (c) {{ c.hidden = (c.dataset.caso !== id); }});
    botoes.forEach(function (b) {{ b.setAttribute('aria-current', String(b.dataset.alvo === id)); }});
  }}
  botoes.forEach(function (b) {{
    b.addEventListener('click', function () {{ mostrar(b.dataset.alvo); }});
  }});
}}());
</script>'''


def main():
    pack, v2, casos = dados()
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'sintonia-es.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(render(pack, v2, casos))
    print('escrito: %s (%d bytes, %d casos)' % (dest, os.path.getsize(dest), len(casos)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
