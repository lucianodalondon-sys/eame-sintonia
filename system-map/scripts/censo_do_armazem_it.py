# -*- coding: utf-8 -*-
"""CENSO DO ARMAZÉM ITALIANO — bytes lá dentro, memória operacional de fora.

O QUE ISTO MEDE
---------------
Deixou de ser verdade dizer «a Itália não está no Supabase». A frase certa é
mais desconfortável e muito mais útil:

    OS BYTES ITALIANOS ESTÃO NO ARMAZÉM.
    A MEMÓRIA OPERACIONAL DELES NÃO EXISTE.

195 objetos sob o prefixo `IT/`, 80,7 MB — e **zero** linhas de `raw_asset` e
**zero** de `collection_run` a dizer quem os trouxe, quando, e por que rota.

Um armazém cheio sem livro de entrada. As caixas estão lá; ninguém sabe dizer
de onde vieram sem ir abrir cada uma.

DE ONDE VÊM OS NÚMEROS — E DE ONDE NÃO VÊM
------------------------------------------
Esta é a distinção que este ficheiro existe para não deixar borrar:

    MEDIDO AQUI       o manifesto que vive no Git, e os PDF no disco.
                      Corre outra vez e dá o mesmo.

    MEDIDO POR FORA   as contagens do banco LIVE. Esta sessão NÃO tem
                      credencial e NÃO as reproduziu. Vêm de
                      `data/samples/SUPABASE-LIVE-MEDICAO-EXTERNA.json`, com o
                      nome de quem mediu ao lado, e o seu estado é
                      EXTERNAL_LIVE_MEASUREMENT — nunca OBSERVED.

Recado de terceiro pode estar certo e continuar não sendo prova nossa.

DOIS ACERVOS ITALIANOS, E NÃO UM
--------------------------------
O erro fácil aqui seria somar coisas que não se somam:

    ARMAZÉM      IT/adama-website/…  — o catálogo comercial da ADAMA Itália,
                 fichas de segurança, etiquetas, brochuras. 141 documentos
                 declarados num manifesto de investigação.

    GOLDEN PATH  49 cópias / 43 conteúdos — boletins fitossanitários regionais
                 (ARPAV, Campania, olivo). Outra gente, outras fontes.

São dois acervos diferentes. Este censo mede a interseção pela **impressão
digital**, nunca pelo nome do ficheiro.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MANIFESTO = os.path.join("research", "adama-italy-product-intelligence-deep",
                         "LABEL-MANIFEST.json")
MEDICAO_EXTERNA = os.path.join("data", "samples", "SUPABASE-LIVE-MEDICAO-EXTERNA.json")


def _abs(rel):
    return os.path.join(RAIZ, rel.replace("/", os.sep))


def _ler(rel):
    caminho = _abs(rel)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────
# O QUE O GIT PROVA — a procedência dos documentos do armazém
# ─────────────────────────────────────────────────────────────────────────
CAMPOS_DE_PROCEDENCIA = ("SHA256", "BYTES", "CAPTURED_AT", "SOURCE_URL", "SOURCE_ID")


def procedencia_recuperavel():
    """Quantos dos documentos do armazém conseguem dizer de onde vieram.

    O manifesto está **no Git**. É por isso que a procedência não se perdeu
    quando o `raw_asset` ficou vazio: ela ficou noutro sítio.

    ⚠️ RECUPERÁVEL NÃO É RECUPERADA. Isto diz que a prova existe para ser lida,
    não que alguém a leu, nem que se pode inserir uma corrida histórica com
    base nela. Recriar história é outra decisão, e não é desta missão.
    """
    m = _ler(MANIFESTO)
    if not m:
        return {"MANIFESTO": "AUSENTE"}
    docs = m.get("DOCUMENTS") or []
    completos = [d for d in docs if all(d.get(c) for c in CAMPOS_DE_PROCEDENCIA)]
    shas = [d["SHA256"] for d in docs if d.get("SHA256")]
    tipos = {}
    for d in docs:
        t = d.get("DOCUMENT_TYPE") or "SEM_TIPO"
        tipos[t] = tipos.get(t, 0) + 1
    estados = {}
    for d in docs:
        e = d.get("DOCUMENT_STATE") or "SEM_ESTADO"
        estados[e] = estados.get(e, 0) + 1
    return {
        "O_QUE_E": (
            "O manifesto do acervo comercial italiano, versionado no Git. E ele "
            "que segura a procedencia enquanto raw_asset esta vazio."),
        "ONDE_VIVE": MANIFESTO,
        "DOCUMENTOS_DECLARADOS": len(docs),
        "CONTEUDOS_UNICOS": len(set(shas)),
        "REGISTOS_COM_CONTEUDO_REPETIDO": len(shas) - len(set(shas)),
        "PROCEDENCIA_RECUPERAVEL": len(completos),
        "PROCEDENCIA_INCOMPLETA": len(docs) - len(completos),
        "CAMPOS_EXIGIDOS": list(CAMPOS_DE_PROCEDENCIA),
        "RUN_ID_NO_MANIFESTO": (
            "NAO — nenhum registo declara corrida. A procedencia e do DOCUMENTO "
            "(quando, de que URL, que bytes); a da CORRIDA nunca foi escrita."),
        "POR_TIPO": dict(sorted(tipos.items())),
        "POR_ESTADO": dict(sorted(estados.items())),
        "BYTES_DECLARADOS": sum(d.get("BYTES") or 0 for d in docs),
        "CAPTURADO_ENTRE": (min(d["CAPTURED_AT"] for d in docs if d.get("CAPTURED_AT")),
                            max(d["CAPTURED_AT"] for d in docs if d.get("CAPTURED_AT")))
        if any(d.get("CAPTURED_AT") for d in docs) else None,
    }


# ─────────────────────────────────────────────────────────────────────────
# A LACUNA — bytes presentes, memória operacional ausente
# ─────────────────────────────────────────────────────────────────────────
def lacuna_do_armazem():
    ext = _ler(MEDICAO_EXTERNA)
    if not ext:
        return {"MEDICAO_EXTERNA": "AUSENTE"}
    st = ext["STORAGE"]
    tb = ext["TABELAS"]
    proc = procedencia_recuperavel()
    conta = a_conta_fecha()

    objetos_documento = next(
        (p["OBJETOS"] for p in st["POR_PREFIXO"] if p["PREFIXO"].endswith("/DOCUMENT")), None)

    return {
        "O_QUE_E": (
            "BYTES PRESENTES != PROCEDENCIA OPERACIONAL COMPLETA. Os objetos estao "
            "no armazem; nenhuma linha de raw_asset ou collection_run os reclama."),
        "ESTADO_DA_MEDICAO": "EXTERNAL_LIVE_MEASUREMENT",
        "PORQUE_NAO_E_OBSERVED": (
            "esta sessao nao tem credencial do banco e NAO reproduziu a leitura. "
            "Quem mediu foi o coordenador, e o nome dele fica ao lado do numero."),
        "MEDIDO_POR": ext["MEDIDO_POR"],
        "MEDIDO_EM": ext["MEDIDO_EM"],
        "ITALY_STORAGE_OBJETOS": st["OBJETOS"],
        "ITALY_STORAGE_BYTES": st["BYTES"],
        "ITALY_STORAGE_POR_PREFIXO": st["POR_PREFIXO"],
        "ITALY_RAW_ASSET_LINHAS": tb["public.raw_asset"]["LINHAS_IT"],
        "ITALY_COLLECTION_RUN_LINHAS": tb["public.collection_run"]["LINHAS_IT"],
        "LACUNA": "STORAGE_SEM_MEMORIA_OPERACIONAL",
        "OBJETOS_SEM_DONO_DECLARADO": st["OBJETOS"],
        # AS TRES CONTAGENS — ontem nao batiam, e hoje batem com explicacao.
        # Ficam aqui porque o cartao do mapa as le daqui; a conta inteira, com
        # a causa de cada diferenca, esta em `a_conta_fecha()`.
        "TRES_CONTAGENS": {
            "DOCUMENTOS_NO_MANIFESTO": proc.get("DOCUMENTOS_DECLARADOS"),
            "CONTEUDOS_UNICOS_NO_MANIFESTO": proc.get("CONTEUDOS_UNICOS"),
            "OBJETOS_DOCUMENT_NO_ARMAZEM": objetos_documento,
            "ESTADO": conta.get("ESTADO"),
            "FORCA_DA_PROVA": conta.get("FORCA_DA_PROVA"),
            "COMO_SE_EXPLICAM": (
                "141 - 138 = 3 documentos que servem a DOIS produtos cada um. "
                "139 - 138 = 1 conteudo publicado pela ADAMA em DUAS URLs. As "
                "duas diferencas tem causas diferentes, e nenhuma e perda."),
            "ONDE_ESTA_A_CONTA": "A_CONTA_FECHA",
        },
        "A_PROCEDENCIA_PERDEU_SE": (
            "NAO. Ela nao esta no banco, mas esta no Git: %s de %s documentos "
            "declaram bytes, hora, URL e fonte. O que nao existe e a CORRIDA."
            % (proc.get("PROCEDENCIA_RECUPERAVEL"), proc.get("DOCUMENTOS_DECLARADOS"))),
        "RUN_HISTORICA": "RUN_NOT_PROVABLE — nenhum registo declara run_id.",
        "NAO_RETROCRIAR": (
            "PROCEDENCIA RECUPERAVEL nao autoriza PROCEDENCIA INVENTADA. Inserir "
            "hoje uma corrida que nunca foi registada seria escrever no livro de "
            "historia um dia que ninguem viveu."),
    }


# ─────────────────────────────────────────────────────────────────────────
# OS DOIS ACERVOS — medidos pela impressão digital, nunca pelo nome
# ─────────────────────────────────────────────────────────────────────────
def dois_acervos():
    from censo_de_identidade_it import caminhos_de_pdf, _sha256, _rel  # noqa: E402

    m = _ler(MANIFESTO) or {}
    do_armazem = {d["SHA256"] for d in (m.get("DOCUMENTS") or []) if d.get("SHA256")}

    do_caminho = {}
    for absoluto in caminhos_de_pdf():
        do_caminho.setdefault(_sha256(absoluto), []).append(_rel(absoluto))

    dentro = sorted(set(do_caminho) & do_armazem)
    return {
        "O_QUE_E": (
            "O acervo do armazem (catalogo comercial ADAMA) e o do Golden Path "
            "(boletins regionais) sao universos diferentes ate prova em contrario. "
            "A prova compara IMPRESSAO DIGITAL, nunca nome de ficheiro."),
        "GOLDEN_PATH_CONTEUDOS": len(do_caminho),
        "ARMAZEM_CONTEUDOS_DECLARADOS": len(do_armazem),
        "JA_NO_ARMAZEM": len(dentro),
        "QUAIS": dentro,
        "FORA_DO_ARMAZEM": len(do_caminho) - len(dentro),
        "DESCONHECIDO": 0,
        "PORQUE_ZERO_DESCONHECIDO": (
            "todo conteudo do Golden Path tem sha256 calculado do disco, e todo "
            "documento do manifesto declara o seu. A comparacao e completa dos "
            "dois lados — nao ha caso por decidir."),
        "RESSALVA": (
            "isto compara com o MANIFESTO do armazem, nao com a lista de chaves do "
            "armazem. Se um objeto foi la parar sem passar pelo manifesto, este "
            "censo nao o ve."),
    }


# ─────────────────────────────────────────────────────────────────────────
# A CONTA QUE NÃO FECHAVA — 141, 138 e 139
# ─────────────────────────────────────────────────────────────────────────
def a_conta_fecha():
    """Os três números explicados, e não só contados.

    Ontem escrevi «três números, nenhum igual» e deixei em `NÃO_RECONCILIADO`,
    porque faltava a lista de chaves. Ela chegou pela metade — as contagens de
    identidade e as duas chaves do único duplicado — e é o suficiente, porque a
    explicação estava do lado de cá o tempo todo, no manifesto:

        141 REGISTOS   uma linha por (produto, documento)
        138 CONTEÚDOS  bytes diferentes
        139 OBJETOS    cópias guardadas no armazém

    A diferença dos dois lados tem causas DIFERENTES, e é isso que estava a
    faltar dizer:

        141 - 138 = 3   três documentos servem a DOIS produtos cada um
        139 - 138 = 1   um conteúdo foi PUBLICADO EM DUAS URLs

    E prova-se olhando para a `SOURCE_URL` dos três grupos repetidos: o
    `227779…` tem duas URLs (`media/731` e `media/6321`) e por isso dois
    objetos; os outros dois têm **uma URL cada** e por isso um objeto cada. O
    armazém bate com o manifesto, documento a documento.

    ⚠️ E CONTINUA A SER PREFIX_MATCH. A chave carrega 16 caracteres do hash;
    isso é endereço, não identidade. Sem ler os bytes de volta — e esta sessão
    não os lê — a igualdade é forte mas parcial. Diz-se isso, não se arredonda.
    """
    m = _ler(MANIFESTO) or {}
    ext = _ler(MEDICAO_EXTERNA) or {}
    docs = m.get("DOCUMENTS") or []
    dentro = (ext.get("STORAGE") or {}).get("DOCUMENT_POR_DENTRO") or {}

    por_sha = {}
    for d in docs:
        if d.get("SHA256"):
            por_sha.setdefault(d["SHA256"], []).append(d)

    grupos = []
    objetos_previstos = 0
    for sha, entradas in sorted(por_sha.items()):
        urls = sorted({e.get("SOURCE_URL") for e in entradas})
        objetos_previstos += len(urls)
        if len(entradas) > 1:
            grupos.append({
                "SHA256": sha,
                "REGISTOS": len(entradas),
                "URLS_DISTINTAS": len(urls),
                "OBJETOS_PREVISTOS": len(urls),
                "PRODUTOS": sorted({e.get("PRODUCT_NAME") for e in entradas}),
                "PORQUE": (
                    "o MESMO byte publicado em %d enderecos diferentes: sao %d "
                    "factos sobre o mundo e UM conteudo" % (len(urls), len(urls))
                    if len(urls) > 1 else
                    "dois produtos que apontam para o MESMO endereco: e RELACAO "
                    "LOGICA, e nao exige byte novo"),
            })

    objetos_medidos = dentro.get("OBJETOS")
    return {
        "O_QUE_E": (
            "REGISTO nao e CONTEUDO e nao e OBJETO. Nenhuma das tres contagens "
            "e derivavel das outras, e as duas diferencas tem causas diferentes."),
        "REGISTOS_DE_MANIFESTO": len(docs),
        "CONTEUDOS_UNICOS": len(por_sha),
        "OBJETOS_PREVISTOS_PELO_MANIFESTO": objetos_previstos,
        "OBJETOS_MEDIDOS_NO_ARMAZEM": objetos_medidos,
        "CONTEUDOS_MEDIDOS_NO_ARMAZEM": dentro.get("PREFIXO_SHA16_DISTINTOS"),
        "AS_DUAS_DIFERENCAS": {
            "REGISTOS_MENOS_CONTEUDOS": len(docs) - len(por_sha),
            "PORQUE_ESSA": ("documentos que servem a mais de um produto. E facto "
                            "a preservar, nao erro — o proprio manifesto ja o dizia."),
            "OBJETOS_MENOS_CONTEUDOS": (
                (objetos_medidos - len(por_sha)) if objetos_medidos else None),
            "PORQUE_ESSA_OUTRA": ("um conteudo publicado em DUAS URLs pela propria "
                                  "ADAMA. Duas publicacoes, dois objetos, um conteudo."),
        },
        "GRUPOS_REPETIDOS": grupos,
        "BATE": (objetos_medidos is not None
                 and objetos_previstos == objetos_medidos
                 and dentro.get("PREFIXO_SHA16_DISTINTOS") == len(por_sha)),
        "ESTADO": ("RECONCILIADO_POR_PREFIXO"
                   if (objetos_medidos is not None
                       and objetos_previstos == objetos_medidos)
                   else "NAO_RECONCILIADO"),
        "FORCA_DA_PROVA": "PREFIX_MATCH",
        "PORQUE_NAO_E_FULL_SHA256_MATCH": (
            "a chave do armazem carrega 16 caracteres do hash, e prefixo curto e "
            "endereco, nao identidade. Fechar como FULL_SHA256_MATCH exigiria ler "
            "os 139 objetos de volta e bater o sha256 inteiro — esta sessao nao "
            "tem credencial para isso."),
        "BYTE_PERDIDO": (
            "NENHUM. Todo conteudo do manifesto tem objeto previsto, e a contagem "
            "de conteudos distintos no armazem e a mesma do manifesto."),
    }


# ─────────────────────────────────────────────────────────────────────────
# QUEM ESCREVEU, E POR QUE A OUTRA METADE NÃO CORREU
# ─────────────────────────────────────────────────────────────────────────
IMPORTADOR = os.path.join("guarda", "catalogo_importar.py")
IMPORTACOES = os.path.join("supabase", "importacoes")


def quem_escreveu():
    """A cadeia real tem DOIS passos, e só o primeiro correu para a Itália.

        1. o operador envia os bytes    →  Storage        (correu)
        2. o gerador escreve o SQL      →  raw_asset      (NUNCA correu para IT)

    O passo 1 mora **fora deste repositório**, de propósito: é a máquina do
    operador, e há um teste que reprova se ela entrar aqui. O passo 2 mora
    aqui — e está preso à Espanha pela própria escrita do ficheiro.
    """
    imp = _abs(IMPORTADOR)
    fonte = open(imp, encoding="utf-8").read() if os.path.exists(imp) else ""
    pasta = _abs(IMPORTACOES)
    ficheiros = sorted(os.listdir(pasta)) if os.path.isdir(pasta) else []
    it = [n for n in ficheiros if n.startswith("IT-")]
    fala_do_bruto = []
    for n in it:
        with open(os.path.join(pasta, n), encoding="utf-8") as f:
            if "raw_asset" in f.read():
                fala_do_bruto.append(n)
    return {
        "O_QUE_E": (
            "Os bytes e a memoria operacional sao escritos por DUAS maos "
            "diferentes, em dois passos que ninguem obriga a andar juntos."),
        "PASSO_1_ENVIA_OS_BYTES": {
            "FERRAMENTA": "scripts/storage_preservar.py --enviar",
            "ONDE_VIVE": "FORA DESTE REPOSITORIO — maquina do operador",
            "PROVA": ("docs/adama/INTEGRACAO-CATALOGO-ADAMA-ES.md linha 69 lista-a "
                      "como NAO INTEGRADA, e tests/es/test_adama_es_gate.py:366 "
                      "reprova se ela aparecer aqui"),
            "CORREU_PARA_A_ITALIA": "SIM — e o que explica os 195 objetos",
        },
        "PASSO_2_ESCREVE_A_MEMORIA": {
            "FERRAMENTA": IMPORTADOR.replace(os.sep, "/"),
            "ONDE_VIVE": "AQUI",
            "ESTA_PRESO_A_ESPANHA": "ADAMA-ES-PRODUCT-INTELLIGENCE.json" in fonte,
            "PROVA": ("as entradas e a saida sao ADAMA-ES-*; nao ha equivalente "
                      "italiano em lado nenhum"),
            "CORREU_PARA_A_ITALIA": "NAO",
        },
        "IMPORTACOES_ITALIANAS_QUE_EXISTEM": it,
        "DESSAS_QUE_FALAM_DO_BRUTO": fala_do_bruto,
        "O_QUE_ISSO_DIZ": (
            "a Italia TEM SQL de importacao — e nenhum dos ficheiros menciona "
            "raw_asset ou collection_run. Ela importa camadas analiticas e nunca "
            "importou a procedencia."),
        "CLASSIFICACAO": "STORAGE_ONLY_PIPELINE",
        "PORQUE_NAO_E_AS_OUTRAS": {
            "LEGACY_BEFORE_RAW_ASSET_OWNER": (
                "NAO — raw_asset existe desde a migration 001, muito antes destes "
                "objetos (capturados em 30/08/2026)."),
            "FAILED_METADATA_WRITE": (
                "NAO ha prova de tentativa falhada: nao existe ficheiro de "
                "importacao italiano do bruto para ter falhado."),
            "INTENTIONAL_NOT_REGISTERED": (
                "NAO ha decisao escrita em lado nenhum a dizer 'a Italia nao se "
                "regista'. Ausencia de decisao nao e decisao."),
        },
        "RESSALVA": (
            "o passo 1 nao pode ser lido por esta sessao — ele vive noutra "
            "maquina. Logo, nao se pode PROVAR que ele nao tentou escrever "
            "raw_asset e falhou. O que se prova e o lado de ca: aqui nao ha "
            "escritor italiano do bruto, e nunca houve."),
    }


def main():
    fora = {
        "PROCEDENCIA_NO_GIT": procedencia_recuperavel(),
        "A_CONTA_FECHA": a_conta_fecha(),
        "LACUNA_DO_ARMAZEM": lacuna_do_armazem(),
        "QUEM_ESCREVEU": quem_escreveu(),
        "DOIS_ACERVOS": dois_acervos(),
    }
    destino = os.path.join(RAIZ, "system-map", "data", "armazem-it.generated.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(fora, f, ensure_ascii=False, indent=2)
        f.write("\n")
    L, A = fora["LACUNA_DO_ARMAZEM"], fora["DOIS_ACERVOS"]
    print("armazem=%s objetos · raw_asset_it=%s · run_it=%s · golden_no_armazem=%d/%d" % (
        L.get("ITALY_STORAGE_OBJETOS"), L.get("ITALY_RAW_ASSET_LINHAS"),
        L.get("ITALY_COLLECTION_RUN_LINHAS"),
        A["JA_NO_ARMAZEM"], A["GOLDEN_PATH_CONTEUDOS"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
