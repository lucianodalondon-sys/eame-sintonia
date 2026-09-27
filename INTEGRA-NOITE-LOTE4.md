# INTEGRA-NOITE · LOTE 4 — sobre o vivo `2ef6fef8` (lote 3 + DATA-DO-FATO)

Ramo **`integra-noite-v4b`**: montado sobre o vivo `554c1ec1` (`integra-noite-v4`), verificado pela nuvem
(`claude/lote4-verificar-ekdj83` @ `f170f383`, `LOTE4-VERIFICAR.md`: bateria inteira + mapa), avançado para `f170f383`
(ff), os 4 consertos da DA-21, junto com o vivo **`2ef6fef8`** (DATA-DO-FATO). **ff-only sobre `2ef6fef8`: SIM.**
**NÃO instalado.** O `-v4b` nasce de `d8839907` (antes dos 2 opcionais, §1) — sem `git revert`, para os pacotes
poderem entrar num lote futuro com as suas mudanças (um revert de junção esconde-as da junção seguinte).

## 1 · Os pacotes

| # | pacote | SHA | junção |
|---|---|---|---|
| 1 | contador-24h-v1 | 4552a305 | limpa |
| 2 | scrap-evolucao-v1 | 3103f723 | limpa · **peça 6 DESLIGADA**: `coleta/scrap_capacidades.EMENDAS_EM_VIGOR = frozenset()` (só liga com `COL-LAW-220` lá dentro) |
| 3 | lista-mestra-v1 | 3f7b43ef | limpa · traz **t6-para-sala-v1** `ff9ba9f2` dentro (achado da nuvem) — **FICA** (DA-21 1) |
| 4 | pesq-fora-do-mur-v1 | 389f9879 | ficha do mapa: + `C-SEGUIR-PESQUISADORES` (0 dúvidas) |
| 5 | nuvem-polso-mercato-v1 | 89020be4 | só gerados |
| 6 | nuvem-voci-campo-v1 | 7c975a9c | limpa |
| 7 | nuvem-concorrenza-v1 | 778c21ff | limpa |
| 8 | nuvem-independencia-v1 | eb3a7b1d | só gerados |
| — | intelligence-bridge-v2 (pote único v2) | ce775ff5 | **FORA — falha SOZINHO nesta máquina (Windows)**: `tests/test_pote_intelligence_casco.py::test_L1_o_casco_desenha_o_pote_com_precedencia_e_sem_regra_de_cruzamento` — a conferência `P6 sintonia-pote.js esta no .gitignore do cliente e no .vercelignore` reprova (medido no `ce775ff5` puro, numa worktree). Juntava limpo (ficha 0 dúvidas); foi medido na bateria inteira e tirado. Para o dono |
| — | concurrency-meta-collection (Meta Ads recorrente) | d447a47f | **FORA — falha SOZINHO nesta máquina (Windows)**: `tests/test_concorrencia_meta.py` 2 — `test_snapshot_datado_e_raw_com_sha` (o sha256 do ficheiro lido ≠ o do recibo: provável fim de linha) e `test_o_envelope_cumpre_a_col_law_505` (o caminho não acaba em `os.path.join('RUN-T','ENVELOPE.json')`: separador). Medido no `d447a47f` puro. Juntava com a lista de `test_italia_na_porta_canonica` unida (22/22). Para o dono |
| — | micro-prova-lote2b-v1 | 005a24cd | **FORA**: conflito de CÓDIGO com o scrap-evolucao (§4) — a DA-21 não decidiu |
| — | lei-pesquisadores-v1 | 94524616 | **FORA**: conflito de CÓDIGO com o scrap-evolucao (§4) — a DA-21 não decidiu |
| — | nuvem-rotulos-t4-v1 · nuvem-int-casco-ponte-v1 | — | FORA: sem PRONTO |

Migrações: **nenhuma**. A ficha do mapa junta-se por `ficha_juntar.py` (fora do Git): só com **0 dúvidas** (só
acréscimos do pacote sobre a base comum); remoção, peça apagada ou campo em conflito PARAM a junção.

## 2 · Os 4 consertos da DA-21 (coordenação 27/09 ~10:50)

1. **t6-para-sala FICA** (entrou pelo lista-mestra).
2. **ORCID → T6 volta, sem perder o conserto do concorrenza** (`3115bfcd`). `curadoria/atribuir_source_id.py`: a
   regra ORCID sai de `_ENTIDADE` para `_IDENTIDADE_NO_ENDERECO`, lida no endereço INTEIRO e antes das outras (a
   mesma precedência que tinha no topo). O iD ORCID é a IDENTIDADE da fonte, não o assunto de uma página; todas as
   outras regras continuam só com nome + casa (IT-T9-021, a Didacta). `test_pesquisadores_t6` +
   `test_comunicacao_concorrenza` + `test_receita_web_t8_t9_t12`: 65 OK.
3. **O runtime não importa `provas/`** (`a6c7dfca`). A regra do domínio registável (TETO_D38, sufixos,
   `MESMO_ORCAMENTO`, `host_limpo`, `dominio_registavel`, `orcamento_de`) **mudou-se tal e qual** para
   `coleta/dominio_registavel.py` (peça C-CONTADOR-24H); `coleta/rota_navegador.py`, `coleta/espera_por_dominio.py`
   e `coleta/reserva_24h.py` importam-na daí; `provas/prova_teto_dominio.py` importa-a daí com os mesmos nomes
   (rodadas, maestro, captura_xhr e testes não mudam). `test_1_nenhum_modulo_de_runtime_importa_provas` passa;
   158 testes OK. A mutação do lote 1 (M14/M17, a D41) passou a atacar o dono novo.
4. **`provas/contador_24h_local.mjs` sem `py` fixo** (`1bdca628`): `SINTONIA_PY`, senão `py` no Windows e `python3`
   fora — a regra que `provas/corrida_abortada_local.mjs` já usava. Só a prova. `test_contador_24h` 17/17 (Windows).

**Mutação** (`provas/integra_noite/mutacao_da21.py` → `mutacao-da21-RESULTADO.txt`): **4/4 mortos** — O1 a regra
ORCID desligada · O2 a regra ORCID lê só nome + casa · O3 todas as regras voltam a ler o endereço inteiro (o conserto
do concorrenza desfeito) · D1 o runtime volta a importar `provas/`. O conserto 4 não tem mutante que morra no
Windows (lá `py` existe): a nuvem mediu o antes (`spawn py ENOENT` em Linux); no Linux, depois, **NÃO SEI** (não
corri lá).
**Mutações antigas que tocam a regra movida:** `provas/_mutantes_prova_teto_social.py` — 15 mortos, M14/M17 no dono
novo; ⚠️ **M9 e M13 «NAO_APLICOU»** — o texto que atacam em `coleta/scrap_colheita.py` já não existe **no vivo
`554c1ec1` nem no `2ef6fef8`** (medido): herdado do lote 3 (o freio-social mudou o ficheiro), não desta integração;
é dívida do dono da prova-teto-social. `provas/contador_24h_mutacao.py`: **10/10**.

## 3 · Testes por NOME — a BATERIA INTEIRA (o método da nuvem), ramo × vivo `2ef6fef8`

`C:/cur/t2b/bateria_inteira.py` (fora do Git): **todo** ficheiro de teste rastreado (`test_*.py`, `*_test.py`,
`provas/testa_*.py`, `*_test.mjs`, `system-map/tests/*.mjs`), cada um corrido da raiz de uma **worktree** com o
nome do vivo, rede fechada, e **sem nenhuma variável `SINTONIA_*`/`BANCO_*`/`PG*`** (nada aponta para a Sala, o
armazém ou um banco reais; a suíte apaga `<raiz>/XX` — cai na worktree). Falha pelo nome; sem nomes, pelo código
de saída. Sob a LOCK-PESADO (12:42, prioridade da coordenação).

**1.ª corrida, com os 10 pacotes** (`provas/integra_noite/lote4-inteira-{ramo,vivo}-v1.json`): ramo `1c7b154f`
393 ficheiros · vivo 374; **152 herdadas**, iguais nome a nome; **5 novas** —
- 2 + 1 = os 2 opcionais, que **falham sozinhos** nesta máquina (§1) → **tirados** (`-v4b`);
- `test_o_controle_separa_lei_de_mencao::test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore` — o mapa
  ainda por regerar (a mesma da nuvem); confere-se depois do mapa (§7);
- `test_fundacao_da_coleta::test_nenhum_ficheiro_de_inteligencia_foi_tocado` — **⛔ decisão, §4.3**.

**Corrida final** (o `-v4b` com o mapa): §7.

## 4 · Decisões abertas

**4.1 · micro-prova-lote2b × scrap-evolucao** — `curadoria/colher_prova_territorio.py` (3 blocos). Proposta (não
aplicada, `C:/cur/t2b/proposta-colher_prova_territorio.py`, sha256 `5db89ce5…`): ficam os dois (rota de navegador na
prova + `REJEITADAS`); medido nela: `test_colher_prova_territorio` 28/28, `test_scrap_evolucao` 36/37 — as páginas
FALSAS do teste do scrap-evolucao (17–24 bytes) não passam o juízo dos bytes do micro-prova; proposta 2: dar-lhes
conteúdo publicado.
**4.2 · lei-pesquisadores × scrap-evolucao** — `coleta/scrap_http.py`, só o comentário do topo: `COL-LAW-704` (na
Bíblia) ou `COL-LAW-220` («proposta à espera do dono»). Juntá-la não liga a peça 6.

**4.3 · ⛔ «A INTELIGÊNCIA ESTÁ CONGELADA» × nuvem-independencia (pacote OBRIGATÓRIO).**
`tests/test_fundacao_da_coleta.py::ODiffDestaMissaoNaoTocouInteligencia` mede o diff de
`origin/claude/italia-biblia-integracao-v1` (a Bíblia, 08/09) até **HEAD** e reprova se algum caminho de
inteligência (`oportunidade`, `signals`, `scoring`, …) foi tocado. O `nuvem-independencia-v1` muda **de propósito**
`motor/v21_oportunidades.py` (+39/−1: o grafo de dependência, INT-LAW-070..077 — é trabalho de Intelligence
encomendado). Medido: no vivo `2ef6fef8` esta classe já tem 1 falha HERDADA (`test_o_portal_nao_ganhou_implementacao`,
os cascos do lote 2); o independencia acrescenta `test_nenhum_ficheiro_de_inteligencia_foi_tocado`. **Não mexi no
teste nem no pacote.** Opções: (a) aceitar — a lei do congelamento já não descreve o estado da casa (a
Intelligence está a ser construída: INT-CONSERTOS, DATA-DO-FATO); a falha fica declarada como consequência da lei, e
a lei é do dono rever; (b) a guarda passa a medir só o diff da missão FUNDAÇÃO (base → o commit dela), como o nome
da classe diz; (c) o independencia sai do lote. **Recomendo (a)** e rever a lei.

## 5 · O `py` sem `yt_dlp`/`faster_whisper` (achado da coordenação 26/09 22:45)

Nas baterias não escondeu nada (os testes que citam `yt_dlp` usam um falso: 37/37 com e sem `PYTHONPATH`) — e por
isso também não provam que a biblioteca real existe. **Todo comando de vídeo/transcrição** do plano leva
`export PYTHONPATH=C:/Users/London1/AppData/Local/Programs/Python/Python312/Lib/site-packages` e
`SINTONIA_ASR_DEVICE=GPU`, e confere antes: `py -c "import yt_dlp, faster_whisper"`.

## 6 · Plano único de instalação (o coordenador instala; um escritor; sem rede)

**A · Código (tudo de uma vez, ff-only, robô PARADO):**
1. `curadoria/PARAR.flag`; esperar a volta acabar. Guardar `git rev-parse HEAD` (= `2ef6fef8`), `git status` e
   `sha256sum` dos livros `M` — contar na hora.
2. `git merge --ff-only <SHA do PRONTO>`.
3. Os livros: `git status` e sha256 IGUAIS ao passo 1 (medido no PRONTO, §7).
4. `correr_a_cadeia.py VALIDAR` (o P1 acusa os livros `M`: aceitar SÓ se a lista for exatamente essa) e
   `PORTOES_POS_COMMIT` → IGUAL. Repor os gerados que o validador reescreve pelo nome.
5. **Sem migrações.** Não correr `motor/cadeia_canonica.sh migrations`.
6. Provas rápidas sem rede: `py -m unittest tests.test_a_porta_cli_liga_o_banco.ORuntimeNaoImportaProvasEHaUmAdaptador
   tests.test_pesquisadores_t6 tests.test_comunicacao_concorrenza tests.test_contador_24h tests.test_scrap_evolucao
   tests.test_italia_na_porta_canonica tests.test_prova_teto_dominio tests.test_rodadas`.
7. Reiniciar o supervisor (mudam `coleta/` e `curadoria/atribuir_source_id.py`); tirar o `PARAR.flag`.

**O que muda sozinho depois de A:** a regra do território volta a dar T6 a um registo ORCID e continua a não ler o
caminho para o resto; o teto por domínio (transporte, rodadas, reserva de 24 h, rota de navegador) lê a regra do
seu dono novo — o mesmo cálculo; a peça 6 continua DESLIGADA.

**B · O que escreve (robô parado; cada passo é decisão do coordenador):** os roteiros de cada pacote
(`CONTADOR-24H`, `SCRAP-EVOLUCAO.md`, `LISTA-MESTRA`, `T6-PARA-SALA.md` — o ensaio já foi aplicado na Sala real às
08:21 —, `CONCORRENCIA-META.md`, `POTE-UNICO.md`). Nenhum passo B corre sozinho com a instalação. Comandos de
vídeo/transcrição: §5.

**Desfazer (código):** `PARAR.flag`; guardar `git status`/`git diff`; `git reset --keep 2ef6fef8`; reiniciar o
supervisor.

## 7 · Mapa e conferências

(por correr, sob a LOCK-PESADO)
