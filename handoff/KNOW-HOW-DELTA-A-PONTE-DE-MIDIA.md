# DELTA PARA O KNOW-HOW CANÓNICO — A PONTE QUE NÃO SABE DE ONDE O BYTE VEIO

```
ORIGEM            C4H · A PONTE DE MÍDIA  →  C-GATE-BIG-COLLECTION-01
BRANCH            claude/big-collection-gate-01
BASE FUNCIONAL    claude/youtube-italia-caption-audio-8b460b @ fa980fe7
                  + claude/collection-preserve-facts-2139eb @ 4708f772
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ 5705ac7b  (medido 2026-09-14)
ÚLTIMA SECÇÃO     §119  (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — quem integrar escolhe o primeiro livre
```

> **⚠️ ESTE FICHEIRO NÃO É UM SEGUNDO KNOW-HOW.**
> O know-how canónico é `SINTONIA-EAME-KNOW-HOW.md`, e ele vive noutra linha.
> Escrever aqui uma cópia das suas leis criaria a coisa que este projeto passa
> a vida a consertar: **dois donos do mesmo conceito**. Isto é um DELTA, na
> forma que `handoff/KNOW-HOW-DELTA-A-BASE-DA-AUDITORIA.md` já fixou.

> **⚠️ E ELE JÁ ESTEVE NO SÍTIO ERRADO.**
> A C4H escreveu este texto em `docs/know-how/SECAO-A-PONTE-DE-MIDIA.md` —
> uma pasta nova, com forma de secção e número em branco. A intenção era boa
> (não reivindicar número sem medir), mas o sítio estava errado: uma pasta
> chamada `know-how/` dentro do repositório é, para quem chegar depois, um
> segundo lugar onde procurar a lei.
>
> ```
> NÃO RECLAMAR O NÚMERO NÃO CHEGA. UM DELTA NO SÍTIO ERRADO
> AINDA É UM SEGUNDO ENDEREÇO PARA A MESMA AUTORIDADE.
> ```
>
> Movido para `handoff/`, que é onde esta casa já punha os outros três, e a
> pasta `docs/know-how/` foi retirada.

---

## A LEI

```
DECLARADO PELO OBSERVADOR  >  DEDUZIDO DO NOME  >  NÃO SEI
```

Quem viu os bytes chegarem sabe mais sobre eles do que a extensão do ficheiro.
A extensão continua a valer — como **último** recurso, nunca como autoridade.

Esta casa já pagou por confiar na extensão: 46 ficheiros `.pdf` que eram a
página HTML do site. E pagou outra vez pelo contrário — um `.mp4` real de
9,2 MB cuja ficha saía `NÃO SEI`, porque a tabela de extensões tinha quatro
entradas e nenhuma era vídeo. `NÃO SEI` não é neutro: a porta da derivação
trata a ausência como «tenta», de propósito e com razão. Resultado: o vídeo
seguia para o extrator de PDF.

```
UMA TRAVA DE ESPÉCIE COM A ESPÉCIE APAGADA A MONTANTE
NÃO PROTEGE NADA: ELA SÓ NÃO TEM O QUE LER.
```

---

## «ALGUÉM ABRE» NÃO É «QUEM ABRE»

Duas perguntas diferentes, e um único executor faz as duas parecer a mesma:

```
_quem_deriva_aceita(media_type)  ->  bool   ALGUÉM abre isto?
executor_para(media_type)        ->  mod    QUEM abre isto?
```

Enquanto houve um executor só, as respostas coincidiam **por acidente**. A porta
já lia capacidade declarada e estava certa; quem derivava a seguir chamava
sempre o mesmo executor, escrito à mão num `import` no topo do runner.

```
UM `import` NO TOPO NÃO É UMA DECISÃO DE ROTEAMENTO.
```

E a espécie tem de **viajar com a unidade**. A porta lê `MEDIA_TYPE` para
decidir se deixa passar; se não o puser na unidade, quem deriva a seguir só
recebe um caminho de ficheiro — e a extensão volta pela janela.

---

## FAMÍLIA, E NÃO LISTA

`application/pdf` cabe numa tupla de um. Mídia não:

```
video/mp4 · video/quicktime · video/webm · audio/mpeg · audio/mp4
audio/wav · audio/ogg · audio/x-m4a · audio/flac · …
```

```
UMA LISTA QUE PRECISA DE SER COMPLETA PARA ESTAR CERTA
ESTÁ ERRADA NO DIA SEGUINTE.
```

A família (`audio` · `video`) decide **a quem perguntar**. Quem responde é o
executor, que abre o contentor e mede com `ffprobe`. A família não afrouxa a
trava — ela só escolhe o interlocutor.

---

## A PONTE NÃO SABE DE ONDE O BYTE VEIO

YouTube, Instagram, site oficial, carregamento à mão ou ficheiro local podem
todos entregar bytes à mesma ponte. Ela recebe **um caminho e um pai canónico**,
e mais nada.

```
UMA PONTE QUE SABE DE ONDE O BYTE VEIO É UMA PONTE POR PLATAFORMA,
E AÍ SÃO CINCO PONTES QUE DIVERGEM EM SILÊNCIO.
```

Isto é verificável, e é verificado: um teste lê o ficheiro **sem comentários
nem literais de texto** e exige que nenhum nome de plataforma apareça no código
que corre. A docstring nomeia-as de propósito — para dizer que as trata a todas
por igual.

```
UM TESTE QUE LÊ A PROSA ESTÁ A VERIFICAR A PROMESSA, NÃO O FACTO.
```

---

## PAÍS NÃO É LÍNGUA, E ISTO TEM PROVA DE CAMPO

A ponte passa `idioma=None` ao dono do ASR. O campo volta `LANGUAGE_SOURCE =
DETECTED`, com a confiança ao lado.

A tentação é olhar para `source_country` do pai e escrever `it`. Um vídeo
italiano pode ter um convidado a falar inglês — e o erro não avisa: o texto sai
com aspeto normal. Já foi medido nesta casa: dois reels voltaram `en` com
confiança 0,37, sendo espanhóis.

```
PAÍS É DE ONDE A FONTE É. LÍNGUA É O QUE SE OUVE.
IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.
```

`LANGUAGE_SOURCE` é o campo que separa «eu declarei» de «a máquina achou». São
graus de prova diferentes, e colapsá-los apaga a única coisa que permite
desconfiar.

---

## ERRO DO RECONHECEDOR NÃO É RECUSA DO CONTEÚDO

```
SEM_FAIXA_DE_AUDIO      REJECTED   propriedade do ORIGINAL
REQUESTED_EMPTY         REJECTED   tem som, e não há fala nele
ASR_INDISPONIVEL        ERROR      a biblioteca não está cá
ASR_FALHOU · TIMEOUT    ERROR      avaria nossa
```

```
UM VÍDEO MUDO NÃO É UMA FERRAMENTA PARTIDA.
E UMA FERRAMENTA AUSENTE NÃO É UM VÍDEO SEM FALA.
```

Sem estas linhas na tabela de destinos, tudo o que vinha da mídia caía em
`UNKNOWN` e a etapa saía `ERROR` sem que nada nosso tivesse falhado. E o recibo
do executor tem de carregar o **porquê** no campo que o runner lê:

```
UM NÚMERO DE FALHAS SEM A RAZÃO DELAS NÃO É TELEMETRIA: É UM ENIGMA.
```

---

## ANTES DE CRIAR UM NOME, PROCURAR SE A CASA JÁ TEM UM

`derived_artifact.kind` é uma **lista fechada de sete valores**, na `migration
022`. Um deles já era `'TRANSCRIPTION'`, com o comentário `-- whisper sobre
audio` ao lado: a casa reservou a palavra antes de existir quem a usasse.

Escrever `AUDIO_TRANSCRIPTION` produziu um sintoma caro de ler — a etapa saiu
`DERIVED FAIL · {'ERROR': 1}` e o motivo era `METADATA_NOT_RECONCILED`, «os
bytes ficaram no armazém e a linha não entrou». Parece avaria de escrita, e era
um nome inventado a bater numa trava que funcionava.

```
UMA LISTA FECHADA É UM VOCABULÁRIO, E NÃO UM OBSTÁCULO.
```

---

## O DERIVADO É DO CONTEÚDO; A CHAVE PRENDE-O A UMA OBSERVAÇÃO

Medido no retry, e é um achado que **não é desta ponte**:

A identidade do derivado é por **conteúdo** — `parent_sha256` + receita. Mas a
linha tem chave estrangeira composta `(raw_asset_id, parent_sha256)`. Duas
corridas sobre os **mesmos bytes** produzem **duas observações**; o filho já
existe e aponta para a primeira. A segunda não o pode adotar, e também não pode
escrever outro.

```
ENQUANTO HOUVER UMA OBSERVAÇÃO SÓ POR CONTEÚDO, OS DOIS FACTOS COINCIDEM.
```

É a mesma trava que o PDF sempre teve, e que nunca fora exercitada com duas
observações do mesmo byte. **Não se mexeu nela para o verde aparecer.**

---

## E O COMENTÁRIO QUE ENVELHECEU CUSTA A MISSÃO SEGUINTE

Dois cabeçalhos desta casa afirmavam que a estrada terminava em `DERIVED` e em
`ADMISSION`. Eram verdade quando foram escritos. Depois a estrada cresceu, e
ninguém foi apagar as frases.

Em 2026-09-14 uma missão leu-as, concluiu que faltava estrada, e começou a
planear arquitectura nova para uma estrada **que já estava construída**.

```
UM COMENTÁRIO DESACTUALIZADO NÃO É RUÍDO: É UMA AFIRMAÇÃO FALSA
ASSINADA POR ESTA CASA, E A PRÓXIMA PESSOA ACREDITA NELA.

CODE/RUNTIME TRUTH VENCE COMENTÁRIO HISTÓRICO — e quem o descobre
tem de ir apagar a frase, não só contorná-la.
```

---

## COMO SE PROVA

```bash
py provas/a_ponte_de_midia_atravessa.py     # local, sem banco, com mídia real
py -m unittest tests.test_c4h_ponte_de_midia
# e contra PostgreSQL 16 de verdade, no CI:
#   .github/workflows/banco-descartavel.yml  ·  job `ponte-de-midia`
```

Medido a 2026-09-14, no CI:

```
ETAPAS_OBSERVADAS = ['ADMISSION', 'DERIVED', 'RAW', 'READY', 'STRUCTURED']
PONTE_DE_MIDIA_POSTGRES = PROVADO · 20 passaram · 0 falharam
```

---

## O QUE A C-GATE-BIG-COLLECTION-01 ACRESCENTOU

### ETAPA REGISTADA ≠ UNIDADE PRODUZIDA

A prova da ponte de mídia media, e media com honestidade:

```
ADMISSION_EXECUTED = YES   ADMISSION_DECISION = NAO_SEI
READY_HANDLING = NOT_RUN   WAITING_ROOM_HANDLING = NOT_RUN
```

A etapa `READY` **correu**. Nenhum READY **existiu**. As duas frases são
verdadeiras ao mesmo tempo, e quem ler só a primeira conclui o contrário da
segunda.

```
ETAPA REGISTADA ≠ UNIDADE PRODUZIDA.
MÓDULO EXISTE ≠ LINHA EXISTE.
```

A única maneira de não as confundir é **ir contar a linha na tabela** — e
depois **abrir outro processo** e perguntar ao dono canónico se ela ainda lá
está. Um recibo de escrita é a afirmação de quem escreveu.

### PERGUNTAR À TABELA NÃO É PERGUNTAR AO DONO

A prova de durabilidade abre um interpretador novo e chama
`sala_de_espera.ler()` — não faz `select`. Um `select` mediria o Postgres, e
no dia em que o dono mudasse de forma de guardar a prova continuaria verde
sobre uma casa vazia.

### UM CAMPO DE CONTRATO NÃO É UMA COLUNA

`CAMPOS_READY` tem 19. A tabela tem coluna homónima para **17**. Os outros dois
estão certos assim, e a equivalência declara-se:

```
ESTADO   constante do contrato — guardar uma coluna cujo valor é sempre o
         mesmo seria guardar a palavra, e não o facto
CORRIDA  mora em `run_id`, que é como a casa inteira lhe chama. Uma segunda
         coluna seria um segundo nome para a mesma identidade, livre para
         divergir
```

Uma verificação ingénua (`campo.lower() in colunas`) reprova sobre uma tabela
correcta. A equivalência tem de ser **declarada e verificada**, para que mudar
de casa obrigue a reescrevê-la.

### UM TEMPLATE QUE FORMATA CÓDIGO COMPETE COM O CÓDIGO

O processo leitor era montado com `... % (RAIZ, RUN)` e o próprio texto do
programa tinha um `%r` numa mensagem de erro. A formatação de fora comeu-o, e
a secção inteira morreu sem imprimir uma linha.

```
UM TEMPLATE QUE FORMATA CÓDIGO COMPETE COM O CÓDIGO PELOS MESMOS SÍMBOLOS,
E QUEM PERDE É SEMPRE O DEPURADOR.
```

Valores para um subprocesso passam por ambiente, em JSON — o mesmo caminho por
onde a resposta volta.

### UM PORTÃO QUE NÃO CORRE NÃO É UM PORTÃO FECHADO

`provas/o_egresso_antes_da_aquisicao.py` abortava há dias, em **todas** as
branches, com `ModuleNotFoundError: yaml`. A causa não era arquitectura: era
uma dependência que ninguém declarou.

```
UM PORTÃO QUE NÃO CORRE NÃO É UM PORTÃO FECHADO: É UM PORTÃO AUSENTE,
E ELE ESTAVA VERMELHO A DIZER ISSO.
```

Escrever um analisador de YAML caseiro para fugir à dependência poria um
segundo dono a interpretar o mesmo ficheiro — e um analisador que se engane
deixa o portão passar por cima da lei que ele existe para guardar.

Medido depois: `CASOS=34 PASS=34 RED_TEAM_SURVIVORS=0`.

### COMO SE PROVA (acrescento)

```bash
# contra PostgreSQL 16 de verdade, no CI:
#   .github/workflows/banco-descartavel.yml  ·  job `portao-big-collection`
py provas/o_portao_da_big_collection.py   # exige SINTONIA_SALA_BACKEND=POSTGRES
```

Medido a 2026-09-14, no CI:

```
MIGRATION_032_APPLIED = True · READY_CONTRACT_FIELDS = 19
ADMISSION_DECISION_CANARIO = SIM (IT-T3-010) · CONTROLO_NEGATIVO = NAO_SEI
WAITING_ROWS = 1 · READY_EXISTS_AFTER_PROCESS_EXIT = True · LEITURA_CAMPOS = 19
PORTAO_BIG_COLLECTION = PROVADO · 18 passaram · 0 falharam
```
