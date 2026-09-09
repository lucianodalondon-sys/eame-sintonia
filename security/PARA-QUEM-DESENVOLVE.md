# SEGURANCA, PARA QUEM DESENVOLVE

Uma pagina. Nao ha ferramenta nova para aprender.

## O que muda no teu dia

Nada. Faz commit como sempre. Os controlos correm sozinhos no push.

So es interrompido se estiveres a introduzir uma exposicao NOVA — e a mensagem
diz-te qual ficheiro e qual campo, nunca o valor.

    OLD SECURITY DEBT != PERMISSION TO ADD NEW DEBT.

A divida que ja existia esta congelada em `security/ratchet-baseline.json`,
aparece no relatorio como divida herdada, e nao bloqueia ninguem. O portao so
compara com ontem.

## Correr antes do push, se quiseres

```
python3 security/ratchet.py          # o portao inteiro, offline, segundos
python3 guarda/social_guarda.py      # so a guarda de credencial
```

## Se o portao te travar

Le a mensagem: ela tem a classe, o ficheiro, o campo e o porque. Depois uma de
duas coisas.

**Foi engano** — tira o campo, ou tira o ficheiro de dentro de
`italia-portale/client/`, ou acrescenta a regra ao `.vercelignore`.

**Foi deliberado e esta revisto** — `python3 security/ratchet.py --freeze` move
a chave para a divida conhecida. O commit dessa mudanca fica a dizer quem a
moveu e porque, e e por isso que isto nao e uma valvula de escape: e uma
decisao com nome.

## As perguntas que o portao faz

| | |
|---|---|
| baseline coerente | um mapeamento de norma nao aponta para um controlo que nao existe |
| credencial no Git | a arvore versionada continua sem chave, cookie ou DSN remoto |
| formas de credencial | os padroes que reconhecemos ainda reconhecem |
| redaccao em runtime | um segredo nao sai num traceback |
| ratchet | nenhuma exposicao nova: dado pessoal, motor, source map, caminho sensivel |
| o ratchet morde | provas que atacam o proprio portao |
| fronteira publicada | o que o deploy serve continua a ser o que dizemos |

E, com a sua propria cadencia: a base viva uma vez por dia, o navegador quando
os cabecalhos mudam.

## Duas coisas que vale a pena saber

**O `.vercelignore` e o `vercel.json` decidem sozinhos o que o mundo descarrega.**
Apagar uma linha de um deles publica um directorio inteiro. O portao ve isso.

**`italia-portale/client/` e publico.** Tudo o que la puseres fica a um
`curl` de distancia de qualquer pessoa, com login ou sem login.

    CODE SENT TO THE BROWSER = CODE AVAILABLE TO THE USER.

## Se alguma coisa correr mal

`security/INCIDENTE.md`. Uma pagina, cinco casos, e cada um comeca por conter o
dano.
