# C10.1 · O REEL PARA DE FABRICAR SOURCE_ID COM URL

```
MEDIDO_EM        = 2026-09-11
C10_1_SOURCE_ID  = PASS
INSTAGRAM_AUDIO_ONLY = PROVEN  (não regrediu)
```

> Evidência de missão. Não é Bíblia, não é MASTER, não substitui contrato.

---

## A · O DEFEITO, E POR QUE A C10 NÃO O CORRIGIU

A C10 encontrou isto e escreveu uma etiqueta ao lado:

```python
SOURCE_ID  = ident.get('SOURCE_URL', NAO_SEI)      # ← o endereço
SOURCE_URL = ident.get('SOURCE_URL', NAO_SEI)      # ← o mesmo endereço
NOTES['SOURCE_ID_KIND'] = 'URL_AS_PLACEHOLDER'     # ← a etiqueta
```

A etiqueta melhorou a observabilidade e **não corrigiu identidade**. Pedia
desculpa pela mentira sem a desfazer.

```
UMA ETIQUETA NÃO TRANSFORMA UM URL EM IDENTIDADE.
```

---

## B · O QUE TORNA ISTO GRAVE, E NÃO APENAS FEIO

`guarda/preservar_coleta._identifica()` é a trava desta casa. Ela recusa as
confissões — `NAO SEI`, `UNKNOWN`, vazio, `None` — e **aceita tudo o resto**.
Medido nesta missão:

```
_identifica('https://www.instagram.com/reel/ABC')  →  True
_identifica('NAO SEI')                             →  False
_identifica(None)                                  →  False
```

Ou seja: o endereço **comprava** um `IDENTITY_STATE` que ninguém tinha provado,
e comprava-o exatamente no sítio onde a casa põe a trava. Com o URL no campo,
`identidade_da_observacao()` devolvia `FORWARD_IDENTITY_UNPROVEN` com
`SOURCE_ID = <o endereço>`; com o sentinela devolve `IDENTITY_STATE = None`.

```
CAN ENTER NÃO SE COMPRA COM IDENTIDADE FALSA.
```

E a linha madura de identidade já dizia isto em claro. `identidade_da_observacao`
na branch `claude/raw-observation-identity-3jbwco` (`d43126e3`, medido):

> *«O QUE NUNCA ACONTECE AQUI: cair para o `sha256`, para o `SOURCE_NATIVE_ID`,
> para a URL, para o `storage_path` ou para o nome do ficheiro.»*

A lei existia. Quem a violava era a cadeia de Reel.

### Por que a bala estava carregada e não disparada

A cadeia de Reel **não chega** hoje a `preservar_coleta` nem a `ingresso` —
medido, nenhum dos dois é importado por ela. Então o URL nunca chegou a
`raw_asset`.

```
DEFEITO LATENTE != DEFEITO INOFENSIVO.
```

O próximo passo declarado da C10 é ligar esta capacidade ao portão canônico. No
minuto em que isso acontecesse, o endereço passaria a trava — e passaria calado.

---

## C · CENSO DE PRODUTORES E CONSUMIDORES

Feito antes de tocar em código, como manda a §4.

### PRODUCERS de `SOURCE_ID=` — três em código não-teste

| ficheiro | papel | veredito |
|---|---|---|
| `ferramentas/reel_transcricao.py:666` | **PRODUCER** | **o defeito** — corrigido aqui |
| `leis/artefato.py:275` | **TRANSLATOR** | `derivado_de` herda do pai; não fabrica |
| `provas/objeto_e_observacao_no_postgres.py:693` | fixture | usa `"NAO SEI"` de propósito |

### CONSUMERS e JUDGES

| ficheiro | papel | nota |
|---|---|---|
| `guarda/preservar_coleta.py` | **PRESERVER / JUDGE** | traduz `SOURCE_ID` → `IDENTITY_STATE`; é a trava |
| `coleta/ingresso.py:91` | **TRANSLATOR** | `DO_COLETOR` lista os campos que sobem |
| `admissao/admissao.py:167,440` | **JUDGE** | `item.get("source_id") or item.get("fonte") or item.get("url")` — cai para URL, noutra camada e com outro dono |
| `system-map/scripts/scan_sources.py` | CONSUMER | outro `SOURCE_ID`, o do atlas de fontes — **namespace diferente** |

`reel_transcricao.py:1050` também escreve `SOURCE_ID`, mas do **dataset**
derivado (`REEL-TRANSCRICOES/…`), não da publicação. Outro objeto, outra
pergunta; não foi tocado.

### `SOURCE_ID_KIND` — dois usos, zero dependentes

Só a linha que a C10 criou e a frase do documento da C10. **Ninguém lê.** Por
isso foi **removido**, não renomeado: depois de o endereço sair do campo não há
substituto nenhum a descrever, e um campo que descreve um arranjo extinto é a
próxima pessoa a acreditar que ele ainda existe.

---

## D · O QUE MUDOU

```python
SOURCE_ID  = ident.get('SOURCE_ID', NAO_SEI)       # nunca do endereço
SOURCE_URL = ident.get('SOURCE_URL', NAO_SEI)      # o endereço fica no campo dele
```

Uma linha. O resto é a docstring que diz porquê, e os testes que impedem o
regresso.

### Qual é o «desconhecido» canônico, e isto foi medido antes de escolher

A `§6` perguntava se ausência física é melhor do que a string. As duas
autoridades foram lidas e **concordam**:

| camada | representação de «não sei qual é a fonte» |
|---|---|
| `leis/artefato.py` | `SOURCE_ID: str = NAO_SEI` — campo tipado com omissão impossível |
| `guarda/preservar_coleta.py` | `SENTINELAS` contém `NAO SEI`; `identidade_da_observacao` traduz para `SOURCE_ID = None` |

E o comentário da própria casa explica porquê as duas coisas não se
contradizem:

> *«Uma confissão preenchida é PIOR do que um campo vazio quando há índice em
> cima: `source_id = 'NAO SEI'` juntaria observações de fontes diferentes
> debaixo de uma palavra que quer dizer "não sei qual".»*

Por isso a ficha fica no sentinela e **quem escreve na base traduz para
ausência**. Nada de inventar um terceiro valor.

---

## E · OS DOIS CASOS

**CASO A — `SOURCE_ID` provado chega no `ident`:** transportado exatamente,
`SOURCE_URL` fica com o endereço, os dois permanecem distintos, e
`_identifica()` aceita. Há um teste para o ataque mais silencioso: `SOURCE_ID`
provado **com `SOURCE_URL` diferente** — se alguém voltar a derivar do endereço,
o provado desaparece sem ninguém dar por isso.

**CASO B — só o endereço chega:** `SOURCE_ID = NAO SEI`, `_identifica()` recusa,
e o URL **não aparece** no campo de identidade. `identidade_do_url()` nunca põe
`SOURCE_ID` no dicionário — medido — então este é o caminho normal de hoje.

```
NÃO SABER QUAL É A FONTE != NÃO HAVER OBSERVAÇÃO.
```

Com `SOURCE_ID` desconhecido, tudo o resto continua a fechar e há teste para
cada um: `RUN_ID`, `SOURCE_URL`, `POST_ID`, `ARTIFACT_ID`, `SHA256`,
`STORAGE_LOCATION`, `CAPTURE_PROVIDER`, `MEDIA_KIND`, `RAW_OBSERVATION_ID` em
`NOT_KNOWN`, e o transcript com pai declarado.

---

## F · RED TEAM — quatro mutações, quatro quedas

| # | mutação | resultado |
|---|---|---|
| 1 | `SOURCE_ID = SOURCE_URL` — a regressão exata da C10 | **FAILED** (6 testes) |
| 2 | `POST_ID` promovido a identidade de fonte | **FAILED** (6) |
| 3 | `SOURCE_ID or SOURCE_URL` — o endereço como reserva | **FAILED** (4) |
| 4 | o caminho físico vira identidade | **FAILED** (5) |

A terceira é a perigosa: parece defensiva, lê-se como cuidado, e repõe o defeito
inteiro sempre que não há prova — que é **sempre**, hoje.

`DOCUMENT_ID` não é fabricado, e há teste. `POST_ID` continua a existir como
metadado da plataforma e não é promovido: `POST_ID != DOCUMENT_ID` enquanto
contrato canônico não provar a equivalência.

---

## G · A DÍVIDA DE MAPA QUE A C10 DEIXOU, E QUE SÓ APARECE DEPOIS DO COMMIT

A C10 reportou `SYSTEM_MAP_CHECK = PASS`, e isso era verdade **no momento em que
foi medido**. Hoje o commit da C10 reprova.

O motivo é mecânico e vale a pena ficar escrito: o censo de código órfão do mapa
conta ficheiros **rastreados**. `provas/instagram_audio_only.py` era *untracked*
quando a C10 validou, e passou a ser rastreado **no próprio commit** — e da
geração seguinte em diante passou a contar como código que nenhuma peça reclama.

```
VALIDAR ANTES DE COMMITAR NÃO MEDE O QUE O COMMIT VAI CRIAR.
```

Corrigido aqui: `C-PROVA-AUDIO-ONLY` declarado em `architecture.declared.json`
— que é o ficheiro **de gente**, não gerado, e é exatamente o conserto que o
próprio validador manda fazer. O mapa voltou a `PASS` com 163 peças.

---

## H · REGRESSÃO

| momento | testes | falhas |
|---|---:|---:|
| baseline, antes de tocar em código | 389 | 1 |
| depois, com os 14 novos | 403 | 1 |

A falha é a mesma nos dois: `test_o_portal_nao_ganhou_implementacao`, entulho
conhecido e anterior, já contado na C9 e na C10.

```
NEW_FAILURES = 0
ASR_OWNERS   = 1
SYSTEM_MAP_CHECK = PASS
```

E o áudio-only foi reconfirmado ao vivo depois da mudança: `VIDEO_STREAMS = 0`,
`AUDIO_STREAMS = 1`, `VIDEO_BYTES_DOWNLOADED = 0`, transcript com pai declarado.
De passagem, o Reel `C-63RfHoJTU` — o que tinha deixado de responder a meio da
C10 — voltou a responder, o que confirma a volatilidade que a C10 registou.

---

## I · O QUE NÃO MUDOU

A rota, a mídia, o seletor de áudio, o dono do ASR, o modelo, a matriz de rotas,
o executor, o registo, o adaptador, a Collection, o portal. E a capacidade
**continua sem atravessar o portão canônico de rotas** — essa é a próxima
missão, e não é esta.

---

## J · RISCO RESTANTE

1. **`admissao/admissao.py:167`** cai para `item.get("url")` quando não há
   `source_id`. É outra camada, outro dono, e a cadeia de Reel não a alimenta
   hoje — mas é o mesmo atalho, vivo, noutro sítio.
2. **`RAW_OBSERVATION_ID` continua `NOT_KNOWN`.** É `raw_asset.id` e só nasce
   quando a Collection o criar.
3. **Enquanto `SOURCE_ID` for desconhecido**, esta observação não terá
   `IDENTITY_STATE` no portão. Isso é o estado correto de hoje, e não um defeito
   a contornar.

---

## K · VEREDITO

```
C10_1_SOURCE_ID      = PASS
INSTAGRAM_AUDIO_ONLY = PROVEN
NEW_FAILURES         = 0
SYSTEM_MAP_CHECK     = PASS
KNOW_HOW_DELTA       = NENHUM
BÍBLIA/CONTRATO      = NÃO precisa mudar

PRÓXIMO PASSO MÍNIMO = ligar a capacidade Instagram audio-only
                       ao portão canônico de rotas

HARD STOP.
```
