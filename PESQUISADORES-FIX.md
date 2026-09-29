# PESQUISADORES_FIX — diagnóstico e proposta (RELIGA-MULTICANAL, D155, 29/09/2026)

**REGISTADO, NÃO LIGADO.** A missão manda registar e não ligar, e é isso que este documento faz.
Nenhuma linha de código da linha PESQUISADORES foi alterada nesta entrega.

---

## 1. O SINTOMA, MEDIDO

```
ferramentas/big_collection/coleta_continua.py  (linha da lista LINHAS)
    {"LINHA": "PESQUISADORES", "TRANSPORTE": "coleta/seguir.py", "CHAMADA": "reserva_24h.reservar("}

O ciclo responde, a cada volta:
    ESPERA_LIGACAO · TRANSPORTE_NAO_EXISTE_NESTA_ARVORE: coleta/seguir.py
```

Medido nesta árvore, nesta missão:

```
COMANDO   git log --all -- coleta/seguir.py            → vazio
COMANDO   git cat-file -e <ref>:coleta/seguir.py       → nenhum ref o tem
COMANDO   ls coleta/seguir.py                          → não existe
```

**`coleta/seguir.py` não existe em ref nenhum deste repositório.** Não é um ficheiro apagado: nunca
existiu. O cadastro aponta para um caminho que nunca foi escrito.

## 2. A CAUSA — o trabalho existe, noutra gaveta

```
O TRANSPORTE REAL:  ferramentas/seguir_pesquisadores/seguir.py      (EXISTE)
```

E à volta dele, o resto da capacidade, também no vivo:

```
(a) IDENTIDADE / CADASTRO ...... ferramentas/seguir_pesquisadores/pessoas.py
(b) DESCOBERTA ................. listas_oficiais.py · fora_do_mur.py
(c) ACOMPANHAMENTO ............. contador.py          ← o contador PRÓPRIO, e é aqui que dói
(d) AQUISIÇÃO .................. orcid_lote.py        (pub.orcid.org)
(e) ENTRADA NA SALA ............ NÃO — tabela `pessoa` = 0 itens
```

A linha não corre **porque o cadastro aponta para o sítio errado** — e não porque o trabalho não exista.

## 3. O QUE IMPEDE DE SIMPLESMENTE REAPONTAR

Medido: `ferramentas/seguir_pesquisadores/seguir.py` responde `SUBSTITUIDO → orcid_lote` e usa um
**contador próprio de 5 pedidos / 24 h**, que vive **fora** do livro da cortesia adaptativa (D90/D124).

```
    ⚠️ REAPONTAR SEM RECONCILIAR PÕE DOIS CONTADORES NA MESMA JANELA DE 24 h.
```

E dois contadores para a mesma janela é exactamente o que esta casa proíbe: cada um deles acha que o
domínio ainda tem lugar, e os dois pedem. Foi esse o defeito que a D90 §2.2 fechou para as outras
linhas — «não havia reserva atómica partilhada; dois processos no mesmo domínio liam ambos 4 e ambos
pediam».

Além disso, `pub.orcid.org` tem orçamento declarado na política
(`regras/POLITICA-CORTESIA-ADAPTATIVA.json`, classe `API_COM_LIMITE_PUBLICADO`): um contador paralelo
de 5/24 h não vê esse orçamento, e o orçamento não vê os pedidos dele. **Nenhum dos dois está certo.**

## 4. AS DUAS PROPOSTAS (nenhuma aplicada)

```
P-1  REAPONTAR
     `coleta_continua.LINHAS` passa a declarar
         "TRANSPORTE": "ferramentas/seguir_pesquisadores/seguir.py"
     e o transporte passa a pedir pela porta única (`coleta/reserva_24h.pedir`), como BUSCA,
     CIENCIA, YOUTUBE, INSTAGRAM e LINKEDIN passaram a pedir nesta entrega.
     CUSTO: o contador próprio de 5/24 h tem de SAIR, não de coexistir.
     GANHO: a linha volta ao ciclo com o mesmo livro de todas as outras.

P-2  RETIRAR
     Declarar a linha inexistente e tirá-la de `LINHAS`. O ciclo deixa de a reportar em
     ESPERA_LIGACAO a cada volta, e o trabalho de `ferramentas/seguir_pesquisadores/` continua a
     correr por fora, como hoje já corre.
     GANHO: o livro de ciclos deixa de ter uma linha que nunca vai correr.
     CUSTO: a capacidade fica declarada como fora do ciclo — o que é a verdade de hoje.
```

**EM QUALQUER DAS DUAS, o contador próprio tem de ser reconciliado com o livro da cortesia.** É essa a
parte que não é mecânica e é por isso que isto é decisão de dono, e não escolha de quem implementa.

## 5. O QUE ESTA ENTREGA FEZ, E SÓ ISTO

```
· escreveu este documento;
· deixou na lista `LINHAS` de `coleta_continua.py` um comentário que aponta para aqui, para que
  quem leia o cadastro errado encontre o motivo antes de o «consertar» sozinho;
· mediu a linha pela sonda de comportamento e registou o resultado: NÃO LIGADA, com o motivo
  `TRANSPORTE_NAO_EXISTE_NESTA_ARVORE`.
```

Nada foi reapontado. Nada foi retirado. Nenhum contador foi tocado.

FIM
