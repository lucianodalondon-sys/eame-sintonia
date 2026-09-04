#!/usr/bin/env node
/* SINTONIA · CONTROLO NEGATIVO — o portão dispara, ou não é portão
   ---------------------------------------------------------------------------
   Quinze verificações passam. Isso prova que OS DADOS DE HOJE estão limpos.
   Não prova que o portão apanharia dados sujos amanhã — e as duas coisas
   parecem exactamente iguais no ecrã:

       UM PORTÃO QUE NUNCA DISPAROU E UM PORTÃO QUE NÃO SABE DISPARAR
       PRODUZEM O MESMO PASS.

   Este ficheiro fabrica a violação de propósito e exige o FAIL. Se o FAIL não
   vier, o verde de `lote-completo` era decorativo e este controlo é o único
   sítio onde isso apareceria.

   NÃO TOCA NADA DE PRODUÇÃO
   --------------------------
   `harness.mjs` resolve o cliente a partir da sua própria localização, e isso
   é uma boa propriedade: significa que o portão não pode ser redireccionado
   por variável de ambiente para dados amigáveis. Em vez de abrir esse buraco
   só para poder testar, copio a árvore inteira para uma pasta temporária,
   estrago a cópia e corro o portão DE LÁ. O repositório não muda um byte, e o
   portão continua sem ter como ser apontado para outro sítio em produção.

   O CONTROLO DO CONTROLO
   -----------------------
   A primeira corrida é sobre a cópia INTACTA, e tem de passar. Sem ela, um
   FAIL nas mutações não provaria nada: podia ser a cópia partida, e eu estaria
   a celebrar um portão que reprova tudo — que é tão inútil quanto um que
   aprova tudo.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const PORTAL = path.resolve(AQUI, '..');
const CAMPO = 'IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json';

const R = [];
const G = '\x1b[32m', V = '\x1b[31m', D = '\x1b[2m', X = '\x1b[0m';

function copia() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sintonia-cn-'));
  fs.cpSync(PORTAL, path.join(dir, 'italia-portale'), { recursive: true });
  return path.join(dir, 'italia-portale');
}

function correPortao(raiz, portao = 'lote-completo.mjs') {
  try {
    const out = execFileSync(process.execPath,
      [path.join(raiz, 'audit', portao)],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { code: 0, out };
  } catch (e) {
    return { code: e.status === undefined ? -1 : e.status,
             out: (e.stdout || '') + (e.stderr || '') };
  }
}

/* Um FAIL só conta quando é O FAIL CERTO. Um portão que reprova por outro
   motivo qualquer — ficheiro partido, JSON inválido — não provou que apanha
   esta violação; provou que se desfez. */
function reprovouEm(saida, id) {
  const linha = saida.split('\n').find((l) => l.includes(id));
  return Boolean(linha && /FAIL/.test(linha.replace(/\x1b\[[0-9;]*m/g, '')));
}

function caso(nome, oQue, mutar, idEsperado, portao = 'lote-completo.mjs') {
  const raiz = copia();
  try {
    const p = path.join(raiz, 'client', 'upstream', CAMPO);
    const d = JSON.parse(fs.readFileSync(p, 'utf8'));
    mutar(d, raiz);
    if (d) fs.writeFileSync(p, JSON.stringify(d, null, 1), 'utf8');
    const { code, out } = correPortao(raiz, portao);
    const certo = reprovouEm(out, idEsperado);
    R.push({
      nome, oQue, pass: code !== 0 && certo,
      detalhe: code === 0
        ? `o portão PASSOU com a violação injectada — ${idEsperado} não dispara`
        : certo ? `${idEsperado} reprovou, como tinha de reprovar`
                : `reprovou, mas NÃO em ${idEsperado} — pode ter-se desfeito por outro motivo`,
    });
  } finally {
    fs.rmSync(path.dirname(raiz), { recursive: true, force: true });
  }
}

/* ── 0 · o controlo do controlo ──────────────────────────────────────────── */
{
  const raiz = copia();
  const { code } = correPortao(raiz);
  R.push({
    nome: 'COPIA_INTACTA_PASSA', oQue: 'a cópia não mutada continua a passar',
    pass: code === 0,
    detalhe: code === 0 ? 'a cópia é fiel — um FAIL abaixo vem da mutação, não da cópia'
                        : 'a cópia já falha sem mutação: nada abaixo prova o que quer que seja',
  });
  fs.rmSync(path.dirname(raiz), { recursive: true, force: true });
}

/* ── 1 · evidência a atravessar como entrada autorizada ──────────────────── */
caso('EVIDENCE_ONLY_NAO_ATRAVESSA',
     'um registo EVIDENCE_ONLY declarado entre as entradas autorizadas',
     (d) => {
       d.ENTRADAS_AUTORIZADAS.push({
         ID: 'CONTROLO_NEGATIVO#evidencia', SUBCONJUNTO: 'sinais verificados V1',
         DESTINO: 'EVIDENCE_ONLY', AVISO: null, LIMITES: null,
       });
     },
     'EVIDENCE_ONLY_NOT_PROMOTED_TO_SIGNAL');

/* ── 2 · derrubado a atravessar ──────────────────────────────────────────── */
caso('DROPPED_NAO_ATRAVESSA',
     'um registo DROPPED declarado entre as entradas autorizadas',
     (d) => {
       d.ENTRADAS_AUTORIZADAS.push({
         ID: 'CONTROLO_NEGATIVO#derrubado', SUBCONJUNTO: 'sinais verificados V1',
         DESTINO: 'DROPPED', AVISO: null, LIMITES: null,
       });
     },
     'DROPPED_CANNOT_RENDER');

/* ── 3 · a promoção disfarçada, que é a que ninguém veria ────────────────── */
/* As duas de cima declaram o crime no próprio campo. Esta não: a evidência
   entra JÁ VESTIDA DE CARTÃO, que é como isto aconteceria de verdade — um
   gerador a montante com um destino trocado. Só a aritmética a apanha. */
caso('EVIDENCIA_VESTIDA_DE_CARTAO_NAO_ATRAVESSA',
     'um 48.º registo entra como CARTAO sem que o universo-base mude',
     (d) => {
       d.ENTRADAS_AUTORIZADAS.push({
         ID: 'CONTROLO_NEGATIVO#promovido', SUBCONJUNTO: 'sinais verificados V1',
         DESTINO: 'CARTAO', AVISO: null, LIMITES: null,
       });
     },
     'FIELD_SIGNALS_VISIBLE_47');

/* ── 4 e 5 · as duas provas novas do portao da casa ──────────────────────── */
/* Elas nasceram nesta missao e passaram a primeira. Passar com o dado limpo e
   o que qualquer portao inerte faz — por isso entram aqui no mesmo pe que as
   outras. O ficheiro mutado agora e o DADO DO BROWSER, nao o handoff. */
{
  const raiz = copia();
  const { code } = correPortao(raiz, 'casa-gate.mjs');
  R.push({
    nome: 'COPIA_INTACTA_PASSA_NA_CASA', oQue: 'a cópia não mutada passa também no portão da casa',
    pass: code === 0,
    detalhe: code === 0 ? 'a cópia é fiel no browser — um FAIL abaixo vem da mutação'
                        : 'a cópia já falha sem mutação no portão da casa',
  });
  fs.rmSync(path.dirname(raiz), { recursive: true, force: true });
}

caso('HASH_TROCADO_NA_CASA_E_APANHADO',
     'um dos seis hashes consumidos é trocado no dado do browser',
     (_d, raiz) => {
       const f = path.join(raiz, 'client', 'italy-casa.js');
       const t = fs.readFileSync(f, 'utf8');
       fs.writeFileSync(f, t.replace(
         'sha256:1283b4f7a292798f19a964421966316603e7c25aaa9d5b52aa7764bba74ec560',
         'sha256:' + '0'.repeat(64)), 'utf8');
     },
     'CASA_HASHES_6_OF_6_MATCH_PINS_AND_DISK', 'casa-gate.mjs');

caso('EXCLUIDO_NO_DADO_DO_BROWSER_E_APANHADO',
     'o único ITFC- EXCLUÍDO passa a viajar no dado do browser',
     (_d, raiz) => {
       const f = path.join(raiz, 'client', 'italy-casa.js');
       const t = fs.readFileSync(f, 'utf8');
       /* entra como comentário: não é desenhado, e é exactamente esse o ponto —
          NÃO RENDERIZADO NÃO É O MESMO QUE NÃO ENTREGUE. */
       fs.writeFileSync(f, t.replace('window.ITALY_CASA = {',
         '/* ITFC-027 */\nwindow.ITALY_CASA = {'), 'utf8');
     },
     'BROWSER_DATA_ONLY_AUTHORIZED_DESTINATIONS', 'casa-gate.mjs');

const mau = R.filter((r) => !r.pass);
console.log('\n  SINTONIA · CONTROLO NEGATIVO — a violação é fabricada, o FAIL é exigido');
console.log('  ' + '─'.repeat(100));
for (const r of R) {
  console.log(`  ${r.pass ? G + 'PASS' + X : V + 'FAIL' + X}  ${r.nome}`);
  console.log(`        ${D}${r.oQue}${X}`);
  console.log(`        ${r.detalhe}`);
}
console.log('  ' + '─'.repeat(100));
console.log(`  ${mau.length ? V + 'FAIL' + X : G + 'PASS' + X} — ${R.length - mau.length}/${R.length}\n`);
process.exit(mau.length ? 1 : 0);
