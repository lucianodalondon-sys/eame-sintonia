// CASCO-PAINEL-2 · UM COMANDO que refaz os dados do painel e da Sala — para correr depois de cada onda.
//
//     node italia-portale/audit/casco/refazer-painel.mjs [--vivo=...] [--casco=...] [--psql=...] [--dsn-ficheiro=...]
//
// So leitura, sem rede, nada editado a mao:
//   1. a Sala real, em DUAS transacoes `begin read only`: cada uma so e aceite se o proprio banco responder
//      transaction_read_only = on DENTRO dela (prova do D9, nao so o PGOPTIONS). A DSN e lida do ficheiro
//      e nunca impressa.
//   2. `supervisor.py --estado` no vivo, sem .pyc (PYTHONDONTWRITEBYTECODE=1) e com rede fechada; os
//      ficheiros alterados do vivo tem de ser os mesmos antes e depois, senao PARA.
//   3. os originais que nao estao no caminho que a Sala guarda: procura-os pelo tamanho E sha256 nas raizes
//      declaradas (nunca copia, nunca move).
//   4. refaz italy-sala-leitura.local.js e italy-painel.local.js (fora do Git e do deploy) com os geradores
//      sala-leitura.mjs e painel-operacao.mjs.
// Tudo o que escreve vai para <casco>/ (fora do Git): os exports, a leitura, o estado e um RECIBO com sha256.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OPT = Object.fromEntries(process.argv.slice(2).filter((a) => a.startsWith('--') && a.includes('='))
  .map((a) => [a.slice(2, a.indexOf('=')), a.slice(a.indexOf('=') + 1)]));
const U = 'C:/Users/London1';
const VIVO = OPT.vivo || `${U}/orca/workspaces/eame-sintonia/source-curator-service-v1`;
const SALA_DIR = OPT.sala || `${U}/sintonia-sala-italia`;
const CASCO = OPT.casco || `${SALA_DIR}/casco`;
const PSQL = OPT.psql || `${U}/orca/pgtmp/pgsql/bin/psql.exe`;
const DSN_F = OPT['dsn-ficheiro'] || `${SALA_DIR}/SALA_DSN.txt`;
const ONDAS = OPT.ondas || `${SALA_DIR}/ondas`;
const ARMAZEM = OPT.armazem || `${SALA_DIR}/armazem`;
const DECISOES = OPT.decisoes || `${U}/auditoria-madrugada/pergunta-emenda-exp-d78.txt`;
const RAIZES = (OPT.raizes || [
  `${VIVO}/data/collection-store`, `${VIVO}/XX`, `${U}/sintonia-acervo-backup`, 'C:/sc-hot/data/collection-store',
  `${U}/orca/workspaces/eame-sintonia/it-trunk-v1/data/collection-store`,
].join(';')).split(';').filter(Boolean);
const P = path.join(CASCO, 'painel');
fs.mkdirSync(P, { recursive: true });
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const passo = (m) => console.log(`[${new Date().toISOString().slice(11, 19)}] ${m}`);

// ── 1 · a Sala, so leitura, com a prova dentro da transacao ─────────────────
const DSN = fs.readFileSync(DSN_F, 'utf8').trim();
function lerSala(sql, nome) {
  const f = path.join(P, nome + '.sql');
  fs.writeFileSync(f, 'begin read only;\nselect \'RO=\' || current_setting(\'transaction_read_only\');\n' + sql + '\ncommit;\n');
  const out = execFileSync(PSQL, ['-X', '-A', '-t', '-q', '-v', 'ON_ERROR_STOP=1', '-f', f, DSN],
    { encoding: 'utf8', maxBuffer: 1 << 30, env: Object.assign({}, process.env, { PGOPTIONS: '-c default_transaction_read_only=on' }) })
    .replace(/\r/g, '');
  const [ro, ...resto] = out.split('\n');
  if (ro.trim() !== 'RO=on') throw new Error(`PAROU: a transacao de leitura da Sala nao e read only (${ro.trim()}) — nada foi gerado`);
  return { ro: 'on', json: JSON.parse(resto.join('\n').trim() || 'null') };
}
passo('Sala: agregados (so leitura)');
const agg = lerSala(`select json_build_object(
  'AGORA', now()::text,
  'TOTAL', (select count(*) from public.sala_de_espera),
  'POR_DIA', (select coalesce(json_agg(x order by x.dia), '[]'::json) from (select (pousado_em at time zone 'America/Sao_Paulo')::date::text as dia, count(*) as n from public.sala_de_espera group by 1) x),
  'COBERTURA', (select json_build_object('total', count(*),
     'FACT_TIME', count(*) filter (where fact_time <> 'NAO SEI'), 'PUBLICATION_TIME', count(*) filter (where published_at <> 'NAO SEI'),
     'SOURCE_LOCATION', count(*) filter (where source_location <> 'NAO SEI'), 'FACT_LOCATION', count(*) filter (where fact_location <> 'NAO SEI'))
     from public.sala_de_espera_atual));`, 'leitura-agregados');
passo('Sala: export dos itens (so leitura)');
const exp = lerSala(`select coalesce(json_agg(row_to_json(x) order by x.pousado_em, x.run_id, x.ordem), '[]'::json) from (
 select s.run_id, s.ordem, s.item_id, s.raw_observation_id::text as raw_observation_id, s.universo, s.source_id, s.estagio,
        s.pousado_em, s.captured_at, s.observed_at, s.published_at, s.published_at_basis, s.source_location, s.source_location_basis,
        s.fact_time, s.fact_time_basis, s.fact_location, s.fact_location_basis, s.completude_tempo_lugar, s.tempo_lugar_evidencia,
        s.revisoes, s.estado_da_fila, s.consumido_em, s.consumido_por, s.texto,
        r.storage_path as raw_storage_path, r.source_url as raw_source_url, r.sha256 as raw_sha256,
        r.media_type as raw_media_type, r.bytes as raw_bytes, r.captured_at as raw_captured_at, r.preserved as raw_preserved
   from public.sala_de_espera_atual s left join public.raw_asset r on r.id::text = s.raw_observation_id::text) x;`, 'leitura-export');
const EXPORT = path.join(CASCO, 'SALA-EXPORT-LEITURA.json');
fs.writeFileSync(EXPORT, JSON.stringify(exp.json));

// ── 2 · o estado do servico, sem mexer no vivo ─────────────────────────────
passo('servico: supervisor.py --estado (so leitura)');
const sujos = () => execFileSync('git', ['-C', VIVO, 'status', '--porcelain'], { encoding: 'utf8' });
const antes = sujos();
const sup = execFileSync('py', ['curadoria/supervisor.py', '--estado'], {
  cwd: VIVO, encoding: 'utf8', env: Object.assign({}, process.env, {
    PYTHONDONTWRITEBYTECODE: '1', PYTHONUTF8: '1', HTTP_PROXY: 'http://127.0.0.1:9', HTTPS_PROXY: 'http://127.0.0.1:9' }),
});
if (sujos() !== antes) throw new Error('PAROU: o vivo mudou enquanto se lia o estado do servico');
fs.writeFileSync(path.join(P, 'SUPERVISOR-ESTADO.json'), sup.slice(sup.indexOf('{')));
fs.writeFileSync(path.join(P, 'SUPERVISOR-ESTADO.medido_em'), new Date().toISOString());

// ── 3 · os originais fora do caminho da Sala: procura por tamanho + sha256 ───
passo('originais: conferir o caminho da Sala e procurar os que faltam');
const falta = exp.json.filter((x) => x.raw_storage_path && !fs.existsSync(path.join(ARMAZEM, x.raw_storage_path)));
const alvo = new Map(falta.map((x) => [x.raw_sha256, Number(x.raw_bytes)]));
const tamanhos = new Set(alvo.values());
const achados = {};
let lidos = 0;
function varre(d) {
  let ents; try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
  for (const e of ents) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) { varre(p); continue; }
    let st; try { st = fs.statSync(p); } catch { continue; }
    if (!tamanhos.has(st.size)) continue;
    lidos++;
    const h = sha(fs.readFileSync(p));
    if (alvo.has(h)) (achados[h] = achados[h] || []).push(p.replace(/\\/g, '/'));
  }
}
if (falta.length) for (const r of RAIZES) varre(r);
const leitura = Object.assign({}, agg.json, { SHOW_TRANSACTION_READ_ONLY: agg.ro,
  PROCURA: { FORA_DO_CAMINHO_DA_SALA: falta.length, RAIZES, CRITERIO: 'mesmo tamanho em bytes E mesmo sha256 que o raw_asset', LIDOS: lidos, ACHADOS: achados } });
const LEITURA = path.join(P, 'LEITURA-SALA-PAINEL.json');
fs.writeFileSync(LEITURA, JSON.stringify(leitura, null, 1));

// ── 4 · os geradores ────────────────────────────────────────────────────────
passo('gerar: sala-leitura.mjs');
const intel = OPT.intel || path.join(HERE, 'INTELLIGENCE-EXPERIMENTAL-EXEMPLO-VAZIO.json');
const r1 = execFileSync(process.execPath, [path.join(HERE, 'sala-leitura.mjs'), EXPORT, ARMAZEM, path.join(CASCO, 'italy-sala-leitura.local.js'),
  `--achados=${LEITURA}`, `--intel=${intel}`], { encoding: 'utf8' });
passo('gerar: painel-operacao.mjs');
const fecho = OPT['fecho-onda3'] || path.join(ONDAS, 'ONDA3-WEB-20260925-1934', 'FECHO-ONDA3.md');
const r2 = execFileSync(process.execPath, [path.join(HERE, 'painel-operacao.mjs'), `--vivo=${VIVO}`, `--ondas=${ONDAS}`, `--sala=${LEITURA}`,
  `--export=${EXPORT}`, `--supervisor=${path.join(P, 'SUPERVISOR-ESTADO.json')}`, `--fecho-onda3=${fecho}`, `--decisoes=${DECISOES}`,
  `--copia=${path.join(P, 'italy-painel.local.js')}`], { encoding: 'utf8' });

const recibo = { feito_em: new Date().toISOString(), sala_so_leitura: [agg.ro, exp.ro], sala_total: agg.json.TOTAL,
  fora_do_caminho_da_sala: falta.length, achados_noutro_caminho: Object.keys(achados).length,
  ficheiros: Object.fromEntries([EXPORT, LEITURA, path.join(P, 'SUPERVISOR-ESTADO.json'), path.join(CASCO, 'italy-sala-leitura.local.js'),
    path.join(P, 'italy-painel.local.js')].map((f) => [f.replace(/\\/g, '/'), sha(fs.readFileSync(f))])) };
fs.writeFileSync(path.join(P, 'RECIBO-REFAZER.json'), JSON.stringify(recibo, null, 1));
console.log(JSON.stringify({ sala: JSON.parse(r1).contagem, painel: JSON.parse(r2), recibo }, null, 1));
