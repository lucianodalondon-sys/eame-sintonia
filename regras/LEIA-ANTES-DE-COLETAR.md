# LEIA ANTES DE COLETAR

> **Este ficheiro é gerado do System Map.** Não o edite à mão: edite a peça
> em `system-map/data/architecture.declared.json` e rode
> `py system-map/scripts/generate_system_map.py`.

Toda missão de coleta começa procurando as réguas. Elas estão todas aqui,
e o caminho de cada uma é onde ela realmente vive.

---

## ANTES DE QUALQUER COISA: CONSULTE O ACERVO

O acervo de fontes é **capital parado** — consulta-se antes de coletar. Não se
coleta para descobrir o que já se sabe.

- **AS FONTES** — O capital parado da casa: 23 bases oficiais e abertas, mais 44 contas publicas do concorrente em 4 plataformas. Consulta-se antes de coletar.
  - `docs/fontes/ATLAS-DE-FONTES-EAME.md`
  - `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`
  - `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`
- **O que a ADAMA sabe de si** — O catalogo comercial e o portfolio da ADAMA lidos por dentro: o que vende em cada pais, com que rotulo, modo de acao e substancia — e onde ha lacuna.
  - `fontes/adama_catalogo_ler.py`
  - `fontes/adama_catalogo_montar.py`
  - `fontes/adama_it_eu.py`

```bash
py candidatas/fonte_nova.py --listar     # a fila de fontes candidatas
py candidatas/fonte_nova.py --tipos      # os tipos aceites
```

**Fonte nova entra pela porta, e o que entra é candidata — nunca fonte.**
Fonte nasce quando alguém a abre, olha o que ela entrega e guarda evidência.

---

## AS RÉGUAS DA COLETA

Cada uma vale no **momento em que o dado entra**. Depois é tarde.

### As palavras que a busca digita

Os termos de busca, agrupados por cultura-problema, na lingua de quem trabalha no campo. Sao 103 palavras em dois ficheiros: 35 do censo de rotulos, todas italianas, e 68 do sensor, das quais 13 recortes de 17 sao da Italia.

*Por que existe:* Buscar 'septoria wheat' na Italia devolve literatura internacional, nao a conversa tecnica de quem esta no campo — o que se procura e 'septoriosi del frumento'. E o CROP e o ISSUE de cada item saem DESTA consulta, nunca de leitura livre do titulo, e e isso que torna a linha auditavel.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/rotulos_censo.py` |
| onde vive | `regras/sensor_coleta.py` |
| onde vive | `regras/sensor_medir.py` |

### De onde veio — carimbado na coleta

Carimba, em cada registo, de onde ele veio — no momento em que ele entra.

*Por que existe:* Sem procedencia, um numero vira verdade so porque esta escrito. E ela so vale se for posta na coleta: depois e tarde, porque o dado ja entrou sem ela e ninguem consegue recuperar a origem.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/proveniencia.py` |

### O contrato de cada fonte italiana

13 contratos executaveis: quem e, onde esta, como se acha, o que se espera de volta, como se sabe que e o documento certo — e COMO ELE FALHA.

*Por que existe:* Os testes precisaram de ver vermelho: oito documentos foram corrompidos de proposito, na memoria e nunca no disco, e os oito reprovaram. Um PDF que virou «Access denied» com HTTP 200 reprovou — porque 200 nao e prova de nada. Teste que nunca viu vermelho nao e teste.

| | |
|---|---|
| estado | PENDING — e uma lei sem prova executavel apontando para ela. |
| onde vive | `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md` |
| onde vive | `regras/italy_contract_test.mjs` |
| onde vive | `regras/italy_contracts.mjs` |
| onde vive | `regras/italy_pilot_guards.mjs` |
| onde vive | `regras/italy_scheduling_guards.mjs` |
| onde vive | `regras/italy_source_health.mjs` |

### Quem esta autorizado a ser coletado

A regua que decide se uma conta publica entra na coleta: identidade provada e conta local do pais.

*Por que existe:* Estar na lista nao e autorizacao. Sem esta regua, oito execucoes pagas ja foram queimadas nesta casa devolvendo o alvo errado.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `data/samples/COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json` |
| onde vive | `regras/comunicacao_identidade.py` |
| onde vive | `regras/comunicacao_lote.py` |
| onde vive | `regras/comunicacao_universo.py` |

---

## COM O QUE SE VAI

- **A fala vira texto, sem fatura** — Transcreve o audio dos videos na propria maquina, com whisper local.
- **Abrir PDF, ODS e HTML** — Tira o texto de dentro de um PDF, de uma planilha ODS ou de uma pagina.
- **Apify — a rota paga** — Guarda e reveza as chaves de acesso das coletas pagas, e limpa qualquer mensagem de erro antes de escrever no log.
- **O navegador — a rota gratis** — Abre a pagina publica pelo proprio navegador e le o que ela ja mostra de graca.

---

## O PADRÃO, E O CHÃO QUE NÃO DESCE

```bash
py medidas/padrao_da_coleta.py
```

Dez regras medidas a cada corrida do CI. Ele **não** exige que esteja tudo
certo hoje — exige **não piorar**. Um coletor novo sem carimbo de data faz
o número subir, e o portão reprova nomeando o ficheiro.

O que todo registo de coleta tem de carregar:

| campo | por quê |
|---|---|
| `RAW_SHA256` | testemunho não é prova |
| `CAPTURED_AT` | quando eu vi |
| `FACT_TIME` | quando aconteceu — **não é o mesmo** |
| `SOURCE_LOCATION` / `FACT_LOCATION` | de onde veio o documento ≠ onde o fato é |
| `CADENCE_STATE` | sem ela, fonte morta parece fonte quieta |
| `EGRESS_IP` | por onde a requisição saiu |
| `ITEM_COUNT_RAW` → `NORMALIZED` | o que veio, e o que atravessou a régua |
| `COST_USD` | mesmo quando é zero — medido ≠ ausente |

---

## AS LEIS QUE NÃO SE QUEBRAM

- **NÃO SEI continua NÃO SEI.** Registrar desconhecido é resultado válido.
- **Ausência não é ausência no mundo.** «Não encontrámos nesta leitura»,
  nunca «não existe».
- **Lista vazia é FALHA, não zero.** A diferença entre «não há» e «não
  consegui ver» é a diferença entre um relatório e uma mentira.
- **`HTTP 200` não basta.** Há 200 com página de erro: status bom, corpo lixo.
- **Endereço errado nosso não é bloqueio da fonte.**
  `ROUTE_NOT_FOUND ≠ SOURCE_BLOCKED`.
- **Estado de porta não é veredito.**
  `ACCESS_CLASSIFICATION ≠ ANALYTIC_VERDICT`.
- **Número digitado à mão mente.** Contagem é calculada, nunca digitada.
- **Teste que nunca viu vermelho não é teste.**

---

Gerado de 4 réguas, 4 ferramentas e 2 peças de fonte declaradas no mapa.
