# RELATÓRIO — T1 · PRAZO DE VALIDADE (TTL) PARA AS FONTES MUTABLE

Branch `ttl-mutable-v1`, a partir de `recollection-prova-v2` @ `0ac7947b`, 2026-09-23.
Sem rede, nada colhido, nada na Sala, nenhum serviço vivo tocado.

## ENTREGA

```
ORIGEM_MUTABLE     know-how §167-3 / RELATORIO-RECOLLECTION.md (RECOLLECTION-V1, 22/09):
                   as datas que os próprios artigos declaram — Riunite 19/26 editados > 24 h
                   depois (máx 72 d), Balsamico 3/7 (27 d), Zootecnica 3/4 (7,2 d)

TABELA X           Riunite + Zootecnica · 23 edições depois da 1.ª captura · 0 PERDIDAS em todas
                   (revisitas por corrida · atraso máximo da edição)
                                 corrida diária        corrida a cada 6 h
                   ATUAL         37,2 · 0,7 d          37,3 · 0,2 d
                   TTL 1 d       37,2 · 0,7 d           9,3 · 0,9 d
                   TTL 3 d       12,4 · 2,7 d           3,1 · 2,3 d     ← escolhido
                   TTL 7 d        5,3 · 6,7 d           1,3 · 6,3 d
                   TTL 14 d       2,6 · 13,7 d          0,7 · 13,3 d
                   CURVA          4,1 · 12,5 d          1,2 · 7,5 d
                   FALSE_DOCUMENT_UNCHANGED (dias-edição por ver, as 3 fontes, diária):
                   ATUAL 13,5 · TTL 3 d 45,5 · TTL 7 d 112,5 · CURVA 50,5

X_ESCOLHIDO        3 dias (259 200 s). Poupa ~2/3 na cadência diária e ~92% a cada 6 h;
                   o atraso tem tecto no prazo, em qualquer cadência. A CURVA poupa mais,
                   mas atrasa até 12,5 d e exige memória nova. Sem saber O QUE as edições
                   mudam, preferiu-se o atraso curto.
APLICADO           YES — regra em decidirSobreDetalhe; prazo só em IT-T7-017 e IT-T10-022.
                   MUTABLE sem prazo (boletins, Balsamico) continua a revisitar sempre.
PROVA_OFFLINE      provas/ttl_mutable_local.mjs 12/0: edição apanhada na 1.ª corrida depois
                   do prazo; controlo sem prazo revisitado sempre; 15 → 6 pedidos a matérias.
                   Mais: incrementalidade_test 31/0 (+5) · recollection_test 31/0 ·
                   paridade_test 32/0 · motor_de_rota_test 47/0 · paridade_duas_rodadas 13/0 ·
                   recollection_http_local 15/0 · recollection_indice_local 13/0 ·
                   italy_contract_test 349/76 — os mesmos 76 da base, por nome
MUTATION           5/5 mortos pela suíte dona da regra (3 também pela prova offline);
                   red teams da R1: 12/12 e 12/12 pela dona (M8 traduzido para a linha nova)
FINAL_HEAD = REMOTE_HEAD   na mensagem de entrega
SYSTEM_MAP_CHECK   na mensagem de entrega
```

## Ressalvas

- Cada página declara só a ÚLTIMA modificação: o número de edições é um mínimo.
- A cadência das corridas em produção é NÃO SEI — daí as duas colunas.
- O que as edições mudam é NÃO SEI (só se vêem as datas). Se a Coordenação souber que
  estas edições importam no próprio dia, o prazo desce para 1 dia (corrida a cada 6 h:
  37 → 9 revisitas, atraso ≤ 0,9 d) — é uma linha na tabela, sem código.
- IT-T7-042 (Balsamico) tem o mesmo perfil e ficou sem prazo (fora da coorte e do briefing).
- Erro meu, apanhado: o script de mutação restaurou um ficheiro pelo Git e apagou a
  mudança por commitar; salvou-a uma cópia feita antes. Nada perdido.
