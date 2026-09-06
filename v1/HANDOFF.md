# HANDOFF — SINTONIA LABEL INTELLIGENCE V1 · ITALIA

Estado no fim desta sessao. Tudo aqui foi **medido**, nao estimado. Onde nao foi
provado, esta escrito que nao foi.

## LEI ZERO (vale para quem continuar)

Nunca inventar, completar, presumir ou preencher fato ausente. Na duvida:
`NOT_PROVED` / `NEEDS_REVIEW` / `UNKNOWN`. Falha de acesso, de parser ou de
coleta **nao e zero**. Inferencia tem de vir rotulada como inferencia.

Leis nomeadas que o produto inteiro sustenta:
`PARSER_FAILURE != REGULATORY_ABSENCE` · `EXPIRY != WITHDRAWAL` ·
`CATALOG_PRESENCE != MARKET_PRESENCE` · `SOURCE_REORDER != LABEL_CHANGE_EVENT` ·
`CAPTURED_AT != EFFECTIVE_AT` · `DOCUMENT_CHANGED != REGULATORY_MEANING_CHANGED`
e, desde esta sessao, `SOWING_BAN_IS_NOT_A_USE`.

Tokens de ignorancia aparecem com o nome proprio, nunca como `-`, `0` ou `N/A`.
`NOT_RELEVANT` **nao** e ignorancia: e a decisao da regra C-05.

## PROIBICOES PERMANENTES

NAO tocar: `sintonia/canonical`, P0.2, Passaporte, Universal, Supabase canonico,
portal oficial, dominio oficial. NAO fazer deploy. NAO integrar ao portal.
`PORTAL_INTEGRATION = NO`, mesmo se algum portao passar.

## O QUE ESTA SESSAO FEZ

**Os 11 MUST_FIX da rodada 3 estao fechados**, cada um com uma medicao contra a
fonte primaria e um teste de regressao em `v1/testes/test_casco.js`. O resumo
numerico esta em `v1/testes/CONFERENCIA-MUST-FIX.json`; a narrativa, na secao L
de `v1/ENTREGA-V1.md`.

Antes deles foi preciso resolver um bloqueio que impedia qualquer conserto:

> Toda a camada de USO lia `IT-ROTULOS-PARES-V3.json` de `sintonia/canonical`,
> que **nao esta neste repositorio e nao esta acessivel**. Sem ele, `exclusao.py`
> e `payload.py` nao rodam.

`v1/fonte/pares_reconstruir.py` remonta os 2.928 pares a partir de dois
artefatos versionados derivados do proprio original, e **para** se alguma posicao
nao bater. `v1/fonte/pares_conferir.py` prova que serve: R-10 identico nas 2.928
chaves, os 2.926 pares publicados identicos nos 9 campos, e o HTML remontado por
esse caminho saiu com sha256 `7e4ea2a7b445fafa...` — o mesmo alvo que o arbitro
da rodada 3 julgou.

Tres regras novas, todas com o modulo, a medicao e o falso positivo que as
moldou escritos ao lado do codigo:

| regra | arquivo | o que fecha |
|---|---|---|
| `R-14` | `v1/inteligencia/par_validar.py` | o PAR cultura x alvo contra a celula desenhada. **47 pares retirados** |
| `R-10b` | `v1/coleta/exclusao.py` | proibicao de semeadura em sucessao lida como permissao. **4 pares** |
| `R-15` | `v1/inteligencia/heranca_validar.py` | `MAX`/`INTERVALO` herdados de celula mesclada, e a nota que enumera culturas |

Os 47 de R-14 **sao exatamente** os que o arbitro enumerou por conta propria,
com outro instrumento e a partir de coordenadas que este repositorio nao tem.
Convergencia independente; nao e veredito.

`2.926 -> 2.875` pares publicados. Portoes 19/19, ruido 12/12, tela 23/23.

## COMO CONTINUAR

```sh
git clone https://github.com/lucianodalondon-sys/eame-sintonia
cd eame-sintonia
git checkout claude/label-intelligence-v1-italy
apt-get install -y poppler-utils            # pdftotext e pdftoppm sao obrigatorios
python3 v1/fonte/recoletar.py .             # traz e confere os 223 arquivos da fonte
sh v1/casco/build.sh
python3 v1/testes/test_portoes.py ; node v1/testes/test_casco.js
python3 v1/testes/conferir_mustfix.py       # remede os MUST_FIX contra a fonte
```

**A fonte primaria nao esta no git** — 60 CSV (272 MB) e 163 PDF (34 MB), por
decisao da casa (D-003). `recoletar.py` confere cada sha256 contra
`v1/fonte/MANIFESTO-FONTE.json`; arquivo que nao bate nao e aceito. Medido nesta
sessao: **223 conferidos, 0 com sha errado**.

Dois detalhes de acesso que custaram tempo e estao resolvidos no script:
os dois hosts do Ministero recusam clientes diferentes (`dati.salute.gov.it`
devolve `SSLV3_ALERT_HANDSHAKE_FAILURE` ao `urllib`; `fitosanitari` manda um
`Public-Key-Pins` dobrado que faz o `curl 8` abortar), entao cada arquivo e
tentado nos dois. E o host das etichette omite a intermediaria TLS — a cadeia e
montada por `pilot-label-intelligence/bin/chain.sh`. **Nunca desligar a
verificacao.**

Sem essa fonte, **nao rode portao nem red team**: todo veredito foi ganho
reproduzindo contra esses arquivos, e um veredito sobre outro acervo nao e
comparavel.

## O QUE ESTA SESSAO NAO ENTREGOU

- **`DEMO_READY` continua `NAO`**, e a razao principal continua a mesma: nenhum
  arbitro adjudicou ESTE build. Quem mede nao pode ser quem produziu.
- **Os 1.056 pares de rota de PROSA nao tem instrumento nenhum.** R-14 e
  geometrica e nao alcanca prosa; e o teste so-de-texto foi medido e **nao
  discrimina** (93,6% de coocorrencia nos pares que a geometria condena, 98,5%
  nos que ela absolve, nos MESMOS rotulos). E o maior buraco aberto.
- **As quatro abstencoes de R-14 sao superficie nova de ataque.** Cada uma
  nasceu de um falso positivo real, todas erram para o lado de nao apagar uso
  verdadeiro, e todas podem estar deixando passar um par falso. A quarta rodada
  adversarial deve comecar por elas.
- **Cobertura por celula de cultura desenhada:** `NOT_MEASURED`. O vocabulario
  fechado de uso esta declarado na tela de COBERTURA; contar quantas celulas de
  cultura existem nos 163 documentos exigiria um leitor que nao existe.
- **`FUSION_DETECTOR = NOT_IMPLEMENTED`**, com as tres tentativas medidas.
- **PHI:** `PROTOTYPE_NOT_SHIPPED`, nada publicado.
- **A trilha B (`claude/label-intelligence-demo-safe-italy`) nao foi tocada.**
  A 3a passagem do `PRE_DEMO_GATE` continua sem veredito e `DEMO_SAFE_READY`
  continua `NOT_DECIDED`. Esta sessao tinha permissao de escrita so em
  `claude/label-intelligence-v1-italy`.
- **`empacotar.py` e o passo 5-7 do pipeline** continuam precisando do manifesto
  de leitura de canonical, que nenhum artefato daqui reconstitui. Agora eles
  FALHAM DIZENDO isso, ou sao pulados com "passo nao executado", em vez de
  escrever campo inventado. `MANIFESTO_DE_LEITURA_NOT_AVAILABLE` **nao** e
  "nenhum rotulo mudou".

## O QUE DIZER EM VOZ ALTA NUMA DEMO

Esta e uma ferramenta **PILOT / SHADOW**, nao integrada ao Sintonia, read-only
sobre dado publico do Ministero della Salute (IODL 2.0). O dado e um instantaneo
de 2026-08-31, nao um feed. `ACT_NOW` significa "olhe hoje", nunca "pare de
vender" — a ferramenta **nao emite ACTION**. Uso autorizado agora passa por
conferencia geometrica onde ha tabela desenhada, e **nao passa por nenhuma** onde
o rotulo escreve em prosa: a coluna "Evidencia do par" diz qual e o caso de cada
linha, e `NOT_CHECKED` nao e aprovacao.
