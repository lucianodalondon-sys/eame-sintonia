# -*- coding: utf-8 -*-
"""CENSO DE IDENTIDADE — CAMINHO, CAPTURA, CONTEÚDO, CÓPIA, DERIVADO.

POR QUE ISTO EXISTE
-------------------
O censo do corpo italiano mediu bem, mas explicou mal. Ele viu

    49 caminhos de PDF  →  43 conteúdos SHA-256 diferentes

e escreveu, em prosa, que os seis excedentes eram «o mesmo documento guardado
em dois sítios» — a loja do coletor e a amostra versionada. Isso era um
palpite com cara de facto. **Caminho diferente não prova captura diferente, e
SHA igual não prova a mesma captura.** Nenhuma das duas frases se decide
olhando para o nome da pasta.

Este ficheiro decide olhando para a PROVA DE CAPTURA de cada caminho. E o que
a prova diz é o contrário do palpite: os seis pares são

    DUAS CAPTURAS REAIS E INDEPENDENTES QUE TROUXERAM OS MESMOS BYTES

— feitas em momentos diferentes, por atores diferentes, e por vezes por rotas
diferentes. O ficheiro na amostra não é uma fotocópia do ficheiro na loja: é
uma segunda ida à fonte, que por acaso encontrou o documento inalterado.

Isto muda o modelo de dados. Um esquema que guardasse «um caminho por
conteúdo» apagaria uma captura verdadeira — e com ela a prova de que o
documento não mudou entre 2 e 7 de setembro.

AS QUATRO ESPÉCIES QUE ESTE CENSO SEPARA
----------------------------------------
    CONTEÚDO      os bytes. Identidade = SHA-256. Não tem data nem dono.
    CAPTURA       uma ida à fonte, num instante, por um ator, por uma rota.
                  Identidade = (registo, corrida/pacote, URL, quando).
    CÓPIA         um lugar no disco onde os bytes ficaram. Identidade = caminho.
                  O caminho muda de nome sem que o conteúdo mude.
    DERIVADO      o que uma ferramenta fez a partir de um conteúdo pai.

TRÊS REGISTOS DE PROVA
----------------------
Cada caminho tem de encontrar a sua captura num destes três, e só num:

    1. o livro do coletor   data/collection-ledger/italy/observations.ndjson
    2. o manifesto da amostra   data/samples/IT-SOURCE-SAMPLES/*/MANIFEST.json
    3. o manifesto do pacote VPN   data/samples/IT-BOLLETTINI-VPN-2026/*.json

Caminho sem prova em nenhum deles não vira SAME nem INDEPENDENT: vira
CAPTURA_DESCONHECIDA, e o grupo inteiro cai para UNKNOWN. Não há quarta
resposta por estética.

O QUE ESTE CENSO NÃO FAZ
------------------------
Não escreve no Supabase, não copia byte nenhum, não desenha tabela. Ele só
mede que espécies existem, para que a decisão de esquema venha depois da
prova e não antes dela.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LIVRO = os.path.join("data", "collection-ledger", "italy", "observations.ndjson")
AMOSTRAS = os.path.join("data", "samples", "IT-SOURCE-SAMPLES")
PACOTE_VPN = os.path.join("data", "samples", "IT-BOLLETTINI-VPN-2026")
REGISTO_DERIVADOS = os.path.join("data", "derivados", "REGISTO-DE-ARTEFATOS.json")

SAME = "SAME_CAPTURE_MULTIPLE_STORAGE_COPIES"
INDEP = "INDEPENDENT_CAPTURES_SAME_CONTENT"
UNKNOWN = "UNKNOWN"

DESCONHECIDA = "CAPTURA_DESCONHECIDA"


def _abs(rel):
    return os.path.join(RAIZ, rel.replace("/", os.sep))


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _rel(caminho):
    return os.path.relpath(caminho, RAIZ).replace(os.sep, "/")


# ─────────────────────────────────────────────────────────────────────────
# OS TRÊS REGISTOS DE PROVA
# ─────────────────────────────────────────────────────────────────────────
def capturas_do_livro():
    """O que o coletor registou: uma linha por documento visto numa corrida.

    A chave é o RAW_PATH — o caminho que a própria corrida diz ter escrito.
    """
    fora = {}
    caminho = _abs(LIVRO)
    if not os.path.exists(caminho):
        return fora
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                obs = json.loads(linha)
            except ValueError:
                continue
            alvo = obs.get("RAW_PATH")
            if not alvo:
                continue
            fora[alvo] = {
                "REGISTO": "LIVRO_DO_COLETOR",
                "CAPTURE_ID": "LIVRO:%s:%s" % (obs.get("RUN_ID"), obs.get("SOURCE_URL")),
                "RUN_ID": obs.get("RUN_ID"),
                "SOURCE_ID": obs.get("SOURCE_ID"),
                "SOURCE_URL": obs.get("SOURCE_URL"),
                "CAPTURED_AT": obs.get("CAPTURED_AT"),
                "ATOR": "coletor-piloto",
                "SHA256_DECLARADO": obs.get("RAW_SHA256"),
            }
    return fora


def capturas_das_amostras():
    """O que cada manifesto de amostra registou: uma ida à fonte por pasta.

    O manifesto guarda a captura no topo (quando, por que método, de que IP) e
    os ficheiros em baixo. Cada ficheiro herda a captura da sua pasta.
    """
    fora = {}
    base = _abs(AMOSTRAS)
    if not os.path.isdir(base):
        return fora
    for pasta in sorted(os.listdir(base)):
        manifesto = os.path.join(base, pasta, "MANIFEST.json")
        if not os.path.exists(manifesto):
            continue
        with open(manifesto, encoding="utf-8") as f:
            m = json.load(f)
        cap = m.get("CAPTURE") or {}
        quando = cap.get("CAPTURED_AT_UTC")
        for ficheiro in m.get("FILES") or []:
            nome = ficheiro.get("RAW_FILE")
            if not nome:
                continue
            rel = "/".join([AMOSTRAS.replace(os.sep, "/"), pasta, nome])
            fora[rel] = {
                "REGISTO": "MANIFESTO_DA_AMOSTRA",
                "CAPTURE_ID": "AMOSTRA:%s:%s:%s" % (
                    m.get("SOURCE_ID"), quando, ficheiro.get("SOURCE_URL")),
                "RUN_ID": None,
                "SOURCE_ID": m.get("SOURCE_ID"),
                "SOURCE_URL": ficheiro.get("SOURCE_URL"),
                "CAPTURED_AT": quando,
                "ATOR": cap.get("METODO"),
                "EGRESS_IP": cap.get("EGRESS_IP"),
                "HTTP_STATUS": ficheiro.get("HTTP_STATUS"),
                "SHA256_DECLARADO": ficheiro.get("SHA256"),
            }
    return fora


def capturas_do_pacote_vpn():
    """O pacote VPN é UMA captura para o pacote inteiro.

    Ele não tem manifesto por ficheiro: tem um recibo por pacote, com a data e
    o IP de saída. Todos os ficheiros do pacote herdam essa captura — e isso é
    tudo o que se pode honestamente afirmar sobre eles.
    """
    fora = {}
    base = _abs(PACOTE_VPN)
    if not os.path.isdir(base):
        return fora
    recibo = None
    for nome in sorted(os.listdir(base)):
        if nome.lower().endswith(".json"):
            with open(os.path.join(base, nome), encoding="utf-8") as f:
                recibo = json.load(f)
            break
    if not recibo:
        return fora
    quando = recibo.get("CAPTURED_AT")
    for pasta, _sub, ficheiros in os.walk(base):
        for nome in ficheiros:
            rel = _rel(os.path.join(pasta, nome))
            fora[rel] = {
                "REGISTO": "PACOTE_VPN",
                "CAPTURE_ID": "PACOTE_VPN:%s:%s" % (recibo.get("SOURCE_URL"), quando),
                "RUN_ID": None,
                "SOURCE_ID": None,
                "SOURCE_URL": recibo.get("SOURCE_URL"),
                "CAPTURED_AT": quando,
                "ATOR": "recolha manual por VPN",
                "EGRESS_IP": recibo.get("EXIT_IP_COUNTRY"),
                "SHA256_DECLARADO": None,
            }
    return fora


def prova_de_captura():
    """Junta os três registos. Um caminho não pode ter duas provas: a primeira
    que o reclamar fica, e a ordem é a da confiança — o livro do coletor é o
    registo mais rico, depois o manifesto por ficheiro, depois o por pacote."""
    junto = {}
    for registo in (capturas_do_pacote_vpn(), capturas_das_amostras(), capturas_do_livro()):
        junto.update(registo)
    return junto


# ─────────────────────────────────────────────────────────────────────────
# A CLASSIFICAÇÃO
# ─────────────────────────────────────────────────────────────────────────
def classificar(grupo):
    """Um grupo é um conteúdo com mais de um caminho. Ele termina em exatamente
    um dos três estados — e o estado é lido da prova, nunca do nome da pasta."""
    ids = [c["PROVA"]["CAPTURE_ID"] if c["PROVA"] else DESCONHECIDA for c in grupo]
    if DESCONHECIDA in ids:
        return UNKNOWN, "pelo menos um caminho nao tem prova de captura em nenhum dos tres registos"
    unicos = sorted(set(ids))
    if len(unicos) == 1:
        return SAME, "todos os caminhos apontam para a MESMA captura: %s" % unicos[0]
    quandos = sorted({c["PROVA"]["CAPTURED_AT"] for c in grupo})
    atores = sorted({str(c["PROVA"]["ATOR"]) for c in grupo})
    return INDEP, (
        "%d capturas distintas, com provas separadas. Quando: %s. Ator: %s."
        % (len(unicos), " | ".join(quandos), " | ".join(atores)))


def caminhos_de_pdf():
    """Exatamente os mesmos caminhos que o censo do corpo conta.

    A regra do que é italiano vive lá e é importada daqui — dois censos com
    duas regras de contagem produziriam dois números verdadeiros e
    contraditórios, que é o pior resultado possível.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from censo_do_corpus_it import e_italiano  # noqa: E402

    fora = []
    for pasta, _sub, ficheiros in os.walk(RAIZ):
        if ".git" in pasta.replace("\\", "/").split("/"):
            continue
        for nome in ficheiros:
            if not nome.lower().endswith(".pdf"):
                continue
            absoluto = os.path.join(pasta, nome)
            if e_italiano(_rel(absoluto)):
                fora.append(absoluto)
    return sorted(fora)


def censo():
    prova = prova_de_captura()
    por_conteudo = {}
    for absoluto in caminhos_de_pdf():
        rel = _rel(absoluto)
        sha = _sha256(absoluto)
        por_conteudo.setdefault(sha, []).append({"CAMINHO": rel, "PROVA": prova.get(rel)})

    grupos = []
    for sha in sorted(por_conteudo):
        copias = por_conteudo[sha]
        if len(copias) < 2:
            continue
        estado, porque = classificar(copias)
        grupos.append({
            "SHA256": sha,
            "ESTADO": estado,
            "PORQUE": porque,
            "COPIAS": [{
                "CAMINHO": c["CAMINHO"],
                "REGISTO": (c["PROVA"] or {}).get("REGISTO", DESCONHECIDA),
                "CAPTURED_AT": (c["PROVA"] or {}).get("CAPTURED_AT"),
                "SOURCE_URL": (c["PROVA"] or {}).get("SOURCE_URL"),
                "ATOR": (c["PROVA"] or {}).get("ATOR"),
                "RUN_ID": (c["PROVA"] or {}).get("RUN_ID"),
            } for c in copias],
        })

    sem_prova = sorted(_rel(p) for p in caminhos_de_pdf() if _rel(p) not in prova)

    capturas = {(c or {}).get("CAPTURE_ID") for c in
                (prova.get(_rel(p)) for p in caminhos_de_pdf())}
    capturas.discard(None)

    contagem = {}
    for g in grupos:
        contagem[g["ESTADO"]] = contagem.get(g["ESTADO"], 0) + 1

    return {
        "O_QUE_E": (
            "CAMINHO, CAPTURA, CONTEUDO e COPIA sao quatro especies. Caminho diferente "
            "NAO prova captura diferente; SHA igual NAO prova a mesma captura. Cada grupo "
            "abaixo foi classificado pela PROVA DE CAPTURA de cada caminho, nunca pelo nome "
            "da pasta."),
        "COPIAS_NO_DISCO": len(caminhos_de_pdf()),
        "CONTEUDOS_UNICOS": len(por_conteudo),
        "CAPTURAS_DISTINTAS": len(capturas),
        "COPIAS_SEM_PROVA_DE_CAPTURA": len(sem_prova),
        "ONDE_FALTA_PROVA": sem_prova,
        "GRUPOS_COM_MAIS_DE_UMA_COPIA": len(grupos),
        "VEREDITO": contagem,
        "GRUPOS": grupos,
    }


def derivados():
    """O que o registo de derivados já sabe dizer sobre linhagem.

    Este bloco não decide nada: ele mostra que o contrato do derivado já existe
    na camada de ficheiros — pai, tipo de derivação, ator, versão, quando — e
    que a dívida está do lado do banco, não do lado da medição.
    """
    caminho = _abs(REGISTO_DERIVADOS)
    if not os.path.exists(caminho):
        return {"REGISTO": "AUSENTE"}
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    itens = d.get("ARTEFATOS") if isinstance(d, dict) else d
    itens = [a for a in (itens or []) if a.get("PARENT_SHA256")]
    campos = ("PARENT_ARTIFACT_ID", "PARENT_SHA256", "DERIVATION_TYPE",
              "EXECUTOR_ID", "EXECUTOR_VERSION", "PIPELINE_VERSION", "DERIVED_AT")
    completos = sum(1 for a in itens if all(a.get(c) for c in campos))
    com_muitos_lugares = sum(
        1 for a in itens
        if len((a.get("NOTES") or {}).get("PARENT_STORAGE_LOCATIONS") or []) > 1)
    return {
        "O_QUE_E": (
            "DERIVADO nao e RAW. Cada derivado declara de que conteudo nasceu, por que "
            "ferramenta e em que versao. O contrato ja existe nos ficheiros; falta-lhe "
            "casa no banco."),
        "DERIVADOS_COM_PAI": len(itens),
        "LINHAGEM_COMPLETA": completos,
        "CAMPOS_DA_LINHAGEM": list(campos),
        "PAI_GUARDADO_EM_MAIS_DE_UM_LUGAR": com_muitos_lugares,
    }


def main():
    fora = {"IDENTIDADE_DO_ARTEFATO": censo(), "LINHAGEM_DO_DERIVADO": derivados()}
    destino = os.path.join(RAIZ, "system-map", "data", "identidade-it.generated.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(fora, f, ensure_ascii=False, indent=2)
        f.write("\n")
    i = fora["IDENTIDADE_DO_ARTEFATO"]
    print("copias=%d conteudos=%d capturas=%d grupos=%d veredito=%s sem_prova=%d" % (
        i["COPIAS_NO_DISCO"], i["CONTEUDOS_UNICOS"], i["CAPTURAS_DISTINTAS"],
        i["GRUPOS_COM_MAIS_DE_UMA_COPIA"], i["VEREDITO"], i["COPIAS_SEM_PROVA_DE_CAPTURA"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
