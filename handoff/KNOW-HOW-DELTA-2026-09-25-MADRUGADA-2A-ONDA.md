# KNOW-HOW DELTA — 2026-09-25 · madrugada da 2.ª onda (coordenador Hermes)

> Delta interino (regra do Know-How: um único `SINTONIA-EAME-KNOW-HOW.md` na raiz; deltas em `handoff/`).
> Histórico medido, não estado atual — revalidar antes de usar. Fonte das medições: `auditoria-madrugada/HANDOFF-VIVO.md` e `DECISOES-DONO-2026-09-23.md` (D32–D50).

## O que ficou provado (com SHA)

| quando | o quê | prova |
|---|---|---|
| 25/09 01:50 | R1 instalada no robô (25 READY revistas; 19 devolvidas com motivo) | `5ba9647e`; recontagem no vivo READY 143→183 (`reparo-fontes-v2 0d4f4da7`) |
| 25/09 02:43 | FILA-ÚNICA instalada (932→1199 candidatas; 932 antigas idênticas; 0 duplicados) | `7b769819` |
| 25/09 02:45 | Régua T1 (janelas por cultura) instalada; prova cega de positivos 16/16 | `7cdb7ea4` |
| 25/09 08:00 | Pacote INTEGRA instalado: teto D38 **por domínio** (livro do teto por onda), D40 (1.º alvo não coletado + até 3 novos), ponte que onboarda (canário lê o contrato do disco + sha256), prova-teto independente | `d235c32a` (fast-forward de `7cdb7ea4`) |
| 25/09 ~08:00 | 17 fontes entraram no coletor (FONTES 193→210) pela prova de rota de 25/09 06:38 (vale até 02/10) | `regras/italy_contracts_onboarded.json` |
| 25/09 ~08:05 | Coorte da 2.ª onda CONGELADA: 28 (22 correm, 80 pedidos, máx. 5/domínio; prova-teto PASS) | `290e7349`, COORTE_SHA256 `06f87b97…` |

## Lições (regras que a noite ensinou)

1. **O teto "5 por site" contava por FONTE, não por DOMÍNIO.** cia.it recebeu 16 pedidos na 1.ª onda sem nenhuma trava disparar. D38: por domínio registável, por corrida; nunca separar fontes em corridas para contornar. **Um limite só existe se houver um contador único e uma prova independente que o confira depois** (a PROVA-TETO lê o livro do transporte, não o contador do disjuntor).
2. **Coleta que visita e volta vazia é o maior desperdício:** 12/18 fontes da 1.ª onda pediam 1 só alvo (o 1.º link do índice) que já estava no livro. D40 (dedupe antes do pedido + até 3 novos) mediu 4→27–30 documentos novos por corrida.
3. **O robô de fontes aprovar ≠ a coleta poder usar.** Funil medido (25/09 06:40): READY 183 → fora do portão 110 (99 READY_LEGACY) → elegíveis 73 → prontas 18. Os buracos eram: ponte que importava contratos mas nunca onboardava (`onboardar_rotas_provadas.py` sem chamador); canário que provava o contrato do Git HEAD em vez do contrato do disco (14/17 trocados); coletor web só registado em T7/T10; re-check periódico que só olha ELIGIBLE (READY_LEGACY nunca volta; `gatilho_discovery.py:228`). **Antes de dizer "faltam fontes", medir o funil etapa a etapa.**
4. **As janelas de cultura não publicam como "lista → notícia".** Canário de 30 janelas: 8 "página = boletim", 6 JS, 3 PDF, 13 outros. D42: PDF pela rota existente; "página = boletim" com identidade fonte:BOLETIM:data e dedupe por sha256 da parte do boletim; sem data = UNKNOWN (nunca a data de coleta).
5. **A régua não era o bloqueio da Sala para T1/T2** (aprova 41/41 T2, 51/55 T1 nos boletins): o bloqueio era o que o coletor guardou (páginas de entrada). As 7 agências T2 da coorte apontam notícias gerais — clima T2 **não provado** até os contratos apontarem boletins.
6. **O robots.txt era lido pela metade** (só a 1.ª regra; guardado cortado aos 120 caracteres). D34/D39: leitor único RFC 9309; HTML no robots e 403 = recusa com estados próprios.
7. **"Vermelho herdado" pode esconder um teste que nunca correu:** o 2b5 da Sala esteve vermelho 11 dias porque a trava de nomes de banco recusava arrancar (classe B), não por defeito da Sala (91/91 quando corre).
8. **O validador do mapa depende do NOME DO RAMO** (`NODES[…].facts` = "branch <nome>"): o mesmo commit passa num ramo e reprova noutro/destacado. Instalar por fast-forward num ramo de nome diferente reprova P1_SEM_DRIFT sem defeito real. Conserto pela causa (D50), sem enfraquecer o validador.
9. **Cópia do robô com a fila inteira da produção vai à rede sozinha** (164 pedidos a 52 sites em 10 min numa cópia). D41.3: cópia começa com rede FECHADA; rede só com autorização, fila filtrada e D38 ativo.
10. **Memória do PC partilhado é recurso crítico:** 2 cadeias do mapa mortas pelo sistema. Regra: trabalho pesado só com LOCK-PESADO e ≥5 GB livres; `LOCK-PRIORIDADE.txt` para o caminho crítico; desligar Postgres de prova no fim.
11. **Nuvem (crédito Claude, D50):** serve para código/mapa/testes sobre o GitHub; nunca coleta, livros vivos ou VPN. Piloto: mapa regerado e validado em ~10 min, verificado localmente (carimbo IGUAL, VALIDAR PASS). `claude --cloud` exige terminal interativo (pty).

## Passo anterior — CUMPRIDO (25/09 08:05)
Instalação INTEGRA + onboarding de 17 + congelamento da coorte da 2.ª onda (28).

## Próximo passo autorizado (D47/D50)
MICRO-V3 real (6 fontes fixadas antes da rede; ≥2 SIM e >16,7%) → só então 2.ª onda web (28) → prova-teto sobre o livro → instalar CONTRATO-44 (+23 prontas em cópia) e RECEITA-T8 (+10) para a 3.ª onda.

KNOW_HOW_DELTA: ENTREGUE COMO DELTA · handoff/KNOW-HOW-DELTA-2026-09-25-MADRUGADA-2A-ONDA.md
