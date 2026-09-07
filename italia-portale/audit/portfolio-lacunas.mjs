/* ══ O QUE FALTA A CADA PRODUTO, PRODUTO A PRODUTO ═══════════════════════════
   O ecra do portafoglio mostra 51 cartoes e alguns estavam vazios. «Vazio» nao
   e um diagnostico: pode ser dado que nao temos, dado que temos e nao ligamos,
   ou dado que o motor recusou por nao o poder provar. Sao tres coisas
   diferentes e so uma delas se resolve indo buscar mais nada.

       UM CARTAO VAZIO NAO DIZ PORQUE ESTA VAZIO. ESTA REGUA DIZ.

   Le do MODELO — a mesma superficie que o portal desenha — e do ficheiro de
   pares do rotulo, que e o dono do estado da leitura. Nao le da rede: uma
   regua que vai a rede mede a rede, nao o produto. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadData, mount } from './lib/harness.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(AQUI, '..', '..');
const C = { v: '\x1b[32m', a: '\x1b[33m', r: '\x1b[31m', d: '\x1b[2m', x: '\x1b[0m' };

export async function medirLacunas() {
  await loadData();
  const m = mount();
  const P = m.AM.collections.products.records;
  const com = P.filter((p) => p.inCommercial);

  /* O estado da leitura do rotulo vem de quem a fez. Se o ficheiro nao estiver
     no disco a coluna diz NAO SEI — nunca inventa um estado. */
  let leitura = {};
  try {
    const j = JSON.parse(fs.readFileSync(
      path.join(RAIZ, 'data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json'), 'utf8'));
    for (const x of j.POR_PRODUTO || []) leitura[String(x.REGISTRATION_ID)] = x.ESTADO_DA_LEITURA;
  } catch { leitura = null; }

  const n = (p, k) => ((p[k] || []).length);
  const linhas = com.map((p) => {
    const ligacoes = n(p, 'verifiedLinks') + n(p, 'relatedLinks')
      + n(p, 'checkNeededLinks') + n(p, 'rejectedLinks');
    const moa = (p.moaList || []).length || (p.frac || p.hrac || p.irac ? 1 : 0);
    const falta = [];
    if (!p.inRegulatory) falta.push('REGISTO');
    if (!p.labelUrl) falta.push('ETIQUETA');
    if (!(p.aiList || []).length && !p.ai) falta.push('PRINCIPIO_ATIVO');
    if (!moa) falta.push('MECANISMO_DE_ACAO');
    if (!ligacoes) falta.push('USO_DE_ROTULO');
    /* A CULTURA PODE VIR DE DOIS SITIOS, E BASTA UM.
       `p.crops` e a lista que o CATALOGO declara. Mas o Avastel tem trinta
       linhas de uso, cada uma com a sua cultura lida no rotulo, e a regua
       dizia-lhe «falta CULTURA» na mesma — porque olhava so para o catalogo.
       Uma lacuna que se anuncia com o dado a vista ao lado nao e uma lacuna:
       e a regua a medir o sitio errado. */
    const culturasDeRotulo = new Set();
    for (const k of ['verifiedLinks', 'relatedLinks', 'checkNeededLinks', 'rejectedLinks'])
      for (const l of (p[k] || [])) if (l.crop || l.cropOnLabel) culturasDeRotulo.add(l.crop || l.cropOnLabel);
    if (!(p.crops || []).length && !culturasDeRotulo.size) falta.push('CULTURA');
    return {
      nome: p.name, reg: p.reg || null, categoria: p.category || null,
      etiqueta: !!p.labelUrl, ligacoes, moa: !!moa,
      leitura: leitura ? (leitura[String(p.reg)] || (p.reg ? 'FORA_DO_MANIFESTO' : '—')) : 'NAO_SEI',
      falta,
      /* A LACUNA TEM DONO, E O DONO DIZ O QUE A RESOLVE. */
      accao: !p.inRegulatory ? 'NAO_HA_O_QUE_COLHER_AQUI'
        : ligacoes ? 'COMPLETO'
        : (leitura && /TABELA_NAO_LOCALIZADA|TABELA_SEM_PAR/.test(leitura[String(p.reg)] || ''))
          ? 'LEITOR_DE_ROTULO' : 'RECOLHA',
    };
  }).sort((a, b) => a.falta.length - b.falta.length || a.nome.localeCompare(b.nome));

  const porAccao = {};
  for (const l of linhas) porAccao[l.accao] = (porAccao[l.accao] || 0) + 1;
  const porFalta = {};
  for (const l of linhas) for (const f of l.falta) porFalta[f] = (porFalta[f] || 0) + 1;
  return { linhas, porAccao, porFalta, total: com.length,
    completos: linhas.filter((l) => !l.falta.length).length };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const r = await medirLacunas();
  console.log('');
  console.log('  SINTONIA · LACUNAS DO PORTAFOGLIO — o que falta, e de quem e');
  console.log('  ' + '─'.repeat(104));
  console.log('  ' + 'PRODUTO'.padEnd(34) + 'REG'.padEnd(9) + 'LIG'.padStart(4) + '  '
    + 'LEITURA DO ROTULO'.padEnd(24) + 'O QUE FALTA');
  console.log('  ' + '─'.repeat(104));
  for (const l of r.linhas) {
    const cor = !l.falta.length ? C.v : l.accao === 'NAO_HA_O_QUE_COLHER_AQUI' ? C.r : C.a;
    console.log('  ' + l.nome.padEnd(34) + String(l.reg || '—').padEnd(9)
      + String(l.ligacoes).padStart(4) + '  ' + String(l.leitura).padEnd(24)
      + cor + (l.falta.join(' · ') || 'nada') + C.x);
  }
  console.log('  ' + '─'.repeat(104));
  console.log('  completos: ' + r.completos + '/' + r.total);
  console.log('  por accao : ' + JSON.stringify(r.porAccao));
  console.log('  por lacuna: ' + JSON.stringify(r.porFalta));
  console.log('');
  console.log('  ' + C.d + 'LEITOR_DE_ROTULO         a etiqueta esta ca; o leitor nao achou a tabela.' + C.x);
  console.log('  ' + C.d + 'RECOLHA                  ha registo e etiqueta, e a leitura nem sequer foi tentada.' + C.x);
  console.log('  ' + C.d + 'NAO_HA_O_QUE_COLHER_AQUI nao esta no registo lido. Ausencia AQUI, nao no mundo.' + C.x);
  console.log('');
}
