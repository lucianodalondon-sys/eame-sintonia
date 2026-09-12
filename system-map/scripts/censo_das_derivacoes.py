# -*- coding: utf-8 -*-
"""CENSO DAS DERIVAÇÕES — o que esta casa produz a partir do que colheu.

POR QUE ISTO VEM ANTES DA TABELA
--------------------------------
`derived_artifact` é a única tabela que sobreviveu a quatro missões de medição.
Isso não autoriza desenhá-la de cabeça. Desenhar primeiro e medir depois é como
se mede o buraco pelo tamanho da tampa que já se comprou.

Este ficheiro pergunta ao repositório, e não à memória:

    quem produz derivado?
    de que espécie é cada saída?
    que identidade cada uma consegue provar hoje?

A ARMADILHA QUE ELE EXISTE PARA EVITAR
--------------------------------------
Chamar tudo de derivado. «Derivado» não é «tudo o que não é o PDF original»:

    RAW_CAPTURE        veio da fonte como está. A legenda que o YouTube
                       entregou junto com o vídeo NÃO foi produzida por nós.
    DERIVED_ARTIFACT   nós produzimos, a partir de bytes que guardámos.
    STRUCTURED_RECORD  uma linha normalizada. Tem outra casa no banco.
    CLAIM / FACT       o que o texto AFIRMA. Espécie de outro andar, e a
                       COL-LAW-502 existe para não deixar confundir.

Meter uma legenda do YouTube em `derived_artifact` diria que nós a produzimos.
Diria mal, e a partir daí a linhagem mentiria para toda a gente.

O QUE ESTE CENSO NÃO FAZ
------------------------
Não escreve no banco, não aplica migration, não copia byte. Ele mede — e o
desenho da tabela vem depois, cabendo no que se mediu.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REGISTO = os.path.join("data", "derivados", "REGISTO-DE-ARTEFATOS.json")
CONTRATO = os.path.join("leis", "artefato.py")

# ─────────────────────────────────────────────────────────────────────────
# OS PRODUTORES, medidos e classificados um a um
# ─────────────────────────────────────────────────────────────────────────
# Cada entrada é uma AFIRMAÇÃO VERIFICÁVEL: o ficheiro tem de existir, e o
# censo confere. A classificação da espécie é a parte que exige leitura humana
# — e por isso ela fica escrita aqui, ao lado do ficheiro que a sustenta, e não
# adivinhada por uma expressão regular.
PRODUTORES = [
    {
        "PRODUTOR": "coleta/executor_texto_de_pdf.py",
        "ENTRADA": "PDF preservado (RAW)",
        "SAIDA": "texto simples",
        "FORMATO": "text/plain",
        "ESPECIE": "DERIVED_ARTIFACT",
        "PORQUE": ("nos produzimos, a partir de bytes que guardamos. Declara pai, "
                   "tipo de derivacao, executor e versao — e escreve em "
                   "data/derivados/."),
        "FERRAMENTA": "texto-de-pdf",
        "TEM_VERSAO": True,
        "TEM_PAI": True,
        "TEM_QUANDO": True,
    },
    {
        "PRODUTOR": "coleta/pdf_text.py",
        "ENTRADA": "PDF",
        "SAIDA": "texto simples",
        "FORMATO": "text/plain",
        "ESPECIE": "BIBLIOTECA",
        "PORQUE": ("nao e produtor: e a biblioteca que o executor usa. Nao escreve "
                   "artefato nenhum, e nao entra na tabela."),
        "FERRAMENTA": None,
        "TEM_VERSAO": False,
        "TEM_PAI": False,
        "TEM_QUANDO": False,
    },
    {
        "PRODUTOR": "ferramentas/youtube_transcrever.py",
        "ENTRADA": "audio de video",
        "SAIDA": "transcricao",
        "FORMATO": "text/plain",
        "ESPECIE": "DERIVED_ARTIFACT",
        "PORQUE": ("Whisper local. Nos produzimos, e o MODELO e escolhivel "
                   "(`base`, `small`, ...) — dois modelos sobre o mesmo audio dao "
                   "dois textos diferentes, ambos legitimos."),
        "FERRAMENTA": "whisper",
        "TEM_VERSAO": True,
        "TEM_PAI": True,
        "TEM_QUANDO": True,
    },
    {
        # Ate a C10.4C este PRODUTOR era `ferramentas/instagram_transcrever.py`.
        # Essa rota baixava o video inteiro e foi APOSENTADA — deixar a
        # declaracao no nome dela era o mapa a registar um segundo dono do
        # mesmo conceito.  ONE CONCEPT -> ONE OWNER.
        "PRODUTOR": "ferramentas/reel_transcricao.py",
        "ENTRADA": "audio de reel",
        "SAIDA": "transcricao",
        "FORMATO": "text/plain",
        "ESPECIE": "DERIVED_ARTIFACT",
        "PORQUE": ("o mesmo caso do YouTube, noutra plataforma — e por rota "
                   "audio-only: o video nunca chega a nascer."),
        "FERRAMENTA": "whisper",
        "TEM_VERSAO": True,
        "TEM_PAI": True,
        "TEM_QUANDO": True,
    },
    {
        "PRODUTOR": "data/samples/ES-T8-001-transcricoes.json",
        "ENTRADA": "a propria plataforma",
        "SAIDA": "legenda entregue pelo YouTube",
        "FORMATO": "text/plain",
        "ESPECIE": "RAW_CAPTURE",
        "PORQUE": ("⚠️ NAO E DERIVADO. A legenda veio COM a coleta; nos nao a "
                   "produzimos. Mete-la em derived_artifact seria declarar uma "
                   "linhagem que nao existe."),
        "FERRAMENTA": None,
        "TEM_VERSAO": False,
        "TEM_PAI": False,
        "TEM_QUANDO": False,
    },
    {
        "PRODUTOR": "ferramentas/italy_extract_fields.mjs",
        "ENTRADA": "documento italiano",
        "SAIDA": "campos extraidos",
        "FORMATO": "application/json",
        "ESPECIE": "STRUCTURED_RECORD",
        "PORQUE": ("extrai CAMPOS, nao um artefato com bytes proprios. Uma linha "
                   "normalizada tem casa noutro andar do banco."),
        "FERRAMENTA": None,
        "TEM_VERSAO": False,
        "TEM_PAI": False,
        "TEM_QUANDO": False,
    },
    {
        "PRODUTOR": "admissao/admissao.py",
        "ENTRADA": "documento ou claim",
        "SAIDA": "decisao de admissao",
        "FORMATO": "decisao",
        "ESPECIE": "CLAIM_OU_JUIZO",
        "PORQUE": ("julga, nao produz artefato. COL-LAW-502: documento pronto nao "
                   "e fato pronto, e o juizo sobre um texto nao e um derivado dele."),
        "FERRAMENTA": None,
        "TEM_VERSAO": False,
        "TEM_PAI": False,
        "TEM_QUANDO": False,
    },
]


def _abs(rel):
    return os.path.join(RAIZ, rel.replace("/", os.sep))


def censo_dos_produtores():
    """Confere que cada produtor declarado existe, e conta por espécie."""
    fora, por_especie = [], {}
    for p in PRODUTORES:
        existe = os.path.exists(_abs(p["PRODUTOR"]))
        item = dict(p, EXISTE=existe)
        fora.append(item)
        por_especie[p["ESPECIE"]] = por_especie.get(p["ESPECIE"], 0) + 1
    derivados = [p for p in fora if p["ESPECIE"] == "DERIVED_ARTIFACT"]
    return {
        "O_QUE_E": (
            "Nem tudo o que nao e o PDF original e derivado. Derivado e o que NOS "
            "produzimos a partir de bytes que guardamos."),
        "PRODUTORES_MEDIDOS": len(fora),
        "TODOS_EXISTEM": all(p["EXISTE"] for p in fora),
        "POR_ESPECIE": dict(sorted(por_especie.items())),
        "PRODUTORES_DE_DERIVADO": len(derivados),
        "FERRAMENTAS_DE_DERIVACAO": sorted({p["FERRAMENTA"] for p in derivados}),
        "TIPOS_REAIS_HOJE": sorted({p["SAIDA"] for p in derivados}),
        "QUANTOS_TEM_VERSAO_ESCOLHIVEL": sum(1 for p in derivados if p["TEM_VERSAO"]),
        "PORQUE_A_VERSAO_IMPORTA": (
            "o Whisper tem MODELO escolhivel: `base` e `small` sobre o mesmo audio "
            "dao dois textos diferentes, e ambos sao legitimos. Nao e hipotese — "
            "esta escrito em ferramentas/youtube_transcrever.py. Sem a versao na "
            "identidade, o segundo apagaria o primeiro em silencio."),
        "PRODUTORES": fora,
    }


# ─────────────────────────────────────────────────────────────────────────
# O CONTRATO QUE JÁ EXISTE — reusar antes de inventar vocabulário
# ─────────────────────────────────────────────────────────────────────────
CAMPOS_DO_CONTRATO = ("ARTIFACT_TYPE", "PARENT_ARTIFACT_ID", "PARENT_SHA256",
                      "DERIVATION_TYPE", "EXECUTOR_ID", "EXECUTOR_VERSION",
                      "PIPELINE_VERSION", "SHA256", "BYTES")


def o_contrato_que_ja_existe():
    """`leis/artefato.py` já diz o que é um derivado. A tabela obedece-lhe.

    Inventar nomes novos no banco criaria duas gramáticas para a mesma coisa —
    e a tradução entre elas seria mais uma coisa a poder mentir.
    """
    caminho = _abs(CONTRATO)
    if not os.path.exists(caminho):
        return {"CONTRATO": "AUSENTE"}
    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()
    presentes = [c for c in CAMPOS_DO_CONTRATO if c in fonte]
    return {
        "O_QUE_E": (
            "A lei do artefato ja existe em codigo, e distingue RAW de DERIVED. A "
            "tabela nao inventa vocabulario: traduz este."),
        "ONDE_VIVE": CONTRATO,
        "CAMPOS_EXIGIDOS": list(CAMPOS_DO_CONTRATO),
        "CAMPOS_PRESENTES": presentes,
        "CONTRATO_COMPLETO": len(presentes) == len(CAMPOS_DO_CONTRATO),
    }


# ─────────────────────────────────────────────────────────────────────────
# O ACERVO DERIVADO REAL, e o pai que ele NÃO tem
# ─────────────────────────────────────────────────────────────────────────
def o_acervo_derivado():
    caminho = _abs(REGISTO)
    if not os.path.exists(caminho):
        return {"REGISTO": "AUSENTE"}
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    itens = d.get("ARTEFATOS") if isinstance(d, dict) else d
    derivados = [a for a in (itens or []) if a.get("PARENT_SHA256")]

    por_tipo, por_ferramenta, por_estado = {}, {}, {}
    for a in derivados:
        for chave, campo in (("DERIVATION_TYPE", por_tipo),
                             ("EXECUTOR_ID", por_ferramenta),
                             ("STATE", por_estado)):
            v = a.get(chave) or "SEM_VALOR"
            campo[v] = campo.get(v, 0) + 1

    pais = {a["PARENT_SHA256"] for a in derivados}
    filhos = {a.get("SHA256") for a in derivados if a.get("SHA256")}
    chaves = {(a["PARENT_SHA256"], a.get("DERIVATION_TYPE"),
               a.get("EXECUTOR_ID"), a.get("EXECUTOR_VERSION"))
              for a in derivados}

    # O TEMPO: derivado nasce DEPOIS do bruto, e nunca no mesmo instante por
    # conveniencia. Aqui mede-se quantos conseguem provar as duas datas.
    com_derived_at = sum(1 for a in derivados
                         if a.get("DERIVED_AT") and a["DERIVED_AT"] != "NAO SEI")
    com_collected_at = sum(1 for a in derivados
                           if a.get("COLLECTED_AT") and a["COLLECTED_AT"] != "NAO SEI")

    return {
        "O_QUE_E": "Os derivados que esta casa ja produziu, medidos do registo.",
        "DERIVADOS": len(derivados),
        "PAIS_DISTINTOS": len(pais),
        "FILHOS_DISTINTOS_POR_BYTES": len(filhos),
        "CHAVES_DE_DERIVACAO_DISTINTAS": len(chaves),
        "POR_TIPO": dict(sorted(por_tipo.items())),
        "POR_FERRAMENTA": dict(sorted(por_ferramenta.items())),
        "POR_ESTADO": dict(sorted(por_estado.items())),
        "COM_DERIVED_AT": com_derived_at,
        "COM_COLLECTED_AT_DO_PAI": com_collected_at,
        "O_TEMPO_DO_PAI_NAO_SE_INVENTA": (
            "%d de %d derivados sabem quando foram derivados; %d sabem quando o "
            "pai foi colhido. Onde falta, fica UNKNOWN — copiar o `derived_at` "
            "para o `captured_at` daria uma data com cara de medida."
            % (com_derived_at, len(derivados), com_collected_at)),
    }


def o_pai_canonico_que_nao_existe():
    """Quantos dos derivados podem ser ligados HONESTAMENTE a um `raw_asset`.

    A resposta importa porque uma chave estrangeira bonita é a tentação óbvia
    desta missão: bastava inventar as linhas de `raw_asset` que faltam, e tudo
    ficaria ligado.

    Mas o `raw_asset` italiano tem **zero** linhas — está medido em
    `armazem-it.generated.json`, e a corrida que teria trazido aqueles PDF é
    `RUN_NOT_PROVABLE`. Sem pai canónico, não há chave estrangeira a fazer.

        LEGADO SEM PAI CANÓNICO CONTINUA LEGADO SEM PAI CANÓNICO.

    A migration é **para a frente**. O legado fica classificado, não remendado.
    """
    caminho = os.path.join(RAIZ, "system-map", "data", "armazem-it.generated.json")
    linhas_it = None
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            linhas_it = (json.load(f).get("LACUNA_DO_ARMAZEM") or {}).get(
                "ITALY_RAW_ASSET_LINHAS")
    acervo = o_acervo_derivado()
    return {
        "O_QUE_E": (
            "Quantos derivados existentes conseguem apontar para um raw_asset "
            "canonico. E a pergunta que decide se ha backfill honesto a fazer."),
        "DERIVADOS_EXISTENTES": acervo.get("DERIVADOS"),
        "LINHAS_DE_RAW_ASSET_IT": linhas_it,
        "LIGAVEIS_HONESTAMENTE": 0 if linhas_it == 0 else "NAO_SEI",
        "CLASSE": "LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT",
        "PORQUE": (
            "raw_asset IT = %s. Sem pai no banco nao ha chave estrangeira a "
            "cumprir, e inventar as linhas em falta seria fabricar a coleta que "
            "nunca foi registada." % linhas_it),
        "O_QUE_SE_FAZ": (
            "NADA com o legado. A migration e FORWARD: ela abre a casa para o "
            "que vier a seguir, e nao pinta de novo o que ficou para tras."),
    }


def main():
    fora = {
        "PRODUTORES": censo_dos_produtores(),
        "CONTRATO_JA_EXISTENTE": o_contrato_que_ja_existe(),
        "ACERVO_DERIVADO": o_acervo_derivado(),
        "O_PAI_CANONICO": o_pai_canonico_que_nao_existe(),
    }
    destino = os.path.join(RAIZ, "system-map", "data", "derivacoes.generated.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(fora, f, ensure_ascii=False, indent=2)
        f.write("\n")
    P, A, C = fora["PRODUTORES"], fora["ACERVO_DERIVADO"], fora["O_PAI_CANONICO"]
    print("produtores=%d (derivado=%d) · ferramentas=%s · derivados=%s "
          "· chaves=%s · ligaveis=%s" % (
              P["PRODUTORES_MEDIDOS"], P["PRODUTORES_DE_DERIVADO"],
              ",".join(x for x in P["FERRAMENTAS_DE_DERIVACAO"] if x),
              A.get("DERIVADOS"), A.get("CHAVES_DE_DERIVACAO_DISTINTAS"),
              C.get("LIGAVEIS_HONESTAMENTE")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
