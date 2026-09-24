// LOTE-MICRO · o lote FIXO da micro de prova, escrito ANTES de ir a rede.
//
// Regra do bot Luciano: o lote escolhe-se antes da rede, e a prova tem de
// superar 16,7 % de SIM (3/18 da 1.a onda). Este script NAO vai a rede e NAO
// corre a micro: congela o que a micro vai pedir, com as pecas do coletor,
// para que depois se compare o previsto com o que aconteceu.
//
// Para cada fonte do lote:
//   ALVOS_PREVISTOS  os enderecos que o coletor pediria, pela ordem dele:
//                    alvosDoContrato() sobre a capa JA medida (sha256 na medida)
//                    -> decidirSobreDetalhe() com o livro de hoje
//                    -> cortados pela janela do contrato E pelo teto 5/site
//                       (robots + indice + 3 materias; sem indice: robots + 4)
//   PREVISAO_SIM     a honesta: taxa de SIM do historico da fonte na Sala
//                    (e a regua de hoje sobre os textos ja colhidos), nunca um desejo
//
// Uso: node ferramentas/rendimento/lote_micro.mjs --bot <arvore do bot> --capas C:/rend/indices-lote
//      --curadores a.json,b.json --antes <antes-da-rede.json> --saida LOTE-MICRO-V1.json
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";

const arg = (n, d = null) => { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; };
const BOT = arg("--bot");
const imp = p => import(pathToFileURL(`${BOT}/${p}`).href);
const { CONTRACTS } = await imp("regras/italy_contracts.mjs");
const { alvosDoContrato } = await imp("regras/motor_de_rota.mjs");
const { memoriaDosDetalhes, decidirSobreDetalhe } = await imp("regras/incrementalidade.mjs");
const { CORTESIA_PADRAO } = await imp("coleta/italy_pilot_collect.mjs");
const LIVRO = `${BOT}/data/collection-ledger/italy/observations.ndjson`;
const livroBytes = readFileSync(LIVRO);
const memoria = memoriaDosDetalhes(livroBytes.toString("utf8").split("\n").filter(Boolean).map(JSON.parse));
const curadores = arg("--curadores").split(",").map(p => new Map(JSON.parse(readFileSync(p, "utf8")).FONTES.map(f => [f.SOURCE_ID, f])));
const agora = new Date().toISOString();
const sha = b => createHash("sha256").update(b).digest("hex");

// ── O LOTE, com o porque de cada fonte (decidido antes da rede) ────────────
// Os numeros de historico vem de medidas/sala-por-fonte.json e da regua de hoje
// corrida sem rede sobre os textos ja colhidos (medidas/lote-regua-offline.json).
const LOTE = [
  { SOURCE_ID: "IT-T10-018", PAPEL: "PRINCIPAL", PRECONDICAO: "nenhuma (ELIGIBLE no vivo 55b50a63; esta na coorte da 1.a onda)",
    PORQUE: "unica fonte do portao com materia nova DENTRO da janela (11 novas nas 30 da janela); 19 SIM em 46 textos na Sala (41 %); tem a unica janela de cultura provada num texto (data de colheita da pera Conference)",
    PREVISAO: { DOCUMENTOS: 3, SIM_ESPERADO: 1.2, INTERVALO: "0 a 3", BASE: "3 materias (teto) x 41 % (19/46 na Sala); regua T10 de hoje sobre os 46 textos: 20 SIM" } },
  { SOURCE_ID: "IT-T2-002", PAPEL: "T2_DE_JANELA", PRECONDICAO: "PROMOVER READY_LEGACY -> DETAIL/v1 (revalidar no Curator). NAO e a R1. Sem isto o portao recusa-a e ela CONTA COMO NAO_CORREU, nao como 0 SIM",
    PORQUE: "a unica T2 de janela que o coletor sabe colher (boletim Agrometeo...informa por zona: fenologia, difesa integrata, evapotraspirazione); a regua T2 instalada da SIM a 4 de 4 textos ja colhidos; ARPAE agrometeo (IT-T2-001) tambem da SIM mas o coletor nao tem rota para ela",
    PREVISAO: { DOCUMENTOS: 4, SIM_ESPERADO: 2.8, INTERVALO: "0 a 4", BASE: "4 zonas (robots + 4 = teto 5); 4/4 SIM na regua de hoje; P(edicao nova desde 18/09) ~0,7: 3 visitas anteriores (07, 14, 18/09) viram versao nova todas, mas a data da edicao nao se le na capa (JavaScript)" } },
  { SOURCE_ID: "IT-T7-041", PAPEL: "R1", PRECONDICAO: "R1 instalada (o contrato ja esta na tabela do coletor)",
    PORQUE: "a unica da R1 com varias materias novas na janela (7 novas, 7 na janela; teto 3); T7 tem regua",
    PREVISAO: { DOCUMENTOS: 3, SIM_ESPERADO: 0.4, INTERVALO: "0 a 1", BASE: "1 texto na Sala, 1 SIM antigo mas a regua de hoje diz NAO_SEI; os titulos da janela sao semana da bonifica, eventos, avisos ANAC/concursos: institucional" } },
];
// Fica FORA de proposito (decidido antes da rede):
const FORA = [
  { SOURCE_ID: "IT-T7-141", PORQUE: "o unico endereco da janela (MAX_TARGETS 1) e uma LISTAGEM («comunicati-stampa-2026/»), nao uma materia: o gate de detalhe tende a recusa-la; 0 textos na Sala" },
  { SOURCE_ID: "IT-T2-051", PORQUE: "T2 pronta, mas o endereco da janela e «30 anni per l'ambiente»: sem ligacao agricola a regua T2 da NAO_SEI; o historico da 1 NAO em 1" },
  { SOURCE_ID: "IT-T2-034", PORQUE: "T2 pronta, 0 novas na janela (o 1.o link ja esta no livro); historico 1 NAO em 1" },
  { SOURCE_ID: "IT-T7-031", PORQUE: "R1, 1 materia na janela (projecto europeu); historico 1 NAO em 1 — baixaria a taxa" },
  { SOURCE_ID: "IT-T2-032/033/037/050/063/070", PORQUE: "T2 da R1 SEM contrato no coletor (so no curador) e com endereco da janela sem ligacao agricola (polen, campos electromagneticos, aguas subterraneas, laboratorios)" },
];

function contratoDe(id) {
  if (CONTRACTS[id]) return { c: CONTRACTS[id], ORIGEM: "COLETOR" };
  for (const m of curadores) if (m.get(id)?.ACQUISITION) return { c: m.get(id), ORIGEM: "CURADOR" };
  return { c: null, ORIGEM: "NENHUM" };
}

const linhas = [];
for (const f of LOTE) {
  const { c, ORIGEM } = contratoDe(f.SOURCE_ID);
  const aq = c?.ACQUISITION;
  let alvos = [], capa = null, teto;
  if (aq?.STRATEGY === "HTML_LINK_DISCOVERY") {
    const p = `${arg("--capas")}/${f.SOURCE_ID}.html`;
    const buf = readFileSync(p);
    capa = { CAMINHO: p, SHA256: sha(buf), BYTES: buf.length };
    const t = await alvosDoContrato(f.SOURCE_ID, c, { buscar: async () => ({ status: 200, buf }) });
    alvos = t.erro ? [] : t.map(a => a.url);
    teto = CORTESIA_PADRAO.TETO_POR_HOST - 2;            // robots + indice
  } else if (f.SOURCE_ID === "IT-T2-002") {
    // o `case` do coletor sem __ARPAV_TODAS: as 4 zonas do piloto; sem indice
    alvos = [1, 9, 16, 24].map(n => `https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_${String(n).padStart(2, "0")}.pdf`);
    teto = CORTESIA_PADRAO.TETO_POR_HOST - 1;            // so robots
  }
  const decididos = alvos.map(u => ({ URL: u, DECISAO: decidirSobreDetalhe(u, { memoria, sourceId: f.SOURCE_ID, contrato: c, agora }).DECISAO }));
  const vai = decididos.filter(d => d.DECISAO !== "SKIP_KNOWN").slice(0, teto);
  linhas.push({ ...f, CONTRATO: ORIGEM, CAPA_MEDIDA: capa, ALVOS_PREVISTOS: vai, ALVOS_NO_INDICE: decididos.length,
                MAX_TARGETS: aq?.MAX_TARGETS ?? null, TETO_DE_MATERIAS_POR_CORRIDA: teto });
}

const antes = JSON.parse(readFileSync(arg("--antes"), "utf8"));
const docs = LOTE.reduce((s, f) => s + f.PREVISAO.DOCUMENTOS, 0);
const esp = LOTE.reduce((s, f) => s + f.PREVISAO.SIM_ESPERADO, 0);
const semArpav = LOTE.filter(f => f.SOURCE_ID !== "IT-T2-002");
const docsA = semArpav.reduce((s, f) => s + f.PREVISAO.DOCUMENTOS, 0), espA = semArpav.reduce((s, f) => s + f.PREVISAO.SIM_ESPERADO, 0);
const d = {
  DATASET: "LOTE-MICRO-V1", ESCRITO_EM: agora, ESCRITO_ANTES_DA_REDE: true,
  REGRA: "lote FIXO escolhido antes da rede (bot Luciano); superar 16,7 % de SIM (3 SIM / 18 fontes da 1.a onda); NAO se corre aqui — o coordenador corre depois de instalar a R1",
  COMO_CONTAR: "taxa = SIM / documentos novos admitidos a Admissao nesta micro; fonte cuja PRECONDICAO falhou conta como NAO_CORREU (fora do denominador), decidido agora e nao depois",
  LOTE: linhas, FORA,
  PREVISAO_TOTAL: {
    COM_ARPAV: { DOCUMENTOS: docs, SIM_ESPERADO: +esp.toFixed(1), TAXA: `${(100 * esp / docs).toFixed(0)} %` },
    SEM_ARPAV_SE_A_PRECONDICAO_FALHAR: { DOCUMENTOS: docsA, SIM_ESPERADO: +espA.toFixed(1), TAXA: `${(100 * espA / docsA).toFixed(0)} %` },
    ALVO: "> 16,7 %",
    RESSALVA: "estimativa de balcao a partir de 1-46 textos por fonte; o intervalo real e largo (0 SIM e possivel)" },
  ANTES_DA_REDE: { ...antes, LIVRO_DO_COLETOR: { CAMINHO: LIVRO, SHA256: sha(livroBytes), LINHAS: livroBytes.toString("utf8").split("\n").filter(Boolean).length } },
};
writeFileSync(arg("--saida"), JSON.stringify(d, null, 1) + "\n");
console.log(JSON.stringify(d.PREVISAO_TOTAL, null, 1));
for (const l of linhas) console.log(l.SOURCE_ID, l.CONTRATO, l.ALVOS_PREVISTOS.length, "alvos:", l.ALVOS_PREVISTOS.map(a => a.URL.split("/").pop() || a.URL).join(" | ").slice(0, 200));
