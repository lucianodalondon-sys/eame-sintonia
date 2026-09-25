"""As respostas do agente (claude-opus-5-5, assinatura) ao LOTE-20260925T072003Z — 30 casos de janela D29.
Cada uma cita TODAS as paginas que o robo trouxe para o caso (o ingerir confere URL + sha256)."""
import json

L = "C:/cur/banc30-lotes/LOTE-20260925T072003Z/LOTE.json"
lote = json.load(open(L, encoding="utf-8"))

R = {  # CASO -> (CLASSE, PORQUE)
    "IT-T1-006": ("ROTA_FIXA", "a pagina E o boletim agrometeorologico e fitossanitario (agrumi, olivo), actualizado no mesmo endereco; nao ha lista de itens"),
    "IT-T2-109": ("FOLHA_XLSX", "os dados sao folhas Excel semanais por estacao (medido em D32 4); a colheita de folha de calculo nao existe"),
    "IT-T2-132": ("CASCA_VAZIA", "a entrada devolve 293 bytes com 1 ligacao (redireccionamento/JS); nada para ler"),
    "IT-T2-133": ("ROTA_FIXA_PDF", "pagina de servico; o boletim e UM pdf fixo (meteo.regione.marche.it/assets/previsioni/bollettino.pdf)"),
    "IT-T2-134": ("SEM_ITENS_NO_HTML", "so ligacoes de menu (amministrazione trasparente); as publicacoes agrometeo nao estao no HTML"),
    "IT-T2-136": ("ROTA_FIXA", "a pagina agrometeo e o proprio boletim; a pagina extra pedida e a mesma"),
    "IT-T2-138": ("ROTA_FIXA", "mapas semanais (imagens) numa pagina fixa; 0 itens"),
    "IT-T2-139": ("ROTA_FIXA", "previsao agrometeo numa pagina fixa; 0 itens"),
    "IT-T2-147": ("NAO_SEI", "a pagina de boletins so lista PDFs de neve; o boletim agrometeo nao aparece nas 2 paginas lidas"),
    "IT-T2-148": ("ROTA_FIXA", "a pagina E o boletim (irma de IT-T1-006: arsacweb.it e arsac.calabria.it publicam o mesmo boletim)"),
    "IT-T2-149": ("LIGACOES_MORTAS", "as noticias ?p=N devolvem 404 (?p=1454 no reparo, ?p=1529 aqui)"),
    "IT-T2-150": ("JAVASCRIPT", "a home so tem menu (node/N); os boletins sao um modulo JS (Bollettini.css)"),
    "IT-T2-151": ("JAVASCRIPT", "/bollettini tem 0 caracteres em paragrafo e o modulo Bollettini em JS: a lista nao esta no HTML"),
    "IT-T2-152": ("ROTA_FIXA", "o boletim agrometeorologico de Firenze e a propria pagina; as familias sao o menu do LaMMA"),
    "IT-T2-153": ("ROTA_FIXA", "o CAAR publica boletins em paginas fixas por cultura (bollettino-di-viticoltura.html, -olivicoltura, ...): varias rotas fixas, nao uma lista"),
    "IT-T2-158": ("SITE_ENCERRADO", "a entrada diz «Fine vita del sito web del SIARL»"),
    "IT-T3-013": ("JAVASCRIPT", "a pagina dos boletins interprovinciais e uma aplicacao (static/js): os boletins nao estao no HTML"),
    "IT-T3-014": ("ITENS_PDF", "10 DTU em PDF na entrada; receita PDF: INDEX https://www.protezionedellepiante.it/category/documenti-tecnici-ufficiali/ LINK_PATTERN ^https?://(www\\.)?protezionedellepiante\\.it/wp-content/uploads/\\d{4}/\\d{2}/dtu-[^/?#]+\\.pdf(\\?|#|$) — canario PDF ja PASS em D32 (4); precisa OUTPUT_TYPE=PDF"),
    "IT-T3-015": ("FONTE_GENERICA", "«Approfondimenti» da Regione Toscana: pagina geral, 0 caracteres em paragrafo, sem boletins fitossanitarios"),
    "IT-T3-016": ("NAO_SEI", "pagina de assinatura de newsletters; os numeros nao estao na pagina"),
    "IT-T3-018": ("JAVASCRIPT", "news-e-eventi com 0 caracteres em paragrafo: lista montada por JS"),
    "IT-T3-019": ("FONTE_GENERICA", "pagina de projectos de investigacao; nao publica boletins"),
    "IT-T3-022": ("ESPERA_ROBOTS_RFC", "a entrada (139 bytes) salta para /wps/portal/site/sfr, que o leitor de robots de hoje diz proibido e a RFC 9309 diz permitido (D34/D39, robots-rfc9309-v1, por instalar)"),
    "IT-T3-024": ("SERVICO_COM_LOGIN", "sistema de autorizacoes RUOP com SPID (AUTH_BLOCK decidido em D32 4)"),
    "IT-T3-025": ("ITENS_PDF", "a entrada lista 5 provincias; cada uma lista os boletins em PDF (NA: 27). Receita PDF por provincia: INDEX .../bollettini_2026/NA_2026.html LINK_PATTERN ^https?://www\\.agricoltura\\.regione\\.campania\\.it/difesa/bollettini/bollettini_2026/pdf/NA-\\d{2}-\\d{2}\\.pdf$ — precisa OUTPUT_TYPE=PDF e 5 rotas (uma por provincia)"),
    "IT-T3-026": ("JAVASCRIPT", "SIMfito: os boletins vem de template.html por JS"),
    "IT-T3-027": ("ITENS_PDF", "23 boletins em PDF na entrada; receita PDF: INDEX http://www.ersa.fvg.it/cms/aziende/in-formazione/Bollettini/index.html LINK_PATTERN ^https?://www\\.ersa\\.fvg\\.it/(cms/)?aziende/bollettini-(integrata|biologica)/.+\\.pdf$ — precisa OUTPUT_TYPE=PDF"),
    "IT-T3-028": ("JAVASCRIPT", "boletins territoriais: aplicacao (static/js); o item do canario era outra pagina de servico"),
    "IT-T3-029": ("PAGINAS_TEMATICAS", "18 paginas informativas fixas por praga (colpo di fuoco, flavescenza...): conteudo de referencia, nao publicacao datada"),
    "IT-T3-031": ("ROTA_FIXA", "pagina informativa de vigilancia do territorio; so familias de paginas fixas (modulistica)"),
}
out = []
for c in lote["CASOS"]:
    classe, porque = R[c["CASO"]]
    lidas = [p["URL"] for p in c["PAGINAS"] if p.get("SHA256")]
    out.append({"CASO": c["CASO"], "RESPOSTA": "SEM_RECEITA", "PAGINAS_LIDAS": lidas,
                "PORQUE": "[%s] %s" % (classe, porque)})
assert len(out) == len(lote["CASOS"]) == 30
json.dump(out, open("C:/cur/banc30-lotes/respostas1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print(collections.Counter(R[c][0] for c in R).most_common())
