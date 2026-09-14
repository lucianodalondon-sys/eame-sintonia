# RED TEAM — A ESPINHA COMUM DA INTELLIGENCE V1

```
MISSAO     C-INT-SPINE-01
ALVO       research/intelligence/INTELLIGENCE-SPINE-CONTRACT-V1.md
ESPECIE    EVIDENCIA DE REVISAO — NAO CANONICA
MEDIDO_EM  2026-09-14
```

> Um ataque **KILLED** quando a arquitetura o derruba com lei + prova.
> **PARTIAL** quando o núcleo é verdadeiro e a parte que fica está escrita.
> **SURVIVED** quando fica de pé como argumento arquitetural — e nesse caso
> `INTELLIGENCE_SPINE_CONTRACT_READY = NO`.
>
> Um ataque que cai no argumento e sobrevive no repositório **não foi
> derrubado: foi adiado** — e vai para `PARTIAL`, com o estado nomeado.

---

# PLACAR

```
KILLED    11
PARTIAL    3
SURVIVED   0
```

Nenhum ataque sobreviveu como argumento arquitetural. Os três `PARTIAL` têm
núcleo verdadeiro, e os três são **matéria-prima ou atomicidade**, não desenho.

---

# 1 · `SIGNAL` E `FINDING` SÃO A MESMA COISA

**Tentativa.** Se um sinal já tem sujeito, tempo, lugar e espécie, ele já
afirma. Um achado é um sinal com mais campos. Dois nomes, um objeto.

**Contra-prova.**

```
SINAL   diz: esta FONTE, lida por esta REGRA, e evidencia desta ESPECIE
             sobre este SUJEITO
ACHADO  diz: ISTO E ASSIM, e aqui esta porque, o que o contradiz,
             o que o derrubaria e qual o nivel
```

O sinal herda a autoridade da fonte; o achado **assume** autoridade própria. E
a máquina não tem aresta entre os dois: há três portões no meio, e cada um sabe
recusar (`P2`, 2 testes). A prova mais dura é estrutural: `Sinal` não tem campo
`NIVEL`, não tem `TRACO_DE_DECISAO` e não tem arestas de julgamento.

```
VEREDITO  KILLED
```

---

# 2 · `CROSSING` ESTÁ A JULGAR ANTES DA HORA

**Tentativa.** Escolher a chave de junção já é julgar. Decidir que «mesma área»
significa «mesma região» é uma interpretação. Logo o cruzamento julga.

**Contra-prova.** A escolha da chave é uma **regra versionada**, não um
julgamento sobre o mundo — e o cruzamento declara a pergunta que responde
(`INT-LAW-090`). A diferença mede-se pela reversibilidade:

```
mudar a REGRA de juncao       -> recalcula-se, e o resultado muda
mudar o JULGAMENTO            -> exige causa canonica e fica na historia
```

E a prova estrutural: `Cruzamento` não tem onde escrever `APOIA`, `CONTRADIZ`,
`SUFICIENTE`, `CONCLUSAO` nem `VEREDITO`
(`P3.test_o_cruzamento_nao_tem_onde_escrever_julgamento`). O dia em que alguém
lhe acrescentar um desses campos, o teste falha — e é esse o ponto.

⚠️ **A parte do ataque que é verdade, e está escrita:** a herança de precisão
*é* uma decisão, e por isso ela **não é opcional nem configurável**: o
cruzamento herda o pior lado, sempre, e `P3.test_o_cruzamento_herda_o_pior_lado`
guarda-a.

```
VEREDITO  KILLED
```

---

# 3 · `JUDGMENT` ESTÁ A DUPLICAR A ADMISSION

**Tentativa.** A Admission já decide o que entra, com regra e versão
(`ADMITIDO_POR`). O julgamento da Intelligence é a mesma decisão, outra vez.

**Contra-prova.** São perguntas diferentes, e a fronteira está em runtime:

```
ADMISSION julga o ARTEFATO:  «isto da para conferir depois?»
                             origem · tempo · estagio · universo
JUDGMENT  julga o MUNDO:     «esta evidencia apoia ou contradiz esta hipotese?»
```

A Admission nunca liga duas evidências; o julgamento **só existe** ligando. E a
Admission não tem hipótese: não há nada, do lado dela, que possa ser apoiado ou
contradito.

A prova de que não há duplicação de dono: a Intelligence **não reescreve**
`ADMITIDO_POR`, `ITEM_ID` nem `SOURCE_ID` — o `Sinal` aponta para eles e
`ItemPronto` é `frozen`.

```
VEREDITO  KILLED
```

---

# 4 · `VALIDATION_QUEUE` VIROU FERRAMENTA DISFARÇADA

**Tentativa.** Uma fila precisa de ordem, de atribuição, de prazo. Isso é uma
ferramenta. Chamar-lhe «estado» é cosmética.

**Contra-prova — e este ataque valeu a pena, porque mudou o desenho.** A fila
**não é objeto**:

```python
def fila_de_validacao(self):
    return [h for h in self.hipoteses.values()
            if h.VALIDACAO == "PENDENTE" and h.ESTADO == "HIPOTESE"]
```

Sem tabela, sem identidade, sem persistência própria. Ordem, atribuição e prazo
**são da Delivery**, e a Delivery não pode alterar `VALIDACAO` — só a
Intelligence, e o evento fica na história com quem validou e porquê.

```
UMA FILA COM ARMAZENAMENTO PROPRIO E UM SEGUNDO DONO
DA MESMA VERDADE, A ESPERA DE DIVERGIR.
```

⚠️ E o ataque deixou uma lei que não estava escrita:
**se um dia a fila ganhar um `id`, deixou de ser uma projeção.** É o sinal a
vigiar.

```
VEREDITO  KILLED
```

---

# 5 · `FINDING` NÃO CONSEGUE VOLTAR ATRÁS

**Tentativa.** Um achado promovido é o fim da linha: os estados de reversão
existem no papel e ninguém os escreve.

**Contra-prova.** Sete causas canónicas com destino fixo, e `reverter()` recusa
qualquer causa fora da lista (`P6.test_causa_sem_nome_canonico_e_recusada`). As
quatro transições do enunciado têm origem:

```
REOPEN      NORMALIZATION_REVISED
DOWNGRADE   NO_LONGER_PRESENT · DEPENDENCY_DISCOVERED · WINDOW_CLOSED
REJECT      RECORD_INVALIDATED · SOURCE_RETRACTED
SUPERSEDE   AUTHORIZATION_CHANGED
```

E não há `CONFIRM` na lista de reversões, de propósito: reconfirmar é promover
outra vez, com evidência nova, e passa pelos mesmos portões.

```
VEREDITO  KILLED
```

---

# 6 · UMA EVIDÊNCIA NOVA APAGA A ANTERIOR

**Tentativa.** «Corrigir» é sobrescrever. O estado ativo é o que interessa; o
resto é ruído.

**Contra-prova.** `Evento` é `frozen` e `Historia` só tem `escrever()` —
não existe `apagar`, não existe `editar`. `P7` promove, reverte duas vezes e
confere a série inteira:

```
HIPOTESE -> CONFIRMADO -> REJEITADO -> REABERTO
```

E `P7.test_os_eventos_sao_imutaveis` tenta alterar um evento e falha.

O que o ataque acerta, e a lei já cobre: o **estado ativo** muda. O que ele
erra é achar que isso apaga o histórico (`INT-LAW-211`).

```
VEREDITO  KILLED
```

---

# 7 · UM MÓDULO DE DISEASE CRIA UMA SEGUNDA ARQUITETURA

**Tentativa.** Doença precisa de régua de níveis, de janela de infeção, de
fenologia. Regulatório precisa de vigência e de país. São duas máquinas.

**Contra-prova.** `P11` corre o domínio `REGULATORIO` pelos **mesmos sete
portões**, e chega a achado e a reversão. E
`P11.test_o_dominio_so_traz_dados_nunca_portoes` fecha a lista de campos de
`PacoteDeDominio` e verifica que **nenhum valor de nenhum pacote é chamável**:

```python
for valor in vars(pacote).values():
    self.assertFalse(callable(valor))
```

Um domínio traz léxico, critérios, chaves e régua. **Não traz máquina.**

⚠️ E a régua de um domínio não vale no outro: `P11.test_a_regua_de_um_dominio_nao_vale_no_outro`
tenta usar `NIVEL_2` no domínio regulatório e é recusado.

```
VEREDITO  KILLED
```

---

# 8 · `COLLECTION_GAP` CHAMA O COLETOR DIRETAMENTE

**Tentativa.** Um requisito que diz «preciso do boletim X» já é um pedido de
coleta. Basta alguém acrescentar a URL para ser mais útil.

**Contra-prova — e este é o ataque que produziu o achado da missão.** O
requisito recusa **12 palavras em código**:

```
GAP_ID · SATISFACTION_STATE · DECISION · DECISION_ID · ROTA · ROUTE ·
EXECUTOR · COLETOR · COLLECTOR · SCRAPER · API · URL · ENDPOINT · PRIORITY
```

`P10.test_o_requisito_nao_pode_nomear_rota_executor_nem_decisao` tenta as quatro
formas óbvias («chamar o coletor», «usar a API», «DECISION = COLLECT_NOW»,
«abrir a URL») e as quatro levantam `LeiViolada`.

E `P10.test_a_maquina_nao_tem_nenhuma_porta_para_coletar` lê o próprio
ficheiro e confere que não há `import requests`, `urllib.request`, `http://`,
`https://`, `subprocess` nem `socket`.

```
A INTELLIGENCE NAO CHEGA A FORMAR A FRASE QUE NOMEARIA UMA ROTA.
```

E a razão de fundo: `GAP`, `DECISION` e `ROTA` **já têm dono** —
`leis/gestao_da_coleta.py`, `GESTAO_DA_COLETA/v1`, com a fronteira escrita:
*«o gestor decide o que e quando; o orquestrador decide como e por onde»*.

```
VEREDITO  KILLED
```

---

# 9 · UMA AMBIGUIDADE EPPO VIRA MATCH EXATO

**Tentativa.** `peronospora` tem três códigos candidatos. Escolher o mais comum
é pragmático: na vinha é quase sempre `PLASVI`.

**Contra-prova.** «Quase sempre» é a definição do erro. `_resolver()` devolve
`UNRESOLVED` **com o termo original preservado**, e `P8` confere que o sujeito
não é nenhum dos três códigos. Depois, `P8.test_e_um_cruzamento_sobre_termo_ambiguo_nao_se_faz`
prova a consequência: **sem identidade resolvida, o cruzamento não se faz**
(`NOT_POSSIBLE`), porque não há chave de junção semântica.

O ataque tem um precedente medido nesta casa, e por isso não é hipotético:

```
"Sintomo di peronospora al 12,5% delle foglie..."  -> porta: SIM
"Peronospora osservata al 12,5% delle foglie..."   -> porta: NAO_SEI
MESMO FACTO · MESMO EPPO · MESMA CULTURA · MESMO VALOR
```

```
VEREDITO  KILLED
```

---

# 10 · UM DADO PÚBLICO VIRA PREVISÃO DE VENDA

**Tentativa.** Registo + pressão de doença + preço da commodity + janela = o
agricultor vai comprar. Chamar-lhe `OPPORTUNITY` de nível C é só nomear o óbvio.

**Contra-prova.** `oportunidade()` levanta `LeiViolada` para C e D quando as
fontes são só públicas, **e também quando o contrato de dado privado está
vazio** — a palavra «interno» não basta (`P12`, 4 testes). E o que separa B de
C não é esforço: é a ligação `CAMPO → OPERADOR DA TERRA`, que é privada por
construção.

```
DADO PUBLICO EXTERNO PROVA AGRONOMIA E REGULACAO.
NAO PROVA CARTEIRA, NAO PROVA CLIENTE, NAO PROVA VENDA.
```

E o pior erro, que o teste também guarda: **não declarar o nível**
(`P12.test_nivel_nao_declarado_e_recusado`). Uma oportunidade de nível A
apresentada como nível D é uma promessa que o dado não sustenta.

```
VEREDITO  KILLED
```

---

# 11 · `UNKNOWN` VIRA AUSÊNCIA

**Tentativa.** `if not valor:` é idiomático em Python. `NAO SEI` é falsy o
suficiente na prática, e o código fica mais limpo.

**Contra-prova.** `e_falso()` **levanta** em `NAO SEI` e em `None`
(`P9.test_perguntar_se_nao_sei_e_falso_levanta_lei`). E a lei atravessa três
camadas, não uma:

```
no rastreio     criterio duro em NAO SEI  -> DESCARTADO, nao «medio»
na precisao     _pior(NAO SEI, X)         -> NAO SEI, sempre
no cruzamento   area ou janela NAO SEI    -> NOT_POSSIBLE
```

`P9` tem 4 testes, um por camada mais o da função.

```
VEREDITO  KILLED
```

---

# 12 · O PORTAL APARECE COMO OWNER

**Tentativa.** O portal mostra achados; quem mostra acaba por decidir o que é
mostrável; logo o portal possui o estado.

**Contra-prova.** Nesta espinha o Portal **não aparece de todo**: não há
`CLIENT_SAFE = true` em lado nenhum (`oportunidade()` devolve sempre `false`),
não há renderização, não há ordem de apresentação. E `INT-LAW-023` já proíbe o
portal de refazer cruzamento, completar relação ausente, recalcular
independência, converter `UNKNOWN` em `PASS` ou reclassificar achado.

⚠️ O que o ataque acerta: **ordem e atribuição da fila de validação são da
Delivery**, e isso está escrito no §4.5 do contrato. Mas a Delivery não pode
escrever `VALIDACAO` — o estado vive na hipótese, e só a Intelligence o move.

```
VEREDITO  KILLED
```

---

# 13 · A MESMA DECISÃO PASSA A TER DOIS DONOS

**Tentativa.** O enunciado propõe `JUDGMENT` **e** `FINDING`, `CANDIDATE_FINDING`
**e** hipótese, `VALIDATION_QUEUE` **e** estado de validação. Três pares, três
duplicações.

**Contra-prova — e foi este ataque que definiu a forma da espinha.** Os três
pares foram fundidos, e a fusão está escrita no §2 do contrato:

```
JUDGMENT + FINDING              -> UM dono. O julgamento e o ATO; o achado e o
                                   objeto. A arbitragem V1 ja o tinha escrito
                                   como uma entrada: «FINDING / ANALYTIC_JUDGMENT»
CANDIDATE_FINDING + HYPOTHESIS  -> UM objeto, com o nome que ja existia
VALIDATION_QUEUE + VALIDACAO    -> UM estado, no objeto. A fila e projecao.
```

⚠️ **O núcleo que fica, e é real:** `COLLECTION_GAP` tinha mesmo dois donos, e
esta missão encontrou-o — mas ao contrário do que o ataque supõe. Não era a
espinha a duplicar: era um nome único a cobrir **dois** conceitos que já tinham
donos diferentes. A correção está no §4.10.

```
VEREDITO  PARTIAL — o nucleo verdadeiro esta escrito, e resolvido no §4.10
```

---

# 14 · UM ESTADO FOI CRIADO SÓ PORQUE PARECIA CONVENIENTE

**Tentativa.** `SCREENING` não estava no enunciado. `INTELLIGENCE_REQUEST` não
estava no enunciado. Foram acrescentados para a arquitetura parecer completa.

**Contra-prova, um a um:**

```
SCREENING              tem numero externo: EFSA 2017-2024, 392 pragas novas,
                       27 voltaram a ser mencionadas. ~7%.
                       Sem rastreio barato, 93% de intelligence falsa com
                       aparencia impecavel.
INTELLIGENCE_REQUEST   nao e novo: esta na arbitragem V1 com dono e estado
                       NOT_IMPLEMENTED, e no know-how §14 como «KIT/KIQ».
                       Foi RECUPERADO, nao inventado.
```

E o teste inverso — estados que **não** foram criados apesar de parecerem
convenientes: `CANDIDATE_FINDING`, `VALIDATION_QUEUE`, `EVIDENCE`, `REVERSAL`
e `JUDGMENT` como estágio. Cinco recusas contra dois acréscimos, e cada recusa
tem a razão escrita.

```
VEREDITO  KILLED
```

---

# OS TRÊS `PARTIAL`, NOMEADOS

Além do ataque 13, dois sobrevivem como **estado do repositório**, não como
argumento — e é por isso que não são `KILLED`:

## `PARTIAL-A` · O portão `G0` não recebe o dado que precisa para recusar bem

```
O ATAQUE     «clima favoravel prova doenca»
O ARGUMENTO  CAI — a regua exige OBSERVED_FIELD_SIGNAL para o nivel 1 (P1)
O ESTADO     SOBREVIVE — EVIDENCE_SPECIES nao atravessa a fronteira.
             Medido: 0 de 12 campos do contrato READY.
```

Hoje, `G0` recusa **tudo** por omissão de espécie e levanta requisito. É o
comportamento correto, e é também a prova de que a máquina está a funcionar
sobre matéria-prima que não existe.

```
UM PORTAO QUE NAO RECEBE O DADO NAO RECUSA: DEIXA PASSAR.
ESTE RECUSA POR OMISSAO — O QUE E HONESTO, E NAO E UTIL.
```

## `PARTIAL-B` · A arbitragem foi feita sobre fotografias incompletas

```
O ATAQUE     «a arbitragem de conceitos esta errada»
O ARGUMENTO  CAI para 21 dos 22 conceitos — foram lidos nos artefatos
O ESTADO     SOBREVIVE — um mudou de veredito quando re-medido contra a linha
             funcional (COLLECTION_GAP, §4.10), e NAO SE SABE se e o unico,
             porque nenhum commit contem todas as autoridades.
```

```
CONTROL_PLANE_ATOMICITY = FAIL
```

Isto **não** derruba a espinha — a espinha foi construída lendo os artefatos
onde eles vivem — mas impede que ela seja chamada canónica, e é exatamente o
que a próxima missão tem de fechar.

---

# VEREDITO

```
SPINE_V1 = COERENTE, E SUFICIENTE PARA IMPLEMENTAR INTELLIGENCE_RUN
ATAQUES SOBREVIVENTES COMO ARGUMENTO = 0
IMPLEMENTACAO = NAO AUTORIZADA
PROMOCAO A CANONICO = BLOQUEADA POR CONTROL_PLANE_ATOMICITY
```

```
INTELLIGENCE_SPINE_CONTRACT_READY = YES
```

O mais valioso deste red team foi o ataque 8. Ele ia ser `KILLED` por citação
de lei — `INT-LAW-020`, «volta pela Collection canónica» — e em vez disso
obrigou a ir ler quem já possuía o conceito. Encontrou `GESTAO_DA_COLETA/v1`, e
com ele a prova de que `COLLECTION_GAP` nunca foi um conceito só.

```
UM ATAQUE QUE SE DERRUBA CITANDO A LEI NAO FOI ATACADO.
FOI RESPONDIDO.
```
