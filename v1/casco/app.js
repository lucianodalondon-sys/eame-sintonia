// SINTONIA — LABEL INTELLIGENCE V1 · casco
// O casco NAO interpreta documento. Ele mostra intelligence objects e produtos
// que a inteligencia ja resolveu, e leva qualquer afirmacao de volta a prova.
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

// Tokens que significam AUSENCIA DE CONHECIMENTO. Nunca vira "-", "0" ou "N/A".
const UNK = ['NOT_KNOWN','NOT_PROVED','NOT_PRESERVED','NOT_PRESENT','UNKNOWN',
             'NOT_APPLICABLE','NOT_ATTEMPTED','NOT_EMITTED_BY_THIS_TOOL','NOT_CHECKED'];
const isUnk = v => UNK.includes(String(v));
// Renderiza valor preservando o token de ignorancia, com o nome dele visivel.
const val = v => isUnk(v) ? `<span class="unknown" title="a fonte nao sustenta este campo">${esc(v)}</span>`
                          : esc(v);

const WIN = {ACT_NOW:['act','p-act','ACT NOW'], PREPARE:['prep','p-warn','PREPARE'],
             MONITOR:['mon','p-ok','MONITOR'], PLAN_NEXT_CYCLE:['mon','p-dim','PLAN NEXT CYCLE'],
             NO_ACTION_YET:['','p-dim','NO ACTION YET'], UNKNOWN:['unk','p-unk','UNKNOWN']};
const PROOF = {PROVED:'p-ok', NOT_PROVED:'p-unk', NEEDS_REVIEW:'p-rev'};
const CAPS = {REGULATORY:'Regulatory', DEVELOPMENT_MARKET:'Desenv. de Mercado',
              COMMERCIAL_RTV:'Comercial / RTV', MARKETING_PRODUCT:'Marketing / Produto',
              SUPPLY:'Supply', INTELLIGENCE:'Inteligencia',
              COUNTRY_PRODUCT_TEAM:'Country / Product Team'};

// Os dois lados escrevem o nome da cultura de jeitos diferentes: o leitor de
// cultura x alvo normaliza ("VITE"), o leitor de dose guarda como esta impresso
// ("Vite*", "Cetriolo, Zucchino (Uso in serra)"). Casar por igualdade exata fazia
// a tela dizer NOT_KNOWN para dose que existe e esta provada.
const nrm = s => String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
  .toUpperCase().replace(/[^A-Z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();
function casa(a, b) {            // um contem o outro, apos normalizar
  const x = nrm(a), y = nrm(b);
  if (!x || !y) return false;
  if (x === y) return true;
  return x.split(' ').some(t => t.length > 3 && y.includes(t))
      || y.split(' ').some(t => t.length > 3 && x.includes(t));
}
// A validade tem de aparecer igual em TODA tela. Antes, CULTURA x ALVO mostrava
// "2026-08-15" seco enquanto CALENDARIO e PRODUTO 360 marcavam o mesmo produto
// como vencido-e-ainda-ativo. Mesma data, tres leituras diferentes.
function validade(p) {
  if (isUnk(p.expiry)) return val(p.expiry);
  if (typeof p.dte === 'number' && p.dte < 0)
    return `<span style="color:var(--bad)">${esc(p.expiry)}</span>
            <span class="pill p-bad" title="a validade passou e o registro ainda lista o produto como ativo. Vencer nao e ser revogado.">VENCIDA</span>`;
  if (typeof p.dte === 'number' && p.dte <= 90)
    return `${esc(p.expiry)} <span class="pill p-warn">${p.dte}d</span>`;
  return esc(p.expiry);
}
const P = window.__PAYLOAD__;
const byReg = Object.fromEntries(P.products.map(p => [p.reg, p]));

// ---------------------------------------------------------------- evidencia
function drawer(html) { $('#dr').innerHTML =
  `<button class="close" onclick="document.getElementById('dr').classList.remove('open')">&times;</button>${html}`;
  $('#dr').classList.add('open'); }

function evObj(id) {
  const o = P.objects.find(x => x.INTELLIGENCE_OBJECT_ID === id);
  if (!o) return;
  const rt = o.CAPABILITY_ROUTING.map(r =>
    `<div style="margin:3px 0"><b>${CAPS[r.CAPABILITY_ID]||r.CAPABILITY_ID}</b>
     <span class="pill ${r.ROUTING_STATE==='RELEVANT'?'p-ok':r.ROUTING_STATE==='POTENTIALLY_RELEVANT'?'p-warn':r.ROUTING_STATE==='UNKNOWN'?'p-unk':'p-dim'}">${r.ROUTING_STATE}</span>
     <code>${esc(r.RULE_ID)}</code><div class="meta">${esc(r.JUSTIFICATION)}</div></div>`).join('');
  drawer(`<h3>Evidencia</h3>
  <div class="meta">objeto <code>${esc(o.INTELLIGENCE_OBJECT_ID)}</code></div>
  <dl>
    <dt>Fato (o que a fonte diz)</dt><dd>${esc(o.FACT)}</dd>
    <dt>Significado regulatorio derivado</dt><dd>${val(o.DERIVED_REGULATORY_MEANING)}
      ${o.DERIVED_BY_RULE!=='NOT_PROVED'?`<code>${esc(o.DERIVED_BY_RULE)}</code>`:''}</dd>
    <dt>Implicacao de negocio</dt><dd>${val(o.POTENTIAL_BUSINESS_IMPLICATION)}
      <div class="meta">${esc(o.BUSINESS_IMPLICATION_NOTE)}</div></dd>
    <dt>Revisao recomendada</dt><dd>${val(o.RECOMMENDED_REVIEW)}</dd>
    <dt>Acao</dt><dd>${val(o.ACTION)}<div class="meta">esta ferramenta nao emite acao</div></dd>
    <dt>Antes &rarr; Depois</dt><dd>${val(o.BEFORE_VALUE)} &rarr; ${val(o.AFTER_VALUE)}</dd>
    <dt>Estado da prova</dt><dd><span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span>
      &nbsp;<code>${esc(o.CONFIDENCE_STATE)}</code></dd>
    <dt>Documento antes</dt><dd class="mono">${val(o.SOURCE_DOCUMENT_BEFORE)}</dd>
    <dt>Documento depois</dt><dd class="mono">${val(o.SOURCE_DOCUMENT_AFTER)}</dd>
    <dt>Local da evidencia</dt><dd>${val(o.EVIDENCE_LOCATION)}</dd>
    <dt>Fonte oficial</dt><dd>${o.SOURCE_URL?`<a href="${esc(o.SOURCE_URL)}" target="_blank">${esc(o.SOURCE_URL)}</a>`:val('NOT_KNOWN')}</dd>
    <dt>Autoridade</dt><dd>${val(o.SOURCE_AUTHORITY)}</dd>
    <dt>Capturado em</dt><dd>${val(o.CAPTURED_AT)}</dd>
    <dt>Detectado em</dt><dd>${val(o.DETECTED_AT)}</dd>
    <dt>Janela de observacao</dt><dd>${val(o.OBSERVATION_WINDOW||'NOT_APPLICABLE')}</dd>
    <dt>Parser</dt><dd class="mono">${val(o.PARSER_VERSION)}</dd>
    <dt>Regras</dt><dd class="mono">${esc(o.RULESET_VERSION)}</dd>
    <dt>Janela temporal</dt><dd>${esc(o.TIME_WINDOW)} <code>${esc(o.TIME_WINDOW_RULE)}</code></dd>
  </dl>
  <h3 style="margin-top:16px">Quem pode precisar olhar</h3>${rt}`);
}
window.evObj = evObj;

function evProd(reg) {
  const p = byReg[reg]; if (!p) return;
  drawer(`<h3>${esc(p.name)}</h3>
  <div class="meta">registro <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Titular</dt><dd>${val(p.holder)}</dd>
    <dt>Estado administrativo</dt><dd>${val(p.status)}</dd>
    <dt>Validade declarada</dt><dd>${val(p.expiry)}</dd>
    <dt>Substancias ativas</dt><dd>${val(p.actives)}</dd>
    <dt>Instantaneo do registro</dt><dd class="mono">${esc(p.snapshot)}<br>sha256 ${esc(p.snapshot_sha)}</dd>
    <dt>Fonte do registro</dt><dd><a href="${esc(p.source_url)}" target="_blank">CSV oficial</a></dd>
    <dt>PDF da etichetta</dt><dd>${p.pdf_url&&!isUnk(p.pdf_url)?`<a href="${esc(p.pdf_url)}" target="_blank">abrir no Ministero</a>`:val(p.pdf_url)}</dd>
    <dt>sha256 do PDF</dt><dd class="mono">${val(p.pdf_sha)}</dd>
    <dt>Bytes</dt><dd>${val(p.pdf_bytes)}</dd>
    <dt>Etichetta em vigor desde</dt><dd>${val(p.label_effective)}
      <div class="meta">data declarada pela fonte, nao inferida</div></dd>
    <dt>Capturado em</dt><dd>${val(p.captured_at)}</dd>
    <dt>Run de coleta</dt><dd class="mono">${val(p.run)}</dd>
    <dt>Estados de leitura</dt><dd>${Object.entries(p.states).map(([k,v])=>
      `<span class="pill ${v?'p-ok':'p-dim'}">${k}</span>`).join(' ')}</dd>
  </dl>`);
}
window.evProd = evProd;

function evUso(reg, i) {
  const p = byReg[reg], u = p.uses[i];
  drawer(`<h3>Uso autorizado</h3>
  <div class="meta">${esc(p.name)} &middot; <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Cultura</dt><dd>${val(u.crop)}</dd>
    <dt>Alvo</dt><dd>${val(u.target)}</dd>
    <dt>Como esta escrito no rotulo</dt><dd>${val(u.crop_raw)} &middot; ${val(u.target_raw)}</dd>
    <dt>Classe de evidencia</dt><dd><span class="pill ${u.evidence==='TABLE_GEOMETRY'?'p-ok':'p-dim'}">${esc(u.evidence)}</span>
      <div class="meta">${u.evidence==='TABLE_GEOMETRY'
        ? ('linha lida da geometria da tabela' + (isUnk(u.page)
            ? ', mas a pagina nao foi preservada por este leitor'
            : ', com pagina no documento'))
        :'par montado a partir de prosa ou lista do rotulo, nao de uma linha de tabela'}</div></dd>
    <dt>Rota do extrator</dt><dd class="mono">${val(u.route)}</dd>
    <dt>Pagina</dt><dd>${val(u.page)}</dd>
    <dt>Citacao literal</dt><dd>${val(u.quote)}
      <div class="meta">os pares reusados nao gravam coordenada x e a etichetta tem varias
      colunas por pagina; o trecho literal nao e recuperavel. Tentado e medido no piloto.</div></dd>
    <dt>Fonte</dt><dd><a href="${esc(p.pdf_url)}" target="_blank">PDF oficial</a>
      <div class="mono">sha256 ${esc(p.pdf_sha)}</div></dd>
    <dt>Leitor</dt><dd class="mono">it_rotulo_parser/3.4.0 (reuso de sintonia/canonical @ bdb57cf)</dd>
  </dl>
  <div class="lei">A frase correta e &ldquo;par extraido pelo nosso leitor a partir do rotulo&rdquo;,
  nunca &ldquo;o rotulo diz&rdquo;.</div>`);
}
window.evUso = evUso;

function evDose(reg, i) {
  const p = byReg[reg], d = p.doses[i];
  drawer(`<h3>Dose</h3>
  <div class="meta">${esc(p.name)} &middot; <code>${esc(p.reg)}</code></div>
  <dl>
    <dt>Cultura</dt><dd>${val(d.crop)} ${d.crop_inherited?'<span class="pill p-dim">CELULA MESCLADA</span>':''}</dd>
    <dt>Alvo</dt><dd>${val(d.target)}</dd>
    <dt>Dose por hectare</dt><dd>${isUnk(d.dose_ha)?val(d.dose_ha):esc(d.dose_ha+' '+d.unit_ha)}
      ${d.dose_ha_inherited?'<span class="pill p-dim">HERDADA DE CELULA MESCLADA</span>':''}</dd>
    <dt>Dose por concentracao</dt><dd>${isUnk(d.dose_conc)?val(d.dose_conc):esc(d.dose_conc+' '+d.unit_conc)}</dd>
    <dt>Max. aplicacoes</dt><dd>${val(d.max_app)}
      ${d.max_app_inherited?'<span class="pill p-dim">HERDADA</span>':''}</dd>
    <dt>Intervalo</dt><dd>${val(d.interval)}</dd>
    <dt>Conferencia pelos fios da tabela</dt><dd>
      <span class="pill ${d.rule_check==='CONFIRMED_BY_RULE'?'p-ok':d.rule_check==='CONTRADICTED_BY_RULE'?'p-bad':'p-dim'}">${esc(d.rule_check)}</span>
      ${d.rejected?`<div class="meta">valor rebaixado: ${esc(d.rejected)} — um fio desenhado separa
        a linha do valor que ela recebeu. Rebaixado, nao corrigido no palpite.</div>`:''}</dd>
    <dt>Pagina</dt><dd>${val(d.page)}</dd>
    <dt>Citacao do documento</dt><dd><div class="quote">${esc(d.quote||'NOT_PRESERVED')}</div></dd>
    <dt>Fonte</dt><dd><a href="${esc(p.pdf_url)}" target="_blank">PDF oficial</a>
      <div class="mono">sha256 ${esc(p.pdf_sha)}</div></dd>
    <dt>Leitor</dt><dd class="mono">v1 dose_extrair + dose_validar (fios da tabela)</dd>
  </dl>`);
}
window.evDose = evDose;

// ---------------------------------------------------------------- 1 · TODAY
function cardObj(o) {
  const [cls, pill, lbl] = WIN[o.TIME_WINDOW] || ['', 'p-dim', o.TIME_WINDOW];
  const cons = o.CAPABILITY_ROUTING
    .filter(r => r.ROUTING_STATE === 'RELEVANT' || r.ROUTING_STATE === 'POTENTIALLY_RELEVANT')
    .map(r => `<span class="pill ${r.ROUTING_STATE==='RELEVANT'?'p-ok':'p-warn'}"
      title="regra ${esc(r.RULE_ID)}: ${esc(r.JUSTIFICATION)}">${CAPS[r.CAPABILITY_ID]||r.CAPABILITY_ID}</span>`);
  const semRota = cons.length === 0;
  return `<div class="card ${cls}">
    <h4>${esc(o.PRODUCT_NAME||'NOT_KNOWN')} <span class="meta mono">${esc(o.REGISTRATION_ID)}</span></h4>
    <div class="meta">${esc(o.FACT)}</div>
    <div class="ba"><span class="b">${val(o.BEFORE_VALUE)}</span>
      <span class="arr">&rarr;</span><span class="a">${val(o.AFTER_VALUE)}</span></div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:6px">
      <span class="pill p-dim">${esc(o.CHANGE_TYPE)}</span>
      <span class="pill ${pill}">${lbl}</span>
      <span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span>
      <span class="meta">detectado ${val(o.DETECTED_AT)}</span>
      <button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">ver evidencia</button>
    </div>
    <div class="rt">${semRota
      ? '<span class="pill p-unk">SEM ROTEAMENTO PROVADO</span>'
      : '<span class="meta">pode interessar a:</span> ' + cons.join(' ')}</div>
  </div>`;
}

function viewToday() {
  const provados = P.objects.filter(o => o.PROOF_STATE === 'PROVED');
  const rev = P.objects.filter(o => o.OBJECT_TYPE === 'NEEDS_HUMAN_REVIEW');
  const dq = P.objects.filter(o => o.OBJECT_TYPE === 'DATA_QUALITY_EVENT');
  const exp = provados.filter(o => o.OBJECT_TYPE === 'EXPIRY_EVENT');
  const ordem = {ACT_NOW:0, PREPARE:1, MONITOR:2, PLAN_NEXT_CYCLE:3, NO_ACTION_YET:4, UNKNOWN:5};
  // Um vencimento que passou NAO e uma mudanca: e uma condicao que continua valendo.
  // Misturar os dois faz 15 cards iguais soterrarem as mudancas de verdade.
  const mudancas = provados.filter(o => o.OBJECT_TYPE !== 'EXPIRY_EVENT').sort((a,b) =>
    (ordem[a.TIME_WINDOW]??9) - (ordem[b.TIME_WINDOW]??9) ||
    String(b.DETECTED_AT).localeCompare(String(a.DETECTED_AT)));
  const condicoes = exp.slice().sort((a,b) => String(a.VALID_FROM).localeCompare(String(b.VALID_FROM)));
  $('#v-today').innerHTML = `
  <div class="cards">
    <div class="kpi"><b>${provados.filter(o=>o.OBJECT_TYPE!=='EXPIRY_EVENT').length}</b><span>mudancas provadas na janela</span></div>
    <div class="kpi"><b style="color:var(--bad)">${exp.length}</b><span>validade vencida e ainda listado ativo</span></div>
    <div class="kpi"><b style="color:var(--rev)">${rev.length}</b><span>itens que a maquina recusou adivinhar</span></div>
    <div class="kpi"><b style="color:var(--unk)">${dq.length}</b><span>estados de leitura a resolver</span></div>
    <div class="kpi"><b class="mono" style="font-size:15px">${esc(P.history.window)}</b><span>janela observada</span></div>
  </div>
  <div class="lei"><b>${P.history.raw_field_diffs}</b> diferencas brutas entre os instantaneos oficiais.
    <b>${P.history.noise}</b> (${P.history.noise_pct}%) sao a fonte reordenando a propria lista e nao viram evento.
    Restam <b>${P.history.true_changes}</b> mudancas reais. O que voce ve abaixo ja passou por esse filtro.</div>
  <h2>Mudou entre dois instantaneos oficiais (${mudancas.length})</h2>
  <div class="meta" style="margin-bottom:8px">Um campo do registro tinha um valor e passou a ter
    outro. Cada card mostra o antes, o depois, e os dois documentos que provam.</div>
  ${mudancas.map(cardObj).join('') || '<div class="block meta">nenhuma mudanca provada na janela</div>'}

  <h2>Condicoes que continuam valendo hoje (${condicoes.length})</h2>
  <div class="lei">Isto <b>nao mudou agora</b>: e um conflito entre dois campos oficiais que segue
    de pe. A validade declarada ja passou e o registro continua listando o produto como autorizado.
    <b>Vencer nao e ser revogado</b> &mdash; a ferramenta mostra os dois campos e nao conclui saida
    de mercado.</div>
  <div class="tw"><table>
    <thead><tr><th>Validade</th><th>Ha</th><th>Produto</th><th>Registro</th>
      <th>Estado declarado hoje</th><th></th></tr></thead>
    <tbody>${condicoes.map(o => {
      const p2 = byReg[o.REGISTRATION_ID] || {};
      return `<tr><td class="mono" style="color:var(--bad)">${esc(o.VALID_FROM)}</td>
      <td>${typeof p2.dte === 'number' ? (-p2.dte)+'d' : val('NOT_KNOWN')}</td>
      <td>${esc(o.PRODUCT_NAME)}</td><td class="mono">${esc(o.REGISTRATION_ID)}</td>
      <td>${val(p2.status)}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td></tr>`;
    }).join('')}</tbody></table></div>`;
}

// ---------------------------------------------------------------- 2 · PRODUCT 360
function viewProduto(reg) {
  const p = byReg[reg] || P.products[0];
  $('#psel').value = p.reg;
  const objs = P.objects.filter(o => o.REGISTRATION_ID === p.reg);
  const venc = typeof p.dte === 'number' && p.dte < 0;
  const porCultura = {};
  p.uses.forEach((u,i) => (porCultura[u.crop] = porCultura[u.crop]||[]).push({...u, i}));
  $('#pdet').innerHTML = `
  ${p.out_of_active_set ? `<div class="lei"><b>Este registro nao esta no conjunto ativo do
    instantaneo vigente.</b> ${esc(p.out_of_active_set_note)}</div>` : ''}
  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap">
      <h3>${esc(p.name)}</h3>
      <button class="ev" onclick="evProd('${p.reg}')">ver proveniencia</button></div>
    <div class="meta">registro <code>${esc(p.reg)}</code> &middot; ${esc(p.holder)} &middot; ${esc(p.activity)}</div>
    <div class="tw" style="margin-top:9px"><table><tbody>
      <tr><th>Substancias ativas</th><td>${val(p.actives)}</td></tr>
      <tr><th>Formulacao</th><td>${val(p.formulation)}</td></tr>
      <tr><th>Estado administrativo</th><td>${val(p.status)}</td></tr>
      <tr><th>Registrado em</th><td>${val(p.registered_at)}</td></tr>
      <tr><th>Validade</th><td${venc?' style="color:var(--bad)"':''}>${val(p.expiry)}
        ${venc?` &mdash; vencida ha ${-p.dte} dias e o registro ainda o lista como &ldquo;${esc(p.status)}&rdquo;.
        <span class="meta">EXPIRY != WITHDRAWAL — a ferramenta nao conclui saida de mercado</span>`:''}</td></tr>
      <tr><th>Etichetta em vigor desde</th><td>${val(p.label_effective)}</td></tr>
      <tr><th>Documento</th><td class="mono">${val(p.pdf_sha)}</td></tr>
    </tbody></table></div>
  </div>

  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline">
      <h3>Usos autorizados</h3>
      <span class="meta">${p.uses.length} pares &middot;
      ${p.uses.filter(u=>u.evidence==='TABLE_GEOMETRY').length} de tabela,
      ${p.uses.filter(u=>u.evidence!=='TABLE_GEOMETRY').length} de prosa/lista</span></div>
    ${p.uses.length ? `<div class="tw"><table>
      <thead><tr><th>Cultura</th><th>Alvos</th><th>Evidencia</th><th></th></tr></thead>
      <tbody>${Object.entries(porCultura).sort().map(([c,us]) => `<tr>
        <td><b>${esc(c)}</b></td>
        <td class="meta">${[...new Set(us.map(u=>u.target))].join(' &middot; ')}</td>
        <td>${(()=>{const t=us.filter(x=>x.evidence==='TABLE_GEOMETRY').length, n=us.length;
          return t===n?'<span class="pill p-ok">TABELA</span>'
               : t===0?'<span class="pill p-dim">TEXTO</span>'
               : `<span class="pill p-ok">TABELA ${t}</span> <span class="pill p-dim">TEXTO ${n-t}</span>`;})()}</td>
        <td>${us.map(x=>`<button class="ev" title="${esc(x.target)}" onclick="evUso('${p.reg}',${x.i})">${esc(String(x.target).slice(0,14))}</button>`).join(' ')}</td>
      </tr>`).join('')}</tbody></table></div>`
      : `<div class="lei">Nenhum par cultura x alvo foi lido para este produto.
         <b>Isto e estado de leitura, nao ausencia de uso autorizado.</b>
         <code>PARSER_FAILURE != REGULATORY_ABSENCE</code></div>`}
  </div>

  <div class="block">
    <div style="display:flex;justify-content:space-between;align-items:baseline">
      <h3>Dose</h3><span class="meta">estado do leitor: <code>${esc(p.dose_state)}</code></span></div>
    ${p.doses.length ? `<div class="tw"><table>
      <thead><tr><th>Cultura</th><th>Alvo</th><th>Dose/ha</th><th>Max</th><th>Intervalo</th><th>Fios</th><th></th></tr></thead>
      <tbody>${p.doses.map((d,i) => `<tr>
        <td>${esc(d.crop)}</td><td>${esc(d.target)}</td>
        <td>${isUnk(d.dose_ha)?val(d.dose_ha):esc(d.dose_ha+' '+d.unit_ha)}</td>
        <td>${val(d.max_app)}</td><td>${val(d.interval)}</td>
        <td><span class="pill ${d.rule_check==='CONFIRMED_BY_RULE'?'p-ok':d.rule_check==='CONTRADICTED_BY_RULE'?'p-bad':'p-unk'}"
          title="${d.rule_check==='NOT_LOCATED'?'a linha ou o valor nao foi localizado no documento para conferir contra os fios':d.rule_check==='NOT_CHECKED'?'esta linha nao foi submetida a conferencia por fios':''}"
          >${d.rule_check==='CONFIRMED_BY_RULE'?'CONFIRMADA':d.rule_check==='CONTRADICTED_BY_RULE'?'REVISAR':esc(d.rule_check)}</span></td>
        <td><button class="ev" onclick="evDose('${p.reg}',${i})">prova</button></td>
      </tr>`).join('')}</tbody></table></div>`
      : `<div class="lei">Dose nao estruturada para este produto (<code>${esc(p.dose_state)}</code>).
         A maioria dos herbicidas italianos declara dose em <b>prosa</b>, nao em tabela, e este
         leitor le tabela. <b>Isto nao significa produto sem dose.</b></div>`}
  </div>

  <div class="block">
    <h3>Tempo de carencia (PHI)</h3>
    <div class="lei">Nao publicado nesta versao. O extrator de carencia esta marcado
      <code>PROTOTYPE_NOT_SHIPPED</code>: 2 de 15 rotulos, com a primeira linha de cada bloco
      contaminada pela coluna vizinha. <b>As etichette trazem carencia; nos e que nao lemos.</b>
      <code>PHI_PROVED = 0</code> por decisao.</div>
  </div>

  <div class="block">
    <h3>Eventos deste produto (${objs.length})</h3>
    ${objs.length ? objs.map(cardObj).join('')
      : '<div class="meta">nenhum evento registrado na janela observada. <code>NO_CHANGE_OBSERVED_IN_WINDOW</code> nao e o mesmo que &ldquo;nunca mudou&rdquo;.</div>'}
  </div>`;
}
window.viewProduto = viewProduto;

// ---------------------------------------------------------------- 3 · TIMELINE
function viewTimeline() {
  const v = P.versions;
  const porData = {};
  P.objects.filter(o => o.PROOF_STATE === 'PROVED' && o.OBSERVATION_WINDOW)
    .forEach(o => (porData[o.OBSERVATION_WINDOW] = porData[o.OBSERVATION_WINDOW]||[]).push(o));
  $('#v-timeline').innerHTML = `
  <div class="lei">Tres coisas diferentes, que a ferramenta nunca funde:
    <b>DOCUMENT_DIFF</b> (o arquivo mudou de sha256) &middot;
    <b>SEMANTIC_DIFF</b> (um campo mudou de valor apos normalizacao) &middot;
    <b>REGULATORY_CHANGE_EVENT</b> (o campo que mudou tem significado regulatorio por regra R-*).
    Um documento novo nao e uma mudanca; um campo diferente nao e automaticamente regulatorio.</div>
  <div class="cards">
    <div class="kpi"><b>${P.history.snapshots}</b><span>instantaneos oficiais baixados</span></div>
    <div class="kpi"><b>${P.history.distinct}</b><span>documentos distintos por sha256</span></div>
    <div class="kpi"><b style="color:var(--dim)">${P.history.snapshots - P.history.distinct}</b><span>republicados sem mudar (nao contam como versao)</span></div>
    <div class="kpi"><b>${P.history.raw_field_diffs}</b><span>DOCUMENT/campo bruto</span></div>
    <div class="kpi"><b>${P.history.normalised_field_diffs}</b><span>SEMANTIC_DIFF apos normalizar</span></div>
    <div class="kpi"><b style="color:var(--ok)">${P.history.true_changes}</b><span>REGULATORY_CHANGE_EVENT</span></div>
  </div>
  <h2>Versoes arquivadas do registro oficial</h2>
  <div class="tw"><table>
    <thead><tr><th>Data</th><th>Versao (sha256)</th><th>Bytes</th><th>ADAMA ativos</th>
      <th>Republicado identico em</th><th>Eventos ate a versao seguinte</th><th></th></tr></thead>
    <tbody>${v.map((x,i) => {
      const jan = i < v.length-1 ? `${x.date}..${v[i+1].date}` : null;
      const evs = jan ? (porData[jan]||[]) : [];
      return `<tr>
        <td class="mono">${esc(x.date)}</td>
        <td class="mono">${esc(x.id)}</td>
        <td>${x.bytes.toLocaleString('pt-BR')}</td>
        <td>${x.adama_active}</td>
        <td class="meta">${x.republished.length ? x.republished.join(', ') : '<span class="meta">—</span>'}</td>
        <td>${evs.length ? `<b style="color:var(--ok)">${evs.length}</b>` : '<span class="meta">nenhum</span>'}</td>
        <td><a href="${esc(x.url)}" target="_blank">CSV</a></td></tr>`;}).join('')}
    </tbody></table></div>`;
}

// ---------------------------------------------------------------- 4 · CROP x TARGET
function viewCrop() {
  const q = ($('#cq')?.value || '').trim().toLowerCase();
  const qt = ($('#ct')?.value || '').trim().toLowerCase();
  const linhas = [];
  P.products.forEach(p => {
    p.uses.forEach((u,i) => {
      if (q && !String(u.crop).toLowerCase().includes(q)) return;
      if (qt && !String(u.target).toLowerCase().includes(qt)) return;
      const d = p.doses.find(x => casa(x.crop, u.crop) && casa(x.target, u.target));
      linhas.push({p, u, i, d});
    });
  });
  const prods = new Set(linhas.map(l => l.p.reg));
  $('#cres').innerHTML = `
    <div class="meta" style="margin:8px 0">${linhas.length} pares em ${prods.size} produtos.
      Dose aparece quando existe linha de dose lida para <b>este mesmo par</b> — o nome da cultura
      e casado apos normalizar, porque o leitor de uso escreve &ldquo;VITE&rdquo; e o de dose guarda
      &ldquo;Vite*&rdquo; como esta impresso. Quando nao existe, o campo diz
      <span class="unknown">NOT_KNOWN</span> em vez de ficar vazio.</div>
    <div class="tw"><table>
      <thead><tr><th>Produto</th><th>Registro</th><th>Cultura</th><th>Alvo</th>
        <th>Dose/ha</th><th>Evidencia do par</th><th>Validade</th><th></th></tr></thead>
      <tbody>${linhas.slice(0,400).map(l => `<tr>
        <td><a onclick="go('produto');viewProduto('${l.p.reg}')" style="cursor:pointer">${esc(l.p.name)}</a></td>
        <td class="mono">${esc(l.p.reg)}</td>
        <td>${esc(l.u.crop)}</td><td>${esc(l.u.target)}</td>
        <td>${l.d ? (isUnk(l.d.dose_ha)?val(l.d.dose_ha):esc(l.d.dose_ha+' '+l.d.unit_ha)+
             (l.d.rule_check==='CONTRADICTED_BY_RULE'?' <span class="pill p-bad">REVISAR</span>':''))
             : val('NOT_KNOWN')}</td>
        <td><span class="pill ${l.u.evidence==='TABLE_GEOMETRY'?'p-ok':'p-dim'}">${l.u.evidence==='TABLE_GEOMETRY'?'TABELA':'TEXTO'}</span></td>
        <td>${validade(l.p)}</td>
        <td><button class="ev" onclick="evUso('${l.p.reg}',${l.i})">prova</button></td>
      </tr>`).join('')}</tbody></table></div>
    ${linhas.length>400?`<div class="meta">mostrando 400 de ${linhas.length} — refine a busca</div>`:''}`;
}
window.viewCrop = viewCrop;

// ---------------------------------------------------------------- 5 · CALENDAR
function viewCal() {
  const fx = [[30,'30 dias'],[90,'90 dias'],[180,'180 dias'],[365,'12 meses']];
  const venc = P.products.filter(p => typeof p.dte === 'number' && p.dte < 0);
  const bloco = (lo,hi,lbl) => {
    const l = P.products.filter(p => typeof p.dte === 'number' && p.dte >= lo && p.dte <= hi)
      .sort((a,b) => a.dte - b.dte);
    return `<div class="block"><h3>${lbl} <span class="meta">(${l.length})</span></h3>
    ${l.length ? `<div class="tw"><table>
      <thead><tr><th>Validade</th><th>Faltam</th><th>Produto</th><th>Registro</th><th>Estado</th><th>Usos lidos</th><th></th></tr></thead>
      <tbody>${l.map(p=>`<tr><td class="mono">${esc(p.expiry)}</td><td>${p.dte}d</td>
        <td>${esc(p.name)}</td><td class="mono">${esc(p.reg)}</td><td class="meta">${esc(p.status)}</td>
        <td>${p.uses.length||'<span class="unknown">NOT_KNOWN</span>'}</td>
        <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
      </tbody></table></div>` : '<div class="meta">nenhum produto nesta janela</div>'}</div>`;
  };
  $('#v-cal').innerHTML = `
  <div class="lei">Todas as datas abaixo vem do campo <code>data_scadenza_autorizzazione</code> do
    registro oficial. <b>A ferramenta nao cria prazo que nao esta na fonte</b> — nao ha deadline de
    revisao inventado aqui. E vencimento nao e revogacao.</div>
  <div class="block" style="border-left:3px solid var(--bad)">
    <h3>Validade ja vencida, e o registro ainda lista como ativo <span class="meta">(${venc.length})</span></h3>
    <div class="meta">Estes sao um conflito entre dois campos oficiais de hoje, nao uma conclusao nossa.</div>
    <div class="tw" style="margin-top:8px"><table>
      <thead><tr><th>Validade</th><th>Ha</th><th>Produto</th><th>Registro</th><th>Estado declarado</th><th></th></tr></thead>
      <tbody>${venc.sort((a,b)=>a.expiry.localeCompare(b.expiry)).map(p=>`<tr>
        <td class="mono" style="color:var(--bad)">${esc(p.expiry)}</td><td>${-p.dte}d</td>
        <td>${esc(p.name)}</td><td class="mono">${esc(p.reg)}</td><td>${esc(p.status)}</td>
        <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
      </tbody></table></div></div>
  ${bloco(0,30,'Vencem em ate 30 dias')}
  ${bloco(31,90,'31 a 90 dias')}
  ${bloco(91,180,'91 a 180 dias')}
  ${bloco(181,365,'181 dias a 12 meses')}`;
}

// ---------------------------------------------------------------- 6 · ACTION CENTER
function viewAction() {
  const caps = Object.keys(CAPS);
  const blocos = caps.map(c => {
    const meus = P.objects.map(o => {
      const r = o.CAPABILITY_ROUTING.find(x => x.CAPABILITY_ID === c);
      return r ? {o, r} : null;
    }).filter(Boolean);
    const porEstado = {};
    meus.forEach(x => (porEstado[x.r.ROUTING_STATE] = porEstado[x.r.ROUTING_STATE]||[]).push(x));
    const rtvNota = c === 'COMMERCIAL_RTV'
      ? `<div class="lei">O campo nao recebe fato regulatorio bruto. Regra <code>C-05</code>:
         tudo fica <code>NOT_RELEVANT</code> ate o portao <code>G-01</code>, que exige prova e
         revisao humana registrada. <b>Esta versao nao abre esse portao.</b>
         A ferramenta so criaria <code>COMMERCIAL_MESSAGE_CANDIDATE</code>, nunca uma mensagem.</div>`
      : '';
    if (!meus.length) return `<div class="block"><h3>${CAPS[c]}</h3>${rtvNota}
      <div class="meta">nenhum objeto alcanca esta capacidade</div></div>`;
    const linha = (est, lista) => `<div style="margin:9px 0">
      <span class="pill ${est==='RELEVANT'?'p-ok':est==='POTENTIALLY_RELEVANT'?'p-warn':est==='NOT_RELEVANT'?'p-dim':'p-unk'}">${est}</span>
      ${est==='UNKNOWN'?'<span class="meta">— nenhuma regra cobre este tipo para esta area. <b>Isto nao diz que a area nao precisa olhar; diz que nao sabemos.</b></span>':''}
      <span class="meta">${lista.length} objeto(s) &middot; regra ${esc(lista[0].r.RULE_ID)} — ${esc(lista[0].r.JUSTIFICATION)}</span>
      <div class="tw" style="margin-top:6px"><table>
        <thead><tr><th>Produto</th><th>Tipo</th><th>Antes &rarr; Depois</th><th>Janela</th><th>Prova</th><th></th></tr></thead>
        <tbody>${lista.slice(0,60).map(({o}) => `<tr>
          <td>${esc(o.PRODUCT_NAME||'NOT_KNOWN')}<div class="mono meta">${esc(o.REGISTRATION_ID)}</div></td>
          <td>${esc(o.CHANGE_TYPE)}</td>
          <td>${val(o.BEFORE_VALUE)} &rarr; ${val(o.AFTER_VALUE)}</td>
          <td><span class="pill ${(WIN[o.TIME_WINDOW]||[,'p-dim'])[1]}">${esc(o.TIME_WINDOW)}</span></td>
          <td><span class="pill ${PROOF[o.PROOF_STATE]||'p-dim'}">${esc(o.PROOF_STATE)}</span></td>
          <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td>
        </tr>`).join('')}</tbody></table></div>
      ${lista.length>60?`<div class="meta">mostrando 60 de ${lista.length}</div>`:''}</div>`;
    return `<div class="block"><h3>${CAPS[c]} <span class="meta">(${meus.length})</span></h3>${rtvNota}
      ${['RELEVANT','POTENTIALLY_RELEVANT','UNKNOWN','NEEDS_REVIEW','NOT_RELEVANT']
        .filter(e => porEstado[e]).map(e => linha(e, porEstado[e])).join('')}</div>`;
  });
  $('#v-action').innerHTML = `
  <div class="lei">Roteamento diz <b>quem pode precisar olhar</b>, nunca <b>o que fazer</b>.
    Cada estado abaixo aponta a regra <code>C-*</code> que o autoriza, em
    <code>v1/inteligencia/REGRAS.md</code>. Tipo de evento sem regra sai <code>UNKNOWN</code>.
    <b>Esta ferramenta nao emite ACTION.</b></div>
  ${blocos.join('')}`;
}

// ---------------------------------------------------------------- 7 · REVIEW QUEUE
function viewReview() {
  const rev = P.objects.filter(o => o.OBJECT_TYPE === 'NEEDS_HUMAN_REVIEW');
  const dq = P.objects.filter(o => o.OBJECT_TYPE === 'DATA_QUALITY_EVENT');
  const semUso = P.products.filter(p => !p.uses.length);
  const semDose = P.products.filter(p => !p.doses.length);
  $('#v-review').innerHTML = `
  <div class="lei"><b>Esta tela mostra o que a maquina recusou adivinhar.</b>
    Nenhum item aqui e uma afirmacao sobre o produto — todos sao afirmacoes sobre o
    <b>nosso estado de leitura</b>. <code>PARSER_FAILURE != REGULATORY_ABSENCE</code></div>
  <div class="cards">
    <div class="kpi"><b style="color:var(--rev)">${rev.length}</b><span>doses rebaixadas por contradicao de fio</span></div>
    <div class="kpi"><b style="color:var(--unk)">${dq.length}</b><span>rotulos sem tabela de uso lida</span></div>
    <div class="kpi"><b style="color:var(--unk)">${semUso.length}</b><span>produtos sem par cultura x alvo</span></div>
    <div class="kpi"><b style="color:var(--unk)">${semDose.length}</b><span>produtos sem dose estruturada</span></div>
    <div class="kpi"><b style="color:var(--unk)">${P.products.length}</b><span>produtos sem PHI (nao publicado)</span></div>
  </div>

  <h2>Dose rebaixada: o fio da tabela contradiz o valor (${rev.length})</h2>
  <div class="meta" style="margin-bottom:8px">O extrator leu um valor; os fios desenhados da tabela
    mostram que ele pertence a outra linha. O valor foi <b>rebaixado, nao corrigido no palpite</b> —
    trocar um erro por outro nao e conserto.</div>
  <div class="tw"><table>
    <thead><tr><th>Produto</th><th>Cultura</th><th>Alvo</th><th>Valor rebaixado</th><th>Onde</th><th></th></tr></thead>
    <tbody>${rev.map(o => `<tr>
      <td>${esc(o.PRODUCT_NAME)}<div class="mono meta">${esc(o.REGISTRATION_ID)}</div></td>
      <td>${val(o.AFFECTED_CROP)}</td><td>${val(o.AFFECTED_TARGET)}</td>
      <td style="color:var(--bad)">${val(o.BEFORE_VALUE)}</td>
      <td class="meta">${val(o.EVIDENCE_LOCATION)}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td>
    </tr>`).join('') || '<tr><td colspan=6 class="meta">nenhuma</td></tr>'}</tbody></table></div>

  <h2>Rotulos cuja tabela de uso nao foi lida (${dq.length})</h2>
  <div class="lei">A maioria dos herbicidas italianos declara dose em <b>prosa</b>
    (&ldquo;alla dose di 1-3 l/ha&rdquo;), nao em tabela. Este leitor le tabela.
    <b>Nenhum destes produtos e um produto sem uso ou sem dose.</b></div>
  <div class="tw"><table>
    <thead><tr><th>Produto</th><th>Registro</th><th>Atividade</th><th>Estado do leitor</th><th>Pares lidos</th><th></th></tr></thead>
    <tbody>${dq.slice(0,200).map(o => {
      const p = byReg[o.REGISTRATION_ID] || {};
      return `<tr><td>${esc(o.PRODUCT_NAME)}</td><td class="mono">${esc(o.REGISTRATION_ID)}</td>
      <td class="meta">${esc(p.activity||'NOT_KNOWN')}</td>
      <td><code>${esc(p.dose_state||'NOT_ATTEMPTED')}</code></td>
      <td>${p.uses?p.uses.length:0}</td>
      <td><button class="ev" onclick="evObj('${o.INTELLIGENCE_OBJECT_ID}')">evidencia</button></td></tr>`;
    }).join('')}</tbody></table></div>`;
}

// ---------------------------------------------------------------- 9 · COVERAGE
function viewCov() {
  const c = P.coverage;
  const barra = (k, o) => `<tr><td>${k.replace(/_/g,' ')}</td>
    <td><b>${o.COVERED}</b> <span class="meta">de ${o.OF}</span></td>
    <td style="width:44%"><div style="background:#0b0e10;border-radius:4px;height:16px;position:relative">
      <div style="position:absolute;inset:0 auto 0 0;width:${o.PCT}%;background:${o.PCT>=90?'var(--ok)':o.PCT>=40?'var(--warn)':'var(--unk)'};border-radius:4px"></div>
      <b style="position:relative;font-size:10.5px;padding-left:6px;line-height:16px">${o.PCT}%</b></div></td></tr>`;
  $('#v-cov').innerHTML = `
  <div class="lei"><b>Nao existe um numero unico de cobertura nesta ferramenta.</b>
    Cada linha abaixo conta uma coisa diferente e <b>nenhuma implica a seguinte</b>:
    ter o PDF nao e ter lido, ter lido nao e ter estruturado o uso, e ter o uso nao e ter a dose.</div>
  <div class="block"><h3>Cobertura por etapa</h3>
    <div class="tw"><table><tbody>${Object.entries(c).map(([k,o]) => barra(k,o)).join('')}</tbody></table></div>
    <div class="meta" style="margin-top:9px">${esc(P.coverage_note)}</div></div>
  <div class="block"><h3>Historico e comparabilidade</h3>
    <div class="tw"><table><tbody>
      <tr><td>Instantaneos oficiais baixados</td><td><b>${P.history.snapshots}</b></td></tr>
      <tr><td>Documentos distintos (sha256)</td><td><b>${P.history.distinct}</b></td></tr>
      <tr><td>Janela observada</td><td class="mono">${esc(P.history.window)}</td></tr>
      <tr><td>Diferencas brutas de campo</td><td>${P.history.raw_field_diffs}</td></tr>
      <tr><td>Apos normalizar (SEMANTIC_DIFF)</td><td>${P.history.normalised_field_diffs}</td></tr>
      <tr><td>Ruido de serializacao suprimido</td><td><b>${P.history.noise}</b> (${P.history.noise_pct}%)</td></tr>
      <tr><td>Eventos regulatorios</td><td><b style="color:var(--ok)">${P.history.true_changes}</b></td></tr>
    </tbody></table></div></div>
  <div class="block"><h3>O que esta versao declaradamente nao faz</h3>
    <ul class="meta" style="line-height:1.8">
      <li>nao emite <code>ACTION</code> — o parser nao produz acao;</li>
      <li>nao emite <code>PHI_CHANGE</code> — portao <code>G-02</code> fechado, <code>PHI_PROVED = 0</code>;</li>
      <li>nao emite implicacao de negocio — portao <code>G-03</code>, nenhuma regra <code>B-*</code> existe;</li>
      <li>nao envia nada ao campo — portao <code>G-01</code> fechado;</li>
      <li>nao infere demanda, estoque, preco ou concorrencia a partir de rotulo;</li>
      <li>nao publica citacao literal dos pares cultura x alvo: os pares reusados nao gravam
          coordenada x e a etichetta tem varias colunas por pagina. Tentado, medido, descartado.</li>
    </ul></div>`;
}

// ---------------------------------------------------------------- 10 · SEARCH
function viewSearch() {
  const q = ($('#sq').value||'').trim().toLowerCase();
  if (!q) { $('#sres').innerHTML = '<div class="meta">digite um produto, registro, cultura, alvo, substancia ativa, estado ou tipo de mudanca</div>'; return; }
  const prods = P.products.filter(p =>
    [p.name,p.reg,p.actives,p.holder,p.status,p.activity,p.formulation].join(' ').toLowerCase().includes(q)
    || p.uses.some(u => (u.crop+' '+u.target).toLowerCase().includes(q)));
  const objs = P.objects.filter(o =>
    [o.PRODUCT_NAME,o.REGISTRATION_ID,o.CHANGE_TYPE,o.FACT,o.BEFORE_VALUE,o.AFTER_VALUE]
      .join(' ').toLowerCase().includes(q));
  $('#sres').innerHTML = `
  <div class="lei">A busca so consulta os <b>intelligence objects</b> e os produtos ja resolvidos
    pela inteligencia. <b>Ela nao le PDF e nao gera resposta livre.</b> Toda linha do resultado
    leva a prova.</div>
  <h2>Produtos (${prods.length})</h2>
  ${prods.length ? `<div class="tw"><table>
    <thead><tr><th>Produto</th><th>Registro</th><th>Titular</th><th>Ativos</th><th>Validade</th><th>Usos</th><th>Doses</th><th></th></tr></thead>
    <tbody>${prods.slice(0,80).map(p=>`<tr>
      <td><a onclick="go('produto');viewProduto('${p.reg}')" style="cursor:pointer">${esc(p.name)}</a></td>
      <td class="mono">${esc(p.reg)}</td><td class="meta">${esc(p.holder)}</td>
      <td class="meta">${val(p.actives)}</td><td>${val(p.expiry)}</td>
      <td>${p.uses.length||'<span class="unknown">0 lidos</span>'}</td>
      <td>${p.doses.length||'<span class="unknown">NOT_KNOWN</span>'}</td>
      <td><button class="ev" onclick="evProd('${p.reg}')">prova</button></td></tr>`).join('')}
    </tbody></table></div>` : '<div class="meta">nenhum produto</div>'}
  <h2>Eventos (${objs.length})</h2>
  ${objs.length ? objs.slice(0,40).map(cardObj).join('') : '<div class="meta">nenhum evento</div>'}`;
}
window.viewSearch = viewSearch;

// ---------------------------------------------------------------- roteador
const VIEWS = {today:viewToday, produto:()=>viewProduto($('#psel').value),
               timeline:viewTimeline, crop:viewCrop, cal:viewCal, action:viewAction,
               review:viewReview, cov:viewCov, search:viewSearch};
function go(v) {
  $$('nav a').forEach(a => a.classList.toggle('on', a.dataset.v === v));
  $$('.view').forEach(x => x.classList.remove('on'));
  $('#v-'+v).classList.add('on');
  (VIEWS[v]||(()=>{}))();
  window.scrollTo(0,0);
}
window.go = go;
$$('nav a').forEach(a => a.onclick = () => go(a.dataset.v));
document.addEventListener('keydown', e => { if (e.key === 'Escape') $('#dr').classList.remove('open'); });

// selects e buscas
$('#psel').innerHTML = P.products.slice().sort((a,b)=>a.name.localeCompare(b.name))
  .map(p => `<option value="${p.reg}">${esc(p.name)} — ${esc(p.reg)}</option>`).join('');
$('#psel').addEventListener('change', () => viewProduto($('#psel').value));
['cq','ct'].forEach(id => $('#'+id).addEventListener('input', viewCrop));
$('#sq').addEventListener('input', viewSearch);

go('today');
