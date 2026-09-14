/* SINTONIA SYSTEM MAP — A LEI DA FRESCURA
   ---------------------------------------------------------------------------
   ESTE FICHEIRO NAO MEDE NADA. Ele DECIDE, e so isso.

   O mapa continua a ser a foto de UMA arvore. Isso esta certo. O defeito era
   outro: ele podia mostrar uma foto velha SEM AVISAR. Para avisar, quatro
   factos tem de existir separados, e nenhum pode ser confundido com o outro:

     ARCHITECTURE_SOURCE_TREE   a arvore que o gerador MEDIU  (GENERATED FROM)
     DEPLOYED_COMMIT            o commit que a build IMPLANTOU
     LATEST_CANONICAL_HEAD      a cabeca ACTUAL da linha canonica
     SYSTEM_MAP_CHECK           o veredito do validador

   AS QUATRO LEIS QUE ESTE FICHEIRO EXISTE PARA IMPOR:

       GENERATED   !=  DEPLOYED
       DEPLOYED    !=  LATEST REMOTE
       MAP VALID   !=  MAP CURRENT
       COVERAGE    !=  FRESHNESS

   A ultima e a mais facil de violar por acidente, e por isso `decidir()` NAO
   RECEBE COBERTURA. Nao e uma escolha de estilo: um numero que nao entra na
   funcao nao pode influenciar a decisao, e o teste consegue prova-lo.

       AUSENCIA DE PROVA DE STALENESS  !=  PROVA DE CURRENT.

   Por isso a ordem de decisao e: primeiro o que esta partido, depois o que nao
   se consegue medir, e so no fim o verde. Verde e o ULTIMO recurso, nunca o
   estado por omissao.
   --------------------------------------------------------------------------- */
'use strict';

(function (raiz) {
  const SHA = /^[0-9a-f]{40}$/;
  const CHECKS = new Set(['PASS', 'FAIL', 'UNKNOWN']);

  const curto = s => (typeof s === 'string' && s.length >= 7 ? s.slice(0, 8) : '—');

  /* ── ESTADOS ───────────────────────────────────────────────────────────────
     Vocabulario proprio da FRESCURA, escolhido para nao colidir com os quatro
     estados canonicos das PECAS (PROVEN · PENDING · BROKEN · UNKNOWN). Duas
     palavras iguais com dois sentidos seriam duas verdades com o mesmo nome —
     o pecado que este repositorio ja pagou uma vez.

     `BROKEN` e `UNKNOWN` repetem-se de proposito nos dois vocabularios: ali
     falam de uma peca, aqui falam do mapa inteiro, e o rotulo na tela diz
     sempre qual dos dois esta a falar («SYNC», nunca «estado da peca»). */
  const CURRENT = 'CURRENT';
  const STALE = 'STALE';
  const UNKNOWN = 'UNKNOWN';
  const BROKEN = 'BROKEN';

  const AVISO = {
    [CURRENT]: {
      emoji: '🟢',
      titulo: 'CURRENT',
      frase: 'O commit servido e a cabeca actual desta linha, e o validador passou.',
      grita: false,
    },
    [STALE]: {
      emoji: '🔴',
      titulo: 'STALE',
      frase: 'SYSTEM MAP DESATUALIZADO — NAO USE COMO VERDADE ACTUAL.',
      grita: true,
    },
    [UNKNOWN]: {
      emoji: '⚪',
      titulo: 'FRESHNESS UNKNOWN',
      frase: 'NAO FOI POSSIVEL CONFIRMAR a cabeca remota ao vivo. '
        + 'Isto nao e prova de que esta actual.',
      grita: false,
    },
    [BROKEN]: {
      emoji: '🔴',
      titulo: 'SYSTEM MAP INVALID',
      frase: 'A proveniencia do que esta servido contradiz-se ou nao passou o validador.',
      grita: true,
    },
  };

  /**
   * A decisao, e nada mais.
   *
   * @param {object} m  MEDICOES. Tudo pode faltar; faltar nunca da verde.
   *   repository              string   dono/repo, do estado gerado
   *   source_branch           string   a branch de onde a build saiu
   *   state_branch            string   a branch que o gerador mediu
   *   state_repository        string   o repo que o gerador mediu
   *   generated_from          sha40    PROVENANCE.HEAD do estado servido
   *   deployed_commit         sha40    DEPLOYED_COMMIT, nascido no build
   *   latest_canonical_head   sha40    medido ao vivo, ou null
   *   latest_head_error       string   porque falhou a medicao, ou null
   *   system_map_check        PASS|FAIL|UNKNOWN
   *   check_reason            string   porque o validador nao correu, ou null
   *   map_belongs_to_deployed_tree
   *                           true|false|null  o mapa servido foi DERIVADO da
   *                           arvore implantada? true so quando a build a
   *                           regerou e validou; null quando ninguem provou
   *   behind_by               int      commits de atraso, so se calculavel
   *   deployment_present      bool     existe artefato de deploy?
   *   schema_do_estado        string   SCHEMA do estado servido
   *   schema_declarado        string   SYSTEM_MAP_SCHEMA do artefato de deploy
   * @returns {{state:string, emoji:string, titulo:string, frase:string,
   *            grita:boolean, atraso:(string|null), razoes:string[]}}
   */
  function decidir(m) {
    m = m || {};
    const razoes = [];

    const check = CHECKS.has(m.system_map_check) ? m.system_map_check : 'UNKNOWN';
    const gerado = m.generated_from;
    const servido = m.deployed_commit;
    const remoto = m.latest_canonical_head;

    /* ── 1 · PARTIDO ─────────────────────────────────────────────────────────
       Vem primeiro porque um mapa que se contradiz nao merece a pergunta
       seguinte. Se a proveniencia mente, «esta actual?» nao tem resposta. */
    if (check === 'FAIL') {
      razoes.push('SYSTEM_MAP_CHECK REPROVOU para o que esta servido.');
      return veredito(BROKEN, razoes, null);
    }
    if (m.deployment_present && servido && !SHA.test(servido)) {
      razoes.push(`DEPLOYED_COMMIT nao e um SHA de 40 hex: ${String(servido).slice(0, 20)}`);
      return veredito(BROKEN, razoes, null);
    }
    if (gerado && !SHA.test(gerado)) {
      razoes.push('PROVENANCE.HEAD do estado servido nao e um SHA de 40 hex.');
      return veredito(BROKEN, razoes, null);
    }
    if (m.deployment_present && m.repository && m.state_repository
        && m.repository !== m.state_repository) {
      razoes.push('o artefato de deploy e o estado gerado discordam sobre o REPOSITORIO: '
        + `${m.repository} vs ${m.state_repository}`);
      return veredito(BROKEN, razoes, null);
    }
    if (m.deployment_present && m.schema_declarado && m.schema_do_estado
        && m.schema_declarado !== m.schema_do_estado) {
      razoes.push('o SCHEMA do estado servido nao e o que o artefato de deploy declara.');
      return veredito(BROKEN, razoes, null);
    }

    /* A BRANCH DIVERGENTE E UM AVISO, NAO UM VEREDITO — e isto foi medido.
       Um alias de branch estava a servir um mapa cujo `PROVENANCE.BRANCH` dizia
       OUTRA branch, legitimamente: a arvore veio de la. E ao regenerar dentro do
       contentor da Vercel, `git rev-parse --abbrev-ref HEAD` responde `master`,
       porque o checkout dela nao carrega o nome do ramo. Reprovar por isto seria
       gritar por uma diferenca que nao prova nada sobre frescura. */
    if (m.source_branch && m.state_branch && m.source_branch !== m.state_branch) {
      razoes.push(`aviso: o deploy saiu de ${m.source_branch} e o mapa servido foi `
        + `gerado em ${m.state_branch}.`);
    }

    /* ── 2 · SEM O COMMIT SERVIDO NAO HA PERGUNTA ────────────────────────────
       Uma copia commitada nao prova o que a build implantou. */
    if (!m.deployment_present || !servido) {
      razoes.push('nao existe artefato de deploy: o commit efectivamente servido '
        + 'nao foi provado. Uma copia commitada nao prova o que a build implantou.');
      return veredito(UNKNOWN, razoes, null);
    }

    /* ── 3 · ATRASADO — E ISTO PROVA-SE SOZINHO ──────────────────────────────
       ⚠️ VEM ANTES DAS MEDICOES QUE FALTAM, DE PROPOSITO. Se a cabeca remota foi
       medida e o commit servido nao e ela, o mapa ESTA atras — e continua a estar
       quer o validador tenha corrido, quer nao. Po-lo depois do portao do
       validador transformaria uma prova de staleness QUE EXISTE num UNKNOWN, que
       e a unica maneira de esta lei mentir para o lado confortavel.

           NAO SEI SE ESTA VALIDO  !=  NAO SEI SE ESTA ATRASADO. */
    if (remoto && SHA.test(remoto) && servido !== remoto) {
      const atraso = Number.isInteger(m.behind_by) && m.behind_by > 0
        ? `MAP IS ${m.behind_by} COMMIT${m.behind_by > 1 ? 'S' : ''} BEHIND`
        : 'HEAD MISMATCH';
      razoes.push(`o commit servido (${curto(servido)}) nao e a cabeca actual `
        + `desta linha (${curto(remoto)}).`);
      return veredito(STALE, razoes, atraso);
    }
    if (m.map_belongs_to_deployed_tree === false) {
      razoes.push(`o mapa servido foi gerado de ${curto(gerado)} e nao corresponde `
        + `a arvore de ${curto(servido)}: ele nao e o mapa DESTA arvore.`);
      return veredito(STALE, razoes, 'MAP OF ANOTHER TREE');
    }

    /* ── 4 · O QUE NAO SE CONSEGUIU MEDIR ────────────────────────────────────
       Aqui nao ha prova de atraso. E isso NAO e prova de actualidade. */
    if (check !== 'PASS') {
      razoes.push('SYSTEM_MAP_CHECK nao deu PASS para o que esta servido'
        + (m.check_reason ? `: ${m.check_reason}` : '.'));
      return veredito(UNKNOWN, razoes, null);
    }
    if (m.map_belongs_to_deployed_tree !== true) {
      razoes.push('nada prova que o mapa servido foi derivado da arvore implantada.');
      return veredito(UNKNOWN, razoes, null);
    }
    if (!remoto || !SHA.test(remoto)) {
      razoes.push('LATEST CANONICAL HEAD nao foi medido'
        + (m.latest_head_error ? ` (${m.latest_head_error})` : '')
        + '. Sem a cabeca remota, «igual» nao e uma frase que se possa dizer.');
      return veredito(UNKNOWN, razoes, null);
    }

    /* ── 5 · VERDE, e so agora ───────────────────────────────────────────────
       As quatro condicoes, todas MEDIDAS: cabeca remota medida, commit servido
       igual a ela, mapa provadamente derivado daquela arvore, e validador PASS. */
    razoes.push('cabeca remota medida, commit servido igual a ela, mapa derivado '
      + 'desta mesma arvore, validador PASS.');
    return veredito(CURRENT, razoes, null);
  }

  function veredito(estado, razoes, atraso) {
    const a = AVISO[estado];
    return {
      state: estado, emoji: a.emoji, titulo: a.titulo, frase: a.frase,
      grita: a.grita, atraso: atraso, razoes: razoes,
    };
  }

  raiz.SM_FRESHNESS = {
    decidir,
    ESTADOS: { CURRENT, STALE, UNKNOWN, BROKEN },
    SHA_RE: SHA,
    /* O ROTULO DA COBERTURA VIVE AQUI, ao lado da lei que ela nao governa.
       624/1321 nunca foi um indicador de actualizacao: e quantos ficheiros
       rastreados desta arvore o mapa consegue classificar. */
    COBERTURA_ROTULO: 'MAP COVERAGE',
    COBERTURA_EXPLICACAO: 'ficheiros rastreados desta arvore que o mapa '
      + 'representa e classifica. NAO e «ficheiros actualizados», e nao entra '
      + 'na decisao de frescura.',
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
