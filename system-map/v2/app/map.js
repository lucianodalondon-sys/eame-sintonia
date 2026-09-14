/* SINTONIA SYSTEM MAP V2 — a tela.
   ===========================================================================
   ELA SÓ DESENHA. Não sabe o nome de nenhum departamento, não conhece nenhuma
   peça, não decide nenhum estado e não inventa nenhuma seta. Tudo isso chega
   pronto de `state.v2.generated.json`.

       SE UM FACTO SOBRE A MÁQUINA APARECER NESTE FICHEIRO, É UM DEFEITO.

   Um facto escrito aqui escapa ao validador: ninguém o compara com o
   repositório, e ele envelhece sem dar erro nenhum.

   OS QUATRO NÍVEIS
   ----------------
       0  a máquina      os departamentos, e o sentido do fluxo
       1  o departamento os seus sistemas
       2  o sistema      os seus subsistemas
       3  a engenharia   ficheiros, linhas e provas — só na gaveta, sob pedido

   Uma pessoa não técnica tem de responder às perguntas macro sem chegar ao 3.
   =========================================================================== */
(() => {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const plural = (n, um, muitos) => n + ' ' + (n === 1 ? um : muitos);
  const el = (t, c, txt) => {
    const n = document.createElement(t);
    if (c) n.className = c;
    if (txt != null) n.textContent = txt;
    return n;
  };

  let S = null;                    // o estado gerado
  // O vocabulario visivel vem do estado. Escreve-lo aqui criaria uma segunda
  // lista de nomes, e duas listas divergem na terceira vez que alguem mexe.
  const rot = (v) => (S && S.ROTULOS && S.ROTULOS[v]) || v;
  let rota = { nivel: 0, id: null }; // onde estamos

  // ── carregar ────────────────────────────────────────────────────────────
  fetch('../data/state.v2.generated.json')
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => { S = d; arrancar(); })
    .catch((e) => {
      $('#view').innerHTML =
        '<div class="empty">Não consegui ler o estado gerado (' + e.message + ').<br>' +
        'Corra <code>python3 system-map/v2/scripts/generate_map_v2.py</code> ' +
        'e sirva a pasta por HTTP — <code>fetch</code> não abre <code>file://</code>.</div>';
    });

  function arrancar() {
    const p = S.PROVENANCE, c = S.CONTAS;
    $('#stamp').innerHTML =
      'branch <b>' + p.BRANCH + '</b> · HEAD <b>' + p.HEAD.slice(0, 7) + '</b><br>' +
      'medido em ' + (p.GENERATED_AT || '').slice(0, 10) +
      ' · ' + c.FILES_TRACKED + ' ficheiros no git';
    $('#q').addEventListener('input', procurar);
    $('#dclose').addEventListener('click', fechar);
    $('#scrim').addEventListener('click', fechar);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { if ($('#drawer').classList.contains('on')) fechar(); else subir(); }
    });
    addEventListener('resize', () => cabos(rota));
    addEventListener('hashchange', doHash);
    doHash();
  }

  function doHash() {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!h) { ir(0, null, true); return; }
    const c = S.CONCEITOS[h] || S.DEPARTAMENTOS.find((d) => d.id === h);
    if (!c) { ir(0, null, true); return; }
    ir(S.CONCEITOS[h] ? (S.CONCEITOS[h].nivel === 1 ? 2 : 3) : 1, h, true);
  }

  function ir(nivel, id, semHash) {
    rota = { nivel, id };
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

  // ── migalhas ────────────────────────────────────────────────────────────
  function migalhas(trilho) {
    const n = $('#crumbs'); n.innerHTML = '';
    trilho.forEach((t, i) => {
      if (i) n.appendChild(el('span', 'sep', '›'));
      const b = el('button', 'crumb', t.nome);
      if (i === trilho.length - 1) b.disabled = true;
      else b.onclick = () => ir(t.nivel, t.id);
      n.appendChild(b);
    });
    if (trilho.length > 1) {
      const v = el('button', 'back', '← Voltar');
      v.onclick = subir;
      n.appendChild(v);
    }
  }

  const dep = (id) => S.DEPARTAMENTOS.find((d) => d.id === id);
  const nome = (id) => (S.CONCEITOS[id] || dep(id) || { nome: id }).nome;
  const fam = (id) => {
    const c = S.CONCEITOS[id];
    return (c ? dep(c.departamento) : dep(id) || {}).familia || '';
  };

  // ── cartão ──────────────────────────────────────────────────────────────
  function cartao(o, aoAbrir, extra) {
    const n = el('button', 'node ' + (o.familia || fam(o.id)));
    n.id = 'n-' + o.id;
    n.appendChild(el('div', 'top4'));
    n.appendChild(el('h3', null, o.nome));
    n.appendChild(el('p', 'what', o.frase));
    if (o.problema) {
      const w = el('div', 'warnline');
      w.appendChild(el('b', null, '⚠'));
      w.appendChild(el('span', null, o.problema));
      n.appendChild(w);
    }
    const f = el('div', 'foot');
    const p = el('span', 'pill ' + (o.status || '').replace(/\s+/g, '-'), rot(o.status));
    p.dataset.s = o.status;
    f.appendChild(p);
    if (extra) f.appendChild(el('span', 'more', extra));
    n.appendChild(f);
    n.onclick = aoAbrir;
    return n;
  }

  // ── desenhar o nível ────────────────────────────────────────────────────
  function desenhar() {
    const v = $('#view'); v.innerHTML = '';
    if (rota.nivel === 0) return nivel0(v);
    if (rota.nivel === 1) return nivel1(v, dep(rota.id));
    return nivel2(v, S.CONCEITOS[rota.id]);
  }

  function lede(h, p) {
    const d = el('div', 'lede');
    d.appendChild(el('h1', null, h));
    d.appendChild(el('p', null, p));
    return d;
  }

  function bandas() {
    const b = el('div', 'bands');
    S.FAMILIAS.forEach((f) => b.appendChild(el('span', 'band ' + f.id, f.nome)));
    return b;
  }

  function nivel0(v) {
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }]);
    v.appendChild(lede('A máquina SINTONIA',
      'Cada bloco é um departamento. As linhas mostram por onde o dado passa — e a ' +
      'forma da linha diz o que a sustenta: contínua quando há prova de que já correu, ' +
      'tracejada quando só há código, pontilhada quando só está escrito. Clique num ' +
      'bloco para entrar nele.'));
    v.appendChild(bandas());
    const rail = el('div', 'rail level0');
    S.DEPARTAMENTOS.forEach((d) => {
      const dentro = plural(d.conta_n1, 'sistema', 'sistemas') +
        (d.conta_n2 ? ' · ' + plural(d.conta_n2, 'subsistema', 'subsistemas') : '');
      rail.appendChild(cartao({ ...d, familia: d.familia }, () => ir(1, d.id), dentro));
    });
    v.appendChild(rail);
    v.appendChild(legenda());
    cabos(rota);
  }

  function nivel1(v, d) {
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }, { nivel: 1, id: d.id, nome: d.nome }]);
    v.appendChild(lede(d.nome, d.frase));
    const rail = el('div', 'rail level1');
    d.n1.forEach((id) => {
      const c = S.CONCEITOS[id];
      const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === id);
      const extra = kids.length ? plural(kids.length, 'subsistema', 'subsistemas')
        : (c.engenharia ? plural(c.engenharia, 'peça de engenharia', 'peças de engenharia')
                        : 'sem ficheiros — medido no uso');
      rail.appendChild(cartao(c, () => abrir(id), extra));
    });
    v.appendChild(rail);
    v.appendChild(legenda());
    legado(v, (c) => c.departamento === d.id);
    cabos(rota);
  }

  function nivel2(v, c) {
    const t = [{ nivel: 0, id: null, nome: 'A MÁQUINA' },
               { nivel: 1, id: c.departamento, nome: nome(c.departamento) }];
    if (c.nivel === 2 && c.parent) t.push({ nivel: 2, id: c.parent, nome: nome(c.parent) });
    t.push({ nivel: 2, id: c.id, nome: c.nome });
    migalhas(t);
    const cab = lede(c.nome, c.frase);
    const ver = el('button', 'back', 'Ver o detalhe desta peça →');
    ver.style.marginTop = '12px';
    ver.onclick = () => detalhe(c);
    cab.appendChild(ver);
    v.appendChild(cab);
    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === c.id);
    if (kids.length) {
      const rail = el('div', 'rail level2');
      kids.forEach((k) => rail.appendChild(
        cartao(k, () => abrir(k.id),
          k.engenharia ? plural(k.engenharia, 'peça de engenharia', 'peças de engenharia') : '')));
      v.appendChild(rail);
    } else {
      v.appendChild(el('div', 'empty',
        'Esta peça não tem subsistemas. O detalhe — e a engenharia — abre ao lado.'));
    }
    v.appendChild(legenda());
    if (!kids.length) detalhe(c);
    cabos(rota);
  }

  function legado(v, filtro) {
    const ls = Object.values(S.CONCEITOS).filter((c) => c.legacy && filtro(c));
    if (!ls.length) return;
    const d = el('details', 'legacy');
    d.appendChild(el('summary', null,
      'LEGADO · ' + plural(ls.length, 'peça', 'peças') +
      ' fora do fluxo de hoje — histórico, não corrente'));
    const rail = el('div', 'rail level1');
    ls.forEach((c) => rail.appendChild(cartao(c, () => abrir(c.id), 'fora do fluxo')));
    d.appendChild(rail);
    v.appendChild(d);
  }

  // ── as linhas, desenhadas sobre o que o browser mediu ────────────────────
  function cabos(r) {
    const svg = $('#wires');
    svg.innerHTML = '';
    const vis = r.nivel === 0 ? 0 : (r.nivel === 1 ? 1 : 2);
    const dentro = (id) => document.getElementById('n-' + id);
    const ligs = S.LIGACOES.filter((l) => dentro(l.de) && dentro(l.para));
    if (!ligs.length) return;
    const base = $('#stage').getBoundingClientRect();
    const marca = {};
    ligs.forEach((l, i) => {
      const A = dentro(l.de).getBoundingClientRect();
      const B = dentro(l.para).getBoundingClientRect();
      const mesmaLinha = Math.abs(A.top - B.top) < 24;
      let x1, y1, x2, y2, d0 = null;
      if (l.retorno) {
        // O caminho de volta nunca se mistura com o de ida: desce por baixo do
        // trilho, corre, e sobe. Sobreposta a ida, ela seria lida como parte
        // dela — e um fluxo de retorno lido como ida é uma seta a mentir.
        x1 = A.left + A.width / 2 - base.left; y1 = A.bottom - base.top;
        x2 = B.left + B.width / 2 - base.left; y2 = B.bottom - base.top;
        const fundo = Math.max(y1, y2) + 46;
        d0 = `M ${x1} ${y1} C ${x1} ${fundo}, ${x2} ${fundo}, ${x2} ${y2}`;
      }
      if (mesmaLinha && B.left > A.left) {
        x1 = A.right - base.left; y1 = A.top + A.height / 2 - base.top;
        x2 = B.left - base.left;  y2 = B.top + B.height / 2 - base.top;
      } else {
        x1 = A.left + A.width / 2 - base.left; y1 = A.bottom - base.top;
        x2 = B.left + B.width / 2 - base.left; y2 = B.top - base.top;
      }
      const dx = Math.max(28, Math.abs(x2 - x1) * 0.45);
      const dy = Math.max(26, Math.abs(y2 - y1) * 0.5);
      const d = d0 || (mesmaLinha
        ? `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`
        : `M ${x1} ${y1} C ${x1} ${y1 + dy}, ${x2} ${y2 - dy}, ${x2} ${y2}`);
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
      p.setAttribute('marker-end', 'url(#' + id + ')');
      svg.appendChild(p);
      const hit = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      hit.setAttribute('d', d); hit.setAttribute('class', 'wirehit');
      hit.style.pointerEvents = 'stroke';
      hit.addEventListener('click', () => detalheLigacao(l));
      svg.appendChild(hit);
      marca[l.de] = 1;
    });
    const box = $('#stage').getBoundingClientRect();
    svg.setAttribute('width', box.width); svg.setAttribute('height', box.height);
    void vis;
  }

  const cor = (s) => ({ OBSERVED: '#198754', IMPLEMENTED: '#00783f',
                        DECLARED: '#d99a00', UNKNOWN: '#7f8b87' }[s] || '#7f8b87');

  function legenda() {
    const g = el('div', 'legend');
    g.appendChild(el('b', null, 'A LINHA É A PROVA:'));
    [['OBSERVED', 'já correu — há artefato que o prova'],
     ['IMPLEMENTED', 'há código que o faz, e ninguém provou que correu'],
     ['DECLARED', 'está escrito numa autoridade, e não há código'],
     ['UNKNOWN', 'nada o prova — NÃO SEI']].forEach(([k, txt]) => {
      const d = el('div', 'k');
      d.innerHTML = '<svg width="46" height="10"><line x1="1" y1="5" x2="45" y2="5" ' +
        'class="wire ' + k + '" style="stroke:' + cor(k) + '"/></svg>';
      d.appendChild(el('span', null, txt));
      g.appendChild(d);
    });
    return g;
  }

  // ── a gaveta ────────────────────────────────────────────────────────────
  function abrir(id) {
    const c = S.CONCEITOS[id];
    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === id);
    if (kids.length) { ir(2, id); return; }
    detalhe(c);
  }

  function bloco(h, p) {
    const d = el('div', 'qa');
    d.appendChild(el('h4', null, h));
    d.appendChild(el('p', null, p));
    return d;
  }

  function detalhe(c) {
    const h = $('#dhead'); h.innerHTML = '';
    const p = el('span', 'pill ' + (c.status || '').replace(/\s+/g, '-'), rot(c.status));
    p.dataset.s = c.status;
    h.appendChild(p);
    h.appendChild(el('h2', null, c.nome));
    h.appendChild(el('div', 'src', nome(c.departamento) + (c.parent ? ' › ' + nome(c.parent) : '')));

    const b = $('#dbody'); b.innerHTML = '';
    b.appendChild(bloco('O que é', c.frase));
    b.appendChild(bloco('Por que existe', c.porque));

    const dims = el('div', 'dims');
    [['Canónico', c.canonico, c.canonico_motivo],
     ['Implementado', c.implementado, c.implementado_motivo],
     ['Observado', c.observado, c.observado_motivo],
     ['Saúde', c.status, c.status_motivo]].forEach(([n, v, r]) => {
      const d = el('div', 'dim');
      d.appendChild(el('div', 'n', n));
      const vv = el('div', 'v ' + String(v).replace(/\s+/g, '-'), rot(v));
      vv.dataset.v = v;
      d.appendChild(vv);
      d.appendChild(el('div', 'r', r));
      dims.appendChild(d);
    });
    b.appendChild(dims);

    if (c.problema) {
      const w = el('div', 'warnline');
      w.appendChild(el('b', null, 'PROBLEMA'));
      w.appendChild(el('span', null, c.problema));
      b.appendChild(w);
      b.appendChild(el('div', 'src', ' '));
    }
    (c.impedimentos || []).filter((i) => i.bloqueia).forEach((i) => {
      b.appendChild(bloco('O que a bloqueia',
        i.porque + ' — e ' + i.ausentes.length + ' de ' +
        plural(i.caminhos.length, 'caminho exigido não existe', 'caminhos exigidos não existem') +
        ': ' + i.ausentes.join(', ')));
      b.appendChild(el('div', 'src', 'exigido por ' + i.exigido_por));
    });

    b.appendChild(bloco('O que entra', c.entra));
    if (c.entra_de && c.entra_de.length) b.appendChild(ligacoes('Entra de', c.entra_de));
    b.appendChild(bloco('O que sai', c.sai));
    if (c.sai_para && c.sai_para.length) b.appendChild(ligacoes('Sai para', c.sai_para));
    if (!c.entra_de.length && !c.sai_para.length && c.nivel === 2 && c.parent) {
      // Um subsistema nao tem seta propria: o caminho do dado entra e sai pelo
      // sistema que o contem. Exigir-lhe uma seta inventaria arestas para tapar
      // um buraco que nao existe — e aresta inventada e a pior mentira do mapa.
      b.appendChild(bloco('Como o dado chega aqui',
        'Esta peça é parte de «' + nome(c.parent) + '». O caminho do dado entra e ' +
        'sai por ele — um subsistema não tem seta própria.'));
    } else if (!c.entra_de.length && !c.sai_para.length) {
      b.appendChild(bloco('Sem entrada nem saída — e porquê',
        { SOURCE_BY_DESIGN: 'é uma origem: nada a alimenta, por desenho.',
          SINK_BY_DESIGN: 'é um destino: nada sai dela, por desenho.',
          TERMINAL_BY_DESIGN: 'é um ponto final: mede ou guarda, e o caminho acaba aí.',
          FERRAMENTA_DE_MAO: 'corre à mão, pela linha de comando. Não está no caminho automático.',
          INSTRUMENTO: 'observa a máquina de fora; não faz parte do fluxo do dado.',
          LEGADO: 'ficou para trás.' }[c.papel] || 'NÃO SEI — e isso está por explicar.'));
    }

    b.appendChild(bloco('Quem é o dono', c.dono || 'NÃO SEI'));
    const a = c.autoridade || {};
    b.appendChild(bloco('Qual autoridade define isto',
      a.estado === 'CONFIRMADA'
        ? a.file + ' — e a frase citada foi encontrada lá.'
        : 'NÃO SEI · ' + (a.file || 'nenhuma autoridade apontada')));
    if (a.anchor) b.appendChild(el('div', 'src', '“' + a.anchor + '”'));

    if (c.observacoes && c.observacoes.length) {
      const d = el('div', 'qa');
      d.appendChild(el('h4', null, 'Qual é a prova de que correu'));
      c.observacoes.forEach((o) => {
        const l = el('p', null, (o.existe ? '✓ ' : '✗ ') + o.prova);
        d.appendChild(l);
        d.appendChild(el('div', 'src', o.path + (o.existe
          ? (o.tipo === 'pasta' ? ' · ' + o.itens + ' ficheiros' : ' · ' + o.bytes + ' bytes')
          : ' · não existe')));
      });
      b.appendChild(d);
    }

    const kids = Object.values(S.CONCEITOS).filter((x) => x.parent === c.id);
    if (kids.length) {
      const d = el('div', 'qa');
      d.appendChild(el('h4', null, 'Que componentes internos tem'));
      kids.forEach((k) => {
        const btn = el('button', 'lk');
        btn.innerHTML = '<span class="tag ' +
          (k.status === 'OK' ? 'OBSERVED' : k.status === 'BLOQUEADO' ? 'UNKNOWN' : 'DECLARED') +
          '">' + rot(k.status) + '</span>';
        btn.appendChild(document.createTextNode(k.nome));
        btn.onclick = () => { fechar(); ir(2, k.id); };
        d.appendChild(btn);
      });
      b.appendChild(d);
    }

    if (c.ficheiros_proprios && c.ficheiros_proprios.length) {
      const g = el('details', 'eng');
      g.appendChild(el('summary', null,
        'A ENGENHARIA · ' + plural(c.ficheiros_proprios.length, 'ficheiro', 'ficheiros') +
      ' — abra só se precisar'));
      const f = el('div', 'files');
      c.ficheiros_proprios.forEach((x) => f.appendChild(el('div', null, x)));
      g.appendChild(f);
      b.appendChild(g);
    }
    if (c.caminhos_ausentes && c.caminhos_ausentes.length) {
      b.appendChild(bloco('Caminhos declarados que não existem',
        c.caminhos_ausentes.join(' · ')));
    }
    mostrar();
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

  function detalheLigacao(l) {
    const h = $('#dhead'); h.innerHTML = '';
    const p = el('span', 'pill', rot(l.status)); p.style.background = cor(l.status);
    h.appendChild(p);
    h.appendChild(el('h2', null, nome(l.de) + ' → ' + nome(l.para)));
    const b = $('#dbody'); b.innerHTML = '';
    b.appendChild(bloco('O que esta seta quer dizer', l.significado));
    b.appendChild(bloco('Por que ela tem este estado', l.motivo));
    const d1 = l.prova_declarada, d2 = l.prova_implementada, d3 = l.prova_observada;
    b.appendChild(bloco('Está declarada?', d1.estado === 'CONFIRMADA'
      ? 'Sim — ' + d1.file : 'Não · ' + d1.estado));
    if (d1.anchor) b.appendChild(el('div', 'src', '“' + d1.anchor + '”'));
    b.appendChild(bloco('Está implementada?', d2.estado === 'ENCONTRADA'
      ? 'Sim — há linha de código que a prova.' : 'Não · ' + d2.estado));
    if (d2.estado === 'ENCONTRADA') {
      b.appendChild(el('div', 'src', d2.file + ':' + d2.line));
      b.appendChild(el('div', 'files', d2.snippet));
    }
    b.appendChild(bloco('Já foi observada a correr?', d3 && d3.existe
      ? 'Sim — ' + d3.prova : 'Não — nenhum artefato prova que este caminho carregou alguma coisa.'));
    if (d3 && d3.path) b.appendChild(el('div', 'src', d3.path));
    mostrar();
  }

  const mostrar = () => { $('#drawer').classList.add('on'); $('#scrim').classList.add('on'); };
  const fechar = () => { $('#drawer').classList.remove('on'); $('#scrim').classList.remove('on'); };

  // ── procurar ────────────────────────────────────────────────────────────
  function procurar(e) {
    const t = e.target.value.trim().toLowerCase();
    if (!t) { desenhar(); return; }
    const v = $('#view'); v.innerHTML = ''; $('#wires').innerHTML = '';
    migalhas([{ nivel: 0, id: null, nome: 'A MÁQUINA' }, { nivel: 0, id: null, nome: 'procura' }]);
    const alvo = [];
    S.DEPARTAMENTOS.forEach((d) => alvo.push({ id: d.id, nome: d.nome, frase: d.frase,
      onde: 'departamento', nivel: 1, status: d.status }));
    Object.values(S.CONCEITOS).forEach((c) => alvo.push({ id: c.id, nome: c.nome, frase: c.frase,
      onde: nome(c.departamento) + (c.parent ? ' › ' + nome(c.parent) : ''),
      nivel: 2, status: c.status,
      extra: (c.ficheiros_proprios || []).join(' ') }));
    const hits = alvo.filter((a) =>
      (a.nome + ' ' + a.frase + ' ' + (a.extra || '')).toLowerCase().includes(t)).slice(0, 40);
    if (!hits.length) { v.appendChild(el('div', 'empty', 'Nada encontrado para “' + t + '”.')); return; }
    v.appendChild(lede('Procura', hits.length + ' resultado(s) para “' + t + '”.'));
    hits.forEach((a) => {
      const c = el('div', 'hitcard');
      const p = el('span', 'pill ' + (a.status || '').replace(/\s+/g, '-'), rot(a.status));
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
