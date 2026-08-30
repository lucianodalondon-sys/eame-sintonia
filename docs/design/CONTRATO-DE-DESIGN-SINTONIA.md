# Contrato de design — SINTONIA

`captured_at = 2026-08-30` · entrada: `SPAIN-DEMO-CONTENT-V1` (freeze V1.1)

> Este documento é contrato, não tela. Ele diz o que a interface **tem que** mostrar e o que ela **não pode** deixar acontecer. Nenhuma decisão visual pode revogar uma linha daqui.

---

## 1 · A lei do produto

O Sintonia não existe para dizer "aja". Existe para dizer **o que se sabe, com que idade, e o que isso autoriza**.

Por isso o design tem uma função invertida em relação a um dashboard comum:

> **Não use design para esconder incerteza. Use design para torná-la visível.**

Um dashboard esconde `NÃO SEI` porque ele estraga a composição. Aqui `NÃO SEI` é conteúdo de primeira classe e ocupa espaço.

---

## 2 · As quatro distinções que a tela pode matar

Cada uma já custou um erro real neste projeto. Uma tela que as apague desfaz o trabalho de cinco rodadas.

| # | Distinção | Como a tela mata | Como a tela protege |
|---|---|---|---|
| 1 | `WINDOW_OPEN` ≠ `CURRENT_NEED` | badge verde "janela aberta" ao lado de um botão de ação | janela e necessidade em **campos separados**, com rótulo próprio; `PRODUCT_ACTION_NEED = NOT_KNOWN` visível no mesmo bloco |
| 2 | `SEASON_SIGNAL` ≠ `CURRENT_SIGNAL` | número grande "8,83%" sem data ao lado | **idade do dado ao lado do número**, sempre, na mesma linha visual |
| 3 | `GEOGRAPHIC_ADJACENCY` ≠ `NETWORK_COVERAGE` | mapa que pinta as ADV cobrindo o território aragonês | rede desenhada **no seu próprio território**, com legenda dizendo o nível medido |
| 4 | `REGISTRATION` ≠ `COMMERCIAL_AVAILABILITY` | produto listado como se estivesse à venda | resposta regulatória rotulada como registro, e `COMMERCIAL_CLOCK = NÃO SEI` no mesmo cartão |

---

## 3 · Três tipos de conteúdo, três tratamentos visuais

Nunca no mesmo estilo:

- **FATO** — vem de fonte, com caminho de evidência. Peso normal, cor de texto padrão, sempre com origem clicável.
- **INTERPRETAÇÃO** — leitura minha sobre fatos. Marcada, recuada, com verbo de leitura ("a convergência sugere"). Nunca em número grande.
- **AÇÃO** — o que alguém pode fazer. Só aparece com `ACTION_TYPE` explícito e nunca sem `EVIDENCE` e `MISSING` no mesmo bloco.

E um quarto, que não é conteúdo e sim ausência:

- **NÃO SEI / NOT_COLLECTED / NOT_KNOWN** — mesmo peso tipográfico do fato. Nunca cinza-claro, nunca em rodapé, nunca colapsado por padrão.

---

## 4 · Arquitetura de informação

```
PAÍS  (ES · IT · FR)              cada país é um produto completo
 └── CASOS                        3 na Espanha, 3 na Itália, 0 na França
      └── CASO
           ├── O QUE ESTÁ ACONTECENDO   fato + data de observação + idade
           ├── ONDE                     região, com o nível da medida declarado
           ├── ESCALA                   área, com fonte e unidade
           ├── RELÓGIOS                 agronômico · observação · comercial
           ├── JANELA                   aplicação vs monitoramento, separadas
           ├── NECESSIDADE ATUAL        pode ser NOT_KNOWN, e frequentemente é
           ├── RESPOSTA ADAMA           registrada · pública (NOT_COLLECTED)
           ├── CONCORRENTE              registrado · público (NOT_COLLECTED)
           ├── CIÊNCIA E PESSOAS        com estado de identidade
           ├── FATOS / INTERPRETAÇÕES / DESCONHECIDOS   três listas separadas
           ├── MAPA DE AÇÃO             6 funções × 6 estados
           └── EVIDÊNCIA                caminhos reproduzíveis
CAMADA EAME                        existe, e hoje mostra zero relações
```

A camada EAME **aparece mesmo vazia**. Esconder que ela está vazia seria a mesma mentira que esconder um `NÃO SEI`.

---

## 5 · Inventário de componentes

| Componente | O que carrega | Regra dura |
|---|---|---|
| `CaseHeader` | país, cultura, issue, região, `CASE_TYPE` | `CASE_TYPE` nunca aparece como "AGIR AGORA" sem objeto direto |
| `SignalBlock` | valor, unidade, data de observação, idade em dias, suporte amostral | magnitude e suporte amostral em **campos distintos**; nunca se compensam |
| `ClockRow` | agronômico, observação, comercial | `NÃO SEI` renderizado igual aos outros dois |
| `WindowBlock` | janela de aplicação, janela de monitoramento, status, necessidade atual | os quatro campos sempre presentes; nenhum omitido por estar vazio |
| `ResponseCard` | registro, titular, estado, caducidad, alvo explícito vs genérico | `EXPLICIT` e `GENERIC` são rótulos visuais diferentes |
| `EvidenceLink` | caminho, fonte, versão, data de captura | todo número tem um |
| `UnknownList` | lista de desconhecidos | mesmo peso do bloco de fatos |
| `ActionMatrix` | 6 funções × `ACTION_TYPE` | `ACT_NOW` sem `EVIDENCE` não renderiza |
| `CountrySwitch` | ES · IT · FR | mostra o estado do país, inclusive `NOT_READY` |
| `CrossMarketPanel` | relações EAME | renderiza vazio com o motivo, não some |

---

## 6 · Sistema visual

**ADAMA Design System.** Corporativo `#009845` · `#00783F` · `#978B87`. LL Brown primária, Aleo como acento técnico, Arial como fallback de escritório. A Shape correto, logo ADAMA completo. Não inventar marca.

Cores de produto **somente quando semanticamente corretas** — nunca para decorar um estado.

Semântica de cor, e ela é restrita:

- verde corporativo = identidade da marca, **não** "está tudo bem"
- um estado nunca é comunicado só por cor: cor + rótulo textual, sempre
- `ACT_NOW` não ganha vermelho de alarme. Há **um** `ACT_NOW` em dezoito linhas e ele é regulatório interno

Espaço em branco generoso. Sem dashboard genérico, sem KPI tiles, sem gauge.

---

## 7 · Proibições

A tela não pode:

1. mostrar um botão de ação ao lado de `PRODUCT_ACTION_NEED = NOT_KNOWN`;
2. mostrar número de campo sem a idade do dado na mesma linha;
3. renderizar `NOT_COLLECTED` como `0` ou como espaço vazio;
4. renderizar `EXPLICIT_SPECIES_RESPONSE = NONE` de forma que se leia "a ADAMA não tem produto";
5. mostrar afirmação de fabricante com o mesmo peso de fato regulatório;
6. colapsar `UNKNOWNS` por padrão;
7. exibir qualquer número econômico;
8. mostrar a camada EAME como se tivesse conteúdo.

---

## 8 · Teste adversarial obrigatório

Antes de qualquer protótipo ser aceito, oito perguntas. Uma resposta "sim" reprova.

1. Ela faz `window open` parecer "aplique agora"?
2. Ela esconde que o dado de campo está velho?
3. Ela faz `NONE explicit response` parecer "a ADAMA não tem produto"?
4. Ela faz adjacência parecer cobertura?
5. Ela mostra claim de fabricante como fato?
6. Ela esconde `NOT_KNOWN`?
7. Ela sugere disponibilidade comercial?
8. Ela mostra a camada EAME como se tivesse relações?
