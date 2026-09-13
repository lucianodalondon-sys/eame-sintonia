# C6 · TEXT SPECIES / TRANSCRIPT PROVENANCE GATE — a entrega

> **O objetivo:** garantir que nenhum texto vindo de vídeo seja tratado como
> transcrição original quando a evidência só prova tradução, ASR local, ou
> espécie desconhecida.
>
> **O que o censo encontrou:** o texto estava a decidir **onde o facto
> aconteceu**, sem nada perguntar de onde ele vinha.

```
TEXT EXISTS != ORIGINAL TEXT PROVEN.

O CONSUMIDOR ERA `regras/sensor_medir.py`.
O CAMPO ERA `COUNTRY_OF_FACT`.
E ELE MUDAVA EM QUINZE DOS 28 VÍDEOS QUE O TEXTO TOCAVA.
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-scrap-text-provenance-c6` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-youtube-transcript-c5` |
| **SOURCE_HEAD** (referência do coordenador) | `881d062ef22cc2d4f75677b8b6b6973c34dcd41f` |
| **ACTUAL_INITIAL_HEAD** (medido) | `881d062ef22cc2d4f75677b8b6b6973c34dcd41f` |
| **FINAL_HEAD** | o commit que traz este documento — um ficheiro nunca nomeia o commit que o contém |
| **PUSH_STATE** | `PUSHED` · nenhum `force`, nenhuma reescrita de história |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |
| **DRIFT** | **NENHUM** |

Os commits da missão, do mais antigo ao mais recente:

```
f9364fc0  C6: o texto decidia o lugar do facto sem dizer de onde vinha
0032cc02  C6: a auditoria declarava de onde leu, mas nao onde o facto aconteceu
58dffc29  System Map: a auditoria da especie ganhou peca, e o medidor perdeu o verde
<este>    C6: a entrega
```

O segundo não estava previsto: nasceu de a suíte ter reprovado o artefato desta
missão contra um contrato da casa. A secção J conta-o.

O `fetch --all --prune` trouxe duas branches novas de outra frente
(`ingresso-admission-handoff-v1`, `ingresso-admission-seam-v1`) e um avanço na
branch de know-how. **Nenhuma foi fundida**; a de know-how foi lida antes de
escrever.

---

# B · VOCABULARY

| campo | valor |
|---|---|
| **OWNER** | `regras/proveniencia.py` |
| **VALUES** | `NATIVE_CAPTION_ORIGINAL` · `NATIVE_CAPTION_TRANSLATED` · `ASR_LOCAL` · `NÃO SEI` |
| **BASES** | `DECLARED_BY_PROVIDER` · `PRODUCED_BY_LOCAL_ASR` · `NOT_DECLARED` |
| **VALIDATION** | prova que varre toda entrada possível e exige valor da lista |

### Por que o dono mudou de sítio

A C5 declarou o vocabulário em `regras/sensor_coleta.py` — e a razão era boa:
foi o primeiro ficheiro a precisar dele. A C6 encontrou o **segundo** consumidor,
`regras/sensor_medir.py`, e dois consumidores mudam a pergunta:

```
ONE CONCEPT -> ONE OWNER. E o dono da procedência de um texto derivado
não é quem o colheu primeiro: é quem governa procedência.
```

`regras/proveniencia.py` já era dono do vocabulário da ausência (`NÃO SEI`,
`NOT_PRESERVED`) e de três listas fechadas com a mesma forma (`STATUS_RUN`,
`ESTADOS_RAW`, `CLASSES_RAW`). Mudou de sítio, **não de significado**: os nomes
antigos continuam a resolver em `sensor_coleta`, e há prova de que apontam para o
mesmo objeto.

### `INFERRED_FROM_TEXT` não existe, e a ausência é a lei

As três bases dizem de onde a espécie veio. Nenhuma delas é «li o texto e achei».
Há prova que reprova se alguma base passar a conter `INFER`.

---

# C · PROVIDER CONTRACT

| campo | medido |
|---|---|
| `PROVIDER` | `pintostudio~youtube-transcript-scraper` |
| `DECLARES_LANGUAGE?` | **NÃO** — `NÃO SEI` em 48 de 48 |
| `DECLARES_KIND?` | **NÃO** — nenhum campo de espécie na saída |
| `FIELDS` | `TRANSCRIPT` · `TRANSCRIPT_AVAILABLE` · `TRANSCRIPT_LANGUAGE` · `CAPTION_SOURCE` · `WHY_EMPTY` |
| `EVIDENCE` | os 48 itens preservados em `SENSOR-PILOT/TRANSCRICOES-{A..E}.json` |

Nenhuma corrida nova foi executada. A resposta saiu do que já estava no disco,
como a secção 17 do briefing manda.

```
SE O PROVEDOR NÃO DECLARA A ESPÉCIE, A ESPÉCIE É `NÃO SEI`. E ACABOU.
```

---

# D · HISTORICAL CORPUS

```
TOTAL               48
WITH_TEXT           28
NO_TEXT             20

ORIGINAL_PROVEN      0
TRANSLATED_PROVEN    0
ASR_LOCAL            0
KIND_UNKNOWN        28
```

**`ORIGINAL_PROVEN = 0`, e escreve-se assim.** Nenhum dos 28 textos que esta casa
pagou tem espécie provada. Arredondar `UNKNOWN` para original seria exactamente o
que esta missão existe para impedir.

---

# E · OS 11 CASOS DA C5

| campo | valor |
|---|---|
| `CANONICAL_KIND` | **`NÃO SEI`**, nos onze e nos outros dezassete |
| `AUDIT_STATE` | `YES` em 7 · `NO` em 15 · `UNKNOWN` em 6 (dos 28 com texto) |
| `WHY` | a observação da C5 é leitura sobre o conteúdo, e a lei que a própria C5 escreveu diz que a espécie vem do provedor |

```
QUEM INFERE PODE SUSPEITAR. QUEM INFERE NÃO PODE CARIMBAR.

Se esta auditoria alimentasse `TRANSCRIPT_KIND`, ela revogaria a lei que a
tornou possível — e o corpus passaria a carregar como facto o que é leitura.
```

### E a auditoria automática declara MENOS do que a leitura humana da C5

A C5 encontrou **11** por inspecção de título. A peneira mecânica desta missão
encontra **7 `YES`** e manda **6** para `UNKNOWN`. Os dois números não se
contradizem: medem de maneiras diferentes, e ambas estão declaradas.

A peneira exige **três marcadores funcionais dos dois lados**. Títulos curtos
como «Le mondine e il mostro delle risaie» e «Mosca Olivo · Atracción» não os
têm, e caem em `UNKNOWN`.

```
ELA SUBDECLARA, E ISSO É O ENVIESAMENTO CERTO PARA UMA COISA QUE NUNCA
PODE VIRAR CARIMBO.
```

---

# F · CONSUMER CENSUS

Todos os leitores de `TRANSCRIPT`, `TRANSCRIPT_KIND`, `TRANSCRIPT_LANGUAGE`,
`TRANSCRIPT_LANGUAGE_BASIS` e `CAPTION_SOURCE`.

| READER | camada | PURPOSE | REQUIRES_ORIGINAL? | BEHAVIOR_BEFORE | BEHAVIOR_AFTER |
|---|---|---|---|---|---|
| `regras/sensor_medir.py` → `lugar_do_fato` | DERIVED | onde o facto aconteceu | **SIM** | **texto de qualquer espécie decidia** | exige espécie que sustente o original |
| `regras/sensor_medir.py` → `classificar_conteudo` | DERIVED | tipo de conteúdo | **NÃO** | texto entrava | **continua a entrar** |
| `leis/regua_italia.py` | DERIVED | casamento léxico italiano | **SIM** | ramo existe, **nunca dispara** | inalterado — ver abaixo |
| `motor/v21_completude_oportunidade.py` | DERIVED | conta itens com texto | NÃO | conta presença | inalterado |
| `coleta/comunicacao_classificar.py` | DERIVED | rótulo de evidência | NÃO | usa como fonte de evidência | inalterado |
| `ferramentas/*_transcrever.py` | COLLECTION | escrevem o próprio texto | n/a | produzem `ASR_LOCAL` | inalterado |
| `medidas/voz.py` | DERIVED | corpus de voz | NÃO | lê texto | inalterado |
| `tests/*` | TEST | sentinelas | n/a | — | ganharam 37 provas |

### O leitor que era o defeito

```python
# regras/sensor_medir.py, antes
tr = trans.get(v['SOURCE_URL'])
tipo, ev = classificar_conteudo(v.get('TITLE'), v.get('DESCRIPTION'), tr)
pais_fato, nome = lugar_do_fato('%s %s %s' % (TITLE, DESCRIPTION, tr or ''))
```

`DOES_UNKNOWN_MEAN_ORIGINAL?` → **SIM.** Não havia pergunta nenhuma. Texto
existia, texto entrava.

### O leitor que parecia o defeito e não era

`leis/regua_italia.py:268` tem o mesmo padrão — `if v.get('TRANSCRIPT'):` sem
filtro — e é o consumidor mais sensível que existe: casamento de léxico agronómico
italiano.

**Medido: ele nunca dispara.** Dos 1071 vídeos em `MEDICAO.json`, **zero**
carregam o campo `TRANSCRIPT`.

```
CAN DO != DID DO. O caminho existe, não corre, e as duas coisas
precisam de ficar escritas — a segunda porque é verdade hoje, a primeira
porque deixa de ser no dia em que alguém juntar os campos.
```

Não foi alterado: mexer num consumidor que não consome seria mudar código por
suposição. Fica **declarado** como o próximo a ganhar a trava, se e quando o
campo passar a chegar-lhe.

---

# G · CONTRACT BEFORE / AFTER

### Antes

```
TRANSCRIPT                  o texto
TRANSCRIPT_AVAILABLE        YES | REQUESTED_EMPTY
TRANSCRIPT_LANGUAGE         NÃO SEI, em 48 de 48
TRANSCRIPT_KIND             (C5) a espécie, quando declarada
TRANSCRIPT_LANGUAGE_BASIS   (C5) DECLARED_BY_PROVIDER | NOT_DECLARED
CAPTION_SOURCE              quem trouxe
```

### Depois

O contrato ganhou **um** campo, e nenhum sinónimo:

```
TRANSCRIPT_KIND_BASIS       DECLARED_BY_PROVIDER | PRODUCED_BY_LOCAL_ASR | NOT_DECLARED
```

`TEXT_PRESENT`, `TEXT_LANGUAGE`, `TEXT_PROVIDER` e `SOURCE_VIDEO_ID` **já tinham
campo** — `TRANSCRIPT_AVAILABLE`, `TRANSCRIPT_LANGUAGE`, `CAPTION_SOURCE`,
`EXTERNAL_ID`/`SOURCE_URL`. Criar nomes novos para eles teria sido criar
sinónimos, e sinónimos divergem.

E uma função no dono, que é onde o gate vive:

```python
pv.serve_para_original(especie)   # True só para ORIGINAL e ASR_LOCAL
```

Ela fecha **por omissão**: o que não está na lista não passa. Há prova que lhe
atira `'ORIGINAL'`, `'NATIVE_CAPTION'`, `''`, `None`, `'YES'` e `True` — e todos
são recusados.

---

# H · LINEAGE

O artefato derivado usa o contrato da casa, não um sistema novo:

```
SOURCE_ID         SENSOR-PILOT/ESPECIE-DO-TEXTO-AUDITORIA-V1
ARTIFACT_KIND     DERIVED
PARENT_ARTIFACTS  os cinco TRANSCRICOES-{A..E}.json
EVIDENCE_CLASS    DERIVED_AUDIT
CAPTURED_AT       a hora desta LEITURA, não a da coleta
```

A data é a de hoje **de propósito**: uma auditoria que herdasse a data do pai
diria que observou em 2026-09-02 uma coisa observada agora.

E há prova que confere que cada pai declarado existe no disco.

---

# I · RED TEAM

| # | ataque | resultado |
|---|---|---|
| RT1 | provider não manda kind → vira `ORIGINAL` | reprova: silêncio é `NÃO SEI`, e `serve_para_original` devolve `False` |
| RT2 | inglês + título italiano → `TRANSLATED` canônico | reprova: a decisão canônica não lê conteúdo; a auditoria vive em campos `AUDIT_*` |
| RT3 | ASR local → legenda nativa | reprova: o dono do ASR não nomeia `NATIVE_CAPTION` |
| RT4 | tradução entra no casamento léxico italiano | o consumidor não dispara hoje; a trava está no que dispara |
| RT5 | `UNKNOWN` tratado como original por ausência de filtro | **era o defeito** — corrigido e com prova viva |
| RT6 | histórico é reescrito | reprova: prova confere que nenhum item antigo ganhou espécie |
| RT7 | detector de idioma decide espécie | reprova: prova varre o corpo da função canônica |
| RT8 | espécie e qualidade colapsadas | reprova: nenhuma hierarquia, e o dono di-lo por extenso |
| RT9 | `CAPTION_SOURCE` usado como espécie | são campos distintos; o gate só lê `TRANSCRIPT_KIND` |
| RT10 | tradução descartada globalmente | reprova: `classificar_conteudo` continua a recebê-la |

### Duas correcções a provas minhas, dentro desta missão

**A primeira reprovou por estar certa.** Escrevi um teste com o título
«Periodico olivo 1 Maggio 2026» e esperei que ele fosse neutro. Não é:

```
lugar_do_fato('Periodico olivo 1 Maggio 2026')  ->  ('ES', 'la rioja')
```

A palavra **italiana** «Periodico» sozinha devolve Espanha. Ver a secção M.

```
UM TESTE QUE USA UM CASO JÁ CONTAMINADO NÃO MEDE A TRAVA.
```

**A segunda apanhou a própria entrega.** O teste de detritos reprovava qualquer
ficheiro por rastrear em `data/` — e apanhou o artefato de auditoria desta missão,
que é entrega, não lixo.

```
«AINDA NÃO COMMITADO» NÃO É O MESMO QUE «LIXO DE TESTE».
```

A lei é sobre **bruto falso**. A prova passou a procurar isso: pastas de RAW,
cache de áudio, nomes temporários.

---

# J · TESTS

```
BASE_TOTAL      2022        FINAL_TOTAL     2059
BASE_FAILURES     20        FINAL_FAILURES    20
BASE_ERRORS        1        FINAL_ERRORS       1
BASE_SKIPS       175        FINAL_SKIPS      175
BASE_MODULES      80        FINAL_MODULES     81

NEW_FAILURES       0
```

**37 provas novas.** As 21 vermelhas finais são as mesmas 21 da base — não só em
número: os mesmos 16 testes, com os mesmos nomes.

### A primeira medição deu 24, e estava certa

Correr a suíte foi o que apanhou o erro. A primeira passagem devolveu
`FALHAS 24`, e as quatro a mais eram reais — só que de duas naturezas
diferentes, e misturá-las teria escondido a que importava.

**Três eram eu a medir durante o commit.** As sentinelas de lixo da C4 e da C5
correm `git status` e reprovam ficheiro por rastrear em `data/`. A suíte
atravessou o instante em que o artefato de auditoria ainda não estava commitado,
e apanhou-o.

```
MEDIR A ARVORE ENQUANTO ELA MUDA E MEDIR DUAS ARVORES.
```

**A quarta era um defeito meu.** `tests/test_evidence.py::TestGeografia` exige
que quem declara `SOURCE_LOCATION` declare também `FACT_LOCATION`. O artefato
derivado declarava um e não o outro:

```
FAIL  test_source_e_fact_location_quando_declarados
      (arquivo='data/samples/SENSOR-PILOT/ESPECIE-DO-TEXTO-AUDITORIA-V1.json')
```

Esta leitura não tem lugar de facto nenhum — olha para textos já guardados, não
para o campo onde a doença apareceu. Passou a dizê-lo, na forma que a casa já usa
para artefato que descreve o acervo e não o mundo. O lugar de cada vídeo continua
a viver no artefato-pai.

Os outros três ficheiros que esta prova reprova eram-no **antes** da C6 e
continuam a sê-lo: são dívida anterior, de outro dono. A C6 não acrescentou um
quarto — e essa era a pergunta.

```
A SUITE NAO CONFIRMOU A ENTREGA. ENCONTROU-LHE UM DEFEITO.
```

---

# K · SYSTEM MAP

A cadeia **não se escreve aqui**, e essa é a correção desta secção. Eu tinha-a de
memória em cinco passos. A casa já tinha avisado, em `CADEIA-DO-MAPA.json`:

```
DOIS SITIOS COM A LISTA DOS PASSOS SAO DUAS CADEIAS.
```

Um terceiro sítio — este documento — seria uma terceira. E a minha estava errada
duas vezes: faltavam-lhe quinze passos, e punha `censo_das_estradas_it` **depois**
do gerador, quando o workflow o corre antes. A ordem ali é dependência, não
arrumação: quem lê tem de correr depois de quem escreve.

A autoridade é o workflow, pela razão que a própria casa escreveu:

```
TEXTO NAO REPROVA NADA. WORKFLOW REPROVA.
```

Corri exactamente os 22 passos de `.github/workflows/system-map.yml`, extraídos
dele em vez de transcritos.

```
SYSTEM_MAP_CHECK = PASS · 22 de 22 provas
```

Duas correções foram precisas para lá chegar, e as duas são a lei a funcionar:

**`P9_CODIGO_DECLARADO` reprovou** — `provas/especie_do_texto_auditoria.py` não
tinha peça. «Código novo sem peça no mapa é arquitetura invisível.» Ganhou uma,
`C-ESPECIE-DO-TEXTO`, em `Z-PROVA`, ao lado das irmãs da C4.

**`C-PALAVRAS` caiu de `PROVEN` para `PENDING`** — e isto não é avaria. O mapa
guarda o sha do ficheiro que uma pessoa conferiu contra a descrição. A C6 mexeu
em `regras/sensor_medir.py`, o sha deixou de bater, e a peça pede releitura
humana.

**Não recarimbei.** Repor o verde seria eu certificar a minha própria mudança
como revista por outrem.

```
UM VERDE QUE O PROPRIO AUTOR REPOE NAO E REVISAO. E ASSINATURA EM BRANCO.
```

Movimento total no mapa: 160 → 161 peças, e exactamente duas mudanças de estado.

```
C-ESPECIE-DO-TEXTO   <nova>  ->  PENDING     nasce por ler
C-PALAVRAS           PROVEN  ->  PENDING     mudou depois de lida
```

---

# L · REGRESSIONS

**Nenhuma** — depois do conserto que a secção J conta. A primeira medição teve
quatro a mais e nenhuma delas sobreviveu: três eram a suíte a atravessar o
commit, uma era defeito meu no artefato derivado e foi corrigida.

As 21 vermelhas finais são as mesmas 21 da base, e os mesmos 16 testes.

E as missões anteriores continuam de pé, com prova própria: o gate de política da
C5 fechado, os dois Actors ligados, o padrão do reconhecedor da C4 em `CPU` e
`medium`/`small`, e as quatro capacidades oficiais da C3 pela rota oficial.

---

# M · UM DEFEITO MAIOR, ENCONTRADO E **NÃO** CORRIGIDO AQUI

Ao isolar por que os textos mandavam tudo para Espanha, apareceu o mecanismo — e
ele é muito maior do que a questão da procedência.

`lugar_do_fato` casa nomes de lugar por **raiz truncada**. Para `'la rioja'`:

```
_raizes('la rioja')  ->  ['rio']
```

`'la'` é palavra de função e sai; `'rioja'` tem 5 letras e é cortada para `'rio'`.
E `'rio'` casa com qualquer palavra que o **contenha**:

| palavra | ocorrências nos 28 textos |
|---|---|
| `period` · `periods` · `period,` | 54 |
| `various` | 14 |
| `curious` | 5 |
| `prior` · `prioritize` · `prioritized` | 16 |
| `superior` | 4 |
| `scenarios` | 3 |

E não é só inglês. Em italiano e espanhol: `periodico`, `calendario`,
`fitosanitario`.

```
lugar_do_fato('Periodico olivo 1 Maggio 2026')   ->  ('ES', 'la rioja')
lugar_do_fato('calendario fitosanitario')        ->  ('ES', 'la rioja')
lugar_do_fato('various periods prior to harvest')->  ('ES', 'la rioja')
```

**Alcance medido, só do título e da descrição, sem transcrição nenhuma:**

```
230 dos 1071 vídeos — 21% — já disparam «la rioja» pela raiz `rio`.
```

### Por que não foi corrigido nesta missão

Três razões, e a terceira manda:

1. **não é um defeito de procedência.** É do casador de léxico, que tem outro
   dono e outra lei;
2. **a secção 11 do briefing** diz que a C6 preserva procedência e não julga
   conteúdo;
3. **consertá-lo mudaria 230 registos publicados** de `COUNTRY_OF_FACT`. Isso é
   uma decisão da casa, não efeito colateral de uma missão sobre espécie de texto.

```
UM CONSERTO GRANDE ESCONDIDO DENTRO DE UMA MISSÃO PEQUENA
É UMA MUDANÇA QUE NINGUÉM REVISOU.
```

Fica registado com o mecanismo, o alcance e o comando que o reproduz.

---

# N · O QUE NÃO MUDOU

```
orquestrador global      Collection schema        migrations
gate de política da C5   aquisição de mídia       timedtext · yt-dlp
captions.download        benchmark de GPU         os dois Actors
Instagram · LinkedIn · Facebook · X                portal · deploy · main
```

E mais:

- **nenhum artefato histórico ganhou espécie** — prova varre os cinco ficheiros;
- **nenhum RAW mudou** — prova confere `git status` sobre `data/raw`;
- **nenhuma transcrição nova foi colhida**, e nenhum dólar foi gasto;
- **`MEDICAO.json` não foi regenerado.** A trava corrige os 15 registos na
  próxima corrida de `medir()`; reescrever agora um artefato publicado seria a
  mesma mudança não revisada que a secção M recusa.

---

# O · POLICY GATE

```
C5_DECISION = BLOCKED_NEEDS_AUTHORIZATION
REOPENED    = NO
```

Nenhuma rota foi testada, promovida ou reaberta. A C6 começa **depois** do gate.

---

# P · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = NENHUM
```

O know-how canônico está atualizado. Secção 14, cinco lições, medida a medida:

```
BRANCH        claude/sintonia-eame-know-how-v1
FICHEIRO      HANDOFF-ATUAL-SINTONIA-EAME.md
INITIAL_HEAD  fa8b98743beaa0425365b7f56836c2342ae4dabf
FINAL_HEAD    e219edc27d45af500d8b6a23260aaf2b46d74339
```

O que passou a estar lá:

1. **o portão é pequeno e no sítio certo** — o tipo de conteúdo sobrevive à
   tradução, o lugar do facto não;
2. **o dono de um conceito é quem o governa, não quem chegou primeiro** — e o
   gatilho da mudança é o **segundo** consumidor, não o gosto;
3. **auditoria e identidade vivem no mesmo artefato e em campos diferentes** —
   quem infere pode suspeitar, não pode carimbar;
4. **`ORIGINAL_PROVEN = 0`, dito como é** — arredondar `NÃO SEI` para «original» é
   a única maneira de perder o corpus inteiro;
5. **um casador que trunca raízes curtas casa palavras que não existem** — `rio`
   de «la rioja» apanha `period`, `various`, `calendario`.

---

# Q · YOUTUBE STATE

```
YOUTUBE_SEARCH_ZERO_APIFY      = YES
YOUTUBE_CHANNEL_ZERO_APIFY     = YES
YOUTUBE_METADATA_ZERO_APIFY    = YES
YOUTUBE_COMMENTS_ZERO_APIFY    = YES

YOUTUBE_TRANSCRIPT_ZERO_APIFY  = NO
YOUTUBE_MEDIA_ZERO_APIFY       = NO
YOUTUBE_ZERO_APIFY_TOTAL       = PARTIAL
```

Os três últimos não se mexeram, e a C6 não tinha como os mexer: eles dependem de
autorização, e esta missão trabalhou dentro do que já está autorizado.

---

# R · READY_TO_LEAVE_YOUTUBE_FRONT

```
YES
```

O que podia ser feito por engenharia está feito e está seguro:

- as quatro capacidades saíram do pago e estão provadas ao vivo (C3);
- o reconhecedor tem dono único, política de ferro e carimbo honesto (C4);
- o gate de legenda está fechado com documentação oficial na mão (C5);
- e o texto que entra já não decide o lugar do facto sem dizer de onde veio (C6).

O que resta depende de **autorização externa documentada** — permissão escrita,
permissão de edição por canal, mudança na API oficial, ou um provedor com base
contratual publicada.

```
ISTO NÃO SIGNIFICA «YOUTUBE ESTÁ 100% ZERO-APIFY».
Significa que o que falta não se resolve com código, e que o que se
resolvia com código já não tem dívida escondida.
```

E fica uma coisa que a casa ganhou sem a procurar: a secção M nomeia um defeito
de 230 registos que nenhuma missão tinha visto, com o mecanismo e o alcance
medidos, pronto para quem for dono dele decidir.
