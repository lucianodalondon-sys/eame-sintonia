/* SINTONIA SYSTEM MAP V2 — a tela.
   ===========================================================================
   ELA SÓ DESENHA. Não sabe o nome de nenhum departamento, não conhece nenhuma
   peça, não decide nenhum estado e não inventa nenhuma seta. Tudo chega pronto
   de `estado.gerado.json`.

       SE UM FACTO SOBRE A MÁQUINA APARECER NESTE FICHEIRO, É UM DEFEITO.

   Um facto escrito aqui escapa ao validador: ninguém o compara com o
   repositório, e ele envelhece sem dar erro nenhum.

   OS QUATRO NÍVEIS (COL-LAW-109)
   -------------------------------
       0  a máquina       os departamentos, e o sentido do fluxo
       1  o departamento  as suas peças, na ordem do fluxo
       2  o subsistema    o que há dentro de uma peça
       3  a engenharia    ficheiros e provas — na gaveta, sob pedido

   Uma pessoa não técnica responde às perguntas macro sem chegar ao 3.
   =========================================================================== */
(() => {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const plural = (n, um, mts) => n + ' ' + (n === 1 ? um : mts);
  const el = (t, c, txt) => {
    const n = document.createElement(t);
    if (c) n.className = c;
    if (txt != null) n.textContent = txt;
    return n;
  };

  let S = null;
  let rota = { nivel: 0, id: null };
  let foco = null;            // id da peça em foco
  let soProblemas = false;
  let verLegado = false;
  let zoom = 1, panX = 0, panY = 0;

  // O vocabulário visível vem do estado. Escrevê-lo aqui criaria uma segunda
  // lista de nomes, e duas listas divergem na terceira vez que alguém mexe.
  const rot = (v) => (S && S.ROTULOS && S.ROTULOS[v]) || v;

  fetch('estado.gerado.json')
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => { S = d; arrancar(); })
    .catch((e) => {
      $('#view').innerHTML =
        '<div class="empty">Não consegui ler o estado gerado (' + e.message + ').<br>' +
        'Corra <code>python3 system-map/v2/scripts/gerar_mapa.py</code> e sirva por HTTP — ' +
        '<code>fetch</code> não abre <code>file://</code>.</div>';
    });

  function arrancar() {
    const p = S.PROVENANCE, c = S.CONTAS;
    $('#stamp').innerHTML =
      'branch <b>' + p.BRANCH + '</b> · HEAD <b>' + p.HEAD.slice(0, 7) + '</b><br>' +
      'medido em ' + (p.GENERATED_AT || '').slice(0, 10) + ' · ' +
      c.FILES_TRACKED + ' ficheiros · ' + S.BIBLIA.leis_conhecidas + ' leis';
    $('#candidato').innerHTML =
      '<b>ESTA PÁGINA É UM CANDIDATO.</b> O mapa oficial continua a ser servido em ' +
      '<code>/system-map/</code> e não foi substituído. Aqui está a reconstrução, ' +
      'para ser olhada antes de qualquer decisão.';

    $('#q').addEventListener('input', procurar);
    $('#dclose').addEventListener('click', fechar);
    $('#scrim').addEventListener('click', fechar);
    $('#btProblemas').addEventListener('click', () => {
      soProblemas = !soProblemas;
      $('#btProblemas').setAttribute('aria-pressed', String(soProblemas));
      desenhar();
    });
    $('#btLegado').addEventListener('click', () => {
      verLegado = !verLegado;
      $('#btLegado').setAttribute('aria-pressed', String(verLegado));
      desenhar();
    });
    $('#btMais').addEventListener('click', () => aplicaZoom(zoom * 1.2));
    $('#btMenos').addEventListener('click', () => aplicaZoom(zoom / 1.2));
    $('#btReset').addEventListener('click', () => { zoom = 1; panX = panY = 0; transformar(); });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if ($('#drawer').classList.contains('on')) fechar();
        else if (foco) { foco = null; desenhar(); }
        else subir();
      }
    });
    arrastar();
    addEventListener('resize', () => cabos());
    addEventListener('hashchange', doHash);
    doHash();
  }

  // ── zoom e arrastar ─────────────────────────────────────────────────────
  function aplicaZoom(z) { zoom = Math.min(2.5, Math.max(0.4, z)); transformar(); }
  function transformar() {
    $('#mundo').style.transform =
      'translate(' + panX + 'px,' + panY + 'px) scale(' + zoom + ')';
    $('#zoomv').textContent = Math.round(zoom * 100) + '%';
  }
  function arrastar() {
    const st = $('#stage');
    let a = false, x0 = 0, y0 = 0;
    st.addEventListener('pointerdown', (e) => {
      if (e.target.closest('.node,.ctrl,button,input,details,summary')) return;
      a = true; x0 = e.clientX - panX; y0 = e.clientY - panY;
      st.classList.add('grabbing'); st.setPointerCapture(e.pointerId);
    });
    st.addEventListener('pointermove', (e) => {
      if (!a) return;
      panX = e.clientX - x0; panY = e.clientY - y0; transformar();
    });
    const solta = () => { a = false; st.classList.remove('grabbing'); };
    st.addEventListener('pointerup', solta);
    st.addEventListener('pointercancel', solta);
    st.addEventListener('wheel', (e) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault(); aplicaZoom(zoom * (e.deltaY < 0 ? 1.1 : 1 / 1.1));
    }, { passive: false });
  }

  // ── navegação ───────────────────────────────────────────────────────────
  function doHash() {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!h) return ir(0, null, true);
    if (S.CONCEITOS[h]) return ir(2, h, true);
    if (S.DEPARTAMENTOS.some((d) => d.id === h)) return ir(1, h, true);
    ir(0, null, true);
  }
  function ir(nivel, id, semHash) {
    rota = { nivel, id }; foco = null;
    if (!semHash) location.hash = id ? encodeURIComponent(id) : '';
    $('#q').value = '';
    desenhar();
  }
  function subir() {
    if (rota.nivel === 0) return;
    if (rota.nivel === 1) return ir(0, null);
    const c = S.CONCEITOS[rota.id];
    if (!c) return ir(0, null);
    if (c.nivel === 2 && c.parent) return ir(2, c.parent);
    ir(1, c.departamento);
  }

  const dep = (id) => S.DEPARTAMENTOS.find((d) => d.id === id);
  const nome = (id) => (S.CONCEITOS[id] || dep(id) || { nome: id }).nome;
  const fam = (id) => {
    const c = S.CONCEITOS[id];
    return ((c ? dep(c.departamento) : dep(id)) || {}).familia || '';
  };
  const problema = (c) => ['BLOQUEADO', 'ATENCAO', 'NAO_IMPLEMENTADO'].includes(c.status);

  function migalhas(trilho) {
    const n = $('#crumbs');
    [...n.querySelectorAll('.crumb,.sep,.back')].forEach((x) => x.remove());
    const ctrls = n.querySelector('.ctrls');
    trilho.forEach((t, i) => {
      if (i) n.insertBefore(el('span', 'sep', '›'), ctrls);
      const b = el('button', 'crumb', t.nome);
      if (i === trilho.length - 1) b.disabled = true;
      else b.onclick = () => ir(t.nivel, t.id);
      n.insertBefore(b, ctrls);
    });
    if (trilho.length > 1) {
      const v = el('button', 'back', '← Voltar');
      v.onclick = subir;
      n.insertBefore(v, ctrls);
    }
  }

  // ── cartão ──────────────────────────────────────────────────────────────
  function cartao(o, aoAbrir, extra) {
    const n = el('button', 'node ' + (o.familia || fam(o.id)) + (o.legacy ? ' legado' : ''));
    n.id = 'n-' + o.id;
    n.appendChild(el('div', 'top4'));
    n.appendChild(el('h3', null, o.nome));
    n.appendChild(el('p', 'what', o.frase));
    if (o.status_motivo && problema(o)) {
      const w = el('div', 'warnline');
      w.appendChild(el('b', null, '⚠'));
      w.appendChild(el('span', null, o.status_motivo));
      n.appendChild(w);
    }
    const f = el('div', 'foot');
    const p = el('span', 'pill ' + (o.status || ''), rot(o.status));
    p.dataset.s = o.status;
    f.appendChild(p);
    // A origem do que a ferramenta mostra vive na SUPERFICIE do cartao, e nao
    // so na gaveta: a pergunta «isto e dado a serio?» e a primeira que se faz,
    // e obrigar a abrir cada uma das onze para a responder era esconde-la.
    if (o.ferramenta && o.ferramenta.de_onde_vem) {
      const v = o.ferramenta.de_onde_vem;
      const g = el('span', 'vem ' + v.replace(/\s+/g, '-'), v);
      g.title = o.ferramenta.leitura || '';
      f.appendChild(g);
    }
    if (extra) f.appendChild(el('span', 'more', extra));
    n.appendChild(f);
    n.onclick = aoAbrir;
    return n;
  }

  function lede(h, p) {
    const d = el('div', 'lede');
    d.appendChild(el('h1', null, h));
    d.appendChild(el('p', null, p));
    return d;
  }

  // ── desenhar ────────────────────────────────────────────────────────────
  function desenhar() {
    const v = $('#view'); v.innerHTML = '';
    if (rota.nivel === 0) nivel0(v);
    else if (rota.nivel === 1) nivel1(v, dep(rota.id));
    else nivel2(v, S.CONCEITOS[rota.id]);
    aplicarFoco();
  }

  function nivel0(v) {
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }]);
    v.appendChild(lede('A máquina SINTONIA',
      'Cada bloco é um departamento. As linhas mostram por onde o dado passa — e a ' +
      'forma da linha diz o que a sustenta: contínua quando há medição que prova que ' +
      'correu, tracejada quando só há código, pontilhada quando só está escrito. ' +
      'Clique num bloco para entrar.'));
    const b = el('div', 'bands');
    S.FAMILIAS.forEach((f) => b.appendChild(el('span', 'band ' + f.id, f.nome)));
    v.appendChild(b);
    const rail = el('div', 'rail level0');
    S.DEPARTAMENTOS.forEach((d) => {
      if (soProblemas && !['BLOQUEADO', 'ATENCAO', 'NAO_IMPLEMENTADO'].includes(d.status)) return;
      rail.appendChild(cartao({ ...d, familia: d.familia, status_motivo: null },
        () => ir(1, d.id),
        plural(d.conta_n1, 'peça', 'peças') +
        (d.conta_n2 ? ' · ' + plural(d.conta_n2, 'subsistema', 'subsistemas') : '')));
    });
    v.appendChild(rail);
    v.appendChild(legenda());
    cabos();
  }

  function nivel1(v, d) {
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }, { nivel: 1, id: d.id, nome: d.nome }]);
    v.appendChild(lede(d.nome, d.frase));
    const rail = el('div', 'rail level1');
    d.n1.forEach((id) => {
      const c = S.CONCEITOS[id];
      if (soProblemas && !problema(c)) return;
      const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === id);
      rail.appendChild(cartao(c, () => abrir(id),
        kids.length ? plural(kids.length, 'subsistema', 'subsistemas')
          : (c.engenharia ? plural(c.engenharia, 'peça de engenharia', 'peças de engenharia')
            : 'medido no uso')));
    });
    v.appendChild(rail);
    v.appendChild(legenda());
    legado(v, (c) => c.departamento === d.id);
    cabos();
  }

  function nivel2(v, c) {
    const t = [{ nivel: 0, id: null, nome: 'A MÁQUINA' },
               { nivel: 1, id: c.departamento, nome: nome(c.departamento) }];
    if (c.nivel === 2 && c.parent) t.push({ nivel: 2, id: c.parent, nome: nome(c.parent) });
    t.push({ nivel: 2, id: c.id, nome: c.nome });
    migalhas(t);
    const cab = lede(c.nome, c.frase);
    const b = el('button', 'back', 'Ver o detalhe desta peça →');
    b.style.marginTop = '12px';
    b.onclick = () => detalhe(c);
    cab.appendChild(b);
    v.appendChild(cab);
    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === c.id);
    if (kids.length) {
      const rail = el('div', 'rail level2');
      kids.forEach((k) => rail.appendChild(cartao(k, () => abrir(k.id),
        k.engenharia ? plural(k.engenharia, 'peça de engenharia', 'peças de engenharia') : '')));
      v.appendChild(rail);
    } else {
      v.appendChild(el('div', 'empty',
        'Esta peça não tem subsistemas. O detalhe — e a engenharia — abre ao lado.'));
      detalhe(c);
    }
    v.appendChild(legenda());
    cabos();
  }

  function legado(v, filtro) {
    const ls = Object.values(S.CONCEITOS).filter((c) => c.legacy && filtro(c));
    if (!ls.length) return;
    const box = el('div', 'legadobox');
    box.appendChild(el('h4', null,
      'LEGADO · ' + plural(ls.length, 'peça', 'peças') +
      ' fora do fluxo de hoje — histórico, não corrente' +
      (verLegado ? '' : ' · use «Mostrar legado»')));
    if (verLegado) {
      const rail = el('div', 'rail level1');
      ls.forEach((c) => rail.appendChild(cartao(c, () => detalhe(c), 'fora do fluxo')));
      box.appendChild(rail);
    }
    v.appendChild(box);
  }

  // ── as linhas ───────────────────────────────────────────────────────────
  const cor = (s) => ({ OBSERVED: '#198754', IMPLEMENTED: '#00783f',
                        DECLARED: '#d99a00', UNKNOWN: '#7f8b87' }[s] || '#7f8b87');

  function cabos() {
    const svg = $('#wires'); svg.innerHTML = '';
    const dentro = (id) => document.getElementById('n-' + id);
    const ligs = S.LIGACOES.filter((l) => dentro(l.de) && dentro(l.para));
    const base = $('#mundo').getBoundingClientRect();
    ligs.forEach((l, i) => {
      const A = dentro(l.de).getBoundingClientRect();
      const B = dentro(l.para).getBoundingClientRect();
      const z = zoom || 1;
      const rel = (r) => ({ l: (r.left - base.left) / z, r: (r.right - base.left) / z,
                            t: (r.top - base.top) / z, b: (r.bottom - base.top) / z,
                            cx: (r.left + r.width / 2 - base.left) / z,
                            cy: (r.top + r.height / 2 - base.top) / z });
      const a = rel(A), b = rel(B);
      const mesma = Math.abs(A.top - B.top) < 24;
      let d;
      if (l.retorno) {
        const fundo = Math.max(a.b, b.b) + 46;
        d = `M ${a.cx} ${a.b} C ${a.cx} ${fundo}, ${b.cx} ${fundo}, ${b.cx} ${b.b}`;
      } else if (mesma && b.l > a.l) {
        const dx = Math.max(26, (b.l - a.r) * 0.5);
        d = `M ${a.r} ${a.cy} C ${a.r + dx} ${a.cy}, ${b.l - dx} ${b.cy}, ${b.l} ${b.cy}`;
      } else {
        const dy = Math.max(26, Math.abs(b.t - a.b) * 0.5);
        d = `M ${a.cx} ${a.b} C ${a.cx} ${a.b + dy}, ${b.cx} ${b.t - dy}, ${b.cx} ${b.t}`;
      }
      const id = 'ah' + i;
      const mk = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
      mk.setAttribute('id', id); mk.setAttribute('viewBox', '0 0 10 10');
      mk.setAttribute('refX', '9'); mk.setAttribute('refY', '5');
      mk.setAttribute('markerWidth', '6'); mk.setAttribute('markerHeight', '6');
      mk.setAttribute('orient', 'auto-start-reverse');
      const tri = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      tri.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
      tri.setAttribute('fill', cor(l.status));
      mk.appendChild(tri); svg.appendChild(mk);
      const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', d);
      p.setAttribute('class', 'wire ' + l.status + (l.retorno ? ' retorno' : ''));
      p.setAttribute('data-de', l.de); p.setAttribute('data-para', l.para);
      p.setAttribute('marker-end', 'url(#' + id + ')');
      svg.appendChild(p);
      const hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      hit.setAttribute('d', d); hit.setAttribute('class', 'wirehit');
      hit.style.pointerEvents = 'stroke';
      hit.addEventListener('click', () => detalheLigacao(l));
      svg.appendChild(hit);
    });
    const box = $('#view').getBoundingClientRect();
    svg.setAttribute('width', box.width / (zoom || 1));
    svg.setAttribute('height', box.height / (zoom || 1));
    aplicarFoco();
  }

  // ── foco: acima e abaixo ────────────────────────────────────────────────
  function caminho(id) {
    const acima = new Set(), abaixo = new Set();
    const sobe = (x) => S.LIGACOES.filter((l) => l.para === x && !l.retorno)
      .forEach((l) => { if (!acima.has(l.de)) { acima.add(l.de); sobe(l.de); } });
    const desce = (x) => S.LIGACOES.filter((l) => l.de === x && !l.retorno)
      .forEach((l) => { if (!abaixo.has(l.para)) { abaixo.add(l.para); desce(l.para); } });
    sobe(id); desce(id);
    return { acima, abaixo };
  }

  function aplicarFoco() {
    const ns = [...document.querySelectorAll('.node')];
    const ws = [...document.querySelectorAll('.wire')];
    ns.forEach((n) => n.classList.remove('apagado', 'focado', 'acima', 'abaixo'));
    ws.forEach((w) => w.classList.remove('apagado'));
    if (!foco) return;
    const { acima, abaixo } = caminho(foco);
    ns.forEach((n) => {
      const id = n.id.slice(2);
      if (id === foco) n.classList.add('focado');
      else if (acima.has(id)) n.classList.add('acima');
      else if (abaixo.has(id)) n.classList.add('abaixo');
      else n.classList.add('apagado');
    });
    ws.forEach((w) => {
      const de = w.getAttribute('data-de'), para = w.getAttribute('data-para');
      const dentro = (x) => x === foco || acima.has(x) || abaixo.has(x);
      if (!(dentro(de) && dentro(para))) w.classList.add('apagado');
    });
  }

  function legenda() {
    const g = el('div', 'legend');
    g.appendChild(el('b', null, 'A LINHA É A PROVA:'));
    [['OBSERVED', 'uma medição real prova que este caminho carregou'],
     ['IMPLEMENTED', 'há código que o faz, e ninguém provou que correu'],
     ['DECLARED', 'está escrito num contrato, e não há código'],
     ['UNKNOWN', 'nada o prova — NÃO SEI']].forEach(([k, txt]) => {
      const d = el('div', 'k');
      d.innerHTML = '<svg width="46" height="10"><line x1="1" y1="5" x2="45" y2="5" ' +
        'class="wire ' + k + '" style="stroke:' + cor(k) + '"/></svg>';
      d.appendChild(el('span', null, txt));
      g.appendChild(d);
    });
    return g;
  }

  // ── gaveta ──────────────────────────────────────────────────────────────
  function abrir(id) {
    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === id);
    if (kids.length) return ir(2, id);
    foco = id; desenhar(); detalhe(S.CONCEITOS[id]);
  }

  function bloco(h, p) {
    const d = el('div', 'qa');
    d.appendChild(el('h4', null, h));
    d.appendChild(el('p', null, p));
    return d;
  }

  // ── A FERRAMENTA QUE O CLIENTE ABRE ────────────────────────────────────
  // Quatro perguntas, pela ordem em que uma pessoa as faz: de onde vem isto,
  // o que me mostra, onde é que eu o vejo, e como é que sabem. Nada aqui está
  // escrito no ficheiro: tudo chega medido de `casco.generated.json`.
  //
  // Quando a origem não foi medida, a caixa diz NÃO SEI em vez de ficar vazia.
  // Uma caixa vazia lê-se como «não há nada»; NÃO SEI lê-se como «ninguém
  // mediu» — e são coisas diferentes.
  function ferramenta(b, f) {
    const cx = el('div', 'ferr');

    const org = el('div', 'orig ' + (f.de_onde_vem || '').replace(/\s+/g, '-'));
    org.appendChild(el('div', 'n', 'DE ONDE VEM O QUE ELA MOSTRA'));
    org.appendChild(el('div', 'v', f.de_onde_vem || 'NÃO SEI'));
    if (f.leitura) org.appendChild(el('p', null, f.leitura));
    cx.appendChild(org);

    const cam = Object.keys(f.camadas || {});
    const rd = el('div', 'qa');
    rd.appendChild(el('h4', null, 'RECEBE DE'));
    if (cam.length) {
      const w = el('div', 'camadas');
      cam.forEach((k) => {
        const c1 = f.camadas[k];
        const t = el('div', 'camada ' + (c1.tipo || '').replace(/\s+/g, '-'));
        t.appendChild(el('span', 'ct', c1.tipo || 'NÃO SEI'));
        t.appendChild(el('span', 'cn', k));
        t.appendChild(el('span', 'cq', c1.o_que_e || ''));
        if (c1.prova && c1.prova.file) {
          t.title = c1.prova.file + ':' + c1.prova.line;
        }
        w.appendChild(t);
      });
      rd.appendChild(w);
    } else {
      rd.appendChild(el('p', null,
        'NÃO SEI. Nenhuma camada com procedência foi medida nesta tela — ' +
        'e nenhuma seta foi desenhada, porque desenhar uma seria inventá-la.'));
    }
    if (f.recebe) rd.appendChild(el('p', 'longo', f.recebe));
    cx.appendChild(rd);

    if (f.mostra) {
      const d = el('div', 'qa');
      d.appendChild(el('h4', null, 'MOSTRA'));
      d.appendChild(el('p', 'longo', f.mostra));
      cx.appendChild(d);
    }

    const on = el('div', 'qa');
    on.appendChild(el('h4', null, 'APARECE EM'));
    on.appendChild(el('p', null,
      (f.telas && f.telas.length
        ? plural(f.telas.length, 'tela', 'telas') + ' do portal: ' + f.telas.join(', ')
        : 'A vista «' + f.vista + '» do portal') +
      (f.blocos && f.blocos.length ? ' · blocos: ' + f.blocos.join(', ') : '') + '.'));
    if (f.modo) {
      on.appendChild(el('p', null,
        f.modo === 'EXPLORATORIA'
          ? 'É EXPLORATÓRIA: tem mais do que uma tela, dá para entrar e navegar.'
          : 'É ANÁLISE PRONTA: uma só tela, uma leitura fechada.'));
    }
    if (f.prova_das_telas) {
      on.appendChild(el('div', 'src',
        f.prova_das_telas.file + ':' + f.prova_das_telas.line +
        ' — ' + f.prova_das_telas.simbolo));
    }
    cx.appendChild(on);

    const pr = el('div', 'qa');
    pr.appendChild(el('h4', null, 'PROVA'));
    if (f.prova_do_nome && f.prova_do_nome.file) {
      pr.appendChild(el('p', null, 'Encontrada na tela servida, com este nome.'));
      pr.appendChild(el('div', 'src',
        f.prova_do_nome.file + ':' + f.prova_do_nome.line +
        ' — ' + (f.prova_do_nome.snippet || '')));
    }
    (f.contratos || []).forEach((k) =>
      pr.appendChild(el('div', 'src', 'contrato · ' + k)));
    if (!(f.contratos || []).length) {
      pr.appendChild(el('p', null,
        'Sem contrato de bloco escrito. É por isso que a origem está em NÃO SEI.'));
      (f.tecido_comum || []).forEach((k) => pr.appendChild(el('div', 'src',
        'só tecido comum a várias telas, que não fala por esta · ' + k)));
    }
    cx.appendChild(pr);

    const gaps = (f.riscos || []).concat(f.perguntas_abertas || [], f.confissoes || []);
    if (gaps.length) {
      const g = el('div', 'qa gaps');
      g.appendChild(el('h4', null, 'O QUE ESTÁ POR RESOLVER'));
      gaps.slice(0, 6).forEach((x) => g.appendChild(el('p', 'longo', x)));
      cx.appendChild(g);
    }

    b.appendChild(cx);
  }

  function ligacoes(t, arr) {
    const d = el('div', 'qa');
    d.appendChild(el('h4', null, t));
    arr.forEach((l) => {
      const b = el('button', 'lk');
      b.innerHTML = '<span class="tag ' + l.status + '">' + rot(l.status) + '</span>';
      b.appendChild(document.createTextNode(l.nome + ' — ' + l.significado));
      b.onclick = () => { fechar(); const c = S.CONCEITOS[l.id]; ir(c ? 2 : 1, l.id); };
      d.appendChild(b);
    });
    return d;
  }

  function detalhe(c) {
    const h = $('#dhead'); h.innerHTML = '';
    const p = el('span', 'pill ' + c.status, rot(c.status));
    p.dataset.s = c.status;
    h.appendChild(p);
    h.appendChild(el('h2', null, c.nome));
    h.appendChild(el('div', 'src',
      nome(c.departamento) + (c.parent ? ' › ' + nome(c.parent) : '') +
      ' · papel canónico: ' + (c.papel_canonico || 'NÃO SEI')));

    const b = $('#dbody'); b.innerHTML = '';
    b.appendChild(bloco('1 · O que é', c.frase));
    b.appendChild(bloco('2 · Por que existe', c.porque));

    const v = el('div', 'verdades');
    [['A Bíblia exige', c.biblia], ['Está contratado', c.declarado],
     ['Há código', c.codigo], ['Já correu', c.observado]].forEach(([n, val]) => {
      const d = el('div', 'vv');
      d.appendChild(el('div', 'n', n));
      d.appendChild(el('div', 'v ' + val, rot(val)));
      v.appendChild(d);
    });
    b.appendChild(v);

    if (c.leis && c.leis.length) {
      const lw = el('div', 'leis');
      c.leis.forEach((l) => {
        const s = el('span', 'lei ' + (l.italia || ''), l.id + ' · ' + l.nome);
        s.title = 'na Itália: ' + (l.italia || 'NÃO SEI');
        lw.appendChild(s);
      });
      b.appendChild(lw);
    }

    if (c.ferramenta) ferramenta(b, c.ferramenta);

    b.appendChild(bloco('3 · O que recebe', c.entra));
    if (c.entra_de && c.entra_de.length) b.appendChild(ligacoes('4 · De quem recebe', c.entra_de));
    b.appendChild(bloco('5-6 · O que faz, e o que produz', c.sai));
    if (c.sai_para && c.sai_para.length) b.appendChild(ligacoes('7 · Para onde manda', c.sai_para));
    if (!c.entra_de.length && !c.sai_para.length) {
      b.appendChild(bloco('Sem entrada nem saída — e porquê',
        { SOURCE: 'é uma origem: nada a alimenta, por desenho.',
          SINK: 'é um destino: nada sai dela, por desenho.',
          TERMINAL: 'é um ponto final: mede ou guarda, e o caminho acaba aí.',
          INSTRUMENTO: 'observa a máquina de fora; não faz parte do fluxo do dado.',
          LEGADO: 'ficou para trás, e por isso está fora do fluxo.',
          FERRAMENTA_DE_MAO: 'corre à mão; não está no caminho automático.'
        }[c.papel_de_fluxo] ||
        (c.nivel === 2 && c.parent
          ? 'é parte de «' + nome(c.parent) + '» — o caminho do dado entra e sai por ele.'
          : 'NÃO SEI — e isso está por explicar.')));
    }

    b.appendChild(bloco('8-9-10 · Canónico, implementado, observado',
      c.biblia_motivo + ' · ' + c.codigo_motivo + ' · ' + c.observado_motivo));
    b.appendChild(bloco('11-12 · Está bloqueado? Que problema existe?',
      c.status === 'BLOQUEADO'
        ? 'Sim. ' + c.status_motivo + ' — ' + c.observado_motivo
        : (problema(c) ? c.status_motivo : 'Nenhum problema medido.')));
    b.appendChild(bloco('13 · Quem é o dono', c.dono || 'NÃO SEI'));

    const ct = c.contrato || {};
    b.appendChild(bloco('15 · Que autoridade define isto',
      ct.estado === 'CONFIRMADA'
        ? ct.file + ' — e a frase citada foi encontrada lá.'
        : 'NÃO SEI · ' + (ct.file || 'nenhum contrato apontado')));
    if (ct.anchor) b.appendChild(el('div', 'src', '“' + ct.anchor + '”'));

    if (c.medicoes && c.medicoes.length) {
      const d = el('div', 'qa');
      d.appendChild(el('h4', null, '14 · Qual é a prova'));
      c.medicoes.forEach((o) => {
        d.appendChild(el('p', null,
          (o.estado === 'CONFIRMA' ? '✓ ' : '✗ ') + o.prova));
        d.appendChild(el('div', 'src',
          o.artefato + ' :: ' + o.caminho + ' = ' + JSON.stringify(o.valor) +
          ' (esperava ' + JSON.stringify(o.espera) + ')'));
      });
      b.appendChild(d);
    } else {
      b.appendChild(bloco('14 · Qual é a prova',
        'Ninguém apontou uma medição que provasse que isto já correu.'));
    }

    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === c.id);
    if (kids.length) {
      const d = el('div', 'qa');
      d.appendChild(el('h4', null, 'Que componentes internos tem'));
      kids.forEach((k) => {
        const btn = el('button', 'lk');
        btn.innerHTML = '<span class="tag ' +
          (k.status === 'OK' ? 'OBSERVED' : 'DECLARED') + '">' + rot(k.status) + '</span>';
        btn.appendChild(document.createTextNode(k.nome));
        btn.onclick = () => { fechar(); ir(2, k.id); };
        d.appendChild(btn);
      });
      b.appendChild(d);
    }

    if (c.ficheiros_proprios && c.ficheiros_proprios.length) {
      const g = el('details', 'eng');
      g.appendChild(el('summary', null,
        '16 · A ENGENHARIA · ' + plural(c.ficheiros_proprios.length, 'ficheiro', 'ficheiros') +
        ' — abra só se precisar'));
      const f = el('div', 'files');
      c.ficheiros_proprios.forEach((x) => f.appendChild(el('div', null, x)));
      g.appendChild(f);
      b.appendChild(g);
    }
    if (c.caminhos_ausentes && c.caminhos_ausentes.length) {
      b.appendChild(bloco('17 · Que lacunas existem',
        'Caminhos declarados que não existem: ' + c.caminhos_ausentes.join(' · ')));
    }
    mostrar();
  }

  function detalheLigacao(l) {
    const h = $('#dhead'); h.innerHTML = '';
    const p = el('span', 'pill', rot(l.status));
    p.style.background = cor(l.status);
    h.appendChild(p);
    h.appendChild(el('h2', null, nome(l.de) + ' → ' + nome(l.para)));
    h.appendChild(el('div', 'src', 'tipo de ligação: ' + l.tipo));
    const b = $('#dbody'); b.innerHTML = '';
    b.appendChild(bloco('O que esta seta quer dizer', l.significado));
    b.appendChild(bloco('Por que ela tem este estado', l.motivo));
    const d1 = l.prova_declarada, d2 = l.prova_codigo, d3 = l.prova_observada;
    b.appendChild(bloco('Está declarada?', d1.estado === 'CONFIRMADA'
      ? 'Sim — ' + d1.file : 'Não · ' + d1.estado));
    if (d1.anchor) b.appendChild(el('div', 'src', '“' + d1.anchor + '”'));
    b.appendChild(bloco('Há código que a faça?', d2.estado === 'ENCONTRADA'
      ? 'Sim — há linha de código que a prova.' : 'Não · ' + d2.estado));
    if (d2.estado === 'ENCONTRADA') {
      b.appendChild(el('div', 'src', d2.file + ':' + d2.line));
      b.appendChild(el('div', 'files', d2.snippet));
    }
    b.appendChild(bloco('Alguma medição prova que correu?',
      d3 && d3.estado === 'CONFIRMA' ? 'Sim — ' + d3.prova
        : 'Não. ' + (d3 && d3.artefato
          ? 'A medição apontada não confirma.' : 'Nenhuma medição foi apontada.')));
    if (d3 && d3.artefato) {
      b.appendChild(el('div', 'src',
        d3.artefato + ' :: ' + d3.caminho + ' = ' + JSON.stringify(d3.valor) +
        ' (esperava ' + JSON.stringify(d3.espera) + ')'));
    }
    mostrar();
  }

  const mostrar = () => { $('#drawer').classList.add('on'); $('#scrim').classList.add('on'); };
  const fechar = () => { $('#drawer').classList.remove('on'); $('#scrim').classList.remove('on'); };

  // ── procurar ────────────────────────────────────────────────────────────
  function procurar(e) {
    const t = e.target.value.trim().toLowerCase();
    if (!t) return desenhar();
    const v = $('#view'); v.innerHTML = ''; $('#wires').innerHTML = '';
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }, { nivel: 0, id: null, nome: 'procura' }]);
    const alvo = [];
    S.DEPARTAMENTOS.forEach((d) => alvo.push({ id: d.id, nome: d.nome, frase: d.frase,
      onde: 'departamento', nivel: 1, status: d.status, extra: '' }));
    Object.values(S.CONCEITOS).forEach((c) => alvo.push({ id: c.id, nome: c.nome,
      frase: c.frase, onde: nome(c.departamento) + (c.parent ? ' › ' + nome(c.parent) : ''),
      nivel: 2, status: c.status,
      extra: (c.ficheiros_proprios || []).join(' ') + ' ' + (c.papel_canonico || '') }));
    const hits = alvo.filter((a) =>
      (a.nome + ' ' + a.frase + ' ' + a.extra).toLowerCase().includes(t)).slice(0, 40);
    if (!hits.length) return v.appendChild(el('div', 'empty', 'Nada encontrado para “' + t + '”.'));
    v.appendChild(lede('Procura', plural(hits.length, 'resultado', 'resultados') +
      ' para “' + t + '”.'));
    hits.forEach((a) => {
      const c = el('div', 'hitcard');
      const p = el('span', 'pill ' + a.status, rot(a.status));
      p.dataset.s = a.status;
      c.appendChild(p);
      const w = el('div');
      w.appendChild(el('div', null, a.nome));
      w.appendChild(el('div', 'path', a.onde));
      c.appendChild(w);
      c.onclick = () => { $('#q').value = ''; ir(a.nivel, a.id); };
      v.appendChild(c);
    });
  }
})();
