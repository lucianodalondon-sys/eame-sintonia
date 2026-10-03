// PERFIS OPERACIONAIS. Um perfil diz COMO uma execucao agendada colhe —
// horario, fuso, zonas. NAO diz QUEM: isso passou a ser pergunta ao portao.
//
// ⚠️ A LISTA FIXA SAIU DAQUI EM 2026-09-22 (cutover, Fase 5).
// Estava escrita `SOURCES: ["IT-T3-005", "IT-T2-002", "IT-T2-004"]` e nunca
// tinha falado com o livro do Curator. Medido no dia em que se perguntou:
// IT-T3-005 estava em SEMANTIC_REVIEW (nunca promovida) e IT-T2-002 e
// IT-T2-004 estavam READY_LEGACY (promovidas pela regua antiga, antes de
// existir gate de detalhe). Nenhuma das tres era elegivel, e a lista dizia
// que as tres eram.
//
//     UMA LISTA ESCRITA A MAO NAO ENVELHECE COM O LIVRO.
//     NO DIA SEGUINTE ELA E UM CARIMBO VELHO COM CARA DE DECISAO.
//
// A populacao vem agora de `curadoria/collection_gate.py`, que e o dono
// unico da regra. A regra NAO e copiada para JavaScript: uma segunda copia
// da lei envelhece sozinha e diverge em silencio.

export const PROFILES = {
  "forward-only-live": {
    descricao: "coleta operacional diaria: quem entra e quem o portao do Curator admite hoje",
    //: De onde sai a populacao. Ler este campo e OBRIGATORIO antes de colher:
    //: um perfil sem ele nao diz de onde vem a populacao, e um coletor que
    //: adivinhe volta a ter lista fixa — desta vez escondida no coletor.
    POPULACAO: "COLLECTION_GATE",
    OPS_BRANCH: "ops/italy-forward-only-live",
    SCHEDULER_TIMEZONE: "Europe/Rome",
    OPERATIONAL_COLLECTION_HOUR: 20,
    aviso_de_horario: "20:00 = OPERATIONAL_COLLECTION_TIME. NAO e SOURCE_DECLARED_PUBLICATION_TIME. Nao sabemos a que horas as fontes publicam.",
    ARPAV_OPERATIONAL_ZONES: {
      numeradas: 32,
      publicadas: 29,
      nao_publicadas: [17, 18, 19],
      medido: "as zonas 17, 18 e 19 devolvem HTTP 404 com 564 bytes, de forma consistente. Isso e fato da fonte, nao falha nossa.",
      decisao: "operar com as 29 publicadas",
      custo_medido_por_execucao: "13.373.903 bytes (~12,8 MB) para as 32 tentativas",
      por_que_29_e_nao_4: "o contrato ja provou que cada zona e uma versao independente (hashes e CreationDate diferentes) e que as URLs sao previsiveis. Com 4 zonas nao se pode dizer 'Veneto capturado'.",
      ressalva_de_crescimento: "em dia sem mudanca o resultado e SEEN_AGAIN e ZERO bytes novos sao guardados. So publicacao real gera bytes. A ARPAV declara 2x por semana na temporada, entao a estimativa e ~13 MB x 2 por semana, nao por dia."
    }
  }
};

export const PERFIL_PADRAO = "forward-only-live";
