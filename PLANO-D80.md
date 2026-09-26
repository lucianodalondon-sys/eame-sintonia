# PLANO-D80 · retirar as não-fontes, numerar as de fora de IT, a página herda a classe do site

Ramo **`d80-v1`**, a partir do vivo `origin/servico-20260923-0923` @ **`69b0e23f`**. Feito a 26/09, **sem rede**.
Nada aplicado no vivo; o vivo e a Sala não foram tocados. Instalar = `git merge --ff-only` (o ramo desce de `69b0e23f`).

## 0 · O que muda (e o que NÃO muda)

| Parte | Onde | O que faz |
|---|---|---|
| (i) | `candidatas/fonte_nova.py` | `recusar(url, motivo, duplicada_de=, decisao=)` guarda o estado de antes (`RECUSA_ANTERIOR`), a mãe (`DUPLICADA_DE`), quem recusou e quando. `reverter_recusa(url, decisao)` desfaz **só** o que a mesma decisão recusou e deixa rasto (`RECUSAS_REVERTIDAS`). As chamadas antigas gravam o mesmo que gravavam. |
| (i) | `curadoria/worker.py` (QUALIFY) | uma ficha `RECUSADA` não se qualifica → BLOCK/POLICY «RECUSADA pela porta de entrada» (nunca se tenta outra vez sozinha). |
| (ii) | `curadoria/worker.py` (QUALIFY) | decisão do canal com `PAIS` ≠ IT → número `<PAIS>-T<n>-<seq>` (max+1 sobre o Atlas + os livros JSON de `curadoria/` e `regras/` + o que já se cunhou; nunca recicla), guardado em **`NOVAS_FORA_DE_IT`** (não em `NOVAS`), e **PARA** em CAPABILITY_BLOCK. Site que já tem número na casa → não recebe outro (BLOCK semântico). Canal/LinkedIn de fora de IT → NAO SEI. |
| (iii) | `curadoria/rota_do_scrap_youtube.py` + `worker.py` | página HTML sem classe herda a classe **única** das fontes do **mesmo host** (host exacto; subdomínio é outro site). Não herda: a raiz do site (é a organização, já é fonte), site misto, e candidata com NAO SEI registado por **dúvida de identidade** (`decisao_semantica.DUVIDA_DE_IDENTIDADE`). Decisão com prova vale antes. |
| ferramenta | `curadoria/aplicar_d80.py` | a seco (padrão) / `--aplicar` / `--reverter`, sempre com `--recibo=`. Confere cada linha contra a ficha de AGORA: se a ficha mudou desde a montagem, não mexe. |

**Porque (ii) PARA no número.** A estrada de coleta toda é italiana: `curadoria/validar_contratos.py:51` só aceita
`IT-T<n>-<nnn>` e `regras/italy_contracts.mjs:690` **rebenta** o coletor se uma linha de outro prefixo entrar na tabela
onboarded. Deixar um `EU-` seguir para contrato e onboarding parava a coleta italiana inteira. Por isso: número sim,
contrato não, READY nunca automático. Abrir a estrada para fora de IT é outra missão (e do dono).

**Leitura minha das palavras do D80(ii):** em «fontes EU/INT» incluí também as 2 cujo país da prova é **GR** (Benaki) e
**FR** (INRAE) — são as 7 «decididas fora de IT» da BLOQUEADAS-268. Se o dono quis só EU e INT, basta tirar essas 2
decisões do canal antes de religar (ficam como estão hoje).

## 1 · A lista congelada (i): `curadoria/D80-LISTA-V1.json`

Montada da BLOQUEADAS-268 (`bloqueadas-v1` @ 889b2166) sobre uma cópia do vivo `69b0e23f` + os 17 livros sujos
(sha256 conferidos 17/17). **113 linhas → 102 RECUSAR, 11 NAO SEI.**

- **82 não-fontes** recusadas, cada uma com o motivo da leitura anterior (Opus/humano, `DECISOES-SEMANTICAS-V1`) ou da
  regra que casou: 47 NAO_E_FONTE · 20 FORA_DO_AGRO_APARENTE · 14 SEMENTE_ERRADA · 1 página de serviço.
- **20 duplicadas** recusadas **com a mãe escrita** (`DUPLICADA_DE`). A mãe acha-se por esta ordem, a mais forte primeiro:
  (1) o mesmo endereço já é a entrada de uma fonte; (2) nomeada na leitura **e** do mesmo site; (3) leitura à mão de 25/09;
  (4) a mãe dita pelo dono (`--mae=`); (5) a fonte do site cuja entrada é a raiz; (6) a única fonte do site;
  (7) nomeada na leitura, candidata ainda sem número (só Rete Rurale, CAND-0009).
- **11 ficam NAO SEI (não se recusam):**
  - 3 «talvez seja a mesma» (ISTAT CAND-0270; EIMA CAND-0573/0574) — dúvida de identidade, é do dono;
  - 7 páginas do MASAF em `masaf.gov.it` (CAND-0652, 0658, 0659, 0660, 0661, 0663, 0665): o site tem **5 fontes**
    (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma é a mãe provada. Se o dono disser qual é,
    entram com `--mae=masaf.gov.it=<SOURCE_ID>` (a ferramenta recusa um SOURCE_ID que não seja do site);
  - 1 casa da SOI (CAND-1050): a leitura de 25/09 nomeou **duas** mães (IT-T8-064/066) e o site tem 3 fontes.

## 2 · O ENSAIO (cópia do vivo, rede FECHADA) — `curadoria/ENSAIO-D80-V1.json`

Cópia = worktree `36d3d213` + os 17 livros sujos do vivo; proxy morto e `socket.create_connection` barrado.
**0 tentativas de rede.** Ordem igual à do plano: a seco → `--aplicar` → o robô corre só as QUALIFY reabertas e os
BUILD_CONTRACT que elas pedirem → `--reverter`.

| Medida | Resultado |
|---|---|
| a seco | 113/113 PRONTA; 102 a recusar; QUALIFY a reabrir: 7 «fora de IT» + 212 «indeterminado» |
| `--aplicar` | **102 recusadas**, 219 QUALIFY reabertas |
| QUALIFY | 219 corridas: 3 OK, 216 BLOCK = 102 «RECUSADA pela porta» + 7 «D80(ii) número, para» + 107 continuam NAO SEI |
| (ii) números | **EU-T12-002** biostimulants.eu · **INT-T12-001** croplife.org · **EU-T12-003** fertilizerseurope.com · **GR-T5-001** Benaki · **FR-T5-001** INRAE · **INT-T5-001** CIMMYT · **INT-T12-002** FAO — todas em CAPABILITY_BLOCK, 0 contratos |
| (iii) números | **IT-T2-168** SNPA linee guida (site: IT-T2-108) · **IT-T2-169** ARSARP pubblicazioni (IT-T2-149) · **IT-T8-071** Agraria Sassari eventi (IT-T8-062) → BUILD_CONTRACT 3/3 OK → CANARY_PENDING |
| READY novas | **0** (READY só pelo canário, com rede) |
| `--reverter` | 102 revertidas; **1204/1204 fichas iguais às do vivo** (tirando o rasto `RECUSAS_REVERTIDAS`) |

Das 8 «herda plausível» da BLOQUEADAS-268, **3 herdaram**; as outras 5 estão em **sites mistos hoje**: ISPRA
(CAND-1039/1040/1041: T2+T5), Acta Italus Hortus (CAND-0993, soihs.it: T1+T8), Entomologica eventos (CAND-1053: T3+T8).
«Site misto não herda» — ficam NAO SEI.

Os números do ensaio são os que o vivo daria **se nada mudar até lá**; o robô a correr pode cunhar outros IT- antes
(os de fora de IT só nascem por aqui).

Testes: `test_d80` 22/22; os 23 ficheiros de teste que tocam as peças mudadas: **1 vermelho igual antes e depois**
(`test_zz_guarda_isolamento`, as mesmas 6 queixas sobre ficheiros de outras lanes). Mutação: **15/15 mortos**.
Dois testes antigos mudaram de propósito (`test_decisao_semantica`: EU/INT agora recebem número fora de IT, nunca `IT-`).

## 3 · O COMANDO (coordenador, robô PARADO, um só escritor)

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
R=C:/Users/London1/auditoria-madrugada/D80 ; mkdir -p $R
# 1. Parar o robô — CUTOVER-RUNBOOK.md passo 1 (PARAR.flag e esperar o supervisor sair). A SONDA não é afectada.
# 2. Instalar (só código + a lista + o ensaio; nenhum livro vivo é tocado pelo merge)
git -C $V fetch origin d80-v1 && git -C $V rev-parse FETCH_HEAD     # tem de dar o SHA do relatório
git -C $V merge --ff-only FETCH_HEAD
# 3. A seco — confere contra as fichas de AGORA
cd $V && py curadoria/aplicar_d80.py --recibo=$R/RECIBO-A-SECO.json
#    esperar: POR_AGORA PRONTA=113 (menos, se o robô mexeu nalguma: essas NAO se tocam), A_RECUSAR=102,
#    QUALIFY_A_REABRIR {"territorio decidido fora de IT": 7, "territorio indeterminado pelo nome": ~212}
#    [opcional, se o dono disser a mae do MASAF: acrescentar --mae=masaf.gov.it=<SOURCE_ID> aqui e no passo 4]
# 4. Aplicar (i) e reabrir as QUALIFY de (ii) e (iii)
py curadoria/aplicar_d80.py --aplicar --recibo=$R/RECIBO-APLICAR.json      # esperar RECUSADAS 102
sha256sum $R/*.json
# 5. Portão IT (o worker NAO verifica o egresso sozinho) e religar — CUTOVER-RUNBOOK.md passo 8
py superficie/rede.py --portao-de-egresso IT      # EGRESS_GATE=PASS, senão não religar
rm $V/curadoria/PARAR.flag    # e o supervisor pelo mesmo meio de hoje (py curadoria/supervisor.py, cwd $V)
```

O robô faz o resto: as 219 QUALIFY → 7 números fora de IT (param) + 3 páginas com número IT → contrato → rota → canário.

**Desfazer (i)** (robô parado): `py curadoria/aplicar_d80.py --reverter --recibo=$R/RECIBO-REVERTER.json` — repõe as
102 fichas e reabre as QUALIFY «RECUSADA pela porta». Os números já cunhados em (ii)/(iii) **não se apagam** (nunca
reciclar); o código volta com `git -C $V reset --keep 69b0e23f` (depois de guardar status/diff).

## 4 · Lista final por fonte (do ensaio)

| # | Candidata | Nome | Decisão | Duplicada de | Motivo (resumo) |
|---|---|---|---|---|---|
| 1 | CAND-0270 | ISTAT — statistiche agricoltura | NAO SEI | — | duvida de identidade (IDENTIDADE_DUPLICADA_POSSIVEL): ISTAT ja tem ficha no Atlas (IT-T1-001); dar numero aqui arrisca dois numeros para a mesma fonte |
| 2 | CAND-0064 | Agrisicilia | RECUSADA | — | D80(i) NAO_E_FONTE: agriturismo/camping em Selinunte, nao e fonte. |
| 3 | CAND-0429 | DICHIARAZIONE DI ACCESSIBILITA' | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra PAGINA_DE_SERVICO casa no  |
| 4 | CAND-0320 | Dichiarazione di accessibilità | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra PAGINA_DE_SERVICO casa no  |
| 5 | CAND-0398 | Obiettivi di accessibilità | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra PAGINA_DE_SERVICO casa no  |
| 6 | CAND-0318 | Parlamento Europeo | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. · regra ORGAO_LE |
| 7 | CAND-0369 | A journey through the Crotone Sila, amidst na | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra TURISMO casa no nome/URL |
| 8 | CAND-0367 | A trip to Lake Ampollino | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra TURISMO casa no nome/URL |
| 9 | CAND-0395 | ARUS | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 10 | CAND-0413 | Avviso per iscrizione in elenco strutture per | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra PAGINA_DE_SERVICO casa no  |
| 11 | CAND-0345 | Calabria Straordinaria | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. · regra TURISMO  |
| 12 | CAND-0352 | CalabriaSUE - Sportello Unico per l’Edilizia | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 13 | CAND-0370 | Calabrian pasta: traditional shapes | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 14 | CAND-0316 | Camera dei Deputati | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. · regra ORGAO_LE |
| 15 | CAND-0396 | Campania Artecard | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 16 | CAND-0381 | Consiglio Regionale | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 17 | CAND-0408 | Corecom Abruzzo | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 18 | CAND-0274 | InLombardia | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 19 | CAND-0430 | Intranet | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 20 | CAND-0314 | Irfis | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 21 | CAND-0317 | Presidenza del Consiglio dei Ministri | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. · regra ORGAO_LE |
| 22 | CAND-0312 | Protezione Civile | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 23 | CAND-0368 | Relax at the Bagni di Guida | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 24 | CAND-0353 | SaniBook | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 25 | CAND-0298 | Segnalazione di condotte illecite | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 26 | CAND-0315 | Senato della Repubblica | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. · regra ORGAO_LE |
| 27 | CAND-0344 | Sportello del Consumatore | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 28 | CAND-0333 | Spotify | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra REDE_SOCIAL_OU_APP casa no |
| 29 | CAND-0311 | Vai al sito | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 30 | CAND-0296 | Visita il sito | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 31 | CAND-0465 | dati.lombardia.it | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 32 | CAND-0424 | hatsapp.com | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra REDE_SOCIAL_OU_APP casa no |
| 33 | CAND-0290 | open.spotify.com | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra REDE_SOCIAL_OU_APP casa no |
| 34 | CAND-0299 | open.spotify.com | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. · regra REDE_SOCIAL_OU_APP casa no |
| 35 | CAND-0489 | Area Riservata | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 36 | CAND-0485 | ESG e Sostenibilità | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 37 | CAND-0484 | Energia | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 38 | CAND-0477 | Le nostre eccellenze | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 39 | CAND-0528 | Mozilla Firefox 29+ | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 40 | CAND-0529 | PEC | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 41 | CAND-0490 | Powered by Noetica | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 42 | CAND-0483 | Pubblica Amministrazione | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 43 | CAND-0481 | Real Estate | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 44 | CAND-0573 | eimaagrimach.in | NAO SEI | — | duvida de identidade (IDENTIDADE_DUPLICADA_POSSIVEL): possivel mesma fonte que EIMA IT-T11-001 (eima.it); decisao de identidade do dono. — nao se recu |
| 45 | CAND-0574 | eimashow.it | NAO SEI | — | duvida de identidade (IDENTIDADE_DUPLICADA_POSSIVEL): possivel mesma fonte que EIMA IT-T11-001 (eima.it); decisao de identidade do dono. — nao se recu |
| 46 | CAND-0585 | interreg-central.eu | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 47 | CAND-0570 | mondomacchina.it | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 48 | CAND-0491 | prenotazioni-evento.nomisma.it | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 49 | CAND-0552 | previdenzacooperativa.it | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 50 | CAND-0660 | Controlli | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 51 | CAND-0665 | Leggi tutto | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 52 | CAND-0663 | PNRR | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 53 | CAND-0658 | Politiche europee | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 54 | CAND-0659 | Politiche nazionali | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 55 | CAND-0661 | Qualità | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 56 | CAND-0652 | masaf.gov.it | NAO SEI | — | duplicada sem mae provada: o site masaf.gov.it tem 5 fontes (IT-T12-128, IT-T5-095, IT-T7-002, IT-T8-019, IT-T9-023) e nenhuma e a mae provada |
| 57 | CAND-0637 | Department of Science and Technology of Henan | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 58 | CAND-0636 | Universidad Técnica del Norte - Ecuador | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: instituicao real sem relacao agricola evidente pelo endereco; sem prova colhida. |
| 59 | CAND-0700 | Abbonati / Rinnova | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape/servico/login/pagina solta recolhido pelo crawler; nao e uma fonte. |
| 60 | CAND-0715 | Calendario eventi | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 61 | CAND-0704 | Cerca adesso | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 62 | CAND-0703 | Contenuti riservati agli abbonati | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 63 | CAND-0669 | Francesco Lollobrigida | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 64 | CAND-0721 | I libri tecniche Nuove | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 65 | CAND-0712 | L'esperto risponde | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 66 | CAND-0716 | Mediagallery | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 67 | CAND-0651 | Privacy policy | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. · regra PAGINA_DE_SERVICO casa no nom |
| 68 | CAND-0720 | Tecniche Nuove | RECUSADA | IT-T8-033 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T8-033: Tecniche Nuove e a editora; a fonte e a revista Terra e Vita, que ja tem ficha (IT-T1-015). |
| 69 | CAND-0718 | Vai allo shop generale | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 70 | CAND-0731 | VisitTrentino | RECUSADA | — | D80(i) FORA_DO_AGRO_APARENTE: FORA_DO_AGRO_APARENTE: turismo; sem prova colhida. |
| 71 | CAND-0705 | Visualizza tutti | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 72 | CAND-0654 | Whatsapp | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. · regra REDE_SOCIAL_OU_APP casa no no |
| 73 | CAND-0614 | hatsapp.com | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. · regra REDE_SOCIAL_OU_APP casa no no |
| 74 | CAND-0664 | politicheagricole.it | RECUSADA | IT-T12-020 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T12-020: PAGINA_DE_OUTRA_FONTE: pagina interna de MASAF; a fonte e a organizacao, nao cada pagina. |
| 75 | CAND-0666 | politicheagricole.it | RECUSADA | IT-T12-020 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T12-020: PAGINA_DE_OUTRA_FONTE: pagina interna de MASAF; a fonte e a organizacao, nao cada pagina. |
| 76 | CAND-0667 | politicheagricole.it | RECUSADA | IT-T12-020 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T12-020: PAGINA_DE_OUTRA_FONTE: pagina interna de MASAF; a fonte e a organizacao, nao cada pagina. |
| 77 | CAND-0668 | politicheagricole.it | RECUSADA | IT-T12-020 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T12-020: PAGINA_DE_OUTRA_FONTE: pagina interna de MASAF; a fonte e a organizacao, nao cada pagina. |
| 78 | CAND-0671 | politicheagricole.it | RECUSADA | IT-T12-020 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T12-020: PAGINA_DE_OUTRA_FONTE: pagina interna de MASAF; a fonte e a organizacao, nao cada pagina. |
| 79 | CAND-0674 | reterurale.it | RECUSADA | CAND-0009 | D80(i) PAGINA_DE_OUTRA_FONTE de CAND-0009: e a pagina PAC_2023_27 do reterurale.it — a mesma fonte que CAND-0009 (Rete Rurale), que continua pendente  |
| 80 | CAND-0717 | visualizza tutti | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 81 | CAND-0760 | 5‰ per sostenerci | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 82 | CAND-0758 | About us | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 83 | CAND-0768 | Archivio | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 84 | CAND-0759 | Collabora | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 85 | CAND-0765 | Festival | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 86 | CAND-0770 | GlobalProject | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 87 | CAND-0772 | HCE web design | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 88 | CAND-0763 | Podcast | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 89 | CAND-0767 | Prevendite | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 90 | CAND-0766 | Programma & Info | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 91 | CAND-0762 | Programmi | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 92 | CAND-0761 | Radio | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 93 | CAND-0771 | Sport alla rovescia | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 94 | CAND-0764 | Webzine | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 95 | CAND-0757 | sherwood.it | RECUSADA | — | D80(i) SEMENTE_ERRADA: SEMENTE_ERRADA: nasceu do crawl de sherwood.it — a Radio Sherwood (webzine cultural), que a C1 passou a usar como semente por s |
| 96 | CAND-0797 | Come associarsi | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 97 | CAND-0799 | Comunicati Stampa | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 98 | CAND-0801 | Dati Economici | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 99 | CAND-0802 | Disciplinare | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 100 | CAND-0795 | Gli associati | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 101 | CAND-0796 | Organi e Staff | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 102 | CAND-0800 | Relazione Annuale e Risorse | RECUSADA | IT-T10-039 | D80(i) PAGINA_DE_OUTRA_FONTE de IT-T10-039: PAGINA_DE_OUTRA_FONTE: pagina interna de Unaitalia (CAND-0269); a fonte e a organizacao, nao cada pagina. |
| 103 | CAND-0786 | adraxles.com | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 104 | CAND-0788 | eshop.wuerth.it | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 105 | CAND-0803 | paginesispa.it | RECUSADA | — | D80(i) NAO_E_FONTE: NAO_E_FONTE: link de rodape, loja, pagina de servico ou pagina solta recolhida pelo crawler. |
| 106 | CAND-0906 | Privacy | RECUSADA | — | D80(i) PAGINA_DE_SERVICO: regra PAGINA_DE_SERVICO casa no nome/URL («Privacy») |
| 107 | CAND-0942 | ARSARP Molise | RECUSADA | IT-T2-149 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T2-149: leitura a mao de 25/09: a casa do site arsarp.it ja e a fonte |
| 108 | CAND-1023 | DSA3 — Scienze Agrarie, Alimentari e Ambienta | RECUSADA | IT-T5-032 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T5-032: o mesmo endereco ja e a entrada de IT-T5-032 |
| 109 | CAND-1025 | Dip. Agraria, Univ. Sassari | RECUSADA | IT-T8-062 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T8-062: leitura a mao de 25/09: a casa do site agrariaweb.uniss.it ja e a fonte |
| 110 | CAND-1047 | SIDEA — Societa Italiana di Economia Agraria | RECUSADA | IT-T8-065 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T8-065: leitura a mao de 25/09: a casa do site sidea.org ja e a fonte |
| 111 | CAND-1050 | SOI — Societa di Orticoltura Italiana | NAO SEI | — | duplicada sem mae provada: o site soihs.it tem 3 fontes (IT-T1-023, IT-T8-064, IT-T8-066) e nenhuma e a mae provada |
| 112 | CAND-1052 | Societa Entomologica Italiana | RECUSADA | IT-T3-020 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T3-020: o mesmo endereco ja e a entrada de IT-T3-020 |
| 113 | CAND-1060 | Olivonews | RECUSADA | IT-T1-022 | D80(i) DUPLICADA_DA_ORGANIZACAO de IT-T1-022: leitura a mao de 25/09: a casa do site olivonews.it ja e a fonte |

| Parte | Candidata | Nome | Número no ensaio | Classe | Fontes do site / estado |
|---|---|---|---|---|---|
| (ii) | CAND-0525 | biostimulants.eu | EU-T12-002 | T12 | PAIS=EU · CAPABILITY_BLOCK |
| (ii) | CAND-0514 | croplife.org | INT-T12-001 | T12 | PAIS=INT · CAPABILITY_BLOCK |
| (ii) | CAND-0526 | fertilizerseurope.com | EU-T12-003 | T12 | PAIS=EU · CAPABILITY_BLOCK |
| (ii) | CAND-0640 | Benaki Phytopathological Institute (BPI) - Gr | GR-T5-001 | T5 | PAIS=GR · CAPABILITY_BLOCK |
| (ii) | CAND-0650 | Institut National de Recherche pour l'Agricul | FR-T5-001 | T5 | PAIS=FR · CAPABILITY_BLOCK |
| (ii) | CAND-0642 | International Maize and Wheat Improvement Cen | INT-T5-001 | T5 | PAIS=INT · CAPABILITY_BLOCK |
| (ii) | CAND-0635 | The Food and Agriculture Organization (FAO) | INT-T12-002 | T12 | PAIS=INT · CAPABILITY_BLOCK |
| (iii) | CAND-0858 | Linee guida SNPA | IT-T2-168 | T2 | IT-T2-108 · CANARY_PENDING |
| (iii) | CAND-0944 | ARSARP Molise — Pubblicazioni | IT-T2-169 | T2 | IT-T2-149 · CANARY_PENDING |
| (iii) | CAND-1027 | Dip. Agraria, Univ. Sassari — Tutti gli event | IT-T8-071 | T8 | IT-T8-062 · CANARY_PENDING |
