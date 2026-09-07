// Gera docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md a partir dos contratos + saude medida.
import { CONTRACTS } from "./italy_contracts.mjs";
import { medir } from "./italy_source_health.mjs";
import { writeFileSync } from "node:fs";

const L = [];
const P = (...s) => L.push(...s);

P("# MATRIZ DE CONTRATOS DE FONTE — ITÁLIA V1", "",
  "**Data:** 2026-09-07 · **Branch:** `claude/italy-source-contracts-v1`", "",
  "Um contrato responde, de forma executável: quem é · onde está · como encontro · o que espero",
  "receber · como sei que é o documento certo · qual a identidade · qual a data · como sei que mudou ·",
  "qual a frequência · o que preservo · como falha · o que a falha significa.", "",
  "Contratos em `regras/italy_contracts.mjs`. Medidor em `regras/italy_source_health.mjs`.", "",
  "Este arquivo é **gerado** por `fontes/italy_write_matrix.mjs`. Não editar à mão.", "",
  "---", "", "## As leis que esta matriz carrega", "", "```",
  "HTTP_200                 ≠  HEALTHY_SOURCE",
  "EMPTY_LIST               ≠  ZERO_DOCUMENTS        (lista vazia FALHA fechada)",
  "SAME_URL                 ≠  SAME_DOCUMENT         (hash novo = observação nova)",
  "DOCUMENT_ID              ≠  BYTE_ID               (identidade semântica ≠ SHA256)",
  "DECLARED_FREQUENCY       ≠  OBSERVED_FREQUENCY",
  "ACCESS_CLASSIFICATION    ≠  ANALYTIC_VERDICT",
  "SOURCE_VERDICT           ≠  SOURCE_HEALTH",
  "AGROCLIMATIC_SIGNAL      ≠  PEST_OCCURRENCE",
  "COMPANY_CLAIM            ≠  REGULATORY_FACT",
  "BROWSER_RENDERED_EXTRACT ≠  RAW_PRESERVED",
  "QUERY_MATCH              ≠  PROVED_TOPIC",
  "ROWS                     ≠  UNIQUE_ORGANIZATIONS",
  "```", "", "---", "", "## A matriz", "");

P("| SOURCE_ID | OWNER | T | VAL | ROTA | SAÍDA | IDENTIDADE | CAMPO DE DATA | FREQ. DECLARADA | FREQ. OBSERVADA | FORWARD | ARQUIVO | AUTOM. | SAÚDE | VEREDITO |",
  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|");

const corta = (s, n = 40) => String(s ?? "—").replace(/\|/g, "/").replace(/\n/g, " ").slice(0, n);
for (const [id, c] of Object.entries(CONTRACTS)) {
  const h = medir(id);
  P(`| \`${id}\` | ${corta(c.OWNER, 24)} | ${c.TERRITORY} | ${c.VALUE} | ${c.ROUTE_TYPE.replace("_ROUTE", "")} | ${c.OUTPUT_TYPE} | ${corta(c.IDENTITY_KEYS?.join(" + "), 38)} | ${corta(c.DOCUMENT_DATE_FIELD, 30)} | ${corta(c.DECLARED_FREQUENCY, 26)} | **${corta(c.OBSERVED_FREQUENCY, 26)}** | ${c.HISTORICAL_OR_FORWARD === "FORWARD_ONLY" ? "**SIM**" : "não"} | ${c.ARCHIVE_REQUIREMENT} | ${String(c.AUTOMATION_FEASIBILITY).split(" ")[0]} | ${h.HEALTH} | ${h.VERDICT} |`);
}

P("", "---", "", "## SE NÃO COLETARMOS HOJE, O QUE DESAPARECE?", "",
  "Três fontes são **`FORWARD_ONLY`**: o documento de hoje some quando chega o de amanhã.",
  "Não é detalhe técnico — é risco de perda irreversível.", "",
  "| fonte | o que se perde | por quê |", "|---|---|---|",
  "| `IT-T3-005` Terre dell'Etruria | a edição semanal inteira, com os **139 pontos** e suas coordenadas | o site mostra uma edição por vez; `/bollettini` devolve **404** |",
  "| `IT-T2-002` ARPAV Veneto | o boletim de cada uma das **32 zonas** | nome de arquivo fixo, conteúdo sobrescrito, sem data na URL |",
  "| `IT-T2-004` SIAS Sicília | a janela de 11 dias por estação | URL fixa, janela móvel; há seção de série histórica **não testada** |",
  "",
  "**Consequência para a coleta futura:** essas três precisam de cadência **pelo menos igual** à de",
  "publicação delas — senão o dado deixa de existir. As outras dez têm arquivo e podem ser buscadas depois.",
  "", "---", "", "## Onde o contrato admite que não sabe", "",
  "- `IT-T3-008` **Puglia** — o nome da cultura é **imagem**, não texto. Pode ser *derivado* da praga",
  "  (`Bactrocera oleae` → olivo), e nesse caso o campo é `CROP_DERIVED`, **nunca** `CROP_EXTRACTED`.",
  "- `IT-T5-002` **FEM OpenPub** — os 188 resultados são o que a **busca casou**: não são 188 evidências",
  "  independentes, nem 188 pesquisadores, nem 188 trabalhos comprovadamente sobre o tema.",
  "- `IT-T9-008` **ADAMA** e `IT-T9-002` **Bayer** — não há caminho honesto para virar `RAW_PRESERVED`",
  "  enquanto o servidor recusar cliente sem navegador. Não forçar.",
  "- **Frequência observada** só foi provada por datas de documento em quatro fontes. Nas demais é",
  "  `NÃO SEI`, mesmo quando o site declara uma cadência — declaração não é medição.",
  "", "---", "", "## Controles negativos", "",
  "Um teste que nunca viu vermelho não é teste. `node regras/italy_source_health.mjs --negativos`",
  "corrompe o documento **em memória** (nunca no disco) e exige que a saúde caia para `FAILED`.", "",
  "```",
  "IT-T2-001  PDF esperado vira HTML de 'Access denied'  (a armadilha do /view do Plone)",
  "IT-T3-010  documento vazio",
  "IT-T3-008  PDF sem nenhum marcador de conteúdo",
  "IT-T4-001  CSV sem a coluna obrigatória",
  "IT-T7-002  planilha sem a coluna CODICE IT",
  "IT-T9-008  extrato de navegador sem data — sem identidade",
  "IT-T3-005  HTML de monitoramento vazio",
  "IT-T1-001  resposta SDMX vazia",
  "```");

writeFileSync("docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md", L.join("\n") + "\n");
console.log("matriz escrita —", L.length, "linhas,", Object.keys(CONTRACTS).length, "contratos");
