// CASCO-LEITURA (D78) · a vista SO DE LEITURA da Sala: o que aconteceu, quando, onde, fonte/prova e
// o que a Intelligence concluiu — inclusive NAO SEI. Sem pontuacao, sem ordem de «relevancia».
//
//     node italia-portale/audit/casco/sala-leitura.mjs <SALA-EXPORT-LEITURA.json> <raiz-do-armazem> [saida-copia.js]
//
// Le um EXPORT so-leitura da Sala (a view `sala_de_espera_atual` + `raw_asset`, feito com
// default_transaction_read_only=on) e escreve `italia-portale/client/italy-sala-leitura.js`.
// ⚠️ ESSE FICHEIRO TEM TEXTO DA SALA (o trecho de cada documento): esta no .gitignore e no
// .vercelignore do cliente e NUNCA entra no Git nem num deploy. O export fica em
// C:/Users/London1/sintonia-sala-italia/casco/.
//
// Regras:
//   · os quatro campos SEPARADOS — FACT_TIME, PUBLICATION_TIME, SOURCE_LOCATION, FACT_LOCATION —
//     cada um com valor, base e precisao, ou NAO SEI. Nada se funde: UNKNOWN nao vira facto.
//   · a prova: o endereco de origem e o bruto no armazem, conferido pelo sha256 que a Sala guarda.
//     Bruto que nao esta no disco diz «NAO ENCONTRADO» com o sha256 — nunca um link partido.
//   · coluna Intelligence = NAO_EXECUTADA ate a Intelligence ter saida (INT-LAW-023: o portal nao
//     reconstroi Intelligence).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENTE = path.resolve(HERE, '..', '..', 'client');
const [EXPORT, ARMAZEM, COPIA] = process.argv.slice(2);
if (!EXPORT || !ARMAZEM) { console.error('uso: sala-leitura.mjs <export.json> <armazem> [copia.js]'); process.exit(2); }

const NS = 'NAO SEI';
const vazio = (v) => v == null || String(v).trim() === '' || /^(NAO SEI|NÃO SEI|UNKNOWN|NOT_KNOWN)\b/i.test(String(v).trim());
const campo = (valor, base, precisao, tipo) => ({
  valor: vazio(valor) ? NS : String(valor),
  base: vazio(base) ? NS : String(base),
  // a base de um NAO SEI e o PORQUE: mostra-se, nao se esconde
  porque: vazio(valor) && !vazio(base) ? String(base) : null,
  precisao: vazio(precisao) ? NS : String(precisao),
  tipo: vazio(tipo) ? null : String(tipo),
});
const json = (x) => { if (x == null) return {}; if (typeof x === 'object') return x; try { return JSON.parse(x); } catch { return {}; } };

// o trecho: a primeira linha com frase (>= 8 palavras), como o corpo da LUGAR-FATO — o que o documento
// DIZ, nao uma conclusao. Nunca o texto inteiro.
function trecho(t) {
  const linhas = String(t || '').split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const l = linhas.find((x) => (x.match(/[A-Za-zÀ-ÿ']+/g) || []).length >= 8) || linhas[0] || '';
  return l.length > 240 ? l.slice(0, 237) + '…' : l;
}

const itens = JSON.parse(fs.readFileSync(EXPORT, 'utf8'));
const out = [];
for (const x of itens) {
  const ev = json(x.tempo_lugar_evidencia);
  const co = json(x.completude_tempo_lugar);
  const rel = String(x.raw_storage_path || '');
  const f = rel ? path.join(ARMAZEM, rel) : null;
  let raw = { estado: 'SEM_CAMINHO', sha256: x.raw_sha256 || NS };
  if (f && fs.existsSync(f)) {
    const sha = crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
    raw = sha === x.raw_sha256
      ? { estado: 'CONFERIDO', href: pathToFileURL(f).href, sha256: sha, media: x.raw_media_type, bytes: Number(x.raw_bytes) || null }
      : { estado: 'SHA_DIFERENTE', sha256: x.raw_sha256, noDisco: sha };
  } else if (f) {
    raw = { estado: 'NAO_ENCONTRADO', sha256: x.raw_sha256 || NS, caminho: rel };
  }
  out.push({
    id: `${x.run_id}#${x.ordem}`, itemId: x.item_id, sourceId: x.source_id, universo: x.universo, estagio: x.estagio,
    pousadoEm: x.pousado_em, capturadoEm: x.captured_at, revisoes: Number(x.revisoes) || 0,
    trecho: trecho(x.texto),
    campos: {
      FACT_TIME: campo(x.fact_time, x.fact_time_basis, ev.FACT_TIME_PRECISION, ev.FACT_TIME_KIND),
      PUBLICATION_TIME: campo(x.published_at, x.published_at_basis, ev.PUBLISHED_AT_PRECISION, null),
      SOURCE_LOCATION: campo(x.source_location, x.source_location_basis, ev.SOURCE_LOCATION_PRECISION, null),
      FACT_LOCATION: campo(x.fact_location, x.fact_location_basis, ev.FACT_LOCATION_PRECISION, ev.FACT_LOCATION_KIND),
    },
    completude: co,
    prova: { url: vazio(x.raw_source_url) ? null : x.raw_source_url, raw },
    intelligence: 'NAO_EXECUTADA',
  });
}
// ordem: a mais recente primeiro — tempo de pouso, nunca «relevancia»
out.sort((a, b) => String(b.pousadoEm).localeCompare(String(a.pousadoEm)) || a.id.localeCompare(b.id));

const contagem = {};
for (const k of ['FACT_TIME', 'PUBLICATION_TIME', 'SOURCE_LOCATION', 'FACT_LOCATION']) {
  contagem[k] = {
    comValor: out.filter((i) => i.campos[k].valor !== NS).length,
    comBase: out.filter((i) => i.campos[k].base !== NS).length,
    comPrecisao: out.filter((i) => i.campos[k].precisao !== NS).length,
  };
}
contagem.RAW = out.reduce((a, i) => (a[i.prova.raw.estado] = (a[i.prova.raw.estado] || 0) + 1, a), {});
contagem.INTELLIGENCE = { NAO_EXECUTADA: out.length };
const exportSha = crypto.createHash('sha256').update(fs.readFileSync(EXPORT)).digest('hex');
const pacote = { gerado: new Date().toISOString(), export: path.basename(EXPORT), exportSha256: exportSha, total: out.length, contagem, itens: out };
const js = '/* GERADO por italia-portale/audit/casco/sala-leitura.mjs — TEM TEXTO DA SALA: fora do Git e do deploy. */\n'
  + 'window.ITALY_SALA_LEITURA = ' + JSON.stringify(pacote) + ';\n';
fs.writeFileSync(path.join(CLIENTE, 'italy-sala-leitura.js'), js);
if (COPIA) fs.writeFileSync(COPIA, js);
console.log(JSON.stringify({ total: out.length, exportSha256: exportSha, contagem }, null, 1));
