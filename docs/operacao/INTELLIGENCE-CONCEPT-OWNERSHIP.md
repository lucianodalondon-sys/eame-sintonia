# MATRIZ DE CONCEITOS E DONOS — INTELLIGENCE

```
MISSAO     C-INT-CENSUS-01 · 2026-09-13
MEDIDO EM  claude/raw-observation-identity-3jbwco @ 84186dfa
```

> Evidência de auditoria. A contagem é de **ficheiros que tocam o conceito**,
> excluindo o próprio System Map e a sua cópia no cliente — o mapa a falar de uma
> peça não é a máquina a usá-la.

---

## A LEI QUE ESTA MATRIZ MEDE

```
ONE CONCEPT → ONE OWNER
```

E a pergunta que ela responde não é «quem menciona?», é **«quem decide?»**.

---

## A MATRIZ

| conceito | ficheiros | maior massa | dono provado | colisão |
|---|---|---|---|---|
| `EVIDENCE` | 327 | `data` 49 · `tests` 39 | **NÃO SEI** | — |
| `SIGNAL` | 301 | `data` 54 · `docs` 53 | **NÃO SEI** | — |
| `LABEL` | 267 | `data` 45 · `italia-portale` 38 | **NÃO SEI** | — |
| `PORTFOLIO` | 218 | `italia-portale` 85 | ENTREGA (por massa) | — |
| `OPPORTUNITY` | 186 | `italia-portale` 50 · `build` 29 | `C-V21-OPORTUNIDADE` disputa com a ENTREGA | **SIM** |
| `FINDING` | 188 | `docs` 42 · `data` 21 | **NÃO SEI** | — |
| `SCIENCE` | 179 | `italia-portale` 51 | ENTREGA (por massa) | — |
| `RELEVANCE` | 157 | `italia-portale` 37 | **NÃO SEI** | — |
| `PRIORITY` | 126 | `docs` 34 · `data` 33 | **NÃO SEI** | — |
| `CROSSING` | 120 | `docs` 23 · `motor` 16 | `C-V21-CRUZAMENTO` | não |
| `CONFIDENCE` | 108 | `italia-portale` 21 | **NÃO SEI** | — |
| `CONVERGENCE` | 78 | `italia-portale` 19 | **NÃO SEI** | — |
| `VALIDATION` | 58 | `italia-portale` 23 · `motor` 5 | **NÃO SEI** | — |
| `FUTURE_SIGNAL` | 54 | `italia-portale` 27 | ENTREGA (por massa) | — |
| `FACT / CLAIM` | 50 | `build` 11 · `docs` 9 | `C-V21-INGEST` (`v21_dominio_da_alegacao.py`) | não |
| `DISEASE_PRESSURE` | 12 | `build` 4 | **NÃO SEI** | — |
| **`COLLECTION_GAP`** | **0** | — | **NÃO EXISTE** | — |
| **`INTELLIGENCE_RUN`** | **0** | — | **NÃO EXISTE** | — |

---

## AS DUAS COLISÕES PROVADAS

### COLISÃO 1 · O GERADOR CANÓNICO TEM DOIS NOMES

```
CONCEITO          gerador canonico da inteligencia
OWNER_CANDIDATES  claude/acervo-to-package-intelligence-v1 @ 51010733
                  claude/opportunity-commercial-priority-v1 @ 55c2674
COLLISION         YES
```

| onde | diz |
|---|---|
| `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json` | `51010733` |
| `motor/v21_cadeia.sh:35` e `:47` | `55c2674` |

E o contrato lista a safra de `55c2674` — `V21-69bf448ac934a6d9` — entre as
`STALE_KNOWN_BUILD_IDS`.

```
PROVEN_OWNER = o contrato.
```

Não por ser mais simpático, mas porque **é ele que o portão executa**: `build-gate.mjs`
lê `CONTRATO.EXPECTED_BUILD_ID` e recusa o resto — medido a correr, 2/2 PASS. O
cabeçalho da cadeia é prosa; o contrato é executado.

```
ENTRE DOIS DOCUMENTOS QUE DISCORDAM, GANHA O QUE UM PORTAO LE.
```

**Consequência prática:** quem seguir a instrução da cadeia gera um pacote que o
portão recusa. Documentado, não corrigido.

### COLISÃO 2 · OPPORTUNITY É CALCULADA NUM SÍTIO E DECIDIDA NOUTRO

```
CONCEITO          OPPORTUNITY
OWNER_CANDIDATES  C-V21-OPORTUNIDADE (motor/v21_oportunidades.py, v21_fechar.py)
                  italia-portale (50 ficheiros)
                  build/ (29 ficheiros, artefactos congelados)
COLLISION         YES
```

O motor calcula; a Entrega carrega a maior massa do conceito; e `build/` guarda
safras congeladas que ainda o afirmam. Três camadas com voz sobre a mesma palavra.

`PROVEN_OWNER = NÃO SEI` — e é NÃO SEI de propósito. Distinguir «quem calcula» de
«quem apresenta» de «quem congelou» exige ler as três camadas, e isso é trabalho de
arbitragem, não de censo.

---

## O QUE ESTA MATRIZ NÃO PROVA

```
NAO_SEI  a maioria dos conceitos nao tem dono PROVADO, e a matriz diz NAO SEI
         em vez de eleger o candidato com mais ficheiros. Contar ficheiros mede
         MASSA, e massa nao e propriedade.

         UM CONCEITO ESPALHADO POR 327 FICHEIROS NAO TEM DONO POR MAIORIA.
```

Os dois zeros — `COLLECTION_GAP` e `INTELLIGENCE_RUN` — são o achado mais limpo
desta matriz: a Intelligence desta árvore **não tem noção de corrida própria**, e
não sabe nomear um buraco de coleta. Quando existir Intelligence canónica, esses
dois conceitos nascem do zero.
