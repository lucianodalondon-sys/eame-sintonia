# DÍVIDA DE LEITURA E VOCABULÁRIO — o que a auditoria mediu

## 1 · A pergunta da missão, respondida

```
CONJUNTO NOVO PODE SUBSTITUIR O ANTIGO?   NÃO
UNIÃO ANTIGO + NOVO AINDA NECESSÁRIA?     SIM
```

Cem pares (rótulo × cultura) que o conjunto antigo tinha e o novo não tinha foram
auditados **um a um**. Um agente leu a geometria de cada rótulo e classificou cada
cultura; um segundo agente tentou **derrubar** cada alegação de autorização, com
instrução explícita de refutar na dúvida. O refutador manda.

| veredito | n |
|---|---:|
| `AUTORIZADO_MAS_NAO_LIDO` — o rótulo autoriza, o parser não lê | **66** |
| `AUTORIZADO_E_LIDO` — resolvidos pelo parser desta madrugada | **33** |
| `NAO_AUTORIZADO` — o conjunto antigo estava errado | **1** |
| `NAO_SEI` | **0** |

**Noventa e nove de cem eram autorização real.** Substituir apagaria autorização
que existe. A união não é precaução: é o que a medição obriga.

### O único erro do conjunto antigo

`011526 SULTAN × CIPOLLA`. O rótulo diz *«diserbante selettivo per colza, cavoli a
infiorescenza, cavoli a testa, cavoli a foglia e **aglio**»*. Aglio, não cipolla.
Ali o conjunto novo está certo e o antigo estava errado.

### O que ainda bloqueia, por rótulo

| rótulo | produto | pares |
|---|---|---:|
| `008189` | LEBRON 0.5 G | 6 |
| `014479` | SCHERMO 0.5 G | 6 |
| `017955` | MAGANIC | 3 |
| `015630` | CARSON 45% WG | 3 |
| 38 outros | | 1–2 cada |

A classe dominante é **`MATRIZ_MULTICOLUNA`**: colunas que o extrator de PDF fundiu
num bloco só. O corte por calha e por cabeçalho foi implementado esta madrugada e
resolveu parte; falta a âncora funcionar também quando uma linha atravessa a calha
(o caso do MAGANIC, onde `Orzo (invernale  Maculatura reticolare…` preenche a
calha exatamente onde ela deveria estar).

## 2 · O que o parser recuperou esta madrugada

| | v3.1 (publicado ontem) | v3.3 (agora) |
|---|---:|---:|
| pares publicados | 2.313 | **2.845** |
| perdas reais (rótulo × cultura) | 100 | **74** |
| rótulos sem nenhum par | 44 | **41** |
| precisão no gabarito | 0,965 | 0,965 |
| recall no gabarito | 0,866 | **0,870** |

Três correções, todas com testemunha:

1. **Tabela de uma linha.** `len(cells) >= 2` descartava tabela com uma só linha —
   zerava SPYRALE, que está no meu próprio gabarito. A regra da linha única é mais
   **estreita**, não igual: sem célula vizinha não há como inferir onde a linha
   termina, então a faixa é a própria altura da célula e o que cai fora vira
   `AMBIGUOUS_ROW`.
2. **Densidade, não comprimento.** `len(t) > 110` recusava célula de cultura que é
   uma lista longa legítima. Seis auditorias independentes apontaram esta guarda.
   Agora o critério é densidade de nomes de cultura.
3. **Coordenadas de palavra.** `ler_geometria` lia `<word xMin=…>` e as jogava
   fora. Sem elas não há como separar colunas fundidas.

### Dois erros meus que a medição pegou

- Cindir a célula em **toda** quebra de linha custou 7 pares no BLAISE ULTRA:
  `Grano tenero e duro,` / `Triticale` continua sendo **uma** célula. Agora só
  cinde quando o vão supera 1,6 × a altura de linha.
- `xmax` da coluna pelo **máximo** fez 008259 perder cereais, barbabietola, mais e
  soia de uma vez — justamente quando a regra nova acertava as ortícolas. Agora é
  a **mediana**: ela descreve onde a coluna termina; o máximo descreve a célula
  mais larga dela.
- E pôr a cisão de colunas dentro de `ler_geometria` derrubou o recall de 0,868
  para **0,504** num golpe: todas as rotas usam essa função, e eu estava
  estilhaçando o bloco de que as outras dependem.

### Um falso positivo publicado, achado pela auditoria

`SOIA × APION` e `SOIA × FITONOMO`, em três rótulos. A frase *«Afidi (foglie non
accartocciate), apion, fitonomo»* pertence à linha das **Foraggere** (prati-pascoli,
loglio, mais, barbabietola da foraggio, **erba medica**) — não à soia. Seis pares
errados, extintos.

## 3 · Vocabulário do motor — proposta, não alteração

O motor vive em `claude/opportunity-commercial-priority-v1` (`b3935bd`). Alterar
`v21_normalizar.py` a partir daqui seria mexer no motor de fora. O que sai é
**proposta com a regressão já rodada**.

```
alvos do vocabulário de rótulos ................ 61
com ISSUE_ID no motor .......................... 14
sem ISSUE_ID ................................... 47   ← auditados
```

| decisão final | n |
|---|---:|
| `NEEDS_NEW_ISSUE_ID` | 40 |
| `NOISE_KEEP_OUT` | 4 |
| `NAO_SEI` | 2 |
| `SYNONYM_OF_EXISTING` | 1 |

**A regressão de alias rodou contra os 4,0 milhões de caracteres do corpus** e
contra uma lista de palavras comuns italianas. Rejeitou `acaro` e `lema` — este
casaria *«problema»*. Nenhum alias entra sem passar por ela.

`LEPIDOTTERI` foi rebaixado a `NOISE_KEEP_OUT` pelo desafiador: é nível de ordem,
e criar um ISSUE_ID de ordem ao lado de ISSUE_IDs de espécie mistura réguas.

## 4 · O que isto NÃO fez

`PREVIEW = NÃO FEITO`, por ordem. Nenhum portal foi tocado, nenhum `package.json`
criado, nenhuma linhagem paralela aberta. `v21_normalizar.py` não foi alterado.
