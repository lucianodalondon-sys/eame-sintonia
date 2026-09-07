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

### A regra de coleta externa

A lei que diz o que se coleta primeiro e o que nao pode ser esquecido: video, pesquisadores e LinkedIn nao sao acessorios.

*Por que existe:* Veiculo sem regra atropela. A ordem de prioridade nao e gosto: video vem primeiro porque e a unica camada que entrega fala tecnica longa.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `docs/operacao/PORTOES-DE-COLETA-10B.md` |
| onde vive | `docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md` |
| onde vive | `regras/portao.py` |
| onde vive | `regras/portoes_eame.py` |

### A saude de cada fonte

Diz se uma fonte respondeu bem, respondeu torto, ou nao respondeu.

*Por que existe:* HTTP 200 nao basta: ha 200 com pagina de erro — status bom, corpo lixo. Por isso a checagem e de schema e identidade. E lista vazia e FALHA, nunca 'zero resultados': a diferenca entre 'nao ha' e 'nao consegui ver' e a diferenca entre um relatorio e uma mentira.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/source_health.py` |

### As palavras que a busca digita

Os termos de busca, agrupados por pais-cultura-problema, na lingua de quem trabalha no campo daquele pais.

*Por que existe:* Buscar 'septoria wheat' na Franca devolve literatura internacional, nao a conversa tecnica francesa. E o CROP e o ISSUE de cada item saem DESTA consulta, nunca de leitura livre do titulo — e o que torna a linha auditavel.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/rotulos_censo.py` |
| onde vive | `regras/sensor_coleta.py` |
| onde vive | `regras/sensor_medir.py` |

### Cicatrizes do Brasil (lei portada)

Traz para o EAME as leis que o Brasil ja aprendeu na dor, em vez de reinventar cada uma.

*Por que existe:* O EAME nao inventa contrato novo quando o Brasil ja tem lei madura para a mesma pergunta.

| | |
|---|---|
| estado | PROVEN — existe teste que exercita esta lei. |
| onde vive | `regras/cicatrizes_brasil.py` |

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

### O lugar do fato — carimbado na coleta

Separa o lugar de onde o documento veio do lugar onde o fato aconteceu, e propoe o candidato lendo o texto na lingua do pais.

*Por que existe:* Uma fonte italiana a falar de Espanha nao torna o fato italiano. Esta e das licoes que o Brasil ensinou a esta casa, e so vale se for aplicada quando o dado entra.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/fato_local.py` |
| onde vive | `regras/lugar_do_fato.py` |

### O padrao do departamento de coleta

Mede seis coisas em toda a coleta — ficha antes de coletar, carimbo de data, fonte separada do fato, descarte registado, rendimento e custo — e reprova se alguma piorar.

*Por que existe:* Medir uma vez nao conserta nada. Ele nao exige que esteja tudo certo hoje: exige NAO PIORAR. «Esta tudo certo» nao e executavel hoje; «nao piorou» e. A divida fica a vista, com nome e numero, em vez de virar silencio.

| | |
|---|---|
| estado | PROVEN — esta no caminho: alguem o chama antes de publicar. |
| onde vive | `data/samples/PADRAO-DA-COLETA-CHAO.json` |
| onde vive | `regras/padrao_da_coleta.py` |

### O que a coleta tem de trazer

O contrato de campos por video — 32 campos, em codigo — e a regua de como o sistema fala do que colheu.

*Por que existe:* A lista esta em codigo para que o proximo pais nao a redigite e nao a encolha em silencio. Sinal nao vira pedido, ausencia nao vira negativo.

| | |
|---|---|
| estado | PROVEN — o motor importa esta lei para decidir. |
| onde vive | `regras/voz.py` |

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
- **SINTONIA SCRAP — o despachador** — O botao unico da coleta de Instagram e YouTube: 24 fases, as gratis primeiro, despachavel de qualquer lugar sem ninguem estar na maquina.

---

## O PADRÃO, E O CHÃO QUE NÃO DESCE

```bash
py regras/padrao_da_coleta.py
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

Gerado de 10 réguas, 5 ferramentas e 2 peças de fonte declaradas no mapa.
