// FIXTURE — O COMPORTAMENTO LEGADO, CONGELADO, DOS 7 `case` DO PILOTO
//
// Copiado VERBATIM de `coleta/italy_pilot_collect.mjs` @ 380bf090 (HEAD do
// cutover antes de remover o `switch`): os 7 `case` de `alvosDe()` e os 7 de
// `identidade()`. Serve a UMA prova — `regras/cutover_equivalencia_test.mjs`
// — que compara, alvo a alvo e ficheiro a ficheiro, o que o `switch` fazia
// com o que o contrato faz agora.
//
//     LEGACY_BEHAVIOR_CAPTURED = YES  é ISTO, e não uma frase num relatório.
//
// ⚠️ ESTE FICHEIRO NÃO É CÓDIGO DE PRODUÇÃO E NÃO EVOLUI. Se um dia a prova
// deixar de fazer sentido, apaga-se a prova e a fixture juntas. Corrigir aqui
// um comportamento legado seria reescrever a régua com que se mede.
//
// As ÚNICAS diferenças em relação ao original, todas de injecção para a
// prova correr sem rede e com relógio fixo:
//   · `baixar` entra por parâmetro (era o `baixar` do módulo);
//   · `globalThis.__ARPAV_TODAS` entra como `arpavTodas`;
//   · `new Date()` do fallback de IT-T3-008 entra como `agora()`;
//   · o `t()` do pdftotext entra como `pdfTexto()`.

export async function alvosDeLegado(sourceId, c, { baixar, arpavTodas = false, agora = () => new Date() }) {
  switch (sourceId) {
    case "IT-T3-005":
      return [{ url: c.CANONICAL_ENTRY_URL, nome: "monitoraggio.html" }];
    case "IT-T2-002":
      // No piloto medimos 4. Na operacao forward-only medimos as 29 publicadas.
      // As zonas 17, 18 e 19 devolvem 404 consistente: o site nao as publica. Fato da fonte.
      const zonas = arpavTodas
        ? Array.from({ length: 32 }, (_, i) => i + 1).filter(n => ![17, 18, 19].includes(n))
        : [1, 9, 16, 24];
      return zonas.map(n => ({ url: `https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_${String(n).padStart(2, "0")}.pdf`, nome: `agro_${String(n).padStart(2, "0")}.pdf`, zone: n }));
    case "IT-T2-004":
      return [{ url: "http://www.sias.regione.sicilia.it/NHEOWL0530_00.html", nome: "NHEOWL0530_00.html", table: "PRECIPITAZIONE_GIORNALIERA" }];
    case "IT-T3-010": {
      const idx = await baixar("http://www.apol.it");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const html = idx.buf.toString("latin1");
      const links = [...html.matchAll(/href="([^"]*Bollettino_Mosca[^"]*\.pdf)"/gi)].map(m => new URL(m[1], "http://www.apol.it").href);
      if (links.length === 0) return { erro: "EMPTY_LIST — o indice nao listou nenhum boletim. Isto e FAILED, nao zero documentos." };
      const atual = links[0];
      return [{ url: atual, nome: atual.split("/").pop() }];
    }
    case "IT-T3-002": {
      const idx = await baixar("https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/SA_2026.html");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      // os href do indice sao RELATIVOS ("pdf/SA-02-09.pdf"), nao absolutos — resolver contra a pagina
      const base = "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/";
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*SA-\d{2}-\d{2}\.pdf)"/gi)].map(m => new URL(m[1], base).href);
      if (links.length === 0) return { erro: "EMPTY_LIST — indice sem boletins. FAILED." };
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T3-008": {
      const idx = await baixar("https://www.agrometeopuglia.it/bollettini");
      if (idx.erro || idx.status !== 200) return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
      const links = [...idx.buf.toString("latin1").matchAll(/href="([^"]*Notiziario_Agrometeorologico_N\d+_[\d-]+\.pdf)"/gi)].map(m => new URL(m[1], "https://www.agrometeopuglia.it").href);
      if (links.length === 0) {
        // ACHADO: o indice de agrometeopuglia.it e renderizado por JavaScript — o curl nao ve os links.
        // Isto NAO e lista vazia da fonte: e limite do nosso instrumento. Por isso NAO e EMPTY_LIST/FAILED.
        // Caimos para a ROTA PREVISIVEL que o contrato ja documenta, procurando a edicao corrente
        // para tras a partir de hoje. A descoberta fica marcada como degradada, e o motivo vai no ledger.
        const hoje = agora();
        for (let volta = 0; volta < 10; volta++) {
          const d = new Date(hoje.getTime() - volta * 864e5);
          const dd = String(d.getUTCDate()).padStart(2, "0"), mm = String(d.getUTCMonth() + 1).padStart(2, "0"), aa = d.getUTCFullYear();
          // o numero da semana nao e adivinhavel: varremos os numeros plausiveis da temporada
          for (const n of [37, 36, 35]) {
            const u = `https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/${aa}/Notiziario_Agrometeorologico_N${n}_${dd}-${mm}-${aa}.pdf`;
            const t = await baixar(u, 1);
            if (!t.erro && t.status === 200 && t.buf?.length > 100000 && t.buf.subarray(0,4).toString("latin1") === "%PDF")
              return [{ url: u, nome: u.split("/").pop(), descoberta_degradada: "INDEX_REQUIRES_BROWSER — indice e JavaScript; caiu para a rota previsivel do contrato" }];
          }
        }
        return { erro: "indice exige navegador E a rota previsivel nao achou edicao nos ultimos 10 dias" };
      }
      return [{ url: links[0], nome: links[0].split("/").pop() }];
    }
    case "IT-T4-001": {
      const idx = await baixar("https://www.dati.salute.gov.it/it/dataset/fitosanitari/");
      if (idx.erro || idx.status !== 200) return { erro: `pagina inacessivel: ${idx.erro || idx.status}` };
      const m = idx.buf.toString("latin1").match(/opendata\/(PROD_FTS_6_(\d{8})\.csv)/);
      if (!m) return { erro: "EMPTY_LIST — nenhuma versao de CSV anunciada na pagina. FAILED." };
      return [{ url: `https://www.dati.salute.gov.it/sites/default/files/opendata/${m[1]}`, nome: m[1], sourceVersion: m[2] }];
    }
  }
  return { erro: "fonte sem alvo definido no piloto" };
}

export function identidadeLegada(sourceId, alvo, buf, { pdfTexto = () => "" } = {}) {
  const t = pdfTexto;
  switch (sourceId) {
    case "IT-T3-005": {
      const h = buf.toString("utf8");
      const p = h.match(/Bollettino del periodo dal\s*([\d-]+)\s*al\s*([\d-]+)/);
      const br = s => s ? s.split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: p ? `TERRETRURIA:${p[1]}:${p[2]}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: br(p?.[2]), FACT_TIME: "por ponto — cada ponto traz sua propria data de campionamento" };
    }
    case "IT-T2-002": {
      const s = buf.toString("latin1");
      const g = (s.match(/\/CreationDate\s*\(D:(\d{14})/) || [])[1];
      const iso = g ? `${g.slice(0, 4)}-${g.slice(4, 6)}-${g.slice(6, 8)}` : null;
      return { DOCUMENT_ID: g ? `ARPAV:Z${String(alvo.zone).padStart(2, "0")}:${g}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao" };
    }
    case "IT-T2-004": {
      const h = buf.toString("latin1");
      const w = h.match(/dal\s*(\d{2}\/\d{2}\/\d{4})\s*al\s*(\d{2}\/\d{2}\/\d{4})/);
      const iso = w ? w[2].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: w ? `SIAS:${alvo.table}:WINDOW_END_${iso}` : null, SOURCE_DATE: w ? `${w[1]} a ${w[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "por linha — cada celula tem sua propria data" };
    }
    case "IT-T3-002": {
      const m = alvo.nome.match(/^([A-Z]{2})-(\d{2})-(\d{2})\.pdf$/);
      const iso = m ? `2026-${m[3]}-${m[2]}` : null;
      return { DOCUMENT_ID: m ? `CAMPANIA:${m[1]}:${m[2]}-${m[3]}-2026` : null, SOURCE_DATE: m ? `${m[2]}/${m[3]}/2026` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o boletim nao data a observacao de campo" };
    }
    case "IT-T3-010": {
      const txt = t();
      const p = txt.match(/MOSCA DELLE OLIVE\s+(\d{2}\/\d{2}\/\d{4})\s*-\s*(\d{2}\/\d{2}\/\d{4})/);
      const n = alvo.nome.match(/_n_(\d+)_/);
      const compr = (txt.match(/COMPRENSORIO\s*-?\s*([A-Z]{2})\s*-\s*([A-Z ]+)/) || []);
      const iso = p ? p[1].split("/").reverse().join("-") : null;
      return { DOCUMENT_ID: n && p ? `APOL:${p[1].slice(-4)}:N${n[1]}:${(compr[1] || "?") + "-" + (compr[2] || "?").trim()}` : null, SOURCE_DATE: p ? `${p[1]} a ${p[2]}` : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o periodo e de validade, nao de observacao" };
    }
    case "IT-T3-008": {
      const n = alvo.nome.match(/_N(\d+)_([\d-]+)\.pdf/);
      const iso = n ? n[2].split("-").reverse().join("-") : null;
      return { DOCUMENT_ID: n ? `ARIF:SETTIMANALE:${iso?.slice(0, 4)}:N${n[1]}` : null, SOURCE_DATE: n ? n[2] : null, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN" };
    }
    case "IT-T4-001": {
      const v = alvo.sourceVersion;
      const iso = v ? `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}` : null;
      return { DOCUMENT_ID: v ? `MINSALUTE:FTS6:${v}` : null, SOURCE_DATE: iso, SOURCE_DATE_ISO: iso, FACT_TIME: "UNKNOWN — o CSV traz datas de registro por linha, nao uma data de fato do arquivo" };
    }
  }
  return { DOCUMENT_ID: null };
}

export const LEGADO_HEAD = "380bf090";
export const LEGADO_FONTES = ["IT-T3-005", "IT-T2-002", "IT-T2-004", "IT-T3-002", "IT-T3-010", "IT-T3-008", "IT-T4-001"];
