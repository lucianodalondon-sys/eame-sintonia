# §___ · A PONTE QUE NÃO SABE DE ONDE O BYTE VEIO

> **Secção escrita em forma final, com o número em branco de propósito.**
>
> `SINTONIA-EAME-KNOW-HOW.md` **não existe nesta branch**, e existe em 16
> documentos distintos noutras, com cinco cabeças que declaram «última
> atualização material» diferentes — e o §118 ocupado por quatro títulos.
> Escolher um número aqui criaria a divergência seguinte.
>
> **Aplicar esta secção é decisão de gente.** O texto está pronto; o número não
> se reivindica sem medir se está livre.

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
