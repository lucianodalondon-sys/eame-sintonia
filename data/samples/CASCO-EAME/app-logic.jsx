
class Component extends DCLogic {
  state = {
    screen: this.props.telaInicial || 'home',
    country: this.props.paisInicial || 'es',
    lang: this.props.idiomaInicial || 'pt',
    countryOpen: false, langOpen: false,
    caseTab: 'sintese', line: 'all', status: 'all', win: 'all', zoom: 'ano',
    acervoTab: 'todos', fontesTab: 'todas', relTab: 'snapshots'
  };

  set(patch) { this.setState(patch); }

  renderVals() {
    const s = this.state;
    const screens = ['home','futuro','casos','caso','calendario','acervo','fontes','analises','relatorios','config','eame','lib'];
    const at = {}; const nav = {}; const go = {};
    screens.forEach(k => {
      at[k] = s.screen === k;
      nav[k] = s.screen === k ? '#ffffff' : 'rgba(255,255,255,.46)';
      go[k] = () => this.set({ screen: k, countryOpen: false, langOpen: false });
    });
    nav.casos = (s.screen === 'casos' || s.screen === 'caso') ? '#ffffff' : 'rgba(255,255,255,.46)';
    at.casosRail = s.screen === 'casos' || s.screen === 'caso';

    // ── CAMADA DE DADOS DO CASCO — a view lê daqui, nunca do markup ──────────
    const ST = {
      provado:   { label: 'PROVADO',        color: '#4fd18b', border: 'rgba(0,152,69,.45)', dash: 'solid' },
      parcial:   { label: 'PARCIAL',        color: '#f89e18', border: 'rgba(248,158,24,.45)', dash: 'solid' },
      medido:    { label: 'MEDIDO',         color: '#f89e18', border: 'rgba(248,158,24,.45)', dash: 'solid' },
      coleta:    { label: 'EM COLETA',      color: '#00a0df', border: 'rgba(0,160,223,.45)', dash: 'solid' },
      construcao:{ label: 'EM CONSTRUÇÃO',  color: 'rgba(255,255,255,.66)', border: 'rgba(151,139,135,.4)', dash: 'solid' },
      naoconect: { label: 'NÃO CONECTADO',  color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naomedido: { label: 'NÃO MEDIDO',     color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naoiniciada:{ label: 'NÃO INICIADA',  color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      congelado: { label: 'CONGELADO',      color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naosei:    { label: 'NÃO SEI',        color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naoaplica: { label: 'NÃO SE APLICA',  color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naodeterm: { label: 'NÃO DETERMINADO',color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      naocomp:   { label: 'AINDA NÃO COMPARÁVEL', color: 'rgba(255,255,255,.42)', border: 'rgba(151,139,135,.4)', dash: 'dashed' },
      comparavel:{ label: 'COMPARÁVEL',     color: '#4fd18b', border: 'rgba(0,152,69,.45)', dash: 'solid' },
      bloqueado: { label: 'BLOQUEADO',      color: '#c05a9a', border: 'rgba(117,33,87,.5)', dash: 'solid' }
    };
    const st = k => ({ label: ST[k].label, color: ST[k].color, border: ST[k].border, dash: ST[k].dash });
    const dim = (k, v, note) => ({ k, note: note || '', state: ST[v].label, color: ST[v].color, border: ST[v].border, dash: ST[v].dash });

    const COUNTRY_STATUS = {
      es: { name: 'Espanha', kind: 'PAÍS', badge: 'FUNDAÇÃO COMPLETA', badgeColor: '#4fd18b', badgeBorder: 'rgba(0,152,69,.45)',
        foundation: [
          dim('Portfólio', 'provado', 'catálogo integrado'),
          dim('Regulatório', 'provado', 'registro integrado'),
          dim('RAW / evidência original', 'provado', 'verificada'),
          dim('Campo / sinais', 'parcial', 'cobertura declarada'),
          dim('Tempo / janela', 'naoconect', 'relógios agronômicos'),
          dim('Decisão', 'construcao', 'vocabulário local e cruzamentos')
        ] },
      it: { name: 'Itália', kind: 'PAÍS', badge: 'EM COLETA', badgeColor: '#00a0df', badgeBorder: 'rgba(0,160,223,.45)',
        foundation: [
          dim('Portfólio', 'coleta', 'catálogo em coleta'),
          dim('Regulatório', 'medido', 'medido'),
          dim('RAW / evidência original', 'coleta', 'rota aberta'),
          dim('Campo / sinais', 'congelado', 'congelado após evidência atual'),
          dim('Tempo / janela', 'naoconect', ''),
          dim('Decisão', 'naoiniciada', '')
        ] },
      fr: { name: 'França', kind: 'PAÍS', badge: 'EM COLETA', badgeColor: '#00a0df', badgeBorder: 'rgba(0,160,223,.45)',
        foundation: [
          dim('Portfólio', 'coleta', ''),
          dim('Regulatório', 'coleta', ''),
          dim('RAW / evidência original', 'coleta', 'rota aberta'),
          dim('Campo / sinais', 'naoconect', ''),
          dim('Tempo / janela', 'naoconect', ''),
          dim('Decisão', 'naoiniciada', '')
        ] },
      eame: { name: 'EAME', kind: 'CAMADA', badge: 'CAMADA CROSS-MARKET', badgeColor: 'rgba(255,255,255,.66)', badgeBorder: 'rgba(151,139,135,.4)',
        foundation: [
          dim('Área de cultura', 'comparavel', ''),
          dim('Preço de referência', 'comparavel', ''),
          dim('Regulatório', 'parcial', 'por país'),
          dim('Campo / sinais', 'naocomp', ''),
          dim('Tempo / janela', 'naocomp', ''),
          dim('Decisão', 'naoiniciada', '')
        ] }
    };
    const countries = COUNTRY_STATUS;
    const setCountry = {};
    Object.keys(countries).forEach(k => {
      setCountry[k] = () => this.set({
        country: k, countryOpen: false,
        screen: k === 'eame' ? 'eame' : (s.screen === 'eame' ? 'home' : s.screen)
      });
    });
    const countryList = Object.keys(COUNTRY_STATUS).map(k => ({
      id: k, name: COUNTRY_STATUS[k].name, kind: COUNTRY_STATUS[k].kind,
      badge: COUNTRY_STATUS[k].badge, badgeColor: COUNTRY_STATUS[k].badgeColor, badgeBorder: COUNTRY_STATUS[k].badgeBorder,
      isLayer: k === 'eame', open: setCountry[k]
    }));
    const countryPortals = countryList.filter(c => !c.isLayer);
    const layerEntry = countryList.filter(c => c.isLayer);

    // Mapa de ação — oito áreas, Market Development no centro do fluxo
    const AREAS = [
      { name: 'Market Development', role: 'avalia e programa a investigação', core: true },
      { name: 'Regulatório', role: 'verifica condições e rótulo', core: false },
      { name: 'Portfólio', role: 'confirma resposta registrada', core: false },
      { name: 'Técnico / Agronomia', role: 'valida no campo', core: false },
      { name: 'Marketing', role: 'prepara comunicação', core: false },
      { name: 'Comercial', role: 'prepara equipe e território', core: false },
      { name: 'Ciência & P&D', role: 'investiga a hipótese', core: false },
      { name: 'Supply', role: 'planeja disponibilidade', core: false }
    ];
    const actionAreas = AREAS.map(a => ({
      name: a.name, role: a.role,
      accent: a.core ? '#4fd18b' : 'rgba(151,139,135,.45)',
      bg: a.core ? 'rgba(0,152,69,.07)' : 'var(--s2)',
      border: a.core ? 'rgba(0,152,69,.35)' : 'var(--hair2)',
      badge: a.core ? 'ÁREA CENTRAL' : '',
      state: ST.naodeterm.label, stateColor: ST.naodeterm.color, stateBorder: ST.naodeterm.border
    }));

    // Camadas de evidência do caso — estado, nunca score
    const evidenceLayers = [
      { name: 'Campo', s: 'naomedido' },
      { name: 'Ciência', s: 'naomedido' },
      { name: 'Clima', s: 'naomedido' },
      { name: 'Regulatório', s: 'naomedido' },
      { name: 'Portfólio local ADAMA', s: 'naomedido' },
      { name: 'Competição', s: 'naomedido' },
      { name: 'Tempo', s: 'naoconect' }
    ].map(l => ({ name: l.name, state: ST[l.s].label, color: ST[l.s].color, border: ST[l.s].border, dash: ST[l.s].dash }));

    // Camadas que não podem ser fundidas
    const decisionLayers = [
      { k: 'Resposta local registrada', v: 'NÃO PROVADO' },
      { k: 'Janela agronômica', v: 'NÃO CONECTADA' },
      { k: 'Janela de decisão', v: 'NÃO DETERMINADA' },
      { k: 'Disponibilidade comercial', v: 'NÃO SEI' },
      { k: 'Prioridade interna', v: 'NÃO SEI' }
    ];
    const competitorLayers = [
      { k: 'Resposta registrada do concorrente', v: 'NÃO SEI' },
      { k: 'Atividade paga em mídia', v: 'NÃO SEI' },
      { k: 'Comunicação pública', v: 'NÃO SEI' },
      { k: 'Atividade técnica', v: 'NÃO SEI' }
    ];
    const radarContract = ['country','crop','issue / theme','region','why_on_radar','first_observed','last_observed','source_date','current_evidence','missing_evidence','agronomic_window','decision_window','who_should_look','next_checkpoint'];
    const radarStates = ['EARLY SIGNAL','CONVERGENCE FORMING','DECISION POTENTIALLY OPEN','FUTURE PLANNING','NÃO SEI'];
    const acervoContract = ['country','source','source_type','document_type','product','registration','crop','issue','capture_date','source_date','raw_state','sha_verified','evidence_level'];
    const sourceContract = ['country','entity_kind','source_role','access_state','cadence','geographic_scope','crop_scope','prospective / retrospective','last_capture','next_expected','collection_state'];
    const agroContract = ['crop','issue','phenology / BBCH','application_window','source','precision','state'];
    // ── CAMADA EAME — comparação, convergência e coordenação (nunca soma de países)
    const drill = (c, screen) => () => this.set({ country: c, screen: screen || 'home', countryOpen: false });
    const eameLanes = ['es','it','fr'].map(k => ({
      code: k.toUpperCase(), name: COUNTRY_STATUS[k].name,
      foundation: COUNTRY_STATUS[k].badge, color: COUNTRY_STATUS[k].badgeColor, border: COUNTRY_STATUS[k].badgeBorder,
      freshness: '—', signals: 'NÃO MEDIDO', windows: 'NÃO MEDIDO',
      gaps: k === 'es' ? 'relógios agronômicos e vocabulário local' : (k === 'it' ? 'catálogo e RAW em coleta' : 'fundação em coleta'),
      open: drill(k, 'home'), openCases: drill(k, 'casos')
    }));
    const convergenceSlots = [
      { id: 'CM-SLOT-01', countries: 'dois ou mais mercados', line: '#00a0df', lineLabel: 'linha do assunto — a definir' },
      { id: 'CM-SLOT-02', countries: 'dois ou mais mercados', line: '#7db41e', lineLabel: 'linha do assunto — a definir' }
    ];
    const divergenceTypes = [
      { k: 'Divergência regulatória', v: 'NÃO MEDIDA' },
      { k: 'Divergência de portfólio', v: 'NÃO MEDIDA' },
      { k: 'Divergência de tempo', v: 'NÃO MEDIDA' },
      { k: 'Divergência de sinal de campo', v: 'NÃO MEDIDA' },
      { k: 'Divergência de concorrência', v: 'NÃO MEDIDA' },
      { k: 'Divergência de cobertura de evidência', v: 'PARCIAL — declarada por país' }
    ];
    const timingLanes = ['es','it','fr'].map(k => ({
      code: k.toUpperCase(), name: COUNTRY_STATUS[k].name, state: 'JANELA LOCAL NÃO CONECTADA', open: drill(k, 'calendario')
    }));
    const planningStates = ['NEXT MARKET APPROACHING','MULTI MARKET ACTIVE','ONLY FUTURE MARKETS','REGIONAL PREPARATION POSSIBLE','NÃO SEI'];
    const asymRows = [
      { problem: 'Problema — slot 01', es: 'NÃO PROVADA', it: 'NÃO SEI', fr: 'NÃO SEI' },
      { problem: 'Problema — slot 02', es: 'NÃO SEI', it: 'NÃO PROVADA', fr: 'NÃO SEI' }
    ];
    const comparability = [
      { d: 'Área de cultura', es: 'comparavel', it: 'comparavel', fr: 'comparavel' },
      { d: 'Preço de referência', es: 'comparavel', it: 'comparavel', fr: 'comparavel' },
      { d: 'Regulatório', es: 'parcial', it: 'parcial', fr: 'parcial' },
      { d: 'Sinal de campo', es: 'parcial', it: 'naocomp', fr: 'naocomp' },
      { d: 'Clima', es: 'naomedido', it: 'naomedido', fr: 'naomedido' },
      { d: 'Portfólio local', es: 'naocomp', it: 'naocomp', fr: 'naocomp' },
      { d: 'Atividade de concorrência', es: 'bloqueado', it: 'bloqueado', fr: 'bloqueado' },
      { d: 'Tempo / janela', es: 'naoconect', it: 'naoconect', fr: 'naoconect' }
    ].map(r => ({
      d: r.d,
      esL: ST[r.es].label, esC: ST[r.es].color, esB: ST[r.es].border, esD: ST[r.es].dash,
      itL: ST[r.it].label, itC: ST[r.it].color, itB: ST[r.it].border, itD: ST[r.it].dash,
      frL: ST[r.fr].label, frC: ST[r.fr].color, frB: ST[r.fr].border, frD: ST[r.fr].dash
    }));
    const regionalAreas = [
      { name: 'Market Development regional', why: 'decide onde aprofundar, coordenar ou antecipar', core: true },
      { name: 'Regulatório', why: 'mesmo ato tocando mais de um mercado', core: false },
      { name: 'Portfólio', why: 'assimetria de resposta registrada entre países', core: false },
      { name: 'Marketing', why: 'narrativa reaproveitável entre mercados', core: false },
      { name: 'Comercial', why: 'sequência de entrada por mercado', core: false },
      { name: 'Ciência & P&D', why: 'hipótese que se repete em mais de um país', core: false },
      { name: 'Supply', why: 'demanda potencial em mercados sequenciais', core: false }
    ].map(a => ({
      name: a.name, why: a.why,
      accent: a.core ? '#4fd18b' : 'rgba(151,139,135,.45)',
      bg: a.core ? 'rgba(0,152,69,.07)' : 'var(--s2)',
      border: a.core ? 'rgba(0,152,69,.35)' : 'var(--hair2)',
      badge: a.core ? 'ÁREA CENTRAL' : '',
      state: 'NÃO DETERMINADO'
    }));
    const eameRadarTypes = [
      { k: 'A', t: 'Mesmo issue em múltiplos mercados' },
      { k: 'B', t: 'Mudança regulatória tocando vários mercados' },
      { k: 'C', t: 'Assimetria de portfólio local' },
      { k: 'D', t: 'Sinal observado em mais de um mercado' },
      { k: 'E', t: 'Sequência de janelas de mercado' },
      { k: 'F', t: 'Atividade de concorrência entre mercados' },
      { k: 'G', t: 'Molécula, tecnologia ou IP com relevância multi-mercado' }
    ];
    const eameRadarContract = ['countries','common_evidence','local_differences','time_sequence','what_is_not_comparable','why_eame_should_look'];
    const crossCaseParts = ['A pergunta comum','Países envolvidos','O que é comum','O que é diferente','Evidência local por país','Resposta ADAMA local por país','Tempo por país','Pergunta de planejamento regional','Quem deve olhar','O que ainda não sabemos']
      .map((t, i) => ({ n: i + 1, t }));
    const regionalActionContract = ['area','countries_affected','why_regional','local_owner','regional_owner','timing','evidence_required'];
    const eameGrammar = ['Onde existe questão regional?','Onde os mercados divergem?','Qual a sequência de janelas?','Onde o portfólio local difere?','O que investigar regionalmente?','Onde falta cobertura?'].map((t, i) => ({ n: i + 1, t }));

    const grammar = ['O que merece atenção','Ainda há tempo para agir?','Por que está no radar?','Quem deve olhar?','Qual evidência sustenta?','O que ainda não sabemos?']
      .map((t, i) => ({ n: i + 1, t }));

    const langs = { pt: 'PT', en: 'EN', es: 'ES', it: 'IT', fr: 'FR' };
    const setLang = {};
    Object.keys(langs).forEach(k => { setLang[k] = () => this.set({ lang: k, langOpen: false }); });

    // tabs do detalhe de caso
    const caseTabs = ['sintese','evidencias','convergencia','cruzamentos','areas','historico'];
    const tab = {}; const tabColor = {}; const goTab = {};
    caseTabs.forEach(k => {
      tab[k] = s.caseTab === k;
      tabColor[k] = s.caseTab === k ? '#ffffff' : 'rgba(255,255,255,.5)';
      goTab[k] = () => this.set({ caseTab: k });
    });

    // filtros do Radar / Casos — o casco filtra slots estruturais, não dados
    const LINES = {
      disease: { label: 'Disease Control', color: '#00a0df' },
      weed:    { label: 'Weed Control',    color: '#7db41e' },
      pest:    { label: 'Pest Control',    color: '#9d1d96' },
      crop:    { label: 'Crop Enhancement',color: '#f89e18' }
    };
    const STATUS = {
      formacao:   { label: 'Em formação',      color: '#978b87' },
      observacao: { label: 'Em observação',    color: '#f89e18' },
      confirmado: { label: 'Caso confirmado',  color: '#009845' },
      bloqueado:  { label: 'Bloqueado',        color: '#752157' }
    };
    // estados de janela temporal — o calendário só dá contexto, nunca decide aplicação
    const WIN = {
      aberta:     { label: 'Janela aberta',        color: '#009845' },
      encerrando: { label: 'Janela se encerrando', color: '#f89e18' },
      encerrada:  { label: 'Janela encerrada',     color: '#978b87' },
      proximo:    { label: 'Próximo ciclo',        color: '#00a0df' },
      naosei:     { label: 'Janela não conhecida', color: 'rgba(255,255,255,.35)' }
    };
    const rawCases = [
      { id: 'SLOT-01', cls: 'REGULATORY DEADLINE',     line: 'disease', status: 'confirmado', country: 'Espanha', win: 'aberta' },
      { id: 'SLOT-02', cls: 'GEOGRAPHIC PRIORITY',     line: 'disease', status: 'observacao', country: 'Espanha', win: 'encerrando' },
      { id: 'SLOT-03', cls: 'INVESTIGATE',             line: 'weed',    status: 'formacao',   country: 'Espanha', win: 'proximo' },
      { id: 'SLOT-04', cls: 'ACTIVATION QUESTION',     line: 'pest',    status: 'observacao', country: 'Espanha', win: 'naosei' },
      { id: 'SLOT-05', cls: 'CHANGE DETECTED',         line: 'crop',    status: 'formacao',   country: 'Espanha', win: 'encerrada' },
      { id: 'SLOT-06', cls: 'REGULATORY DEADLINE',     line: 'weed',    status: 'bloqueado',  country: 'Espanha', win: 'naosei' },
      { id: 'SLOT-07', cls: 'GEOGRAPHIC PRIORITY',     line: 'pest',    status: 'formacao',   country: 'Espanha', win: 'proximo' },
      { id: 'SLOT-08', cls: 'INVESTIGATE',             line: 'crop',    status: 'observacao', country: 'Espanha', win: 'aberta' }
    ];
    const cases = rawCases
      .filter(c => s.line === 'all' || c.line === s.line)
      .filter(c => s.status === 'all' || c.status === s.status)
      .filter(c => s.win === 'all' || c.win === s.win)
      .map(c => ({
        id: c.id, cls: c.cls, country: c.country,
        lineLabel: LINES[c.line].label, color: LINES[c.line].color,
        statusLabel: STATUS[c.status].label, statusColor: STATUS[c.status].color,
        winLabel: WIN[c.win].label, winColor: WIN[c.win].color,
        open: () => this.set({ screen: 'caso', caseTab: 'sintese' })
      }));
    const winChip = {}; const setWin = {};
    ['all','aberta','encerrando','encerrada','proximo','naosei'].forEach(k => {
      winChip[k] = s.win === k ? 'rgba(255,255,255,.12)' : 'transparent';
      setWin[k] = () => this.set({ win: k });
    });
    const ZOOM = { ano: '100%', tri: '190%', mes: '320%' };
    const zoomOn = {}; const zoomColor = {}; const setZoom = {};
    Object.keys(ZOOM).forEach(k => {
      zoomOn[k] = s.zoom === k;
      zoomColor[k] = s.zoom === k ? '#ffffff' : 'rgba(255,255,255,.5)';
      setZoom[k] = () => this.set({ zoom: k });
    });

    const lineChip = {}; const setLine = {};
    ['all','disease','weed','pest','crop'].forEach(k => {
      lineChip[k] = s.line === k ? 'rgba(255,255,255,.12)' : 'transparent';
      setLine[k] = () => this.set({ line: k });
    });
    const statusChip = {}; const setStatus = {};
    ['all','formacao','observacao','confirmado','bloqueado'].forEach(k => {
      statusChip[k] = s.status === k ? 'rgba(255,255,255,.12)' : 'transparent';
      setStatus[k] = () => this.set({ status: k });
    });

    const subTabs = (key, keys) => {
      const active = {}; const color = {}; const set = {};
      keys.forEach(k => {
        active[k] = s[key] === k;
        color[k] = s[key] === k ? '#ffffff' : 'rgba(255,255,255,.5)';
        set[k] = () => this.set({ [key]: k });
      });
      return { active, color, set };
    };
    const acervo = subTabs('acervoTab', ['todos','regulatorio','ciencia','campo','mercado']);
    const fontes = subTabs('fontesTab', ['todas','green','amber','red']);
    const rel = subTabs('relTab', ['snapshots','freezes','dossies']);

    return {
      at, nav, go,
      countryName: countries[s.country].name,
      countryKind: countries[s.country].kind,
      countryBadge: countries[s.country].badge,
      countryBadgeColor: countries[s.country].badgeColor,
      countryBadgeBorder: countries[s.country].badgeBorder,
      foundation: countries[s.country].foundation,
      countryList, countryPortals, layerEntry,
      actionAreas, evidenceLayers, decisionLayers, competitorLayers,
      radarContract, radarStates, acervoContract, sourceContract, agroContract, grammar,
      eameLanes, convergenceSlots, divergenceTypes, timingLanes, planningStates, asymRows,
      comparability, regionalAreas, eameRadarTypes, eameRadarContract, crossCaseParts,
      regionalActionContract, eameGrammar,
      countryOpen: s.countryOpen,
      toggleCountry: () => this.set({ countryOpen: !s.countryOpen, langOpen: false }),
      setCountry,
      langCode: langs[s.lang],
      langOpen: s.langOpen,
      toggleLang: () => this.set({ langOpen: !s.langOpen, countryOpen: false }),
      setLang,
      tab, tabColor, goTab,
      cases, lineChip, setLine, statusChip, setStatus, winChip, setWin,
      zoomOn, zoomColor, setZoom, zoomWidth: ZOOM[s.zoom],
      caseCount: cases.length,
      acervoOn: acervo.active, acervoColor: acervo.color, setAcervo: acervo.set,
      fontesOn: fontes.active, fontesColor: fontes.color, setFontes: fontes.set,
      relOn: rel.active, relColor: rel.color, setRel: rel.set
    };
  }
}
