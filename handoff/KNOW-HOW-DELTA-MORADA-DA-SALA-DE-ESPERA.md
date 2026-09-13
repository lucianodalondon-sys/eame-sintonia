# HANDOFF · DELTA DE KNOW-HOW · A MORADA DA SALA DE ESPERA

**Para aplicar em `claude/sintonia-eame-know-how-v1` →
`SINTONIA-EAME-KNOW-HOW.md`, no PRÓXIMO NÚMERO LIVRE.**

> Quem integrar **lê o último `§` do ficheiro e usa o seguinte.** O nome deste
> ficheiro não carrega número, de propósito: o delta anterior desta linha
> (`KNOW-HOW-DELTA-108-CONTROL-PLANE.md`) ficou a mentir no nome quando outra
> missão tomou o `§108`.
>
> ```text
> UM NUMERO NO NOME DO FICHEIRO E UMA PROMESSA QUE O FICHEIRO NAO PODE CUMPRIR.
> ```
>
> As subsecções abaixo dizem `X.1`, `X.2`… — **acompanham o número escolhido**.

```
ORIGEM      C-GREADY-02 · A MORADA DA SALA DE ESPERA
MEDIDO_EM   2026-09-13
BASE        claude/raw-observation-identity-3jbwco @ 247fbf25
            trabalho em claude/funny-hypatia-y7ho5s
NAO_DUPLICA o delta do Control Plane fala de ONDE A AUTORIDADE VIVE;
            aqui fica o que se aprendeu sobre MEDIR UMA ESCOLHA QUE JA FOI FEITA
```

---

# §<PRÓXIMO LIVRE> · UMA PROVA VERMELHA POR FALTA DE FERRAMENTA NÃO DIZ NADA SOBRE O CÓDIGO

## O QUÊ

A Sala de Espera do SINTONIA vive num ficheiro por corrida
(`data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`), com **um** dono
(`admissao/sala_de_espera.py`), escrita atómica, trava por corrida, retry
idempotente e conflito explícito. `G-READY-01` e `G-READY-02` estão fechados.

Esta missão foi mandada **decidir** isso. Encontrou a decisão já tomada por
gente em `docs/decisoes/ADR-SALA-DE-ESPERA-V1.md`, um dia antes. Então mudou de
trabalho: em vez de escolher, **auditou** — bancada própria, opção B construída
a sério em PostgreSQL real, 16 ataques — e confirmou.

## X.1 · O QUE QUASE CORREU MAL, E É A LIÇÃO PRINCIPAL

A prova canónica da Sala de Espera correu e deu isto:

```
FALHA E2_a_porta_respondeu_SIM_a_um_documento_REAL   a porta disse -
FALHA E3_a_unidade_POUSOU_na_sala_de_espera          estado=None
... e mais 15 FALHA em cascata
POUSA_NA_ESPERA=FAIL
```

Um relatório escrito nesse instante teria dito **«a Sala de Espera não
funciona»**, e teria sido falso em todas as palavras. O que faltava era
`pdftotext` na máquina. Sem ele a derivação não produz texto, a cadeia para em
`DERIVED`, e **os 24 casos a jusante caem como dominó** — nenhum deles por
defeito nenhum.

```
UMA PROVA VERMELHA POR FALTA DE FERRAMENTA
DIZ ALGO SOBRE A MAQUINA, E NADA SOBRE O CODIGO.
```

Instalado o `poppler-utils` e dado um banco descartável **virgem** (o outro já
tinha migrations de uma corrida anterior, e a 001 rebentava com
`type "pais" already exists`), a mesma prova, sem uma linha alterada:

```
POUSA_NA_ESPERA=PASS · 26/26
```

O sinal de alarme que devia ter disparado mais cedo: **uma cascata de falhas
que começa toda no mesmo ponto** raramente são N defeitos. É um defeito, ou nem
isso — é a bancada.

## X.2 · TRÊS «FACTOS» MEDIDOS COM O GREP ERRADO, E OS TRÊS ERAM FALSOS

A missão começou com uma remedição rápida que produziu três FAIL. Nenhum
sobreviveu ao segundo olhar:

| «facto» | o que era mesmo |
|---|---|
| `READY tem DOIS construtores` | a 2.ª ocorrência é uma **string literal** em `generate_system_map.py:1060`, ponteiro de prova para o mapa |
| `existe tabela canónica READY` | `grep -i ready` casou com **«already exists»** em dois comentários, e com o valor `READY` de um ENUM de etapas |
| `a morada em ficheiro NÃO existe` | a **pasta** não existe; o **código** existe, tem dono e dois chamadores |

```
UM GREP QUE CONTA DEFINICOES TEM DE SABER
DISTINGUIR UMA DEFINICAO DE UMA CITACAO DELA.
```

E o terceiro é o mais subtil, porque a resposta certa já tem nome na casa:

```
DESTINO VAZIO != DESTINO SEM DONO.   (CAN DO != DID DO)
```

## X.3 · O RED TEAM ACUSOU DUAS PROVAS INOCENTES — PELA MESMA RAZÃO

O ataque `RT15` («escrever na morada sem passar pelo dono») perguntava:

```python
if "PRONTO-PARA-INTELIGENCIA" in t and "espera." not in t:   # ← NOMEAR
```

e acusou `provas/a_fronteira_da_coleta.py` (que faz `os.path.isdir(destino)`
para **medir**) e `provas/mutacao_do_fluxo_canonico.py` (que carrega a morada
numa string de **mutação**, aplicada a uma cópia da árvore num temporário).

```
NOMEAR UMA MORADA NAO E ESCREVER NELA.
```

É a **terceira** vez neste par de missões que o mesmo erro aparece com outra
roupa, e é a mesma família do `RT01` que o censo do Control Plane cometeu
contra si próprio: **casar com a menção quando a pergunta era sobre o
comportamento.**

E o conserto tem uma regra própria: o detetor foi **corrigido** para só acusar
quem leva um caminho derivado da morada a uma chamada de escrita.

```
UM FALSO POSITIVO CONSERTA-SE NO MEDIDOR, E NAO NA PROSA DO RELATORIO.
Escrever «isto e falso positivo» por baixo de um FALHA deixa o medidor a
mentir para a proxima pessoa.
```

## X.4 · UM NÚMERO SEM A BASE CONTRA A QUAL FOI MEDIDO NÃO É UM NÚMERO

O ramo `tmp/know-how-ready-address-20260913` foi registado como tendo **0
commits únicos** — sem dizer contra quê. Medido a sério:

| base | commits únicos |
|---|---|
| `origin/main` | 271 |
| a linha funcional | 127 |
| `origin/claude/sintonia-eame-know-how-v1` | **0** |

As três medições estão certas. Só uma responde à pergunta que interessava
(«perde-se trabalho se eu apagar isto?»), e é a terceira — o tip **está
contido** na linha do know-how.

```
«0 COMMITS UNICOS» SEM BASE E UMA FRASE QUE PARECE MEDICAO E NAO E.
```

## X.5 · CONSTRUIR A OPÇÃO PERDEDORA A SÉRIO É O QUE TORNA A VITÓRIA UMA MEDIÇÃO

A OPÇÃO B (PostgreSQL) podia ter sido descartada em prosa. Em vez disso levou
**a mesma bateria com os mesmos nomes de caso**, contra PostgreSQL 16 real,
numa tabela com os 11 campos e nem um a mais. Resultado: `21/21 PASS`.

```
UMA OPCAO QUE NUNCA CORREU NAO PERDE NEM GANHA. ELA NAO FOI MEDIDA.
```

E só por ter corrido é que apareceram as três coisas que nenhuma prosa teria
dado:

1. **`on conflict do nothing` engole uma história divergente em silêncio.** O
   ficheiro levanta `ConflitoDeCorrida` e nomeia o caminho. Medido, não suposto.
   E `do update ... where` também devolve 0 linhas: para o banco **gritar**, ele
   tem de LER-E-COMPARAR antes — que é exatamente o que o ficheiro já faz.
2. **A chave estrangeira para o RAW não está à venda.** `ITEM_ID` é
   `decisao.item`, texto natural. Sem um 12.º campo não há FK — e o 12.º campo é
   o que a `COL-LAW-043` proíbe. Compra-se um banco pela integridade
   referencial, e aqui ela não vem na caixa.
3. **`psql -c` rebenta o `ARG_MAX` num lote de 5000 unidades**, antes de o
   PostgreSQL ver um byte. Não é limite do banco: é limite do idioma que a casa
   usa em todo o lado.

## X.6 · O PORTÃO QUE NÃO VÊ O FICHEIRO NOVO APROVA-O SEM O LER

O validador do System Map deu `18/18 PASS` com as duas provas novas na árvore —
e `P9_CODIGO_DECLARADO` («todo ficheiro de código pertence a uma peça do mapa»)
passou **não por elas estarem declaradas, mas por o scanner não as ver**: ele lê
ficheiros **rastreados pelo git**, e elas estavam por commitar.

```
UM PORTAO VERDE SOBRE UM FICHEIRO QUE ELE NAO LE
E UM PORTAO VERDE SOBRE NADA.
```

A ordem certa é **commitar e só então regerar o mapa**. É primo do
`O COMMIT NAO PODE CONHECER O SEU PROPRIO SHA` que a casa já tinha escrito.

## X.7 · CONSEQUÊNCIA

A Sala de Espera fica em ficheiro, e o veredito é `FILE_WAITING_ROOM_WINS` —
mas o que torna a decisão barata **não** é o ficheiro:

```
O DONO UNICO E O QUE TORNA A DECISAO REVERSIVEL.
```

Porque `admissao/sala_de_espera.py` é o único escritor, trocar o meio mais tarde
é uma mudança **dentro** dele, e não uma reescrita de quem o chama. A parte cara
já está paga, e foi paga por outra missão.

O que fica por ganhar, e não tem consumidor que o peça hoje: unicidade garantida
pelo motor, consulta por campo, e leitura parcial.

```
UMA VANTAGEM SEM CONSUMIDOR E UMA CONTA A PAGAR ANTES DO JANTAR.
```
