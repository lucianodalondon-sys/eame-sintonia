# RETE-VOCI-DATI — o dado já coletado, nas gavetas do pote v2

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Nada publicado, nenhum deploy, nenhuma tela mexida. Nenhum livro vivo tocado
> (curadoria/*-V1.json de estado, data/collection-ledger, candidatas/FONTES-CANDIDATAS.json: só lidos, ou nem isso).
> Sem rede. Ramo `claude/rete-voci-dati-adapters-sit3hj`, base `00075d2`.

## 1 · O que foi feito

Um script único, **`pacote/rete_voci_dati.py`** (peça `C-RETE-VOCI-DATI`, Z-PACOTE). Ele lê só ficheiros rastreados e
devolve uma **ENTRADA-EXTRA** (`ENTRADA_EXTRA_POTE/v1`). A extra vem no formato do livro de corrida que o gerador do pote
(`pacote/pote_intelligence_casco.py`, `ce775ff5`) já lê: `LINEAGE`, `ITENS_POR_FERRAMENTA` e `GAPS`.

```bash
# o coordenador, com o livro da rodada:
python3 pacote/rete_voci_dati.py --saida C:/tmp/ENTRADA-EXTRA.json \
        --juntar C:/…/ENTRADA-DA-PONTE-Rn.json --saida-junta C:/tmp/LIVRO-Rn+EXTRA.json \
        --pote italia-portale/client/sintonia-pote.js
# sem --juntar: só a extra, que também é um livro válido sozinho
```

`juntar` só **acrescenta**:
- O cabeçalho continua a ser o da corrida: `INTELLIGENCE_RUN_ID`, `SOURCE_HEAD`, `CORTE`, `RESULT_STATE`.
- Recusa `OBJETO_ID` repetido.
- Recusa um par `(CORRIDA_UPSTREAM, ITEM_ID)` que já esteja na corrida.
- Recusa payload v1: não tem LINEAGE onde juntar.

| regra | onde |
|---|---|
| os ficheiros lidos (12), cada um com o blob do Git na prova | `pacote/rete_voci_dati.py:92` (`FICHEIROS`) |
| cada registo passa pelo **`portao_g0` do motor**; o que ele bloqueia vira lacuna contada, não objeto | `pacote/rete_voci_dati.py:189` (`Livro.item`) |
| `COLHIDO_EM` só quando o ficheiro o diz; sem ele, o G0 recebe o **limite inferior provado** (a publicação), e isso só bloqueia a mais | `pacote/rete_voci_dati.py:196` |
| «2026-09-02 (lido nesta data)» é **leitura**, não publicação | `pacote/rete_voci_dati.py:149` |
| SOURCE_ID só do Atlas + contratos do Curator + registo-mestre; um domínio com várias fichas → prefixo do caminho, senão NÃO SEI | `pacote/rete_voci_dati.py:315` |
| voices: sem pessoa (`SPEAKER_ID` NÃO SEI), só o papel; o texto do curador sobre agricultor privado não viaja | `pacote/rete_voci_dati.py:268`, `:278` |
| Meta: **«observado em 31/08/2026»**; o estado ATIVO/INATIVO é o da observação («não é o estado de hoje») | `pacote/rete_voci_dati.py:395` |
| FMC Moto Srl (motos, 11 anúncios) fora, contada | `pacote/rete_voci_dati.py:114` |
| preços ISMEA pela régua da casa (`leis/preco_de_mercado.py`) | `pacote/rete_voci_dati.py:446` |
| **série só com ≥2 pontos, períodos distintos e a MESMA unidade**; o ponto «PREV» sem data não entra | `pacote/rete_voci_dati.py:545` |
| ciência: o facto é a PUBLICAÇÃO; `STUDY_PERIOD` fica como veio; resumo não viaja | `pacote/rete_voci_dati.py:588` |
| a lista do MUR só **enriquece** (nome, fascia, ateneo, SSD) por OpenAlex ID | `pacote/rete_voci_dati.py:567` |
| independência de fontes: o grafo do motor por gaveta | `pacote/rete_voci_dati.py:715` |
| sources: rendimento contado **sobre esta extra**, provado só por itens da própria fonte | `pacote/rete_voci_dati.py:727` |
| archive: os objetos que a extra produziu, mesma espécie e mesma prova | `pacote/rete_voci_dati.py:756` |
| portão de saída: tipo, prova em G0, «hoje» afirmado, e-mail/telefone, série inválida | `pacote/rete_voci_dati.py:834` |
| junta | `pacote/rete_voci_dati.py:871` |
| contagem commitada (o teste A2 reprova se divergir da árvore) | `data/derivados/RETE-VOCI-DATI/CONTAGEM.json` |

## 2 · Quantos objetos por compartimento

Na árvore `b97b7f1`: **851 de 1.301** registos passaram G0.

| gaveta | objetos | por tipo | bloqueados em G0 (lacuna) | recusados pelo adaptador |
|---|---|---|---|---|
| **voices** | **7** | 7 SINAL | 12 | 2 (`ACESSO_DE_FONTE`: a leitura falhou) |
| **competitors** | **408** | 408 FATO (402 anúncios Meta + 6 comunicações de empresa) | 156 | 13 (11 FMC Moto + 2 que não são facto da empresa) |
| **market** | **131** | 95 FATO + **36 SERIE** | 4 (período sem ano) | 4 (a régua não lê a unidade €/Ettogrado) |
| **science** | **341** | 270 FATO (21 T6 + 249 corpus) + 71 CONTAGEM (pesquisador × par) | 278 (MUR) | 88 (prova de pessoa fraca ou fora do domínio) |
| **sources** | **10** | 10 CONTAGEM (`RENDIMENTO_DE_FONTE`) | — | 2 fontes sem prova → lacuna |
| **archive** | **887** | 773 FATO + 36 SERIE + 71 CONTAGEM + 7 SINAL | — | — |

Entram no pote sem nenhuma recusa: extra sozinha, 0 recusados; junta com a corrida sintética, os mesmos 6 recusados
dela, nenhum a mais.

## 3 · Testes — pela bateria INTEIRA, por nome

`provas/integra_noite/bateria_inteira_por_nome.py`, rede fechada, em cópias limpas (worktrees).

| | base `00075d2` | ramo `b97b7f1` |
|---|---|---|
| ficheiros de teste | 393 | 394 (+ `tests/test_rete_voci_dati.py`) |
| testes corridos | 7.373 | 7.404 |
| falhas por nome | 340 | 339 |

**0 novas.** Uma sumiu: `tests/test_o_controle_separa_lei_de_mencao.py::test_M5_o_ponto_fixo…`. A base `00075d2` é o
commit de insumos, que acrescentou um `.txt` sem regerar o mapa. O ramo regerou. Não é conserto meu de código.

Resultados em `provas/rete_voci_dati/bateria-base-00075d2.json` e `…/bateria-ramo-b97b7f1.json`.

`tests/test_rete_voci_dati.py`: **31/31**.

**Ajuste declarado:** nenhum teste da casa foi mexido.

## 4 · Mutação

`provas/_mutantes_rete_voci_dati.py` (peça `C-PROVA-RETE-VOCI-DATI`) deu **24/24 mortos** (`provas/rete_voci_dati/MUTACAO-RESULTADO.txt`). Os defeitos plantados:
- G0 ignorado
- Meta diz «hoje»
- FMC Moto entra
- série de 1 ponto
- série com unidades misturadas
- publicação vira tempo do facto
- leitura vira publicação
- SOURCE_ID da plataforma
- a pessoa da voz viaja
- texto sobre agricultor privado viaja
- archive muda a espécie
- rendimento a dobrar
- domínio ambíguo escolhe a primeira ficha
- NÃO SEI vira vazio
- o portão não olha «hoje»
- o portão não olha contacto
- a junta aceita LINEAGE repetida
- a junta deixa a extra mandar no cabeçalho
- o resumo do artigo viaja
- captura desconhecida vira data longínqua
- escrever no portal
- relógio na identidade
- prova de pessoa fraca aceite
- estado do anúncio sem a data

O R17 **sobreviveu** na 1.ª corrida (a junta recusava pelo OBJETO_ID antes de olhar a LINEAGE). Acrescentei o teste
E5; depois disso, morto.

## 5 · Mapa

- `correr_a_cadeia.py REGERAR` → `CADEIA=OK`.
- `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** (P1…P10).
- Commit dos gerados.
- `impressao_da_arvore.py --conferir-carimbo` → ver o commit final.

## 6 · O que NÃO SEI / o que ficou de fora, e porquê

1. **147 vídeos das empresas no YouTube → lacuna.** O dataset diz `IT-SRC-YOUTUBE`, que é a plataforma e não a fonte
   (COL-LAW-034). A URL `watch?v=` não traz o canal, e o Atlas não tem SOURCE_ID do canal. Ligar exige o `channel_id`.
2. **12 das 19 vozes → lacuna.** Os jornais que as publicaram (il Resto del Carlino, igrandivini, askanews, agrapress,
   argav, ANSA, risoitaliano, confagricolturaveneto) não estão no Atlas. Fonte nova entra por `candidatas/`.
3. **MUR (278) → lacuna.** O ficheiro não diz de quando é a lista, e o MUR não tem ficha no Atlas. Aqui só enriquece.
4. **Divergência de SOURCE_ID.** Os ficheiros Agri-food declaram `EU-T10-002`, mas o Atlas tem o portal como
   `EU-T10-001`. O Atlas manda; o declarado viaja em `SOURCE_ID_DECLARADO_NO_FICHEIRO`.
5. **As 589 obras T6 não estão no Git** (`foto-final/` fica fora). Entram as 21 do `ENSAIO-OFFLINE`, os 71
   pesquisador × par do `POR-EVIDENCIA` e 249 obras IT do corpus de pesquisador.
6. **Ficaram de fora de propósito, por serem pessoas privadas:**
   - os 58 comentários do YouTube (`field-voices.json`);
   - as 922 vozes do `motor/voce_dal_campo.py` (sobretudo ES/FR, com nomes ditos em transcrição).
7. **A «Rete Commerciale» simulada não foi tocada.** Não há dado real dela no repositório: **NÃO SEI**.
8. **As chaves continuam como o contrato as define.** `CROP_ID` dos cereais Agri-food fica NÃO SEI (código de produto
   não é cultura), e `COMPANY_ID` das comunicações também. Fora do contrato viajam: `TIPO_DO_DADO`, `OBSERVADO_EM`,
   `TERMOS_DE_CULTURA`, `PONTOS`…
9. **Design:** nenhuma mudança visual (o casco lê as gavetas como já lia). `ADAMA_DESIGN_SYSTEM_MATCH` não se aplica.
10. **Dependências:** `python3` 3.11, PyYAML e `node` 22 presentes. Nenhuma contornada.

## EM PALAVRAS SIMPLES

A vitrine tinha prateleiras vazias com um bilhete «vazio porque…», enquanto no armazém já havia mercadoria:
- vozes do campo;
- preços do ISMEA e da Comissão Europeia;
- os anúncios da concorrência vistos a 31/08;
- trabalhos científicos e pesquisadores.

Agora há **uma máquina que leva essa mercadoria para as prateleiras**. Cada peça vai com:
- **a etiqueta do que é**: facto, voz, série de preços ou contagem;
- **o recibo até à caixa onde estava**: o ficheiro, o registo, o link e as datas.

A máquina tem regras:
- O que não tem recibo não entra: fica numa lista, contado, com o motivo.
- Um anúncio diz sempre «visto em 31/08», nunca «hoje».
- Uma série de preços só existe com dois pontos ou mais, na mesma unidade.
- Ninguém privado leva o nome.

Plantei 24 defeitos de propósito, e os testes apanharam os 24.
