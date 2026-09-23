"""D15: candidata LinkedIn/Instagram fica POLICY_BLOCK, com o trecho dos termos como prova.

    py ferramentas/unificacao/aplicar_d15_politica.py [--escrever] [--porta FICHEIRO]

A ponte (curadoria/ponte_candidatas.py) escrevia RECUSADA para LinkedIn e Instagram;
desde a D15 escreve POLICY_BLOCK. Esta ferramenta corrige as linhas ja escritas pela
MESMA regra: TIPO LINKEDIN ou INSTAGRAM e ESTADO que nao seja POLICY_BLOCK nem PROMOVIDA.

- a prova passa a ser o trecho dos termos (candidatas/PROVA-TERMOS-REDES-SOCIAIS-V1.json:
  endereco, data em vigor, data de leitura, sha256 da pagina guardada);
- a EVIDENCIA antiga (a sonda de 14/09, com o 429) fica em EVIDENCIA_HISTORICA — 429 e
  «demasiados pedidos», nao «proibido»;
- o motivo passa de MOTIVO_DA_RECUSA para MOTIVO_DO_BLOQUEIO; a linha ganha
  D15 = {ESTADO_ANTERIOR, MOTIVO_ANTERIOR, QUANDO, DECISAO}. Nada se apaga.
Idempotente. Sem --escrever so conta. Grava pelo dono da porta (fonte_nova.gravar).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "candidatas"))
import fonte_nova as FN  # noqa: E402

TIPOS = ("LINKEDIN", "INSTAGRAM")
MOTIVO = {"LINKEDIN": "LINKEDIN_POLICY: coleta automatizada proibida pelos TOS da plataforma.",
          "INSTAGRAM": "INSTAGRAM_POLICY: coleta automatizada proibida pelos TOS da plataforma."}


def aplicar(doc: dict) -> list[str]:
    mudadas = []
    for c in doc["CANDIDATAS"]:
        if c.get("TIPO") not in TIPOS or c.get("ESTADO") in ("POLICY_BLOCK", "PROMOVIDA"):
            continue
        ev = FN.evidencia_da_politica(c["TIPO"])
        if ev is None:
            raise SystemExit("sem prova dos termos para %s: nada escrito" % c["TIPO"])
        anterior = c.get("MOTIVO_DA_RECUSA")
        c["D15"] = {"ESTADO_ANTERIOR": c["ESTADO"], "MOTIVO_ANTERIOR": anterior,
                    "QUANDO": datetime.now(timezone.utc).isoformat(),
                    "DECISAO": "D15 (DECISOES-DONO-2026-09-23, linha 144): POLICY_BLOCK pelos termos"}
        if c.get("EVIDENCIA"):
            c.setdefault("EVIDENCIA_HISTORICA", c["EVIDENCIA"])
        c["ESTADO"] = "POLICY_BLOCK"
        c["MOTIVO_DO_BLOQUEIO"] = (anterior or MOTIVO[c["TIPO"]]).split(" Worker marcado")[0]
        c["MOTIVO_DA_RECUSA"] = None
        c["EVIDENCIA"] = FN.texto_da_evidencia(ev)
        c["EVIDENCIA_POLITICA"] = ev
        mudadas.append(c["CANDIDATA_ID"])
    if any(c.get("ESTADO") == "POLICY_BLOCK" for c in doc["CANDIDATAS"]):
        doc.setdefault("ESTADOS", {}).setdefault("POLICY_BLOCK", FN.ESTADO_POLICY_BLOCK)
    return mudadas


if __name__ == "__main__":
    if "--porta" in sys.argv:
        FN.FILA = Path(sys.argv[sys.argv.index("--porta") + 1])
    doc = FN.carregar()
    m = aplicar(doc)
    print(json.dumps({"MUDADAS": len(m), "PROXIMA_EXPANSAO_PEOPLE_SOCIAL":
                      sum(1 for c in doc["CANDIDATAS"] if c.get("ESTADO") == "POLICY_BLOCK")},
                     ensure_ascii=False))
    if "--escrever" in sys.argv and m:
        FN.gravar(doc)
