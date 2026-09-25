// A IDENTIDADE PELO MOTOR, PARA QUEM NAO E NODE (o canario do Curator, em Python).
//
//     node regras/identidade_do_motor_cli.mjs < pedido.json
//
// UM MOTOR SO: o canario de «a pagina e o boletim» (D42 (2)) nao reimplementa a identidade em
// Python — pergunta a ESTE motor, com os mesmos leitores que o coletor injecta. Pedido (stdin):
//   { "SOURCE_ID", "CONTRATO", "ALVO": {url, nome}, "BYTES_EM": caminho do ficheiro }
// Resposta (stdout, uma linha JSON): a identidade do motor + BOLETIM_CARACTERES (caracteres sem
// espaco do recorte CONTENT_SCOPE, ou do texto todo) — ou { "ERRO": ... } com codigo 2.
import { readFileSync } from "node:fs";
import { identidadeDoContrato, recortar, ContratoInvalido } from "./motor_de_rota.mjs";
import { textoVisivel } from "../coleta/retrato_html.mjs";

const pedido = JSON.parse(readFileSync(0, "utf8"));
const buf = readFileSync(pedido.BYTES_EM);
const leitores = {
  RAW_UTF8: () => buf.toString("utf8"),
  RAW_LATIN1: () => buf.toString("latin1"),
  PAGE_TEXT: () => textoVisivel(buf),
};
try {
  const id = identidadeDoContrato(pedido.SOURCE_ID, pedido.CONTRATO, pedido.ALVO, { leitores }) || {};
  const parte = recortar(textoVisivel(buf), pedido.CONTRATO?.IDENTITY?.CONTENT_SCOPE);
  console.log(JSON.stringify({ ...id, BOLETIM_CARACTERES: parte == null ? 0 : parte.replace(/\s+/g, "").length }));
} catch (e) {
  console.log(JSON.stringify({ ERRO: `${e instanceof ContratoInvalido ? "CONTRATO_INVALIDO" : e.name}: ${e.message}` }));
  process.exit(2);
}
