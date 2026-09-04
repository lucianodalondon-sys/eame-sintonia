export const meta = {
  name: 'convegno-shard',
  description: 'Um lote de gravacoes de fala cientifica italiana: le cada uma inteira, extrai a relacao completa, passa pela regua e refuta',
  phases: [
    { title: 'Leitura', detail: 'um agente por gravacao, lendo o texto integral' },
    { title: 'Refutacao', detail: 'um cetico por relacao extraida' },
  ],
}

const REPO = '/home/user/eame-sintonia'
const SC = '/tmp/claude-0/-home-user-eame-sintonia/b6cc5475-b0e9-5242-bac3-292cc842a48f/scratchpad'

const FRONTEIRA = `
TRILHA B · INTELIGENCIA. A coleta corre em outro processo e NAO E SUA.
PROIBIDO: escrever em ${SC}/probe/wf3*, mexer em fila, cursor ou paginacao, lancar coleta
nova, reiniciar fan-out, tocar portal/site/Vercel/producao, ou promover achado a canonico.
STATUS_CHANGES = 0 e SCORE_CHANGES = 0, sempre.
Ler e obrigatorio. UMA leitura HTTP para conferir uma fonte que voce vai citar e permitida:
isso e verificacao. Varrer host novo, nao.`

const LEI = `
LEIS DESTA CASA — nao negociaveis:
1. PRESENCA LEXICAL NAO PROVA CONTEXTO AGRONOMICO. Custou caro quatro vezes nesta missao:
   "sentiamo un bel pomodoro forte" era degustacao de AZEITE e virou CROP=POMODORO;
   "grano saraceno" (Fagopyrum) virou FRUMENTO; "l'umidita NOTTURNA" virou NOTTUE; e "pesc"
   no Coldiretti era PESCA (peixe), nao PESCO. LEIA O CONTEXTO de cada casamento.
2. CULTURA CITADA != SINAL DE CAMPO. Sinal e cultura + alvo + lugar + tempo + direcao.
3. NAO ASSOCIE POR PROXIMIDADE TEXTUAL. Num audio de 3 horas, o alvo do minuto 12 e a regiao
   do minuto 148 NAO estao ligados por estarem no mesmo arquivo. Cada eixo precisa da SUA
   evidencia, e voce declara qual — e o que nao ligou, voce declara que nao ligou.
4. O PAPEL DE QUEM FALA NUNCA SAI DO CONTEUDO. Num convegno cada bloco tem um relator
   diferente: diga QUEM esta falando naquele trecho, com o nome que a propria fala declara.
   SOURCE_LOCATION nunca vira FACT_LOCATION.
5. UMA VOZ NAO E UMA TENDENCIA. Convergencia se chama CLUSTER NELLE FONTI MONITORATE.
6. PORTFOLIO RELATION != LABEL AUTHORIZATION. 51 produtos comerciais != 163 registros no
   Ministero != 56 agrofarmaci que o Fitogest atribui a ADAMA.
7. MOLECULA MARCADA != MOLECULA ADAMA. Confira SEMPRE contra as 53 de activeIngredients.json.
   NAO estao la, entre outras: acetamiprid, spinosad, deltametrina, mancozeb, pyraclostrobin,
   propanil, bentazone, clomazone, cycloxydim, etofenprox, rame, zolfo, fosmet, metribuzin.
8. AUSENCIA NA NOSSA LEITURA != AUSENCIA NO MUNDO. A leitura de rotulo cobre 102 dos 163
   registros. Nao achou o par? Diga que NAO ACHAMOS.
9. TRANSCRICAO AUTOMATICA ERRA. Estas falas sao YOUTUBE_ASR_AUTO: nomes proprios e nomes de
   molecula vem deformados ("captano" por captan, "fluxapiroxad" por fluxapyroxad,
   "flu-p-radi furone" por flupyradifurone). Cite o que esta escrito, e diga na citacao
   quando voce esta lendo atraves de um erro evidente de ASR.
10. NAO_SEI e resposta.`

const RADAR = `
RADAR ADAMA ITALIA (pacote canonico V2.1, em ${SC}/v21/*.json):
  culturas por peso de rotulo: BARBABIETOLA 239 · FRUMENTO 176 · MELO 146 · ORZO 131 ·
  MAIS 112 · PATATA 100 · BRASSICACEE 100 · VITE 96 · ERBA_MEDICA 87 · SEGALE 82 ·
  TRITICALE 71 · LEGUMINOSE 70 · CAROTA 63 · CUCURBITACEE 58 · COLZA 56 · FRAGOLA 51 ·
  PESCO 45 · POMODORO 44 · CIPOLLA 42 · GIRASOLE 39 · SOIA 28 · CILIEGIO 27 · TABACCO 26 ·
  AGRUMI 17 · ALBICOCCO 16 · RISO 15 · LATTUGA 11 · PERO 11 · ... · OLIVO 1
  alvo n.1: AFIDI com 436 pares.
  2.030 pares em productRelationships.json. LINK_STRENGTH do mais forte ao mais fraco:
  LINHA_DA_TABELA > BLOCO_DA_CULTURA > DECLARACAO_DE_PRODUTO > SUBSTANCIA_ATIVA.
  53 substancias ativas em activeIngredients.json — entre elas AZOXYSTROBIN, CAPTAN, FOLPET,
  FLUAZINAM, FLUXAPYROXAD, DIFENOCONAZOLE, TEBUCONAZOLE, PROTHIOCONAZOLE, CYMOXANIL,
  METALAXYL-M, FLUDIOXONIL, BUPIRIMATE, FENPROPIDIN, PIRIMICARB, LAMBDA-CYHALOTHRIN,
  TAU-FLUVALINATE, TEFLUTHRIN, GLYPHOSATE, PENDIMETHALIN, MESOTRIONE, SULCOTRIONE,
  METAMITRON, METAZACHLOR, ETHOFUMESATE, PHENMEDIPHAM, TERBUTHYLAZINE, CHLOROTOLURON,
  NICOSULFURON, IMAZAMOX, FLORASULAM, TRIBENURON, MESOSULFURON-METHYL, CLODINAFOP,
  PINOXADEN, CLETHODIM, PROPAQUIZAFOP, QUIZALOFOP-P-ETHYL, DIFLUFENICAN, BIFENOX, DICAMBA,
  FLUROXYPYR, 2,4-D, CHLORANTRANILIPROLE, FLONICAMID, METALDEHYDE, IMAZALIL, FOSETYL-AL.
  regioes das 37 oportunidades: Emilia-Romagna, Veneto, Lombardia, Friuli-Venezia Giulia,
  Piemonte, Puglia, Toscana, Sicilia, Trentino-Alto Adige.
  ASSIMETRIA DECLARADA: OLIVO tem 1 par de rotulo LIDO (MORAINE 018101 x INFESTANTI, um
  HERBICIDA) e 3 oportunidades. A lacuna e de LEITURA, e nao prova ausencia de mercado.`

const ACERVO = `
O ACERVO CONTRA O QUAL VOCE CRUZA — tudo fechado e versionado:
  ${REPO}/data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json
      21 sinais de BOLETIM que ja sobreviveram a refutacao adversarial. E aqui que se procura
      "a fala confirma algo ja visto em fonte escrita".
  ${REPO}/data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json
      421 mencoes de substancia ativa em 14 boletins, com fronteira de palavra
  ${REPO}/data/samples/IT-CAMPO-V1/IT-CIMICE-TRAPPOLE-UNIBO-SERIE.json  177 pontos 2021-2026
  ${REPO}/data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json
      7 cruzamentos JA FEITOS e 7 nao-cruzamentos JA JUSTIFICADOS. LEIA ANTES: repetir um
      deles nao e achado. Dois deles ESFRIAM o caso — e esse e o padrao a imitar.
  ${REPO}/data/samples/IT-CRUZAMENTO-V1/IT-ENRIQUECIMENTO-CONFIRMADAS-V1.json
  ${REPO}/data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json   91 fichas de fonte
  ${REPO}/data/samples/IT-SNAPSHOT-V1/IT-INVENTARIO-FALA-V2.json
      117 objetos de fala, com CROP/ISSUE/REGION/MOLECULE marcados e o EVIDENCE_SPAN de cada
  ${SC}/v21/*.json  o pacote canonico inteiro`

const RELACAO_SCHEMA = {
  type: 'object',
  required: ['object_id', 'what_this_recording_is', 'relations', 'notes'],
  properties: {
    object_id: { type: 'string' },
    what_this_recording_is: { type: 'string' },
    speakers_declared: { type: 'array', items: { type: 'string' } },
    classes: { type: 'array', items: { type: 'string' } },
    relations: {
      type: 'array',
      items: {
        type: 'object',
        required: ['who', 'who_evidence', 'what', 'crop', 'crop_evidence', 'issue',
                   'issue_evidence', 'region', 'region_evidence', 'moment', 'direction',
                   'certainty', 'quote_it', 'adama_relation', 'ruler_verdict', 'axes_not_linked'],
        properties: {
          who: { type: 'string' },
          who_role: { type: 'string' },
          who_evidence: { type: 'string' },
          what: { type: 'string' },
          crop: { type: 'string' },
          crop_evidence: { type: 'string' },
          issue: { type: 'string' },
          issue_evidence: { type: 'string' },
          region: { type: 'string' },
          region_evidence: { type: 'string' },
          moment: { type: 'string' },
          direction: { type: 'string', enum: ['RISING', 'FALLING', 'STABLE', 'PRESENT_NO_TREND', 'ABSENT', 'NAO_SEI'] },
          direction_evidence: { type: 'string' },
          practice: { type: 'string' },
          window_or_stage: { type: 'string' },
          numbers_cited: { type: 'array', items: { type: 'string' } },
          molecules_named_in_speech: { type: 'array', items: { type: 'string' } },
          molecules_that_are_adama: { type: 'array', items: { type: 'string' } },
          molecules_that_are_not_adama: { type: 'array', items: { type: 'string' } },
          certainty: { type: 'string', enum: ['COMPROVADO', 'INFERENCIA', 'HIPOTESE', 'NAO_SEI'] },
          quote_it: { type: 'string' },
          adama_relation: { type: 'string' },
          adama_label_pairs: { type: 'array', items: { type: 'string' } },
          link_strength: { type: 'string' },
          ruler_verdict: { type: 'string', enum: ['CONFIRMED', 'REJECTED', 'UNKNOWN', 'VALIDATION_REQUIRED'] },
          ruler_why: { type: 'string' },
          axes_not_linked: { type: 'string' },
          commercial_direction: { type: 'string', enum: ['OPENS', 'SUPPORTS', 'WEAKENS', 'CONTRADICTS', 'CLOSES', 'NEUTRAL', 'UNKNOWN'] },
        },
      },
    },
    false_lexical_matches: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
}

const REFUTA_SCHEMA = {
  type: 'object',
  required: ['refuted', 'confidence', 'why', 'what_i_checked'],
  properties: {
    refuted: { type: 'boolean' },
    confidence: { type: 'string', enum: ['HIGH', 'MEDIUM', 'LOW'] },
    why: { type: 'string' },
    what_i_checked: { type: 'string' },
    correction: { type: 'string' },
    axis_that_failed: { type: 'string' },
  },
}

// Este workflow e um LOTE. O universo inteiro foi partido em varios lotes que correm ao
// mesmo tempo, porque o teto de concorrencia e por workflow: com 4 nucleos sao 2 agentes
// por workflow, e a maquina fica em 0,10 de carga. Mais workflow, e nao mais agente dentro
// de um, e o que acelera.
const OBJETOS = (args && args.objetos) || []
const LOTE = (args && args.lote) || '?'
if (!OBJETOS.length) throw new Error('lote sem objetos: passe args.objetos')
log(`Lote ${LOTE}: ${OBJETOS.length} gravacoes, ${OBJETOS.reduce((a, o) => a + o.chars, 0)} caracteres`)

phase('Leitura')
const lidos = await pipeline(
  OBJETOS,
  o => agent(`Voce vai LER UMA GRAVACAO INTEIRA de ciencia fitopatologica italiana e extrair
dela a inteligencia que a ADAMA Italia pode usar. E a sua unica gravacao: leia toda.
${FRONTEIRA}
${LEI}
${RADAR}
${ACERVO}

A SUA GRAVACAO
  id       ${o.id}
  titulo   ${o.tit}
  data     ${o.data}
  tamanho  ${o.chars} caracteres de fala
  arquivo  ${REPO}/data/samples/IT-CONVEGNO-V1/falas/${o.id}.json  (campo TRANSCRIPT)
  pista    ${o.pista}

COMO LER 200 MIL CARACTERES SEM MENTIR SOBRE ELES: leia com python3 em blocos, e procure por
termo — cultura, alvo, molecula, regiao, numero, ano. NAO resuma o que voce nao leu. Se voce
cobriu 60% do texto, diga em notes que cobriu 60% e qual parte.

PRIMEIRO: diga o que E esta gravacao (what_this_recording_is) e QUEM fala nela
(speakers_declared) — os nomes que a propria fala declara, nunca inferidos. Num convegno cada
bloco tem relator diferente, e atribuir a fala errada a pessoa errada e o defeito mais caro
que este acervo ja cometeu.

DEPOIS, para cada relacao que a evidencia sustentar:
    QUEM disse (com o papel DECLARADO) · O QUE · QUAL CULTURA · QUAL ALVO · QUAL REGIAO ·
    QUAL MOMENTO · QUAL DIRECAO · COM QUE CERTEZA · e a CITACAO LITERAL em italiano
Cada eixo com a SUA evidencia. Em axes_not_linked diga o que voce NAO conseguiu ligar.

DEPOIS, a REGUA. Confira cada molecula contra ${SC}/v21/activeIngredients.json e cada par
cultura x alvo contra ${SC}/v21/productRelationships.json, com fronteira de palavra. Declare
o LINK_STRENGTH LIDO no arquivo, e nunca um mais forte. Veredito: CONFIRMED, REJECTED,
UNKNOWN ou VALIDATION_REQUIRED, com o porque.

E commercial_direction, que e o que esta casa aprendeu a valorizar: a relacao ABRE, SUSTENTA,
ENFRAQUECE, CONTRADIZ ou FECHA um caso ADAMA? Um achado que FECHA vale tanto quanto um que
abre — dois dos sete cruzamentos ja existentes esfriam o caso, e foi assim que eles ficaram
defensaveis.

DEVOLVA NO MAXIMO 6 RELACOES, e prefira 3 excelentes a 6 razoaveis: cada uma sera atacada por
um cetico na fase seguinte. Zero relacoes tambem e um resultado correto — diga por que.

Registre em false_lexical_matches toda palavra que casou com o vocabulario e NAO significa o
que parece. Isso ensina a regua e vale tanto quanto uma relacao.`,
    { label: `ler:${o.id}`, phase: 'Leitura', schema: RELACAO_SCHEMA }),

  (lido, o) => {
    if (!lido || !lido.relations || !lido.relations.length) return []
    return parallel(lido.relations.slice(0, 6).map(r => () =>
      agent(`Voce e um CETICO. Nao concorde: DERRUBE. Na duvida, cai.
${LEI}

A RELACAO, extraida da gravacao ${o.id} (${o.tit}):
  quem       ${r.who} · papel ${r.who_role || 'NAO_SEI'} · evidencia: ${r.who_evidence}
  o que      ${r.what}
  cultura    ${r.crop}   (evidencia: ${r.crop_evidence})
  alvo       ${r.issue}  (evidencia: ${r.issue_evidence})
  regiao     ${r.region} (evidencia: ${r.region_evidence})
  momento    ${r.moment}
  direcao    ${r.direction} (evidencia: ${r.direction_evidence || 'NAO_SEI'})
  moleculas  na fala: ${(r.molecules_named_in_speech || []).join(', ') || 'nenhuma'}
             ditas ADAMA: ${(r.molecules_that_are_adama || []).join(', ') || 'nenhuma'}
  certeza    ${r.certainty}
  citacao    "${(r.quote_it || '').slice(0, 900)}"
  relacao    ${r.adama_relation}
  pares      ${(r.adama_label_pairs || []).join(' | ') || 'nenhum declarado'}
  forca      ${r.link_strength || 'NAO_SEI'}
  regua      ${r.ruler_verdict} — ${r.ruler_why || ''}
  direcao comercial: ${r.commercial_direction || 'NAO_SEI'}
  eixos nao ligados: ${r.axes_not_linked}

ATAQUE, cada passo com leitura real do arquivo
${REPO}/data/samples/IT-CONVEGNO-V1/falas/${o.id}.json:
1. A CITACAO EXISTE no TRANSCRIPT? Procure. E ASR: aceite grafia deformada, mas a SUBSTANCIA
   precisa estar la. Nao achou -> REFUTADO.
2. CADA EIXO tem evidencia PROPRIA, ou algum foi ligado por proximidade num audio de horas?
   Ligado por proximidade -> REFUTADO, e nomeie o eixo em axis_that_failed.
3. QUEM FALA foi declarado na propria fala, ou foi atribuido ao relator errado do convegno?
   Atribuido -> REFUTADO.
4. A MOLECULA dita ADAMA esta MESMO entre as 53? Confira em
   ${SC}/v21/activeIngredients.json com fronteira de palavra. Rame, zolfo, mancozeb,
   acetamiprid, spinosad, deltametrina, pyraclostrobin, metribuzin NAO estao. Errou -> REFUTADO.
5. O PAR cultura x alvo existe em ${SC}/v21/productRelationships.json, e com a forca
   declarada? Nao existe, ou a forca foi inflada -> REFUTADO.
6. A DIRECAO foi DITA ou deduzida da estacao do ano? Deduzida -> a relacao nao morre, mas a
   direcao vira NAO_SEI: escreva isso em correction.
7. A gravacao e de 2025 ou de 2026? Um bilancio 2024/2025 descreve a campanha PASSADA. Se a
   relacao foi apresentada como situacao CORRENTE, isso e erro de tempo: diga em correction.

refuted=true se qualquer ataque de 1 a 5 derrubar, ou se voce ficar em duvida.`,
        { label: `refuta:${o.id}:${(r.crop || '?').slice(0, 10)}`, phase: 'Refutacao', schema: REFUTA_SCHEMA })
        .then(v => ({ objeto: o.id, relation: r, verdict: v }))))
  },
)

const testadas = lidos.flat().filter(Boolean)
const vivas = testadas.filter(t => t.verdict && t.verdict.refuted === false)
const mortas = testadas.filter(t => t.verdict && t.verdict.refuted === true)
log(`Lote ${LOTE}: ${testadas.length} relacoes testadas · ${vivas.length} sobreviveram · ${mortas.length} refutadas`)

return {
  lote: LOTE,
  gravacoes: OBJETOS.length,
  caracteres: OBJETOS.reduce((a, o) => a + o.chars, 0),
  relacoes_testadas: testadas.length,
  relacoes_vivas: vivas.length,
  relacoes_refutadas: mortas.length,
  vivas: vivas.map(v => ({ objeto: v.objeto, ...v.relation, verificacao: v.verdict })),
  refutadas: mortas.map(m => ({ objeto: m.objeto, crop: m.relation.crop, issue: m.relation.issue, quote_it: m.relation.quote_it, veredito: m.verdict })),
}

