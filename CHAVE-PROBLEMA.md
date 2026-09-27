# CHAVE-PROBLEMA — o PROBLEMA passa a ser chave da Collection (destrava CAP-WIN)

> Missão CHAVE-PROBLEMA (27/09), achado do LAB PESQUISA-CRUZAMENTOS F.2-4. Base: `claude/declare-problem-contract-lj7kfp`
> @ `c551062` (lote6 + porta única). Offline: **não toquei a Sala real nem nenhum livro vivo**.

## O que estava medido

`motor/cap_win.py` (l.387-392 na base) dizia: *«`PROBLEMA` NÃO EXISTE no contrato 033 … até a Collection o declarar
todo item real sai NOT_POSSIBLE»*. Medi e a frase estava **meio certa**: a porta **já** escrevia um bloco `PROBLEMA`
dentro da `janela_declarada` (boletins T2/T3 desde a D84; estudos T5 desde o ESTUDOS-CHAVES) — mas **fora de
contrato**:

| | na base | por que era perigoso |
|---|---|---|
| `VALOR` | **lista** de nomes | a CAP-WIN colava a lista com vírgulas num `ISSUE_ID` (`"margaronia,mosca dell'olivo"`) que ninguém escreveu |
| `VEIO_DE` | frase livre (`"item.texto: as secoes do boletim…"`) | não dizia *onde* o nome está escrito |
| `BASE` | a descrição da **regra** | não era o trecho; nada conferia que o nome estava no texto |
| código | nenhum | — |

## O que fiz

### 1 · O contrato `PROBLEMA/v1` — sem migração

Dono da **forma**: `leis/afirmacao_da_fonte.py` (o mesmo dono do vocabulário D112/COL-LAW-221), l.67-158.

```
VALOR     UM nome canónico (tabela versionada MESMO_PROBLEMA, D111) — ou «NAO SEI» com PORQUE
VEIO_DE   TEXT · SECTION_HEADER · DOCUMENT_TITLE   (onde o nome está ESCRITO)
BASE      o trecho LITERAL que contém o nome      (conferido contra o texto do item)
FORMA     o nome como a fonte o escreve           (tem de estar dentro da BASE)
CODIGO    EPPO só com o binómio latino ESCRITO e casado EXACTAMENTE com a tabela do repo
          (data/samples/ES-T4-001/eppo-dictionary.json via motor/normalize_agro.py); senão NOME_CANONICO.
CANDIDATOS / AUSENTES   todos os nomes que o item cita, com a base de cada um
```

**Duas pragas no item = NÃO SEI** (D112, «outra praga no meio»), com os candidatos à vista.
**Nome comum italiano nunca cunha EPPO** (normalize_agro: «esta árvore NÃO tem autoridade italiano→EPPO»).

**Por que não há migração e por que não quebra a 033:** a trava `janela_declara_as_quatro_chaves` só exige
`CULTURA/REGIAO_DO_FATO/FASE/JANELA` com `VALOR/VEIO_DE/BASE` — não proíbe uma quinta chave; a revisão já aceita o
campo `janela_declarada` (`revisao_so_de_campo_revisivel`); e a vista `sala_de_espera_atual` já devolve a última
revisão da janela inteira. As quatro chaves, o default e a trava ficam **byte a byte** iguais (a 033 não foi tocada).
Provado em teste (`tests/test_chave_problema.py::C4`) e num **Postgres descartável** (abaixo).

### 2 · Um produtor só (nenhum extrator novo)

- `leis/boletim_do_campo.py` l.631-771: `mencoes_do_boletim` (o **mesmo** vocabulário `PROBLEMAS`, a **mesma** regra de
  AUSENTE — extraída para `_estado_da_praga`, l.142, usada também por `ler_boletim` — e a **mesma** tabela
  `MESMO_PROBLEMA`) e `declarar_problema` (preenche o contrato a partir das menções já lidas). Para estudos T5, as
  menções são os `SPANS` de `leis/estudo_chaves.py`, tal como vieram.
- `admissao/admissao.py` l.2129-2166 (e l.2280, onde a `janela_declarada` o chama): `_problema_da_chave` / `problema_da_chave` — a porta escreve o contrato na
  `janela_declarada` (T2/T3/T5; outros universos: NÃO SEI com o porquê). A leitura antiga (`SECOES` por cultura, que
  `cruzamentos_max` lê) viaja ao lado.
- `admissao/reprocessar_problema.py` (novo): o reprocessador da Sala. Lê uma **cópia** exportada da vista, devolve a
  janela ATUAL com **só** a chave PROBLEMA trocada, **a seco**, idempotente (igual = não repete). `--aplicar` exige a
  Sala canónica, recusa revisões de outra versão do código, e escreve **só** por `sala_de_espera.rever` (INSERT).

### 3 · Quem lê, lê a chave — nunca o texto

- `motor/cap_win.py` l.392-432: `par_em_campo` lê `PROBLEMA` **só** por `AF.problema_da_chave` (a base é conferida
  contra o `TEXTO`; lista, bloco fora do contrato, base que o texto não tem ou NÃO SEI → `NOT_POSSIBLE`).
- `motor/motor_das_capacidades.py` l.667-676: o objeto do futuro lê o `ISSUE_ID` pelo mesmo leitor.

## Testes

`tests/test_chave_problema.py` — **35/35**: contrato (A1-A9), produtor (B1-B9), porta e 033 (C1-C4), leitor e
ponta-a-ponta (D1-D6), reprocesso (E1-E7).

**Ajustes de teste, declarados** (nenhuma asserção afrouxou; a decisão é esta missão — o PROBLEMA passou a ter contrato):

| ficheiro | o quê |
|---|---|
| `tests/test_cap_win.py` | `jd()` declara PROBLEMA no contrato; se o nome não está no texto do item, vai como 1.ª linha (DOCUMENT_TITLE). No corte ARIF×APOL o nome **já** estava escrito («Mosca delle olive») e a base é essa. |
| `tests/test_porta_unica_referencia.py` | o PROBLEMA do item de janela vem do **produtor real** sobre o próprio texto. |
| `tests/dados/int-r7/SINTETICO-R7-SALA-EXPORT.json` | PROBLEMA no contrato (base «Mosca delle olive»). O `ARIF-EVT` declarava *Bactrocera oleae* **sem o nome no texto** — praga inferida — e passou a NÃO SEI (nenhum teste dependia do valor). |
| `tests/test_boletim_do_campo.py` | a lista antiga lê-se em `CANDIDATOS`; Salerno cita **uma** praga não ausente → `VALOR = "mosca della frutta"`, e o contrato é conferido contra o texto. |
| `tests/test_estudo_chaves.py` | idem para estudos; `COM_PROBLEMA` conta o VALOR do contrato e o estudo com dois problemas conta em `PROBLEMA_SO_CANDIDATOS` (novo em `admissao/reprocessar_estudos_chaves.py`). |

## Mutação

`provas/chave_problema/mutacao_chave_problema.py` → `MUTACAO-CHAVE-PROBLEMA.json`: ****16/16 MORTOS** (re-corrida sobre o código final `053250b`)**.
Os quatro pedidos: praga do cabeçalho vira praga do trecho (M01), outra praga no meio (M02), sinónimo não unificado
(M03), inferência por semelhança — EPPO pelo nome mais parecido (M04) e forma parecida vira menção (M05). Mais: o
leitor aceitar bloco fora do contrato / base fora do texto / lista (M06-M08), CAP-WIN e motor a lerem sem contrato
(M09-M10), ausente vira valor (M11), título perde DOCUMENT_TITLE (M12), a porta volta ao formato antigo (M13), o
reprocesso apagar outras chaves / repetir / aplicar outra versão (M14-M16).

## Ensaio num Postgres DESCARTÁVEL

`provas/chave_problema/ensaio_033_descartavel.py` → `ENSAIO-033-CHAVE-PROBLEMA.json`: ****PASS** (PostgreSQL 16 descartável, `initdb` próprio, porta livre; versão `chave-problema@c868ea7549d052aa`)**.
34 migrações pela cadeia; `pousar` de um item com PROBLEMA dentro da janela (a 033 aceitou) e de um item ANTIGO
(`JANELA_NAO_MEDIDA`); cópia exportada pela vista → seco → `--aplicar` (1 inserida) → aplicar outra vez (0 inseridas);
pela vista, a CAP-WIN deixou de ter `JANELA_DECLARADA.PROBLEMA` na falta (continua a faltar CULTURA e REGIÃO nesse
item antigo — é a verdade da Sala); `sala_de_espera` com o mesmo md5 antes/depois; UPDATE e DELETE na revisão recusados.

## Bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `c551062` | 314 | 7030 | 131 |
| ramo (código `053250b`, árvore limpa) | 315 | 7065 | 132 |

- **Nova, pelo nome: 1** — `test_o_controle_separa_lei_de_mencao.test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore`:
  é o carimbo do mapa, que só fica IGUAL depois de a cadeia regerar (medido de propósito ANTES do REGERAR). Depois do
  REGERAR e do commit: ver «System Map» abaixo. **Sumidas: 0.**
- Módulo novo: `test_chave_problema` 35/35.
- Na 1.ª medição (árvore por commitar) caíam também `test_candidatos_tematicos.test_a_admissao_e_o_gate_nao_mudaram` e
  `test_gate_de_aceitacao_tematica.test_a_admission_nao_foi_tocada`: medem `git diff HEAD -- admissao/` (o próprio teste
  declara que guarda a SESSÃO, não o ficheiro). Com o código commitado passam — e passam na bateria `053250b`.
- Efeito colateral herdado (base e ramo): `test_atomicidade_da_intelligence` regrava
  `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`; reposto, não commitado.
- JSON: `provas/chave_problema/BATERIA-BASE-c551062.json`, `…/BATERIA-DEPOIS.json`.

## System Map

`REGERAR` pela cadeia e commit dos gerados · `VALIDAR` = **SYSTEM_MAP_CHECK=PASS** · `--conferir-carimbo` =
**IGUAL** (conferido depois do último commit; o SHA final vai no relatório da sessão — o commit não conhece o próprio
SHA). `VALIDAR` regera no lugar e só muda `PROVENANCE.HEAD`/`GENERATED_AT`: reposto, não commitado.
`test_system_map.py`: as mesmas 10 reprovações da base (a base mediu 11; a 11.ª, `scanner_e_deterministico`, foi
efeito do censo regravado na árvore-base); `a_coleta_nao_conversa_com_o_motor_as_centenas` passa. `test_M5` (o carimbo)
passa depois do REGERAR. Peças tocadas, frase reescrita à mão: `C-AFIRMACAO-DA-FONTE`,
`C-LUGAR-COLETA`, `C-ADMISSAO`, `C-INT-CAP-WIN`, `C-INT-MOTOR-CAPACIDADES`, `C-SALA-DE-ESPERA` (+
`admissao/reprocessar_problema.py`), `C-PROVA-COLETA` (+ `provas/chave_problema/*`, este relatório). Não usei
`--stamp`: as peças tocadas ficam 🟡 «mudou depois da declaração», que é a verdade.

## ▶ PARA O COORDENADOR: o comando no vivo

Git Bash, na máquina da Sala, a partir de uma cópia deste ramo **@ o SHA do fim deste relatório** (`$M`). Não precisa
de migração nem de parar o robô para o seco; para o `--aplicar`, o mesmo cuidado do `MIGRACAO-SALA.md` (LOCK-PESADO
livre, robô parado).

```bash
M=/c/Users/London1/orca/workspaces/eame-sintonia/<pasta com claude/declare-problem-contract-lj7kfp @ SHA>
S=$HOME/sintonia-sala-italia ; mkdir -p $S/chave-problema ; C=$S/chave-problema
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH"
export PGPASSFILE="$S/pgpass.conf"
export SINTONIA_SALA_DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
export SINTONIA_SALA_BACKEND=POSTGRES
export SINTONIA_PSQL_EXE="$HOME/orca/pgtmp/pgsql/bin/psql.exe"
```

**1 · exportar a CÓPIA (só leitura, pela vista).**
```bash
psql -X -A -t -v ON_ERROR_STOP=1 "$SINTONIA_SALA_DSN" -o $C/copia-sala.json -c "
select json_agg(json_build_object('run_id', run_id, 'ordem', ordem, 'item_id', item_id, 'universo', universo,
       'texto', texto, 'janela_declarada', janela_declarada) order by run_id, ordem)
  from public.sala_de_espera_atual"
sha256sum $C/copia-sala.json
```

**2 · SECO (não abre banco).**
```bash
cd $M && py admissao/reprocessar_problema.py --entrada $C/copia-sala.json --seco --saida $C/revisoes.json
```
Ler a `CONTA`: `COM_PROBLEMA` (saem de NÃO SEI), `SO_CANDIDATOS` (duas pragas: continuam NÃO SEI), `SO_AUSENTES`,
`SEM_LEITOR_NO_UNIVERSO`, `POR_VEIO_DE`, `COM_EPPO`, `REVISOES`, `ERROS` (tem de ser 0). Abrir 5 itens de
`revisoes.json` à mão e conferir que a `BASE` está no texto. Qualquer surpresa → **PARAR**.

**3 · backup.** `cmd //c "$(cygpath -w $S/backup_sala.cmd)"` → `BACKUP=PASS`; anotar o caminho e o `sha256sum`.
(Só `sala_de_espera_revisao` muda, e só por INSERT; o backup é para poder provar isso.)

**4 · fotografia antes.**
```bash
psql -X -A -t "$SINTONIA_SALA_DSN" -c "select count(*), md5(string_agg(t::text,'|' order by run_id, ordem)) from sala_de_espera t"
psql -X -A -t "$SINTONIA_SALA_DSN" -c "select count(*) from sala_de_espera_revisao"
```

**5 · APLICAR (robô parado).**
```bash
cd $M && py admissao/reprocessar_problema.py --aplicar $C/revisoes.json --recibo $C/recibo.json
```
Esperado: `INSERIDAS = CONTA.REVISOES` do seco. `RECUSADO: … corra o SECO outra vez` → o código mudou; refazer 2.

**6 · conferir.** O passo 4 outra vez: `sala_de_espera` com **o mesmo** md5; `sala_de_espera_revisao` com
`+INSERIDAS`. Correr o passo 5 outra vez → `INSERIDAS = 0` (idempotente).

**Desfazer:** não há UPDATE a desfazer. As revisões ficam no histórico (a trava do banco não deixa apagar); para
voltar ao anterior, restaura-se o backup do passo 3 como no `MIGRACAO-SALA.md` §3.

## O que NÃO fiz / NÃO SEI

- **Números da Sala real: NÃO SEI.** Não abri a Sala; quantos itens saem de NÃO SEI só sai do passo 2.
- **Item com duas pragas continua NÃO SEI.** O par por SECÇÃO (cultura da secção × praga da secção) é o próximo passo;
  aqui seria escolher.
- **CULTURA e REGIÃO continuam as mesmas** (fora do pedido): a CAP-WIN só fecha o par com as três.
- **CAP-OPP e as vozes (`voce_dal_campo`) não foram religadas** a esta chave nesta missão: o contrato já está lá para elas.
- Achados, não mexidos: `motor/normalize_agro.norm` apaga o que está entre parênteses — `mencoes_de_problema` não vê
  «(Bactrocera oleae)»; o produtor novo não depende disso (lê a forma já recortada). E o léxico T6 dá o nome
  `peronospora` a *Plasmopara viticola* **e** a *Phytophthora infestans*: o contrato apanha (dois EPPO → nenhum código).

## EM PALAVRAS SIMPLES

A máquina que diz «é hora de tratar a mosca da oliveira na Puglia?» precisava de três coisas escritas em cada
boletim: **a cultura, a praga e o lugar**. A praga até era lida, mas vinha num saco misturado (às vezes três pragas
juntas, sem dizer de que frase veio), e a máquina, honestamente, recusava tudo.

Agora a praga tem **uma ficha com regras**: um nome só; a frase exata do boletim onde ele está escrito; se estava
numa frase, num cabeçalho ou no título; e o código internacional (EPPO) **só** quando o boletim escreve o nome
científico. Se o boletim fala de **duas** pragas, a ficha diz **NÃO SEI** — escolher uma seria inventar. Os cinco
jeitos de escrever «mosca da oliveira» contam como **uma** praga.

Quem lê a ficha confere que a frase está mesmo no boletim; se não está, recusa. Para as fichas antigas da Sala há um
programa que as refaz numa **cópia**, sem gravar nada, e só grava (acrescentando, nunca apagando) quando o
coordenador mandar. Provei num banco de testes descartável que funciona e que a Sala não precisa de mudar de forma.

O que ainda falta para a janela abrir de verdade nos itens antigos: a **cultura** e o **lugar** deles, que continuam
em branco — isso não era desta missão.
