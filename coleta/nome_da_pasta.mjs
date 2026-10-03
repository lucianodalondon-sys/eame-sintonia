// O NOME FISICO DA PASTA DE UM DOCUMENTO — FECHAR-ONDA2-B (D60 c).
//
// ⚠️ MEDIDO NA 2.a ONDA (25/09/2026). A IT-T2-050 (ARPA Campania) rebentou em
// `guardarRaw` (`coleta/italy_pilot_collect.mjs`): a identidade generica pelo
// endereco (`<SID>:URL:{caminho}`, `regras/italy_contracts.mjs`) leva o endereco
// inteiro — `...-2026?redirect=%2F` — e o coletor fazia do DOCUMENT_ID o nome da
// pasta trocando so `: / \`. O Windows recusa `?` (e `* " < > |`): mkdir ENOENT.
//
//     O DOCUMENT_ID E A IDENTIDADE. O NOME DA PASTA E SO UM ENDERECO NO DISCO.
//     MUDAR O SEGUNDO NAO PODE MEXER NO PRIMEIRO.
//
// Por isso este modulo NAO apaga caracter nenhum do DOCUMENT_ID, e o livro
// continua a guardar a identidade inteira. So o nome FISICO muda, e so quando
// o nome de sempre nao pode existir no disco:
//
//   1  o nome de sempre (`: / \` -> `_`) serve se nao tiver caracter proibido
//      e couber num nome de pasta (255 bytes). Nesse caso NADA muda: as pastas
//      que ja existem continuam a ser as mesmas.
//   2  senao, percent-encoding REVERSIVEL dos caracteres proibidos (e do
//      proprio `%`, para a volta ser unica) + `~` + 12 hex do sha256 do
//      DOCUMENT_ID inteiro. O hash separa dois DOCUMENT_ID que so diferem em
//      `:` vs `/` (o nome de sempre ja os juntava) e marca o nome como novo.
//   3  nome codificado comprido demais: corta-se o prefixo legivel e fica o
//      hash, que e estavel. A volta ja nao e possivel pelo nome, e nao precisa:
//      a identidade inteira esta no livro, ao lado do RAW_PATH.
//
// COMPATIBILIDADE: `pastaDoDocumento` procura primeiro a pasta de sempre. Uma
// pasta antiga com `?` so pode existir num sistema que a aceite (Linux); ai
// continua a ser encontrada, e nao se cria uma segunda para o mesmo documento.
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";

// Os proibidos do Windows num nome de ficheiro, alem de `: / \` (que o nome de
// sempre ja trocava), mais os caracteres de controlo.
export const PROIBIDOS = /[*?"<>|\x00-\x1f]/;
const A_CODIFICAR = /[%*?"<>|\x00-\x1f]/g;
// 255 e o limite de UM nome de pasta no NTFS (UTF-16) e no ext4 (bytes).
export const LIMITE_DO_NOME = 255;
// O nome novo fica bem abaixo do limite: o caminho inteiro ainda leva a raiz,
// a fonte, a versao e o ficheiro.
export const LIMITE_DO_NOME_NOVO = 150;
const HASH = 12;

const bytes = (s) => Buffer.byteLength(s, "utf8");

export function nomeDeSempre(documentId) {
  return String(documentId).replace(/[:\/\\]/g, "_");
}

export function nomeDeSempreServe(documentId) {
  const n = nomeDeSempre(documentId);
  return !PROIBIDOS.test(n) && bytes(n) <= LIMITE_DO_NOME && n.length > 0;
}

export function nomeDaPasta(documentId) {
  const id = String(documentId);
  if (nomeDeSempreServe(id)) return nomeDeSempre(id);
  const h = createHash("sha256").update(id, "utf8").digest("hex").slice(0, HASH);
  let cod = nomeDeSempre(id).replace(A_CODIFICAR,
    (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, "0"));
  const cabe = LIMITE_DO_NOME_NOVO - 1 - HASH;
  if (bytes(cod) > cabe) {
    // Corta-se por caracter e nunca a meio de um `%XX` nem de um caracter UTF-8.
    let corte = "";
    for (const c of cod) {
      if (bytes(corte + c) > cabe) break;
      corte += c;
    }
    cod = corte.replace(/%[0-9A-F]?$/, "");
  }
  return `${cod}~${h}`;
}

// A volta do percent-encoding: devolve o nome de sempre (`: / \` ja eram `_`).
// So vale para nomes que nao foram cortados (regra 3): de um nome cortado volta
// so o prefixo. A identidade inteira nunca depende disto — esta no livro.
export function nomeDeSempreDe(nome) {
  const m = /^(.*)~([0-9a-f]{12})$/.exec(String(nome));
  if (!m) return String(nome);
  return m[1].replace(/%([0-9A-F]{2})/g, (_, x) => String.fromCharCode(parseInt(x, 16)));
}

export function pastaDoDocumento(base, documentId, existe = existsSync) {
  const deSempre = `${base}/${nomeDeSempre(documentId)}`;
  if (!nomeDeSempreServe(documentId)) {
    // A pasta antiga, se um sistema a deixou criar, continua a ser a pasta.
    let ha = false;
    try { ha = existe(deSempre); } catch { ha = false; }
    if (ha) return deSempre;
  }
  return `${base}/${nomeDaPasta(documentId)}`;
}
