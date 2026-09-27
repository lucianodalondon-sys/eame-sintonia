# INT-R7-CAPS — CAP-WIN + CAP-SCI no motor, D112 (Puglia), saída para o pote v2 · EXPERIMENTAL / NAO_PARA_CLIENTE

Ramo `claude/int-r7-caps-motor-5rwp2n`. Base: G0/v4 + CAP-WIN (já no ramo) + merge de
`claude/cap-sci-intelligence-fjqmyd` (`df08010`). Rede externa: nenhuma (só GitHub). Livros vivos: **não tocados**.

## O que fiz

1. **Merge CAP-SCI** (`df08010`): o único conflito com significado foi o mapa declarado → **união** das peças
   (`C-INT-CAP-SCI`, `C-PROVA-CAP-SCI-MUTACAO` ao lado de `C-INT-CAP-WIN`); os gerados foram refeitos pela cadeia.
2. **Motor das capacidades** — `motor/motor_das_capacidades.py`: **uma** corrida G0/v4 (`:722`) e o **mesmo** livro
   para as duas capacidades (`:744`, `:745`) → um `INTELLIGENCE_RUN_ID`, uma LINEAGE, nenhum contador duplicado
   (mutante M28 prova). Conflitos resolvidos pelo significado, declarados:
   - `URL`/`DOCUMENT_ID` **não são READY** (a CAP-WIN lia `item.URL`; a CAP-SCI recusa campo fora do READY) →
     vêm do RAW (`raw_asset.source_url`/`document_key`) pelo `RAW_OBSERVATION_ID` (`:169`, `:468`). Nunca cunhados.
   - `JANELA_DECLARADA` não está em `CAMPOS_READY` → viaja **ao lado** do READY e só a CAP-WIN a lê.
   - **Triagem** pelo FATO (`:298`): estudo declarado (DOI/TRIAL/espécie) → CAP-SCI; resto → CAP-WIN. Ganchos
     `cap_win.julgar(fora=)` (`motor/cap_win.py:750`, `:774`) e `capacidade_cientifica.julgar(triados_fora=)`
     (`motor/capacidade_cientifica.py:697`, `:725`). **Estudo nunca vira janela** (o portão `:824` reprova).
3. **D112** (verbatim da missão; **não está escrita no repo** → `D112` em `:99`):
   (a) lugar só com origem `ESCRITO`/`CITADO`, pela lei que já existe `leis/lugar_do_fato.sustenta_fato` (`:239`, `:266`);
   (b) `ENTITY_SOURCE` em toda chave (`:461`); (c) sem evidência = NAO SEI; (d) `DA_FONTE` × `INTERPRETACAO_DO_SISTEMA`
   em todo objeto e relação; (e,f,g) `relacoes` (`:353`): `MESMA_REDACAO` (N aplicações/1 instituição),
   `DIVERGENT` (`UNRESOLVED`; só pode **baixar** um ACT_NOW, `:530`), `TEMPORAL_CHANGE` (`NAO_PROVA: MUDANCA_NO_CAMPO`).
4. **Saída para o pote v2** (contrato do gerador `ce775ff5`, `:89`): `INTELLIGENCE_RUN_ID` **primeira chave**
   (`:776`), prova com `URL`, `DOCUMENT_ID`, `PUBLICADO_EM` = `PUBLISHED_AT` (`:482`), `FACT_TIME` da corrida;
   portão próprio `conferir_saida` (`:812`). Contrato declarado em `RUNBOOK-R7.md` §6. Espécie: o juízo viaja como
   `SINAL` (o pote não tem `ANALYTIC_JUDGMENT`; decisão do dono do pote).
5. **RUNBOOK-R7.md**: export da CÓPIA com `begin transaction read only` + `PGOPTIONS=default_transaction_read_only=on`
   (`motor/r7_export_da_copia.sql`), motor, gerador; e o que cada capacidade tem de devolver (ARIF/APOL, estudos).

## Provas

- **Gerador de verdade** (`provas/int_r7/aceite_pelo_gerador.py`, tirado do objeto git `ce775ff5`, sem cópia):
  aceita; `windows` 1 · `science` 2 · `future` 1 · `sources` 3; 1 recusado à vista (EST-02 sem `DOCUMENT_ID`).
- **Cópia descartável, esquema real** (`provas/int_r7/E2E-COPIA-DESCARTAVEL.json`): migrations 32 PASS, semeada
  pelos donos (`pousar`/`rever`), export `READ_ONLY=on`, `INSERT` recusado na mesma sessão, motor = mesma resposta
  da fixture, pote idem. (Rodado como usuário não-root; como root o teste S1 salta com NAO SEI.)
- **Testes**: `tests/test_motor_das_capacidades.py` — 64 (1 salta como root). CAP-WIN 56, CAP-SCI 49 continuam OK.
- **Mutação**: `provas/int_r7/mutantes.py` **32/32 mortos** (M19, M20, M30 sobreviveram na 1.ª passagem → 3 testes
  novos; M19 estava plantado de forma equivalente e foi reescrito para o defeito real). CAP-WIN 22/22, CAP-SCI 22/22 de novo.

## Bateria por NOME (rede fechada, cada módulo num subprocesso, cópias limpas)

| | árvore | módulos | testes | falhas |
|---|---|---|---|---|
| ANTES | `df08010` (merge) | 258 | 5981 | 128 |
| DEPOIS | `b1a2f09` | 259 | 6045 | 127 |

**Novas: 0.** Sumida: `test_o_controle_separa_lei_de_mencao.test_M5` (carimbo, fecha com o mapa commitado).
ANTES × base CAP-WIN (`a7537ec`): 0 novas; sumiu `test_linkedin_op_01…test_A2` (rede). Arquivos:
`provas/int_r7/BATERIA-*.json`. Nenhum teste enfraquecido; nenhum teste antigo ajustado.

## System Map

`correr_a_cadeia.py REGERAR` → `CADEIA=OK`; `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`**; `--conferir-carimbo` → **`IGUAL`**.
Peças novas `C-INT-MOTOR-CAPACIDADES`, `C-PROVA-INT-R7` (PENDING: não recarimbei — carimbo é leitura humana).
`INDICE-DE-FONTES` +1 endereço (o `https://` de uma asserção de teste).

## NÃO SEI / declarado

- D112, D95/D96 não estão no repo. O contrato do pote é o de `ce775ff5`; o pote unificado pode mudar.
- Se a Sala real preenche `VEIO_DE`/`FACT_LOCATION_VEIO_DE`: NAO SEI. Se não, todo lugar sai NAO SEI (certo, não defeito).
- Instituição = `SOURCE_ID` (não sei se duas SOURCE_ID são a mesma instituição).
- O `.sql` de export lê a vista da Sala fora de `admissao/sala_de_espera.py`: o dono não tem leitor que devolva
  FATO + janela + RAW juntos; é só leitura, numa cópia. Se o dono quiser o leitor dentro dele, é decisão dele.
- Design: não se aplica (nenhuma UI tocada).

## EM PALAVRAS SIMPLES

Agora as duas “cabeças” da Intelligence — a que diz **quando agir** no campo e a que diz **o que a ciência sustenta** —
trabalham na **mesma rodada**, olhando os mesmos papéis, sem contar nada duas vezes. Um estudo científico nunca
vira “praga no campo”. O sistema só aceita um lugar se a fonte **escreveu** esse lugar; diz de onde tirou cada
nome; separa “o que a fonte disse” de “o que eu concluí”; conta o mesmo boletim copiado para três províncias como
**uma** instituição; quando duas fontes dão limites diferentes, **não escolhe** — deixa a briga à vista; e quando a
recomendação muda de uma semana para outra, avisa que isso **não prova** que o campo mudou. No caso da mosca da
oliveira na Puglia, a resposta continua “ainda não há ação defensável: monitorar”. O resultado sai no formato
que o pote do portal lê, e o coordenador tem o passo a passo para rodar numa cópia da Sala sem risco de escrever nela.
