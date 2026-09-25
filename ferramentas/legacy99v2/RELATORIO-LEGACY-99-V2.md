# LEGACY-99 v2 — o código que faltava para as antigas voltarem

Ramo `legacy-99-v2`, a partir de `legacy-99-v1` @ 92d6b3c5. **Não instalado.** Missão: `auditoria-madrugada/missao-legacy-codigo.txt`.
Rede fechada por omissão (D41.3). A rede só se abriu para os canários autorizados, em rodadas de 1 fonte por domínio, com um contador que recusa o 6.º pedido ao mesmo domínio e o portão de consenso PASS IT antes de cada rodada.

## Em palavras simples

**O resultado que importa: com este código, 11 fontes antigas passam a ser elegíveis**, e já estão na tabela do coletor, por isso não precisam do onboarding. Antes eram 0 destas 32. Mais 1 passa a régua, mas pede revisão humana.

| Bloco | O que faz | Resultado medido (cópia do vivo 290e7349) |
|---|---|---|
| **A. Importar do coletor** | o Curator aprende o contrato que o coletor já executa: a mesma aquisição, com a origem escrita à parte do passado. Depois a fonte vai ao canário com as réguas de hoje. **Importar nunca aprova.** | **21 HTML importadas → 11 elegíveis**, 1 elegível mas com revisão humana, 9 não passam (5 «não é notícia», 1 poucas ligações, 1 sem corpo útil, 1 lista vazia, 1 robots sem resposta). 8 fontes só existem como `case` e 3 são PDF: ficam de fora, com o nome |
| **B. YouTube pela rota do canal** | o contrato do Curator passa a ser o do coletor (página do canal, permitida). O canário do Curator aprende a prová-la | **1 canal real** (IT-T10-017, 2 pedidos): **a rota passa, o canário passa, a régua não aprova** («falta ITEM_ABERTO, BODY_UTIL»). A régua de hoje só aprova notícias HTML. **Um vídeo nunca passa sem uma decisão de régua** |
| **C. Re-check das antigas** | o robô volta a medir sozinho as READY_LEGACY: 10 por dia, 1 por domínio, pelo caminho oficial | sem rede: hoje apanharia **26** (15 domínios). O 1.º lote tem 10, e todas passam em ~3 dias |
| **D. O defeito dos colchetes** | um link malformado na página já não derruba o reparo | reproduzido por teste e corrigido no dono único das ligações |

## ⚠️ Três coisas que correram mal, e já estão tratadas

1. **O meu import tinha um defeito que o ensaio apanhou.** A linha da tabela do coletor não traz a «identidade» (o coletor gera-a). 14 das 21 rebentaram no canário do Curator com `KeyError: 'IDENTITY'`. Os meus testes não o viram, porque os contratos falsos não chegavam ao canário.
   - **Conserto:** o import leva a identidade, pela ordem: a da linha, depois a do Curator, depois a que o coletor gera (lida pelo dono, `italy_contracts.mjs`).
   - Sem identidade, não importa.
   - Há teste e mutante para isto (A10). Depois do conserto: **11 elegíveis**.
2. **Na 1.ª corrida da mutação, um mutante (C6: «o re-check liga-se por omissão») fez os testes antigos do supervisor chamar o `remedir` verdadeiro.** Escreveu nos livros **desta árvore** (não no vivo, e sem rede): um lote de 10.
   - Guardei o estado, o diff e uma cópia (`INCIDENTE-mutante-C6-escreveu-livros-da-arvore.diff`) e repus só esses 2 ficheiros.
   - Agora os testes antigos têm um fio de tropeçar (o `remedir` verdadeiro rebenta num teste).
   - O mutador fotografa os livros antes de cada mutante e acusa quem escrever: **0 nas corridas seguintes**.
3. **Aprendido na PROVA-ROTA-CICLO e aplicado aqui:** o re-check (C) **escreve no livro**, por isso está **desligado por omissão** e só o serviço (`main()`) o liga. Há `--sem-revalidar-legacy` para o desligar.

## O que mudou (ficheiro)

| Ficheiro | O quê |
|---|---|
| `curadoria/importar_do_coletor.py` (novo) | `planear` (quem importa / quem fica e porquê), `contrato_importado` (puro; exige impressão igual à da linha e identidade), `aplicar` (escrita atómica + `ready_split.remedir`) |
| `curadoria/canario.py` | D: `hrefs_da_entrada` deixa de fora o que não é endereço. B: `url_da_rota`, `canario_youtube_canal`, controlo positivo do lote do canal |
| `curadoria/worker.py` | B: o VALIDATE_ROUTE pergunta ao robots pela rota do contrato (`url_da_rota`); o canário do canal para o adaptador |
| `curadoria/escrever_contratos.py` | B: o molde novo de YouTube nasce na rota do canal, igual à linha do coletor (a mesma impressão sha256) |
| `curadoria/gatilho_discovery.py` | C: `candidatas_legacy`, `lote_legacy`, `revalidar_legacy_se_devido` |
| `curadoria/supervisor.py` | C: `_hook_revalidar_legacy`, desligado por omissão e ligado pelo `main()` |

**A proveniência, a condição que faltava:** `docs/operacao/OUT-OF-FLOW-LEGACY-DECISION-V1.md` recusava importar porque «o contrato de hoje não separa proveniência da importação atual da aquisição histórica». O contrato importado leva agora dois blocos separados:
- `PROVENIENCIA_DO_CONTRATO`: IMPORTADO_DO_COLETOR, data, tabela, sha256 da linha, aquisição anterior no Curator;
- `AQUISICAO_HISTORICA`: `PROVADA: false`, com a data da promoção antiga e a nota «CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN».

## Provas

- **Testes novos: 37**, todos sem rede e sem livros reais:
  - `test_legacy_colchetes` (2);
  - `test_legacy_recheck` (12, incluindo o supervisor);
  - `test_importar_do_coletor` (23);
  - mais os ajustes em `test_onboardar_rotas_provadas`.
- **Mutação: C+D 11/11, A+B 15/15**. Nas corridas finais, 0 mutantes escreveram num livro (`MUTACAO-CD.json`, `MUTACAO-AB.json`).
- **Regressão:** 31 módulos que tocam no que mudou. **461 testes, 2 falhas, as mesmas 2 na base** (`test_collection_gate` → `onda_web.py` por declarar, vindo da integra-onda2; `test_reconciliar_livros` → censo dos livros reais). **0 novas.** Os livros ficaram iguais antes e depois das duas corridas.
- **Ensaio** (`ENSAIO-*`): cópia fiel do vivo **290e7349** (a instalação da 2.ª onda, de hoje) + este código, com sha256 dos livros em `ENSAIO-0`.
  1. Plano sem rede: IMPORTA=62 (21 HTML + 41 YouTube), FICA=11 (8 `case` + 3 PDF).
  2. Aplicar as 62 sem rede: 62 em CANARY_PENDING, **0 READY**.
  3. Canário das 21 HTML: 61 pedidos, no máximo 3 por domínio. Resultado: **11 elegíveis**, 1 READY com revisão humana, 9 falham.
  4. Um canal YouTube real: 2 pedidos; rota e canário OK; régua PASS_PARCIAL.

## Plano de instalação (depois do MICRO; quem instala é o coordenador; um escritor no vivo)

O código vai por `git merge --ff-only` deste ramo, se o vivo estiver na base. Se não estiver, primeiro junta-se ao vivo, e desfaz-se com `git reset --keep <antes>`. Reiniciar o supervisor liga o **C** (re-check 10/24h). Para não o ligar: `--sem-revalidar-legacy`.

**A no vivo** (bot quieto; guardar antes `curadoria/italy_contracts_curator.json` e os `LIFECYCLE-*`):
```
py curadoria/importar_do_coletor.py                       # mostra: esperado IMPORTA=62 FICA=11
py curadoria/importar_do_coletor.py --aplicar --ids=IT-T1-005,IT-T1-007,IT-T1-009,IT-T1-010,IT-T1-011,IT-T1-016,IT-T1-018,IT-T1-022,IT-T10-009,IT-T11-005,IT-T2-006,IT-T2-008,IT-T5-006,IT-T5-015,IT-T5-024,IT-T5-025,IT-T5-027,IT-T5-030,IT-T5-033,IT-T9-009,IT-T9-011
```
⚠️ **Só as 21 HTML** (a lista é o `SEM_CONTRATO_NO_CURATOR` do plano de 25/09, conferida contra `ENSAIO-0`; confirmar com o plano do momento antes de correr). Depois, o worker do robô mede-as sozinho. Mas o worker **não** tem o contador por domínio desta cópia: com as 21 de uma vez, um domínio com 2-3 fontes pode passar de 5 pedidos. **Recomendo lotes de 1 fonte por domínio**, como no ensaio (a ronda 1 tinha 19 e a ronda 2 tinha 2).

**B (YouTube) no vivo: NÃO importar ainda.** Passariam de READY_LEGACY a «falhou» sem ganho, porque a régua não aprova vídeo, e não sei se a onda social (D35.4) lê esse estado. O molde novo e o canário ficam instalados, para quando houver a decisão da régua para vídeo (ramo de vídeo nos 4 passos, como o PDF dos boletins).

**Desfazer A:** repor o `italy_contracts_curator.json` guardado. As fontes voltam ao estado de antes por uma transição nova no livro (append-only).

## O que isto não prova

- Que as 11 dão SIM: é prova de rota e de corpo, não de régua de universo.
- Que o vivo, com o worker a correr a fila inteira, dá os mesmos 11. A cópia correu só estas fontes, sem concorrência.
- As 8 `case` e as 3 PDF continuam no plano dos boletins (declarar o `case` como contrato e o ramo PDF na régua). Não foram feitas.
