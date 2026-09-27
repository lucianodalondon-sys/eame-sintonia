// ALVOS-NOVOS-2 · o filtro de pagina de LISTA, medido sem rede.
//
//     node scripts/capa_materia/medir_filtro_lista.mjs <observations.ndjson da producao>
//
// 1. No livro da producao: quantos dos enderecos ja coletados o filtro recusaria (o risco:
//    perder materias).
// 2. Nos 14 indices guardados pela ALVOS-NOVOS (INDICES-D40-V1.json, sha256 conferido): o que
//    ele recusa hoje, fonte a fonte, e o que o D40 passa a escolher.
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { CONTRACTS } from "../../regras/italy_contracts.mjs";
import { alvosDoContrato, ePaginaDeLista } from "../../regras/motor_de_rota.mjs";
import { memoriaDosDetalhes, decidirSobreDetalhe } from "../../regras/incrementalidade.mjs";

const [LIVRO] = process.argv.slice(2);
const AQUI = new URL(".", import.meta.url);
const bruto = readFileSync(LIVRO);
const linhas = bruto.toString("utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const memoria = memoriaDosDetalhes(linhas);
const agora = new Date().toISOString();

const livroRecusados = [...memoria.keys()].filter(ePaginaDeLista).map((url) => {
  const ult = linhas.filter((l) => l.SOURCE_URL === url).at(-1);
  return { url, SOURCE_ID: ult.SOURCE_ID, ULTIMO_RESULTADO: ult.OBSERVATION_RESULT };
});

const indices = JSON.parse(readFileSync(new URL("INDICES-D40-V1.json", AQUI), "utf8"));
const fontes = [];
for (const f of indices.FONTES.filter((x) => x.ESTADO === "OK")) {
  const buf = readFileSync(f.FICHEIRO);
  if (createHash("sha256").update(buf).digest("hex") !== f.SHA256) throw new Error(`${f.SOURCE_ID}: sha256 mudou`);
  const c = CONTRACTS[f.SOURCE_ID];
  const todos = await alvosDoContrato(f.SOURCE_ID, { ...c, ACQUISITION: { ...c.ACQUISITION, MAX_TARGETS: 1e6 } },
    { buscar: async () => ({ status: 200, buf }) });
  const classificar = (url) => {
    const d = decidirSobreDetalhe(url, { memoria, sourceId: f.SOURCE_ID, contrato: c, agora });
    return d.DECISAO === "SKIP_KNOWN" ? "CONHECIDO" : d.DECISAO === "REVALIDATE" ? "REVISITA" : "NOVO";
  };
  const alvos = await alvosDoContrato(f.SOURCE_ID, c, { buscar: async () => ({ status: 200, buf }), classificar });
  fontes.push({ SOURCE_ID: f.SOURCE_ID, NO_INDICE: todos.length,
    RECUSADOS_COMO_LISTA: todos.map((a) => a.url).filter(ePaginaDeLista),
    ...alvos.D40, ALVOS_D40: alvos.map((a) => a.url),
    NOVOS_NA_CORRIDA: alvos.filter((a) => classificar(a.url) === "NOVO").length });
}
const out = {
  DATASET: "MEDICAO-FILTRO-LISTA-V1", MEDIDO_EM: agora,
  LIVRO: { CAMINHO: LIVRO, SHA256: createHash("sha256").update(bruto).digest("hex"), ENDERECOS: memoria.size,
           RECUSARIA: livroRecusados.length, RECUSADOS: livroRecusados },
  INDICES: { FONTES: fontes, LINKS: fontes.reduce((s, x) => s + x.NO_INDICE, 0),
             RECUSADOS_COMO_LISTA: fontes.reduce((s, x) => s + x.RECUSADOS_COMO_LISTA.length, 0) },
};
writeFileSync(new URL("MEDICAO-FILTRO-LISTA-V1.json", AQUI), JSON.stringify(out, null, 1) + "\n");
console.log("LIVRO: recusaria", livroRecusados.length, "de", memoria.size);
for (const r of livroRecusados) console.log("  ", r.SOURCE_ID, r.ULTIMO_RESULTADO, r.url);
for (const x of fontes) console.log(x.SOURCE_ID.padEnd(11), "indice", x.NO_INDICE, "listas", x.RECUSADOS_COMO_LISTA.length,
  "novos", x.NOVOS, "| corrida novos", x.NOVOS_NA_CORRIDA, x.RECUSADOS_COMO_LISTA.slice(0, 2).join(" "));
console.log("INDICES: links", out.INDICES.LINKS, "recusados como lista", out.INDICES.RECUSADOS_COMO_LISTA);
