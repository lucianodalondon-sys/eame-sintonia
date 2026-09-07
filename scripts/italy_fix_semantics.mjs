// FECHAMENTO — quatro correcoes semanticas nos manifestos e no JSON mestre.
// Nao toca em nenhum byte de amostra. So em campos de classificacao.
import { readFileSync, writeFileSync } from "node:fs";

const patch = (p, f) => { const o = JSON.parse(readFileSync(p, "utf8")); f(o); writeFileSync(p, JSON.stringify(o, null, 1)); console.log("corrigido", p); };
const S = id => `data/samples/IT-SOURCE-SAMPLES/${id}/MANIFEST.json`;

// A · Ministero della Salute — e fonte REGULATORIA PRIMARIA, nao apenas descoberta/identidade
patch(S("IT-T4-001"), m => {
  m.TERRITORY = "T4";
  m.OWNER_KIND = "OFFICIAL_NATIONAL_AGENCY";
  m.SOURCE_ROLE = "REGULATORY_PRIMARY";
  m.SOURCE_ROLE_SECUNDARIO = "tambem serve como IDENTITY_SOURCE (quem e o titular do registro) e VALIDATION_SOURCE (confere o que uma empresa afirma). Mas isso e uso secundario.";
  m.CORRECAO_2026_09_07 = "a rodada anterior descreveu esta fonte como 'so descoberta e identidade'. ERRADO. E o registro oficial de autorizacao: T4 REGULATORY, OWNER_KIND OFFICIAL_NATIONAL_AGENCY, ROLE REGULATORY_PRIMARY. E a fonte que separa COMPANY_CLAIM de REGULATORY_FACT — nao um catalogo de nomes.";
});

// B · Giornate Fitopatologiche / AIPP — tres territorios pelas tres rotas, e dois owners
patch(S("IT-T5-003"), m => {
  m.TERRITORY = "T5";
  m.TERRITORIOS_ALIMENTADOS = {
    T5: "SCIENCE — o bilancio fitossanitario e evidencia cientifica/retrospectiva de campanha (esta amostra)",
    T6: "RESEARCHERS — o PDF traz nome, e-mail institucional, orgao e regiao de quem assina (Antonietta Altieri, Ufficio Fitosanitario Regione Basilicata)",
    T11: "EVENTS — o ciclo 'I Giovedi dell'AIPP' e as Giornate Fitopatologiche sao evento, com data e sessao",
    regra: "MESMA ORIGEM, TRES LEITURAS. Nao duplicar a fonte: um SOURCE_ID, tres territorios alimentados, com a origem unica preservada."
  };
  m.SOURCE_ROLE = "SCIENCE_SOURCE + IDENTITY_SOURCE (pesquisador) + VALIDATION_SOURCE";
  m.OWNERS_SEPARADOS = {
    "IT-OWN-AIPP": { nome: "AIPP — Associazione Italiana per la Protezione delle Piante", OWNER_KIND: "TRADE_ASSOCIATION", papel: "hospeda os PDFs (aipp.it) e organiza o ciclo 'I Giovedi dell'AIPP'" },
    "IT-OWN-GIORNATE-FITO": { nome: "Giornate Fitopatologiche", OWNER_KIND: "CONSORTIUM", papel: "o evento cientifico, com site proprio (giornatefitopatologiche.it)" },
    evidencia_da_separacao: "o link esta em giornatefitopatologiche.it, mas os PDFs moram em aipp.it/wp-content/uploads/. Sao DUAS entidades; nao fundir.",
    aviso: "ambos os OWNER_KIND acima sao provisorios — nao foram medidos no estatuto de cada entidade nesta rodada"
  };
  m.CORRECAO_2026_09_07 = "a rodada anterior descreveu esta fonte como 'so descoberta e identidade'. ERRADO. E ciencia (T5), alimenta pesquisadores (T6) e e evento (T11).";
});

// C · ARPAE — clima e clima. Nao vira ocorrencia de praga.
patch(S("IT-T2-001"), m => {
  m.TERRITORY = "T2";
  m.EVIDENCE_CLASS = "AGROCLIMATIC_SIGNAL";
  m.LEI_DE_NAO_PROMOCAO = {
    regra: "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE",
    o_que_pode: "contribuir para interpretar pressao agronomica — explicar por que a praga apertou ou afrouxou",
    o_que_nao_pode: "ser lido, sozinho ou combinado, como ocorrencia de praga. Chuva e temperatura nao sao inseto.",
    correcao: "a redacao anterior classificava esta amostra como OBSERVED_FIELD_SIGNAL, o que abria porta para promocao indevida. Corrigido para AGROCLIMATIC_SIGNAL."
  };
  m.WHAT_IT_DOES_NOT_PROVE = "presenca de praga · ocorrencia fitossanitaria · risco modelado de praga · decisao de tratamento · dado por talhao. AGROCLIMATIC_SIGNAL nunca vira PEST_OCCURRENCE.";
});

// D · os quatro estados, com os numeros reais
patch("data/samples/ITALY-SOURCE-MASTER-V1.json", d => {
  d.estados_de_cobertura_2026_09_07 = {
    porque_existe: "a frase 'as outras 47 continuam sem teste' era ambigua e ERRADA. Fonte cuja porta ja foi medida nao e fonte 'nao testada'. Estes sao os quatro estados, com os numeros reais.",
    ROTAS_NO_CATALOGO: 54,
    ROUTE_PROBED: { n: 51, o_que_significa: "a porta foi medida do IP italiano: codigo HTTP, tamanho, tipo de conteudo, e classificacao de acesso" },
    SAMPLE_CAPTURED: { n: 7, o_que_significa: "um documento real foi baixado, alem da homepage" },
    RAW_PRESERVED: { n: 7, o_que_significa: "o documento esta no disco com MIME, BYTES e SHA256 no manifesto, e o hash confere contra os bytes" },
    ANALYTICALLY_CLASSIFIED: { n: 7, o_que_significa: "tem veredito, prioridade, recorrencia, o que prova e o que NAO prova escritos a mao" },
    NUNCA_TOCADAS: { n: 3, quais: ["IT-T3-003", "IT-T3-010", "IT-T7-012"], motivo: "o catalogo nao tem URL utilizavel para elas — o campo URL e 'NÃO SEI'" },
    PROBADAS_SEM_AMOSTRA: { n: 44, o_que_significa: "porta medida, documento nao capturado. NAO sao 'nao testadas'; sao 'testadas na porta, nao na entrega'." },
    aviso: "51 + 3 = 54. As 7 com amostra estao DENTRO das 51 probadas, nao sao um grupo separado."
  };
});

// e a lei permanente
patch("data/samples/ITALY-SOURCE-MASTER-V1.json", d => {
  d.leis_permanentes = d.leis_permanentes || {};
  d.leis_permanentes.ROUTE_NOT_FOUND_NAO_E_SOURCE_BLOCKED = {
    lei: "ROUTE_NOT_FOUND != SOURCE_BLOCKED",
    lei_irma: "OLD_URL_FAILURE != CURRENT_SOURCE_FAILURE",
    de_onde_veio: "nesta rodada, 7 supostos bloqueios eram endereco errado no nosso proprio catalogo: um 'www' a mais (Campania), um host morto (publications.fmach.it), um caminho antigo (ARPAE 404). Se ninguem conferisse, virariam 'a Italia bloqueia'.",
    antes_de_escrever_BLOCKED_e_obrigatorio: [
      "1 · verificar o dominio oficial",
      "2 · localizar a pagina canonica atual",
      "3 · conferir redirects",
      "4 · procurar o link atual a partir da homepage ou da busca do proprio site",
      "5 · so entao registrar bloqueio"
    ],
    consequencia: "erro de catalogo NOSSO nunca vira defeito DA FONTE",
    lei_relacionada: "BLOCKED_EM_CURL_ITALIANO != BLOCKED_EM_BROWSER_ITALIANO (ver fase_C_D_executada_2026_09_07.regra_de_assimetria_do_curl)"
  };
});
