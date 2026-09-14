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
