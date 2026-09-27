# CONTRATOS-12 — as 12 fontes web elegíveis sem contrato de coleta, e a ordem dentro do domínio

Ramo `contratos-12-v1`, a partir de `a55c667f` (ONDA2-G3). **Não instalado.** Missão:
`auditoria-madrugada/missao-contratos-12.txt`.

**Rede: zero pedidos desta bancada.** A prova de rota das 12 já tinha sido feita pela PONTE-ONBOARD
(`origin/ponte-onboard-v1` @ 819bfe81). Ela fez 3 rondas, com o portão de consenso PASS IT e no
máximo 1 fonte por domínio por ronda (`ENSAIO-2-rotas-provadas-3rondas.json`). Não se repetiu
(«não dupliques»). Todas as cópias abaixo correram com o proxy fechado (D41.3).

Livros vivos copiados às 04:36, do bot @ 7cdb7ea4; os 15 ficheiros e os sha256 estão em
`FOTO-DOS-LIVROS-0436.txt`.

## 1–2. As 12, e o contrato de cada uma

Uma fonte entra nesta lista se: ficou elegível entre 02:10 e 03:10 de 25/09, não tem contrato de
coleta e é web (fora T8 e T12). O ficheiro completo é `DOZE-WEB-SEM-CONTRATO.json`. O sha256 é a
impressão da PONTE (`curadoria/sha_do_contrato.py`: SOURCE_ID + OUTPUT_TYPE + ACQUISITION), no
contrato **em disco** do Curator.

| SOURCE_ID | Domínio | Das 46 da R1 | Janela D29 (REND) | Contrato no Curator (sha256) | Prova da PONTE | Entra no coletor |
|---|---|---|---|---|---|---|
| IT-T2-032 | arpal.liguria.it | sim | NAO_SEI | sim · `6eed46d2…` | ROUTE_PROVEN, **mesmo sha** | **ENTRA** |
| IT-T2-037 | arpat.toscana.it | sim | NAO_SEI | sim · `73876bd1…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T2-050 | arpacampania.it | sim | NAO_SEI | sim · `7f5224be…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T2-145 | arpa.veneto.it | não | não medido | sim · `246b4a24…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T2-146 | arpa.veneto.it | não | não medido | sim · `8b533e29…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T3-045 | amap.marche.it | não | não medido | sim · `49c73c40…` | **CAPABILITY_BLOCK** (a página aberta é capa, não matéria) | fica |
| IT-T5-160 | ibba.cnr.it | não | não medido | sim · `4c86a071…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T5-167 | crea.gov.it | não | não medido | sim · `5ddc65e3…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T5-185 | sostenibilita.enea.it | não | não medido | sim · `29392a11…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T5-186 | sostenibilita.enea.it | não | não medido | sim · `38169f29…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T5-187 | sostenibilita.enea.it | não | não medido | sim · `5f315fe9…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |
| IT-T7-172 | georgofili.info | não | não medido | sim · `e490f655…` | ROUTE_PROVEN, mesmo sha | **ENTRA** |

- **As 12 têm contrato no Curator.** Nenhuma está hoje na tabela do coletor (`regras/italy_contracts_onboarded.json`).
- **Janela D29:** só 3 foram medidas pela REND (NAO_SEI). As outras 9 **não foram medidas**. Não
  inventei: as 5 ARPA são agrometeorologia regional (o tipo de fonte que a D29 pede), mas a PONTE
  avisa que o item provado das ARPA **não tem ligação agrícola escrita**.

## 3. Quantas entram no coletor: **11 de 12**

Medido com o **código da PONTE-ONBOARD**, sem rede, numa cópia (`git archive origin/ponte-onboard-v1`)
com os livros vivos e as provas da PONTE:
- `onboardar_rotas_provadas.py` em modo mostrar: `ENTRA=17 FICA=23` no total. **Das minhas 12:
  ENTRAM 11; fica IT-T3-045** (`ONBOARD-PONTE-NA-COPIA-SO-MOSTRAR.txt`).
- `--aplicar` **só na cópia**: 17 escritas. A tabela do coletor passa a `6255cd27…`, **o mesmo sha**
  que a PONTE mediu no ensaio dela (`ENSAIO-5`, 856f833f → 6255cd27). Chegámos lá de forma independente.
- **A coorte com essa tabela** (cópia `C:/c12/juntos` = este ramo + livros vivos + tabela):
  `micro_coleta plano` → **PRONTAS 29** (eram 18). Painel: READY 179, elegíveis 69.
  `coorte_unica --congelar` com marcas `ENSAIO`, só na cópia → 29 (`COORTE-29-CONGELADA-SO-NA-COPIA.json`,
  sha `d38ef396…`).
- `onda_web.py --so-plano` sobre essa coorte (`ONDA-WEB-SO-PLANO-COM-AS-11.json`):
  - **correm 23 de 29**;
  - saltam por `TETO_DOMINIO` IT-T2-146 (arpa.veneto.it), IT-T5-186 e IT-T5-187 (enea.it),
    IT-T7-121, IT-T7-123 e IT-T7-135 (cia.it); IT-T7-118 corre parcial;
  - **máximo por domínio: 5**; **total previsto: 83 pedidos**. Para as 11 novas, sem histórico, a
    previsão é o teto inteiro.

⚠️ **Validade:** as provas da PONTE valem 7 dias (`PROVA_MAX_IDADE`). Se a instalação passar desse
prazo, o canário tem de correr de novo, e sem prova recente nenhuma entra. É a regra a funcionar.

⚠️ **O domínio registável junta institutos inteiros.** `ibba.cnr.it` conta como `cnr.it`,
`sostenibilita.enea.it` como `enea.it`, e o mesmo vale para todos os institutos do CNR que vierem a
entrar: **todos dividem 5 pedidos por onda**. É a letra da D38 («domínio registável»). **Pergunta
para o dono:** um instituto do CNR é um «site» ou é o CNR inteiro?

## 4. A ordem dentro do domínio (cia.it: 5 fontes, ~1,5 atendidas por onda)

**Regra** (`ferramentas/big_collection/onda_web.py`, `ordenar_por_dominio`):

    Dentro de cada domínio, primeiro quem NUNCA foi atendido, depois quem foi atendido HÁ MAIS TEMPO;
    no empate, o SOURCE_ID. As fontes de um domínio só trocam de lugar ENTRE SI; os outros domínios
    não se mexem.

- **«Atendida»** = a corrida da fonte fez ≥ 1 pedido. **O instante** vem do `RUN_ID`
  (`IT-T7-2026-09-24-120918-…`). Um `TETO_DOMINIO` sem pedido **não conta** como atendimento.
- **O histórico:** a 1.ª onda (commitada) entra sempre; as ondas seguintes entram pelo
  `ONDA-WEB-ESTADO.json` de cada uma (`--historico=a.json,b.json`).
- **É determinística:** a mesma coorte e o mesmo histórico dão a mesma ordem.
- **É justa:** roda sozinha. O teste das 3 ondas (teto 5, ~3 pedidos por fonte, 2 atendidas por
  onda) prova que **as 5 do cia.it são atendidas em 3 ondas**. Sem a regra, 3 das 5 nunca seriam.
- **Hoje:** IT-T7-112 foi a primeira atendida na 1.ª onda (12:09:18Z) e, por isso, vai primeiro outra
  vez, com IT-T7-118 parcial. Na onda seguinte vão IT-T7-121 e IT-T7-123.

**Testes:** `tests/test_onda_web.py` **17/0**. Os 5 novos: a mais antiga primeiro, nunca antes de
todas, determinística e sem mexer noutros domínios, 3 ondas cobrem as 5, e o instante vem do RUN_ID
só com pedido.
**Mutação:** `provas/onda_web_mutacao.py` **12/12 mortos** (`provas/ONDA-WEB-MUTACAO.json`); os 4
novos são W9 a W12 (sem rotação, nunca atendida para o fim, corrida sem pedido conta, fica a vez mais antiga).

## Para a PONTE-ONBOARD e para a INTEGRA-ONDA2 (sem duplicar)

- Não mexi em `onboardar_rotas_provadas.py`, `sha_do_contrato.py` nem no canário: usei-os como estão
  em `ponte-onboard-v1`.
- O `onda_web.py` deste ramo **substitui** o de `onda2-g3-v1`: é o mesmo ficheiro, com a ordem por
  cima. O pacote integrado deve levar este ramo, não os dois.
