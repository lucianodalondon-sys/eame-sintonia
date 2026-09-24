# P5 · PESSOAS PELO SITE OFICIAL — PARADA POR ORDEM (D25, 23/09 ~19:20)

Branch `pessoas-docentes-v1` (a partir de `origin/unificacao-v1`). A missão foi **parada a meio** por
ordem da coordenação: a Big Collection vem primeiro (D25). Nada foi registado na fila de candidatas.

## ENTREGA

```
ESTADO                 = PARADA (HARD STOP por D25) — nao concluida
CANDIDATAS_NOVAS       = 0   (nenhum registo na porta canonica)
SEMENTES               = 27 planeadas → 13 activas (9 ja lidas pela P4, 4 Veterinaria + ISPAAM fora por decisao do dono 18:50)
CASAS_TENTADAS         = 19 (inclui 2 de Veterinaria lidas ANTES da correcao do dono: bca.unipd, maps.unipd — 30 paginas, 0 perfis)
PESSOAS_LIDAS          = 315 paginas oficiais de pessoas
PAGINAS_COM_PERFIL     = 8
PERFIS_ACHADOS         = 9 (LinkedIn 2, YouTube 2, ResearchGate 5); 0 ja conhecidos na casa
PORTOES_DE_EGRESSO     = 22 PASS IT · 1 BLOCKED (UNKNOWN, antes do 1.o pedido) · ensaio 17:57-18:03 BLOCKED BR x6 com 0 pedidos
PEDIDO_FORA_DE_IT      = 0
BANCO_DE_TESTE         = nenhum aberto
TESTES                 = tests/test_pessoas_docentes.py 5 OK + 4 saltados (so correm quando houver DECISOES-P5-V1.json)
```

## Os 9 perfis achados e a decisão PROPOSTA (não aplicada)

| Pessoa · casa | Perfil | Proposta | Porquê |
|---|---|---|---|
| Giulio Senes · Unimi DISAA (AGRI-04/C costruzioni rurali e territorio agroforestale) | linkedin.com/in/giulio-senes-81515321 | **ENTRA** | a página oficial `unimi.it/it/ugov/rubrica/person0000016159` liga-o; tema agronómico |
| Simon Pierce · Unimi DISAA (botanica ambientale e applicata) | youtube.com/channel/UCcDDOA0UU5DmHcEDCUOzVFw | **ENTRA** | a página oficial `…/person0000017592` põe o canal no campo «Sito web»; frequência e conteúdo NÃO medidos (a lista de vídeos só sai pela Data API, chave só no GitHub) |
| Bianca Castiglioni · CNR IBBA | linkedin.com/in/bianca-castiglioni-12302a48 | FICA_FORA | prova boa («Linkedin:» na ficha oficial), mas o tema é genómica de bovinos de leite — zootecnia, fora do foco dado pelo dono às 18:50. Reversível |
| Carmelo Cannarella · CNR ISB | youtube.com/@cnrisb9684 | FICA_FORA | é o canal do INSTITUTO (logótipo do YouTube no fim da página), não da pessoa |
| Basile, Bosso (ISAFOM), Castiglioni (IBBA), Quaglino, Giupponi (Unimi) | 5 × researchgate.net/profile | FICA_FORA | a missão só aceita ResearchGate se publicar vídeo; não há rota permitida para o verificar |

## O que ficou por fazer (para retomar depois da Big Collection)

1. **2.ª volta interrompida** a seguir a `disaa.unimi.it` (parei o processo pelo PID quando chegou a correcção
   da Veterinária; o portão «depois» dessa corrida não ficou escrito — o último vigia, 22:05 UTC, foi PASS IT).
   Faltam, com a ferramenta já afinada (`--descobrir --refazer`): agraria.unirc, dafnae.unipd (não abriu na 1.ª,
   abre agora), tesaf.unipd, di3a.unict (a listagem é JS: `docenti.smartedu.unict.it`), d3a.univpm, di4a.uniud
   (perfis em `@@cercapersone_detail`), ibbr.cnr (≈160 pessoas em `/ibbr/info/people/<nome>` — a 1.ª volta só
   leu 1), isafom.cnr (11 de 91 por ler), iret.cnr, ibba.cnr (52 fichas `/staff/<nome>/`, a 1.ª leu 3).
   Declaradas sem casa: `www.dafne.unifg.it` (DNS não resolve), `www.ipsp.cnr.it` (403 e certificado recusado).
2. **Escrever `DECISOES-P5-V1.json`** com a tabela acima e o que a 2.ª volta achar; depois
   `--registar` (porta canónica, dedupe contra esta linha, P1, P2, YT3 e a fila da P4).
3. **System Map**: declarar a peça `scripts/pessoas_docentes/` (como a C-CANAIS-PESSOAS da YT3) e correr a cadeia.
4. Know-how: o filão é a ficha do CNR em WordPress com campo «Linkedin:» (IBBA, ISAFOM) e o campo «Sito web»
   da rubrica da Unimi; as páginas de docente das universidades quase nunca ligam perfil (0 em 146 fora da Unimi).

## Veterinária / saúde animal registadas hoje

Nenhuma candidata desse tipo foi registada por esta bancada hoje (P5: 0 registos; YT3: 14 canais de
organizações agrícolas, nenhum de Veterinária/IZS/saúde animal — a UNAITALIA, CAND-0490, é a associação da
fileira avícola: produção, não saúde animal; fica aqui escrita para quem decidir).

## P5b · 24/09 — retomada e ESTACIONADA (pausa de memória)

- Fila da produção trazida (merge de `origin/bc4-correcoes-v1`, 906 linhas); 2.ª volta completa com VPN IT (39 portões PASS IT): 574 páginas de pessoas, 69 perfis.
- `DECISOES-P5-V1.json`: 8 ENTRA, 59 FICA_FORA com motivo (D26 aplicada: 7 da área animal fora).
- **Registadas pela porta canónica: CAND-0907..0914** — LinkedIn: Tania Bobbo, Giovanna Frugis, Stefano Gattolin, Barbara Menin, Cristian Perna, Francesca Sparvoli (CNR IBBA), Giulio Senes (Unimi DISAA); YouTube: Simon Pierce (Unimi DISAA). 906 linhas antigas inalteradas; dedupe por URL e por slug contra produção, P1/P1d, P2, P4/P4b, YT3 (0 colisões).
- Provas: as 8 páginas oficiais estão no ramo em `scripts/pessoas_docentes/evidencia/`; as 777 páginas lidas estão listadas com caminho e sha256 em `EVIDENCIA-P5.json` (ficheiros em `%TEMP%\p5-evidencia`).
- Peça `C-PESSOAS-DOCENTES` declarada em `system-map/data/architecture.declared.json`.

**FALTA AO RETOMAR:** correr a cadeia do System Map com o `LOCK-PESADO.txt` (REGERAR → commit → VALIDAR), know-how § e memória; depois entrega curta.

## P5b · 24/09 tarde — ESTACIONADA de novo (pausa de memória)

- Marca D29 (temas de janela de cultura na página oficial) feita e testada; a leitura honesta: nenhuma das 8 registadas tem sinal forte de D29 (o «clima» que acendia era um bloco de projeto repetido nas fichas do IBBA).
- 5 casas novas D29 na lista (FEM, DiSSPA Bari, SAAF Palermo, DBT Verona, Agraria Sassari) — NÃO visitadas: VPN fora da Itália de 13:05 a pelo menos 14:17 (7 portões BLOCKED, 0 pedidos).
- Mapa: REGERAR feito (ae465951); VALIDAR reprovou só em P9 (as 8 páginas de prova sem peça). Já ligadas à peça C-PESSOAS-DOCENTES; falta regerar e validar outra vez.

**FALTA AO RETOMAR:** com LOCK-PESADO.txt, cadeia REGERAR → commit → VALIDAR (esperado PASS); com VPN IT, `--descobrir` das 5 casas D29, decisões, `--registar` sobre a fila atual; know-how § e entrega.

## P5b · 24/09 noite — as 5 casas D29

- Portão de consenso trazido (`superficie/rede.py` de `origin/egresso-consenso-v1`): o antigo só lia o ipinfo.io, que estava em 429, e dava UNKNOWN falso. A partir daí, 12 portões PASS IT, 269 pedidos.
- Fondazione Edmund Mach: o `robots.txt` do site proíbe `/La-Fondazione/Personale` → respeitado, 0 pessoas.
- DiSSPA Bari: a página do departamento não abre (urllib URLError; curl 302 sem corpo) → declarada, sem insistir.
- SAAF Palermo: 163 pessoas lidas, 0 perfis. Agraria Sassari: a casa só liga à rubrica geral da Uniss; 2 pessoas, 0 perfis.
- Biotecnologie Verona: 74 pessoas, 1 LinkedIn → **CAND-0915 Claudio Zaccone** (AGRI-06/B chimica agraria, ciência do solo; sinal D29 AGROMETEO: «stress idrico delle colture» na ficha). 2 ResearchGate FICA_FORA.
- Total P5: **9 candidatas (CAND-0907..0915)**, fila 906 → 915, 0 linhas antigas alteradas; 1027 páginas com sha256 em `EVIDENCIA-P5.json`, as 9 páginas-prova no ramo.
