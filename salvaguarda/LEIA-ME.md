# SALVAGUARDA — NÃO CANÔNICO

**Branch:** `safeguard/local-recovery-20260914`
**Base:** `5dc11fc748a555112c7364cc1d3b53cbc142ce49`
**Data:** 2026-09-14

## O que esta branch é

Uma **cópia de segurança** do trabalho que existia apenas no disco de
`C:\eame-sintonia` e em nenhum commit, de nenhuma das branches, em 2026-09-14.

## O que esta branch NÃO é

- **Não é a linha viva.** Não representa decisão de arquitetura nem de produto.
- **Não é canônica.** Nenhum ficheiro aqui ganha autoridade por estar aqui.
- **Não deve ser integrada por merge.** Quem precisar de um ficheiro, tira o
  ficheiro. Fundir a branch inteira misturaria salvaguarda com tronco.

## Por que esta base

`5dc11fc7` era o `HEAD` de `claude/italy-forward-only-scheduling-v1`, a branch
que estava montada em `C:\eame-sintonia` quando a medição foi feita. Os
ficheiros modificados foram alterados **em cima desta árvore** — contra
qualquer outra base o diff diria que mudaram coisas que não mudaram. A base
já está publicada em `origin`, portanto a proveniência não depende deste disco.

## Como foi decidido o que entra

Para cada ficheiro calculou-se a impressão digital do conteúdo
(`git hash-object`, com o filtro de fim-de-linha aplicado) e verificou-se se
esse objeto é alcançável a partir de algum commit, em qualquer branch local ou
remota. **Só entrou o que não existia em lado nenhum.**

## O que está aqui

| Commit | Conteúdo |
|---|---|
| 1 | 102 ficheiros únicos: `DESIGN-INGEST`, código e documentos alterados, manifestos e provas de coleta, o decisório do Instagram |
| 2 | 30 ficheiros em quarentena + 3 manifestos de auditoria |

## O que NÃO está aqui, e onde está

- **8 MP4 (138 MB)** e **345 `.gz` (36 MB)** continuam só no disco. A política
  do `.gitignore` (linha 20) proíbe bruto pesado no Git. Estão registados em
  `salvaguarda/RAW-FORA-DO-GIT.json` com `path`, `bytes` e `sha256`.
  `STORAGE_STATE = NOT_UPLOADED` — **nenhum upload foi feito.**
- **49 corridas** declaram `RAW_EVIDENCE_STATE=PRESERVED` apontando para
  ficheiros que já não existem no disco. Estão em
  `salvaguarda/PRESERVED-CLAIM-UNPROVEN.json`. Isso é registo da dúvida,
  **não** conserto da perda.

## A árvore de trabalho não foi limpa

`C:\eame-sintonia` continua com os mesmos 17 modificados e 483 não rastreados.
A existência desta cópia **não** autoriza apagar o original: enquanto os MP4 e
os `.gz` não tiverem cópia provada fora do disco, apagar aquela pasta perde
353 ficheiros que esta branch não guarda.
