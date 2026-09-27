# DELTA PARA O KNOW-HOW CANÓNICO — O BACKEND APOSENTADO, E A MEDIÇÃO QUE VIROU VEREDITO

```
ORIGEM            C-SALA-TRUTH-01
BRANCH            claude/sala-truth-01 @ 6ac09de1
BASE FUNCIONAL    claude/local-gpu-on-current-collection-v1 @ 611e7cbf
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ 5705ac7b   (medido 2026-09-14)
ÚLTIMA SECÇÃO     §119.5   (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — quem integrar escolhe o primeiro livre
```

> **UMA LEI SÓ, E ELA É GERAL.** Esta missão foi pequena de propósito: uma
> prova, um leitor, e as travas. O que ela aprendeu não é sobre a Sala de
> Espera — é sobre **qualquer** medição que sobreviva à peça que mediu.

---

## A LEI

> ## MEDIR UM BACKEND APOSENTADO NÃO PROVA O ESTADO DO ACTUAL.
> ## E NÃO CONSEGUIR MEDIR NÃO É UM RESULTADO DA COISA MEDIDA.

---

## O QUE FOI MEDIDO, E ONDE

`provas/a_fronteira_da_coleta.py` respondia pela Sala de Espera com uma linha:

```python
produzido = os.path.isdir('data/samples/PRONTO-PARA-INTELIGENCIA')
...
"READY_PRODUZIDO": produzido
```

Essa pasta é a morada do backend **FICHEIRO**. A própria Sala declara
`_Ficheiro.CANONICO = False`, e `admissao/sala_de_espera.py::caminho_da_corrida`
tem escrito, em comentário:

> *«Isto é endereço do backend não canónico. Quem quiser saber onde o READY
> operacional vive pergunta a `estado_operacional()`.»*

**A prova não perguntava.** Medido no ficheiro inteiro: `sala_de_espera` aparecia
**0 vezes**. Nenhum import, nenhuma chamada, nenhuma ligação aberta.

E do disco vazio saía um veredito, publicado num artefato que dois mapas leem:

```
READY_PRODUZIDO = false
GAP             = READY_NUNCA_PRODUZIDO
«o contrato existe (...) e NUNCA foi produzido um READY»
```

Enquanto isso, na **mesma pasta**, `system-map/data/pedido-t4.observado.json`
mostrava `WAITING_ROOM.OBSERVED = true` com o nome do ficheiro pousado.

---

## OS TRÊS DEGRAUS DO SALTO

Nenhum deles é grande. É a soma que mente.

| degrau | o que se sabia | o que se publicou |
|---|---|---|
| 1 | não olhei para a Sala canónica | — |
| 2 | a pasta da V1 não existe | «a Sala está vazia» |
| 3 | — | «NUNCA chegou nada» |

O degrau 2 troca o sujeito: mede-se uma coisa e fala-se de outra. O degrau 3
troca o tempo verbal: o presente por todo o passado. Cada troca é pequena e
defensável sozinha; juntas, produzem uma afirmação que nenhuma medição sustenta.

---

## AS QUATRO SEPARAÇÕES QUE ISTO OBRIGA

```
NOT_OBSERVED   != DOES_NOT_EXIST
UNKNOWN        != NO
ERROR          != ZERO
VAZIO AGORA    != NUNCA HOUVE
```

As três primeiras já estão nesta casa (`leis/relevancia_da_fonte.py:96`). **A
quarta é a nova**, e é a mais fácil de perder, porque a resposta errada tem a
forma certa: um número, e o número é zero.

---

## A REGRA OPERACIONAL

1. **Quem mede um conceito pergunta ao dono dele.** Não ao disco, não à tabela,
   não ao caminho. `ONE CONCEPT -> ONE OWNER` vale para quem **lê**, e não só
   para quem escreve.
2. **Antes de responder, verificar se o que se mediu é o canónico.** Um backend
   `DISPONIVEL = True` e `CANONICO = False` está de pé e **não** responde pela
   coisa. Disponível não é canónico.
3. **Sem capacidade de medir, o resultado é `NOT_MEASURED`** — nunca o valor
   mais desfavorável, nunca o mais favorável.
4. **A pergunta que a API canónica responde é a única que se pode responder.**
   `listar_pendentes()` diz *quem espera agora*. Quem já foi `retirar()` sai da
   fila. Logo «zero à espera» não vira «nunca chegou», e **não se inventa um
   `NAO`** para completar o vocabulário: consultar a tabela por fora para
   responder ao histórico criaria um segundo dono da Sala.

> **PREFERE-SE A RESPOSTA CURTA E VERDADEIRA À RESPOSTA COMPLETA E FABRICADA.**

---

## A ARMADILHA DA CORREÇÃO — E ELA É CONTRA-INTUITIVA

Trocar um booleano por três palavras **não é seguro por omissão**:

```python
bool("NOT_MEASURED")  ->  True
```

Um leitor a jusante que não seja atualizado **não fica pessimista: fica
optimista**. Neste caso, `censo_cards_sensores.py` passaria a dizer que **58
sensores atravessaram a fronteira** por a Sala **não** ter sido medida — o
defeito oposto, e pior que o original.

Por isso, quando um campo publicado muda de tipo:

- **a versão do esquema sobe** (`fronteira-observada/v1` → `/v2`);
- **todos os leitores são medidos**, e não só os lembrados;
- **fica uma trava** que reprova qualquer `bool(...)` sobre o campo.

> **UMA CONVERSÃO PARA BOOLEANO É UMA DECISÃO SOBRE O TERCEIRO ESTADO,
> E ELA NUNCA É TOMADA POR QUEM ESCREVE `bool()`.**

---

## O QUE ESTA MISSÃO **NÃO** APRENDEU

- **Não** ficou provado que a Sala canónica tenha ou não material hoje. Esta
  máquina não tem Postgres nem `psql`; o veredito medido é `NOT_MEASURED`, e é
  essa a resposta certa para esta máquina.
- **Não** se mediu a Sala contra Postgres real. As quatro situações estão
  provadas contra um dono de mentira com a mesma superfície do verdadeiro —
  isso prova a **conclusão**, não a tecnologia.
- **Não** se tocou em `M-SALA` nem em `M-TRAVA`: medido, eles derivam de
  **outros** artefatos (`pedido.observado.json` e `TRAVA-DA-INTELIGENCIA.json`),
  e a premissa de que os três nasciam desta prova era falsa. Só `M-READY` e o
  `ENTROU` do censo bebem daqui.

---

## DOIS FACTOS DE AMBIENTE, MEDIDOS DE PASSAGEM

Não são lei; são o que a próxima pessoa nesta máquina vai bater de frente.

1. **A cadeia canónica do mapa não corre nesta árvore.**
   `system-map/scripts/relatorio_do_fluxo.py` rebenta no passo 5 de 20 com
   `TypeError: '<' not supported between 'NoneType' and 'str'`: 31 das 175
   observações do livro italiano têm `MIME_ASSINATURA: null`, e `sorted()` sobre
   um dicionário com chave `None` não existe. **Pré-existente em `611e7cbf`** —
   verificado com a árvore limpa.

2. **`grep` chamado de Python no Windows expande chavetas.**
   `_grep(r'...{0,4}...')` chega ao `grep.exe` do MSYS já partido em três
   padrões. `MSYS=noglob` resolve, e é variável de ambiente — não é conserto de
   código. Sem ela, a prova recusa-se a correr (e bem: ela verifica o código de
   saída do `grep`).
