"""D32 (4): os estados que a decisao nomeia, aplicados NUMA COPIA do livro do robo, pela porta
`lifecycle.registar` (a mesma fronteira de owner; transicao ilegal falha fechada).

  IT-T3-024 Campania autorizacoes  -> AUTH_BLOCK                    (servico com SPID/accedi)
  IT-T3-022 SFR Lombardia          -> CONTRACT_READY_ROUTE_BLOCKED  (robots, pela leitura da casa)
  IT-T2-109 Campania agrometeo     -> sem mudanca de estado: receita de tabela proposta (JSON ao lado)
  IT-T3-014 SFN                    -> sem mudanca de estado: canario PDF passou NA COPIA; o READY
                                      espera a linha do coletor dizer PDF (porta do dono)

uso: py provas/ia_cur/d32_bloco4.py <livro copiado.json> <saida.json>"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import lifecycle as LC   # noqa: E402

LIVRO, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
assert "source-curator-service" not in str(LIVRO).replace("\\", "/"), "so em copia"
LC.LIVRO = LIVRO

PAG = "provas/ia_cur/PAGINAS-LIDAS-COM-REDE.jsonl"
MUDAR = [
    ("IT-T3-024", LC.AUTH_BLOCK,
     "D32 (4): a entrada e o sistema de gestao de autorizacoes fitossanitarias (RUOP) da Regione "
     "Campania; o servico abre por SPID/«Accedi» — conteudo atras de login. Fora, sem contorno.",
     PAG + "#IT-T3-024 sha256 c2df2c1b24142dcd2747ba5186859be3a20a398284fea8f9c83bd4902fecae0d"),
    ("IT-T3-022", LC.CONTRACT_READY_ROUTE_BLOCKED,
     "D32 (4): a raiz redireciona para /wps/portal/site/sfr e o robots tem «Disallow: /wps/» "
     "antes de «Allow: /wps/portal/site/sfr»; o leitor da casa (urllib.robotparser, primeira "
     "regra que casa) proibe. ATENCAO: pela RFC 9309 (regra mais especifica) o caminho e "
     "PERMITIDO — ver ACHADO_ROBOTS na saida. Fora, sem contorno, ate o dono decidir.",
     PAG + "#IT-T3-022 sha256 6e8c19a0ead51a2fa1ef528f0f6302cca024c23a2399e48e6d09573a3bf5e809"),
]
feitas = []
for sid, novo, porque, ev in MUDAR:
    antes = LC.estado_de(sid)
    linha = LC.registar(sid, novo, porque, evidence_ref=ev, extra={"DECISAO": "D32 (4)"})
    feitas.append({"SOURCE_ID": sid, "ANTES": antes, "DEPOIS": linha["NEW_STATE"]})
    print(sid, antes, "->", linha["NEW_STATE"])

saida = {"ONDE": "COPIA do livro vivo — nada instalado", "LIVRO_DA_COPIA": str(LIVRO),
         "TRANSICOES": feitas,
         "SEM_MUDANCA": {
             "IT-T2-109": "receita de tabela proposta: provas/ia_cur/RECEITA-CAMPANIA-AGROMETEO.json",
             "IT-T3-014": "canario PDF PASS na copia (provas/ia_cur/CANARIO-SFN-PDF.json); READY so "
                          "quando a linha do coletor disser OUTPUT_TYPE=PDF (onboardar_rotas_provadas)"},
         "ACHADO_ROBOTS": {
             "HOST": "www.fitosanitario.regione.lombardia.it",
             "ROBOTS": ["User-agent: *", "Disallow: /wps/", "Allow: /wps/portal/site/sfr",
                        "Allow: /wps/wcm/connect", "Crawl-delay: 1"],
             "LEITOR_DA_CASA": "urllib.robotparser: primeira regra que casa -> /wps/portal/site/sfr PROIBIDO",
             "RFC_9309": "regra mais especifica (a mais longa) vence -> /wps/portal/site/sfr PERMITIDO",
             "ONDE_A_CASA_LE_ASSIM": ["curadoria/gate_de_rota.py", "curadoria/descobrir.py",
                                      "coleta/scrap_http.py"],
             "DECISAO_PEDIDA": "manter o bloqueio (lado seguro) ou ler robots pela RFC 9309 em toda a casa"}}
SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
