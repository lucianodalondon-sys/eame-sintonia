/* SINTONIA · MOBILE_INTERACTION_GATE
   ---------------------------------------------------------------------------
   node audit/mobile.mjs [--widths 360,390,430,768,1440] [--shots dir] [--json out.json]

   O portal foi desenhado num monitor. O leitor que decide comprar abre-o no
   telemovel, entre duas filas de vinha, com uma mao. Os portoes anteriores
   mediam UMA coisa no telemovel — se a pagina rolava de lado — e passavam.
   Rolar de lado nao e o unico modo de um ecra falhar: um titulo espremido a
   8px de largura, um botao de 13px, uma etiqueta a 8px de corpo, tudo isso
   passa por «sem overflow» e nenhum deles se pode ler ou tocar.

       O TELEMOVEL NAO E UM DESKTOP ESTREITO. E OUTRO APARELHO.

   Este portao abre um Chromium real em cinco larguras, percorre as dez
   seccoes em cada uma, e MEDE: o que transborda, o que e pequeno demais para
   ler, o que e pequeno demais para tocar, quantas colunas a grelha sustenta,
   e se o nome do produto — a unica palavra que o comercial procura na ficha —
   cabe na caixa onde vive. Depois, a 390px, FAZ a viagem que o leitor faz:
   abre a barra, muda de seccao, filtra, abre uma oportunidade, executa uma
   chamada a acao e volta ao radar. Oito passos, oito medicoes.

       NAO SE PROCURA UMA STRING NO FONTE. CLICA-SE, E MEDE-SE O QUE MUDOU.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import net from 'node:net';
import {
  serve, open, openCase, caseIds, screenText, clickTitle, clickables,
  overflow, shot, C, line,
} from './lib/drive.mjs';
import { loadData } from './lib/harness.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const WIDTHS = String(arg('widths', '360,390,430,768,1440')).split(',').map(Number).filter(Boolean);
const SHOTS = arg('shots', null);
const JSON_OUT = arg('json', null);
/* Varios portoes correm ao mesmo tempo na mesma maquina e cada um serve a sua
   copia da pasta client. serve() de drive.mjs nao rejeita quando a porta esta
   ocupada — emite 'error' e mata o processo. Procura-se uma porta livre antes
   de pedir, senao um portao reprova por causa do vizinho. */
const PORT0 = Number(arg('port', 8951));
const freePort = (p) => new Promise((res) => {
  const s = net.createServer();
  s.once('error', () => res(false));
  s.once('listening', () => s.close(() => res(true)));
  s.listen(p, '0.0.0.0');
});
let PORT = PORT0;
for (let i = 0; i < 24 && !(await freePort(PORT)); i++) PORT = PORT0 + 1 + i;

/* Os limiares. Nenhum e uma opiniao: 10px e onde o texto deixa de ser lido em
   movimento, 24px e o minimo da WCAG 2.2 (2.5.8 Target Size), 44px e o alvo
   confortavel do iOS HIG — daí a regra ser «24 no lado curto OU 44 num lado»,
   que aceita uma tira larga e baixa e recusa um quadrado de 13px. E 170px e a
   largura abaixo da qual uma ficha deixa de mostrar o nome de um produto e uma
   data: duas colunas dessas nao sao duas colunas, sao uma coluna partida. */
const MIN_FONT = 10;
const TAP_SHORT = 24;
const TAP_LONG = 44;
const CARD_MIN = 170;

/* As dez seccoes pelo title do item de navegacao. O portal e italiano; o
   rotulo e o endereco. */
const SECTIONS = [
  'Radar delle Opportunità', 'Radar Futuro', 'Finestre Colturali', 'Polso di Mercato',
  'Voci dal Campo', 'Concorrenza', 'Intelligence Scientifica', 'Portafoglio',
  'Archivio', 'Fonti',
];

/* ── o que o modelo sabe, para conferir o filtro contra a verdade ─────────── */
const ctx = loadData();
const AM = ctx.ITALY_APP_MODEL;
/* ── CONTRA QUE VERDADE SE MEDE A HONESTIDADE DE UM FILTRO ────────────────
   Este mapa vinha de `AM.collections.opportunities`, que e o pacote ANTERIOR
   a reconciliacao: ali OPP_75C37DED9160 e ACT_NOW, e o motor diz VALIDATE_NOW.
   Um portao que confere o ecra contra a fonte errada aprova o defeito que
   existe para apanhar.

       A HONESTIDADE MEDE-SE CONTRA O QUE O MOTOR DECIDIU, NAO CONTRA
       O QUE O PORTAL COSTUMAVA MOSTRAR.

   A instantanea manda; o modelo fica so como reserva se ela faltar. */
const STATUS = {};
if (ctx.MEETING_INTELLIGENCE && Array.isArray(ctx.MEETING_INTELLIGENCE.CASES)) {
  ctx.MEETING_INTELLIGENCE.CASES.forEach((c) => { STATUS[c.ID] = c.STATUS; });
} else {
  AM.collections.opportunities.records.forEach((o) => { STATUS[o.id] = o.status; });
}

/* ═══════════════════════════════════════════════════════════════════════════
   AS MEDICOES DENTRO DA PAGINA
   Uma so evaluate por ecra: entrar e sair do contexto do browser dez vezes por
   seccao e o que faz um portao demorar cinco minutos e ninguem o correr.
   ═════════════════════════════════════════════════════════════════════════ */
const MEASURE = () => {
  const main = document.querySelector('main.sn-main') || document.querySelector('main') || document.body;
  const vis = (el) => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden'; };
  const ownText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());

  /* A caixa onde o texto REALMENTE vive: um <span> inline nao tem largura
     propria — herda a linha. Sobe-se ate ao primeiro antecessor que nao seja
     inline, porque e esse que o layout dimensiona e esse que corta. */
  const blockOf = (el) => { let n = el; while (n && n !== main) { if (getComputedStyle(n).display !== 'inline') return n; n = n.parentElement; } return main; };

  /* A largura que o texto ocupou de facto, medida no proprio nó de texto.
     getBoundingClientRect de um inline com varias linhas devolve a uniao das
     linhas — e a uniao e exatamente o que queremos comparar com a caixa. */
  const textSpan = (el) => {
    let L = Infinity, R = -Infinity;
    for (const n of ownText(el)) {
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) { if (r.width < 0.5) continue; L = Math.min(L, r.left); R = Math.max(R, r.right); }
    }
    return isFinite(L) ? { L, R, w: R - L } : null;
  };

  /* ── o que passa da borda E fica de fora ────────────────────────────────
     overflow() de drive.mjs marca todo elemento cuja caixa passa da largura
     da viewport. Nem todos fazem a pagina rolar: uma tira com ellipsis tem
     `overflow:hidden` no pai, e o texto que «passa» ja foi cortado antes de
     chegar ao ecra — a primeira versao deste portao reprovava 4 ecras por
     causa disso, e os quatro eram falsos.

         SO CONTA O QUE O LEITOR TEM DE ARRASTAR PARA VER.

     Aqui sobe-se pelos antecessores: se o primeiro que corta (hidden, clip,
     auto ou scroll) cabe na viewport, o transbordo morre nele. */
  const de = document.documentElement;
  const CLIP = ['hidden', 'clip', 'auto', 'scroll'];
  const spill = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (!(r.right > de.clientWidth + 2 && r.width > 4 && r.height > 4)) continue;
    if (!vis(el)) continue;
    let p = el.parentElement, dies = false;
    while (p) {
      const pc = getComputedStyle(p);
      if (CLIP.includes(pc.overflowX) || CLIP.includes(pc.overflow)) {
        dies = p.getBoundingClientRect().right <= de.clientWidth + 2; break;
      }
      p = p.parentElement;
    }
    if (dies) continue;
    spill.push({ tag: el.tagName.toLowerCase(), right: Math.round(r.right), w: Math.round(r.width), text: (el.textContent || '').trim().slice(0, 46) });
  }

  /* ── corpo de letra ──────────────────────────────────────────────────────
     So conta quem tem texto PROPRIO. Um <div> que embrulha trinta filhos
     herda o font-size e contaria trinta vezes o mesmo pecado. */
  const small = [];
  for (const el of main.querySelectorAll('*')) {
    if (!vis(el)) continue;
    const own = ownText(el); if (!own.length) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize) || 0;
    if (fs >= 10) continue;
    const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
    small.push({ size: fs, text: own.map((n) => n.textContent.trim()).join(' ').slice(0, 44) });
  }

  /* ── titulo do ecra ──────────────────────────────────────────────────────
     O primeiro texto da barra superior e o nome do ecra: e por ele que o
     leitor sabe onde esta. A 390px, no primeiro carregamento, a sua caixa
     mede 8px e o texto 85px — le-se «R / D / O», uma letra por linha. */
  let title = null;
  const hdr = document.querySelector('header.sn-topbar');
  if (hdr) {
    const cand = [...hdr.querySelectorAll('*')].filter((el) => vis(el)
      && ownText(el).map((n) => n.textContent.trim()).join('').replace(/[^\p{L}\p{N}]/gu, '').length >= 3);
    const el = cand[0];
    if (el) {
      const box = blockOf(el).getBoundingClientRect();
      const t = textSpan(el);
      const lh = parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.2;
      title = {
        text: ownText(el).map((n) => n.textContent.trim()).join(' ').slice(0, 44),
        boxW: Math.round(box.width), boxH: Math.round(box.height),
        textW: t ? Math.round(t.w) : 0, lines: Math.max(1, Math.round(box.height / lh)),
      };
      title.fits = title.textW <= title.boxW + 4;
    }
  }

  /* ── grelha de fichas ────────────────────────────────────────────────────
     Linha = fichas cujo topo coincide dentro de 8px. Nao se le o CSS da
     grelha: le-se onde as caixas foram parar. */
  const cards = [...document.querySelectorAll('[data-case]')].filter(vis)
    .map((c) => { const r = c.getBoundingClientRect(); return { id: c.getAttribute('data-case'), y: Math.round(r.y + window.scrollY), w: Math.round(r.width) }; });
  const rows = [];
  for (const c of cards) {
    const row = rows.find((r) => Math.abs(r.y - c.y) <= 8);
    if (row) { row.w.push(c.w); } else rows.push({ y: c.y, w: [c.w] });
  }
  const grid = {
    cards: cards.length,
    maxPerRow: rows.reduce((a, r) => Math.max(a, r.w.length), 0),
    /* duas fichas na mesma linha e ambas estreitas demais para caber o que a
       ficha tem de dizer — a grelha nao colapsou quando devia */
    split: rows.filter((r) => r.w.length >= 2 && r.w.every((w) => w < 170)).map((r) => r.w),
  };

  /* ── nome do produto na ficha ───────────────────────────────────────────
     O slot carrega data-product: o nome e um CAMPO, nao uma ocorrencia no
     texto. Mede-se altura, largura, transbordo — e depois um teste de
     acerto, porque uma caixa com 47x16 tapada por outra e invisivel na
     mesma. */
  const products = [];
  for (const el of document.querySelectorAll('[data-product]')) {
    const name = (el.getAttribute('data-product') || '').trim();
    const shown = (el.textContent || '').trim();
    el.scrollIntoView({ block: 'center', inline: 'nearest' });
    const r = el.getBoundingClientRect();
    const box = blockOf(el).getBoundingClientRect();
    const t = textSpan(el);
    const hit = document.elementFromPoint(Math.round(r.x + Math.min(5, r.width / 2)), Math.round(r.y + r.height / 2));
    products.push({
      name, w: Math.round(r.width), h: Math.round(r.height),
      empty: !shown,
      clipped: r.height < 6 || r.width < 6,
      overflows: !!t && t.w > box.width + 2,
      covered: !(hit && (hit === el || el.contains(hit) || hit.contains(el))),
    });
  }
  window.scrollTo(0, 0);
  return { spill, small, title, grid, products };
};

/* ═══════════════════════════════════════════════════════════════════════════
   A VARREDURA POR LARGURA
   ═════════════════════════════════════════════════════════════════════════ */
const server = await serve(PORT);
const perWidth = [];
const allErrors = [];

for (const W of WIDTHS) {
  const { browser, page, errors } = await open({ port: PORT, width: W, height: 900 });
  const rec = {
    width: W, screens: 0,
    overflow: [], clipped: 0, small: new Map(), taps: new Map(), crushedTitles: [], grid: null, products: [],
  };

  for (const sec of SECTIONS) {
    /* A primeira seccao e a que ja esta aberta: clicar nela ANTES de medir
       apagaria justamente o defeito do primeiro carregamento — e o primeiro
       carregamento e o unico ecra que todo o leitor ve. */
    if (sec !== SECTIONS[0]) {
      const went = await clickTitle(page, sec, 520);
      if (!went) { rec.overflow.push({ sec, note: 'nav item not reachable' }); continue; }
    }
    rec.screens++;

    const ov = await overflow(page);
    const m = await page.evaluate(MEASURE);
    /* O sintoma que o leitor sente e a pagina rolar de lado; o defeito que o
       causa e um bloco que passa da borda sem ninguem o cortar. Exige-se os
       dois. Os que passam mas morrem num antecessor ficam contados a parte,
       para o portao dizer o que viu e porque nao o contou. */
    if (ov.scrollWidth > ov.docWidth + 2 || m.spill.length) {
      rec.overflow.push({ sec, scrollWidth: ov.scrollWidth, docWidth: ov.docWidth, spill: m.spill.slice(0, 4) });
    }
    rec.clipped += Math.max(0, ov.offenders.length - m.spill.length);
    for (const s of m.small) rec.small.set(s.size + '|' + s.text, s);
    if (m.title && !m.title.fits) rec.crushedTitles.push({ sec, ...m.title });

    /* Alvos de toque: clickables() ja descarta o filho clicavel dentro do pai
       clicavel — senao uma ficha com seis spans valia seis botoes. */
    for (const c of (await clickables(page))) {
      if (!c.visible) continue;
      const short = Math.min(c.w, c.h), long = Math.max(c.w, c.h);
      if (short >= TAP_SHORT || long >= TAP_LONG) continue;
      const label = (c.title || c.text || c.tag).replace(/\s+/g, ' ').slice(0, 30);
      rec.taps.set(label + '|' + c.w + 'x' + c.h, { sec, label, tag: c.tag, w: c.w, h: c.h, short, pointer: c.pointer, handler: c.hasHandler });
    }

    if (sec === SECTIONS[0]) { rec.grid = m.grid; rec.products = m.products; }
    if (SHOTS) await shot(page, SHOTS, `w${W}-${sec.replace(/\s+/g, '-').toLowerCase()}`);
  }

  rec.small = [...rec.small.values()].sort((a, b) => a.size - b.size);
  rec.taps = [...rec.taps.values()].sort((a, b) => a.short - b.short);
  rec.minFont = rec.small.length ? rec.small[0].size : null;
  rec.badProducts = rec.products.filter((p) => p.empty || p.clipped || p.overflows || p.covered);
  perWidth.push(rec);
  allErrors.push(...errors.map((e) => `${W}px · ${e}`));
  await browser.close();
}

/* ═══════════════════════════════════════════════════════════════════════════
   A VIAGEM A 390px
   Oito passos. Cada um so conta se o ecra MUDOU — e a mudanca e medida no
   conteudo de <main>, nao no innerText do body: a barra lateral repete-se em
   todos os ecras e faz duas telas diferentes parecerem a mesma.
   ═════════════════════════════════════════════════════════════════════════ */
const journey = [];
const step = (id, name, ok, got) => { journey.push({ id, name, ok: !!ok, got }); return ok; };

const J = await open({ port: PORT, width: 390, height: 844 });
const jp = J.page;
const fp = () => jp.evaluate(() => {
  const m = document.querySelector('main.sn-main') || document.body;
  const t = (m.innerText || '').replace(/ /g, ' ');
  const hdr = document.querySelector('header.sn-topbar');
  return {
    chars: t.length,
    cases: document.querySelectorAll('[data-case]').length,
    title: hdr ? (hdr.innerText || '').trim().split('\n')[0].trim() : '',
    head: t.slice(0, 120).replace(/\s+/g, ' '),
  };
});
const changed = (a, b) => a.title !== b.title || a.head !== b.head || Math.abs(a.chars - b.chars) > 40;

if (SHOTS) await shot(jp, SHOTS, 'j0-390-load');

/* 1 · a barra de navegacao a 390 vira uma tira horizontal. Nao basta que ela
      exista com overflow-x:auto: tem de ROLAR, e o item que estava fora do
      ecra tem de ficar debaixo do dedo. Prova-se com um teste de acerto no
      centro do item depois de o rolar para dentro — se outra coisa responde
      nesse ponto, o item esta la mas nao e alcancavel. */
{
  const r = await jp.evaluate((label) => {
    const a = document.querySelector('aside'); const el = document.querySelector(`[title="${label}"]`);
    if (!a || !el) return { ok: false, why: 'strip or item missing' };
    const cs = getComputedStyle(a);
    const scrollable = cs.overflowX === 'auto' || cs.overflowX === 'scroll';
    const room = a.scrollWidth - a.clientWidth;
    a.scrollLeft = 0; el.scrollIntoView({ block: 'nearest', inline: 'center' });
    const moved = a.scrollLeft;
    const b = el.getBoundingClientRect(); const ab = a.getBoundingClientRect();
    const hit = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2);
    return {
      scrollable, room, moved, sw: a.scrollWidth, cw: a.clientWidth,
      inStrip: b.x >= ab.x - 1 && b.right <= ab.right + 1 && b.y >= ab.y - 1 && b.bottom <= ab.bottom + 1,
      hitIsItem: !!hit && (hit === el || el.contains(hit) || hit.contains(el)),
    };
  }, 'Fonti');
  step('J1', 'nav strip is reachable and scrolls', r.scrollable && r.room > 8 && r.moved > 0 && r.inStrip && r.hitIsItem,
    `overflowX=${r.scrollable ? 'auto' : 'no'} scrollW=${r.sw} clientW=${r.cw} scrolled=${r.moved}px hit=${r.hitIsItem ? 'the item' : 'something else'}`);
}

/* 2 · mudar de seccao pela tira */
{
  const before = await fp();
  const went = await clickTitle(jp, 'Fonti', 800);
  const after = await fp();
  step('J2', 'a nav click switches the screen', went && changed(before, after) && /FONTI/i.test(after.title),
    `${before.title} (${before.chars} ch) -> ${after.title} (${after.chars} ch)`);
  if (SHOTS) await shot(jp, SHOTS, 'j2-390-section-switched');
}

/* 3 · filtrar. Uma lista que muda nao chega: as fichas que sobram tem de SER
      do estado escolhido. Conferir contra ITALY_APP_MODEL e o que separa um
      filtro de uma animacao. */
{
  await clickTitle(jp, 'Radar delle Opportunità', 700);
  const before = await caseIds(jp);
  /* O radar unico filtra por pastilhas (`data-meeting-filter`), nao por um
     <select>. Procurar o controlo que EXISTE, e nao o que existia. */
  const set = await jp.evaluate(() => {
    const chip = document.querySelector('[data-meeting-filter="ACT_NOW"]');
    if (chip) { chip.click(); return 'ACT_NOW'; }
    const s = [...document.querySelectorAll('select')].find((x) => [...x.options].some((o) => o.value === 'ACT_NOW'));
    if (!s) return null;
    s.value = 'ACT_NOW'; s.dispatchEvent(new Event('change', { bubbles: true })); return s.value;
  });
  await jp.waitForTimeout(700);
  const after = await caseIds(jp);
  const wrong = after.filter((id) => STATUS[id] && STATUS[id] !== 'ACT_NOW');
  step('J3', 'a filter changes the list, and honestly', !!set && after.length > 0 && after.length !== before.length && wrong.length === 0,
    `status=ACT_NOW · ${before.length} -> ${after.length} cards · ${wrong.length} of them not ACT_NOW in the model`);
  if (SHOTS) await shot(jp, SHOTS, 'j3-390-filtered');
  await jp.evaluate(() => {
    const s = [...document.querySelectorAll('select')].find((x) => [...x.options].some((o) => o.value === 'ACT_NOW'));
    if (s) { s.value = ''; s.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await jp.waitForTimeout(600);
}

/* 4 · abrir uma oportunidade tocando na ficha */
let detail = null;
{
  const before = await fp();
  const opened = await openCase(jp, null, 900);
  detail = await fp();
  step('J4', 'tapping a card opens the detail', opened && detail.cases === 0 && detail.chars > 2500 && changed(before, detail),
    `cards ${before.cases} -> ${detail.cases} · detail ${detail.chars} ch · title "${detail.title.slice(0, 46)}"`);
  if (SHOTS) await shot(jp, SHOTS, 'j4-390-detail');
}

/* 5 · o mapa das accoes: a seccao que diz a quem o caso pertence */
{
  const txt = await screenText(jp);
  const areas = ['SVILUPPO DI MERCATO', 'PORTAFOGLIO', 'COMMERCIALE', 'MARKETING', 'NORMATIVO',
    'TECNICO E SCIENTIFICO', 'APPROVVIGIONAMENTO'].filter((a) => txt.includes(a));
  step('J5', 'the action map is on the detail', txt.includes('MAPPA DELLE AZIONI') && areas.length > 0,
    `"MAPPA DELLE AZIONI" ${txt.includes('MAPPA DELLE AZIONI') ? 'present' : 'ABSENT'} · ${areas.length} department(s) named`);
}

/* 6 · executar uma chamada a acao. A de voltar nao conta: voltar e o passo 7.
      Mede-se pelo ecra que ficou, nao pelo clique que foi aceite. */
{
  /* Uma chamada a acao que abre um PDF ou um separador novo nao muda o ecra —
     e nao provaria nada. Tenta-se ate tres, voltando a ficha entre tentativas,
     e conta a primeira que MUDA o que esta na tela. */
  const onDetail = () => jp.evaluate(() => ((document.querySelector('main.sn-main') || document.body).innerText || '').includes('MAPPA DELLE AZIONI'));
  const PICK = (n) => {
    const m = document.querySelector('main.sn-main'); const out = [];
    for (const el of m.querySelectorAll('*')) {
      const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const isClick = cs.cursor === 'pointer' || !!el.onclick || el.tagName === 'BUTTON' || el.tagName === 'A';
      if (!isClick) continue;
      let p = el.parentElement, nested = false;
      while (p && m.contains(p)) { const pc = getComputedStyle(p); if (pc.cursor === 'pointer' || p.tagName === 'A' || p.tagName === 'BUTTON') { nested = true; break; } p = p.parentElement; }
      if (nested) continue;
      const t = (el.textContent || '').trim().replace(/\s+/g, ' ');
      if (!t || t.length > 60 || t.startsWith('←') || !/→/.test(t)) continue;
      out.push({ t, el });
    }
    if (out.length <= n) return null;
    out[n].el.click(); return out[n].t;
  };
  let fired = null, before = null, after = null; const tried = [];
  for (let i = 0; i < 3; i++) {
    if (!(await onDetail())) { await clickTitle(jp, 'Radar delle Opportunità', 700); await openCase(jp, null, 800); }
    before = await fp();
    const t = await jp.evaluate(PICK, i);
    if (!t) break;
    tried.push(t);
    await jp.waitForTimeout(900);
    after = await fp();
    if (changed(before, after)) { fired = t; break; }
  }
  step('J6', 'a CTA on the detail actually fires', !!fired,
    fired ? `"${fired}" · ${before.chars} ch -> ${after.chars} ch · "${after.title.slice(0, 40)}"`
      : (tried.length ? `${tried.length} CTA(s) clicked, none changed the screen: ${tried.join(' | ')}` : 'no forward CTA found on the detail'));
  if (SHOTS) await shot(jp, SHOTS, 'j6-390-after-cta');
}

/* 7 · voltar ao radar */
{
  const went = await clickTitle(jp, 'Radar delle Opportunità', 800);
  const back = await fp();
  step('J7', 'the reader gets back to the radar', went && back.cases > 0 && /RADAR DELLE OPPORTUNIT/i.test(back.title),
    `${back.cases} cards · title "${back.title.slice(0, 40)}"`);
}

/* 8 · e navega outra vez, ja com a tira usada duas vezes */
{
  const before = await fp();
  const went = await clickTitle(jp, 'Portafoglio', 800);
  const after = await fp();
  step('J8', 'navigation still works after the journey', went && changed(before, after) && /PORTAFOGLIO/i.test(after.title),
    `${before.title} -> ${after.title} (${after.chars} ch)`);
  if (SHOTS) await shot(jp, SHOTS, 'j8-390-navigated-again');
}

allErrors.push(...J.errors.map((e) => 'journey · ' + e));
await J.browser.close();
server.close();

/* ═══════════════════════════════════════════════════════════════════════════
   O JUIZO
   ═════════════════════════════════════════════════════════════════════════ */
const per = (fn) => perWidth.map((r) => `${r.width}:${fn(r)}`).join(' ');
const nOverflow = perWidth.reduce((a, r) => a + r.overflow.length, 0);
const nSmall = perWidth.reduce((a, r) => a + r.small.length, 0);
const nTaps = perWidth.reduce((a, r) => a + r.taps.length, 0);
const nSplit = perWidth.reduce((a, r) => a + (r.grid ? r.grid.split.length : 0), 0);
const nProd = perWidth.reduce((a, r) => a + r.badProducts.length, 0);
const nTitle = perWidth.reduce((a, r) => a + r.crushedTitles.length, 0);
const noProducts = perWidth.filter((r) => !r.products.length).length;
const jFail = journey.filter((s) => !s.ok).length;
const screens = perWidth.reduce((a, r) => a + r.screens, 0);

console.log('\n  SINTONIA · MOBILE_INTERACTION_GATE');
console.log(`  ${screens} screens measured across ${WIDTHS.length} widths (${WIDTHS.join(', ')}) + an 8-step journey at 390px`);
console.log('  ' + '─'.repeat(108));
console.log(line(nOverflow === 0, 'MB1', 'No screen spills past the viewport or scrolls sideways', 0, per((r) => r.overflow.length)));
console.log(line(nSmall === 0, 'MB2', `No text under ${MIN_FONT}px in <main> (distinct strings)`, 0, per((r) => r.small.length)));
console.log(line(nTaps === 0, 'MB3', `Every tap target ≥${TAP_SHORT}px short side or ≥${TAP_LONG}px long`, 0, per((r) => r.taps.length)));
console.log(line(nSplit === 0, 'MB4', `Card grid collapses when a row cannot hold ${CARD_MIN}px cards`, 0, per((r) => (r.grid ? r.grid.split.length : '-'))));
console.log(line(nProd === 0 && noProducts === 0, 'MB5', 'Product name on a card is rendered and not clipped', 0, per((r) => (r.products.length ? r.badProducts.length : 'NO SLOTS'))));
console.log(line(nTitle === 0, 'MB6', 'Top-bar screen title fits the box it lives in', 0, per((r) => r.crushedTitles.length)));
console.log(line(jFail === 0, 'MB7', 'The 390px interaction journey completes end to end', 0, `${8 - jFail}/8 steps`));
console.log(line(allErrors.length === 0, 'MB8', 'No console error at any width or during the journey', 0, allErrors.length));
console.log('  ' + '─'.repeat(108));

console.log('\n  VIAGEM A 390px · o que o leitor faz, medido passo a passo');
for (const s of journey) console.log(line(s.ok, s.id, s.name, 'ok', s.got));

console.log('\n  ' + 'WIDTH'.padEnd(8) + 'SCREENS  OVERFLOW  <10px  TAPS<24  TITLE  GRID              PRODUCT SLOTS');
for (const r of perWidth) {
  const m = (n) => (n === 0 ? C.g(String(n).padStart(6)) : C.r(String(n).padStart(6)));
  const g = r.grid ? `${r.grid.cards} cards · ${r.grid.maxPerRow}/row` : 'n.a.';
  const p = r.products.length ? `${r.products.length} slots · ${r.badProducts.length} bad` : C.r('none rendered');
  console.log('  ' + (r.width + 'px').padEnd(8) + String(r.screens).padStart(7)
    + m(r.overflow.length) + '  ' + m(r.small.length) + ' ' + m(r.taps.length) + ' ' + m(r.crushedTitles.length)
    + '  ' + g.padEnd(18) + p);
}

/* ── os piores, com a medida ao lado ──────────────────────────────────────── */
const worstW = perWidth.find((r) => r.taps.length) || perWidth[0];
if (worstW && worstW.taps.length) {
  console.log(`\n  ALVOS DE TOQUE PEQUENOS DEMAIS @${worstW.width}px (piores ${Math.min(8, worstW.taps.length)} de ${worstW.taps.length})`);
  for (const t of worstW.taps.slice(0, 8)) {
    console.log('   ' + C.r(`${t.w}×${t.h}px`).padEnd(22) + t.label.padEnd(32)
      + C.d(`<${t.tag}> ${t.sec} · cursor:${t.pointer ? 'pointer' : 'default'}${t.handler ? ' · own onclick' : ''}`));
  }
}
const smallW = perWidth.find((r) => r.small.length) || perWidth[0];
if (smallW && smallW.small.length) {
  console.log(`\n  TEXTO ABAIXO DE ${MIN_FONT}px @${smallW.width}px (menor = ${smallW.minFont}px · ${smallW.small.length} strings distintas)`);
  for (const s of smallW.small.slice(0, 8)) console.log('   ' + C.r(`${s.size}px`).padEnd(16) + s.text);
}
if (nTitle) {
  console.log('\n  TITULO DO ECRA ESPREMIDO (caixa mais estreita que o proprio texto)');
  for (const r of perWidth) {
    for (const t of r.crushedTitles.slice(0, 3)) {
      console.log('   ' + C.r(`${r.width}px`).padEnd(16) + `"${t.text}" · box ${t.boxW}px, text ${t.textW}px, ${t.lines} lines` + C.d(` · ${t.sec}`));
    }
  }
}
for (const r of perWidth) for (const o of r.overflow.slice(0, 3)) console.log(`\n  SPILL @${r.width}px · ${o.sec} · doc ${o.docWidth}px, scroll ${o.scrollWidth}px · ` + JSON.stringify(o.spill || o.note));
for (const r of perWidth) for (const p of r.badProducts.slice(0, 3)) console.log(`\n  PRODUTO @${r.width}px · ` + JSON.stringify(p));

/* Transparencia sobre o que foi visto e nao contado: se um dia um destes
   deixar de ser cortado, aparece em MB1 e o numero aqui desce. */
const nClipped = perWidth.reduce((a, r) => a + r.clipped, 0);
if (nClipped) console.log(`\n  ${C.d(`nota · ${nClipped} elementos passam da borda mas morrem num antecessor que corta (ellipsis, overflow:hidden): nao rolam a pagina, nao contam`)}`);

console.log(`\n  ECRAS MEDIDOS = ${screens} · LARGURAS = ${WIDTHS.join('/')} · PASSOS DA VIAGEM = ${8 - jFail}/8`);
console.log(`  overflow=${nOverflow} · sub-${MIN_FONT}px=${nSmall} · alvos pequenos=${nTaps} · grelha partida=${nSplit} · produto ilegivel=${nProd} · titulo espremido=${nTitle}`);
if (SHOTS) console.log(`  capturas em ${SHOTS}`);
if (allErrors.length) console.log('  ' + C.r('console: ') + allErrors.slice(0, 4).join(' | '));

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ widths: WIDTHS, perWidth, journey, errors: allErrors }, null, 1));

/* NON-VACUIDADE · um portao que nao mediu nada nao passou: reprova.
   Dez seccoes por largura, doze fichas no radar, oito passos na viagem. */
const vacuous = screens < WIDTHS.length * SECTIONS.length || journey.length !== 8
  || perWidth.some((r) => !r.grid || r.grid.cards < 1);
if (vacuous) console.log('  ' + C.r('VACUO: o portao nao chegou a medir o que diz medir.'));

const FAIL = nOverflow || nSmall || nTaps || nSplit || nProd || noProducts || nTitle || jFail || allErrors.length || vacuous;
console.log('');
process.exit(FAIL ? 1 : 0);
