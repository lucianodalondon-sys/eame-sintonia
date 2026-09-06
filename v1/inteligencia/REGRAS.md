# REGRAS DE INTERPRETACAO E ROTEAMENTO

Toda afirmacao derivada desta ferramenta nasce de uma regra escrita aqui, com
identificador. Nenhum roteamento nasce de bom senso. O que nenhuma regra cobre
sai como `UNKNOWN`, e `UNKNOWN` aparece na tela.

## 1 · As cinco camadas, que nunca se misturam

| camada | quem produz | pode ser inventada? |
|---|---|---|
| `FACT` | a fonte oficial | nunca |
| `DERIVED_REGULATORY_MEANING` | regra `R-*` sobre o FACT | so por regra escrita |
| `POTENTIAL_BUSINESS_IMPLICATION` | regra `B-*`, e sempre rotulada como potencial | so por regra escrita |
| `RECOMMENDED_REVIEW` | regra `V-*` — pede olhar humano, nao afirma nada | so por regra escrita |
| `ACTION` | **nenhuma regra automatica** | **nunca** |

`ACTION` nao e emitida por esta ferramenta. O parser nao produz acao. O maximo
que a ferramenta faz e `RECOMMENDED_REVIEW`, que e um convite a olhar.

## 2 · Leis que nenhuma regra pode violar

    DOCUMENT_CHANGED        != REGULATORY_MEANING_CHANGED
    SOURCE_REORDER          != LABEL_CHANGE_EVENT
    EXPIRY                  != WITHDRAWAL
    PARSER_FAILURE          != REGULATORY_ABSENCE
    CATALOG_PRESENCE        != MARKET_PRESENCE
    LABEL_CHANGE            != MARKETING_CLAIM_CHANGE
    EXPIRY_EVENT            != DEMAND_DROP / STOCK_RISK / STOP_SELLING

## 3 · Regras de significado regulatorio (`R-*`)

| id | condicao (FACT) | significado derivado | prova |
|---|---|---|---|
| `R-01` | `data_scadenza_autorizzazione` mudou entre dois instantaneos oficiais | a validade declarada da autorizacao mudou | dois CSV oficiais arquivados, campo a campo |
| `R-02` | `stato_amministrativo` mudou | o estado administrativo declarado mudou | idem |
| `R-03` | registro presente em B e ausente em A | produto passou a constar no registro | idem |
| `R-04` | registro presente em A e ausente em B | produto deixou de constar entre ativos | idem |
| `R-05` | `ragione_sociale` mudou | o titular declarado mudou | idem |
| `R-06` | `sostanze_attive` mudou apos normalizacao multivalorada | a composicao declarada mudou | idem |
| `R-07` | `data_decreto_revoca` / `data_decorrenza_revoca` mudou | houve ato de revoga com data | idem |
| `R-08` | sha256 do PDF da etichetta mudou entre duas capturas | o documento do rotulo mudou | dois PDFs com hash distinto |
| `R-09` | validade oficial ja passou e o estado nao e Revocato/Scaduto | a data de validade passou **e o registro segue listando o produto como autorizado** | um campo do CSV vigente |
| `R-10` | `EXCLUSION_IS_NOT_PERMISSION` — uma cultura cujo unico apoio textual no rotulo esta **dentro** de uma janela de exclusao (`ad esclusione di`, `escluso/a/i/e`, `ad eccezione di`, `tranne`, `eccetto`) nao pode ser publicada como uso autorizado | o leitor de uso reusado nao modela escopo negativo. Medido: em `002983` e `013405` toda ocorrencia da raiz `cilieg` esta dentro de "Pomodoro (ad esclusione di Pomodoro ciliegino)", e mesmo assim `CILIEGIO x OIDIO` saia como uso autorizado — uma exclusao de tomate cereja virou permissao de cerejeira |

`R-09` e a unica que exige nota permanente na tela: **vencer nao e ser revogado.**
A ferramenta mostra os dois campos e nao conclui saida de mercado.

## 4 · Regras de ruido (`N-*`) — o que NAO vira evento

| id | padrao | por que nao e mudanca |
|---|---|---|
| `N-01` | campo multivalorado com os mesmos itens em ordem diferente | serializacao da fonte, nao regulacao |
| `N-02` | diferenca so de espaco em branco | idem |
| `N-03` | valor que reaparece no mesmo registro/campo (A→B→A) | fonte oscilando entre publicacoes |
| `N-04` | mesmo documento recapturado com sha256 identico | uma captura nova nao e uma versao nova |
| `N-05` | parser diferente sobre o mesmo documento | mudanca de instrumento, nao de fato |

Medido no acervo: `N-01` sozinha responde por 496 das 528 diferencas brutas.

## 5 · Regras de janela temporal (`T-*`)

| id | condicao | janela | por que |
|---|---|---|---|
| `T-01` | validade ja passou e produto ainda listado ativo | `ACT_NOW` | ha um conflito declarado entre dois campos oficiais **hoje** |
| `T-02` | validade em ate 90 dias | `PREPARE` | prazo oficial proximo, com data na fonte |
| `T-03` | validade entre 91 e 180 dias | `MONITOR` | prazo oficial no horizonte |
| `T-04` | validade acima de 180 dias | `PLAN_NEXT_CYCLE` | ha data, sem urgencia |
| `T-05` | mudanca real detectada nos ultimos 30 dias de janela observada | `PREPARE` | o fato e novo para nos |
| `T-06` | qualquer outro caso | `NO_ACTION_YET` | nada na fonte pede tempo |
| `T-07` | dado em revisao | `UNKNOWN` | nao se atribui tempo a fato nao provado |

`ACT_NOW` aqui significa **"olhe hoje"**, nunca "pare de vender".

## 6 · Capacidades ADAMA e regras de roteamento (`C-*`)

Roteamento diz **quem pode precisar olhar**, nunca **o que fazer**.

| id | capacidade | recebe | estado | justificativa |
|---|---|---|---|---|
| `C-01` | `REGULATORY` | todo evento com `PROOF_STATE = PROVED` | `RELEVANT` | a mudanca e do registro oficial, que e o objeto de trabalho desta area |
| `C-02` | `REGULATORY` | todo item `NEEDS_REVIEW` | `RELEVANT` | so esta area pode adjudicar leitura de rotulo |
| `C-03` | `DEVELOPMENT_MARKET` | `CROP_USE_ADDED`, `TARGET_USE_ADDED` | `POTENTIALLY_RELEVANT` | uso novo pode abrir avaliacao; a ferramenta nao afirma oportunidade |
| `C-04` | `DEVELOPMENT_MARKET` | `CROP_USE_REMOVED`, `TARGET_USE_REMOVED`, `DOSE_CHANGE` | `POTENTIALLY_RELEVANT` | pode exigir reavaliacao de posicionamento |
| `C-05` | `COMMERCIAL_RTV` | qualquer evento | `NOT_RELEVANT` **por padrao** | o campo nao deve receber fato regulatorio bruto; so passa pelo portao `G-01` |
| `C-06` | `MARKETING_PRODUCT` | `CROP_USE_ADDED/REMOVED`, `TARGET_USE_ADDED/REMOVED`, `DOSE_CHANGE`, `RESTRICTION_CHANGE` | `POTENTIALLY_RELEVANT` | material publicado pode citar o uso que mudou; gera `CONTENT_REVIEW_CANDIDATE`, nunca "material errado" |
| `C-07` | `SUPPLY` | `EXPIRY_EVENT` | `POTENTIALLY_RELEVANT` | e uma data no horizonte, e so isso. `EXPIRY != WITHDRAWAL`: a regra nao autoriza derivar dela nenhum efeito comercial — nem sobre procura, nem sobre inventario, nem sobre venda |
| `C-10` | `SUPPLY` | `STATUS_CHANGE` | `POTENTIALLY_RELEVANT` | o estado administrativo do registro mudou. O fato e a mudanca de estado; a consequencia de abastecimento nao esta provada por ele |
| `C-11` | `SUPPLY` | `DATE_CHANGE` | `POTENTIALLY_RELEVANT` | um campo de data que **nao** e a validade se moveu. Vale olhar porque planejamento usa data, mas nao e vencimento e nao pode ser lido como tal |
| `C-12` | `SUPPLY` | `REVOCATION_ACT_CHANGE` | `POTENTIALLY_RELEVANT` | mudou um dado do ato de revoga (motivo, decreto, decorrencia). Isto e sobre o ATO, nao sobre a existencia do produto no mercado |
| `C-13` | `SUPPLY` | `PRODUCT_LEFT_ACTIVE_SET` | `POTENTIALLY_RELEVANT` | a registracao saiu do conjunto ativo do instantaneo. `CATALOG_PRESENCE != MARKET_PRESENCE`: sair do conjunto ativo prova uma coisa so, que a linha saiu daquele conjunto naquele instantaneo |
| `C-08` | `INTELLIGENCE` | todo evento provado | `RELEVANT` | a area cruza portfolio, cultura, alvo e tempo |
| `C-09` | `COUNTRY_PRODUCT_TEAM` | eventos do proprio pais | `POTENTIALLY_RELEVANT` | dono do portfolio local |
| `C-99` | qualquer | tipo de evento sem regra acima | `UNKNOWN` | nenhuma regra cobre; aparece como nao roteado |

Uma regra de roteamento so pode ser citada por um tipo de evento que ela
nomeia. `C-07` ja foi escrita para `EXPIRY_EVENT, STATUS_CHANGE` e usada por
cinco tipos: o cabecalho dizia "sao eventos com data" sobre uma saida do
conjunto ativo, que nao e uma data. Cinco tipos diferentes agora tem cinco
regras, cada uma com a sua propria justificativa, porque as razoes sao
diferentes — e porque juntar vencimento com saida do conjunto ativo debaixo de
uma frase so e exatamente a confusao que `EXPIRY != WITHDRAWAL` proibe.

## 7 · Portoes (`G-*`)

| id | portao | condicao para abrir |
|---|---|---|
| `G-01` | mensagem para o campo (RTV) | exige `PROOF_STATE = PROVED` **e** revisao humana registrada. A ferramenta nunca abre este portao sozinha; ela so cria `COMMERCIAL_MESSAGE_CANDIDATE` |
| `G-02` | `PHI_CHANGE` | so existe se o PHI estiver provado. Como `PHI_PROVED = 0`, nenhum `PHI_CHANGE` pode ser emitido nesta versao |
| `G-03` | implicacao de negocio | so com regra `B-*` propria. Nao existe nenhuma `B-*` nesta versao, entao `POTENTIAL_BUSINESS_IMPLICATION = NOT_PROVED` em todos os objetos |

## 8 · O que esta versao declaradamente NAO faz

- nao emite `ACTION`;
- nao emite `PHI_CHANGE` (portao `G-02` fechado por falta de prova);
- nao emite implicacao de negocio (portao `G-03`, sem regra `B-*`);
- nao envia nada ao campo (portao `G-01`);
- nao infere demanda, estoque, preco ou concorrencia a partir de rotulo.
