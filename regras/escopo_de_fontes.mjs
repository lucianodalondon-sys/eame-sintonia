// O PORTAO DE ESCOPO DAS FONTES — o lado Node.
//
//     UMA LEI, UM FICHEIRO DE LEI. DUAS IMPLEMENTACOES LEEM O MESMO FICHEIRO.
//
// Este ficheiro NAO tem uma copia da regra: ele le `regras/ESCOPO-DE-FONTES.json`,
// exactamente o mesmo que `regras/escopo_de_fontes.py` le. Escrever aqui a lista
// dos paises outra vez daria dois donos a mesma lei — e no dia em que alguem
// mudasse um, o outro continuava a autorizar em silencio, que e a pior maneira
// de uma trava se perder.
//
// `tests/test_escopo_de_fontes.py` corre os DOIS lados sobre os MESMOS
// identificadores e reprova se um unico veredito divergir. Uma segunda
// implementacao sem essa prova e uma segunda verdade a espera de acontecer.
//
// E ele existe porque o coletor documental italiano e Node: se a trava vivesse
// so no Python, a rota que realmente vai buscar PDFs a Italia passava por baixo
// dela. Uma trava que nao esta na porta por onde se entra nao e uma trava.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const AQUI = dirname(fileURLToPath(import.meta.url));
const REGISTO = join(AQUI, "ESCOPO-DE-FONTES.json");

export const ITALY_ACTIVE = "ITALY_ACTIVE";
export const SPAIN_FUTURE = "SPAIN_FUTURE";
export const FRANCE_FUTURE = "FRANCE_FUTURE";
export const SHARED_EUROPE_INACTIVE = "SHARED_EUROPE_INACTIVE";
export const UNKNOWN = "UNKNOWN";
export const NAO_SEI = "NAO SEI";

const R = JSON.parse(readFileSync(REGISTO, "utf8"));
export const PAIS_OPERACIONAL_ATIVO = R.PAIS_OPERACIONAL_ATIVO;
const PAISES = R.PAISES;
const ALLOWLIST = Object.fromEntries(
  Object.entries(R.ITALY_ALLOWLIST).filter(([k]) => k !== "NOTA"));

// O mesmo prefixo canonico que o lado Python le. Nunca URL, host, slug ou lingua.
const RE_SOURCE_ID = /^(EU|FR|ES|IT)-T\d{1,2}-\d{2,4}/;

export function paisDe(sourceId) {
  const m = RE_SOURCE_ID.exec(String(sourceId ?? "").trim().toUpperCase());
  return m ? m[1] : NAO_SEI;
}

function grupoDoPais(pais) {
  return PAISES[pais]?.GRUPO ?? UNKNOWN;
}

/** A UNICA pergunta: esta fonte pode ser CHAMADA pela operacao ativa?
 *  Fecha por omissao. UNKNOWN nunca ativa. */
export function veredito(sourceId, { paisDaOperacao = null } = {}) {
  const op = (paisDaOperacao ?? PAIS_OPERACIONAL_ATIVO).toUpperCase();
  const ident = String(sourceId ?? "").trim();
  const pais = paisDe(ident);

  if (pais === NAO_SEI) {
    return { identidade: ident, pais: NAO_SEI, grupo: UNKNOWN, permitido: false,
             italy_use_allowed: NAO_SEI,
             motivo: `SOURCE_ID sem identidade canonica (${JSON.stringify(ident)}) — `
                   + `COUNTRY_SCOPE UNKNOWN. UNKNOWN nao ativa.` };
  }
  const grupo = grupoDoPais(pais);
  if (pais === op) {
    return { identidade: ident, pais, grupo, permitido: true, italy_use_allowed: "YES",
             motivo: `COUNTRY_SCOPE = ${pais} = pais da operacao ativa` };
  }
  const aut = ALLOWLIST[ident.toUpperCase()];
  if (aut && aut.ITALY_USE_ALLOWED === "YES" && op === "IT") {
    return { identidade: ident, pais, grupo: ITALY_ACTIVE, permitido: true,
             italy_use_allowed: "YES",
             motivo: `autorizada explicitamente para a operacao italiana: ${aut.PORQUE ?? ""}` };
  }
  const estado = PAISES[pais]?.STATUS_OPERACIONAL ?? "INACTIVE";
  if (pais === "EU") {
    return { identidade: ident, pais, grupo, permitido: false, italy_use_allowed: "UNKNOWN",
             motivo: `fonte europeia/partilhada sem autorizacao explicita para a operacao `
                   + `${op}. ITALY_USE_ALLOWED = UNKNOWN — e UNKNOWN nao ativa.` };
  }
  return { identidade: ident, pais, grupo, permitido: false, italy_use_allowed: "NO",
           motivo: `COUNTRY_SCOPE = ${pais}, STATUS_OPERACIONAL = ${estado}. Preservada e `
                 + `pesquisavel; fora do caminho operacional ${op}.` };
}

export function permitida(sourceId, opcoes = {}) {
  return veredito(sourceId, opcoes).permitido;
}

/** O PREFLIGHT. Chama-se ANTES da aquisicao — antes da descoberta, nao so antes
 *  do download: descobrir ja e ir a fonte. */
export function exigir(sourceId, opcoes = {}) {
  const v = veredito(sourceId, opcoes);
  if (!v.permitido) {
    const e = new Error(v.motivo);
    e.name = "FonteForaDoEscopo";
    e.veredito = v;
    throw e;
  }
  return v;
}
