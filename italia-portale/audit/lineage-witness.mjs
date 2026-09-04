/* SINTONIA · A TESTEMUNHA DA LINHAGEM, LIDA
   ---------------------------------------------------------------------------
   Um clone `--single-branch` da Linha B nao tem 8c082f7 nem 0b490ec: sao
   commits de outra linhagem, que o handoff apenas NOMEIA. Sem eles o portao do
   lote nao consegue responder se os carimbos estao na mesma historia.

       RESPONDER COM `git fetch --all` SERIA TROCAR UMA PROVA POR UMA LIGACAO.

   Aqui refaz-se, offline, a conta que o proprio Git faz:

       sha1("commit " + tamanho + "\0" + corpo) == SHA

   Se um byte mudar, o SHA muda. Se um `parent` mudar, a cadeia parte-se. Se o
   descendente declarado nao for o que a cadeia termina, falha. Nao ha nada a
   confiar — ha uma conta a repetir.

   PRECEDENCIA: quando o Git local TEM os objectos, e o Git que responde. Isto e
   o segundo melhor, e nunca o primeiro.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const FICHEIRO = path.join(AQUI, 'UPSTREAM-LINEAGE-WITNESS.json');

/** Le a testemunha e prova-a por dentro. Devolve {ok, porque, cadeia, mapa}. */
export function lerTestemunha(ficheiro = FICHEIRO) {
  if (!fs.existsSync(ficheiro)) return { ok: false, porque: ['testemunha ausente'], mapa: new Map() };
  let W;
  try { W = JSON.parse(fs.readFileSync(ficheiro, 'utf8')); }
  catch (e) { return { ok: false, porque: [`testemunha ilegivel: ${e.message}`], mapa: new Map() }; }

  const mau = [];
  const mapa = new Map();
  for (const c of W.COMMITS || []) {
    const corpo = Buffer.from(c.CORPO_B64 || '', 'base64');
    const sha = crypto.createHash('sha1')
      .update(Buffer.concat([Buffer.from(`commit ${corpo.length}\0`), corpo])).digest('hex');
    if (sha !== c.SHA) { mau.push(`${(c.SHA || '?').slice(0, 7)}: o corpo da ${sha.slice(0, 7)}`); continue; }
    /* os parents sao lidos do CORPO, nunca do campo declarado: um campo pode
       mentir, o corpo nao — mentir nele muda o SHA. */
    const linhas = corpo.toString('utf8').split('\n');
    const pais = [];
    for (const l of linhas) { if (l.startsWith('parent ')) pais.push(l.slice(7).trim()); else if (!l.trim()) break; }
    if (JSON.stringify(pais) !== JSON.stringify(c.PARENTS || []))
      mau.push(`${c.SHA.slice(0, 7)}: PARENTS declarados diferem dos do corpo`);
    mapa.set(c.SHA, pais);
  }
  /* Os extremos declarados tem de SER os extremos da cadeia. Sem isto, trocar
     DESCENDANT por zeros nao partia nada: a caminhada nunca lia o campo, e uma
     testemunha que declara um fim que nao tem e uma testemunha que nao se leu
     a si propria.

         UM CAMPO QUE NINGUEM VERIFICA E UM CAMPO QUE PODE MENTIR. */
  if (mau.length === 0) {
    const filhos = new Set();
    for (const [s, pais] of mapa) for (const p of pais) if (mapa.has(p)) filhos.add(p);
    const pontas = [...mapa.keys()].filter((s) => !filhos.has(s));          // sem filho na cadeia
    const raizes = [...mapa.keys()].filter((s) => !(mapa.get(s) || []).some((p) => mapa.has(p)));
    if (pontas.length !== 1 || pontas[0] !== W.DESCENDANT)
      mau.push(`DESCENDANT declarado ${String(W.DESCENDANT).slice(0, 7)} nao e a ponta da cadeia (${pontas.map((x) => x.slice(0, 7)).join(',') || 'nenhuma'})`);
    if (raizes.length !== 1 || raizes[0] !== W.ANCESTOR)
      mau.push(`ANCESTOR declarado ${String(W.ANCESTOR).slice(0, 7)} nao e a raiz da cadeia (${raizes.map((x) => x.slice(0, 7)).join(',') || 'nenhuma'})`);
  }

  return { ok: mau.length === 0, porque: mau, ancestor: W.ANCESTOR, descendant: W.DESCENDANT, mapa };
}

/** `a` e antepassado de `b` segundo a testemunha? Caminha do descendente para tras. */
export function antepassadoNaTestemunha(a, b, t = lerTestemunha()) {
  if (!t.ok) return { resposta: null, porque: t.porque };
  const cheio = (s) => [...t.mapa.keys()].find((k) => k.startsWith(s)) || s;
  const A = cheio(a), B = cheio(b);
  if (!t.mapa.has(B)) return { resposta: null, porque: [`${b} nao esta na testemunha`] };
  /* a testemunha tem de terminar exactamente onde diz terminar */
  if (t.descendant !== B && !t.mapa.has(A)) return { resposta: null, porque: [`${a} nao esta na testemunha`] };
  const visto = new Set();
  let frente = [B];
  while (frente.length) {
    const s = frente.shift();
    if (s === A) return { resposta: true, porque: [] };
    if (visto.has(s)) continue;
    visto.add(s);
    for (const p of (t.mapa.get(s) || [])) frente.push(p);
  }
  /* Chegar ao fim da cadeia sem encontrar A so e resposta se a cadeia estiver
     inteira ate ao ancestral declarado. Se ela se esgotou noutro sitio, nao
     sabemos — e nao saber nunca e passar. */
  return t.mapa.has(A)
    ? { resposta: false, porque: [`${a} nao aparece na ascendencia de ${b}`] }
    : { resposta: null, porque: [`a testemunha nao alcanca ${a}`] };
}
