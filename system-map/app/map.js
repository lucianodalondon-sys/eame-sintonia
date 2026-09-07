/* SINTONIA SYSTEM MAP — a tela
   ---------------------------------------------------------------------------
   ESTA TELA NAO SABE NADA.

   O comportamento e o do prototipo aprovado — arrastar, zoom, hover, clique,
   caminho completo, minimapa, inventario. O que mudou foi a origem dos dados:
   antes as pecas e as ligacoes estavam escritas dentro deste ficheiro; agora
   vem todas de `state.generated.json`, que o gerador produz lendo o repositorio.

   E essa a diferenca entre um mapa e o desenho de um mapa. O desenho continua
   bonito no dia seguinte a arquitetura mudar. Este nao consegue: se ninguem
   regerar, o CI reprova o ficheiro velho antes de ele chegar aqui.

   Se encontrares neste ficheiro um `if (id === '...')` com regra de negocio
   dentro, ou o nome de um commit escrito a mao, isso e um bug — e um facto a
   esconder-se no frontend, onde nenhum validador o alcanca.
   --------------------------------------------------------------------------- */
'use strict';

const esc = s => String(s ?? '').replace(/[&<>"']/g, m =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
const $ = id => document.getElementById(id);

const statusLabel = s => ({ green: 'PROVADO OPERACIONAL', yellow: 'ATENCAO / PENDENCIA',
  red: 'QUEBRADO OU AUSENTE', gray: 'NAO SEI' }[s] || s);

/* As visoes da barra lateral. Cada peca carrega as suas em `views`, vindas do
   ficheiro declarado — agrupamento visual e coisa de gente, nao de scanner. */
const VISOES = [
  ['all', '◉', 'Sistema inteiro'], ['official', '→', 'Rota oficial hoje'],
  ['lineage', '⌥', 'Linhagens e donos'], ['acervo', '◫', 'Acervo → pacote'],
  ['generator', '⚙', 'Gerador V2.1'], ['opportunity', '◎', 'Opportunity + relevância'],
  ['portal', '▣', 'Pacote → portal'], ['meeting', '▤', 'Reunião / Comercial'],
  ['science', 'Σ', 'Ciência / Desenv. Mercado'], ['audit', '✓', 'Auditoria / contratos'],
  ['infra', '⌁', 'Coleta / infra'], ['futuro', '◷', 'Projeto futuro / guardado'],
  ['legacy', '○', 'Legado / fora do oficial'],
];

let S, nodes = [], edges = [], nodeById = {}, MUNDO = { w: 1, h: 1 };
let scale = .145, tx = 8, ty = 18, drag = false, lx = 0, ly = 0;
let currentView = 'all', pathSet = null, hoverId = null;
/* As partes ligam-se em conjunto, nao uma de cada vez. Ver COLETA e A ESPERA
   lado a lado e como se percebe o que ja saiu da coleta e ainda nao entrou na
   inteligencia — e essa era exatamente a pergunta que obrigar a escolher uma so
   tornava impossivel de responder. Conjunto vazio = mostra tudo. */
const famsAtivas = new Set();
/* O cartao CLICADO fica preso: o caminho dele nao se desfaz quando o rato sai.
   Seguir uma seta com o olho obriga a mover o rato ao longo dela, e enquanto o
   realce vivia so no hover era exatamente esse movimento que o apagava. Preso,
   da para percorrer o caminho todo com calma. Sai clicando fora, ou no X. */
let presoId = null;

const famNome = id => S.FAMILIES.find(f => f.id === id)?.name || '';

/* As palavras de busca que vivem nos ficheiros desta peca. Ficam guardadas por
   FICHEIRO no estado, e nao por peca, porque quem as escreveu foi o ficheiro —
   atribui-las a peca no gerador seria dar-lhes um dono que o codigo nao tem. */
const termosDe = n => (S.SEARCH_TERMS || []).filter(t => (n.files || []).includes(t.file));

const viewport = $('viewport'), world = $('world'), tooltip = $('tooltip'),
      workspace = $('workspace'), detail = $('detail');

/* ══ 1 · DESENHAR O QUE O FICHEIRO DIZ ════════════════════════════════════ */
function render() {
  world.style.width = MUNDO.w + 'px';
  world.style.height = MUNDO.h + 'px';
  const svg = $('edges');
  svg.setAttribute('viewBox', `0 0 ${MUNDO.w} ${MUNDO.h}`);
  svg.style.width = MUNDO.w + 'px';
  svg.style.height = MUNDO.h + 'px';
  $('miniSvg').setAttribute('viewBox', `0 0 ${MUNDO.w} ${MUNDO.h}`);

  // A FAIXA vem primeiro no DOM porque fica por baixo: ela e o pano de fundo
  // que agrupa, nao mais uma caixa a competir com as zonas.
  $('families').innerHTML = S.FAMILIES.map(f => `
    <section class="family ${f.id}" data-fam="${esc(f.id)}"
             style="left:${f.x}px;top:${f.y}px;width:${f.w}px;height:${f.h}px">
      <div class="familyHead">
        <div class="familyName">${esc(f.name)}</div>
        <div class="familyWhy">${esc(f.why)} · ${f.count} peças</div>
      </div>
    </section>`).join('');

  $('zones').innerHTML = S.TERRITORIES.map(z => `
    <section class="zone ${esc(z.family)}" data-zone="${esc(z.id)}"
             style="left:${z.x}px;top:${z.y}px;width:${z.w}px;height:${z.h}px">
      <div class="zoneHead">
        <div class="zoneFam">${esc(famNome(z.family))}</div>
        <div class="zoneTitle">${esc(z.name)}</div>
        <div class="zoneSub">${esc(z.why)}</div>
      </div>
    </section>`).join('');

  $('nodes').innerHTML = nodes.map(n => `
    <div class="node" id="node-${esc(n.id)}" data-id="${esc(n.id)}"
         style="left:${n.x}px;top:${n.y}px" tabindex="0" role="button"
         aria-label="${esc(n.name)} — ${statusLabel(n.ui_status)}">
      <div class="nodeTop">
        <div class="nodeIcon">${esc(n.icon || '●')}</div>
        <div class="nodeHeadText">
          ${(n.destino || []).length ? `<div class="destinoChips">${
            n.destino.map(d => `<span class="dchip d${d}" title="${
              d === 'GIT' ? 'O que sai daqui vira ficheiro versionado no repositório'
                          : 'O que sai daqui vira linha no banco Supabase'
            }">${d === 'GIT' ? '⎇ git' : '▤ supabase'}</span>`).join('')}</div>` : ''}
          <div class="nodeName">${esc(n.name)}</div>${
          n.nome_em_portugues && n.nome_em_portugues !== n.name
            ? `<div class="nodeAlias">${esc(n.nome_em_portugues)}</div>` : ''}
          <div class="nodeType">${esc(n.kind)}${n.legacy ? ' · legado' : ''}${
            n.pais && n.pais !== 'TRANSVERSAL' ? ' · ' + esc(n.pais) : ''}${
            n.lane === 'futuro' ? ' · projeto futuro' : ''}</div>
        </div>
        <div class="statusPill status-${n.ui_status}">${statusLabel(n.ui_status)}</div>
      </div>
      <div class="nodeSummary">${esc(n.what)}</div>
      <div class="nodeFiles">${esc((n.files.length ? n.files : n.facts || [])
        .slice(0, 2).join(' · ') || 'sem ficheiro')}</div>
    </div>`).join('');

  // A seta sai da direita de quem manda e entra na esquerda de quem recebe — o
  // dado corre da esquerda para a direita, e a curva torna isso visivel mesmo
  // quando as duas pecas estao a cinco zonas de distancia.
  $('edgeLayer').innerHTML = edges.map((e, i) => {
    const a = nodeById[e.from], b = nodeById[e.to];
    if (!a || !b) return '';
    // A seta sai pelo lado que aponta para o destino. Assumir sempre
    // esquerda->direita fazia toda ligacao de volta (o teste que roda o script,
    // o workflow que chama a coleta) dar a volta ao mapa inteiro por fora — e
    // era isso que transformava a leitura num novelo. Aqui a curva vai pelo
    // caminho curto, e a direcao continua legivel pela ponta da seta.
    const atras = b.x < a.x;
    const x1 = atras ? a.x : a.x + 285, y1 = a.y + 66;
    const x2 = atras ? b.x + 285 : b.x, y2 = b.y + 66;
    const dx = Math.max(110, Math.abs(x2 - x1) * .42) * (atras ? -1 : 1);
    const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
    const cls = e.kind === 'expected' ? 'unknown'
      : (a.ui_status === 'red' || b.ui_status === 'red') ? 'broken' : '';
    return `<g class="dyn nat${esc(e.natureza || 'FLUXO')}" data-edge="${i}" data-nat="${
      esc(e.natureza || 'FLUXO')}" data-from="${esc(e.from)}" data-to="${esc(e.to)}">
      <path d="${d}" class="edgePath ${cls}"></path>
      <path d="${d}" class="edgeHit"></path></g>`;
  }).join('');
}

/* ══ 2 · A DICA — o que a peca faz, em portugues comum ════════════════════ */
function showNodeTip(e, n) {
  const de = n.inbound.map(i => nodeById[i]?.name).filter(Boolean);
  const pa = n.outbound.map(i => nodeById[i]?.name).filter(Boolean);
  tooltip.innerHTML =
    `<div class="ttName">${esc(n.name)}</div>
     <div class="ttStatus">${statusLabel(n.ui_status)}${n.legacy ? ' · LEGADO' : ''}</div>
     <div class="ttLabel">O que faz</div><div class="ttText">${esc(n.what)}</div>
     <div class="ttLabel">Por que está aqui</div><div class="ttText">${esc(n.why_here)}</div>
     <div class="ttLabel">Recebe de</div><div class="ttText">${
       de.length ? esc(de.slice(0, 3).join(' · ')) : '— ninguém'}</div>
     ${(() => {
       /* «ENVIA PARA — ninguem» NUM CANAL E UMA MENTIRA POR OMISSAO.
          O canal nao escreve nada, e nunca escreveu: quem escreve e a acao que
          passa por ele. Mas dizer «ninguem» faz o cartao parecer um beco sem
          saida — como se o YouTube engolisse o que capta. Aqui ele responde a
          pergunta que a pessoa esta mesmo a fazer: o que entra por aqui vai
          parar onde? */
       const dest = n.o_que_entra_vai_para || [];
       if (n.kind === 'veiculo') {
         return `<div class="ttLabel">O que entra aqui vai parar em</div>
           <div class="ttText">${dest.length
             ? esc(dest.slice(0, 3).map(d => d.ficheiro).join(' · '))
               + (dest.length > 3 ? ` · e mais ${dest.length - 3}` : '')
             : '— NÃO SEI: nenhuma ação que sai por aqui declara onde guarda'}</div>
           <div class="ttLabel">Quem escreve</div><div class="ttText">${
             dest.length ? esc([...new Set(dest.map(d => nodeById[d.acao]?.name || d.acao))]
               .slice(0, 3).join(' · ')) : '— ninguém'}
             <br><span style="opacity:.7">o canal não guarda nada: só deixa passar</span></div>`
           + ((n.saem_daqui_sem_destino || []).length
             ? `<div class="ttLabel">Saem por aqui e NÃO SEI onde guardam</div>
                <div class="ttText">${esc(n.saem_daqui_sem_destino
                  .map(a => nodeById[a]?.name || a).join(' · '))}</div>` : '');
       }
       return `<div class="ttLabel">Envia para</div><div class="ttText">${
         pa.length ? esc(pa.slice(0, 3).join(' · ')) : '— ninguém'}</div>`;
     })()}
     <div class="ttLabel">Motivo do estado</div><div class="ttText">${esc(n.status_reason)}</div>
     ${n.paises && Object.keys(n.paises).length ? `<div class="ttLabel">Países que toca</div>
       <div class="ttText">${esc(Object.entries(n.paises)
         .map(([k, v]) => `${k} ${v}`).join(' · '))}</div>` : ''}`;
  tooltip.style.display = 'block'; moveTip(e);
}
function showEdgeTip(e, d) {
  const st = d.kind === 'expected' ? 'NÃO SEI — declarada, não provada' : 'LIGAÇÃO PROVADA';
  const p = d.evidence?.[0];
  tooltip.innerHTML =
    `<div class="ttName">${esc(nodeById[d.from]?.name)} → ${esc(nodeById[d.to]?.name)}</div>
     <div class="ttStatus">${st}</div>
     <div class="ttLabel">O que passa aqui</div><div class="ttText">${esc(d.payload || d.type)}</div>
     <div class="ttLabel">Por quê</div><div class="ttText">${esc(d.reason)}</div>
     <div class="ttLabel">Prova</div><div class="ttText">${
       p ? esc(p.file + ':' + p.line) : 'não há linha de código que prove'}</div>`;
  tooltip.style.display = 'block'; moveTip(e);
}
function moveTip(e) {
  let x = e.clientX + 14, y = e.clientY + 14;
  const w = 344, h = tooltip.offsetHeight || 240;
  if (x + w > innerWidth) x = e.clientX - w - 14;
  if (y + h > innerHeight) y = Math.max(8, e.clientY - h - 14);
  tooltip.style.left = x + 'px'; tooltip.style.top = y + 'px';
}

/* ══ O FOCO DO RATO — so as ligacoes DESTE cartao ════════════════════════
   Com 125 setas no ecra, perguntar "onde e que isto se liga?" nao tem resposta:
   as linhas passam por cima umas das outras e o olho nao consegue seguir nenhuma.
   Ao pousar o rato num cartao, tudo o que nao toca nele apaga, e ficam so as
   setas que entram e saem dali — com os vizinhos acesos nas duas pontas.

   E so realce: nao filtra, nao muda contagem, nao altera estado. Tirar o rato
   devolve o mapa exatamente como estava. O que muda o que esta visivel sao os
   filtros e o "mostrar caminho completo"; isto aqui e para o olho. */
function focar(id, forcar) {
  /* com um cartao preso, o rato deixa de mandar — so o clique desfaz */
  if (presoId && !forcar) return;
  if (hoverId === id) return;
  hoverId = id;
  const palco = document.getElementById('world');
  palco.classList.toggle('focando', !!id);
  if (!id) {
    document.querySelectorAll('.node.vizinho, .node.noFoco')
      .forEach(e => e.classList.remove('vizinho', 'noFoco'));
    document.querySelectorAll('#edgeLayer .dyn.acesa')
      .forEach(g => g.classList.remove('acesa'));
    return;
  }
  const vizinhos = new Set([id]);
  document.querySelectorAll('#edgeLayer .dyn').forEach(g => {
    const toca = g.dataset.from === id || g.dataset.to === id;
    g.classList.toggle('acesa', toca);
    if (toca) vizinhos.add(g.dataset.from === id ? g.dataset.to : g.dataset.from);
  });
  document.querySelectorAll('.node').forEach(e => {
    e.classList.toggle('noFoco', e.dataset.id === id);
    e.classList.toggle('vizinho', e.dataset.id !== id && vizinhos.has(e.dataset.id));
  });
}

const hideTip = () => { tooltip.style.display = 'none'; };


/* ══ AS FONTES — o acervo inteiro dentro de um cartao ═════════════════════
   Vinte e tres cartoes lado a lado nao respondem "de onde vem o dado?": empurram
   a pergunta para depois de o leitor decorar vinte e tres nomes. Aqui a lista
   mora dentro da peca, agrupada como esta casa ja a organiza — bases oficiais de
   um lado, contas de rede social do outro, cada uma com o seu estado.

   Nada disto e escrito aqui: vem todo de `state.generated.json`. */
const MARCA = { GREEN: '🟢', YELLOW: '🟡', RED: '🔴', 'NAO SEI': '⚪' };

function escadaHTML(k) {
  if (!k?.escada) return '';
  return `<div class="sec">
    <h4>A escada — o que uma fonte tem de subir</h4>
    <p style="font-size:10px;color:#8a827e;margin-bottom:9px">A distância entre os
      degraus é o trabalho que falta fazer. Subir exige gente: nenhum degrau se
      sobe sozinho.</p>
    ${k.escada.map(d => `<div class="file">
      <b>${d.degrau} · ${esc(d.nome)}</b> ${d.quantas === null
        ? '<span style="color:#8a827e">— não medido</span>'
        : `<b style="float:right">${d.quantas}</b>`}<br>
      ${esc(d.o_que_e)}<br>
      <span style="color:#8a827e">mora em <code>${esc(d.onde)}</code></span>${
      d.sobe_como !== '—' ? `<br><span style="color:#8a827e">sobe: ${
        esc(d.sobe_como)}</span>` : ''}</div>`).join('')}
    <div class="evidence" style="margin-top:9px">
      <b>A porta:</b> <code>${esc(k.porta)}</code> — fonte nova entra por aqui,
      na mão ou de dentro de uma coleta que tropeçou nela. O que entra é
      <b>candidata</b>, nunca fonte.<br>
      ${k.candidatas.length
        ? `<b>${k.candidatas.length}</b> candidata(s) esperando alguém abrir.`
        : 'Fila vazia — nenhuma pista esperando verificação.'}
    </div></div>`;
}

function grupoHTML(g) {
  const itens = g.itens || [];
  const abertos = itens.filter(x => x.sabe_coletar).length;
  return `<details class="grupoFonte">
    <summary><b>${esc(g.titulo)}</b> · ${itens.length}
      <span class="grupoSub">${esc(g.subtitulo)}</span></summary>
    <p class="grupoPorque">${esc(g.porque)}</p>
    ${g.onde ? `<p class="grupoOnde">registrado em <code>${esc(g.onde)}</code></p>` : ''}
    ${itens.map(x => `<div class="file">
      ${MARCA[x.estado] || '⚪'} <b>${esc(x.nome)}</b>
      ${x.id ? `<span style="color:#a09995"> · ${esc(x.id)}</span>` : ''}<br>
      <span style="color:#8a827e">${esc(x.assunto)}${
        x.pais ? ' · ' + esc(x.pais) : ''}</span><br>
      ${esc(x.estado_texto)}${
      x.como_se_entra ? `<br><i>como se entra:</i> ${esc(x.como_se_entra)}` : ''}${
      x.atualiza ? `<br><i>atualiza:</i> ${esc(x.atualiza)}` : ''}${
      x.sabe_coletar ? '' :
        '<br><b style="color:#805d00">a máquina não sabe ir lá sozinha</b>'}
    </div>`).join('')}
  </details>`;
}

/* AS COLETAS QUE JA FORAM FEITAS — o que cada corrida trouxe, e o que sobrou.
   `trouxe` e `sobrou` sao os dois numeros que respondem «o que e descartado»: a
   diferenca entre eles nao e desperdicio, e o filtro a trabalhar. Mas so se sabe
   se ele trabalha bem quando os dois ficam guardados lado a lado. */
function corridasHTML(F) {
  if (!F?.corridas?.length) return '';
  return `<div class="sec">
    <h4>As coletas que já foram feitas (${F.total})</h4>
    <p style="font-size:10px;color:#8a827e;margin-bottom:9px">
      <b>${F.fontes_ja_coletadas.length}</b> fontes já foram buscadas;
      <b>${F.fontes_nunca_coletadas.length}</b> nunca. Trouxeram
      <b>${F.trouxe_total}</b> itens e <b>${F.sobrou_total}</b> atravessaram a régua.
      ${F.custo_total_usd ? `Custo medido: <b>US$ ${F.custo_total_usd}</b> em ${
        F.com_custo_medido} das ${F.total}.` : 'O custo só ficou guardado em ' +
        F.com_custo_medido + ' das ' + F.total + '.'}</p>
    ${F.corridas.map(c => `<div class="file">
      <b>${esc(c.fonte || '— fonte sem ficha')}</b> · ${esc(c.plataforma)}
      ${c.estado ? `<span style="float:right">${esc(c.estado)}</span>` : ''}<br>
      trouxe <b>${c.trouxe ?? '?'}</b> · sobrou <b>${c.sobrou ?? '?'}</b>${
        c.rendimento !== null ? ` · rendimento <b>${c.rendimento}%</b>` : ''}${
        c.custou_usd ? ` · US$ ${c.custou_usd}` : ''}<br>
      <span style="color:#8a827e">quem foi buscar: ${esc(c.quem_foi_buscar)}</span>${
      c.que_pergunta ? `<br><span style="color:#8a827e">pergunta: ${
        esc(typeof c.que_pergunta === 'string' ? c.que_pergunta
            : JSON.stringify(c.que_pergunta)).slice(0, 160)}</span>` : ''}${
      c.erro ? `<br><b style="color:#8c2b27">erro: ${esc(c.erro).slice(0, 120)}</b>` : ''}
    </div>`).join('')}</div>`;
}

// O QUE ESTA LIGADO NESTA FERRAMENTA HOJE — camada a camada.
// Quem abre o portal ve numeros. A pergunta que muda a decisao e sempre a mesma:
// de onde veio este numero? REAL veio do motor com procedencia; FIXTURE foi
// escrito a mao para a tela nao ficar vazia. Misturar os dois sem avisar e o
// caso mais caro, porque parece medicao e nao e.
const ORIGEM_TEXTO = {
  'REAL': 'Tudo o que aparece aqui tem procedência.',
  'CANONICO': 'Dado real com a lei da casa aplicada por cima.',
  'MISTURA': 'Dado real misturado com dado escrito à mão. A tela não avisa qual é qual.',
  'SO FIXTURE': 'Tudo escrito à mão. Não há dado real por baixo.',
  'NAO SEI': 'O contrato desta tela não nomeia camada nenhuma.'
};

function blocoCasco(n) {
  const cor = { REAL: '#3f7d4e', CANONICO: '#6a6f9c', FIXTURE: '#b07d2b' };
  return `
    <div class="sec"><h4>De onde vem o que está nesta tela</h4>
      <p style="font-size:11px;color:#4a443f;margin-bottom:10px">
        <b>${esc(n.de_onde_vem || 'NÃO SEI')}</b> — ${
        esc(ORIGEM_TEXTO[n.de_onde_vem] || '')}</p>
    </div>

    <div class="sec"><h4>O que está ligado nela (${(n.ligado_nela || []).length})</h4>
      <p style="font-size:10px;color:#8a827e;margin-bottom:8px">Cada camada de dado que
        esta ferramenta bebe, e o arquivo que a publica.</p>${
      (n.ligado_nela || []).map(c => `
        <div class="file" style="border-left:3px solid ${cor[c.tipo] || '#8a827e'}">
          <b>${esc(c.camada)}</b>
          <span style="color:${cor[c.tipo] || '#8a827e'};font-weight:600">${esc(c.tipo)}</span>
          <div style="font-size:10px;color:#8a827e">${esc(c.o_que_e)}</div>${
          (c.publicada_em || []).map(f =>
            `<div style="font-size:10px;color:#6b635e">publicada em ${esc(f)}</div>`).join('')}${
          c.prova ? `<div style="font-size:10px;color:#6b635e">prova: ${
            esc(c.prova.file)}:${c.prova.line}</div>` : ''}
        </div>`).join('') ||
      '<div class="tags"><span class="tag">NÃO SEI</span></div>'}</div>${

    (n.tecido_comum || []).length ? `<div class="sec">
      <h4>Contratos que a tocam, mas não falam dela (${n.tecido_comum.length})</h4>
      <p style="font-size:10px;color:#8a827e;margin-bottom:8px">Descrevem o que está
        por baixo de várias telas — tabelas de cor, formatação, o relógio. Ficam aqui
        para não sumirem, mas não servem de descrição desta ferramenta.</p>${
      n.tecido_comum.map(f => `<div class="file">${esc(f)}</div>`).join('')}</div>` : ''}${

    (n.riscos || []).length ? `<div class="sec"><h4>Riscos que o contrato já anotou</h4>${
      n.riscos.map(r => `<div class="file">${esc(typeof r === 'string' ? r
        : (r.risk || r.text || JSON.stringify(r)))}</div>`).join('')}</div>` : ''}${

    (n.perguntas_abertas || []).length ? `<div class="sec"><h4>Perguntas ainda em aberto</h4>${
      n.perguntas_abertas.map(q => `<div class="file">${esc(typeof q === 'string' ? q
        : (q.question || q.text || JSON.stringify(q)))}</div>`).join('')}</div>` : ''}`;
}

function blocoFontes(n) {
  const abertas = n.groups[0];
  const redes = n.groups.slice(1);
  return `
    ${n.header_claim?.divergencia ? `<div class="sec">
      <div class="evidence" style="border-color:var(--warn)">
        <b>⚠ O cabeçalho do atlas e as fichas não batem.</b><br>
        ${esc(n.header_claim.leitura)}</div></div>` : ''}

    ${escadaHTML(n.intake)}
    ${corridasHTML(n.runs)}

    <div class="sec"><h4>O acervo, por tipo de fonte</h4>
      <p style="font-size:10px;color:#8a827e;margin-bottom:9px">Clique num grupo
        para abrir a lista. Bases oficiais e contas de rede social são registros
        diferentes no repositório — e continuam a ser.</p>
      ${grupoHTML(abertas)}
      ${redes.map(grupoHTML).join('')}
    </div>`;
}

/* ══ 3 · O PAINEL — o detalhe todo, com a evidencia linha a linha ═════════ */
function openDetail(id) {
  const n = nodeById[id]; if (!n) return;
  workspace.classList.add('detailOpen');
  const entra = edges.filter(e => e.to === id), sai = edges.filter(e => e.from === id);
  const negocio = (S.BUSINESS_EDGES || []).filter(b => b.from === id);

  const lig = (arr, dir) => arr.length ? arr.map(e => {
    const outro = nodeById[dir === 'in' ? e.from : e.to];
    return `<div class="file"><b>${esc(outro?.name || '?')}</b> · ${esc(e.type)}<br>
      ${esc(e.reason)}${e.evidence?.length
        ? '<br>' + e.evidence.slice(0, 3).map(v => esc(v.file + ':' + v.line)).join('<br>')
        : '<br>⚪ NÃO SEI — declarada, não provada'}</div>`;
  }).join('') : '<div class="tags"><span class="tag">nenhuma ligação provada</span></div>';

  detail.innerHTML = `
    <div class="detailHead">
      <button class="close" id="closeDetail" aria-label="fechar">×</button>
      <div class="detailSub">${esc(n.kind)}${n.legacy ? ' · legado' : ''}</div>
      <div class="detailTitle">${esc(n.name)}</div>${
      n.nome_em_portugues && n.nome_em_portugues !== n.name
        ? `<div style="font-size:11px;color:#8a827e;margin:-4px 0 8px">em português:
             <b style="color:#4a443f">${esc(n.nome_em_portugues)}</b> · o nome de cima
             é o que está escrito no portal</div>` : ''}
      <span class="statusPill status-${n.ui_status}">${statusLabel(n.ui_status)}</span>
    </div>
    <div class="detailBody">
      ${n.lane === 'futuro' ? `<div class="sec"><div class="evidence"
        style="border-color:var(--warn)">◷ <b>PROJETO FUTURO.</b> Construído e
        provado, guardado à espera do seu momento. <b>Não é legado</b> — não morreu.
        <b>Não é rota de hoje</b> — não está andando.</div></div>` : ''}
      ${n.legacy ? `<div class="sec"><div class="evidence" style="border-color:var(--unknown)">
        <b>LEGADO.</b> Continua no repositório, e por isso aparece no mapa — mas
        <b>não é a peça oficial de hoje</b>.</div></div>` : ''}

      <div class="sec"><h4>O que faz</h4><p>${esc(n.what)}</p></div>
      <div class="sec"><h4>Por que está aqui</h4><p>${esc(n.why_here)}</p></div>
      <div class="sec"><h4>Motivo do estado</h4>
        <div class="evidence">${esc(n.status_reason)}</div></div>

      ${n.paises && Object.keys(n.paises).length ? `<div class="sec">
        <h4>Países que esta peça toca</h4><div class="tags">${
        Object.entries(n.paises).map(([k, v]) =>
          `<span class="tag">${esc(k)} · ${v}</span>`).join('')}</div>
        <p style="font-size:10px;color:#8a827e;margin-top:6px">Medido pelos arquivos
          que ela toca, seguindo a convenção do atlas (PAÍS-TERRITÓRIO-seq).
          Sem maioria clara, fica transversal.</p></div>` : ''}

      ${n.departments?.length ? `<div class="sec"><h4>Departamentos</h4><div class="tags">${
        n.departments.map(d => `<span class="tag" title="${esc(S.DEPARTMENTS[d] || '')}"
          >${esc(d.replace(/_/g, ' '))}</span>`).join('')}</div></div>` : ''}

      ${negocio.length ? `<div class="sec"><h4>A quem isto serve (declarado)</h4>${
        negocio.map(b => `<div class="file"><b>${
          esc(b.to.replace('DEPT:', '').replace(/_/g, ' '))}</b><br>${esc(b.reason)}<br>
          fonte: ${esc(b.source)} · declarado por ${esc(b.declared_by)} em ${esc(b.declared_at)}
          </div>`).join('')}</div>` : ''}

      <div class="sec"><h4>Recebe de (${entra.length})</h4>${lig(entra, 'in')}</div>
      <div class="sec"><h4>Envia para (${sai.length})</h4>${lig(sai, 'out')}</div>

      ${n.facts?.length ? `<div class="sec"><h4>Medido</h4>${
        n.facts.map(f => `<div class="file">${esc(f)}</div>`).join('')}</div>` : ''}

      ${n.produces?.length ? `<div class="sec">
        <h4>O que esta peça produz (${n.produces.length})</h4>
        <p style="font-size:10px;color:#8a827e;margin-bottom:8px">Artefatos que ela
          escreve. Quem os lê está ligado a ela por causa disto.</p>${
        n.produces.slice(0, 20).map(f => `<div class="file">${esc(f)}</div>`).join('')}${
        n.produces.length > 20 ? `<div class="file">… e mais ${
          n.produces.length - 20}</div>` : ''}</div>` : ''}

      <div class="sec"><h4>Arquivos que implementam isto (${n.files.length})</h4>${
        n.files.map(f => `<div class="file">${esc(f)}</div>`).join('') ||
        '<div class="tags"><span class="tag">nenhum</span></div>'}</div>

      ${n.groups ? blocoFontes(n) : ''}

      ${n.ligado_nela ? blocoCasco(n) : ''}

      ${n.nao_guarda_nada ? `<div class="sec">
        <h4>O que entra por aqui vai parar onde?</h4>
        <p style="font-size:11px;color:#4a443f;margin-bottom:8px">${esc(n.nao_guarda_nada)}</p>${
        ((n.saem_daqui_sem_destino || []).length ? `<div class="file"
          style="border-left:3px solid #8a827e"><b>NÃO SEI onde estas guardam</b>
          <div style="font-size:10px;color:#8a827e">${esc(n.saem_daqui_sem_destino
            .map(a => nodeById[a]?.name || a).join(' · '))} — saem por este canal e
            nenhum ficheiro ou pasta de destino foi medido no código delas.</div>
        </div>` : '') +
        (n.o_que_entra_vai_para || []).map(d => `<div class="file">
          ${esc(d.ficheiro)}
          <div style="font-size:10px;color:#8a827e">quem escreve: ${esc(d.acao)} ·
            prova: ${esc(d.prova.file)}:${d.prova.line}</div>
        </div>`).join('')}</div>` : ''}

      ${n.destino_texto ? `<div class="sec">
        <h4>Onde para o que sai daqui</h4>
        <p style="font-size:11px;color:#4a443f;margin-bottom:8px">${esc(n.destino_texto)}</p>
        <p style="font-size:10px;color:#8a827e;margin-bottom:8px">A diferença importa:
          no <b>git</b> dá para ver quem mudou o quê e voltar atrás; no <b>banco</b> o
          dado é consultável e cresce sem limite, mas o que estava lá ontem não se
          recupera olhando o commit.</p>${
        (n.destino_prova || []).map(d => `<div class="file">
          <b>${esc(d.onde)}</b> · ${esc(d.file)}${d.line > 1 ? ':' + d.line : ''}
          <div style="font-size:10px;color:#8a827e">${esc(d.snippet)}</div>
        </div>`).join('')}</div>` : ''}

      ${n.texto_do_contrato ? `<div class="sec">
        <h4>Palavras do contrato, como estão escritas</h4>
        <p style="font-size:10px;color:#8a827e;margin-bottom:8px">Em inglês, e de
          propósito: é a prova. Traduzir criaria uma segunda versão do contrato, que
          envelhece sozinha. O resumo em português, acima, foi escrito a partir dos
          números medidos — não é tradução deste texto.</p>
        <div class="evidence">${esc(n.texto_do_contrato)}</div></div>` : ''}

      ${n.evidence_text ? `<div class="sec"><h4>Evidência usada pelo mapa</h4>
        <div class="evidence">${esc(n.evidence_text)}</div></div>` : ''}

      ${n.changed_since_declared?.length ? `<div class="sec">
        <h4>Mudou desde a última leitura humana</h4>${
        n.changed_since_declared.map(f => `<div class="file">${esc(f)}</div>`).join('')}</div>` : ''}

      <div class="sec"><h4>Snapshot</h4><p>
        repo <code>${esc(S.PROVENANCE.REPO)}</code><br>
        branch <code>${esc(S.PROVENANCE.BRANCH)}</code><br>
        commit <code>${esc(S.PROVENANCE.HEAD.slice(0, 10))}</code><br>
        gerado <code>${esc(S.PROVENANCE.GENERATED_AT.slice(0, 10))}</code></p></div>

      ${termosDe(n).length ? `<div class="sec">
        <h4>Palavras realmente usadas na busca (${
          termosDe(n).reduce((a, t) => a + t.total_palavras, 0)})</h4>
        <p style="font-size:10px;color:#8a827e;margin-bottom:8px">Na língua do país,
          sempre. Buscar em inglês devolve literatura internacional, não a conversa
          técnica local.</p>${
        termosDe(n).map(t => t.grupos.map(g => `<div class="file">
          <b>${esc(g.grupo)}</b><br>${esc(g.palavras.join(' · '))}${
          g.porque ? `<br><i>${esc(g.porque)}</i>` : ''}</div>`).join('')).join('')}
        </div>` : ''}

      <div class="sec"><h4>Como pedir mudança</h4><p>Esta tela não altera código —
        de propósito. Para mudar isto: altere o repositório, rode
        <code>generate_system_map.py</code> e o mapa acompanha. Nunca o contrário.</p></div>

      <button class="action" id="pathBtn">Mostrar caminho completo desta peça</button>
    </div>`;

  $('closeDetail').onclick = () => {
    workspace.classList.remove('detailOpen');
    detail.innerHTML = '<div class="empty">Clique em uma peça para entender o que faz, '
      + 'por que está ali, arquivos reais e evidência.</div>';
    pathSet = null; presoId = null; focar(null, true); applyFilters();
  };
  $('pathBtn').onclick = () => highlightPath(id);
}

/* O caminho completo: sobe e desce a partir da peca, mas NUNCA atravessa uma
   ligacao NAO SEI. Atravessar seria transformar "talvez" em "portanto" — que e
   exatamente o erro que este mapa existe para nao cometer. */
function highlightPath(id) {
  const frente = new Set([id]), tras = new Set([id]);
  let mudou = true;
  while (mudou) {
    mudou = false;
    edges.forEach(e => {
      if (e.kind === 'expected') return;
      if (frente.has(e.from) && !frente.has(e.to)) { frente.add(e.to); mudou = true; }
      if (tras.has(e.to) && !tras.has(e.from)) { tras.add(e.from); mudou = true; }
    });
  }
  pathSet = new Set([...frente, ...tras]);
  applyFilters();
}

/* ══ 4 · FILTROS ═════════════════════════════════════════════════════════ */
function activeView(n) {
  /* AQUI E A ITALIA. O que e de outro pais nao aparece por omissao.
     Este mapa e do projeto italiano. Uma peca que existe so para outro pais
     nao pertence a vista normal — nao foi apagada, esta guardada, e vive na
     vista «Projeto futuro / guardado», onde continua inteira e provada.
     Hoje isso e UMA peca: o portao do catalogo espanhol.
     Nao confundir com a maquina comum — o motor, o banco, os testes — que
     ja processou dado espanhol e continua a ser da casa toda. */
  if (currentView !== 'futuro' && currentView !== 'legacy'
      && n.pais && n.pais !== 'ITALIA' && n.pais !== 'TRANSVERSAL') return false;
  if (currentView === 'all') return true;
  if (currentView === 'official') return n.lane === 'official';
  // «futuro» e «legado» sao coisas diferentes, e confundi-las custa caro: legado
  // e o que morreu; futuro e o que foi construido, provado, e esta a espera do
  // seu momento. Dizer que o piloto de Espanha e legado seria enterra-lo vivo.
  if (currentView === 'futuro') return n.lane === 'futuro';
  if (currentView === 'legacy') return n.lane === 'legacy'
                                   || (n.lane !== 'official' && n.lane !== 'futuro');
  return (n.views || []).includes(currentView);
}
function applyFilters() {
  const dept = document.querySelector('input[name=dept]:checked')?.value || 'Todos';
  const stats = new Set([...document.querySelectorAll('input[name=status]:checked')]
    .map(x => x.value));
  const pais = document.querySelector('input[name=pais]:checked')?.value || '';
  const q = ($('search').value || '').trim().toLowerCase();
  const vis = new Set();

  nodes.forEach(n => {
    let ok = stats.has(n.ui_status) && activeView(n);
    if (famsAtivas.size) ok = ok && famsAtivas.has(n.family);
    /* ESCOLHER «ITALIA» NAO PODE ESCONDER A MAQUINA QUE A ITALIA USA.
       Antes, escolher ITALIA deixava 25 cartoes de 86 no ecra, e o mapa parecia
       um projeto minusculo. Nao era: as outras 48 pecas sao TRANSVERSAIS — o
       motor, as reguas, o gerador — e a Italia usa-as todos os dias. Esconder
       a maquina de alguem porque ela nao tem bandeira na testa nao e filtrar,
       e mentir por omissao.
       Agora, escolher um pais mostra o que e DESSE pais mais o que serve todos.
       Quem quiser so o tronco comum escolhe TRANSVERSAL, que continua a filtrar
       exatamente por ele. */
    if (pais) ok = ok && (n.pais === pais
                          || (pais !== 'TRANSVERSAL' && n.pais === 'TRANSVERSAL'));
    if (dept !== 'Todos') ok = ok && (n.departments || []).includes(dept);
    const palheiro = [n.name, n.kind, n.what, n.why_here, n.id, ...(n.files || [])]
      .join(' ').toLowerCase();
    const acha = !q || palheiro.includes(q);
    if (pathSet) ok = ok && pathSet.has(n.id);
    if (ok && acha) vis.add(n.id);
    const el = $('node-' + n.id); if (!el) return;
    el.classList.toggle('hidden', !(ok && acha));
    el.classList.toggle('searchHit', !!q && acha && ok);
    el.classList.toggle('highlight', !!(pathSet && pathSet.has(n.id)));
  });

  // A faixa apaga-se quando nenhuma peca dela esta visivel — assim o filtro
  // nao deixa um retangulo colorido vazio a dizer que ali ha alguma coisa.
  document.querySelectorAll('.family').forEach(f => {
    const viva = nodes.some(n => n.family === f.dataset.fam && vis.has(n.id));
    f.classList.toggle('dim', !viva);
  });
  document.querySelectorAll('.zone').forEach(z => {
    const viva = nodes.some(n => n.territory === z.dataset.zone && vis.has(n.id));
    z.style.opacity = viva ? '' : '.25';
  });

  // que naturezas de seta estao ligadas — vazio nao esconde tudo, mostra tudo
  const nats = new Set([...document.querySelectorAll('input[name=nat]:checked')]
    .map(x => x.value));
  document.querySelectorAll('#edgeLayer .dyn').forEach(g => {
    const dentro = vis.has(g.dataset.from) && vis.has(g.dataset.to)
      && (!nats.size || nats.has(g.dataset.nat || 'FLUXO'));
    g.style.display = dentro ? '' : 'none';
    const p = g.querySelector('.edgePath');
    p.classList.toggle('highlight',
      !!(pathSet && pathSet.has(g.dataset.from) && pathSet.has(g.dataset.to)
         && !p.classList.contains('unknown')));
  });

  const ligVis = edges.filter(e => vis.has(e.from) && vis.has(e.to));
  $('kNodes').textContent = vis.size;
  $('kEdges').textContent = ligVis.length;
  $('kProven').textContent = [...vis].filter(i => nodeById[i].ui_status === 'green').length;
  $('kUnknown').textContent = [...vis].filter(i => nodeById[i].ui_status === 'gray').length;
  mini();
}

/* ══ 5 · CAMERA ══════════════════════════════════════════════════════════ */
function transform() {
  scale = Math.max(.03, Math.min(1.5, scale));
  world.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`;
  mini();
}
function fit() {
  const r = viewport.getBoundingClientRect();
  // Se o palco ainda nao tem tamanho, `Math.min` daria escala 0 e o mapa saia
  // invisivel — desenhado, com tudo no DOM, e a zero pixeis. Tenta no frame
  // seguinte em vez de publicar uma tela em branco.
  if (r.width < 2 || r.height < 2) { requestAnimationFrame(fit); return; }
  scale = Math.min((r.width - 40) / MUNDO.w, (r.height - 40) / MUNDO.h);
  tx = (r.width - MUNDO.w * scale) / 2;
  ty = (r.height - MUNDO.h * scale) / 2;
  transform();
}
function mini() {
  const r = viewport.getBoundingClientRect(), v = $('miniView');
  v.setAttribute('x', -tx / scale); v.setAttribute('y', -ty / scale);
  v.setAttribute('width', r.width / scale); v.setAttribute('height', r.height / scale);
}
function renderMini() {
  const cor = { green: 'var(--ok)', yellow: 'var(--warn)',
                red: 'var(--bad)', gray: 'var(--unknown)' };
  $('miniNodes').innerHTML = nodes.map(n =>
    `<rect x="${n.x}" y="${n.y}" width="285" height="132" rx="14"
           fill="${cor[n.ui_status]}"/>`).join('');
}

/* ══ 6 · INVENTARIO — o repositorio inteiro, sem acreditar na palavra do mapa ═ */
function renderInventory(q = '') {
  q = q.toLowerCase();
  $('inventoryBody').innerHTML = Object.entries(S.INVENTORY).map(([grupo, arr]) => {
    const a = arr.filter(x => x.toLowerCase().includes(q));
    if (!a.length) return '';
    return `<section class="invGroup"><h3>${esc(grupo)} · ${a.length}</h3>
      <div class="invGrid">${a.map(x => `<div class="invFile">${esc(x)}</div>`).join('')}
      </div></section>`;
  }).join('') || '<p style="font-size:11px">Nenhum caminho com esse filtro.</p>';
}

/* ══ 7 · LIGAR TUDO ══════════════════════════════════════════════════════ */
function bind() {
  nodes.forEach(n => {
    const el = $('node-' + n.id); if (!el) return;
    el.addEventListener('mouseenter', e => { showNodeTip(e, n); focar(n.id); });
    el.addEventListener('mousemove', moveTip);
    el.addEventListener('mouseleave', () => { hideTip(); focar(null); });
    el.addEventListener('focus', () => focar(n.id));
    el.addEventListener('blur', () => focar(null));
    el.addEventListener('contextmenu', e => {
      if (!presoId) return;
      e.preventDefault(); e.stopPropagation();
      presoId = null; focar(null, true);
    });
    el.addEventListener('click', e => {
      e.stopPropagation();
      presoId = null;              // solta o anterior para poder prender este
      focar(n.id, true);
      presoId = n.id;
      openDetail(n.id);
    });
    el.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        presoId = null; focar(n.id, true); presoId = n.id;
        openDetail(n.id);
      }
    });
  });
  document.querySelectorAll('#edgeLayer .dyn').forEach(g => {
    const e = edges[+g.dataset.edge], hit = g.querySelector('.edgeHit');
    hit.addEventListener('mouseenter', ev => showEdgeTip(ev, e));
    hit.addEventListener('mousemove', moveTip);
    hit.addEventListener('mouseleave', hideTip);
  });

  /* SOLTAR E COM O BOTAO DIREITO, E SO COM ELE.
     Antes, arrastar o mapa soltava o cartao preso — e arrastar o mapa e
     exatamente o que se precisa de fazer para seguir uma seta ate a outra
     ponta. O gesto que serve para acompanhar a ligacao nao pode ser o mesmo
     que apaga a ligacao. Agora: clique esquerdo prende, botao direito solta,
     e arrastar nao mexe em nada. */
  viewport.addEventListener('contextmenu', e => {
    if (!presoId) return;
    e.preventDefault();
    presoId = null;
    focar(null, true);
  });

  viewport.addEventListener('pointerdown', e => {
    if (e.target.closest('.node')) return;
    if (e.button === 2) return;              // o direito e para soltar, nao arrasta
    drag = true; lx = e.clientX; ly = e.clientY;
    viewport.classList.add('dragging'); viewport.setPointerCapture?.(e.pointerId);
  });
  viewport.addEventListener('pointermove', e => {
    if (!drag) return;
    tx += e.clientX - lx; ty += e.clientY - ly; lx = e.clientX; ly = e.clientY; transform();
  });
  const solta = () => { drag = false; viewport.classList.remove('dragging'); };
  viewport.addEventListener('pointerup', solta);
  viewport.addEventListener('pointercancel', solta);
  viewport.addEventListener('wheel', e => {
    e.preventDefault();
    const r = viewport.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top, velho = scale;
    scale = Math.max(.03, Math.min(1.5, scale * (e.deltaY < 0 ? 1.13 : 1 / 1.13)));
    tx = mx - (mx - tx) * (scale / velho);
    ty = my - (my - ty) * (scale / velho);
    transform();
  }, { passive: false });

  $('plus').onclick = () => { scale *= 1.18; transform(); };
  $('minus').onclick = () => { scale *= .84; transform(); };
  $('fit').onclick = fit;
  $('reset').onclick = () => {
    pathSet = null; famsAtivas.clear(); $('search').value = '';
    document.querySelectorAll('.famBtn').forEach(x => x.classList.remove('active'));
    workspace.classList.remove('detailOpen'); applyFilters();
  };

  $('search').addEventListener('input', applyFilters);
  document.querySelectorAll('input[name=dept],input[name=status],input[name=pais],input[name=nat]')
    .forEach(x => x.addEventListener('change', applyFilters));
  document.querySelectorAll('.sideBtn[data-view]').forEach(b =>
    b.addEventListener('click', () => {
      document.querySelectorAll('.sideBtn[data-view]').forEach(x =>
        x.classList.remove('active'));
      b.classList.add('active'); currentView = b.dataset.view;
      pathSet = null; applyFilters();
    }));

  document.querySelectorAll('.famBtn').forEach(b => b.onclick = () => {
    // cada parte liga e desliga sozinha; as outras nao se apagam
    const f = b.dataset.fam;
    if (famsAtivas.has(f)) { famsAtivas.delete(f); b.classList.remove('active'); }
    else { famsAtivas.add(f); b.classList.add('active'); }
    b.setAttribute('aria-pressed', famsAtivas.has(f) ? 'true' : 'false');
    pathSet = null; applyFilters();
  });

  const modal = $('inventoryModal');
  $('openInventory').onclick = () => { renderInventory(); modal.classList.add('open'); };
  $('closeInventory').onclick = () => modal.classList.remove('open');
  $('invSearch').addEventListener('input', e => renderInventory(e.target.value));
  addEventListener('keydown', e => { if (e.key === 'Escape') modal.classList.remove('open'); });
  addEventListener('resize', mini);
}

async function arrancar() {
  try {
    S = await (await fetch('state.generated.json', { cache: 'no-store' })).json();
  } catch (err) {
    document.querySelector('.mapWrap').innerHTML =
      '<p style="padding:80px 24px;font-size:13px">Não consegui ler '
      + '<code>state.generated.json</code>. Rode '
      + '<code>py system-map/scripts/generate_system_map.py</code>.</p>';
    return;
  }
  nodes = S.NODES; edges = S.EDGES; MUNDO = S.WORLD;
  nodeById = Object.fromEntries(nodes.map(n => [n.id, n]));

  const c = S.COUNTS, P = S.PROVENANCE;
  $('snapshotTop').innerHTML =
    `<b>REPO</b> ${esc(P.REPO)}<br>` +
    `<b>BRANCH</b> ${esc(P.BRANCH)} @ ${esc(P.HEAD.slice(0, 7))}<br>` +
    `<b>GERADO</b> ${esc(P.GENERATED_AT.slice(0, 10))} · ` +
    `${c.files_covered}/${c.files_tracked} arquivos cobertos`;

  // OS ACHADOS FICAM RECOLHIDOS. Eles sao a parte mais valiosa do mapa e a que
  // mais atrapalha: aberto, o painel tapa um terco do desenho, e o mapa existe
  // para ser OLHADO. Fica uma pastilha com a contagem, e abre com um clique.
  const cinza = nodes.filter(n => n.ui_status === 'gray');
  const achados = (S.ACHADOS || []).slice();
  if (cinza.length) {
    achados.unshift({
      titulo: `${cinza.length} peça(s) em NÃO SEI`,
      texto: esc(cinza.map(n => n.name).join(' · ')) + '. Existem no repositório, e '
        + 'nada aponta para elas nem elas apontam para nada.',
      porque_importa: 'O mapa não inventa a ligação que falta.',
      evidencia: [],
    });
  }
  $('warning').innerHTML = achados.length
    ? `<button id="verAchados" class="achadoTag">⚠ ${achados.length} achado${
        achados.length > 1 ? 's' : ''} do mapa <span>mostrar</span></button>
       <div id="achadosCorpo" hidden>${achados.map(a => `
         <div class="achado"><b>${esc(a.titulo)}</b><br>${a.texto}<br>
           <i>${esc(a.porque_importa)}</i>${a.evidencia?.length
             ? `<br><span class="achadoOnde">medido em: ${
                 esc(a.evidencia.join(' · '))}</span>` : ''}</div>`).join('')}</div>`
    : '<button class="achadoTag" disabled>Nenhum achado neste commit</button>';
  if (achados.length) {
    $('verAchados').onclick = () => {
      const c = $('achadosCorpo'), aberto = !c.hidden;
      c.hidden = aberto;
      $('verAchados').querySelector('span').textContent = aberto ? 'mostrar' : 'esconder';
      $('warning').classList.toggle('aberto', !aberto);
    };
  }

  /* SO SE OFERECE O QUE SE PODE MOSTRAR.
     A lista de paises saia de todas as pecas, incluindo as guardadas, e por
     isso oferecia «ESPANHA» numa vista onde nenhuma peca espanhola aparece —
     um botao que promete e nao entrega. Agora so entram os paises com peca
     propria a vista, que aqui e a Italia, mais o tronco comum. */
  const paises = [...new Set(S.NODES
    .filter(n => n.pais === 'ITALIA' || n.pais === 'TRANSVERSAL')
    .map(n => n.pais))].sort();
  $('paises').innerHTML = '<label class="check"><input type="radio" name="pais" '
    + 'value="" checked>Tudo o que este mapa mostra</label>'
    + paises.map(x => `<label class="check"><input type="radio" name="pais"
        value="${esc(x)}">${x === 'TRANSVERSAL' ? 'SÓ O TRONCO COMUM' : esc(x)} · ${
        (x === 'TRANSVERSAL'
          ? S.NODES.filter(n => n.pais === x).length
          : S.NODES.filter(n => n.pais === x || n.pais === 'TRANSVERSAL').length)
        }${x === 'TRANSVERSAL' ? '' : ' <span style="color:#8a827e">(com o tronco comum)</span>'
        }</label>`).join('');

  $('fams').innerHTML = S.FAMILIES.map(f =>
    `<button class="famBtn" data-fam="${esc(f.id)}">
       <span class="swatch" style="background:var(--fam-${
         f.id.replace('F-', '').toLowerCase()})"></span>
       <span>${esc(f.name)} · ${f.count}<small>${esc(f.why.split('.')[0])}</small></span>
     </button>`).join('');

  $('views').innerHTML = VISOES.map(([v, ic, rot]) =>
    `<button class="sideBtn ${v === 'all' ? 'active' : ''}" data-view="${v}">
      <span>${ic}</span>${esc(rot)}</button>`).join('');
  $('depts').innerHTML = '<label class="check"><input type="radio" name="dept" '
    + 'value="Todos" checked>Todos</label>'
    + Object.entries(S.DEPARTMENTS).map(([k, desc]) =>
      `<label class="check" title="${esc(desc)}"><input type="radio" name="dept"
        value="${esc(k)}">${esc(k.replace(/_/g, ' '))}</label>`).join('');

  render(); bind(); renderMini(); applyFilters();
  requestAnimationFrame(fit);

  const alvo = location.hash.slice(1);
  if (alvo && nodeById[alvo]) openDetail(alvo);
}
arrancar();
