"""A Intelligence LÊ a referência da ADAMA. Não a copia, e não cunha nada nela.

    ESPECIE  PROVA DE CONSUMO. Nao e motor, nao e ferramenta, nao corre em
             producao. Mede uma relacao entre duas casas e escreve o veredito.

O QUE ESTE FICHEIRO **NÃO** É
-----------------------------
    NAO copia dados da referencia.      NAO escreve em `referencia/adama/`.
    NAO cria PRODUCT_ID.                NAO reconcilia produto com produto.
    NAO decide o que esta a venda.      NAO e a Intelligence Tool.

O PORQUÊ
--------
A Collection entrega **material admitido** — o que alguém observou. A referência
da ADAMA entrega **facto de catálogo e de registo** — o que é oficialmente
verdadeiro sobre os produtos no país observado. São matérias-primas diferentes,
e a Intelligence precisa das duas para cruzar.

O risco de ter as duas não é ler a mais: é **escrever**. Uma Intelligence que
cunhe o seu próprio identificador de produto cria uma segunda identidade
factual, e a partir daí ninguém sabe qual das duas manda.

    DUAS IDENTIDADES PARA A MESMA COISA NAO SAO REDUNDANCIA. SAO UM CONFLITO
    QUE AINDA NAO ACONTECEU.

Por isso a lei que esta prova impõe é a `INT-LAW-031`, que já existia e que a
espinha já escreve por extenso:

    A INTELLIGENCE NAO CUNHA IDENTIDADE UPSTREAM.

`ADAMA_PRODUCT_ID` é do `referencia/adama/PRODUCT-MASTER.json`, emitido em série
e append-only pelo `fontes/adama_referencia.py`. A Intelligence **cita-o**. Um
identificador citado e um identificador emitido não se parecem no ficheiro, mas
distinguem-se por uma pergunta só: se esta casa desaparecer, o ID continua a
existir? Se sim, é citação.

O QUE FICA POR FAZER, E ESTÁ DECLARADO
--------------------------------------
Ligar um item da Sala a um produto da referência exige uma chave que **hoje não
atravessa a fronteira** (`SUBJECT_ID` — EPPO, CAS, número de registo). Está em
`espinha_da_intelligence.CAMPOS_QUE_NAO_ATRAVESSAM`, e continua lá. Esta prova
mede que a referência está LEGÍVEL e que a lei de identidade se aguenta; **não**
afirma que o cruzamento já é possível.

    LER A REFERENCIA NAO E CRUZAR COM ELA.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASA = os.path.join(RAIZ, "referencia", "adama")

CONTRATO = "CONSUMO_DA_REFERENCIA_ADAMA/v1"

#: O dono do identificador do produto. Não é esta casa.
DONO_DO_PRODUCT_ID = "referencia/adama/PRODUCT-MASTER.json"
CONSTRUTOR_DA_REFERENCIA = "fontes/adama_referencia.py"

#: Os ficheiros que a Intelligence pode LER, e a chave que manda em cada um.
#: Copiada de `referencia/adama/CONTRATO-ADAMA-REFERENCE.md` — a tabela de
#: autoridade. Se a casa da ADAMA mudar de chave, esta cópia fica errada, e é
#: para ficar: é o mesmo desenho de `CAMPOS_DO_READY`.
AUTORIDADE = {
    "PRODUCT-MASTER.json": ("PRODUCTS", "ADAMA_PRODUCT_ID"),
    "PORTFOLIO.json": ("RECORDS", "ADAMA_PRODUCT_ID"),
    "REGISTRATIONS.json": ("RECORDS", "REGISTRATION_NUMBER"),
    "LABEL-DOCUMENTS.json": ("RECORDS", "DOCUMENT_ID"),
    "AUTHORIZED-USES.json": ("RECORDS", "USE_ID"),
    "ACTIVE-INGREDIENTS.json": ("RECORDS", "ACTIVE_INGREDIENT_ID"),
    "PRODUCT-ACTIVE-INGREDIENTS.json": ("RECORDS", "RELATION_ID"),
    "SNAPSHOTS.json": ("RECORDS", "SNAPSHOT_ID"),
    "SOURCE-ID-MAP.json": ("RECORDS", "LEGACY_SOURCE_ID"),
}

#: ⚠️ OS MÓDULOS DA INTELLIGENCE, DECLARADOS. `provas/` NÃO É SÓ DELA.
#: A mesma pasta guarda as provas de outras casas — `red_team_adama_referencia.py`
#: é do DONO da referência, e escreve lá dentro por direito: é um red team que
#: muta o ficheiro para provar que a suite apanha a mutação. Varrer `provas/`
#: inteira e chamar-lhe «a Intelligence» acusaria o dono de invadir a casa dele
#: próprio.
#:
#:     A PASTA NAO E O DONO. QUEM MORA NA MESMA RUA NAO E DA MESMA FAMILIA.
#:
#: Lista declarada, e não varrida, pelo mesmo motivo que `CAMPOS_DO_READY`:
#: quando mudar, tem de ser à mão, e à vista.
MODULOS_DA_INTELLIGENCE = (
    "controle/censo_do_controle.py",
    "controle/portao_do_controle.py",
    "controle/red_team_do_controle.py",
    "motor/corrida_da_inteligencia.py",
    "provas/arbitragem_da_intelligence.py",
    "provas/auditoria_agro_fronteira.py",
    "provas/consumo_da_referencia_adama.py",
    "provas/demanda_de_dados_da_italia.py",
    "provas/espinha_da_intelligence.py",
    "provas/modelo_de_objetos_da_intelligence.py",
)

#: O vocabulário da ignorância da casa da ADAMA. A Intelligence LÊ-O como
#: ignorância — nunca como negativo, nunca como ausência. É a `INT-LAW-112`, e
#: é a mesma palavra que a porta da Collection escreve.
NAO_SEI_DELES = ("UNKNOWN", "MULTIPLE", "NAO SEI")


class LeiViolada(Exception):
    """A prova recusou-se a dar por boa uma leitura. Diz porquê."""


def _ler(nome: str) -> Dict[str, Any]:
    caminho = os.path.join(CASA, nome)
    if not os.path.exists(caminho):
        raise LeiViolada(
            f"{nome} nao existe em referencia/adama/. A Intelligence NAO o "
            "escreve: quem o constroi e " + CONSTRUTOR_DA_REFERENCIA)
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def medir() -> Dict[str, Any]:
    """Mede a relação. Não altera nada, dos dois lados."""
    tabela: List[Dict[str, Any]] = []
    for nome, (campo, chave) in sorted(AUTORIDADE.items()):
        d = _ler(nome)
        linhas = d.get(campo)
        if not isinstance(linhas, list):
            raise LeiViolada(f"{nome}: esperava uma lista em `{campo}`")
        sem_chave = [i for i, x in enumerate(linhas) if chave not in x]
        if sem_chave:
            raise LeiViolada(
                f"{nome}: {len(sem_chave)} linhas sem a chave `{chave}` que o "
                "CONTRATO-ADAMA-REFERENCE.md diz que manda")
        tabela.append({"FICHEIRO": nome, "CHAVE": chave,
                       "LINHAS": len(linhas),
                       "DECLARADO": d.get("COUNT")})

    mestre = _ler("PRODUCT-MASTER.json")
    ids = [p["ADAMA_PRODUCT_ID"] for p in mestre["PRODUCTS"]]
    return {
        "CONTRATO": CONTRATO,
        "PAPEL_DA_INTELLIGENCE": "CONSUMIDOR",
        "DONO_DO_PRODUCT_ID": DONO_DO_PRODUCT_ID,
        "CUNHA_IDENTIDADE": False,
        "COPIA_DADOS": False,
        "TABELA": tabela,
        "PRODUTOS": len(ids),
        "IDS_UNICOS": len(set(ids)) == len(ids),
        "VOCABULARIO_DE_IGNORANCIA": list(NAO_SEI_DELES),
        "CRUZAMENTO_POSSIVEL_HOJE": False,
        "PORQUE_NAO": ("falta `SUBJECT_ID` na fronteira da Sala: sem chave do "
                       "sujeito, ligar item a produto seria palpite"),
    }


def main() -> int:
    r = medir()
    print(f"{r['CONTRATO']} · papel={r['PAPEL_DA_INTELLIGENCE']}")
    for t in r["TABELA"]:
        print(f"  {t['FICHEIRO']:34} {t['CHAVE']:22} {t['LINHAS']:>5} linhas")
    print(f"  produtos={r['PRODUTOS']} ids_unicos={r['IDS_UNICOS']} "
          f"cunha_identidade={r['CUNHA_IDENTIDADE']}")
    print(f"  cruzamento possivel hoje: {r['CRUZAMENTO_POSSIVEL_HOJE']} "
          f"— {r['PORQUE_NAO']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
