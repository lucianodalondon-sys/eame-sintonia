// ALVOS-NOVOS · medicao offline: quantos alvos NOVOS cada indice anuncia hoje, contra o livro da
// producao, e quantos documentos novos uma corrida teria com D40 + teto D38 por dominio.
//
//     node scripts/capa_materia/medir_d40.mjs <pasta-dos-indices> <observations.ndjson da producao>
//
// Zero rede: `buscar` devolve o indice guardado por buscar_indices_d40.py. O resto e o codigo que
// o coletor corre (alvosDoContrato + memoriaDosDetalhes + decidirSobreDetalhe), nao uma copia dele.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { CONTRACTS } from "../../regras/italy_contracts.mjs";
import { alvosDoContrato } from "../../regras/motor_de_rota.mjs";
import { memoriaDosDetalhes, decidirSobreDetalhe } from "../../regras/incrementalidade.mjs";

const [PASTA, LIVRO] = process.argv.slice(2);
const AQUI = new URL(".", import.meta.url);
const indices = JSON.parse(readFileSync(new URL("INDICES-D40-V1.json", AQUI), "utf8"));
const bruto = readFileSync(LIVRO);
const memoria = memoriaDosDetalhes(bruto.toString("utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l)));
const agora = new Date().toISOString();

// D38 como a ONDA2-G3 o define: 5 pedidos por dominio registavel por corrida, robots incluido.
const TETO_POR_DOMINIO = 5;
const gasto = new Map();
const fontes = [];
for (const f of indices.FONTES) {
  const sid = f.SOURCE_ID, c = CONTRACTS[sid];
  const linha = { SOURCE_ID: sid, DOMINIO: f.DOMINIO, MAX_TARGETS_DO_CONTRATO: c.ACQUISITION.MAX_TARGETS ?? null };
  // teto: robots (1, so a 1.a fonte do dominio) + indice (1) + materias
  const antes = gasto.get(f.DOMINIO) ?? 0;
  const robots = antes === 0 ? 1 : 0;
  const livreParaIndice = TETO_POR_DOMINIO - antes - robots;
  if (livreParaIndice < 1) {
    linha.D38 = "DEFERRED_BY_COURTESY — o dominio ja gastou os 5 pedidos nesta corrida";
    linha.DOCUMENTOS_NOVOS_NA_CORRIDA = 0;
  }
  if (f.ESTADO !== "OK") {
    linha.MEDIDO = "NAO_MEDIDO";
    linha.PORQUE = f.PORQUE || "indice nao obtido";
    fontes.push(linha);
    if (!linha.D38) {
      // o indice custaria 1 pedido na corrida real; o que ele anuncia nao se sabe
      gasto.set(f.DOMINIO, antes + robots + 1);
      linha.D38 = `o indice cabe (pedido ${antes + robots + 1} de 5); as materias: NAO SEI`;
      linha.DOCUMENTOS_NOVOS_NA_CORRIDA = "NAO_SEI";
    }
    continue;
  }
  const buf = readFileSync(f.FICHEIRO);
  if (createHash("sha256").update(buf).digest("hex") !== f.SHA256) throw new Error(`${sid}: sha256 do indice mudou`);
  const classificar = (url) => {
    const d = decidirSobreDetalhe(url, { memoria, sourceId: sid, contrato: c, agora });
    return d.DECISAO === "SKIP_KNOWN" ? "CONHECIDO" : d.DECISAO === "REVALIDATE" ? "REVISITA" : "NOVO";
  };
  const alvos = await alvosDoContrato(sid, c, { buscar: async () => ({ status: 200, buf }), classificar });
  if (alvos.erro) { linha.MEDIDO = "ERRO"; linha.ERRO = alvos.erro; fontes.push(linha); continue; }
  Object.assign(linha, { MEDIDO: "OK", ...alvos.D40, ALVOS_D40: alvos.map((a) => a.url) });
  // o que a 1.a onda fazia: o 1.o do indice (MAX_TARGETS), conhecido ou nao
  const semD40 = await alvosDoContrato(sid, c, { buscar: async () => ({ status: 200, buf }) });
  linha.SEM_D40_ALVOS = semD40.map((a) => a.url);
  linha.SEM_D40_NOVOS = semD40.filter((a) => classificar(a.url) === "NOVO").length;
  if (!linha.D38) {
    const livreParaMaterias = TETO_POR_DOMINIO - antes - robots - 1;
    const materias = Math.min(alvos.length, livreParaMaterias);
    gasto.set(f.DOMINIO, antes + robots + 1 + materias);
    linha.PEDIDOS_DE_MATERIA = materias;
    linha.CORTADOS_PELO_D38 = alvos.length - materias;
    linha.DOCUMENTOS_NOVOS_NA_CORRIDA = alvos.slice(0, materias).filter((a) => classificar(a.url) === "NOVO").length;
    linha.REVISITAS_NA_CORRIDA = materias - linha.DOCUMENTOS_NOVOS_NA_CORRIDA;
    // a comparacao justa: o jeito antigo (1.o do indice, MAX_TARGETS) com o MESMO teto D38
    linha.SEM_D40_COM_D38_NOVOS = semD40.slice(0, livreParaMaterias).filter((a) => classificar(a.url) === "NOVO").length;
  }
  fontes.push(linha);
}
const soma = (k) => fontes.reduce((s, x) => s + (typeof x[k] === "number" ? x[k] : 0), 0);
const out = {
  DATASET: "MEDICAO-D40-V1", MEDIDO_EM: agora,
  LIVRO: { CAMINHO: LIVRO, SHA256: createHash("sha256").update(bruto).digest("hex"), ENDERECOS_CONHECIDOS: memoria.size },
  INDICES: "INDICES-D40-V1.json (sha256 de cada indice la dentro; os ficheiros ficam fora do Git)",
  TETO_POR_DOMINIO, FONTES: fontes,
  TOTAL: {
    FONTES: fontes.length,
    MEDIDAS: fontes.filter((x) => x.MEDIDO === "OK").length,
    ALVOS_NOVOS_NOS_INDICES: soma("NOVOS"),
    FONTES_COM_PELO_MENOS_1_NOVO: fontes.filter((x) => x.NOVOS > 0).length,
    FONTES_VAZIO_HONESTO: fontes.filter((x) => x.VAZIO_HONESTO === true).length,
    DOCUMENTOS_NOVOS_POR_CORRIDA_D40_D38: soma("DOCUMENTOS_NOVOS_NA_CORRIDA"),
    DOCUMENTOS_NOVOS_POR_CORRIDA_SEM_D40: soma("SEM_D40_NOVOS"),
    DOCUMENTOS_NOVOS_POR_CORRIDA_SEM_D40_COM_D38: soma("SEM_D40_COM_D38_NOVOS"),
    FONTES_COM_DOCUMENTO_NOVO_D40_D38: fontes.filter((x) => x.DOCUMENTOS_NOVOS_NA_CORRIDA > 0).length,
    NAO_SEI: fontes.filter((x) => x.DOCUMENTOS_NOVOS_NA_CORRIDA === "NAO_SEI").map((x) => x.SOURCE_ID),
  },
};
writeFileSync(new URL("MEDICAO-D40-V1.json", AQUI), JSON.stringify(out, null, 1) + "\n");
for (const x of fontes) console.log(x.SOURCE_ID.padEnd(11), x.DOMINIO.padEnd(28), String(x.MEDIDO).padEnd(10),
  "indice", x.NO_INDICE ?? "-", "conhecidos", x.CONHECIDOS_SALTADOS ?? "-", "novos", x.NOVOS ?? "-",
  "revisitas", x.REVISITAS ?? "-", "| corrida:", x.DOCUMENTOS_NOVOS_NA_CORRIDA, "| sem D40:", x.SEM_D40_NOVOS ?? "-", x.D38 ? "| " + x.D38 : "");
console.log(JSON.stringify(out.TOTAL));
