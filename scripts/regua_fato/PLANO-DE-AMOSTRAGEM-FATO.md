# PLANO DE AMOSTRAGEM · exemplos reais para o `agro_fact_kind` (DA-14, sob D67)

Só leitura. Nada foi coletado, nenhuma régua foi mudada. A régua fica **NAO PRONTA** e **não ligada**; na
Sala, `agro_fact_kind = NAO SEI` até haver exemplos.

## 1 · Quantos faltam

**Meta por tipo:**
- **20 no gabarito**;
- mais **10 numa prova cega NOVA**: a antiga (49 textos) está gasta e passa a contar como gabarito;
- total: **30 textos rotulados por tipo**.

**O que há hoje:** 163 textos rotulados (114 gabarito + 49 cega), taxonomia v2.

| Tipo | Há hoje | Faltam para 20 | + cega nova | **A rotular** | De onde vieram os que há |
|---|---|---|---|---|---|
| REGULATORIO_MOLECULA | **0** | 20 | 10 | **30** | nenhum texto em prosa (só as linhas do registo IT-T4-001) |
| CAMPO_PRODUCAO_COLHEITA | 2 | 18 | 10 | **28** | Plantgest (acervo) |
| NEGOCIO_AGRO | 2 | 18 | 10 | **28** | Senado/bonifica, Ismea (acervo) |
| CAMPO_CLIMA | 4 | 16 | 10 | **26** | ARIF, ARPA Marche, agrometeo (acervo) |
| MERCADO_VAREJO | 5 | 15 | 10 | **25** | **só myfruit** (IT-T10-018) |
| CAMPO_FITOSSANITARIO | 8 | 12 | 10 | **22** | boletins T3 (IT-T3-002/008/010), ARIF, Koppert |
| MERCADO_PRECO | 10 | 10 | 10 | **20** | myfruit 8 de 10 |
| MARKETING_CONCORRENCIA | 12 | 8 | 10 | **18** | Riunite, Chianti Classico, myfruit («Dalle Aziende») |
| EVENTO_TECNICO | 14 | 6 | 10 | **16** | myfruit, Macfrut, Vite in Campo, Georgofili |
| INSTITUCIONAL | 20 | 0 | 10 | **10** | universidades agrárias, CIA, CONAF |
| NAO_FATO | 52 | 0 | 10 | **10** | ARPA, ENEA, universidades |

**Total a rotular: ~233 textos**, e só se cada tipo aparecer. O que é caro são os 6 primeiros tipos.

## 2 · De que fontes da coorte de 60 tendem a vir

Coorte de 60 = a coorte PROVISÓRIA da 3.ª onda, com 40 fontes
(`onda3-pacote-v1:ferramentas/onda3_pacote/ensaio/6-COORTE-ONDA3-PROVISORIA.json`), mais as 20 que só
esperam a RECEITA-T8 (12 T8, 7 T12 e 1 T9, `SEM_RECEITA_WEB`). ⚠️ **Esta composição é leitura minha**:
não achei o ficheiro «coorte de 60».

Legenda: **M** = medido nos rótulos · **P** = presumido pelo nome ou pelo endereço, ainda não medido.

| Tipo | Fontes da coorte que tendem a dar | Nota |
|---|---|---|
| REGULATORIO_MOLECULA | IT-T7-043 Agrofarma-Federchimica (P) · IT-T3-023 terraevita «agrofarmaci-difesa» (P) · IT-T5-111/113 CREA difesa e certificazione (P) | ⚠️ **a coorte provavelmente não chega a 30.** Fora dela: o registo do Ministero (IT-T4-001, CSV), com uma linha = um facto (registo ou revogação); e as fontes T4 que ainda não têm rota |
| CAMPO_PRODUCAO_COLHEITA | IT-T10-021 Plantgest (M no acervo) · IT-T8-028 Rivista di Frutticoltura, IT-T8-039 Rivista di Orticoltura (P) · IT-T7-163 Casalasco (campanha do tomate, P) · IT-T7-139 Florovivaisti (P) | |
| NEGOCIO_AGRO | IT-T8-051 guia da PAC (P) · IT-T12-137 PSRN (P) · IT-T12-024 Regione Veneto Agricoltura (P) · IT-T7-103 Confcooperative (P) · IT-T7-049 Copagri (P) | |
| CAMPO_CLIMA | ARPA T2: IT-T2-032/034/037/050/051/145/146 (M: ARPA Marche 1 CLIMA, mas **a maior parte da ARPA é NAO_FATO**) · IT-T7-021 Villoresi (rega, P) | Onde há mais: os **boletins agrometeo** (rotas da JANELA-FORMAS / boletins-data-local), fora destas 60 |
| MERCADO_VAREJO | IT-T10-018 myfruit (**M: 5 de 5**) | ⚠️ **uma fonte só.** Limitar a 5 por fonte deixa o tipo em 5. Falta uma segunda fonte de varejo (ex.: um observatório de preços ao consumo) |
| CAMPO_FITOSSANITARIO | IT-T3-023 terraevita difesa (P) · IT-T5-111/113 CREA (P) · IT-T8-021 terraevita attualità (P) · IT-T8-028/039 revistas (P) · IT-T10-021 Plantgest (P) | Os que **deram** (M) são os boletins T3, IT-T3-002/008/010, que **não estão** nas 60 |
| MERCADO_PRECO | IT-T10-018 myfruit (**M: 8**) · IT-T7-163 Casalasco (P) · as revistas T8 (P) | ⚠️ Não achei o nome de 5 das 20 T8/T12 no Git: IT-T8-022, -024, -041, -042 e -062. Os endereços das T8 da Edagricole vêm de `curadoria/ROTAS-ELEGIVEIS-V1.json` |
| MARKETING_CONCORRENCIA | IT-T7-017 Riunite (M: 3 no acervo) · IT-T7-033 Chianti Classico (M: 3) · IT-T10-018 myfruit (M: 3) · IT-T7-042 Balsamico (P) · IT-T7-163 Casalasco (P) | A concorrência de proteção de culturas (Syngenta, BASF…) **não está** nas 60 |
| EVENTO_TECNICO | IT-T7-043 Agrofarma «news-ed-eventi» (P) · IT-T8-034 Macchine Agricole News (feiras, P) · IT-T7-019 Confagricoltura Lombardia e as CIA (P) · IT-T5-186 ENEA eventi (P: a ENEA deu NAO_FATO 3 de 3) | |
| INSTITUCIONAL / NAO_FATO | CIA (IT-T7-112…141), ENEA (IT-T5-185/186/187), ARPA | Aparecem sozinhos. Não é preciso procurar |

## 3 · Como amostrar (quando a coleta correr, depois de data/local)

1. **A prova cega nova primeiro.** Por fonte, 1/3 dos textos novos é sorteado para a cega **antes de
   ler**, com semente escrita.
2. **Rotular por estrato de fonte**, pela tabela 2, até cada tipo ter 30.
   - **No máximo 5 por fonte e por tipo**, para um tipo não ser uma fonte só.
   - A exceção declarada é o varejo, que hoje só tem o myfruit.
3. Mesmo protocolo: `PROTOCOLO-GABARITO-FATO.md` + adenda 1. Rótulos com `VALIDADO_POR_HUMANO = NAO`
   enquanto uma pessoa não os ler.
4. **Não mexer na régua** até todos os tipos terem 20 no gabarito. É a decisão DA-14: com poucos
   exemplos, afinar no treino piorou a cega (73 → 77 % no treino, 58 → 46 % na cega).
5. **Medir primeiro o rendimento por fonte.** Na 1.ª onda nova, contar quantos textos de cada tipo deu
   cada fonte. Só depois decidir quantas ondas faltam.

## 4 · Quantas ondas: **NAO SEI** (estimativa)

- O teto é de **5 pedidos por domínio por onda** (D38), e as 60 fontes deram 78 linhas à Sala em duas
  ondas e uma micro.
- Para o REGULATORIO, com 2 a 4 fontes prováveis, isso dá no máximo ~15 a 20 textos por onda. Se metade
  for regulatório, **2 a 4 ondas**.
- É estimativa, não medida: o rendimento real mede-se na primeira onda (passo 5).
