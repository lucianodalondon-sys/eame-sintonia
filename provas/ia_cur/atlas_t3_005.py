"""D32 (3): a ficha do Atlas de IT-T3-005 (Terre dell'Etruria, boletim da mosca-da-azeitona) pela
PORTA CANONICA `curadoria/escrever_no_atlas.ficha` — acrescenta, nunca reescreve.

So o que esta medido: a pagina primaria e os 139 pontos de armadilha do manifesto da casa
(`data/samples/ITALY-T3-005-MONITORAGGIO/MANIFEST.json`, 07/09, robots Allow, duas colheitas com
sha256 identico) e o boletim que a BCR guardou (periodo 07-09 a 13-09-2026). O resto fica NAO SEI.
A linha EVIDENCE da porta cita o manifesto do onboarding em lote; aqui aponta para o manifesto
verdadeiro desta fonte (a unica linha que se corrige, e diz-se porque).
uso: py provas/ia_cur/atlas_t3_005.py"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "curadoria"))
import emparelhar_com_atlas as EM    # noqa: E402
import escrever_no_atlas as EA       # noqa: E402

SID = "IT-T3-005"
if SID in {a["SOURCE_ID"] for a in EM.ler_atlas(do_disco=True)}:
    sys.exit("%s ja tem ficha no Atlas: nada a escrever" % SID)

n = {"SOURCE_ID": SID, "TERRITORY": "T3", "MESMA_ORGANIZACAO": None}
f = {
    "FAMILY": "HTML_SITE",
    "NOME": "Terre dell'Etruria — Monitoraggio mosca dell'olivo (Servizio Agronomico)",
    "URL": "https://www.terretruria.it/monitoraggio",
    "SAMPLE_ITEMS": [{"TITLE": "Bollettino del periodo dal 07-09-2026 al 13-09-2026 — monitoraggio mosca dell'olivo",
                      "PUBLISHED_AT": "2026-09-07"}],
    "REPRESENTATIVE_SAMPLE_COUNT": 1,
    "SAMPLE_PERIOD_START": "2026-09-07", "SAMPLE_PERIOD_END": "2026-09-13",
    "TOPICS_OBSERVED": ["mosca dell'olivo (monitoraggio voli e infestazione attiva)", "fase fenologica",
                        "clima", "difesa: caolino e adacquamenti"],
    "GEOGRAPHIES_OBSERVED": ["Toscana"],
    "CROPS_OBSERVED": ["olivo"],
    "DATE_PRESENT_COUNT": 1,
    "ACTIVITY": "ACTIVE_HIGH_FREQUENCY",
    "HISTORICAL_DEPTH_OBSERVED": "NAO SEI - so o boletim corrente e o seguinte foram vistos",
    "INITIAL_COLLECTION_CADENCE": "SEMANAL NA ESTACAO",
    "CADENCE_REASON": "um boletim por periodo semanal; o proprio site avisa que o monitoramento para fora da estacao",
    "EXPECTED_ITEMS_PER_WEEK": "1",
    "RELEVANT_TO_SINTONIA": "SIM - janela de cultura (D29): mosca-da-azeitona, 139 pontos de armadilha",
    "SOURCE_PATTERN_STABLE": "NAO SEI - 1 boletim visto",
    "CANONICAL_EXAMPLE": "data/samples/ITALY-T3-005-MONITORAGGIO/MANIFEST.json",
}
bloco = EA.ficha(n, f, None)
velho = "(sha256 em curadoria/REAL-EXAMPLE-MANIFEST-V1.json)"
assert bloco.count(velho) == 1
bloco = bloco.replace(velho, "(sha256 no proprio manifesto; boletim BCR 07-13/09 tambem guardado no acervo)")
# as frases fixas da porta que nao sao verdade para ESTA fonte (onboarding em lote != piloto):
for de, para in (
        ("HTTP publico - descoberta por padrao de link na entrada",
         "HTTP publico - pagina fixa /monitoraggio, atualizada por periodo"),
        ("CONTRATO ESCRITO E CANARIO CORRIDO - ver curadoria/italy_contracts_curator.json",
         "COLHIDA COM SUCESSO NA BCR - contrato escrito a mao em regras/ (piloto), nao no livro do robo")):
    assert bloco.count(de) == 1, de
    bloco = bloco.replace(de, para)
cab = ("\n---\n\n## D32 (3) — ficha pela porta canonica, 2026-09-24\n\n"
       "*Proposta do agente IA-CUR, decidida pelo bot Luciano por delegacao (D32). Fonte ja colhida com "
       "sucesso pela BCR; faltava a ficha. Os campos a `NAO SEI` sao medidas que faltam.*\n\n")
txt = EA.ATLAS.read_text(encoding="utf-8")
EA.ATLAS.write_text(txt.rstrip() + "\n" + cab + bloco, encoding="utf-8")
print(bloco)
print("Atlas: %s tem ficha agora: %s" % (SID, SID in {a["SOURCE_ID"] for a in EM.ler_atlas(do_disco=True)}))
