# ROTA-NOVA-CANDIDATAS-D88 · o que falhou por anti-robô / WAF / JavaScript nas minhas micro-provas

D88 (dono, 26/09 19:25): contorno **técnico** de acesso a material **público** passa a ser permitido (anti-robô tipo
Cloudflare, navegador furtivo, JavaScript, outra rota técnica). Continua proibido: conta paga / paywall. Continuam: teto por
domínio, VPN IT, dado pessoal, proveniência da rota. Precisa do dono: login com conta, CAPTCHA pago, proxy pago.

**Como medi** (sem rede, nos bytes já guardados, sha256 abaixo): as 3 rodadas que fiz hoje — micro-prova lote 1 (07:10),
lote 2B (11:05), sonda de monitorização lm-1310 (13:10) — e a SONDA Coldiretti/ANGA/Unaprol (06:25, a minha
`sonda_um_pedido.py`). ⚠️ Marcas como «cloudflare», «recaptcha», «elementor», «noscript» aparecem em **páginas normais**
(servidor de conteúdo, formulário de contacto, construtor de sites) e **não** provam bloqueio. Conta como prova só:
**recusa escrita**, **ligação cortada pelo site**, ou **muitos bytes e quase nenhum texto** (casca de JavaScript).

## A · Recusa do site (anti-robô / WAF) — primeira fila para rota nova

| # | Fonte | Página | Prova (medida) | sha256 (16) | Rota nova provável |
|---|---|---|---|---|---|
| A1 | **IT-T7-050 Coldiretti** (nacional) | www.coldiretti.it | ligação **cortada pelo site** (URLError WinError 10054, HTTP 0), portão IT PASS | sonda `d1310a9eb8087fe9` | navegador real (janela) pela VPN IT; se o corte for pela reputação do IP da saída VPN → **proxy residencial = pago → dono** |
| A2 | IT-T7-051/052/053 Coldiretti Puglia · Sicilia · Veneto | *.coldiretti.it | idem (3/3) | idem | idem (mesma organização: 1 rota serve as 4) |
| A3 | IT-T7-045 **ANGA** | www.anga.it | idem | idem | idem |
| A4 | IT-T7-058 **Unaprol** | www.unaprol.it | idem | idem | idem |
| A5 | **IT-T3-033 Regione Piemonte** — bacheca dei bollettini fitosanitari | regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan/bacheca-dei-bollettini | HTTP 200 com **52 bytes**: «Non è possibile accedere a questo sito direttamente» | `b83591df56c5dbfc` | navegador (cabeçalhos/Referer/cookies de sessão de uma navegação normal) |

## B · Casca de JavaScript (a página só diz «Loading…»; o conteúdo vem por script)

| # | Fonte | Página | Prova | sha256 (16) | Rota nova |
|---|---|---|---|---|---|
| B1 | CAND-0026 **Laimburg** (Alto Adige) | www.laimburg.it | 2 842 bytes, **35 letras** («Versuchszentrum Laimburg Loading…»), 0 links, 4 scripts | `162707d8d64200dc` | navegador sem janela que corre o JS (ou a API JSON que o script chama) |
| B2 | CAND-0018 **Veneto Agricoltura** | www.venetoagricoltura.org | 6 250 bytes, **8 letras** («myPortal»), 0 links, 16 scripts, chamadas AJAX | `20c2f9d91c7b34ff` | idem |
| B3 | **IT-T3-038 Provincia Bolzano** — Landwirtschaft | provincia.bz.it/agricoltura-foreste/agricoltura/default.asp | 2 491 bytes, **61 letras** («… Loading…»), 0 links | `e241a1b86efa26ed` | idem (é também a entrada errada do contrato: cai na casa geral) |

## C · Moldura com o corpo vazio (menu vem; o texto da página vem por script)

| # | Fonte | Página | Prova | sha256 (16) | Porque interessa |
|---|---|---|---|---|---|
| C1 | **IT-T3-028 Emilia-Romagna** — «Elaborazione modelli previsionali e monitoraggi aereobiologici» | agricoltura.regione.emilia-romagna.it/…/elaborazione-modelli-previsionali-e-monitoraggi-aereobiologici-2024 | 830 KB, **319 letras**; a página diz «I report sono redatti a cadenza **settimanale per i fitofagi**» mas **nenhum link** para os relatórios no HTML | `00fbad44ad11c90e` | **sinal precoce semanal** de uma região inteira — o melhor alvo desta lista |
| C2 | ARSAC (Calabria; host de IT-T2-148/IT-T12-…) — «Difesa fitosanitaria del nocciolo: **monitoraggio** e consigli…» | arsacweb.it/difesa-fitosanitaria-del-nocciolo-monitoraggio-… | 106 KB, **134 letras** (só o título) | `f444348c601b9675` | monitorização do avelã |
| C3 | ARSAC — prevenzione fitosanitaria | arsacweb.it/prevenzione-fitosanitaria/ | 129 KB, **146 letras** | `c0af4412d137fcec` | o índice que liga às páginas de monitorização |
| C4 | IT-T3-055 Valle d'Aosta — Popillia japonica / flavescenza dorata / convegno | regione.vda.it/…/popillia_japonica_newman_i.aspx (e as 2 irmãs) | 42–70 KB, **59–95 letras** (só o título), ~270 links de menu | `156133a14131c145` | Popillia e flavescenza (fichas técnicas) |
| C5 | L2B-16 **CODIVE** (Veneto) | codive.it/chi-siamo/ e /condizioni-compagnie-2019/ | 60 KB e 217 KB, **0 letras** | `ba30eb8ffe9482bb` | consórcio de defesa (provavelmente seguros) |
| C6 | L2B-19 CODIPRA Toscano | codipratoscano.it/campagna-cereali-2021/ | 12 KB, **0 letras** (a página irmã tem 1 405) | `8253b2d4335ea170` | idem |
| C7 | L2B-01 Condifesa Foggia | condifesafoggia.it | 128 KB, **197 letras**, AJAX | `a5c8eb443ffd85da` | idem (fraco: pode ser só uma casa curta) |

## D · NÃO são anti-robô (não gastar rota nova aqui)

- **Falha de ligação, repetir:** L2B-17 Condifesa Lombardia (federazione) — `TimeoutError` numa só tentativa.
- **Login com conta (precisa do dono pela D88):** Terre dell'Etruria IT-T3-005 — «Catture adulti: Dato per utenti registrati»
  (a % de infestação é pública e já a lemos); SIMFITO Campania IT-T3-026 — plataforma de **técnicos autorizados**.
- **Não era falha:** Condifesa Brescia (L2B-05) e Condifesa Lombardia Nord-Est (CAND-1069) devolvem **a mesma página, byte
  a byte** (30 789 bytes) — é o **mesmo consórcio com dois endereços**, e a página não liga a publicações. **COSMAN Piemonte
  (L2B-13) não é consórcio de defesa**: é «COnsorzio SMaltimento rifiuti di origine ANimale» — fora (e veterinária não é foco).
- **Páginas «Sem conteúdo linkado» com texto normal** (CODIPE, CODIPRA Trento, Condifesa Umbria…): o site simplesmente não publica.

## E · Robots.txt — ⚠️ a D88 não diz se conta como «acesso técnico»

A D39 manda **cumprir o robots.txt**; a D88 permite contornar bloqueios **técnicos** mas não fala do robots (que é uma
**regra escrita do site**, não um bloqueio). **Não contornei nem proponho contornar sem o dono dizer.** Os que pararam no robots:
Lombardia SFR (fitosanitario.regione.lombardia.it — **proíbe**), Puglia SIT e emergenzaxylella.it (robots responde 302),
SIAS Sicilia, Beratungsring (URLError no robots), meteo VdA (503), IAR Aosta (ligação cortada), fitosanitario.venezia.it
(ROBOTS_BLOCKED), e os 5 consorzi do LOTE 3 (condifesa.it URLError, Ancona-Macerata 500, Cagliari URLError, Piemonte URLError,
**Veneto Est 403** — este 403 no robots pode ser WAF). **Pergunta ao dono:** «o robots.txt conta como acesso técnico que a D88 libera?»

## Ordem sugerida (valor para o casco × esforço)

1. **C1 Emilia-Romagna** (relatórios semanais de fitófagos, região inteira) · 2. **A1–A4 Coldiretti/ANGA/Unaprol** (1 rota serve 6
fontes; se for IP da VPN → dono decide proxy) · 3. **A5 Piemonte** (bacheca dos boletins) · 4. **C2–C3 ARSAC** (monitorização) ·
5. **B1–B3** (Laimburg, Veneto Agricoltura, Bolzano) · 6. C4–C7. Tudo pela VPN IT, teto 5/domínio, proveniência gravada
(«rota: navegador», com a versão), sem conta.

## EM PALAVRAS SIMPLES

- **Seis sites cortam a ligação** quando o nosso robô chega (Coldiretti em 4 regiões, ANGA, Unaprol), e **o Piemonte responde
  «não é possível aceder diretamente»**. Estes são os primeiros para tentar com um navegador de verdade.
- **Três sites mostram só «A carregar…»** (Laimburg, Veneto Agricoltura, Bolzano) — o conteúdo aparece só depois de o
  programa da página correr. Um navegador que corre esse programa resolve.
- **Sete páginas mostram o menu mas o texto vem vazio** — a mais valiosa é a da **Emilia-Romagna**, que diz ter relatórios
  **semanais** de insetos e não mostra os links.
- **Não mexi em nada:** só olhei o que já estava guardado. E há uma pergunta para o dono: o **robots.txt** (a regra escrita
  pelo site) também entra no «pode contornar»? Até ele dizer, continua respeitado.
