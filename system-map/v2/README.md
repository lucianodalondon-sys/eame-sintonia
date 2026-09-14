# O MAPA DA MÁQUINA — System Map V2

**A lei do projeto está em [`../../AGENTS.md`](../../AGENTS.md).** Este ficheiro
explica o que o V2 é, por que ele existe ao lado do V1, e como se mexe nele.

---

## A DIFERENÇA, NUMA FRASE

```
V1  mostra o REPOSITÓRIO  — 102 peças, cada uma ancorada em ficheiros
V2  mostra a MÁQUINA      — 6 departamentos, e a engenharia só no último nível
```

Os dois são verdadeiros e nenhum substitui o outro. O V1 responde *«onde vive
este ficheiro, e quem o reivindica?»* — é a ferramenta de quem programa. O V2
responde *«de onde vem a informação, quem decide, e onde está parado?»* — é a
ferramenta de quem **não** programa.

O teste do V2 é um só, e é duro:

> Se for preciso abrir código para responder às perguntas macro, o mapa falhou.

---

## OS QUATRO NÍVEIS

```
0  A MÁQUINA        os departamentos, e o sentido do fluxo
1  O DEPARTAMENTO   os seus sistemas
2  O SUBSISTEMA     o que há dentro de um sistema
3  A ENGENHARIA     ficheiros, linhas e provas — na gaveta, sob pedido
```

Uma pessoa não técnica tem de conseguir responder às perguntas macro **sem
chegar ao nível 3**. Por isso nenhum cartão dos níveis 0 a 2 mostra caminho,
ficheiro, tabela, função ou SHA.

---

## AS QUATRO DIMENSÕES, QUE NUNCA SE FUNDEM

Era este o defeito que o V2 nasceu para corrigir. Um único verde por cima
esconderia três factos diferentes:

| | pergunta |
|---|---|
| `CANÓNICO` | alguma autoridade diz que isto faz parte da máquina? |
| `IMPLEMENTADO` | existe código no repositório? |
| `OBSERVADO` | há artefato que prove que isto já correu? |
| `IMPEDIDO` | falta um ficheiro que a própria máquina exige para correr? |

```
CANÓNICO=SIM · IMPLEMENTADO=NÃO   → parte prevista, ainda não construída
CANÓNICO=NÃO · IMPLEMENTADO=SIM   → candidata a legado ou a fora-da-arquitetura
CANÓNICO=SIM · IMPLEMENTADO=SIM · OBSERVADO=NÃO  → escrita, nunca provada a correr
```

**CÓDIGO EXISTE não é FLUXO CORREU.** A pastilha grande do cartão resume a
saúde para quem olha de longe; as quatro dimensões continuam à vista, em
separado, no detalhe.

---

## A LINHA É A PROVA

Cada seta carrega o seu próprio grau de evidência, e **nunca se promove**:

| desenho | estado | o que é preciso para o merecer |
|---|---|---|
| contínua | `OBSERVED` | existe artefato que prova que aquele caminho carregou alguma coisa |
| tracejada | `IMPLEMENTED` | há uma linha de código que a faz — e ninguém provou que correu |
| pontilhada | `DECLARED` | está escrita numa autoridade, e não há código |
| cinza | `UNKNOWN` | nada a prova — **NÃO SEI** |

Uma seta contínua sem artefato reprova no validador (`V3_NAO_PROMOVE`).

---

## AS PEÇAS

```
system-map/v2/
  README.md                     este ficheiro
  model/
    machine.model.json          O ÚNICO ficheiro escrito por gente. Declara CONCEITOS
                                e aponta, para cada um, a autoridade que o sustenta.
                                NÃO contém estado — o validador recusa se contiver.
  scripts/
    scan_machine.py             mede o repositório: a autoridade confirma? o ficheiro
                                existe? o artefato existe? a linha de código existe?
    generate_map_v2.py          junta declarado + medido e CALCULA o estado
    validate_map_v2.py          as 14 provas · falha fechado · corre no CI
  data/
    machine.measured.json       medido      ← gerado, nunca editado à mão
    state.v2.generated.json     o resultado ← é isto que a tela lê
  app/
    index.html  map.js  map.css a tela — só renderiza, não sabe nada
  tests/
    test_map_v2.py              provas das regras, metade delas construindo o caso mau
  provas/
    *.png                       a prova visual desta entrega
```

---

## OS COMANDOS

```bash
python3 system-map/v2/scripts/scan_machine.py      # medir
python3 system-map/v2/scripts/generate_map_v2.py   # calcular e escrever o estado
python3 system-map/v2/scripts/validate_map_v2.py   # as 14 provas (falha fechado)
python3 system-map/v2/tests/test_map_v2.py         # as regras não afrouxaram
```

Para ver a tela (o `fetch` do estado precisa de servidor, não de `file://`):

```bash
python3 -m http.server 8099          # da RAIZ do repositório
```

e abrir `http://127.0.0.1:8099/system-map/v2/app/`.

**Sem dependências:** só biblioteca padrão, como o V1 — um mapa de arquitetura
que precisa de pacote de terceiro para ser gerado tem uma dependência que ele
próprio não consegue explicar.

---

## ⚠️ A ORDEM: V1 ANTES DE V2

O V1 **gera** `regras/LEIA-ANTES-DE-COLETAR.md`, e o V2 **observa** esse
ficheiro. Regerar o V2 antes do V1 mede a versão anterior dele, e o portão
acusa drift sobre uma mudança que ainda vai acontecer.

```bash
python3 system-map/scripts/generate_system_map.py    # 1º — o mapa do repositório
python3 system-map/v2/scripts/validate_map_v2.py     # 2º — o mapa da máquina
```

No CI isto já está na ordem certa (passos 1 → 4c em
[`.github/workflows/system-map.yml`](../../.github/workflows/system-map.yml)).

---

## COMO SE MEXE NELE

**Mudou a máquina?** Regere e commite os dois mapas. O ficheiro que se edita à
mão é `model/machine.model.json`, e só ele.

**O mapa está errado?** Conserte a **fonte** — o modelo, o scanner, o gerador —
e regere. Nunca o JSON gerado, nunca o HTML.

> Editar à mão um artefato gerado é a única forma de mentir neste sistema, e é
> uma mentira que não envelhece: nasce errada e nenhum portão a apanha.

**Declarar um conceito novo** exige quatro coisas, e o scanner recusa-as se não
se confirmarem:

1. `authority` — ficheiro **e** a frase citada, que tem de existir lá dentro;
2. `implementa` — os caminhos que o sustentam;
3. `observado_por` — o artefato que provaria que já correu (ou nenhum, e fica
   em `NÃO SEI`, que é resposta válida);
4. `papel` — se ele não tem entrada nem saída, **porquê**: origem, destino,
   ponto final, ferramenta de mão, ou instrumento. Órfão calado reprova.

---

## O QUE O V2 NÃO É

**Não é arquitetura.** É uma projeção.

```
O SYSTEM MAP OBSERVA A MÁQUINA. NÃO A DEFINE.
```

Ele não cria conceito, não decide dono, não arbitra contrato e não inventa
fluxo. Toda linha do modelo aponta para uma autoridade que já existia antes
dele — `AGENTS.md`, o censo da coleta, os contratos, as bíblias. Onde a
autoridade não confirma, o conceito cai para `NÃO SEI` sozinho.

E ele **não substitui o V1**: os dois correm, os dois são provados no mesmo
workflow, e o V1 continua a ser o dono da lei do repositório.

---

## O DESIGN

A tela carrega os tokens oficiais do ADAMA Design System de
`italia-portale/client/_ds/adama-brandwell/`. Nenhuma cor de marca é escrita à
mão.

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND   (só para a rampa de ESTADO)
NEW_PATTERN_REQUIRED = YES
```

**Motivo — e é o mesmo já registado no V1, não uma decisão nova:** o BrandWell
tem quatro cores de *categoria de produto* e nenhuma significa «quebrado».
Pintar peça bloqueada de roxo Pest Control daria a uma cor de marca um segundo
significado, e a partir daí nenhuma das duas leituras seria de confiança.

```
FAMÍLIA → cor de marca ADAMA (faixa e topo do cartão)
ESTADO  → rampa própria de engenharia, só na pastilha
```
