# REROUTE-T1T2 — o reroute entra na Sala só por clima e cultura; a régua T5 exige assunto agro (desligada)

Ramo `claude/reroute-t1t2-rule-t5-v45dba`, base `e24139702` (= `origin/servico-20260923-0923`), 28/09/2026.
Offline: sem rede, sem a Sala real, sem livro vivo escrito. **Nada foi instalado.**

> **D130 (dono real, 28/09 ~12:10), verbatim** — reroute: «Ligar só clima e cultura, como a regra atual
> (ganho hoje: 0, risco: 0)»; ENEA: «Sim, suspender os 2 endereços da ENEA» (feito pelo coordenador em
> `RODADAS-PLANO.json`, não aqui).

```
REROUTE NA SALA                 SÓ T1 e T2 (REROUTE_NA_SALA_D130) · T3/T10 anotam no livro com trecho
RÉGUA T5 C1                     escrita e testada · DESLIGADA (REGUA_T5_EXIGE_AGRO = False) até o dono ver o replay
REPLAY T5 (22 de 28/09)         os 9 NÃO-AGRO saem em todas as leituras · 0 NÃO-AGRO fica
                                ÚTEIS: ficam 3 de 5 (texto inteiro) · 0 de 5 (corpo estrito: CREA sem corpo)
REPLAY T5 (158 de antes)        saem 48 (texto inteiro) / 57 (corpo estrito) · LIDOS: 7 / 16 ÚTEIS perdidos
CORPO()=0 NO CREA               causa: o texto chega numa linha só (coleta/texto_fonte.py:69) — proposta, não consertado
TESTES                          test_reroute_t1t2_d130 14/14 · test_reroute_d56 22/22 (5 contra Postgres 16 descartável)
MUTAÇÃO                         D130+T5: 16/16 mortos · D56 sobre o código fundido: 20/20 (1.ª volta 19/20 → teste apertado)
BATERIA POR NOME                base e24139702: 332 módulos · 7.485 testes · 132 falhas → depois fa8e7c5: 334 · 7.521 · 132
                                NOVAS 0 · SUMIDAS 0 (comparado pelo NOME)
SYSTEM MAP                      REGERAR + VALIDAR → SYSTEM_MAP_CHECK=PASS · --conferir-carimbo = IGUAL
```

---

## 1 · O reroute por cima de `e24139702`, com o escopo da D130

**Merge** de `origin/nuvem/reroute-fecho-v1` (`ebde8b876`, base `a2aa73f42`) sobre `5b6505e` (e24139702 + os
insumos do coordenador). Commit de merge com dois pais — nenhum histórico reescrito. Conflitos: **só** nos
ficheiros gerados do mapa (`system-map/data/*.generated.json`, `state.generated.json` do cliente e
`docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md`). Regra escrita: fica a versão da base e regenera-se pela
cadeia no fim. Código: nenhum ficheiro de código era tocado dos dois lados (medido com `comm` sobre as duas
listas de `git diff --name-only`); `architecture.declared.json` fundiu sozinho.

**O ramo violava a D127/D130** (LAB F7): `REROUTE_ENTRA_NA_SALA = True` com `REROUTE_PROMOVE = {T1,T2,T3,T10}`.
Agora:

| o quê | onde |
|---|---|
| `REROUTE_NA_SALA_D130 = frozenset({"T1", "T2"})` — o escopo do dono, à vista, com a D130 verbatim | `admissao/admissao.py:1742` |
| `REROUTE_ENTRA_NA_SALA = True` fica (a D130 diz «ligar»); `REROUTE_PROMOVE` fica como «régua medida» | `admissao/admissao.py:1741`, `:1765` |
| `julgar_reroute`: régua medida + SIM no corpo + trecho, mas fora do escopo → **NAO_SEI** `REROUTE_FORA_DO_ESCOPO_D130`, com `sim_da_regua`, `fora_do_escopo_d130` e os **trechos** na evidência — vai para o livro, não entra, não é rejeitado | `admissao/admissao.py:1917-1927` |
| segunda trava: `_reroute_entra(d)` — `principal()` e `gavetas_para_a_sala()` só aceitam SIM de reroute **dentro** do escopo, venha a SIM de onde vier | `admissao/admissao.py:1965`, `:1973`, `:1988` |
| o reprocesso da Sala existente só dá gavetas T1/T2; o plano diz o escopo | `admissao/reprocessar_reroute.py:100`, `:115` |
| o recibo de `pela_porta` diz `NA_SALA_D130` | `orquestrador/orquestrador.py:846` |

**O PEDIDO não muda.** `decidir()` continua igual; um pedido T3 que dá SIM continua a ser a linha T3. A D130
só limita o que entra **por reroute**.

**Testes que prendem isto** (`tests/test_reroute_t1t2_d130.py`, 14): o escopo é exactamente `{T1, T2}`; T3 e
T10 anotam com regra, motivo e trecho e não chegam à Sala; uma SIM de T3/T10 **fabricada** não passa
`principal()`/`gavetas_para_a_sala()`; `pela_porta` (backend FICHEIRO) com documentos só-T3 e só-T10 dá
0 READY e o livro com as duas anotações; o reprocesso seco só planeia T1/T2. Mutantes D01–D09 (T3 ou T10 no
escopo, escopo = régua medida, a trava tirada, anotar vira NAO, anotação sem trecho, reprocesso e estrada a
pousar o anotado) — **todos mortos**.

**Ajustes DECLARADOS em `tests/test_reroute_d56.py`** (citando a D130): as expectativas «T3 entra por
reroute» passaram a «T3 anota»; a fixture `BOLETIM` ganhou a frase «Le viti sono in piena fioritura» para
continuar a provar «um item, **duas** gavetas» **dentro** do escopo (T1 + T2); `test_o_menu_nao_conta`
abre T3 no escopo **só dentro do teste** (a prova é do menu, não do escopo); o `test_4` do reprocesso passou
a usar uma gaveta NOVA para a origem errada — a primeira versão do meu ajuste deixou o mutante M15
sobreviver (a gaveta «já estava» escondia a origem errada), e foi a mutação que o mostrou.

## 2 · A régua T5 (proposta C1 do LAB) — escrita, testada, DESLIGADA

`admissao/admissao.py:1537-1612` · chave `REGUA_T5_EXIGE_AGRO = False` (`:1566`) · ligada em `decidir()`
só para o universo T5 (`:1651`).

Com a chave ligada, **só o PEDIDO T5** muda:
1. as palavras T5 casam no **início de palavra** (o mesmo aperto do reroute): `tesi` deixa de casar
   «at**tesi**», `revista` deixa de casar «p**revista**»; a raiz continua a valer à direita;
2. além dos 2 sinais de ciência, **≥ 1 termo de cultura** (lista de T1, palavra inteira) **ou de praga**
   (lista de T3, início de palavra) no **corpo** (página HTML → `leis/fato_do_texto.corpo()`; PDF/texto →
   o texto inteiro, que não tem menu);
3. sem termo agro → **NAO_SEI** `T5_SEM_ASSUNTO_AGRO` (nunca NAO: ausência não vira negativo);
4. página HTML sem corpo separável → **NAO_SEI** `T5_CORPO_NAO_SEPARAVEL`.
As outras réguas e a prova «fala de outro universo» não mudam (teste `test_ligada_so_muda_o_t5`).

### Replay offline (`provas/reroute_t1t2/replay_t5_c1.py` → `REPLAY-T5-C1.json`)

O export da Sala **não traz** `media_type` nem retrato do detector. Em vez de adivinhar quem é HTML, o replay
mede três leituras: **CORPO_ESTRITO** (a porta numa página HTML), **CORPO_SENAO_INTEIRO** (se o extrator
separasse o corpo) e **TEXTO_INTEIRO** (a porta num PDF; a leitura do LAB).

**Os 22 T5 de 28/09** (rótulos do LAB, de modelo):

| leitura | NÃO-AGRO (9) | DISCUTÍVEL (8) | ÚTIL (5) |
|---|---|---|---|
| TEXTO_INTEIRO | **0 fica** · 9 saem | 3 ficam · 5 saem | **3 ficam** (1142, 1148, 1152) · **2 saem** (1145, 1149) |
| CORPO_SENAO_INTEIRO | 0 fica · 9 saem | 3 · 5 | 3 · 2 |
| CORPO_ESTRITO | 0 fica · 9 saem | 0 · 8 | **0 fica · 5 saem** (CREA sem corpo, §3) |

Por fonte: **ENEA 12/12 saem** nas três leituras. O critério do LAB («5 úteis de hoje ficam, ≥ 9 não-agro
saem») **não é cumprido**: saem os 9, mas ficam só 3 úteis (ou 0, na leitura estrita). Os 2 úteis que caem
em texto inteiro caem **pelo início de palavra**, não pelo agro: 1145 só tinha `revista` ⊂ «prevista» +
`ricerca`; 1149 só tinha `tesi` ⊂ «attesi» + `ricerca`. Ou seja: **entraram por acidente de substring**, e
a régua honesta deixa-os com um sinal só.

**Os 158 T5 de antes de 28/09** (180 linhas do export − 22; 176 itens únicos — 56, 57, 60, 62 aparecem 2×):
TEXTO_INTEIRO fica 110, sai **48**; CORPO_ESTRITO fica 101, sai **57**. EU-T5 (artigos) fica 95/100 em texto
inteiro (LAB mediu 98/100 **sem** início de palavra: os 3 a menos são «article» ⊂ «p**article**» e `doi`).

**A lista do que SAI foi lida** (`leitura_sai_t5_c1.py` → `LEITURA-SAI-T5-C1.json`, 57 linhas, rótulo do
agente — **HUMAN_REVIEW = NOT_DONE**):

| leitura | NÃO | DISCUTÍVEL | **ÚTIL perdido** |
|---|---|---|---|
| TEXTO_INTEIRO (sai 48) | 31 | 10 | **7** |
| CORPO_ESTRITO (sai 57) | 31 | 10 | **16** (+9 artigos EU numa linha só: corpo estrito cego) |

Os **7 úteis perdidos em texto inteiro**, e porquê:
- **INNOFLORENERG** ×3 (derived:58, 128, 1244 — floricultura, Sant'Anna): `T5_SEM_ASSUNTO_AGRO` — **flor não
  está na lista de culturas**;
- **Diabrotica × milho Bt** (EU, italiano): `T5_SEM_ASSUNTO_AGRO` — `mais` não está na lista italiana e
  `insetto` não casa «insetti» (lacuna da lista T3, que a régua do pedido já tinha);
- **Trichoderma na vinha**, **zeólito no tomateiro** ×2: caem pelo **início de palavra** (`doi` e
  `article` ⊂ «particle» eram o 2.º sinal por acidente).

Os 31 NÃO que saem são administração universitária, repositórios, ENEA (UV, America's Cup, DAPHNE),
cibermáfia, Lincei, Internet Festival — **o lixo que o LAB descreveu**.

### O canário `derived:1149` (Xylella, CREA)

- **Pedido T5, hoje (chave desligada):** SIM por `ricerca` + `tesi` ⊂ «at**tesi**» (reproduzido: `ANTES_PALAVRAS
  = [ricerca, tesi]`).
- **Pedido T5 com C1:** **NAO_SEI** — com início de palavra sobra só `ricerca` (um sinal). O assunto agro ele
  **tem**: cultura `vite, olivo, oliveti`; praga `malattia, insetto, patogeno` — mas nem chega a ser
  perguntado, porque falha o passo 1. Na leitura estrita também não teria corpo.
- **Reroute T1 (cultura, D130):** **NAO_SEI** também. Como página HTML: `CORPO_NAO_SEPARAVEL` (0 caracteres).
  Lido inteiro: `UM_SO_MOMENTO` — a cultura está (oliveira), mas T1 pede **dois** sinais de momento e só há
  «difesa integrata». Ou seja: **nem a regra nova nem o reroute T1 o admitiriam**; nenhum dos dois o tira da
  Sala (não há rejulgamento automático das linhas que já lá estão).
- Quem reprocessar o 1149 (`nuvem-canario-1149-v1`) precisa saber: rejulgado com C1, ele perde a pertença.

**Recomendação (o dono decide):** **não ligar C1 como está.** Tira todo o lixo medido, mas perde úteis reais,
por duas causas que se consertam antes: (a) a lista de culturas não tem flor/floricultura, milho em italiano
(`mais`), mel/apicultura; a de pragas não tem os plurais italianos (`insetti`); (b) a leitura estrita só é
justa depois de o extrator separar o corpo nos CREA (§3). A contenção das 2 rotas ENEA (D130, já aplicada) cobre
os 9 lixos medidos entretanto. Reverter a suspensão ENEA **só** quando C1 for ligada.

## 3 · Por que `corpo()` devolve 0 caracteres no CREA — só MEDIDO (`provas/reroute_t1t2/medir_corpo_vazio.py`)

**FATO MEDIDO** (export da Sala, `MEDIDA-CORPO-VAZIO.json`): **todos** os textos CREA do export
(IT-T5-056 3/3, IT-T5-111 6/6, IT-T5-113 3/3, IT-T5-167 2/2) são **uma linha só** — o 1149 tem 8.988
caracteres numa linha — e todos dão corpo < 200. As outras fontes IT têm várias linhas e corpo.

**A causa, arquivo:linha:**
1. `coleta/texto_fonte.py:69` — `limpar()` troca **toda** tag por espaço (`re.sub(r'<[^>]+>', ' ', t)`); as
   quebras de linha do texto só existem se existirem **no código-fonte HTML**. Página minificada (sem `\n`
   entre as tags) → o texto sai numa linha. (Medido com o mesmo HTML: minificado → 1 linha, corpo 0; com
   quebras → 5 linhas, corpo 356.)
2. `leis/fato_do_texto.py:194-216` — `corpo()` trabalha **linha a linha**. A linha única tem o rodapé dentro:
   `RODAPE` (`:77`) casa «Seguici», «Partita IVA», «C.F.», «PEC», «Via della Navicella 2», «00184 Roma»…
   → `:211` deita fora a **linha inteira**, isto é, a página inteira; `titulo()` também a recusa (`:189`) e o
   recurso `_linhas_curtas` (`:215`) filtra pelo mesmo RODAPE. Resultado: `""`.

**Proposta (NÃO aplicada — muda o extrator):** em `coleta/texto_fonte.limpar()`, antes de tirar as tags,
trocar os fins de bloco (`</p> </div> </li> </h1-6> <br> </tr> </section> </article> </header> </footer> </nav>
…`) por `\n`. Medido **só dentro do script**: o HTML minificado passa a dar 8 linhas e corpo 356 (igual ao HTML
com quebras). **Por que não aqui:** muda o texto de **todo** documento HTML → muda `producer_version`/hash dos
parâmetros → a D79 (versão do documento) passa a ver «extrator mudou» e a re-extrair; e mexe em tudo o que
lê texto (datas, lugares, réguas). É missão própria, com bateria e replay.

**NÃO SEI:** os bytes HTML do CREA não estão nesta árvore — «minificado» é **inferência do código** (a única
forma de `limpar()` dar uma linha), não medida nos bytes. A zootécnica (IT-T10-022, 4 dos 20 do LAB) não tem
texto no export T5: mesma causa por hipótese, não medida.

## 4 · Instalar (NÃO executado — quem instala é o coordenador) · fast-forward sobre `e24139702`

```bash
S=$HOME/sintonia-sala-italia; VIVA=<pasta viva>; FINAL=<SHA final deste relato>
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH" PGPASSFILE="$S/pgpass.conf"
DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"; B=/c/inst/$(date +%Y%m%d-%H%M)-reroute-t1t2; mkdir -p $B

# 0 · robô parado — e esperar o ciclo em curso acabar
echo "REROUTE-T1T2 a instalar" > $VIVA/curadoria/PARAR.flag
git -C $VIVA rev-parse HEAD                  # TEM de dar e24139702b8216ad54127cf63a14b550bcd4aeab; senão PARAR e perguntar

# 1 · backup PROVADO da Sala (PROVA_VALE=true) + foto dos livros sujos (como LOTE8-INTEGRA §7 passo 2)
py scripts/micro_coleta/provar_backup_da_sala.py --saida=$B
(cd $VIVA && git status --short | awk '{print $2}') > $B/lista      # livros vivos (curadoria/*-V1.json, ledger…)
#   copiar cada ficheiro para $B/livros/ e: (cd $B && find livros -type f | xargs sha256sum) > $B/foto.sha

# 2 · o ramo não toca livro vivo — TEM de sair vazio
git -C $VIVA fetch origin claude/reroute-t1t2-rule-t5-v45dba
git -C $VIVA diff --name-only HEAD $FINAL -- $(cat $B/lista)

# 3 · fast-forward (só --ff-only: recusa = parar)
git -C $VIVA merge --ff-only $FINAL

# 4 · LIVROS_IGUAIS — a foto do passo 1 contra o disco; algum MUDOU → DESFAZER
(cd $B && sed 's# livros/# '"$VIVA"'/#' foto.sha | sha256sum -c)

# 5 · migração 038 pela CADEIA (só cria a vista sala_de_espera_por_gaveta) — duas vezes
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up.txt     # 038 = PASS (as já aplicadas SKIP)
bash motor/cadeia_canonica.sh migrations "$DSN" | tee $B/up2.txt    # idempotente: 038 SKIP HASH=MATCH

# 6 · testes nomeados (rede fechada) — 0 falhas
py -m unittest tests.test_reroute_t1t2_d130 tests.test_reroute_d56 tests.test_migracao_033_sala \
   tests.test_sala_dedup_por_document_key tests.test_sala_idempotente_por_documento tests.test_medir_admission_t3_atual
py -c "import sys;sys.path[:0]=['.','admissao'];import _gavetas,admissao as a;print(sorted(a.REROUTE_NA_SALA_D130),a.REGUA_T5_EXIGE_AGRO)"
#    TEM de imprimir: ['T1', 'T2'] False

# 7 · mapa
py system-map/scripts/impressao_da_arvore.py --conferir-carimbo    # IGUAL
```

### 4b · Reprocessar a Sala que já existe — SÓ T1/T2 (seco → ler → aplicar)

```bash
export SINTONIA_SALA_BACKEND=POSTGRES SINTONIA_SALA_DSN="$DSN"
py admissao/reprocessar_reroute.py --exportar $B/copia.json                     # SÓ LÊ a Sala
py admissao/reprocessar_reroute.py --entrada $B/copia.json --saida $B/plano.json   # SECO (omissão)
#   LER o plano antes de aplicar:
#   · REROUTE_NA_SALA_D130 == ["T1","T2"]  e  GAVETAS_POR_UNIVERSO só com T1/T2 (outra chave = PARAR)
#   · DECISOES com REROUTE_FORA_DO_ESCOPO_D130 = o que só é anotado (T3, T10) — vai para o livro, não para a Sala
#   · DUPLICADOS_ANTES_DA_D56 ficam como estão (nada se apaga nem funde)
py admissao/reprocessar_reroute.py --aplicar $B/plano.json --backup $B/PROVA-BACKUP-SALA.json --recibo $B/recibo.json
py admissao/reprocessar_reroute.py --aplicar $B/plano.json --backup $B/PROVA-BACKUP-SALA.json   # 2.ª vez: INSERIDAS 0
#   o --aplicar RECUSA sem PROVA_VALE, sem PARAR.flag, ou com código diferente do seco

rm $VIVA/curadoria/PARAR.flag                                                  # religar o robô
```

**Desfazer:** `PARAR.flag`; `git -C $VIVA reset -q --keep e24139702`; conferir a foto (`sha256sum -c`);
vista: `psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/038_desfazer.sql "$DSN"`; gavetas
escritas pelo reprocesso: `pg_restore` do dump do passo 1. Só o código: `REROUTE_ENTRA_NA_SALA = False` (volta a
só anotar). **A régua T5 não precisa de desfazer: vai desligada.**

## 5 · Provas

- **Bateria por nome** (`provas/int_r7/bateria_por_nome.py`, rede fechada, 3 trabalhadores, Postgres 16
  descartável nas duas voltas, worktrees limpas, MESMA máquina): base `e24139702` **332** módulos · 7.485
  testes · **132** falhas; depois `fa8e7c5` **334** (+`test_reroute_d56`, +`test_reroute_t1t2_d130`) · 7.521 ·
  **132** — **NOVAS 0 · SUMIDAS 0**. `provas/reroute_t1t2/BATERIA-BASE-e241397.json`,
  `BATERIA-DEPOIS-fa8e7c5.json`, `COMPARAR-BATERIA.txt`. Nas duas voltas, neste contentor: `test_cliente_postgres`
  = TIMEOUT (a prova de processo fica à espera do Postgres), `test_migracao_033_sala.test_3_…` falha — as mesmas
  falhas pelo nome dos dois lados, logo do ambiente, não desta mudança. O commit a seguir a `fa8e7c5` só
  acrescenta este relatório, os JSON da bateria e o mapa regerado (nenhum código).
- **Mutação:** `provas/reroute_t1t2/mutar_reroute_t1t2.py` → `MUTACAO-REROUTE-T1T2.json` **16/16**;
  `provas/reroute_d56/mutar_reroute_d56.py` sobre o código fundido → `MUTACAO-REROUTE-D56-SOBRE-D130.json`
  **20/20** (1.ª volta 19/20: M15 sobreviveu ao meu ajuste do `test_4` — corrigido). O mutador da D56 ganhou
  duas mudanças DECLARADAS: o trecho de M01 (`_reroute_entra`) e `TESTE` com vários módulos.
- **Postgres descartável:** neste contentor `initdb`/`pg_ctl` recusam root; como na REROUTE-D56, um *shim* de
  ambiente em `~/orca/pgtmp/pgsql/bin` (fora do repositório) corre-os como o utilizador `postgres`.
- **System Map:** `correr_a_cadeia.py REGERAR` + `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
  `impressao_da_arvore.py --conferir-carimbo` → `IGUAL` (depois do commit). Peças: `C-ADMISSAO` (descrição
  + D130 e C1), `C-PROVA-COLETA` (+ `provas/reroute_t1t2/*`). Não recarimbei (`--stamp`).

## 6 · FATO · INFERÊNCIA · NÃO SEI

- **FATO:** escopo {T1,T2} no código e nos testes; C1 desligada; replay com os números acima; corpo 0 = linha
  única + RODAPE (medido nos 14 CREA do export e em HTML de teste).
- **INFERÊNCIA:** o HTML do CREA é minificado (do código de `limpar()`); ganho do reroute T1/T2 continua
  ~0 enquanto o fluxo não trouxer boletins (LAB N2).
- **NÃO SEI:** precisão humana (nenhum rótulo aqui é humano); o que a zootécnica tem; se a Intelligence já leu
  os não-agro (LAB N4); o efeito de C1 sobre T5 que chegue em PDF vs HTML no vivo (o export não diz o tipo).

## EM PALAVRAS SIMPLES

O reroute agora faz exactamente o que o senhor mandou: um documento só entra na Sala «por tabela» se for de
**clima ou cultura**. Se a régua achar que é de pragas ou de preço, isso fica **anotado no livro**, com a
frase que prova, mas não entra. Há um teste que reprova se alguém abrir pragas ou preço sem o senhor mandar.

A régua nova de ciência (exigir cultura ou praga no texto e não contar pedaço de palavra) está pronta e
**desligada**. No teste com o que já está na Sala ela tira **todo o lixo** medido (os 12 da ENEA, os repositórios
de universidade), mas também tira **coisa boa**: 2 dos 5 úteis de hoje (que só tinham entrado por acidente, como
a Xylella por «attesi») e 7 úteis antigos (floricultura, milho, vinha). Antes de ligar, falta ensinar à lista
«flor», «milho» em italiano e os plurais — e consertar a leitura das páginas do CREA, que chegam numa linha só e
por isso ficam sem «corpo». Isso último está medido e com a proposta escrita, mas não foi feito aqui.

A notícia da Xylella: pela régua nova ela não entraria pela ciência; pela cultura (oliveira) também não, porque
falta um segundo sinal de época. Ela continua na Sala — ninguém a tira de lá sozinho.
