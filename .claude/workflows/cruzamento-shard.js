export const meta = {
  name: 'cruzamento-shard',
  description: 'Cruzar os sinais ja verificados de um grupo de culturas contra o acervo inteiro, e dizer o que cada cruzamento NAO prova',
  phases: [
    { title: 'Cruzar', detail: 'os dez tipos de conexao, dentro de um grupo de culturas' },
    { title: 'Refutar', detail: 'um cetico por cruzamento proposto' },
  ],
}

const REPO = '/home/user/eame-sintonia'
// O pacote canonico V2.1 vive VERSIONADO no repositorio. Ate 2026-09-04 esta constante
// apontava para o scratchpad efemero de um conteiner que morreu, e com ele morreram tres
// grupos de cruzamento e doze leituras. ARQUIVO NAO COMMITADO NAO SOBREVIVE A TROCA DE
// CONTA. Proveniencia e SHA de cada arquivo em IT-RADAR-V21/MANIFEST.json; conferir com
// `python3 scripts/radar_v21.py verificar`.
const SC = `${REPO}/data/samples`
const V21 = `${SC}/IT-RADAR-V21`

const LEI = `
LEIS DESTA CASA — nao negociaveis:
1. SO CRUZE QUANDO OS EIXOS FOREM COMPATIVEIS. Mesma cultura, mesmo alvo, e regiao e janela
   que se sobrepoem DE VERDADE. Cruzar Emilia-Romagna com Puglia porque as duas sao Italia e
   o defeito cartesiano, e ele ja custou caro nesta casa.
2. CUIDADO COM O TEMPO. Um bilancio fitosanitario 2024/2025 descreve a campanha PASSADA; um
   bollettino de 2026-09-02 descreve a semana corrente. Cruzar os dois como se fossem o mesmo
   momento e erro. Declare sempre, em time_order, o que veio antes.
3. PORTFOLIO RELATION != LABEL AUTHORIZATION. E 51 produtos comerciais != 163 registros no
   Ministero != 56 agrofarmaci que o Fitogest atribui a ADAMA.
4. MOLECULA MARCADA != MOLECULA ADAMA. Confira contra as 53 de activeIngredients.json. NAO
   estao la: acetamiprid, spinosad, deltametrina, mancozeb, pyraclostrobin, propanil,
   bentazone, clomazone, cycloxydim, etofenprox, rame, zolfo, fosmet, metribuzin, fipronil.
5. UMA VOZ NAO E UMA TENDENCIA. Convergencia chama-se CLUSTER NELLE FONTI MONITORATE.
6. AUSENCIA NA NOSSA LEITURA != AUSENCIA NO MUNDO. A leitura de rotulo cobre 102 dos 163
   registros. E A AFIRMACAO DE AUSENCIA E A MAIS FACIL DE FAZER E A MAIS CARA DE ERRAR: um
   sinal desta casa afirmou que NENHUM par VITE x COCCINIGLIA existia, e foi refutado pelo
   proprio arquivo que ele citava como prova.
7. NADA AQUI PROMOVE NADA. STATUS_CHANGES = 0, SCORE_CHANGES = 0.
8. NAO_SEI e resposta.`

const RADAR = `
RADAR ADAMA ITALIA: BARBABIETOLA 239 · FRUMENTO 176 · MELO 146 · ORZO 131 · MAIS 112 ·
PATATA 100 · BRASSICACEE 100 · VITE 96 · ERBA_MEDICA 87 · CAROTA 63 · FRAGOLA 51 · PESCO 45 ·
POMODORO 44 · CIPOLLA 42 · SOIA 28 · CILIEGIO 27 · AGRUMI 17 · RISO 15 · PERO 11 · OLIVO 1.
Alvo n.1: AFIDI, 436 pares. 2.030 pares em ${V21}/productRelationships.json.
LINK_STRENGTH: LINHA_DA_TABELA > BLOCO_DA_CULTURA > DECLARACAO_DE_PRODUTO > SUBSTANCIA_ATIVA.
9 oportunidades confirmadas: OPP_2BDE8FC566CE OPP_3965565ACFCC OPP_576D71D702F0
OPP_6E18A133EE14 OPP_886307860F79 OPP_88CC35C57C7B OPP_8EA4F5C0D3F4 OPP_AF16E6A6B8B3
OPP_E6200AA0FA63. Regioes: Emilia-Romagna, Veneto, Lombardia, FVG, Piemonte, Puglia,
Toscana, Sicilia, Trentino-Alto Adige.
ASSIMETRIA: OLIVO tem UM par de rotulo lido — MORAINE 018101 x INFESTANTI, um HERBICIDA.`

const ACERVO = `
OS ARQUIVOS, todos fechados e versionados:
  ${REPO}/data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json   21 sinais de BOLETIM
  ${REPO}/data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V2.json   19 sinais de FALA
  ${REPO}/data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json  421 mencoes
  ${REPO}/data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-2026-INDICE.json     150 bollettini
  ${REPO}/data/samples/IT-CAMPO-V1/IT-CIMICE-TRAPPOLE-UNIBO-SERIE.json   177 pontos 2021-2026
  ${REPO}/data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json  7 cruzamentos e 7 nao-cruzamentos JA FEITOS
  ${REPO}/data/samples/IT-CRUZAMENTO-V1/IT-ENRIQUECIMENTO-CONFIRMADAS-V1.json
  ${REPO}/data/samples/IT-SNAPSHOT-V1/IT-INVENTARIO-FALA-V3.json  117 objetos, 816 numeros ditos
  ${REPO}/data/samples/IT-CONVEGNO-V1/falas/*.json  o texto integral das gravacoes
  ${REPO}/data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json  91 fichas
  ${V21}/*.json  o pacote canonico`

const TIPOS = `OS DEZ TIPOS, e o nome de cada um:
  1  FALA_CONFIRMA_ESCRITO        a fala confirma algo ja visto em boletim ou documento
  2  FALA_ANTECEDE_INSTITUCIONAL  a voz publica falou ANTES da fonte institucional. Voce
                                  PRECISA das duas datas e da prova de que o assunto e o
                                  mesmo. Sem as duas datas, e coincidencia, e nao entra.
  3  DUAS_VOZES_INDEPENDENTES     duas origens sem relacao apontam o mesmo fenomeno
  4  PRODUTOR_E_TECNICO           quem produz e quem assiste descrevem o mesmo problema
  5  JANELA_QUE_FALTAVA           o conteudo da o QUANDO que faltava a um caso
  6  CONTRADIZ_SINAL_EXISTENTE    bate de frente com sinal ja registrado
  7  ESFRIA_OPORTUNIDADE          enfraquece ou fecha um caso
  8  ABRE_OPORTUNIDADE            abre um caso que nao existia
  9  CONTEXTO_REGIONAL            acrescenta lugar a um caso que estava sem lugar
  10 NECESSIDADE_FUTURA           aponta necessidade sem oportunidade imediata`

const CRUZ_SCHEMA = {
  type: 'object',
  required: ['crossings', 'not_crossed', 'notes'],
  properties: {
    crossings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['kind', 'title', 'crop', 'issue', 'region', 'sources_crossed', 'relation',
                   'adama_link', 'link_strength', 'time_order', 'proves', 'does_not_prove'],
        properties: {
          kind: { type: 'string' }, title: { type: 'string' },
          crop: { type: 'string' }, issue: { type: 'string' }, region: { type: 'string' },
          window: { type: 'string' },
          sources_crossed: { type: 'array', items: { type: 'string' } },
          quotes: { type: 'array', items: { type: 'string' } },
          relation: { type: 'string', enum: ['SUPPORTS', 'WEAKENS', 'CONTRADICTS', 'CLOSES', 'OPENS', 'UNKNOWN'] },
          adama_link: { type: 'string' },
          adama_label_pairs: { type: 'array', items: { type: 'string' } },
          link_strength: { type: 'string' },
          opportunity_ids: { type: 'array', items: { type: 'string' } },
          time_order: { type: 'string' },
          act_now_watch_or_not_yet: { type: 'string', enum: ['ACT_NOW', 'WATCH', 'NOT_YET'] },
          who_at_adama: { type: 'string' },
          what_is_still_missing: { type: 'string' },
          proves: { type: 'string' }, does_not_prove: { type: 'string' },
        },
      },
    },
    not_crossed: {
      type: 'array',
      items: { type: 'object', required: ['pair', 'why'],
               properties: { pair: { type: 'string' }, why: { type: 'string' } } },
    },
    notes: { type: 'string' },
  },
}

const REFUTA_SCHEMA = {
  type: 'object',
  required: ['refuted', 'confidence', 'why', 'what_i_checked'],
  properties: {
    refuted: { type: 'boolean' },
    confidence: { type: 'string', enum: ['HIGH', 'MEDIUM', 'LOW'] },
    why: { type: 'string' }, what_i_checked: { type: 'string' },
    correction: { type: 'string' }, axis_that_failed: { type: 'string' },
  },
}

const GRUPO = (args && args.grupo) || {}
if (!GRUPO.key) throw new Error('passe args.grupo com {key, culturas, foco}')
log(`Grupo ${GRUPO.key}: ${GRUPO.culturas}`)

phase('Cruzar')
const proposto = await agent(`CRUZAMENTOS DE INTELIGENCIA — grupo ${GRUPO.key}.
${LEI}
${RADAR}
${ACERVO}
${TIPOS}

O SEU GRUPO DE CULTURAS: ${GRUPO.culturas}
FOCO: ${GRUPO.foco}

Trabalhe SO com sinais e objetos que tocam essas culturas. Abra os dois arquivos de sinais
verificados com python3, filtre pelo seu grupo, e leia TAMBEM o texto integral da gravacao
quando o sinal vier da fala — a citacao curta do arquivo de sinais nao basta para julgar
compatibilidade de eixo.

ANTES DE ESCREVER: leia os 7 cruzamentos e os 7 nao-cruzamentos que ja existem em
IT-CRUZAMENTOS-V1.json. Repetir um deles nao e achado, e ruido. E veja o padrao dos dois que
ESFRIAM: achar o elo e ainda assim esfriar o caso e o comportamento correto, e vale mais que
um cruzamento otimista.

PARA CADA CRUZAMENTO: cite as fontes cruzadas, as citacoes literais, a ordem no tempo, o par
de rotulo ADAMA com a forca LIDA no arquivo, e — obrigatoriamente — o que ele PROVA e o que
ele NAO PROVA. E classifique em ACT_NOW, WATCH ou NOT_YET, dizendo o que falta para mudar de
faixa. NAO declare ACT_NOW sem janela e sem vinculo.

Devolva no maximo 6 cruzamentos, e prefira 2 excelentes a 6 razoaveis: cada um sera atacado
por um cetico. Zero cruzamentos e um resultado correto se os eixos nao fecharem — e nesse
caso o valor esta todo em not_crossed.

Em not_crossed registre todo par que voce considerou e descartou, com o motivo. Isso impede
que a proxima passagem gaste o mesmo tempo no mesmo beco.`,
  { label: `cruzar:${GRUPO.key}`, phase: 'Cruzar', schema: CRUZ_SCHEMA })

const props = (proposto && proposto.crossings) || []
log(`Grupo ${GRUPO.key}: ${props.length} cruzamentos propostos, ${(proposto && proposto.not_crossed || []).length} descartados com motivo`)

phase('Refutar')
const veredictos = await parallel(props.slice(0, 6).map(c => () =>
  agent(`Voce e um CETICO. Nao concorde: DERRUBE. Na duvida, cai.
${LEI}
${RADAR}
${ACERVO}

O CRUZAMENTO PROPOSTO:
  tipo       ${c.kind}
  titulo     ${c.title}
  cultura    ${c.crop} · alvo ${c.issue} · regiao ${c.region} · janela ${c.window || 'NAO_SEI'}
  fontes     ${(c.sources_crossed || []).join(' | ')}
  citacoes   ${(c.quotes || []).map(q => '"' + String(q).slice(0, 300) + '"').join(' /// ')}
  relacao    ${c.relation}
  elo ADAMA  ${c.adama_link}
  pares      ${(c.adama_label_pairs || []).join(' | ') || 'nenhum declarado'}
  forca      ${c.link_strength}
  ordem      ${c.time_order}
  faixa      ${c.act_now_watch_or_not_yet || 'NAO_SEI'}
  prova      ${c.proves}
  nao prova  ${c.does_not_prove}

ATAQUE, cada passo com leitura real de arquivo:
1. AS DUAS PONTAS EXISTEM? Abra os arquivos citados em sources_crossed e confirme que cada
   citacao esta la, palavra por palavra (ASR pode deformar grafia; a substancia nao).
   Faltou uma ponta -> REFUTADO.
2. OS EIXOS SAO MESMO COMPATIVEIS? Mesma cultura, mesmo alvo, regioes que se sobrepoem?
   Cruzou Emilia-Romagna com Puglia, ou melo com pero, como se fossem o mesmo? -> REFUTADO.
3. A ORDEM NO TEMPO ESTA CERTA? Se o cruzamento e do tipo 2 (fala antecede institucional),
   as DUAS datas tem de estar no arquivo. Se uma ponta e um bilancio 2024/2025 e a outra um
   bollettino de 2026, isso NAO e simultaneidade -> se foi tratado como tal, REFUTADO.
4. O PAR DE ROTULO EXISTE, e com a forca declarada? Confira em
   ${V21}/productRelationships.json com fronteira de palavra. Inflou a forca -> REFUTADO.
5. A MOLECULA dita ADAMA esta entre as 53? Confira em ${V21}/activeIngredients.json.
   Rame, zolfo, mancozeb, acetamiprid, spinosad, deltametrina, fipronil, metribuzin NAO
   estao -> se alguma foi chamada de nossa, REFUTADO.
6. E JA EXISTE? Se este cruzamento repete um dos 7 de IT-CRUZAMENTOS-V1.json sem acrescentar
   eixo novo, ele nao e achado -> REFUTADO, e diga qual repete.
7. O ACT_NOW se sustenta? Sem janela com data e sem vinculo lido, ACT_NOW e invencao -> a
   relacao nao morre, mas a faixa cai: escreva isso em correction.

refuted=true se qualquer ataque de 1 a 6 derrubar, ou se voce ficar em duvida.`,
    { label: `refuta:${GRUPO.key}:${String(c.crop || '?').slice(0, 12)}`, phase: 'Refutar', schema: REFUTA_SCHEMA })
    .then(v => ({ crossing: c, verdict: v }))))

const testados = veredictos.filter(Boolean)
const vivos = testados.filter(t => t.verdict && t.verdict.refuted === false)
const mortos = testados.filter(t => t.verdict && t.verdict.refuted === true)
log(`Grupo ${GRUPO.key}: ${vivos.length} cruzamentos sobreviveram, ${mortos.length} refutados`)

return {
  grupo: GRUPO.key,
  culturas: GRUPO.culturas,
  propostos: props.length,
  sobreviveram: vivos.length,
  refutados: mortos.length,
  cruzamentos: vivos.map(v => ({ ...v.crossing, verificacao: v.verdict })),
  refutados_com_motivo: mortos.map(m => ({ titulo: m.crossing.title, crop: m.crossing.crop, veredito: m.verdict })),
  nao_cruzados: (proposto && proposto.not_crossed) || [],
  notas: proposto && proposto.notes,
}
