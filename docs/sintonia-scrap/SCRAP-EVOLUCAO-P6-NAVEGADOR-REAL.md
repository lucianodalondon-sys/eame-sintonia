# SCRAP-EVOLUCAO-V1 · peça 6 — o navegador real (`web.page.browser_rendered`)

> Declarada em `coleta/scrap_capacidades.py` como `PARTIAL`, `LOCAL / BROWSER_REAL_REQUIRED`.
> **Não está ligada:** espera a emenda `COL-LAW-220` (`ESPERAM_EMENDA`). Enquanto ela não estiver em
> `EMENDAS_EM_VIGOR`, `promete_resultado('web.page.browser_rendered')` responde **não**.

## O que foi medido (coordenador, 26/09 20:25, com rede, VPN IT PASS antes e depois)

`StealthyFetcher` do Scrapling (patchright + chromium), sem janela, `google_search=False` (sem Referer
falso), 1 pedido por alvo. Evidência copiada em `provas/scrap_evolucao/CANARIO-STEALTH-R1.json`
(original: `auditoria-madrugada/canario-stealth/r1/`, com os `.html`).

| fonte | endereço | HTTP | bytes | título | segundos |
|---|---|---|---|---|---|
| IT-T9-008 ADAMA | adama.com/italia | 200 | 76.766 | «ADAMA è uno dei leader mondiali…» | 8,7 |
| IT-T9-002 Bayer | cropscience.bayer.it | 200 | 251.426 | «Bayer Crop Science Italia» | 10,7 |
| IT-T9-003 Syngenta | syngenta.it | 200 | 254.086 | «Syngenta Italia \| Soluzioni…» | 7,7 |

3 de 3, 27 s no total. É **uma** corrida, **uma** classe (Akamai/WAF): por isso `PARTIAL`, não `PROVEN`.

## O corpo não é RAW (COL-LAW-007)

O que o navegador devolve é o **DOM desenhado** depois de correr o JavaScript — não os bytes que o
servidor mandou. Rótulo obrigatório: `BROWSER_RENDERED_EXTRACT` (`ROTULO_DO_CORPO`). O validador do
ficheiro recusa uma capacidade `web.*` com `BROWSER_REAL_REQUIRED` sem esse rótulo. Quando a fonte tem
um JSON por trás, a rota preferida continua a ser `ferramentas/captura_xhr.py` → `STATIC_ENDPOINT`, que
devolve bytes do servidor.

## Só por fonte

`FONTES_DA_CAPACIDADE` nomeia as fontes medidas (IT-T9-002, IT-T9-003, IT-T9-008). Nunca «todas as que
falham». Mesmo portão e teto das outras rotas: egresso IT, robots vivo, 5 pedidos por domínio, janela de
24 h; rota na proveniência (`COL-LAW-704`).

## Custo de memória por página (medido aqui, sem rede)

`provas/scrap_evolucao/medir_ram_navegador.py`, com o Python de estudo que tem o patchright
(`C:/g/scrapling-estudo/.venv-full`; o patchright **não** entrou no repositório). As 3 páginas guardadas
pelo coordenador servidas em 127.0.0.1; tudo o que a página pediria fora foi recusado (proxy fechado).
Resultado em `provas/scrap_evolucao/RAM-NAVEGADOR.json`:

| instante | memória em uso (working set) | memória só dele (privada) |
|---|---|---|
| navegador aberto, sem página | 344 MB | 260 MB |
| com a página da Bayer | 485 MB | 307 MB |
| com a página da Syngenta | 796 MB | 316 MB |
| com a página da ADAMA | 757 MB | 278 MB |

Pico: **796 MB**. ⚠️ É um **piso**: sem rede a página não baixou scripts, imagens nem fontes de fora; a
página real custa mais. A soma inclui o processo `node` do patchright. Um navegador por vez, fechado no fim.

## O que falta para ligar

1. A emenda `COL-LAW-220` entrar na Bíblia (hoje é só texto proposto em
   `auditoria-madrugada/ESTUDO-ORQUESTRACAO-24H-LUCIANO.md`) e o id entrar em `EMENDAS_EM_VIGOR` no mesmo commit.
2. A dependência patchright + chromium entrar no repositório (decisão do dono: a fase atual é zero dependência).
3. O adaptador que corre a página atrás do portão, grava o corpo com o rótulo e conta o teto.
