// A CADENCIA DA REFERENCIA — «esta fonte e devida HOJE?», lida do contrato.
//
// D116 + D117 (dono, 27/09). O registo oficial (IT-T4-001), as bulas e o
// portfolio ADAMA sao BIBLIOTECA DE REFERENCIA versionada, nao noticia. A
// cadencia de cada um e CONTRATO DA COLETA (D117.6): mora no contrato da fonte
// (`regras/italy_contracts.mjs`, bloco `CADENCIA`), e esta peca so a le.
//
// O QUE FALTAVA, MEDIDO (REFERENCIA-MANUTENCAO, 27/09)
// ----------------------------------------------------
// O contrato de IT-T4-001 tinha `RECOLLECTION` — que responde «revisito um
// DETALHE ja conhecido?» — e nenhum campo que respondesse «QUANDO volto a
// fonte?». A coleta agendada (`coleta/italy_recurrent_collect.mjs`) colhia a
// populacao inteira todos os dias, ou nao colhia. Uma fonte semanal colhida
// todo dia gasta teto; uma fonte semanal que ninguem agenda envelhece calada —
// e foi o que aconteceu: nenhuma edicao depois de 14/09.
//
//     RECOLLECTION  != CADENCIA
//     «revisito o detalhe?» e «quando volto a fonte?» sao duas perguntas.
//
// O QUE ELA NAO E
// ---------------
// Nao e portao: quem diz se uma fonte PODE ser colhida continua a ser
// `curadoria/collection_gate.py`. A cadencia so diz QUANDO, dentro do que o
// portao ja admitiu. Nao abre fonte recusada, nunca.
//
//     CADENCIA NAO E ADMISSAO. DEVIDA HOJE NAO E ELEGIVEL.
//
// Nao vai a rede, nao le o relogio (a data entra por argumento — em
// Europe/Rome, calculada por quem chama), nao le o livro. «Ultima checagem
// bem-sucedida» vem de `leis/frescor_da_referencia.py`, o dono dessa leitura.
//
// Contrato SEM `CADENCIA` = comportamento de sempre (todo dia). Nada muda para
// quem nao declarou.

export const TIPOS_DE_CADENCIA = Object.freeze(["SEMANAL", "MENSAL", "ROTACAO_DIARIA"]);
export const DIAS_DA_SEMANA = Object.freeze({ DOM: 0, SEG: 1, TER: 2, QUA: 3, QUI: 4, SEX: 5, SAB: 6 });

export class CadenciaInvalida extends Error {}

const DATA = /^\d{4}-\d{2}-\d{2}$/;
const dia = (iso) => {
  if (!DATA.test(String(iso))) throw new CadenciaInvalida(`data fora do formato AAAA-MM-DD: ${JSON.stringify(iso)}`);
  return new Date(`${iso}T00:00:00Z`);
};
const iso = (d) => d.toISOString().slice(0, 10);
const somar = (d, n) => new Date(d.getTime() + n * 864e5);

// A data da checagem pode vir com hora (CAPTURED_AT do livro). So o DIA conta.
const soODia = (v) => (v == null ? null : String(v).slice(0, 10));

export function conferirCadencia(sourceId, c) {
  if (!c || typeof c !== "object") throw new CadenciaInvalida(`${sourceId}: sem bloco CADENCIA`);
  if (!TIPOS_DE_CADENCIA.includes(c.TIPO))
    throw new CadenciaInvalida(`${sourceId}: CADENCIA.TIPO ${JSON.stringify(c.TIPO)} fora do vocabulario (${TIPOS_DE_CADENCIA.join(", ")})`);
  if (c.TIPO === "SEMANAL") {
    if (!(c.DIA in DIAS_DA_SEMANA)) throw new CadenciaInvalida(`${sourceId}: SEMANAL sem DIA valido`);
    for (const r of c.RETENTAR || [])
      if (!(r in DIAS_DA_SEMANA)) throw new CadenciaInvalida(`${sourceId}: RETENTAR com dia desconhecido ${r}`);
  }
  if (c.TIPO === "ROTACAO_DIARIA" && !(Number.isInteger(c.MAX_POR_DIA) && c.MAX_POR_DIA >= 1))
    throw new CadenciaInvalida(`${sourceId}: ROTACAO_DIARIA exige MAX_POR_DIA inteiro >= 1`);
  return c;
}

// ── DEVIDA HOJE? ────────────────────────────────────────────────────────────
// `hoje` e `ultimaChecagemOk` sao datas (AAAA-MM-DD). `ultimaChecagemOk` null
// = nunca houve checagem bem-sucedida conhecida — NAO e «checada hoje».
// `disparos` so contam para quem declara EXTRAORDINARIA (o portfolio: produto
// ADAMA novo/revogado no diff do registo).
//
// Devolve SEMPRE os mesmos campos: DEVIDA, TENTATIVA, ALERTA, PORQUE.
export function devidaHoje(cad, hoje, ultimaChecagemOk, disparos = []) {
  const h = dia(hoje);
  const ult = soODia(ultimaChecagemOk);
  const u = ult == null ? null : dia(ult);
  const nunca = u == null;

  if (cad.TIPO === "ROTACAO_DIARIA")
    return { DEVIDA: true, TENTATIVA: "ROTACAO", ALERTA: null,
             PORQUE: `rotacao diaria de ate ${cad.MAX_POR_DIA} — quais, decide planoDaRotacao()` };

  if (cad.TIPO === "MENSAL") {
    if (cad.EXTRAORDINARIA && disparos.length)
      return { DEVIDA: true, TENTATIVA: "EXTRAORDINARIA", ALERTA: null,
               PORQUE: `extraordinaria: ${disparos.length} disparo(s) do diff (${cad.EXTRAORDINARIA})` };
    const mesmoMes = !nunca && ult.slice(0, 7) === hoje.slice(0, 7);
    if (mesmoMes)
      return { DEVIDA: false, TENTATIVA: null, ALERTA: null, PORQUE: `ja checada com sucesso neste mes (${ult})` };
    // Um mes inteiro sem checagem, alem do corrente, e alerta — nao so atraso.
    const alerta = nunca ? "NUNCA_CHECADA_COM_SUCESSO"
      : (dia(`${hoje.slice(0, 7)}-01`) - u) / 864e5 > 31 ? `SEM_CHECAGEM_OK_DESDE_${ult}` : null;
    return { DEVIDA: true, TENTATIVA: "MENSAL", ALERTA: alerta,
             PORQUE: nunca ? "nenhuma checagem bem-sucedida conhecida" : `ultima checagem ok em ${ult}, mes anterior` };
  }

  // SEMANAL: a ancora e o ultimo DIA declarado <= hoje.
  const alvo = DIAS_DA_SEMANA[cad.DIA];
  const ancora = somar(h, -((h.getUTCDay() - alvo + 7) % 7));
  const aIso = iso(ancora);
  if (!nunca && u >= ancora)
    return { DEVIDA: false, TENTATIVA: null, ALERTA: null,
             PORQUE: `ja checada com sucesso nesta semana (${ult} >= ${aIso})` };
  // Semana anterior tambem sem checagem ok: o alerta ja vinha de tras.
  const semanaPerdida = nunca || u < somar(ancora, -7);
  const alertaVelho = nunca ? "NUNCA_CHECADA_COM_SUCESSO" : semanaPerdida ? `SEM_CHECAGEM_OK_DESDE_${ult}` : null;
  if (iso(h) === aIso)
    return { DEVIDA: true, TENTATIVA: "PRIMARIA", ALERTA: alertaVelho, PORQUE: `dia declarado (${cad.DIA})` };
  const retentar = (cad.RETENTAR || []).map((r) => DIAS_DA_SEMANA[r]);
  const distancia = (h - ancora) / 864e5;
  // So se retenta DENTRO da semana da ancora e nos dias declarados: o dia
  // da retentativa tem de cair depois da ancora e antes da proxima.
  const ehRetentativa = retentar.some((r) => ((r - alvo + 7) % 7) === distancia && distancia > 0);
  const alerta = alertaVelho || `CHECAGEM_DE_${cad.DIA}_${aIso}_NAO_CONFIRMADA`;
  if (ehRetentativa)
    return { DEVIDA: true, TENTATIVA: "RETENTATIVA", ALERTA: alerta,
             PORQUE: `retentativa: nenhuma checagem ok desde a ancora ${aIso}` };
  // Fora da janela: nao se colhe, e o alerta CONTINUA ate a proxima ancora.
  return { DEVIDA: false, TENTATIVA: null, ALERTA: alerta,
           PORQUE: `fora da janela (${cad.DIA} + ${(cad.RETENTAR || []).join("/") || "sem retentativa"}); a proxima e a ${iso(somar(ancora, 7))}` };
}

// ── A ROTACAO DAS BULAS — QUAIS HOJE ────────────────────────────────────────
// D117.2: primeiro as DISPARADAS pelo diff (produto que mudou), depois a
// rotacao pela checagem mais antiga, ate MAX_POR_DIA — e nunca acima do que
// sobra do teto do DOMINIO nas 24 h (as bulas e o CSV do registo pagam o mesmo
// dominio registavel, `salute.gov.it`).
//
// `fila`: [{ ID, ULTIMA_CHECAGEM_OK }] (ULTIMA_CHECAGEM_OK null = nunca).
// `jaGastos`: pedidos ja feitos a este dominio nas ultimas 24 h.
// `reservaRobots`: pedidos a reservar para o robots.txt (1 se ainda nao lido).
// O CICLO e ESTIMATIVA — diz quantos dias a fila leva a MAX_POR_DIA, e nada mais.
export function planoDaRotacao({ cad, disparados = [], fila = [], jaGastos = 0, teto = 5, reservaRobots = 1 }) {
  const cabe = Math.max(0, Math.min(cad.MAX_POR_DIA, teto - jaGastos - reservaRobots));
  const vistos = new Set();
  const prioridade = [];
  for (const id of disparados) if (!vistos.has(id)) { vistos.add(id); prioridade.push({ ID: id, PORQUE: "DISPARADA_PELO_DIFF" }); }
  const rodada = fila.filter((f) => !vistos.has(f.ID))
    .sort((a, b) => (a.ULTIMA_CHECAGEM_OK == null ? -1 : 0) - (b.ULTIMA_CHECAGEM_OK == null ? -1 : 0)
      || String(a.ULTIMA_CHECAGEM_OK ?? "").localeCompare(String(b.ULTIMA_CHECAGEM_OK ?? ""))
      || String(a.ID).localeCompare(String(b.ID)))
    .map((f) => ({ ID: f.ID, PORQUE: f.ULTIMA_CHECAGEM_OK == null ? "ROTACAO_NUNCA_CHECADA" : `ROTACAO_ULTIMA_${soODia(f.ULTIMA_CHECAGEM_OK)}` }));
  const todos = [...prioridade, ...rodada];
  const total = new Set([...disparados, ...fila.map((f) => f.ID)]).size;
  return {
    HOJE: todos.slice(0, cabe),
    // O que nao coube NAO some: fica dito, e as disparadas vao a frente amanha.
    ADIADAS_DISPARADAS: prioridade.slice(cabe).map((p) => p.ID),
    ORCAMENTO: { TETO_DOMINIO_24H: teto, JA_GASTOS: jaGastos, RESERVA_ROBOTS: reservaRobots, MAX_POR_DIA: cad.MAX_POR_DIA, CABE_HOJE: cabe },
    CICLO_ESTIMADO_DIAS: total ? Math.ceil(total / cad.MAX_POR_DIA) : 0,
    CICLO_E: "ESTIMATIVA — dias para percorrer a fila a MAX_POR_DIA, se todo dia couber o maximo",
  };
}

// ── O FILTRO QUE O CORREDOR APLICA ─────────────────────────────────────────
// Sobre a populacao que o PORTAO ja deu. Quem nao declara CADENCIA passa (e o
// comportamento de sempre). Quem declara e nao e devida hoje sai, e fica DITO
// com o porque — uma fonte fora da cadencia calada le-se como fonte esquecida.
//
// `checagens`: { SOURCE_ID: "AAAA-MM-DD..." | null }, de leis/frescor_da_referencia.py.
// Se `checagens` for null (o dono da leitura nao respondeu), a cadencia NAO
// adivinha: a fonte com CADENCIA fica fora, com motivo NAO SEI — nao saber
// quando foi a ultima checagem nao e motivo para ir a fonte todo dia.
export function filtrarPorCadencia(ids, contratos, hoje, checagens) {
  const aColher = [], foraDaCadencia = {}, alertas = {};
  for (const id of ids) {
    const cad = contratos[id] && contratos[id].CADENCIA;
    if (!cad) { aColher.push(id); continue; }
    conferirCadencia(id, cad);
    if (checagens == null) { foraDaCadencia[id] = "NAO SEI — a ultima checagem ok nao pode ser lida; a cadencia nao adivinha"; continue; }
    const v = devidaHoje(cad, hoje, checagens[id] ?? null);
    if (v.ALERTA) alertas[id] = v.ALERTA;
    if (v.DEVIDA) aColher.push(id); else foraDaCadencia[id] = v.PORQUE;
  }
  return { aColher, foraDaCadencia, alertas };
}
