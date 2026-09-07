// PERFIS OPERACIONAIS. Um perfil diz QUAIS fontes uma execucao agendada pode tocar.
// Guarda impede que uma quarta fonte entre calada no perfil forward-only-live.

export const PROFILES = {
  "forward-only-live": {
    descricao: "as tres fontes cuja evidencia DESAPARECE se nao for preservada no dia",
    SOURCES: ["IT-T3-005", "IT-T2-002", "IT-T2-004"],
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
