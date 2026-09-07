/* SINTONIA SYSTEM MAP — a tela
   ---------------------------------------------------------------------------
   ESTA TELA NAO SABE NADA.

   Nenhum facto arquitectural mora aqui: nem nome de peca, nem ligacao, nem
   status, nem departamento. Tudo vem de `state.generated.json`, que e produzido
   pelo gerador a partir do repositorio. Este ficheiro so desenha.

   E de proposito, e e a regra que impede o mapa de virar uma segunda verdade:
   se a arquitectura mudar e ninguem regerar, esta tela nao tem como mentir
   bonito — ela mostra o que o ficheiro diz, e o CI reprova o ficheiro velho.

   Enquanto leres este ficheiro, se encontrares um `if (id === 'C-...')` com
   regra de negocio dentro, isso e um bug: e facto a esconder-se no frontend.
   --------------------------------------------------------------------------- */
'use strict';

const NS = 'http://www.w3.org/2000/svg';
const el = (t, a = {}) => { const n = document.createElementNS(NS, t);
  for (const k in a) n.setAttribute(k, a[k]); return n; };
const txt = s => document.createTextNode(s);
const $ = s => document.querySelector(s);

const CORES = { PROVEN: 'var(--st-proven)', PENDING: 'var(--st-pending)',
                BROKEN: 'var(--st-broken)', UNKNOWN: 'var(--st-unknown)' };
const ROTULO = { PROVEN: 'PROVADO OPERACIONAL', PENDING: 'PROVADO COM PENDENCIA',
                 BROKEN: 'QUEBRADO OU AUSENTE', UNKNOWN: 'NAO SEI' };
const EMOJI = { PROVEN: '🟢', PENDING: '🟡', BROKEN: '🔴', UNKNOWN: '⚪' };

/* Cor de marca por territorio. Vem das linhas oficiais do ADAMA Design System
   (tokens/colors.css). Nao ha cor inventada: se um territorio novo aparecer sem
   linha atribuida, cai no verde corporativo em vez de ganhar uma cor nova. */
const LINHA = {
  'T-FONTE':   '#00a0df', 'T-REGUA':  '#752157', 'T-MOTOR':  '#009845',
  'T-PACOTE':  '#f89e18', 'T-PORTAL': '#7db41e', 'T-PORTAO': '#9d1d96',
  'T-PERSIST': '#00698f', 'T-CI':     '#00783f', 'T-PROVA':  '#f5b317',
  'T-DS':      '#93cc23', 'T-MAPA':   '#978b87',
};
const corTerr = id => LINHA[id] || '#009845';

/* Geometria — deterministica, calculada a partir da ordem dos territorios.
   Mesmo ficheiro de estado = mesmo desenho, sempre. */
const COL = 5, LARG = 250, ALT = 62, GAPX = 26, GAPY = 16, CAB = 58, PAD = 22, GAPT = 46;

let S, nos = new Map(), caixas = new Map(), MUNDO = { w: 0, h: 0 };
let vista = { x: 0, y: 0, k: 1 };
const filtro = { status: new Set(['PROVEN', 'PENDING', 'BROKEN', 'UNKNOWN']),
                 terr: '', dept: '', kind: '', busca: '', legado: '', foco: null, caminho: false };

/* ══ 1 · POSICIONAR ═══════════════════════════════════════════════════════ */
function dispor() {
  let y = PAD;
  for (const t of S.TERRITORIES) {
    const membros = S.NODES.filter(n => n.territory === t.id);
    if (!membros.length) continue;
    const linhas = Math.ceil(membros.length / COL);
    const cols = Math.min(COL, membros.length);
    const w = PAD * 2 + cols * LARG + (cols - 1) * GAPX;
    const h = CAB + PAD + linhas * ALT + (linhas - 1) * GAPY + PAD;
    caixas.set(t.id, { ...t, x: PAD, y, w, h, membros });
    membros.forEach((n, i) => {
      nos.set(n.id, { ...n,
        x: PAD + PAD + (i % COL) * (LARG + GAPX),
        y: y + CAB + PAD + Math.floor(i / COL) * (ALT + GAPY),
        w: LARG, h: ALT });
    });
    y += h + GAPT;
  }
  MUNDO = { w: Math.max(...[...caixas.values()].map(c => c.x + c.w)) + PAD, h: y };
}

/* ══ 2 · DESENHAR ═════════════════════════════════════════════════════════ */
function desenhar() {
  const svg = $('#palco svg');
  svg.textContent = '';
  const g = el('g', { id: 'camera' });
  svg.appendChild(g);

  const gT = el('g'), gA = el('g'), gP = el('g');
  g.append(gT, gA, gP);

  for (const c of caixas.values()) {
    const grupo = el('g', { class: 'territorio-grupo', 'data-terr': c.id });
    grupo.appendChild(el('rect', { class: 'territorio-caixa', x: c.x, y: c.y,
      width: c.w, height: c.h, rx: 12 }));
    const faixa = el('path', { class: 'territorio-faixa', fill: corTerr(c.id),
      d: `M${c.x} ${c.y + 12} a12 12 0 0 1 12 -12 h${c.w - 24} a12 12 0 0 1 12 12 v${CAB - 12} h${-c.w} Z` });
    grupo.appendChild(faixa);
    const nome = el('text', { class: 'territorio-nome', x: c.x + PAD, y: c.y + 25 });
    nome.appendChild(txt(c.name)); grupo.appendChild(nome);
    const why = el('text', { class: 'territorio-why', x: c.x + PAD, y: c.y + 43 });
    why.appendChild(txt(c.why.length > 96 ? c.why.slice(0, 95) + '…' : c.why));
    grupo.appendChild(why);
    gT.appendChild(grupo);
  }

  for (const e of S.EDGES) {
    const a = nos.get(e.from), b = nos.get(e.to);
    if (!a || !b) continue;
    const x1 = a.x + a.w / 2, y1 = a.y + a.h / 2, x2 = b.x + b.w / 2, y2 = b.y + b.h / 2;
    const dy = Math.abs(y2 - y1);
    const p = el('path', {
      class: 'aresta' + (e.kind === 'expected' ? ' expected' : ''),
      'data-from': e.from, 'data-to': e.to, 'data-type': e.type,
      d: `M${x1} ${y1} C ${x1} ${y1 + dy * .3}, ${x2} ${y2 - dy * .3}, ${x2} ${y2}`,
    });
    p.addEventListener('mouseenter', ev => dica(ev, dicaAresta(e)));
    p.addEventListener('mouseleave', esconderDica);
    gA.appendChild(p);
  }

  for (const n of nos.values()) {
    const grupo = el('g', { class: 'peca', 'data-id': n.id, tabindex: '0',
      role: 'button', 'aria-label': `${n.name} — ${ROTULO[n.status]}` });
    grupo.appendChild(el('rect', { class: 'corpo', x: n.x, y: n.y,
      width: n.w, height: n.h, stroke: CORES[n.status] }));
    grupo.appendChild(el('rect', { class: 'barra', x: n.x, y: n.y,
      width: 4, height: n.h, fill: corTerr(n.territory) }));
    grupo.appendChild(el('circle', { cx: n.x + n.w - 15, cy: n.y + 16, r: 5.5,
      fill: CORES[n.status] }));
    const nome = el('text', { class: 'nome', x: n.x + 15, y: n.y + 24 });
    nome.appendChild(txt(n.name.length > 30 ? n.name.slice(0, 29) + '…' : n.name));
    const tipo = el('text', { class: 'tipo', x: n.x + 15, y: n.y + 42 });
    tipo.appendChild(txt(`${n.kind} · ${n.file_count} ficheiro${n.file_count === 1 ? '' : 's'}`));
    grupo.append(nome, tipo);
    grupo.addEventListener('mouseenter', ev => dica(ev, dicaPeca(n)));
    grupo.addEventListener('mousemove', mover);
    grupo.addEventListener('mouseleave', esconderDica);
    grupo.addEventListener('click', ev => { ev.stopPropagation(); abrir(n.id); });
    grupo.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); abrir(n.id); } });
    gP.appendChild(grupo);
  }
  aplicarCamera();
  minimapa();
}

/* ══ 3 · A DICA — o que a peca faz, em portugues comum ════════════════════ */
function dicaPeca(n) {
  const de = n.inbound.map(i => nos.get(i)?.name).filter(Boolean);
  const pa = n.outbound.map(i => nos.get(i)?.name).filter(Boolean);
  return `<b>${esc(n.name)}</b>
    <div class="l">o que faz</div>${esc(n.what)}
    <div class="l">por que esta aqui</div>${esc(n.why_here)}
    <div class="l">recebe de</div>${de.length ? esc(de.slice(0, 3).join(' · ')) : '— ninguem'}
    <div class="l">envia para</div>${pa.length ? esc(pa.slice(0, 3).join(' · ')) : '— ninguem'}
    <div class="l">status</div>${EMOJI[n.status]} ${ROTULO[n.status]}${
      n.legacy ? '  ·  ⚠ LEGADO — não é a peça oficial de hoje' : ''}
    <div class="l">motivo</div>${esc(n.status_reason)}`;
}
function dicaAresta(e) {
  return `<b>${esc(nos.get(e.from)?.name)} → ${esc(nos.get(e.to)?.name)}</b>
    <div class="l">o que passa aqui</div>${esc(e.payload || e.type)}
    <div class="l">por que</div>${esc(e.reason)}
    <div class="l">prova</div>${e.evidence?.length
      ? esc(e.evidence[0].file + ':' + e.evidence[0].line)
      : '⚪ NAO SEI — nao ha linha de codigo que prove'}`;
}
const esc = s => String(s ?? '').replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function dica(ev, html) { const d = $('#dica'); d.innerHTML = html; d.classList.add('on'); mover(ev); }
function mover(ev) {
  const d = $('#dica'), r = d.getBoundingClientRect();
  d.style.left = Math.min(ev.clientX + 16, innerWidth - r.width - 12) + 'px';
  d.style.top = Math.min(ev.clientY + 16, innerHeight - r.height - 12) + 'px';
}
const esconderDica = () => $('#dica').classList.remove('on');

/* ══ 4 · O PAINEL — o detalhe todo ════════════════════════════════════════ */
function abrir(id) {
  const n = nos.get(id); if (!n) return;
  filtro.foco = id; esconderDica();

  const linkNo = i => `<a data-ir="${i}">${esc(nos.get(i)?.name || i)}</a>`;
  const entra = S.EDGES.filter(e => e.to === id), sai = S.EDGES.filter(e => e.from === id);
  const negocio = S.BUSINESS_EDGES.filter(b => b.from === id);

  const bloco = (titulo, arr) => arr.length ? `<h3>${titulo}</h3><ul class="lista">${arr.join('')}</ul>` : '';
  const linhaAresta = (e, dir) => `<li>${linkNo(dir === 'in' ? e.from : e.to)}
      <div class="caminho">${esc(e.type)} · ${esc(e.reason)}</div>
      ${e.evidence?.length
        ? `<div class="prova">${e.evidence.slice(0, 3)
             .map(v => esc(v.file + ':' + v.line + '  ' + v.snippet)).join('\n')}</div>`
        : '<div class="prova">⚪ NAO SEI — declarado, nao provado</div>'}</li>`;

  $('#painel').innerHTML = `
    <button id="fechar" aria-label="fechar">×</button>
    <h2>${esc(n.name)}</h2>
    <div class="sub">${EMOJI[n.status]} ${ROTULO[n.status]} ·
      ${esc(caixas.get(n.territory)?.name || '')} · ${esc(n.kind)}</div>
    ${n.legacy ? `<div class="destaque" style="border-color:var(--st-unknown)">
      ⚠ <b>LEGADO.</b> Esta peça continua no repositório, e por isso aparece no mapa —
      mas <b>não é a peça oficial de hoje</b>. Não a tome como o caminho atual.</div>` : ''}

    <h3>o que faz</h3><p>${esc(n.what)}</p>
    <h3>por que esta aqui</h3><p>${esc(n.why_here)}</p>
    <h3>por que este status</h3><div class="destaque"
      style="border-color:${CORES[n.status]}">${esc(n.status_reason)}</div>

    ${n.departments?.length ? `<h3>departamentos</h3>${n.departments
      .map(d => `<span class="etiqueta" title="${esc(S.DEPARTMENTS[d] || '')}">${esc(d.replace(/_/g, ' '))}</span>`).join('')}` : ''}

    ${negocio.length ? `<h3>a quem isto serve (declarado)</h3><ul class="lista">${negocio.map(b => `
      <li><b>${esc(b.to.replace('DEPT:', '').replace(/_/g, ' '))}</b>
        <div class="caminho">${esc(b.reason)}</div>
        <div class="prova">declarado por ${esc(b.declared_by)} em ${esc(b.declared_at)}
fonte: ${esc(b.source)}</div></li>`).join('')}</ul>` : ''}

    ${bloco('recebe de', entra.map(e => linhaAresta(e, 'in')))}
    ${bloco('envia para', sai.map(e => linhaAresta(e, 'out')))}
    ${bloco(`ficheiros que implementam isto (${n.files.length})`,
      n.files.map(f => `<li class="caminho">${esc(f)}</li>`))}
    ${n.changed_since_declared?.length ? `<h3>mudou desde a ultima leitura humana</h3>
      <ul class="lista">${n.changed_since_declared
        .map(f => `<li class="caminho">${esc(f)}</li>`).join('')}</ul>` : ''}

    <h3>como pedir mudanca</h3>
    <p style="font-size:12.5px;color:var(--ink-mute)">Esta tela nao altera codigo — de proposito.
    Para mudar isto: abra uma missao no repositorio, altere o codigo, rode
    <code>py system-map/scripts/generate_system_map.py</code> e o mapa acompanha.
    Nunca o contrario.</p>`;

  $('#painel').classList.add('aberto');
  $('#fechar').onclick = fechar;
  $('#painel').querySelectorAll('[data-ir]').forEach(a =>
    a.onclick = () => { abrir(a.dataset.ir); centrarEm(a.dataset.ir); });
  filtro.caminho = true; aplicarFiltros(); centrarEm(id);
}
function fechar() {
  $('#painel').classList.remove('aberto');
  filtro.foco = null; filtro.caminho = false; aplicarFiltros();
}

/* ══ 5 · FILTROS E CAMINHO ════════════════════════════════════════════════ */
function aplicarFiltros() {
  const q = filtro.busca.trim().toLowerCase();
  const ligados = new Set();
  if (filtro.foco) {
    ligados.add(filtro.foco);
    for (const e of S.EDGES) {
      if (e.from === filtro.foco) ligados.add(e.to);
      if (e.to === filtro.foco) ligados.add(e.from);
    }
  }
  const visivel = new Set();
  for (const n of nos.values()) {
    let ok = filtro.status.has(n.status)
      && (!filtro.terr || n.territory === filtro.terr)
      && (!filtro.kind || n.kind === filtro.kind)
      && (!filtro.dept || (n.departments || []).includes(filtro.dept))
      && (!filtro.legado || (filtro.legado === 'legado' ? n.legacy : !n.legacy))
      && (!q || (n.name + ' ' + n.what + ' ' + n.why_here + ' ' + n.id + ' ' +
                 n.files.join(' ')).toLowerCase().includes(q));
    if (filtro.caminho && ligados.size) ok = ok && ligados.has(n.id);
    if (ok) visivel.add(n.id);
  }
  document.querySelectorAll('.peca').forEach(g =>
    g.classList.toggle('apagada', !visivel.has(g.dataset.id)));
  document.querySelectorAll('.peca').forEach(g =>
    g.classList.toggle('focada', g.dataset.id === filtro.foco));
  document.querySelectorAll('.aresta').forEach(p => {
    const dentro = visivel.has(p.dataset.from) && visivel.has(p.dataset.to);
    const noCaminho = filtro.foco &&
      (p.dataset.from === filtro.foco || p.dataset.to === filtro.foco);
    p.classList.toggle('apagada', !dentro);
    p.classList.toggle('acesa', !!noCaminho);
  });
  document.querySelectorAll('.territorio-grupo').forEach(g =>
    g.classList.toggle('apagada',
      !S.NODES.some(n => n.territory === g.dataset.terr && visivel.has(n.id))));
  $('#conta').textContent = `${visivel.size} de ${S.NODES.length} pecas`;
}

/* ══ 6 · CAMERA — pan, zoom, fit, minimapa ════════════════════════════════ */
const palco = () => $('#palco');
function aplicarCamera() {
  const c = document.getElementById('camera');
  if (c) c.setAttribute('transform',
    `translate(${vista.x} ${vista.y}) scale(${vista.k})`);
  minimapaVp();
}
function ajustar() {
  const r = palco().getBoundingClientRect();
  // Se o palco ainda nao tem tamanho (a primeira chamada pode acontecer antes de
  // o browser ter feito o layout), `Math.min` daria escala 0 e o mapa saia
  // invisivel — desenhado, com 51 pecas no DOM, e a zero pixeis. Tenta outra vez
  // no frame seguinte em vez de publicar uma tela em branco.
  if (r.width < 2 || r.height < 2) { requestAnimationFrame(ajustar); return; }
  vista.k = Math.min(r.width / (MUNDO.w + 40), r.height / (MUNDO.h + 40), 1.6);
  vista.x = (r.width - MUNDO.w * vista.k) / 2;
  vista.y = (r.height - MUNDO.h * vista.k) / 2;
  aplicarCamera();
}
function centrarEm(id) {
  const n = nos.get(id); if (!n) return;
  const r = palco().getBoundingClientRect();
  vista.k = Math.max(vista.k, .85);
  const largura = $('#painel').classList.contains('aberto') && r.width > 860
    ? r.width - 430 : r.width;
  vista.x = largura / 2 - (n.x + n.w / 2) * vista.k;
  vista.y = r.height / 2 - (n.y + n.h / 2) * vista.k;
  aplicarCamera();
}
function zoom(fator, cx, cy) {
  const k = Math.min(3, Math.max(.08, vista.k * fator));
  const r = palco().getBoundingClientRect();
  cx = cx ?? r.width / 2; cy = cy ?? r.height / 2;
  vista.x = cx - (cx - vista.x) * (k / vista.k);
  vista.y = cy - (cy - vista.y) * (k / vista.k);
  vista.k = k; aplicarCamera();
}

function minimapa() {
  const svg = $('#minimapa svg');
  svg.textContent = '';
  svg.setAttribute('viewBox', `0 0 ${MUNDO.w} ${MUNDO.h}`);
  for (const c of caixas.values())
    svg.appendChild(el('rect', { x: c.x, y: c.y, width: c.w, height: c.h,
      fill: corTerr(c.id), opacity: .2, rx: 10 }));
  for (const n of nos.values())
    svg.appendChild(el('rect', { x: n.x, y: n.y, width: n.w, height: n.h,
      fill: CORES[n.status], rx: 4 }));
  svg.appendChild(el('rect', { class: 'vp', id: 'vp' }));
  svg.addEventListener('click', ev => {
    const r = svg.getBoundingClientRect(), pr = palco().getBoundingClientRect();
    const wx = (ev.clientX - r.left) / r.width * MUNDO.w;
    const wy = (ev.clientY - r.top) / r.height * MUNDO.h;
    vista.x = pr.width / 2 - wx * vista.k;
    vista.y = pr.height / 2 - wy * vista.k;
    aplicarCamera();
  });
  minimapaVp();
}
function minimapaVp() {
  const vp = document.getElementById('vp'); if (!vp) return;
  const r = palco().getBoundingClientRect();
  vp.setAttribute('x', -vista.x / vista.k);
  vp.setAttribute('y', -vista.y / vista.k);
  vp.setAttribute('width', r.width / vista.k);
  vp.setAttribute('height', r.height / vista.k);
}

/* ══ 7 · LIGAR TUDO ═══════════════════════════════════════════════════════ */
function controlos() {
  const p = palco();
  let arrastando = false, ax = 0, ay = 0;
  p.addEventListener('pointerdown', ev => {
    if (ev.target.closest('.peca')) return;
    arrastando = true; ax = ev.clientX - vista.x; ay = ev.clientY - vista.y;
    p.classList.add('arrastando'); p.setPointerCapture(ev.pointerId);
  });
  p.addEventListener('pointermove', ev => {
    if (!arrastando) return;
    vista.x = ev.clientX - ax; vista.y = ev.clientY - ay; aplicarCamera();
  });
  const solta = () => { arrastando = false; p.classList.remove('arrastando'); };
  p.addEventListener('pointerup', solta);
  p.addEventListener('pointercancel', solta);
  p.addEventListener('click', ev => { if (!ev.target.closest('.peca')) fechar(); });
  p.addEventListener('wheel', ev => {
    ev.preventDefault();
    const r = p.getBoundingClientRect();
    zoom(ev.deltaY < 0 ? 1.13 : 1 / 1.13, ev.clientX - r.left, ev.clientY - r.top);
  }, { passive: false });

  $('#mais').onclick = () => zoom(1.3);
  $('#menos').onclick = () => zoom(1 / 1.3);
  $('#tudo').onclick = () => { fechar(); ajustar(); };
  $('#busca').addEventListener('input', ev => {
    filtro.busca = ev.target.value; filtro.caminho = false; aplicarFiltros(); });
  addEventListener('keydown', ev => {
    if (ev.key === 'Escape') { fechar(); $('#busca').blur(); }
    if (ev.key === '/' && document.activeElement !== $('#busca')) {
      ev.preventDefault(); $('#busca').focus(); }
  });
  addEventListener('resize', minimapaVp);

  const sel = (id, campo, itens, vazio) => {
    const s = $(id);
    s.innerHTML = `<option value="">${vazio}</option>` +
      itens.map(([v, r]) => `<option value="${esc(v)}">${esc(r)}</option>`).join('');
    s.onchange = () => { filtro[campo] = s.value; filtro.caminho = false; aplicarFiltros(); };
  };
  sel('#f-terr', 'terr', S.TERRITORIES.map(t => [t.id, t.name]), 'todos os territorios');
  sel('#f-dept', 'dept', Object.keys(S.DEPARTMENTS)
    .map(d => [d, d.replace(/_/g, ' ')]), 'todos os departamentos');
  sel('#f-kind', 'kind', [...new Set(S.NODES.map(n => n.kind))].sort()
    .map(k => [k, k]), 'todos os tipos');
  // OFICIAL vs LEGADO. Sem este filtro, uma peca legada senta-se ao lado da
  // oficial com a mesma cara — e quem nao conhece o historico do repositorio
  // nao tem como saber qual das duas e o caminho de hoje.
  const sl = $('#f-legado');
  sl.innerHTML = '<option value="">oficial e legado</option>' +
    '<option value="oficial">só o oficial</option>' +
    '<option value="legado">só o legado</option>';
  sl.onchange = () => { filtro.legado = sl.value; filtro.caminho = false; aplicarFiltros(); };

  $('#placar').innerHTML = ['PROVEN', 'PENDING', 'BROKEN', 'UNKNOWN'].map(s => {
    const n = S.NODES.filter(x => x.status === s).length;
    return `<button data-st="${s}" aria-pressed="true" title="${ROTULO[s]}">
      <span class="bola" style="background:${CORES[s]}"></span>${n}</button>`;
  }).join('') + '<span id="conta" style="align-self:center;color:var(--ink-mute)"></span>';
  $('#placar').querySelectorAll('[data-st]').forEach(b => b.onclick = () => {
    const s = b.dataset.st;
    filtro.status.has(s) ? filtro.status.delete(s) : filtro.status.add(s);
    b.setAttribute('aria-pressed', filtro.status.has(s));
    aplicarFiltros();
  });
}

async function arrancar() {
  try {
    S = await (await fetch('state.generated.json', { cache: 'no-store' })).json();
  } catch (e) {
    $('#palco').innerHTML = `<p style="padding:80px 22px">Nao consegui ler
      <code>state.generated.json</code>. Corra
      <code>py system-map/scripts/generate_system_map.py</code>.</p>`;
    return;
  }
  document.getElementById('semjs')?.remove();
  const c = S.COUNTS;
  $('#carimbo').innerHTML =
    `${esc(S.PROVENANCE.REPO)} · ${esc(S.PROVENANCE.BRANCH)}<br>` +
    `${esc(S.PROVENANCE.HEAD.slice(0, 10))} · gerado ${esc(S.PROVENANCE.GENERATED_AT.slice(0, 10))}<br>` +
    `${c.components} pecas · ${c.edges} ligacoes · ${c.files_covered}/${c.files_tracked} ficheiros`;
  dispor(); desenhar(); controlos(); aplicarFiltros(); ajustar();

  const alvo = location.hash.slice(1);
  if (alvo && nos.has(alvo)) abrir(alvo);
}
arrancar();
