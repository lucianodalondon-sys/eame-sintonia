# Workflows guardados — Espanha

> ## 🗄️ PRESERVADO E INATIVO
>
> ```
> COUNTRY_SCOPE        = ES
> STATUS_OPERACIONAL   = FUTURE
> ATIVO_NA_OPERACAO_IT = NAO
> ```
>
> Este documento **não foi apagado e não vai ser**: é conhecimento pago e fica
> inteiro, pesquisável por gente. O que ele deixou de poder fazer é entrar numa
> corrida italiana — o país operacional ativo é `IT`, e a lei está em
> `regras/ESCOPO-DE-FONTES.json`. Quando a operação de Espanha abrir, isto está aqui.

---

Este ficheiro nao esta perdido: esta **guardado de proposito**.

## Porque saiu de `.github/workflows/`

O `adama-es-gate.yml` corre o portao do catalogo espanhol. Enquanto viveu em
`.github/workflows/`, o GitHub disparava-o **a cada envio de codigo** — inclusive
nos envios que so mexiam na Italia. Era o unico dos quatro botoes de coleta que
disparava sozinho, e o unico de outro pais.

Este repositorio e o projeto italiano. Um portao de outro pais a correr a cada
commit nao esta a proteger nada aqui: esta a gastar execucao e a poluir o mapa
com uma peca que diz «ESPANHA» no meio da Italia.

## O que NAO aconteceu

Nada foi apagado. O ficheiro esta inteiro, com o historico todo. O piloto de
Espanha continua a ser **projeto futuro**: construido, provado, a espera do seu
momento — nao e legado, e nao morreu.

## Como voltar a liga-lo

    git mv guarda/es/workflows/adama-es-gate.yml .github/workflows/

E depois recarimbar o mapa:

    py system-map/scripts/generate_system_map.py --stamp
    py system-map/scripts/validate_system_map.py
