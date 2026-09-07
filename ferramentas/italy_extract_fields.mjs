// Extrai os campos de identidade que cada contrato declara, a partir do RAW preservado.
// Prova que a IDENTIDADE SEMANTICA existe e nao depende do SHA.
//   DOCUMENT_ID != BYTE_ID
import { readFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";

const pdf = f => { try { return execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", f, "-"], { maxBuffer: 64e6, encoding: "utf8" }); } catch { return ""; } };
const D = "data/samples/IT-SOURCE-SAMPLES";

console.log("=== APOL (IT-T3-010) — identidade e cadencia\n");
const apol = readdirSync(`${D}/IT-T3-010`).filter(f => f.endsWith(".pdf")).sort();
const apolRegs = [];
for (const f of apol) {
  const t = pdf(`${D}/IT-T3-010/${f}`);
  const per = t.match(/MOSCA DELLE OLIVE\s+(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/);
  const num = f.match(/_n_(\d+)_/);
  const compr = t.match(/COMPRENSORIO\s*-?\s*([A-Z]{2})\s*-\s*([A-Z ]+)/);
  const fen = t.match(/(INGROSSAMENTO FRUTTI|INVAIATURA|MATURAZIONE|ALLEGAGIONE|FIORITURA)/i);
  const nums = (t.match(/\n\s*(\d+)\s+(\d+)\s+(\d+)%\s+(STAZIONARIO|IN AUMENTO|IN DIMINUZIONE)\s+(BASSO|MEDIO|ALTO)/i) || []);
  apolRegs.push({
    RAW_FILE: f, ISSUE_NUMBER: num ? +num[1] : null,
    VALID_FROM: per?.[1] ?? null, VALID_TO: per?.[2] ?? null,
    COMPRENSORIO: compr ? `${compr[1]} - ${compr[2].trim()}` : null,
    PHENOLOGY: fen?.[1] ?? null,
    TRAP_CAPTURES: nums[1] ?? null, PUNTURE: nums[2] ?? null,
    ACTIVE_INFESTATION_PERCENT: nums[3] ? nums[3] + "%" : null,
    TREND: nums[4] ?? null, LEVEL: nums[5] ?? null,
    SOGLIA_CITADA: /soglia/i.test(t)
  });
}
apolRegs.forEach(r => console.log(JSON.stringify(r)));
const d2 = s => { const [a, b, c] = s.split("/").map(Number); return Date.UTC(c, b - 1, a); };
if (apolRegs.length >= 2 && apolRegs.every(r => r.VALID_FROM)) {
  const ds = apolRegs.map(r => d2(r.VALID_FROM)).sort((a, b) => a - b);
  const gaps = ds.slice(1).map((x, i) => (x - ds[i]) / 86400000);
  console.log(`\nintervalos entre VALID_FROM (dias): ${gaps.join(", ")}`);
  console.log(`OBSERVED_FREQUENCY = ${gaps.length && gaps.every(g => g === 7) ? "7D — provado pelas DATAS dos documentos" : "NÃO SEI"}`);
  console.log(`aviso: so ${apolRegs.length} documentos preservados. A pagina lista 9 de 2026 e 14 de 2025, mas contar itens numa lista NAO e provar cadencia.`);
}

console.log("\n=== CAMPANIA (IT-T3-002) — identidade\n");
for (const f of readdirSync(`${D}/IT-T3-002`).filter(f => f.endsWith(".pdf")).sort()) {
  const m = f.match(/^([A-Z]{2})-(\d{2})-(\d{2})\.pdf$/);
  const t = pdf(`${D}/IT-T3-002/${f}`);
  const avv = [...new Set([...t.matchAll(/\(([A-Z][a-z]+ [a-z]+)\)/g)].map(x => x[1]))].slice(0, 6);
  const sost = [...new Set([...t.matchAll(/\b(Etofenprox|Deltametrina|Spinosad|Acetamiprid|Olio bianco|Piretrine|Bacillus thuringiensis)\b/gi)].map(x => x[1]))];
  console.log(JSON.stringify({ RAW_FILE: f, DOCUMENT_ID: m ? `CAMPANIA:${m[1]}:${m[2]}-${m[3]}-2026` : null, PROVINCIA: m?.[1], DATA: m ? `${m[2]}/${m[3]}/2026` : null, avversita_amostra: avv, sostanze_attive: sost, tem_soglia: /soglia/i.test(t) }));
}

console.log("\n=== PUGLIA (IT-T3-008) — a secao fitossanitaria, agora legivel\n");
const pug = pdf(`${D}/IT-T3-008/Notiziario_Agrometeorologico_N36_02-09-2026.pdf`);
console.log(JSON.stringify({
  DOCUMENT_ID: "ARIF:SETTIMANALE:2026:N36",
  numero_e_data: (pug.match(/n\.\s*(\d+)\s+del\s+(\d+\s+\w+\s+\d{4})/) || []).slice(1),
  blocos_Situazione_Fitosanitaria: (pug.match(/Situazione Fitosanitaria/g) || []).length,
  blocos_Situazione_Fenologica: (pug.match(/Situazione Fenologica/g) || []).length,
  blocos_Programma_di_Difesa: (pug.match(/Programma di Difesa/g) || []).length,
  pragas_com_nome_cientifico: [...new Set([...pug.matchAll(/\(([A-Z][a-z]+ [a-z]+)\)/g)].map(x => x[1]))].slice(0, 14),
  sostanze_attive_citadas: [...new Set([...pug.matchAll(/\b(acetamiprid|flupyradifurone|deltametrina|spinosad|cyantraniliprole|pyriproxyfen|Bacillus thuringiensis)\b/gi)].map(x => x[1].toLowerCase()))],
  soglie_citadas: [...new Set([...pug.matchAll(/soglia[^.]{0,80}?(\d+\s*-?\s*\d*\s*%)/gi)].map(x => x[1]))].slice(0, 6),
  CROP_EXTRACTED: false,
  CROP_note: "o nome da cultura e IMAGEM. Pode ser DERIVADO da praga (Bactrocera oleae -> olivo; Plasmopara viticola -> vite), mas isso e CROP_DERIVED, nunca CROP_EXTRACTED."
}, null, 1));

console.log("\n=== TERRE DELL'ETRURIA (IT-T3-005) — identidade do ponto\n");
const pts = JSON.parse(readFileSync("data/samples/ITALY-T3-005-MONITORAGGIO/points-2026-09-07.json", "utf8"));
const comCoord = pts.filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lon));
console.log(JSON.stringify({
  MONITORING_POINTS: pts.length,
  com_coordenada: comCoord.length,
  point_id_unicos: new Set(pts.map(p => p.point_id)).size,
  FACT_LOCATION_RULE: "coordenada do ponto — preferida ao municipio inferido",
  exemplo: comCoord.find(p => p.infestation.includes("Allerta")) || comCoord[1],
  sem_nome: pts.filter(p => !p.name).length,
  datas_distintas: [...new Set(pts.map(p => p.sampling_date))].sort()
}, null, 1));

console.log("\n=== MASAF (IT-T7-002) — linhas x organizacoes\n");
const ods = execFileSync("node", ["ferramentas/ods_peek.mjs", `${D}/IT-T7-002/ELENCO-OP-AOP-al-31-12-2025-agg-08-04-2026.ods`, "100000"], { encoding: "utf8", maxBuffer: 64e6 });
const cel = ods.split(" | ");
const codigos = cel.map(c => c.trim()).filter(c => /^IT\//.test(c));
const aop = codigos.filter(c => c.split("/").length === 4);
const rows = +(ods.match(/linhas de tabela: (\d+)/) || [])[1];
console.log(JSON.stringify({
  RAW_ROWS: rows,
  UNIQUE_ORGANIZATIONS: new Set(codigos).size,
  OP: new Set(codigos).size - aop.length,
  AOP: aop.length,
  duplicados: codigos.length - new Set(codigos).size,
  DUPLICATE_KEY_RULE: "chave = CODICE IT. Casa /^IT\\//. Linha sem CODICE IT nao e organizacao.",
  WHY_DIFFERENT: "as 52 linhas a mais sao cabecalho, titulo do regulamento, linhas de secao por setor e linhas em branco do layout. ROWS != UNIQUE_ORGANIZATIONS — a diferenca fica declarada.",
  CORRECAO_2026_09_07: "eu publiquei 269 e depois 264. AMBOS ERRADOS. O 269 veio de um parse por linha que perdia 3 codigos; o 264 veio de um regex /^IT\\/[A-Z]+\\/\\d+/ que NAO casa os codigos de AOP, que tem QUATRO segmentos (ex.: IT/OLI/AOP/001). O numero certo e 272, com 0 duplicados."
}, null, 1));
