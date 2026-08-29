# PROTOCOLO DO BENCHMARK — escrito ANTES de rodar

**Data:** 2026-08-29 · **MISSÃO 10**

> Este arquivo é **pré-registrado**: foi commitado antes de qualquer execução, e o commit
> anterior ao dos resultados prova isso. Nada aqui pode ser reescrito depois de ver o
> resultado — nem a pergunta, nem os campos, nem o critério de sucesso.

---

## B1 · A PERGUNTA

> **Quais autorizações espanholas entram na janela de 6 meses a partir de 29/08/2026,
> agrupadas por titular, substância e cultura quando disponível?**

## CAMPOS DE SAÍDA EXIGIDOS

```
TOTAL_IN_WINDOW              contagem de registros vigentes com caducidade em [29/08/2026, 28/02/2027]
BY_HOLDER                    contagem por titular (entidade legal, não grupo)
TOP_HOLDERS                  os 10 maiores, com contagem
ADAMA_IN_WINDOW              contagem do titular ADAMA
BY_SUBSTANCE                 contagem por substância do formulado
CROP_COVERAGE                para quantos registros da janela a cultura está disponível,
                             e por qual rota
DENOMINATOR                  total de registros vigentes usado como denominador
REFERENCE_DATE               29/08/2026, explícita
```

## CRITÉRIO DE SUCESSO

Uma rota **conclui** quando produz **todos** os oito campos acima com números que
batem com a fonte. Uma rota que produz sete campos **não concluiu**.

## CONDIÇÃO DE PARADA

- **Rota A (manual):** para em **90 minutos de relógio** ou quando concluir. Se parar por
  tempo, registra-se **até onde chegou** — e isso é o resultado, não uma falha do teste.
- **Rota B (Sintonia):** para quando concluir ou quando uma cadeia falhar fechado.

## O QUE É PROIBIDO NA ROTA A

Usar `scripts/metricas_canonicas.py`, `scripts/chain.py`, `scripts/mapa_regfi.py`,
qualquer amostra em `data/samples/` **já derivada**, ou qualquer documento do repositório
que já contenha a resposta. A rota A começa **na fonte**.

**Permitido na rota A:** o snapshot bruto arquivado
(`data/samples/ES-T4-005/ropf_20260829.json.gz`) **como se fosse o arquivo baixado da
fonte** — porque baixá-lo de novo mediria a rede, não o trabalho. Esta escolha é declarada
aqui, antes de rodar, e **beneficia a rota A**.

## O QUE É MEDIDO — passos, não só relógio

Tempo varia com a rede. Passos são reproduzíveis. As duas rotas registram:

```
ELAPSED_SECONDS         relógio
SOURCE_TOUCHES          quantas vezes a fonte/o snapshot foi aberto
MANUAL_TRANSFORMATIONS  filtros, parses, agrupamentos escritos à mão
JUDGMENT_STEPS          decisões que exigiram critério humano
FILES_OPENED            arquivos distintos abertos
RECONCILIATIONS         vezes que dois números tiveram de ser conciliados
ERROR_OPPORTUNITIES     pontos onde um erro silencioso era possível
ERRORS_MADE             erros efetivamente cometidos e corrigidos
COVERAGE                fração dos oito campos entregues
```

## AMBIENTE DECLARADO

Mesmo contêiner, mesmo disco, mesmo Python. **O download não é contado em nenhuma das
duas rotas** — ambas partem do snapshot já em disco. Sem cache de resultado em nenhuma
das duas.

## VEREDITO DE VALIDADE

Se a comparação for injusta em qualquer direção — pergunta alterada no meio, download
contado só de um lado, rota A sabotada — o resultado é **`INVALID BENCHMARK`** e não
entra em nenhum documento de produto.

---

# B2 · SEGUNDO BENCHMARK (só se houver tempo)

> **Onde a ADAMA deveria investigar prioridade de doença do olivar na Andaluzia, usando
> apenas evidência externa?**

**A pergunta de interesse não é a resposta — é a ORDEM.** Registra-se:

```
FIRST_PRIORITY_BEFORE_AREA   qual província a rota elege antes de considerar área
FIRST_PRIORITY_AFTER_AREA    qual elege depois
DID_THE_ORDER_CHANGE         sim/não
LIMITATIONS_STATED           quais limitações cada rota declarou espontaneamente
```

**Proibido induzir.** A rota A não recebe a dica de que a área existe. Se o analista da
rota A nunca procurar área, isso é **o resultado** — e é exatamente a hipótese em teste.
