# CANÁRIO ATUAL — o item real que estamos seguindo (atualizar a cada mudança de elo)

Regra do dono (28/09 ~13:40): "FAZER UM ITEM REAL SAIR DA FONTE E CHEGAR AO PORTAL", com caminho de volta até a prova original. Peças prontas ≠ SINTONIA funcionando. Nada de frente nova que não ajude este item.

## O ITEM
- **Sala:** `derived:1149` · T5 · fonte `IT-T5-111` (CREA)
- **Fonte:** https://www.crea.gov.it/web/guest/-/xylella-fastidiosa-dalla-ricerca-crea-nuove-strategie-per-l-olivicoltura
- **Coletado AUTOMATICAMENTE:** coleta contínua, ciclo 21 (28/09 08:20 BRT), corrida `IT-T5-2026-09-28-112058-aacf19302d12b1b0`
- **RAW** 2272 · sha256 `f2158520f2362956…` · document_key `IT-T5-111:URL:web/guest/-/xylella-fastidiosa-…` · FORWARD_IDENTIFIED · pousado na Sala 28/09 08:22 BRT (`pertence ao universo v10`)
- **Conteúdo (medido no texto da Sala):** comunicado CREA "22 giu 2026"; resultados de projetos Masaf sobre Xylella fastidiosa em oliveira; 200 genótipos de oliveira selecionados "nelle aree colpite del Salento"; controle do vetor *Philaenus spumarius* (sputacchina); "due nuove specie di nematodi parassiti della sputacchina" (= agentes de controle, NÃO problema); evento no CIHEAM Bari.

## ELOS
| elo | estado | prova |
|---|---|---|
| FONTE → COLETA automática | 🟢 | CICLOS.ndjson ciclo 21; egresso IT; prova-teto PASS |
| RAW → DERIVAÇÃO | 🟢 | raw_asset 2272 → derived 1149 |
| ADMISSION → SALA | 🟢 (com ressalva) | sala_de_espera_atual derived:1149 WAITING |
| **Collection: tempo / lugar / problema do item** | 🔴 **PRIMEIRO VERMELHO** | Sala: PUBLISHED_AT = NAO SEI (texto diz "22 giu 2026"); FACT_LOCATION = NAO SEI (texto diz "aree colpite del Salento"); PROBLEMA ambíguo "xylella, nematode" (nematoides são agentes de controle) |
| INTELLIGENCE (cópia descartável, 28/09 10:48) | 🟡 rodou, item não vira objeto | motor e24139702 sobre export delta (22 itens desde 00:00): 1149 = CAP-WIN NOT_POSSIBLE (INT-LAW-091: PROBLEMA e REGIAO NAO SEI), CAP-SCI FORA (sem DOI); pote v2 `IR-04a259421a451a8aa778`: 1149 só como LACUNA |
| POTE | 🔴 depois | pote EXPERIMENTAL·NAO_PARA_CLIENTE; D126 exige LIBERADO_PARA_CLIENTE + gates + LAB aprova preview |
| CASCO / PREVIEW / PORTAL | 🔴 depois | produção Vercel = 14/09 |

Pasta da corrida na cópia: `C:/Users/London1/sintonia-sala-italia/canario-1149/20260928-1046/` (sala.dump, export_delta.sql, sala-delta.json, MOTOR.json, POTE.json).

## QUEM ESTÁ RESOLVENDO O PRIMEIRO VERMELHO
Equipe nuvem `nuvem-canario-1149-v1` (Collection reprocessa SÓ o item — caminho (b), já decidido pelo coordenador para o myfruit).

## QUAL PROVA FAZ O ELO FICAR VERDE
Nova revisão de `derived:1149` (numa cópia descartável da Sala, pela porta canônica de revisões) com:
- PUBLISHED_AT = 2026-06-22, base = trecho do texto;
- FACT_LOCATION = Salento (se a lei D112 aceitar o trecho "nelle aree colpite del Salento" como sustentação explícita; senão NÃO SEI com o porquê);
- PROBLEMA = Xylella fastidiosa (+ vetor Philaenus spumarius), nematoides como AGENTE DE CONTROLE, nunca problema;
e o motor, rodado de novo sobre a cópia, devolve para 1149 algo diferente de "NOT_POSSIBLE por PROBLEMA/REGIAO NAO SEI" (ou o porquê honesto do próximo elo).

## ESTADOS CONHECIDOS / NÃO RESOLVIDOS / NÃO BLOQUEIAM O CANÁRIO
- System Map: IMPRESSAO_DO_CARIMBO = DIFERENTE já na cópia limpa da entrega do lote 8 (a2aa73f42). NÃO RESOLVIDO.
- 3 grupos de teste falham só neste Windows (CRLF / core.autocrlf=true): test_ligacao_adama I3, test_cruzamentos_max X4, test_acervo A5. Numa cópia com autocrlf=false, os dois primeiros passam; A5 NÃO SEI. NÃO RESOLVIDO.
- "0 livros vivos tocados" no lote 8: a 1ª conferência NÃO provou (lista longa demais para o git). Refeita em seguida por comparação de listas (135 arquivos do lote × 231 livros = 0 em comum) — prova indireta, registrada.
- Sala recebendo ruído por T5: dos 22 itens pousados em 28/09, leitura do coordenador (modelo, NÃO humana) ≈ 8 agro e ≈ 14 não-agro (ENEA: biomedicina espacial, conferência polar, qualidade do ar, nanoinovação…). A MEDIR pelo LAB.
