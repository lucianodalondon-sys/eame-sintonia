# HANDOFF — LABEL INTELLIGENCE · para o acoplamento de amanha

Este documento existe para uma coisa so: amanha, quem for acoplar a Label
Intelligence ao SINTONIA EAME nao precisar reabrir a investigacao. Tudo aqui foi
medido nesta arvore, nao lembrado.

    STANDALONE_TOOL      = YES
    OFFICIAL_INTEGRATION = NO   (decisao do dono: nao acoplar hoje)
    DEPLOY               = NO
    PORTAL_TOUCHED       = NO

## 1 · Identidade

    BRANCH           claude/label-intelligence-v1-italy
    BASE             main
    ARTEFATO         v1/casco/label-intelligence.html   (arquivo unico, ~3,9 MB)
    PAYLOAD          v1/dados/CASCO-PAYLOAD.json        (embutido no HTML, selado)
    REGRAS           v1/inteligencia/REGRAS.md          (R-01 a R-22, C-*, N-*, P-*, T-*, G-*)
    PORTOES          v1/testes/test_portoes.py          -> v1/testes/RESULTADO-PORTOES.json

O HEAD, o REMOTE_HEAD, a contagem de portoes e o estado da arvore desta entrega
estao no commit que traz este arquivo — leia-os do `git log` e do
`RESULTADO-PORTOES.json`, e nao daqui: numero copiado a mao neste projeto ja
envelheceu calado duas vezes, e o portao `MEASURED_CONSTANTS_ARE_MEASURED`
nasceu disso.

## 2 · Como consumir, hoje

A ferramenta e um HTML unico com o payload embutido. Abre no navegador, local,
sem servidor, sem build, sem rede. Para consumir programaticamente, o payload
esta em `v1/dados/CASCO-PAYLOAD.json` e e byte-identico ao que esta dentro do
HTML — o portao `DELIVERED_HTML_CARRIES_THE_VERSIONED_PAYLOAD` confere isso a
cada execucao.

Reconstrucao a partir de um clone limpo esta medida em `v1/ACESSO-A-FONTES.md`:
os 13 artefatos carregam o sha256 do modulo que os produziu, as 223 fontes
primarias batem o sha256 do manifesto versionado, e `payload.py` + `build.sh`
devolvem o HTML byte a byte. O acervo primario (272 MB de CSV oficial + os PDFs)
NAO esta no git; `v1/fonte/recoletar.py` o rebaixa e confere.

## 3 · Capacidades prontas

| capacidade | o que responde | prova que a acompanha |
|---|---|---|
| rotulos oficiais | 166 produtos do registro italiano, com titular, estado, substancias, validade | `pdf_sha`, `snapshot_sha`, `source_url` por produto |
| cultura x alvo | 2.873 pares de uso publicados | `pair_check` (R-14), `crop_name` (R-21), `target_name` (R-17) |
| o selo mais forte | 1.324 pares (46,1%) saem como `FATO` | a formula exige tres colunas — par provado pela geometria (R-14), nome da cultura (R-21) e nome do alvo (R-17) escritos no documento. **Medido: hoje R-14 sozinha da os mesmos 1.324**; as outras duas sao guardas que ainda nao precisaram disparar. Quem for acoplar deve ler `fact` como "R-14 disse sim", nao como "tres testes independentes disseram sim" |
| dose quando provada | 510 linhas de dose | R-11 (cultura da linha), R-12 (teto fora da tabela), R-13 (alvo literal), R-15 (herdados), R-22 (fio dentro da banda) |
| historico / diff | 210 objetos de mudanca, 54 versoes | dois instantaneos oficiais arquivados, campo a campo (R-01 a R-08) |
| alertas quando provados | janelas T-01 a T-09 | so com data na fonte; `ACT_NOW` significa **olhe hoje**, nunca "pare de vender" |
| busca | por produto, cultura, alvo, substancia | a coluna "onde casou" mostra em que campo bateu |
| proveniencia | toda afirmacao material tem rota ate um documento em disco | portao `EVIDENCE_ROUTE_REACHES_A_REAL_DOCUMENT` confere que o arquivo existe e o sha256 bate |
| citacao | 4.261 frases com o verbo "o rotulo escreve" | R-18: cada uma reencontrada no `pdftotext` do PDF oficial pelo portao `QUOTED_TEXT_IS_IN_A_FLAT_READING` |
| regras | R-01 a R-22 escritas, com o portao da tela declarado | portao `UI_RULE_IDS_ARE_DEFINED_IN_REGRAS`: toda regra citada pela interface existe no documento |

## 4 · Limitacoes declaradas — leia antes de acoplar

Estas nao sao bugs abertos por descuido: sao recusas de afirmar, e cada uma tem
nome proprio na tela.

1. **`R-22` e conservadora demais.** Das 10 bandas que ela reprova, um arbitro
   independente verificou no papel que **8 sao dose correta** — cultura, alvo e
   numero do mesmo lado do fio. A tela esconde 8 doses que provavelmente estao
   certas. Erra para o lado de nao publicar.
2. **`R-22` e cega em pagina de duas tabelas.** O denominador de cobertura do
   fio e a bbox das palavras da banda; numa folha de duas tabelas nenhum fio de
   uma tabela so alcanca 60% disso. Ou seja, e justamente onde o risco de fusao
   e maior que ela nao dispara.
3. **`FUSION_DETECTOR = NOT_IMPLEMENTED`.** R-13 acusa o sintoma e R-14 retira o
   par quando a geometria o contradiz, mas nenhum separa alvo quebrado entre
   colunas de alvo fundido.
4. **Cobertura nao e uma so.** Sao 7 coberturas separadas, de proposito.
   `CROP_BLOCK_IN_VOCABULARY_NOT_READ` = 147 celulas cujo nome ESTA no
   vocabulario e mesmo assim nao viraram par.
5. **222 nomes de alvo vem de taxonomia**, nao do documento
   (`TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL`), e 21 nomes de cultura idem
   (`CROP_NAME_NOT_IN_LABEL`). Nenhum deles fecha `FATO` — mas nenhum deles e
   derrubado POR ESSA razao: todos ja caem por `R-14` antes. Ver a nota do selo
   `FATO` acima.
6. **`PHI_PROVED = 0`** — o portao `G-02` esta fechado e nenhum `PHI_CHANGE`
   pode ser emitido nesta versao.
7. **Nenhuma regra `B-*` existe**, entao
   `POTENTIAL_BUSINESS_IMPLICATION = NOT_PROVED` em todos os 210 objetos.
8. **`ACTION` nao e emitida.** O maximo e `RECOMMENDED_REVIEW`.
9. **O passo de manifesto de leitura fica PULADO** sem `sintonia/canonical`
   apontado — isso e passo nao executado, e NAO "nenhum rotulo mudou".

## 5 · O que a integracao vai precisar consumir

Nao implementar hoje. Amanha, o minimo:

    products[]        reg, name, holder, status, actives, expiry, pdf_sha, source_url
    products[].uses[] crop, target, fact, proof, pair_check, crop_name, target_name,
                      crop_scope, crop_scope_other_owner, crop_raw_state, target_raw_state
    products[].doses[] crop, target, dose_ha, dose_conc, band_check, crop_check,
                      quote, crop_cell_state, target_cell_state
    objects[]         o evento de mudanca, com RULE_ID e PROOF_STATE
    coverage          as 7 coberturas separadas — nunca colapsar num numero so
    PRODUCED_BY       MODULE_SHA256 + CONTENT_SHA256 do payload

Duas obrigacoes que viajam com o dado, e nao sao opcionais:

* **todo token de ignorancia tem de continuar visivel com o proprio nome.**
  Sao 45 tokens distintos na tela hoje. Trocar qualquer um por `-`, `0`, `N/A`
  ou celula vazia quebra a lei zero, e ha portao para isso
  (`UNKNOWN_HIDDEN_OR_FILLED`, `UNKNOWN_VISIBLE`);
* **nenhuma frase pode ganhar aspas sem `QUOTE_VERBATIM`.** O verbo "o rotulo
  escreve" e a afirmacao mais forte da ferramenta.

## 6 · Contrato de acoplamento

A Label Intelligence e uma capacidade independente:

    LABEL_INTELLIGENCE

Ela responde: **o que o rotulo oficial ADAMA autoriza, como esta estruturado e
o que mudou.**

Ela **nao** responde, e nao pode ser feita responder por juncao:

    SCIENTIFIC_INTELLIGENCE
    DISEASE_INTELLIGENCE
    OPPORTUNITY
    COMPETITOR_INTELLIGENCE

O SINTONIA pode navegar e cruzar com ela. O que nao pode e fazer uma dessas
familias virar a outra — em particular, **uso autorizado nao e oportunidade
comercial**, e o portao `G-01` continua fechado: a ferramenta nunca envia nada
ao campo sozinha.

## 7 · Design

Nao redesenhar hoje. Quando houver integracao visual amanha, consultar PRIMEIRO
o ADAMA Design System oficial no Claude Design, conforme `CLAUDE.md`. Hoje a
demo funcional existente fica como esta.
