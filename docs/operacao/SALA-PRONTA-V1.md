# SALA-PRONTA-V1 — o que a Intelligence vai ler quando a trava abrir

> **Só leitura, só metadados.** A Sala real foi lida com a sessão forçada a só-leitura
> (`default_transaction_read_only = on`, conferido na própria saída). A coluna `texto` **não foi
> lida**. Nada de crossing, finding, oportunidade nem pontuação. Trava D33 intacta. Não instalado.

| campo | valor |
|---|---|
| missão | SALA-PRONTA-PARA-INT (coordenação, 25/09) |
| ramo | `sala-pronta-v1` a partir de `c821094d` |
| Sala lida | `127.0.0.1:54330/sala_italia`, tabela `public.sala_de_espera`; `psql` da casa (`~/orca/pgtmp/pgsql/bin`), senha pelo `pgpass.conf` ao lado do cluster (fora do Git; nunca em argumento) |
| consulta | `data/derivados/SALA-PRONTA-V1/inventario.sql` |
| saída | `data/derivados/SALA-PRONTA-V1/inventario-RESULTADO.txt` (sha256 `b86ea043b463b34a…`) |
| medido em | 25/09/2026, depois da 1.ª onda (BC5) e antes da MICRO / 2.ª onda |

## 1 · Inventário da Sala real

**69 itens.** Todos `ESTAGIO = DOCUMENTO`, todos `ESTADO_DA_FILA = WAITING`, **0 consumidos**
(`consumido_em` vazio em 69/69 — a Intelligence nunca leu a Sala).

### Por universo e régua

| universo | itens | fontes |
|---|---|---|
| T5 (estatística / academia) | 39 | 26 |
| T10 (mercado) | 19 | 1 (`IT-T10-018`, myfruit) |
| T3 (boletim fitossanitário) | 5 | 3 (`IT-T3-002`, `IT-T3-008`, `IT-T3-010`) |
| T7 (associações / consórcios) | 4 | 3 |
| T9 | 2 | 1 |
| **T1 · T2** | **0** | **0** |

Uma fonte pesa 28 % da Sala: `IT-T10-018` tem 19 de 69. `ADMITIDO_POR`: «pertence ao universo v5»
61, «v7» 8.

### Quando entrou na Sala (`pousado_em`) — é a data da **Sala**, não do fato

| dia | 18/09 | 19/09 | 20/09 | 21/09 | 22/09 | 24/09 |
|---|---|---|---|---|---|---|
| itens | 3 | 1 | 42 | 10 | 5 | 8 |

### Os quatro tempos — nunca confundidos

| campo | o que é | conhecido | NAO SEI |
|---|---|---|---|
| `fact_time` | quando o facto aconteceu | **0** | **69** |
| `published_at` | quando a fonte publicou | **0** | **69** |
| `observed_at` | quando a fonte observou | **0** | **69** |
| `captured_at` | quando **nós** colhemos | 69 | 0 |

`fact_time_basis = NAO SEI` em 69/69. `published_at = captured_at` em **0** — ninguém carimbou a
nossa visita como data de publicação (a armadilha medida a 21/09 não entrou na Sala).

### Lugar — nunca herdado da fonte

| campo | conhecido | NAO SEI |
|---|---|---|
| `fact_location` (onde é o facto) | **0** | **69** |
| `source_location` (onde está a fonte) | 0 | 69 |

`fact_location_basis = NAO SEI` em 69/69. (`fact_location = source_location` em 69 porque **os dois**
dizem `NAO SEI` — não é herança.)

### Outros metadados

`FATO` é o texto `"NAO_SE_APLICA"` em 69/69 (é documento, não facto estruturado).
`source_declared_evidence_class = NAO SEI` em 69/69.

## 2 · As 4 chaves da janela (D29): em quantos itens existem, e de que campo viriam

| chave | itens com valor | campo que a traria | onde está no código |
|---|---|---|---|
| **cultura** (`CROP_ID`) | **0 / 69** | **nenhum**. A Sala não tem coluna de cultura; só poderia vir **dentro** do envelope `FATO`, e o envelope só existe quando o estágio é `FATO` — os 69 são `DOCUMENTO` | colunas: `supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql`; contrato READY: `provas/espinha_da_intelligence.py:74-80` (19 campos, sem cultura); envelope: `admissao/admissao.py:1404` (`envelope_do_fato`), que declara «não lê o texto, não infere, não cunha `crop_eppo`» (`:1426-1440`) |
| **região** (`REGION_ID` / `FACT_LOCATION`) | **0 / 69** | `fact_location` — existe e está `NAO SEI` | coluna: `031_…sql:154`; escrito em `admissao/admissao.py:1537` (`item.get("fact_location", AUSENCIA)`); lido em `admissao/sala_de_espera.py:609` |
| **fase da planta** (`PHENOLOGY_STAGE`) | **0 / 69** | **nenhum** — nem coluna, nem campo do contrato READY | `espinha_da_intelligence.py:74-80` |
| **janela** (intervalo + safra) | **0 / 69** | **nenhum**. O mais próximo é `fact_time`, que é **um ponto**, não um intervalo — e está `NAO SEI` em 69 | `031_…sql:155`; ver a lei em `admissao/admissao.py:314` (`FACT_TIME != PUBLISHED_AT != OBSERVED_AT != COLLECTED_AT`) |

**Região não foi inferida da fonte** — nem podia: `source_location` também é `NAO SEI` em 69.

**Leitura em uma linha:** hoje **nenhum** item da Sala tem **nenhuma** das 4 chaves. Para a
`CAP-WIN` (anexo A do plano da §32), a Sala está em zero. Isso é um gap da **Collection**
(`GAP-WIN-02/04/05` do anexo), não da Intelligence.

## 3 · Plano (só papel): o que muda depois da MICRO e da 2.ª onda

**Esperado pela coordenação:** +N itens com T1/T2.

⚠️ **Risco a medir, não a supor:** o universo **T2 não tem regra de admissão** (registado na
primeira coleta controlada, 16/09: `ADMISSION = NAO_SE_APLICA` ×4 para IT-T2-002, e na BC5: as duas
T2 correram com 0 SIM). Se isso não mudou, as fontes T2 podem **correr com sucesso e não pousar
nada na Sala**. T1 também está em 0 hoje. Então «+N T1/T2 na Sala» pode ser 0 — e isso seria a
regra de admissão, não a coleta.

**Medição logo a seguir** (quando o coordenador disser «volumes reconciliados»), tudo só-leitura:

1. **correr de novo `inventario.sql`** e comparar com este ficheiro, linha a linha: total; por
   universo e fonte; os quatro tempos; `fact_location`; `FATO`;
2. **as 4 chaves**: contar outra vez. Se algum item novo trouxer região/tempo/fase, **mostrar de
   que campo veio** e a base (`*_BASIS`) — sem inferir nada;
3. **o delta por `(RUN_ID, ORDEM)`**: listar só os itens novos (metadados), sem ler texto;
4. **a trava**: `censo_das_estradas_it.py` (ramo `trava-medidores-v1`) sobre o registo da onda em
   `ferramentas/big_collection/` — quantas fontes saem de `NAO_SEI` no critério A;
5. **se T1/T2 correram e a Sala não cresceu nessas famílias**: reportar como gap de Admission
   (regra por universo), com o `RUN_ID` de cada corrida.

Nada disto lê texto para pontuar nem cruza fontes.
