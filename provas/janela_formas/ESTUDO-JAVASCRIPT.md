# JANELA-FORMAS C · estudo: existe uma rota pública JSON/XHR para as 6 fontes «JavaScript»? (D42 (3))

**Só estudo, sem rede** (D42: navegador sem cabeça só se não houver rota pública). Base: as
entradas que o robô guardou no lote da bancada de 25/09 (`C:/cur/banc30-lotes/LOTE-20260925T072003Z/`,
sha256 de cada página no `LOTE.json`) e os robots.txt baixados na medição RFC (`C:/cur/rfc/rede/robots/`).

| fonte | o que o HTML mostra | rota pública? | robots | estado |
|---|---|---|---|---|
| IT-T3-013 · IT-T3-028 · Emilia-Romagna, boletins de produção integrada | frente **Volto** (Plone em React): `RAZZLE_API_PATH` e `RAZZLE_PROXY_REWRITE_TARGET …/agricoltura/++api++/VirtualHostRoot` | **provável: a REST API do Plone** — o mesmo caminho com o prefixo `++api++` (ex.: `https://agricoltura.regione.emilia-romagna.it/++api++/fitosanitario/difesa-sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-e-biologica-2026`) devolve o conteúdo e os filhos (ficheiros) em JSON — padrão do plone.restapi, **não verificado neste site** | cópia lida pela RFC: o grupo `*` só proíbe `/search`, `/folder_contents$`, … → `++api++` **permitido** | **ESPERA 1 pedido autorizado** (confirmar que o JSON responde e lista os boletins) |
| IT-T2-150 · IT-T2-151 · agrometeopuglia | Drupal 8; a lista é montada por um módulo próprio `/modules/custom/Bollettini/js/Bollettini.js`; o `drupalSettings` não traz o endereço | **NÃO SEI** — o endereço de onde o módulo lê está no `.js`, que não foi guardado. O coletor já tinha medido o mesmo («o índice é renderizado por JavaScript», caso IT-T3-008) | sem cópia do robots | **ESPERA 2 pedidos autorizados** (robots + `Bollettini.js`, para ler o endereço) |
| IT-T3-018 · ISPA-CNR notícias | lista vazia no HTML; scripts `functions.bundle.js`, `funzioni.js` | NÃO SEI | **o robots.txt vem em HTML** → pela D39 é `ROBOTS_INVALID_CONTENT` = **recusa** | **FORA pela D39** (sem robots legível não se lê a API) |
| IT-T3-026 · SIMfito Campania | a entrada **não tem JavaScript nenhum**; a lista está numa página `/bollettini` que o robô nunca buscou | NÃO SEI se é JS — a bancada chamou-lhe «JS» por engano de leitura | sem cópia | **ESPERA 1 pedido** (a página `/bollettini`) |

**Headless (navegador sem cabeça):** não é preciso decidir já. A Emilia-Romagna tem, muito
provavelmente, rota pública JSON. Para agrometeopuglia e SIMfito, primeiro ler o `.js` ou a página
(3 pedidos no total), e só depois, se não houver rota, pôr a questão do navegador. O ISPA fica fora
pela D39 enquanto o robots vier em HTML.
