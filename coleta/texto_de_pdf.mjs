// O TEXTO DE UM PDF — UM LEITOR SÓ, PARA O COLETOR E PARA O CANÁRIO DO CURATOR.
//
// D61/D62: a data de emissão e o período de um boletim em PDF vivem no TEXTO do PDF («n. 38/2026 del 21
// settembre 2026 · 14 settembre 2026 - 20 settembre 2026»). O motor (`regras/motor_de_rota.mjs`) tem
// `PDF_TEXT` no vocabulário e NUNCA chama um programa: quem o chama injecta este leitor. Antes, o coletor
// tinha o pdftotext escondido num `switch` por SOURCE_ID e o canário não tinha nenhum — o mesmo boletim
// dava identidade num e rebentava no outro.
//
// pdftotext 4.06 NÃO aceita stdin: grava um temporário, lê, apaga. Falhar (ferramenta ausente, PDF
// partido) devolve "" — texto vazio, que o motor transforma em «NAO SEI» nos campos de data e lugar
// (D62: falta de dado não derruba o documento). Nunca devolve texto inventado.
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";

export function textoDePdf(buf, pasta = tmpdir()) {
  const tmp = join(pasta, `.tmp_${createHash("sha256").update(buf).digest("hex").slice(0, 10)}_${process.pid}.pdf`);
  try {
    mkdirSync(pasta, { recursive: true });
    writeFileSync(tmp, buf);
    return execFileSync("pdftotext", ["-layout", "-enc", "UTF-8", tmp, "-"], { maxBuffer: 64e6, encoding: "utf8" });
  } catch {
    return "";
  } finally {
    rmSync(tmp, { force: true });
  }
}
