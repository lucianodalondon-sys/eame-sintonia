# LEIA ISTO PRIMEIRO

**Pacote:** SINTONIA ITALY PILOT — REALITY HANDOFF
**Montado em:** 2026-09-02 · **Para:** o Claude que vai desenhar o portal do piloto italiano

---

## 1 · O que é o piloto Sintonia Itália

O Sintonia é uma ferramenta de inteligência para a ADAMA — multinacional de proteção de
cultivos. Ele lê o que o mundo agrícola diz em público (registro oficial, boletim de campo,
ciência, imprensa técnica, anúncio de concorrente, vídeo, comentário) e mostra **onde
apontar atenção humana escassa**.

O piloto italiano é uma **demonstração**, e a regra que o define é esta:

> **CAMADA OPERACIONAL SIMULADA + MUNDO AGRÍCOLA REAL.**

Pode ser simulado: notificação, fluxo, mensagem de Field Sales, geração de Action Brief,
atividade de interface.

**Não pode ser inventado:** produto ADAMA, cultura, alvo, autorização, pesquisador, artigo
científico, concorrente, doença, praga, daninha, evento, notícia, janela, pessoa real,
conversa pública real.

O objetivo **não é** construir um universo agrícola. É demonstrar como o Sintonia opera,
usando o **máximo de material italiano real** que existir.

---

## 2 · O que é REAL neste pacote

Cada objeto carrega `PROVENANCE`:

| valor | significa |
|---|---|
| `REAL_FACT` | fato oficial: rótulo autorizado, ato jurídico, decreto regional |
| `REAL_SOURCE` | veio de fonte primária pública que foi lida |
| `REAL_DERIVED` | derivado por nós de material real, declarado como derivação |
| `SYNTHETIC_DEMO` | inventado para demonstrar a experiência |
| `INTERNAL_DATA_REQUIRED` | só existe se a ADAMA conectar dado interno |
| `NOT_YET_PROVABLE` | plausível e sem lastro suficiente |

⚠️ **Neste pacote não há um único objeto `SYNTHETIC_DEMO`.** É de propósito: o que precisa
ser sintético é trabalho do Design, e vai nascer marcado como tal.

---

## 3 · O que ler primeiro

```
1  00-START-HERE/EXECUTIVE-SUMMARY.md          o projeto em 5 minutos
2  00-START-HERE/WHAT-TO-USE-IN-THE-PORTAL.md  as quatro gavetas
3  00-START-HERE/REALITY-COUNTS.md             os números, contados
4  05-GAPS-AND-LIMITS/DO-NOT-CLAIM.md          ANTES de escrever texto de tela
5  05-GAPS-AND-LIMITS/KNOWN-GAPS.md            o que falta, e com que estado
6  01-DESIGN-READY/                            os dados, por camada
7  01-DESIGN-READY/RELATIONSHIPS/              como os objetos se ligam
```

---

## 4 · O que você NUNCA pode afirmar

```
⛔ «a ADAMA não tem produto para <alvo> em <cultura>»
     A cobertura de uso lido é 19 de 163 (11,7%). Falta LEITURA, não registro.
     É a frase mais perigosa do sistema inteiro.

⛔ «o produtor italiano relatou»
     Comentário de YouTube é PLATEIA DAQUELE CANAL. E 32 das 58 vozes italianas
     vêm de canal de HORTA DOMÉSTICA — falam de roseira e limoeiro.

⛔ «o anúncio foi dirigido à Itália»       a Meta diz que ALCANÇOU.
⛔ «há resistência» / «o produto falhou»   só com base oficial; falha não tem dono.
⛔ «o problema está aumentando na Itália»  6 regiões de 20, e nenhuma fala pelo país.
⛔ vendas · share · estoque · demanda      exige dado interno da ADAMA.
⛔ «X vai participar da feira Y»           futuro nunca se infere de passado.
```

Lista completa e comentada em `05-GAPS-AND-LIMITS/DO-NOT-CLAIM.md`.

---

## 5 · As leis semânticas que o pacote inteiro obedece

1. **A unidade de saída é o par `cultura × alvo`** — nunca o documento, nunca a fonte
2. **Contagem bruta não é sinal de alta** — só proporção, entre janelas comparáveis
3. **O par é INFERIDO pelo sistema** — cultura e alvo são observados; a ligação é nossa
4. **Campo vazio sai como NÃO SEI**, jamais como «não há»
5. **`NOT_OBTAINED` ≠ `DOES_NOT_EXIST`** — cobertura é sempre um piso
6. **Porta ausente ≠ rendeu zero**
7. **`CROP_TERM_PRESENT` ≠ `AUTHORIZED_ON_CROP`**
8. **Título casado ≠ ato lido**
9. ⭐ **Relato em primeira pessoa sobre um vaso não é voz de lavoura**
10. ⭐ **Fonte bloqueada por IP não é fonte inexistente** — é problema de rota

---

## 6 · Três descobertas que mudam a leitura

**A data de 2027 não é administrativa.** O acervo dizia *«EXPIRY ≠ WITHDRAWAL: re-registro
é rotina»*. Verdadeiro para uma camada só. A aprovação **europeia** do tau-fluvalinate
expira **na mesma data** dos 7 produtos ADAMA que o contêm, e o ato que a estendeu registra
que a avaliação de risco **não foi finalizada**.

**A ISMEA não está fora do ar — ela nos recusa.** `GEO_IP_BLOCK` para o nosso IP; responde
301 normal de Milão, Berlim, Helsinque e Miami. O Market Pulse italiano exige rota de saída
europeia.

**Nem toda voz de campo é voz de lavoura.** 24 falas de plateia profissional contra 32 de
horta e jardim doméstico. As duas classes não se somam.

---

## 7 · Onde o dado bruto ficou

O pacote é uma **seleção curada**, não um despejo. O bruto pesado continua no repositório e
está indexado em `01-DESIGN-READY/ARCHIVE/archive-index.json`, com caminho e branch.

⚠️ Vários datasets vivem em **branches diferentes** da mesma origem. O índice diz qual.
