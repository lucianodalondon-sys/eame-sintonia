# LINHA-BUSCA — coleta ASSUNTO-PRIMEIRO dentro da Collection canónica (D93)

> Ramo `linha-busca-v1`, criado a partir do **vivo `554c1ec1`**. Missão: coordenação 08:25; decisão do dono **D93**
> às 08:32.
>
> **Sem rede.** A Sala só foi lida: conferi que nenhuma das 13 páginas do BUSCA-LOTE-0 está no armazém.
>
> A fila do vivo não foi tocada: o sha256 deu igual antes e depois. **SEM MAPA.**
>
> A saída fica fora do Git: `C:/Users/London1/sintonia-sala-italia/linha-busca/`.

## Em palavras simples

**Porque o sistema não achava o que o Google acha.**

- A casa é **fonte primeiro**: um site sobe seis degraus antes de a primeira página dele ser colhida.
- O Google é **assunto primeiro**: pergunta-se «peronospora vite setembro», e vêm as páginas, de qualquer site.
- Das 13 páginas de ouro do BUSCA-LOTE-0, **hoje entrariam 0**. Isto vale tanto antes como depois da Admission.
  - **12** vêm de **11 sites** que **nunca estiveram na fila**. O Veneto já tem outras fontes registadas no mesmo
    portal, mas nenhuma pronta.
  - **1** vem de um site cuja fonte está em `CONTRACTED_CANARY_FAILED`: a ARSAC, IT-T12-018.
  - A página nem chega a ser pedida.

**Que lei impede o item de uma fonte CANDIDATA de entrar na Sala.** Levei isto ao dono; a D93 resolveu.

1. **O ponto exato** é `curadoria/collection_gate.py::avaliar()`, na linha que diz:
   `if estado != READY_FOR_COLLECTION: ... "so entra quem esta em READY_FOR_COLLECTION"`.
   - O próprio ficheiro chama-se «O PORTÃO DE ADMISSÃO DA COLLECTION».
   - É a ele que o coletor pergunta, em `coleta/italy_executor.py:637`.
   - A lei por trás é a **COL-LAW-053**, «a fonte nasce; não aparece pronta»: são 4 degraus, e só a fonte
     `READY` é colhida. Nesta casa o `READY` chega por **6 passos**: QUALIFY, contrato, rota, canário, régua,
     READY.
2. **O RAW também exige fonte.** `guarda/preservar_coleta.preservar()` recusa um artefacto sem `SOURCE_ID`
   («B5B · sem fonte não há observação forward»). A migração 026 exige `source_id` não vazio.
3. **A Sala exige `source_id` não vazio** (migração 031). O `READY` tira o `SOURCE_ID` só de `source_id` ou de
   `fonte`, e nunca da URL. A regra está em `admissao.py:252`: «UMA URL NÃO CRIA SOURCE_ID», que é a COL-LAW-206.
4. ⚠️ **A Admission das páginas (`admissao.decidir`) NÃO olha o estado da fonte.** Aceita a URL como origem. O
   bloqueio estava **antes** dela (1) e **depois** dela (2, 3), não nela.

**O que implementei (D93).**

- **O portão:** criei `collection_gate.avaliar_achado_por_busca()` ao lado de `avaliar()`, sem mudar a regra da
  coleta recorrente.
  - Deixa colher **uma página** achada por busca quando a proveniência vem inteira: `ACHADO_POR_BUSCA`, consulta,
    motor, posição, instante e o estado da fonte no momento.
  - Recusa se a fonte já estiver `RECUSADA` ou `POLICY_BLOCK`.
- **A identidade:** o domínio do publicador entra como **candidata pela porta canónica** (`fonte_nova.registar`).
  O `SOURCE_ID` do item passa a ser o **CANDIDATA_ID** que a porta lhe deu, como `CAND-1205`.
  - Nada é inventado: é a identidade que a casa registou para a fonte no degrau 1.
  - Quando o QUALIFY lhe der um `IT-Tn-…`, o livro do Curator liga os dois.
  - Se o site já tem **uma** fonte registada, usa-se essa.
- **A página vai à Admission normal**, pelas mesmas funções da estrada de hoje:
  `item_documental_para_a_porta`, `decidir` e `pronto_para_inteligencia`. As perguntas são as de sempre: legível,
  origem, linhagem, identidade, matéria/capa e universo.
- **Fonte recusada depois:** os itens ficam **marcados** no livro da linha (`--marcar`, D93.4). Nada se apaga.

**O ensaio sem rede com o BUSCA-LOTE-0.**

- Pelo portão D93 passam **13 de 13**, e os **11 domínios novos** entraram como candidatas numa cópia da fila.
- A Admission deu **13 de 13 em quarentena** na pergunta «matéria ou capa». ⚠️ Isto **não prevê** o resultado real:
  - não temos os bytes das páginas (0 de 13 estão no armazém);
  - no lugar delas usei um HTML mínimo com o **resumo** do coordenador, e o detetor não sabe julgar uma página tão
    curta.
- **Quantas passariam de verdade: NÃO SEI** até correr com rede. O comando está no §3, e são os mesmos 13
  endereços.
- O que se vê já nas formas das páginas é uma previsão e **pode estar errada**:
  - **4 são índices ou listas**: Reggio Emilia (14 boletins), o índice do Veneto, a página inicial de
    olivicoltori.net e a lista do Ticino. O detetor tende a chamá-las **capa**, e elas **não entram** (é a regra
    D11). O boletim de cada uma é um link lá dentro.
  - **1 é PDF** (Úmbria): não tem retrato, a pergunta de matéria não se aplica, e decide o vocabulário T3.
  - **Consórcio Fitossanitário**: a palavra «consorzio» puxa o texto para T7. No ensaio, a página de Reggio Emilia
    deu «NAO, é de T7».

**O que falta, e é do dono ou de rede.**

- **Motores:** nenhum foi medido daqui.
  - O Google e o Bing, pelo que se sabe publicamente, costumam barrar `/search` no robots.txt. A D91 manda
    respeitar o robots nas páginas comuns. Se for assim, **só sobram** as APIs oficiais (Google Programmable
    Search, Brave Search), que precisam de **chave do dono** (D88.4, conta), ou a busca feita por fora e
    **importada**, como o Hermes fez no BUSCA-LOTE-0.
  - O `--medir-motores` diz a verdade em 1 volta.
- **Teto de busca:** o domínio do motor também tem teto de **5 pedidos em 24 horas**. Por motor, isso dá **4
  consultas por dia**, porque o robots.txt gasta 1. Com 3 motores são 12. O plano tem **473 consultas**.
  - Por isso a ordem gasta primeiro as **33 nacionais**, que cobrem as 20 regiões de uma vez.
  - Subir o teto para o motor é decisão do dono.
- **O RAW desta v1:**
  - os bytes ficam com sha256 e a proveniência inteira em `RAW-LINHA-BUSCA.jsonl` + `armazem/`, na pasta da
    linha;
  - **ainda não** escrevem uma linha em `raw_asset`, porque o `preservar_coleta` exige uma corrida própria;
  - na Sala, o item entra com `RAW_OBSERVATION_ID = NAO SEI`, e a ligação ao bruto faz-se pelo `ITEM_ID`
    (`derived:busca-<sha256>`).
  - Ligar ao `raw_asset` é o próximo passo, e declaro-o como **dívida**.

## 1 · As consultas (`ferramentas/linha_busca/consultas.py`)

- **As 473 consultas de setembro de 2026** estão em `data/derivados/LINHA-BUSCA/CONSULTAS.json`:
  - **CASCO:** 11 pares cultura × problema. Todos vêm da matriz do dono (`motor/matriz_recorte.py`), menos um:
    frutta × cimice, que veio do BUSCA-LOTE-0 e está declarado. Cada par entra em 3 formas que o BUSCA-LOTE-0
    mostrou ser ouro: «bollettino fitosanitario …», «… catture trappole …», «… {região} {mês} bollettino». Cada
    uma vai às 20 regiões ou fica nacional.
  - **R3:** as 6 famílias nunca amostradas (T1, T4, T6, T8, T11, T12) viram consultas de família.
- **A ordem de gasto:** primeiro as **33 nacionais**, depois as 22 da R3, depois as 418 regionais.
- **Cada consulta leva:** a ferramenta do casco, o universo (T) em que a página vai à Admission, a origem e a
  janela.

## 2 · Os motores (`ferramentas/linha_busca/motores.py`)

| Motor | Rota | Precisa |
|---|---|---|
| `DDG_HTML` | html.duckduckgo.com, HTML sem JavaScript | robots vivo, a medir |
| `BING_HTML` | bing.com/search | robots vivo, a medir |
| `GOOGLE_HTML` | google.com/search | robots vivo, a medir |
| `GOOGLE_CSE` | API oficial Programmable Search | `SINTONIA_GOOGLE_CSE_KEY` + `_CX` (dono) |
| `BRAVE_API` | API oficial Brave Search | `SINTONIA_BRAVE_KEY` (dono) |
| `IMPORTADO:*` | busca feita por fora (ex.: Hermes), entregue em JSON | a rota fica declarada no RAW |

Os leitores de resultados foram testados em **páginas de resultados SINTÉTICAS**, marcadas no nome, feitas pela
forma pública conhecida. A 1.ª corrida com rede guarda as páginas reais em `serp/` (sha256), e essas passam a ser
as fixtures.

## 3 · Os comandos (o coordenador; VPN IT; uma linha de rede de cada vez, D90.2)

```bash
B=<clone de origin/linha-busca-v1>        # ou instalar o ramo no vivo
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
S=C:/Users/London1/sintonia-sala-italia/linha-busca
cd $B
# 0 · sem rede: o plano
py coleta/linha_busca.py --plano --r3=C:/Users/London1/sintonia-sala-italia/intelligence-experimental/EXPD78-R3-20260927T010557Z/LACUNAS-PARA-A-COLETA-R3.json --saida=$S
# 1 · MEDIR os motores (portao IT antes/depois; 1 consulta por motor; robots vivo decide)
py coleta/linha_busca.py --medir-motores --autorizado --saida=$S/MOTORES
# 2 · A MEDIDA PEDIDA: as 13 paginas do BUSCA-LOTE-0 pela linha (sem busca: os resultados ja vieram do Hermes).
#     Numa COPIA da fila primeiro (--fila=), para ler quantas a Admission deixa entrar e porque:
cp $V/candidatas/FONTES-CANDIDATAS.json $S/fila-copia.json
py coleta/linha_busca.py --colher --autorizado --resultados=ferramentas/linha_busca/fixtures/busca-lote-0/RESULTADOS.json \
   --fila=$S/fila-copia.json --livro=$V/curadoria/LIFECYCLE-LEDGER-V1.json --saida=$S/LOTE0-REAL
#     -> $S/LOTE0-REAL/LIVRO-LINHA-BUSCA.jsonl diz, por pagina: estado da fonte, portao, Admission (regra + motivo)
# 3 · buscar (motor que o passo 1 provou) e colher; --pousar leva os admitidos a Sala canonica (D93)
py coleta/linha_busca.py --buscar --autorizado --motor=<MOTOR> --consultas=$S/CONSULTAS.json --n=4 --saida=$S/B1
py coleta/linha_busca.py --colher --autorizado --resultados=$S/B1/RESULTADOS.json --fila=$V/candidatas/FONTES-CANDIDATAS.json \
   --saida=$S/B1 --pousar
# D93.4, sempre que o Curator recusar fontes:
py coleta/linha_busca.py --marcar --saida=$S/B1 --fila=$V/candidatas/FONTES-CANDIDATAS.json
```

- **Os limites estão no transporte canónico, não neste ficheiro:**
  - o robots é lido ao vivo (`scrap_http.permitido`, D91);
  - o teto de ≤5 por domínio é reservado **antes** de o pedido sair (`teto_da_onda`, livro `TETO-<dia>.json`,
    que dá para partilhar com as outras linhas);
  - os redirecionamentos também são vigiados.
- **O portão IT** é conferido antes e depois; se não for IT, o comando para.
- **`--pousar`:** só com a Sala **canónica** ativa (`exigir_canonica`); nunca cai para ficheiro.
- ⚠️ **`--fila` do vivo:** o robô de fontes escreve nessa fila ao mesmo tempo. É o mesmo cuidado de sempre: correr
  com o robô parado, ou numa cópia que depois se junta.

## 4 · Ensaio, testes, mutação

- **`--ensaio`**, com a fixture do BUSCA-LOTE-0 (`fixtures/busca-lote-0/`, feita por `fazer_fixture_lote0.py`):
  - as 13 URLs são reais;
  - as páginas são **SINTÉTICAS**: o texto é o resumo do coordenador;
  - a posição é a ordem da tabela, porque a posição real não foi guardada.
  - Resultado: 13 de 13 passam o portão; 13 de 13 ficam em quarentena na pergunta «matéria», por causa do HTML
    sintético.
  - A fila do vivo ficou igual (`FILA-VIVO-ANTES/DEPOIS.txt`).
- **`tests/test_linha_busca.py`: 18 testes, todos passam** (14 + os 4 da D94-b, §6). Cobrem:
  - o portão D93: proveniência incompleta, fonte recusada, e a regra da coleta recorrente sem mudança;
  - as consultas: nacional primeiro, sem repetir, famílias da R3;
  - os 3 leitores de resultados;
  - a colheita inteira sobre páginas de teste:
    - um boletim de vite é **ADMITIDO**, o `READY` cumpre o contrato da Sala (`_conferir_unidades`) e leva
      `SOURCE_ID = CAND-…`;
    - a capa do mesmo site é **recusada** pela regra de capa;
    - o robots recusa, o teto recusa, e a fonte já recusada não entra;
    - o RAW leva a proveniência inteira, e a candidata entra pela porta;
  - o `--marcar` só acrescenta e não repete;
  - sem `--autorizado`, nada sai à rede.
- **`curadoria/test_collection_gate.py`:** 22 de 23 passam. A que falha é de **base**. Ela lista 4 ficheiros que
  não são desta missão: `nome_da_pasta.mjs`, `teto_da_onda.py`, `onda_web.py` e `buscar_indices_d40.py`.
- **Mutação:** 16 de 16 (§5 e §6).

## 5 · Mutação

**12 de 12** estragos feitos de propósito foram pegos. A corrida foi numa worktree destacada
(`ferramentas/linha_busca/mutar.py.txt`), com a **guarda de rede** no módulo de testes: nenhum mutante saiu à rede.
Os mutantes foram:

- o portão aceita sem proveniência, ou aceita fonte recusada;
- a página é colhida com o portão a recusar;
- vira `READY` sem passar a Admission;
- o RAW fica sem proveniência;
- a mesma fonte vira duas candidatas;
- o `--marcar` apaga o livro;
- sai à rede sem `--autorizado`;
- as consultas regionais vão primeiro;
- o DuckDuckGo não desembrulha o link;
- passa um resultado do próprio motor;
- usa-se o livro de outra árvore por omissão.

## 6 · As regras da D94-b (coordenação 08:58), já no código

| Regra | O que a linha faz | Teste |
|---|---|---|
| Snippet é só descoberta | nunca se guarda o resumo do motor: abre-se a página e guarda-se o RAW (sha256 + proveniência) | `test_o_raw_leva_a_proveniencia_inteira` |
| NAME ≠ PROFILE ≠ PERSON | um **perfil** social achado por busca (`linkedin.com/in/…`, `x.com/<conta>`, `instagram.com/<conta>`) **não é item** e **não vira candidata**. Vai para `PISTAS-DE-CONTA.jsonl`, e só vira candidata com prova: nome + instituição + tema, ou a página oficial a apontar para a conta. A **plataforma** (linkedin.com, x.com…) nunca vira candidata | `test_perfil_nao_e_item_e_nao_vira_candidata` |
| LinkedIn só por post público (medido 08:40) | `linkedin.com/posts/…`, `/feed/update/…`, `x.com/<conta>/status/…`, reels, vídeos: vão para `POSTS-PARA-O-SCRAP.jsonl` com a proveniência. Quem os colhe é o **Scrap**, a porta social canónica, e não esta linha | `test_post_de_linkedin_vai_para_o_scrap` |
| Contar só item único, admitido, com identidade | a saída traz `ITENS_UNICOS_ADMITIDOS`, contados por `ITEM_ID`. O mesmo endereço achado por outra consulta **não é pedido outra vez** (`DUPLICADO_NA_CORRIDA`). Um muro de login/cadastro **não se guarda nem se conta** (`PAGINA_DE_LOGIN`) | `test_so_conta_itens_unicos` · `test_muro_de_login_nao_se_guarda_nem_conta` |

⚠️ A D94-b pede «RAW provado». Nesta v1, o RAW é o ficheiro com sha256 mais a proveniência na pasta da linha, e
**ainda não** a linha em `raw_asset`: é a dívida da §«O que falta». O item de busca na Sala fica com
`RAW_OBSERVATION_ID = NAO SEI`, e a ligação faz-se pelo `ITEM_ID` (`derived:busca-<sha256>`).

**Testes:** 18, todos passam. **Mutação:** 16 de 16. Os 4 mutantes novos: o perfil vira página comum, o post é
colhido como página, o muro de login entra, e o mesmo endereço é pedido duas vezes.

## 7 · A dívida fechada: RAW canónico antes da Sala (coordenação 11:20)

**O que o coordenador mediu com rede:**

- lote 0: **8 de 13** admitidas;
- lote 1: **30** admitidas (20 buscas do Hermes, 91 URLs, 72 domínios).

Mas o `pousar` falhou com `sala_de_espera_run_id_fkey`: a corrida da linha nunca tinha nascido em `collection_run`.
A transação desfez-se, e a Sala ficou em 204.

**O conserto passa pela porta do dono do RAW.** Está em `coleta/linha_busca_raw.py`:

1. **Lê as páginas ADMITIDAS** das pastas da linha (`LIVRO-LINHA-BUSCA.jsonl` + `RAW-LINHA-BUSCA.jsonl`), uma
   por sha256, e **confere os bytes**: o que não bate não entra. Não há pedido novo à rede.
2. **Preserva pelo dono do RAW**, `guarda/preservar_coleta.preservar()`, numa **corrida própria**:
   - a `collection_run` leva `ACTOR = coleta/linha_busca.py`, `PLATFORM = HTTP direto` e a missão com as
     corridas e o motor de origem;
   - cada página vira uma linha em `storage_object` + `raw_asset`, com o `SOURCE_ID` da candidata e o
     `CAPTURED_AT` da colheita original;
   - o `DOCUMENT_ID` **não se inventa**: fica `FORWARD_IDENTITY_UNPROVEN`, que é a verdade.
   - A memória vem de `orquestrador/persistencia.dependencias_do_runtime()`: `SINTONIA_COLLECTION_DSN` no modo
     operacional, ou `BANCO_DESCARTAVEL_URL` no ensaio. Sem memória, **recusa**; nunca cai para ficheiro.
3. **Refaz o READY** pela Admission normal, agora com o **`RAW_OBSERVATION_ID` real** que o banco devolveu.
4. **Só com `--pousar`:** chama `exigir_canonica()` e `pousar(<a mesma corrida>, prontos)`.
   - A chave estrangeira fica satisfeita por construção: a corrida acabou de nascer.
   - Uma página sem observação confirmada **não é pousada** (`SEM_RAW_CANONICO`).

**`colher --pousar`** passou a usar o mesmo caminho, sobre a pasta da própria corrida.

**Ensaio sem banco sobre os 38 reais:** 38 de 38 lidas, com os bytes conferidos, e **38 de 38** refeitas `PRONTO`
pela Admission de hoje, com o vivo `2ef6fef8`.

**Testes:** 22, todos passam. Os 4 novos:

- sem memória recusa;
- preserva e pousa com o id real na **mesma** corrida, e o `READY` cumpre o contrato da Sala;
- sem observação confirmada não pousa;
- byte adulterado não entra.

**Mutação: 21 de 21.** Os 5 mutantes novos: pousa sem `RAW_OBSERVATION_ID`, pousa noutra corrida, byte
adulterado entra, sem memória não recusa, identidade documental inventada.
