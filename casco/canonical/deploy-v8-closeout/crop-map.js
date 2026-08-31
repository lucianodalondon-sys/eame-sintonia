/* <crop-map> — geometria real (Natural Earth via world-atlas + d3-geo).
   Nunca pinta footprint de cultura estimado: só fronteiras reais e estado de fundação
   declarado por país. Atributos:
     countries="ESP,ITA,FRA"  highlight="ESP"  variant="country|regional"  height="360"
   Propriedade opcional .states = { ESP: {label, color} } para o estado de fundação. */
(() => {
  const D3 = { src: 'https://unpkg.com/d3@7.9.0/dist/d3.min.js', integrity: 'sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i' };
  const TOPO = { src: 'https://unpkg.com/topojson-client@3.1.0/dist/topojson-client.min.js', integrity: 'sha384-Ukv1p/xTma6P4/2bY5KzWBw+ydSpXmhCMtyciIQVDJ1RmOxtCYNMF1uXT9T63H67' };
  const ATLAS = 'https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json';

  const load = (() => {
    const cache = {};
    return ({ src, integrity }) => cache[src] || (cache[src] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = src; s.integrity = integrity; s.crossOrigin = 'anonymous';
      s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    }));
  })();

  let atlasPromise = null;
  const atlas = () => atlasPromise || (atlasPromise = (async () => {
    await load(D3); await load(TOPO);
    const topo = await fetch(ATLAS).then(r => r.json());
    return window.topojson.feature(topo, topo.objects.countries);
  })());

  // ids numéricos ISO-3166 usados pelo world-atlas
  const ISO = { ESP: '724', ITA: '380', FRA: '250', PRT: '620', AND: '020', CHE: '756', DEU: '276', BEL: '056', GBR: '826', MAR: '504', DZA: '012', TUN: '788', AUT: '040', NLD: '528', LUX: '442', SVN: '705', HRV: '191', GRC: '300' };
  const NAME = { ESP: 'Espanha', ITA: 'Itália', FRA: 'França' };
  // âncoras de rótulo continental (não são dado geográfico do objeto, só posição do texto)
  const ANCHOR = { ESP: [-3.7, 40.2], ITA: [12.6, 42.6], FRA: [2.4, 46.9] };

  class CropMap extends HTMLElement {
    connectedCallback() { this.render(); this._ro = new ResizeObserver(() => this.draw()); this._ro.observe(this); }
    disconnectedCallback() { this._ro && this._ro.disconnect(); }
    static get observedAttributes() { return ['countries', 'highlight', 'variant', 'height', 'states-json', 'statesjson', 'pointsjson']; }
    attributeChangedCallback() { this.draw(); }

    render() {
      this.style.display = 'block';
      this.style.position = 'relative';
      this.innerHTML = '<div data-slot style="width:100%;height:100%"></div>';
      this.draw();
    }

    async draw() {
      const slot = this.querySelector('[data-slot]');
      if (!slot) return;
      const w = this.clientWidth || 640;
      const h = Number(this.getAttribute('height')) || 360;
      const codes = (this.getAttribute('countries') || 'ESP,ITA,FRA').split(',').map(s => s.trim());
      const hi = this.getAttribute('highlight') || '';
      let states = this.states || {};
      const sj = this.getAttribute('states-json') || this.getAttribute('statesjson');
      if (sj) { try { states = JSON.parse(sj); } catch (e) { /* atributo inválido: mantém fallback declarado */ } }
      let fc;
      try { fc = await atlas(); } catch (e) { slot.innerHTML = '<div style="height:100%;display:grid;place-items:center;font:400 11.5px/1.4 var(--font-primary,sans-serif);color:rgba(255,255,255,.42);border:1px dashed rgba(151,139,135,.32);border-radius:14px">Geometria não carregada — nenhuma fronteira desenhada de memória.</div>'; return; }
      const d3 = window.d3;
      const wanted = codes.map(c => ISO[c]).filter(Boolean);
      const focus = fc.features.filter(f => wanted.includes(String(f.id)));
      if (!focus.length) return;

      // projeção determinística sobre a Europa ocidental (lon -11..21, lat 34..53):
      // territórios ultramarinos nunca desenquadram o mapa
      const RAD = Math.PI / 180;
      const merc = phi => Math.log(Math.tan(Math.PI / 4 + phi * RAD / 2));
      const kx = (w - 20) / ((21 + 11) * RAD);
      const ky = (h - 20) / (merc(53) - merc(34));
      const proj = d3.geoMercator().scale(Math.min(kx, ky)).center([5, 44.2]).translate([w / 2, h / 2]);
      const path = d3.geoPath(proj);
      const svg = d3.create('svg').attr('width', w).attr('height', h).attr('viewBox', [0, 0, w, h])
        .style('display', 'block').style('overflow', 'hidden');

      // graticule discreta — grade de inteligência, não decoração
      svg.append('path').attr('d', path(d3.geoGraticule().step([5, 5])()))
        .attr('fill', 'none').attr('stroke', 'rgba(151,139,135,.14)').attr('stroke-width', 0.6);

      // contexto: países vizinhos em tom quase invisível
      svg.append('g').selectAll('path').data(fc.features.filter(f => !wanted.includes(String(f.id))))
        .join('path').attr('d', path).attr('fill', 'rgba(255,255,255,.022)')
        .attr('stroke', 'rgba(151,139,135,.13)').attr('stroke-width', 0.6);

      // países no escopo
      const g = svg.append('g');
      g.selectAll('path').data(focus).join('path')
        .attr('d', path)
        .attr('fill', d => {
          const code = Object.keys(ISO).find(k => ISO[k] === String(d.id));
          const on = hi && code === hi;
          return on ? 'rgba(0,152,69,.20)' : 'rgba(0,152,69,.075)';
        })
        .attr('stroke', d => {
          const code = Object.keys(ISO).find(k => ISO[k] === String(d.id));
          return (hi && code === hi) ? 'rgba(79,209,139,.85)' : 'rgba(0,152,69,.45)';
        })
        .attr('stroke-width', d => {
          const code = Object.keys(ISO).find(k => ISO[k] === String(d.id));
          return (hi && code === hi) ? 1.6 : 1;
        });

      // rótulo + estado da fundação, no centroide
      focus.forEach(d => {
        const code = Object.keys(ISO).find(k => ISO[k] === String(d.id));
        const [x, y] = ANCHOR[code] ? proj(ANCHOR[code]) : path.centroid(d);
        if (!isFinite(x)) return;
        const st = states[code];
        const lab = svg.append('g').attr('transform', `translate(${x},${y})`);
        lab.append('text').attr('text-anchor', 'middle').attr('y', 0)
          .attr('fill', code === hi ? '#ffffff' : 'rgba(255,255,255,.66)')
          .attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 12).attr('font-weight', 600).attr('letter-spacing', '.04em')
          .text(NAME[code] || code);
        lab.append('text').attr('text-anchor', 'middle').attr('y', 15)
          .attr('fill', (st && st.color) || 'rgba(255,255,255,.42)')
          .attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 8.5).attr('font-weight', 600).attr('letter-spacing', '.12em')
          .text((st && st.label) || 'FUNDAÇÃO — NÃO DECLARADA');
        lab.append('text').attr('text-anchor', 'middle').attr('y', 29)
          .attr('fill', 'rgba(255,255,255,.42)')
          .attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 8.5).attr('letter-spacing', '.1em')
          .text('OBJETOS COM LOCAL PROVADO · —');
      });

      // sequência entre mercados — trilho na base, sem inferir causalidade
      if (this.getAttribute('variant') === 'regional') {
        const order = ['ESP', 'ITA', 'FRA'].filter(c => wanted.includes(ISO[c]));
        const y = h - 22;
        const xs = order.map(c => proj(ANCHOR[c])[0]);
        const x0 = Math.min(...xs), x1 = Math.max(...xs);
        svg.append('path').attr('d', `M${x0},${y} L${x1},${y}`)
          .attr('stroke', 'rgba(151,139,135,.45)').attr('stroke-width', 1).attr('stroke-dasharray', '4 5');
        order.forEach((c, n) => {
          const x = xs[n];
          svg.append('circle').attr('cx', x).attr('cy', y).attr('r', 3.5)
            .attr('fill', '#0d1110').attr('stroke', 'rgba(79,209,139,.7)').attr('stroke-width', 1.2);
          svg.append('text').attr('x', x).attr('y', y - 10).attr('text-anchor', 'middle')
            .attr('fill', 'rgba(255,255,255,.66)').attr('font-family', 'var(--font-primary, sans-serif)')
            .attr('font-size', 9).attr('font-weight', 600).attr('letter-spacing', '.1em').text(c.slice(0, 2));
        });
        svg.append('text').attr('x', x1 + 12).attr('y', y + 3)
          .attr('fill', 'rgba(255,255,255,.42)').attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 8).attr('letter-spacing', '.1em').text('SEQUÊNCIA DE JANELAS — NÃO MEDIDA');
      }

      // pontos tipados: só GEO_RESOLUTION = POINT é desenhado.
      // LOCALITY_TEXT nunca é geocodificado silenciosamente; entra na contagem de não-desenháveis.
      let points = [];
      const pj = this.getAttribute('pointsjson');
      if (pj) { try { points = JSON.parse(pj) || []; } catch (e) { points = []; } }
      const drawable = points.filter(p => p.GEO_RESOLUTION === 'POINT' && Array.isArray(p.LOCALITY_OR_GEOMETRY));
      const undrawable = points.length - drawable.length;
      drawable.forEach(p => {
        const xy = proj(p.LOCALITY_OR_GEOMETRY);
        if (!xy || !isFinite(xy[0])) return;
        const g2 = svg.append('g').attr('transform', `translate(${xy[0]},${xy[1]})`);
        g2.append('circle').attr('r', 5).attr('fill', '#0d1110')
          .attr('stroke', p.STATE_COLOR || 'rgba(79,209,139,.9)').attr('stroke-width', 1.6);
        g2.append('text').attr('y', -10).attr('text-anchor', 'middle')
          .attr('fill', 'rgba(255,255,255,.66)').attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 8.5).attr('letter-spacing', '.08em')
          .text([p.OBJECT_TYPE, p.CROP].filter(Boolean).join(' · '));
      });
      if (undrawable > 0) {
        svg.append('text').attr('x', 14).attr('y', 20)
          .attr('fill', 'rgba(255,255,255,.42)').attr('font-family', 'var(--font-primary, sans-serif)')
          .attr('font-size', 8.5).attr('letter-spacing', '.1em')
          .text(undrawable + ' OBJETO(S) SEM GEO_RESOLUTION = POINT · NÃO DESENHADO(S)');
      }

      slot.innerHTML = '';
      slot.appendChild(svg.node());
    }
  }
  if (!customElements.get('crop-map')) customElements.define('crop-map', CropMap);
})();
