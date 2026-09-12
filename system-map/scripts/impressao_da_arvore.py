#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SINTONIA SYSTEM MAP · A IMPRESSAO DA ARVORE-FONTE

    O DEFEITO, COM NOME E NUMERO.

`publicar_no_deploy.mjs` ja o tinha escrito: o mapa era gerado, commitado, e o
commit mudava o HEAD — logo o carimbo nascia SEMPRE a apontar para o commit
ANTERIOR.

    commit 8e1947d2  ->  state.PROVENANCE.HEAD = c293be65
    commit c293be65  ->  state.PROVENANCE.HEAD = 44e2de1b

Ele fechou metade: o commit IMPLANTADO passou a nascer no build. Ficou a outra
metade, que e a pergunta a que o verde obedece:

    ESTE MAPA E O MAPA DESTA ARVORE?

Enquanto a prova de pertenca for um SHA DE COMMIT, ela e impossivel — nao por
falta de disciplina, mas por construcao. O ficheiro nao pode conter o SHA do
commit que so existe depois de ele entrar la.

    A PERGUNTA CERTA NAO E «QUE COMMIT?». E «QUE FONTES?».

Esta impressao mede as FONTES e exclui as SAIDAS da propria cadeia. Guardar o
mapa regerado nao mexe nas fontes, logo NAO MUDA a impressao — e a pergunta
passa a ter resposta. Editar uma fonte MUDA a impressao, e nesse caso a resposta
certa e «nao», que e exactamente o que se quer ouvir.

O SEGUNDO DEFEITO QUE ISTO FECHA
--------------------------------
Na Vercel a arvore da build NAO E a arvore do repositorio. Medido numa build
real: `Removed 1125 ignored files defined in .vercelignore`, e o mapa so podia
ficar `⚪ UNKNOWN` porque ali nao se consegue medir a arvore.

So que o `.vercelignore` apaga FICHEIROS DO DISCO. Nao apaga o INDICE DO GIT —
e o indice carrega o SHA do blob de cada ficheiro rastreado. Medido: 1504 no
indice, 1126 ausentes do disco.

    ESTAR NO INDICE  !=  ESTAR NO DISCO — e desta vez isso joga a nosso favor.

Por isso ha duas leituras da MESMA impressao, e a diferenca entre elas e so
quem fornece o SHA do blob:

    DO DISCO    ao GERAR, antes do commit existir  (Python, aqui)
    DO INDICE   ao IMPLANTAR, dentro do contentor  (Node, publicar_no_deploy.mjs)

A formula que pode divergir — lista de exclusao, algoritmo, formato da linha —
vive em `CADEIA-DO-MAPA.json`, num sitio so, e os dois lados leem-na de la.
`test_impressao_da_arvore.py` corre as duas e reprova se discordarem.

    A TRANCA CONTINUA FECHADA. ZERO FICHEIROS A MAIS FORAM ENVIADOS AO CONTENTOR.

O QUE ISTO NAO PROVA, E E PRECISO DIZER
---------------------------------------
Impressao igual prova QUE ARVORE — nunca que o mapa e o ponto fixo dela. Quem
prova isso e a P1 do validador, que regenera e compara, e essa precisa da arvore
inteira. Confundir as duas seria trocar uma prova por uma parecida.

    QUE ARVORE  !=  MAPA CORRECTO DAQUELA ARVORE.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CADEIA = json.loads((Path(__file__).with_name("CADEIA-DO-MAPA.json"))
                    .read_text(encoding="utf-8"))
LEI = CADEIA["IMPRESSAO_DA_ARVORE"]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(RAIZ), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.rstrip("\n")


def excluido(caminho: str) -> bool:
    """Saida da cadeia? A lista vem do manifesto, nunca daqui."""
    return any(caminho == e or caminho.startswith(e) for e in LEI["EXCLUIDO"])


def sha_do_disco(caminhos: list[str]) -> list[str]:
    """O SHA de blob DE CADA CAMINHO, calculado pelo proprio git.

    ⚠️ A PRIMEIRA VERSAO DISTO IMPORTAVA `sha_do_disco` DE `scan_repo.py`, E
    ESTAVA ERRADA. Reutilizar parecia a coisa certa — uma implementacao so — mas
    as duas funcoes respondem a PERGUNTAS DIFERENTES, e a medicao disse-o:

        81 ficheiros de `data/derivados/texto/` com dois SHAs diferentes,
        numa arvore de trabalho LIMPA.

    `scan_repo.sha_do_disco` normaliza CRLF para LF antes de medir, e faz bem: a
    pergunta dele e IDENTIDADE DE CONTEUDO entre maquinas, e sem isso o mapa
    gerado no Windows acusava drift contra o CI em Linux. So que aqueles 81
    ficheiros tem CRLF DENTRO DO BLOB COMMITADO — `.gitattributes` protege-os de
    proposito —, e normaliza-los devolve um SHA que o git nunca guardou.

        IDENTIDADE DE CONTEUDO  !=  O QUE O GIT GUARDA.

    Esta impressao tem de bater com o INDICE, logo tem de perguntar ao git. E
    perguntar ao git resolve o CRLF melhor do que o normalizar a mao: `git
    hash-object` aplica os filtros de `.gitattributes` e do `core.autocrlf`
    daquela maquina, o que devolve o SHA que aquele git guardaria — no Windows
    tambem. A licao do CRLF nao foi perdida; foi entregue a quem manda nela.

    Um processo so para a arvore inteira: 1500 caminhos por `--stdin-paths`.
    """
    if not caminhos:
        return []
    for c in caminhos:
        if "\n" in c or c.startswith('"'):
            raise SystemExit(f"CAMINHO_IMPOSSIVEL_DE_MEDIR={c!r}")
    r = subprocess.run(
        ["git", "-C", str(RAIZ), "hash-object", "--stdin-paths"],
        input="\n".join(caminhos) + "\n",
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise SystemExit(f"GIT_HASH_OBJECT_FALHOU={r.stderr.strip()[:200]}")
    shas = r.stdout.split()
    if len(shas) != len(caminhos):
        raise SystemExit(f"GIT_DEVOLVEU={len(shas)}_PARA={len(caminhos)}_CAMINHOS")
    return shas


def _selar(linhas: list[str]) -> str:
    corpo = LEI["SEPARADOR"].join(sorted(linhas)) + LEI["SEPARADOR"]
    algoritmo = getattr(hashlib, LEI["ALGORITMO"])
    return algoritmo(corpo.encode("utf-8")).hexdigest()


def do_disco() -> tuple[str, int, list[str]]:
    """A impressao de quem GERA: o que o git guardaria do disco, agora.

    ⚠️ A LISTA NAO E `git ls-files`, E O PORTAO 2b APANHOU-ME NISSO.

    A primeira versao listava so o que ja estava RASTREADO. O commit que trouxe
    esta lei acrescentou dois ficheiros novos, e o carimbo saiu com 1499 nomes
    enquanto a arvore commitada tinha 1501:

        CARIMBO   bfe6cfe6...  sobre 1499
        ARVORE    ace766e1...  sobre 1501

    Todo commit que ACRESCENTA um ficheiro batia neste desencontro, porque quem
    gera nao consegue ver o que ainda nao foi adicionado ao indice. A lista certa
    e a que `git add -A` levaria: rastreados MAIS os novos que o `.gitignore` nao
    manda ignorar.

        O QUE VAI SER COMMITADO  !=  O QUE JA ESTA RASTREADO.

    O efeito lateral e desejado: um ficheiro por commitar que nao esta ignorado
    move a impressao, e o portao 2b reclama. Isso e uma queixa verdadeira — a
    arvore tem trabalho solto — e nao um falso alarme.

    Ficheiro rastreado e ausente do disco NAO e saltado em silencio — ao gerar,
    a arvore tem de estar inteira, e uma ausencia aqui e uma medicao que falhou.
    Quem sabe conviver com ausencias e `do_indice()`, e por outra razao.
    """
    presentes, ausentes = [], []
    for caminho in git("ls-files", "--cached", "--others",
                       "--exclude-standard").splitlines():
        if excluido(caminho):
            continue
        (presentes if (RAIZ / caminho).exists() else ausentes).append(caminho)
    linhas = [f"{sha} {caminho}"
              for sha, caminho in zip(sha_do_disco(presentes), presentes)]
    return _selar(linhas), len(linhas), ausentes


def do_indice() -> tuple[str, int]:
    """A impressao de quem IMPLANTA: o que o git SABE, mesmo sem o disco ter.

    Esta e a leitura que funciona dentro do contentor da Vercel. O modo e o
    numero de andar (`stage`) sao deitados fora: a linha e `<sha> <caminho>`,
    como o manifesto declara.
    """
    linhas = []
    for ln in git("ls-files", "-s").splitlines():
        meta, caminho = ln.split("\t", 1)
        _modo, sha, _andar = meta.split()
        if excluido(caminho):
            continue
        linhas.append(f"{sha} {caminho}")
    return _selar(linhas), len(linhas)


# ─────────────────────────────────────────────────────────────────────────
# O CARIMBO QUE QUALQUER GERADOR PODE POR — E A REGRA DA VERSAO DE UMA ENTRADA
#
#     UM FICHEIRO COMMITADO NUNCA NOMEIA O COMMIT QUE O CONTEM.
#
# Medido em seis commits seguidos, em tres artefactos: o `PROVENANCE.HEAD` de
# cada um aponta SEMPRE para o commit ANTERIOR. Nao e desleixo de ninguem; e
# impossivel por construcao, e por isso um SHA de commit nunca prova frescura.
#
# Estas funcoes existem para que um gerador possa responder «que arvore medi?»
# sem inventar um segundo algoritmo. O selo continua a ser o de `_selar`, cuja
# formula vive em `CADEIA-DO-MAPA.json` — aqui nao nasce formula nenhuma.
#
# A REGRA DA VERSAO, E POR QUE ELA TEM DUAS METADES
#
#     FONTE    versao = o SHA do blob que o git guardaria
#     GERADO   versao = a IMPRESSAO DA ARVORE que ele proprio carimba
#
# ⚠️ A SEGUNDA METADE NAO E UM ATALHO: E A CORRECCAO DE UM ERRO. Hashar o
# CONTEUDO de um artefacto gerado parece mais rigoroso e e pior: eles carregam
# `HEAD` e `GENERATED_AT`, logo regerar a cadeia sem mudar uma linha da arvore
# movia a versao, e todo artefacto que os lesse nascia STALE em cada corrida.
#
#     UM ALARME QUE TOCA SEMPRE NAO E UM ALARME.
#
# A impressao que o artefacto gerado carimba responde «que FONTES mediste?», que
# e a pergunta de que a frescura precisa, e fica quieta quando so o relogio andou.
# ─────────────────────────────────────────────────────────────────────────
NAO_SEI = "NAO SEI"
GERADO, FONTE = "GERADO", "FONTE"

# ⚠️ UMA ENTRADA GERADA QUE AINDA NAO CARIMBA IMPRESSAO NAO PODE RESPONDER POR
# SI — e as duas saidas obvias sao ambas erradas.
#
#     hashar os bytes dela  ->  ela muda a cada corrida da cadeia (HEAD,
#                               GENERATED_AT), e quem a le nasce STALE sempre
#     dizer NAO SEI         ->  quem a le fica UNVERIFIABLE por uma divida que
#                               nao e dele
#
# A saida honesta e uma CONSTANTE que nao se move, com a falta declarada ao lado:
# a substancia dela deriva da arvore, e a arvore ja esta carimbada no relogio de
# cima. O que se perde e a capacidade de a distinguir de uma irma regerada — e
# isso fica escrito, contavel, em `CARIMBO_EM_FALTA`, em vez de escondido num
# hash que ninguem consegue explicar.
SEM_CARIMBO = "DERIVADO_SEM_CARIMBO"


def _versao_de_um_gerado(caminho: str) -> tuple[str, bool]:
    """(versao, carimbo_em_falta). Ilegivel e outra coisa: ai e NAO SEI."""
    try:
        prov = (json.loads((RAIZ / caminho).read_text(encoding="utf-8"))
                .get("PROVENANCE") or {})
    except (OSError, ValueError):
        return NAO_SEI, False
    impressao = prov.get("SOURCE_TREE_FINGERPRINT")
    return (impressao, False) if impressao else (SEM_CARIMBO, True)


def versoes(entradas: list[tuple[str, str, str]]) -> tuple[list[dict], list[str]]:
    """A VERSAO DE CADA ENTRADA QUE UM GERADOR DECLARA TER LIDO.

    Recebe `(caminho, papel, lido_por)` e devolve as fichas ordenadas por
    caminho, mais os caminhos que nao existem no disco. Uma entrada declarada e
    ausente NAO e saltada em silencio: quem le o artefacto tem de conseguir ver
    que a arvore estava incompleta quando a medicao correu.
    """
    itens, ausentes = [], []
    fontes = [c for c, papel, _ in entradas
              if papel == FONTE and (RAIZ / c).is_file()]
    shas = dict(zip(fontes, sha_do_disco(fontes))) if fontes else {}
    for caminho, papel, lido_por in entradas:
        if not (RAIZ / caminho).is_file():
            ausentes.append(caminho)
            continue
        falta = False
        if papel == GERADO:
            versao, falta = _versao_de_um_gerado(caminho)
            como = ("SOURCE_TREE_FINGERPRINT que o proprio artefacto carimba"
                    if not falta else
                    "constante: este artefacto gerado ainda nao carimba impressao, "
                    "logo nao consegue dizer que arvore mediu")
        else:
            versao, como = (shas.get(caminho, NAO_SEI),
                            "SHA do blob que o git guardaria deste caminho")
        ficha = {"PATH": caminho, "PAPEL": papel, "VERSAO": versao,
                 "COMO_SE_MEDE": como, "LIDO_POR": lido_por}
        if falta:
            ficha["CARIMBO_EM_FALTA"] = True
        itens.append(ficha)
    itens.sort(key=lambda x: x["PATH"])
    return itens, sorted(set(ausentes))


def selar_entradas(itens: list[dict]) -> str:
    """UMA FORMULA DE SELAGEM SO — a de `_selar`, sem copia."""
    return _selar(["%s %s" % (i["VERSAO"], i["PATH"]) for i in itens])


def carimbo(gerado_por: str, entradas: list[tuple[str, str, str]]) -> dict:
    """O BLOCO DE PROVENIENCIA QUE TORNA UM ARTEFACTO AFERIVEL.

    `HEAD` fica — ele diz QUANDO — mas vai acompanhado da razao de nao servir de
    prova. Quem responde «que arvore?» e `SOURCE_TREE_FINGERPRINT`; quem responde
    «as entradas continuam nas versoes que li?» e `INPUTS_DIGEST`.
    """
    impressao, n, fora_do_disco = do_disco()
    itens, ausentes = versoes(entradas)
    return {
        "GENERATED_BY": gerado_por,
        "GENERATED_AT": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "HEAD": git("rev-parse", "HEAD"),
        "HEAD_VERIFICAVEL": False,
        "HEAD_PORQUE_NAO": ("um ficheiro commitado nunca nomeia o commit que o "
                            "contem; este carimbo nasce a apontar para o anterior. "
                            "A prova de frescura e SOURCE_TREE_FINGERPRINT."),
        "SOURCE_TREE_FINGERPRINT": impressao,
        "FICHEIROS_NA_IMPRESSAO": n,
        "FICHEIROS_RASTREADOS_AUSENTES_DO_DISCO": fora_do_disco,
        "INPUTS": itens,
        "INPUTS_COUNT": len(itens),
        "INPUTS_DIGEST": selar_entradas(itens),
        "INPUTS_AUSENTES": ausentes,
    }


def frescura_do_carimbo(prov: dict | None) -> dict:
    """CURRENT · STALE · UNVERIFIABLE · UNKNOWN — e quem pergunta nao e quem escreveu.

    Tres relogios, nunca um:

        A ARVORE     a impressao das FONTES mudou desde que isto foi medido?
        AS ENTRADAS  alguma entrada declarada esta noutra versao?
        O CICLO      alguma entrada GERADA mediu uma arvore que nao e esta?

    Os dois primeiros comparam o artefacto CONSIGO MESMO no tempo: se ninguem
    mexeu em nada desde que ele correu, dizem CURRENT — e dize-lo-iam mesmo que
    ele tivesse medido um `.generated.json` de ha tres arvores atras. O terceiro
    e a lei do ciclo atrasado (§9.2 do contrato) e existe para que regerar sobre
    uma entrada velha nao passe por actual.

        REGERAR SOBRE UMA ENTRADA VELHA NAO TORNA A ENTRADA NOVA:
        TORNA A MENTIRA MAIS RECENTE.

    ⚠️ ELE NOMEIA E NAO REPARA. Ordenar a cadeia pelos INPUTS declarados e outro
    trabalho; usar este relogio para calar o caso seria trocar uma divida por um
    verde.
    """
    if not prov:
        return {"VEREDITO": "UNKNOWN", "MOTIVO": "SEM_CARIMBO",
                "PORQUE": "o artefacto nao traz PROVENANCE"}
    if not prov.get("SOURCE_TREE_FINGERPRINT"):
        return {"VEREDITO": "UNVERIFIABLE", "MOTIVO": "SO_CARIMBA_COMMIT",
                "PORQUE": ("nao carimba SOURCE_TREE_FINGERPRINT; um SHA de commit "
                           "nao se consegue verificar por construcao")}
    declarados = prov.get("INPUTS") or []
    agora, _, _ = do_disco()
    arvore_bate = agora == prov["SOURCE_TREE_FINGERPRINT"]
    if not declarados:
        return {"VEREDITO": "CURRENT" if arvore_bate else "STALE",
                "MOTIVO": "SO_A_ARVORE", "ARVORE_BATE": arvore_bate,
                "IMPRESSAO_CARIMBADA": prov["SOURCE_TREE_FINGERPRINT"],
                "IMPRESSAO_AGORA": agora,
                "PORQUE": ("o artefacto nao declara INPUTS: so a arvore pode ser "
                           "aferida")}

    sumidos = [i["PATH"] for i in declarados if not (RAIZ / i["PATH"]).is_file()]
    if sumidos:
        return {"VEREDITO": "UNVERIFIABLE", "MOTIVO": "ENTRADA_DESAPARECEU",
                "PORQUE": "entradas declaradas que ja nao existem: %s" % sumidos[:5],
                "IMPRESSAO_AGORA": agora}

    hoje, _ = versoes([(i["PATH"], i.get("PAPEL", FONTE), "") for i in declarados])
    sem_carimbo = sorted(i["PATH"] for i in hoje if i.get("CARIMBO_EM_FALTA"))
    por_caminho = {i["PATH"]: i["VERSAO"] for i in hoje}
    if NAO_SEI in por_caminho.values():
        return {"VEREDITO": "UNVERIFIABLE", "MOTIVO": "ENTRADA_SEM_VERSAO",
                "PORQUE": "entradas sem versao afericavel: %s"
                          % [c for c, v in sorted(por_caminho.items())
                             if v == NAO_SEI][:5],
                "IMPRESSAO_AGORA": agora}

    selo_agora = selar_entradas(hoje)
    entradas_batem = selo_agora == prov.get("INPUTS_DIGEST")
    mexidas = sorted(i["PATH"] for i in declarados
                     if i.get("VERSAO") != por_caminho.get(i["PATH"]))
    # ⚠️ O RELOGIO DO CICLO PERGUNTA PELO QUE FOI LIDO, E NAO PELO QUE ESTA LA
    # AGORA — e a primeira versao disto perguntava mal.
    #
    # Ela comparava a versao ACTUAL da entrada com a arvore de agora. Medido num
    # clone: correr a cadeia uma vez depois de mexer numa fonte deixa o pente
    # fino a medir o estado ANTERIOR, mas o estado no disco ja e o novo — logo a
    # comparacao dava «iguais» e o ciclo atrasado passava despercebido.
    #
    #     A PERGUNTA E «QUE ARVORE MEDIA A ENTRADA QUANDO EU A LI?»,
    #     E NAO «QUE ARVORE ELA MEDE AGORA?».
    #
    # A comparacao certa e entre a versao que o artefacto REGISTOU e a arvore que
    # ele proprio diz ter medido. Assim o veredito e uma propriedade do artefacto,
    # e nao do que aconteceu ao disco depois dele.
    #
    # Uma entrada sem carimbo fica de fora: ela nao diz que arvore mediu, e
    # acusa-la seria inventar uma resposta que ela nunca deu.
    ciclo = sorted(i["PATH"] for i in declarados
                   if i.get("PAPEL") == GERADO
                   and i["PATH"] not in sem_carimbo
                   and i.get("VERSAO") != prov["SOURCE_TREE_FINGERPRINT"])

    atual = arvore_bate and entradas_batem and not ciclo
    if atual:
        motivo, porque = "CURRENT", "a arvore e as entradas sao as que foram medidas"
    elif ciclo:
        motivo = "STALE_BY_CYCLE"
        porque = "entrada gerada que nao mediu esta arvore: %s" % ciclo[:5]
    else:
        motivo = "ARVORE_MUDOU" if not arvore_bate else "ENTRADA_MUDOU"
        porque = ("mudou %s%s%s desde a medicao"
                  % ("a arvore" if not arvore_bate else "",
                     " e " if not arvore_bate and not entradas_batem else "",
                     "alguma entrada" if not entradas_batem else ""))
    return {
        "VEREDITO": "CURRENT" if atual else "STALE",
        "MOTIVO": motivo,
        "ARVORE_BATE": arvore_bate,
        "ENTRADAS_BATEM": entradas_batem,
        "ENTRADAS_GERADAS_DE_OUTRA_ARVORE": ciclo,
        "ENTRADAS_SEM_CARIMBO": sem_carimbo,
        "IMPRESSAO_CARIMBADA": prov["SOURCE_TREE_FINGERPRINT"],
        "IMPRESSAO_AGORA": agora,
        "INPUTS_DIGEST_CARIMBADO": prov.get("INPUTS_DIGEST"),
        "INPUTS_DIGEST_AGORA": selo_agora,
        "ENTRADAS_QUE_MUDARAM": mexidas[:10],
        "PORQUE": porque,
    }


CARIMBADO_EM = "system-map/data/architecture.generated.json"


def carimbo_commitado() -> str | None:
    """A impressao que o mapa COMMITADO traz — lida do commit, nao do disco."""
    bruto = git("show", f"HEAD:{CARIMBADO_EM}")
    if not bruto:
        return None
    try:
        return (json.loads(bruto).get("PROVENANCE") or {}).get("SOURCE_TREE_FINGERPRINT")
    except json.JSONDecodeError:
        return None


def conferir_carimbo() -> int:
    """O PORTAO QUE PAGA O PRECO DESTA LEI, E PAGA-O A PORTA.

    A impressao cobre a arvore INTEIRA, de proposito: cobrir «so o que alimenta o
    mapa» exigiria adivinhar o que seis scanners leem, e adivinhar de menos
    produz um VERDE FALSO — o unico erro que este repositorio nao pode dar.

    O preco e real e tem de ser dito: mudar QUALQUER ficheiro rastreado move a
    impressao, mesmo um `.md` que nao muda o mapa. Sem este portao, esse commit
    passava no CI (a P1 ignora o bloco PROVENANCE, e tem de ignorar), era
    implantado, e so entao a tela gritava STALE — um alarme verdadeiro sobre uma
    mudanca legitima, e a chegar tarde e no sitio errado.

        UM ALARME QUE SO TOCA DEPOIS DO DEPLOY E UM ALARME MAL COLOCADO.

    Entao o preco cobra-se aqui: quem mexe na arvore volta a correr a cadeia. Nao
    e regra nova — `AGENTS.md` ja manda regerar e validar antes de fechar a
    tarefa. E o que muda e que agora isso reprova em vez de pedir por favor.
    """
    commitado = carimbo_commitado()
    arvore, n = do_indice()
    if commitado is None:
        print("CARIMBO_AUSENTE · o mapa commitado nao traz SOURCE_TREE_FINGERPRINT. "
              "Corra a cadeia de CADEIA-DO-MAPA.json e commite o resultado.",
              file=sys.stderr)
        return 1
    print(f"CARIMBO_COMMITADO   {commitado}")
    print(f"ARVORE_COMMITADA    {arvore} sobre {n} ficheiro(s)-fonte")
    if commitado != arvore:
        print("IMPRESSAO_DO_CARIMBO=DIFERENTE · o mapa commitado foi gerado de OUTRA "
              "arvore. Alguem mudou um ficheiro rastreado e nao regerou. Corra os "
              "passos de REGERAR em CADEIA-DO-MAPA.json e commite o resultado.",
              file=sys.stderr)
        return 1
    print("IMPRESSAO_DO_CARIMBO=IGUAL · o mapa commitado e o mapa desta arvore")
    return 0


def main() -> int:
    if "--conferir-carimbo" in sys.argv:
        return conferir_carimbo()
    disco, n_disco, ausentes = do_disco()
    indice, n_indice = do_indice()
    igual = disco == indice
    print(f"IMPRESSAO_DO_DISCO   N={n_disco} {disco}")
    print(f"IMPRESSAO_DO_INDICE  N={n_indice} {indice}")
    if ausentes:
        print(f"AUSENTES_DO_DISCO={len(ausentes)} · {' '.join(ausentes[:5])}")
    print(f"IMPRESSAO_DA_ARVORE={'IGUAL' if igual else 'DIFERENTE'}")
    if not igual:
        print("As duas leituras discordam: ha trabalho por commitar, ou a "
              "formula divergiu. Nenhuma das duas autoriza um verde.",
              file=sys.stderr)
    return 0 if igual else 1


if __name__ == "__main__":
    raise SystemExit(main())
