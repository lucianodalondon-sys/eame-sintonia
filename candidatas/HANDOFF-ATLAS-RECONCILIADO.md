# HANDOFF — RECONCILIAÇÃO DO ATLAS, PAUSADA NUM PONTO SEGURO

**Commit deste handoff:** o `HEAD` desta branch
· **Base:** `6eba72b8`
· **Branch:** `claude/italy-agricultural-sources-discovery-dfba81`

> **Para quem continuar:** tudo o que foi medido e construído está commitado e a
> funcionar. **O Atlas reconciliado NÃO foi publicado** — e o motivo não é
> técnico: apareceram duas colisões que as cinco decisões não cobrem. Um comando
> republica-o quando isso for resolvido.

---

## O ESTADO EM UMA TELA

```
CENSO                 257 identidades emitidas · proveniência 257 de 257
ATLAS RECONCILIADO    CONSTRUÍDO E PROVADO, não publicado
                      257 identidades · 0 perdidas · 0 duplicadas · 455.004 chars
                      a trava do scanner aceita-o
ATLAS NO DISCO        o de 6eba72b8, intacto (revertido de propósito)
COLISÕES              3 decididas e aplicadas · 2 NOVAS, sem decisão
SOURCE_IDS_CREATED    0
COLLECTION            todos os deltas 0
REGRESSÃO             720 testes · 37 falhas · 32 nomes = base · NEW_FAILURE 0
MAPA                  MAPA=OK · 102 peças · P9 reprova por ficheiro anterior
ÍNDICE                57 fichas · fecha com o scanner
```

## O QUE MUDOU NO NÚMERO, E POR QUE

A missão anterior disse **255 identidades**. São **257**. E o Atlas, que o mapa
via com **23** fichas, passou a ser visto com **57** — sem eu escrever uma linha
nele.

A diferença toda vem de uma coisa: **o Atlas declara identidade em quatro
formas na mesma linha `SOURCE_ID:`**, e cada leitor meu via só algumas.

| forma | exemplo | quem a perdia |
|---|---|---|
| simples | `IT-T11-001` | ninguém |
| faixa | `ES-T7-001..027` (27 identidades) | o censo e o scanner |
| multi-país | `FR-T9-001 / ES-T9-001 / IT-T9-001 (mesma natureza)` | o scanner |
| com nota | `IT-T11-001 (EIMA) · FR-T11-001 (Vinitech-SIFEL)` | o montador |

Mais dois sítios onde o Atlas declara e eu não lia: **tabelas de estado**
(`| SOURCE_ID | camada | origens |`) e fichas que vivem sob `###` em vez de
`####`. E um terceiro **emissor** que ninguém tinha contado:
`docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`, com 7 identidades.

**A regra que ficou, usada pelos três leitores:**

```
1 · um ID é declarado pela linha SOURCE_ID:, não por aparecer na ficha
2 · o que está entre parênteses é nota, não identidade
3 · o que vem depois de # é comentário (é o modelo de ficha em branco)
4 · faixa a..b é população: expandir
5 · ler CERCAS ``` , não blocos de título
```

## AS CINCO DECISÕES — APLICADAS, E DUAS ERAM CONFIRMAÇÃO

| decisão | resultado |
|---|---|
| **1 · `IT-T4-001` = Ministero** | aplicada. ⚠️ **Nunca esteve em disputa**: as duas linhas que a declaram dizem ambas «Ministero della Salute». A «afirmação ARPAV» era defeito do meu leitor |
| **2 · `ES-T4-005` = MAPA, uma fonte duas rotas** | aplicada. ⚠️ **Também não era colisão**: a ficha `ES-T4-003` escreve `SUPERSEDED_BY: ES-T4-005`, e eu lia essa referência cruzada como declaração |
| **3 · `IT-T10-001` = ARPAV** | aplicada. Colisão real. ISMEA confirmada como `IT-T10-007` |
| **4 · `IT-T10-003` = ISTAT Distribuzione** | aplicada. Colisão real. O `coeweb` fica sem identidade |
| **5 · `IT-T10-002` = OpenStreetMap** | aplicada. Colisão real. BMTI fica sem identidade. `TERRITORY_FIT_REVIEW` registado sem tocar a identidade |

E medido: **`DERIVA_DE_COUNT = 0`.** Nenhum par da população prova «mesma fonte,
dois números». Os candidatos eram membros da faixa `ES-T7` (27 fontes distintas
numa ficha) e casos de **mesmo dono, fontes diferentes** — `IT-T10-004` é o
registo do vinho e `IT-T10-005` o do azeite, ambos do ICQRF.

## ⛔ O QUE BLOQUEIA A PUBLICAÇÃO — E É POUCO

Ao unificar os leitores, **duas colisões novas apareceram**:

| ID | citações | Atlas diz | CONTRATOS diz |
|---|---|---|---|
| `ES-T3-001` | 688 | «Datos de seguimiento de plagas» · página do dataset | «RAIF Andalucía» · endpoint da API |
| `FR-T4-001` | 805 | «Données ouvertes du catalogue E-Phy» · página data.gouv | «ANSES E-Phy» · API data.gouv |

**O meu diagnóstico: nenhuma das duas é colisão.** São a **mesma fonte descrita
em dois ficheiros** — um pela página, o outro pela API. É exatamente o padrão do
`ES-T4-005`: `SAME_SOURCE_MULTIPLE_ROUTES`.

O classificador chama-lhes colisão porque compara nome+rota, e um ficheiro usa o
título do dataset enquanto o outro usa o nome do dono.

**Mas eu não decido isso sozinho** — o §7 proíbe, e são 688 e 805 referências.

### O caminho, em três passos

```
1 · confirmar que ES-T3-001 e FR-T4-001 são SAME_SOURCE_MULTIPLE_ROUTES
    (decisão humana, como as cinco)

2 · afinar o classificador: quando o HOST é o mesmo e um dos registos vem do
    ficheiro de CONTRATOS, é rota da mesma fonte — não fonte diferente
    → candidatas/registry_classificar.py, a função que marca `conflito`

3 · py candidatas/registry_montar_atlas.py
    e depois a cadeia do mapa na ordem que converge:
      py system-map/scripts/validate_system_map.py
      py system-map/scripts/scan_repo.py && py system-map/scripts/scan_sources.py
      py system-map/scripts/generate_system_map.py
```

O montador já prova o resultado sozinho: se perder ou duplicar uma identidade,
**ele para e não escreve**.

## O QUE FICOU COMMITADO E A FUNCIONAR

**Ferramentas** (`candidatas/registry_*.py`, cinco passos):

| ficheiro | o que faz |
|---|---|
| `registry_censo.py` | conta a população inteira, lendo 31 versões do Atlas e três emissores |
| `registry_classificar.py` | os sete estados, com ordem de confiança por campo |
| `registry_colisoes.py` | o dossiê de cada afirmação, com data de primeira atribuição |
| `registry_plano.py` | o plano de 273 linhas, por ordem de execução |
| `registry_montar_atlas.py` | **monta o Atlas e prova-o antes de escrever** |
| `registry_red_team.py` | 20 ataques ao censo (da missão anterior) |

**Provas** em `build/source-registry-reconciliation/`: `ALL-SOURCE-IDS.csv`
(1.747 linhas), `BRANCH-COVERAGE.csv` (257), `COLLISIONS.csv`,
`RECONCILIATION-PLAN.csv` (273), `censo.json`, `classificacao.json`.

**A trava, melhorada** — `system-map/scripts/scan_sources.py`:
- **para** quando duas fichas declaram o mesmo `SOURCE_ID`, nomeando as duas linhas
- passou a entender faixa, multi-país e nota entre parênteses
- continua a ignorar o modelo de ficha em branco (`# ex.: FR-T3-001`)
- **e foi ela que me apanhou três vezes** nesta sessão: foi a trava que apontou
  o sítio de cada defeito do meu montador

**Testes:** `tests/test_source_registry.py` (12, passam) e
`tests/test_atlas_reconciliado.py` (25, **em espera**). As 25 acendem sozinhas
no momento em que o Atlas for publicado — procuram o marcador que o montador
escreve. Deixá-las vermelhas por falta de decisão humana ensinaria a ignorar
vermelho.

## SEIS DEFEITOS DOS MEUS LEITORES, TODOS APANHADOS ANTES DE PUBLICAR

Vale a lista porque cada um produziu um número que eu ia entregar:

1. **«36 colisões» e eram 5** — eu varria URLs de toda a prosa da ficha, e a
   prosa fala de outras fontes. Uma API francesa de empresas aparecia como rota
   de fichas espanholas.
2. **17 identidades quase perdidas** — a faixa `ES-T7-001..027` lida como dois
   números.
3. **Ler as pontas das branches não basta** — `ES-T4-004` existe em 2 das 31
   versões históricas e em nenhuma ponta.
4. **`SUPERSEDED_BY` lido como declaração** — inventou a colisão `ES-T4-005`.
5. **ID mencionado num campo herdava a ficha alheia** — inventou a colisão
   `IT-T4-001`.
6. **Três leitores da mesma coisa** (censo, montador, scanner) deram três
   respostas: 255, 254 e 257. Agora leem o mesmo.

E, de processo: **usei heredoc do shell para escrever regex duas vezes** e
estraguei o ficheiro nas duas — tenho memória registada sobre isso e devia ter
usado a ferramenta de ficheiro. A segunda vez custou um `SyntaxError` commitável.

## O QUE ESTA SESSÃO NÃO FEZ

- **não publicou o Atlas** (bloqueado pelo §16, com 2 colisões sem decisão);
- **não correu o red team desta missão** (§17, 16 ataques) — o da missão
  anterior, com 20 ataques ao censo, continua verde;
- **não escreveu o relatório final** nem a entrega A–AC;
- **não criou nenhum `SOURCE_ID`**, não apagou nenhum, não reescreveu branch
  nenhuma, não fez force-push;
- **não tocou em Collection, Intelligence nem no Portal.**
