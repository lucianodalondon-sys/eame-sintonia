# QUATRO-CHAVES-V1 — a Sala tem de receber janelas

> Coleta/Admissão, **não** Intelligence. Trava D33 intacta. **Não instalado.** Rede **fechada**
> em toda a missão (proxy `127.0.0.1:9`). A Sala real só foi **lida**, com a sessão forçada a
> só-leitura. Nada foi escrito na Sala, no livro de decisões nem nos livros das fontes.

| campo | valor |
|---|---|
| ramo | `quatro-chaves-v1` a partir da produção `servico-20260923-0923` @ `7cdb7ea4` |
| regra de admissão medida | **v9** (T2 v8 · T1 v9) |
| ponto 1 | `data/derivados/QUATRO-CHAVES-V1/PONTO-1.md` (entregue antes, `97cc56d3`) |

## 1 · Ponto 1 — quantos SIM T1/T2 entrariam hoje (resumo)

**0 SIM** em 111 textos T1/T2 já guardados. **A régua não bloqueia**: a porta inteira aceita os
boletins de referência (T2 41/41 com origem; T1 51/55). **O material guardado é que não é
boletim**: T2 70 capas, T1 4 capas, e notícias de outros assuntos (T1 8, T2 4). As duas T2 da 1.ª
onda (ARPA Marche, ARPAE) trouxeram notícias. **A MICRO só trava se o lote voltar a apontar para
a página de entrada ou para notícias.** Buraco: os 4 textos da ARPAV (IT-T2-002) não estão no
armazém.

## 2 · As 4 chaves na cadeia coleta → admissão → Sala

| chave | onde DEVERIA nascer | o que existe hoje | onde se perde |
|---|---|---|---|
| **cultura** | na régua T1, que já a lê | `admissao/admissao.py:1460` `CULTURA_OBRIGATORIA` (vocabulário); `:866` a régua devolve `{"cultura": True}` — **sabe QUE há, não diz QUAL** | (a) `:866` só booleano; (b) `pronto_para_inteligencia` (`:1886`) não tem campo; (c) Sala: `admissao/sala_de_espera.py:131` `CAMPOS_READY` (19 fixos) e `:630` descarta o resto |
| **fase** | na régua T1 (momentos) | `:866` `palavras` — até 8 momentos (fioritura, soglia di intervento, trattamento…) | as mesmas (b) e (c): a evidência fica no livro de decisões, **não** atravessa para o READY |
| **região do FATO** | no contrato da fonte → no item | `regras/contratos_de_fonte.py:219-234` `regra_do_lugar_do_fato()` devolve o **`FACT_LOCATION_RULE`** do contrato (onde procurar, «não é um valor»); o item só tem `fact_location` se o coletor o puser; `pronto_para_inteligencia` copia-o (`:1964`) | **ninguém aplica a regra** ao documento: 0 usos em `coleta/`, `admissao/`, `orquestrador/` que produzam `fact_location` para documentos (só `coleta/scrap_colheita.py:512` lê o contrato, para outro fim). Resultado na Sala: `NAO SEI` em 69/69 |
| **janela** (intervalo + safra) | em lado nenhum hoje | o mais perto é `fact_time` (`:1969`), um **ponto**, e ninguém o extrai de documentos | não existe; a régua **não** extrai intervalo nem safra |

## 3 · A proposta mínima — implementada e testada, NÃO ligada

**O que muda** (só `admissao/admissao.py`):

1. `_formas_que_casam()` (`:786`) — QUAIS formas de um conceito casam como palavra inteira; a
   mesma regra de `_casa`.
2. `janela_declarada(item, decisao)` (`:1828`) — monta as 4 chaves com a lei:

| chave | vem de | lei |
|---|---|---|
| `CULTURA` | relida no texto pela **mesma** regra da régua T1 (texto dobrado, mesma língua, mesmo vocabulário), só quando a régua T1 viu cultura | forma do vocabulário, **sem** normalizar (não é EPPO) |
| `FASE` | `palavras` da decisão T1 (os momentos que a régua achou) | sinais de momento, não estádio normalizado |
| `REGIAO_DO_FATO` | `fact_location` do item, com `fact_location_basis` | **nunca** `source_location` |
| `JANELA` | — | **NAO SEI**: a régua não extrai intervalo nem safra |
| `TEMPOS` | `fact_time`, `published_at`, `captured_at`, cada um no seu campo | FACT_TIME ≠ PUBLISHED_AT ≠ CAPTURED_AT |
| ausência | — | `NAO SEI`, nunca vazio nem None |

**O que NÃO muda, de propósito:** a **evidência da porta**. A 1.ª versão deste conserto punha
`culturas`/`momentos` na evidência da régua — e partiu `tests/test_regua_t1.py::
APortaNaoDecideAJanela`, a lei do dono da régua («a porta não decide a janela»). Recuei: a porta
fica igual e a cultura é relida a jusante. **Nenhum veredito muda.**

**Provas:**
- `tests/test_quatro_chaves.py`: antes **FAILED** (1 ok, 3 falhas, 7 erros — `testes-ANTES.txt`);
  depois **OK 11/11** (`testes-DEPOIS.txt`).
- mutação: **7/7 mortos** (`mutacao-RESULTADO.txt`): região herda a fonte · janela nasce da
  publicação · tempo do fato nasce da publicação · cultura deitada fora · outro universo inventa
  cultura/fase · ausência vira vazio · a porta ganha campo. («Outro universo» sobreviveu à 1.ª
  volta; o teste passou a usar uma decisão com palavras na evidência.)
- vizinhos (`test_regua_t1`, `test_regua_t2`, `test_espinha_da_intelligence`,
  `test_a_sala_de_espera_tem_um_dono`, `test_a_collection_preserva_o_fato`,
  `test_a_linhagem_do_ready`, 167 testes): **as mesmas 6 falhas antes e depois** (dívida da base).
- vereditos: o re-julgamento dos 111 textos gera `REJULGAMENTO-T1-T2.json` **idêntico byte a
  byte** ao de antes do conserto; os boletins-ouro T1 continuam 51 SIM / 4 NAO_SEI.
- nos 51 SIM-ouro de T1, `janela_declarada` dá **FASE em 51** e **cultura em 51** (oliva, videira,
  avelã, citrinos…); **região e janela ficam NAO SEI** — é a verdade: nenhum documento as traz
  estruturadas.

## 4 · Plano — o que falta para as chaves CHEGAREM à Sala (decisão do dono)

Ligar `janela_declarada` muda o **contrato READY de 19 campos** (dono: COL-LAW-043) e as **colunas
da Sala**. Não é conserto de bancada; precisa de ordem:

1. `admissao/admissao.py:1886` `pronto_para_inteligencia` — acrescentar `JANELA_DECLARADA`
   (= `janela_declarada(item, decisao)`);
2. migração nova na Sala: coluna `janela_declarada json` (nula para o que já lá está; o antigo
   fica `NAO SEI`, não se reescreve);
3. `admissao/sala_de_espera.py:131` `CAMPOS_READY` + `pousar` (`:361`, `:634`) + `ler`
   (`:354`, `:583`, e a reconstrução em `:630`);
4. `provas/espinha_da_intelligence.py:74-80` (a cópia do contrato — o teste que a compara falha
   de propósito até ser atualizada) e os testes do contrato (`test_a_sala_de_espera_*`,
   `test_sala_duravel`, `test_a_linhagem_do_ready*`, …);
5. **região e janela precisam da COLETA**, não da porta: aplicar `FACT_LOCATION_RULE` do contrato
   ao documento (ex. ARPAV: «a ZONA do número do arquivo») num dono só, com base escrita; e
   extrair intervalo/safra do boletim — hoje ninguém o faz.

**Ordem sugerida:** 1-4 num só passo (contrato + Sala + testes, com migração ensaiada em banco
descartável), depois 5 por fonte. Até lá, cultura e fase existem na porta e morrem na Sala.
