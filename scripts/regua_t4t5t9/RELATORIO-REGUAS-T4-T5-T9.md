# REGUAS-T4-T5-T9 — relatório

Ramo `reguas-t4t5t9-v1`, a partir de `reroute-d2-v1` (`d23b31b4`).
- **Rede fechada:** proxy `127.0.0.1:9`, nenhum pedido.
- **Vivo e Sala não tocados:** o armazém foi lido por **cópia**.
- **Método:** o da T1/T2. O protocolo foi escrito antes do primeiro rótulo; a adenda, antes de ler os textos novos.

## Veredito: `NAO PRONTO` nos três. Nenhuma régua nova foi escrita.

| Universo | YES | NO | NÃO SEI | Regra (≥ 20 YES e ≥ 20 NO) |
|---|---|---|---|---|
| **T4** registo/autorização de fitossanitários | **0** | 164 | 3 | NAO PRONTO |
| **T5** investigação | **6** | 135 | 26 | NAO PRONTO |
| **T9** empresa do setor | **10** | 152 | 5 | NAO PRONTO |

`CONTAGEM-GABARITO.json` · `rotulos/rotulos-gabarito.json` (167 rótulos, cada um com o trecho que decidiu).
Rotulador: Claude. **`VALIDADO_POR_HUMANO = NAO`**.

### 1. Gabarito

- **Rótulos humanos de T4/T5/T9 que já existiam na casa: 0.** Os gabaritos existentes são de T1, T2, T12, T10 e T7.
- **Amostra base** (`amostrar.py`): 1.177 textos únicos do acervo, em 4 estratos por sonda (SONDA-T4, SONDA-T5, SONDA-T9, ACASO); 123 sorteados.
  - 86 foram para o gabarito e 37 para a prova cega.
  - Resultado: T4 0 YES, T5 4, T9 1.
  - Só **3 textos** em todo o acervo citam uma empresa do setor.
- **Adenda 1** (`amostrar_adenda1.py`): os brutos do armazém das fontes declaradas T4/T5/T9, copiados. Texto tirado pelos extratores da casa. 115 textos:
  - 81 foram para o gabarito e 34 para a prova cega;
  - 107 JSON de observação sem conteúdo ficaram fora (contados).
  - Somou-se: T5 +2, T9 +9. Os T9 são quase todos Koppert, mais Certis Belchim e CBC/Biogard.
- **Porque não chega:** o acervo é de agências de ambiente e clima. O que há de T9 são títulos do YouTube e páginas institucionais de empresas; T4 não tem nenhum registo de produto. **Sem coleta dirigida (com rede), estes universos não se medem.**

### 2. Conserto

**Não feito, por regra** (protocolo, regra 2): não se escreve régua com menos de 20 YES.
- A regra do corpo, «o menu não conta», fica **por escrever**.
- A regra transversal também: T4/T5/T9 deixam de servir para dizer NÃO a outro universo.
- **Ambas precisam do gabarito** para ser medidas.

### 3. Prova cega

**71 textos** (37 + 34), separados **antes** de rotular. **Não foram abertos** e ficam selados para quando houver régua.
- Os 10.864 julgamentos não mudaram: nenhuma linha de `admissao/admissao.py` foi alterada neste ramo.
- **Mutação:** não se aplica, porque não há régua nova para atacar.

### 4. A régua ANTIGA no gabarito (`medir.py` → `MEDICAO-REGUAS-T4T5T9-V1.json`, dentro da amostra)

| Universo | Acerta (TP) | Falso SIM (FP) | Perde (FN) | Precisão |
|---|---|---|---|---|
| T4 | 0 | **20** | 0 | **0 %** |
| T5 | 5 | **45** | 1 | **10 %** |
| T9 | 1 | **21** | 9 | **4,5 %** |

- O alvo é **98 % (T1) e 95 % (T2)**.
- A régua antiga de T9 mede outra coisa: «evento, prodotto, fiera» em vez de empresa do setor. **Perde 9 das 10 empresas.**

### 5. REROUTE outra vez, com cada conjunto de destinos

A base são os rótulos humanos `SINTONIA_RELEVANT`, recalculados de `ferramentas/reroute/MEDICAO-REROUTE-V1.json`. O recálculo é válido porque nenhuma régua mudou.

| Destinos permitidos | Úteis acesos | Inúteis acesos | Precisão | Recall (de 13 úteis) |
|---|---|---|---|---|
| todos (hoje) | 8 | 94 | 8 % | 62 % |
| **sem T4/T5/T9** | 0 | 4 | **0 %** | 0 % |
| sem T4 | 7 | 90 | 7 % | 54 % |
| sem T5 | 5 | 39 | 11 % | 38 % |
| sem T9 | 5 | 93 | 5 % | 38 % |
| só T1/T2 (réguas medidas) | 0 | 0 | — | 0 % |

**Nenhuma variante chega ao alvo.**
- Tirar T4/T5/T9 limpa quase tudo: de 124 acesos no corpus sobram 14.
- Mas o pouco que sobra (T3/T7/T10) também erra: 4 inúteis e 0 úteis. **Essas réguas também nunca foram medidas contra gabarito.**

## Proposta, para decisão, sem código neste ramo

1. **Pouso do REROUTE só para gavetas com régua medida em gabarito.** Hoje são T1 e T2.
   - Hoje o REROUTE só escreve na evidência e não pousa, por isso nada muda agora.
   - A regra vale para quando se ligar o pouso (migração 033).
   - Com ela, os erros vão a 0 e os acertos também, até haver mais réguas medidas.
2. **Missão de coleta dirigida** (com rede, portão IT, teto D38) para ter ≥ 20 YES de cada universo:
   - **T4:** banca dati del Ministero della Salute (fitosanitari), revogações e derrogações.
   - **T5:** CREA, CNR-IPSP, Georgofili com artigo inteiro e não o índice, revistas com resumo.
   - **T9:** notícias e produtos das empresas (Syngenta, BASF, Bayer, Corteva, Certis Belchim, Sipcam…).
   - Depois rotula-se com o mesmo protocolo, que já está escrito.
3. As mesmas perguntas valem para **T3, T7 e T10**, que também acendem no REROUTE sem gabarito.

## Evidência fora do Git (sha256)

- Textos do gabarito e da prova cega (238): `%USERPROFILE%\sintonia-gabarito\REGUA-T4T5T9-V1\textos`.
  - Hash da lista `sha256(ficheiro)+nome`: `e5b2035ab6358c8b0367f8091d2fec1184311ffcfa47bce5db1fcca8d2c328ad`.
- Cópia dos brutos T4/T5/T9 do armazém (253 ficheiros): `C:\ajustes\brutos-t4t5t9`.
  - Mesmo hash: `16bd447f9394f326c5bcdc844cf4625e84c4c0a0a09c02b7177666552570c920`.
- O sha256 de cada texto rotulado está em `A-ROTULAR.json` / `A-ROTULAR-ADENDA1.json` (`SHA256_NORMALIZADO`).

## Instalar

**Nada a instalar.** Este ramo não muda código que corre em produção. Só traz protocolo, rótulos, medição e o mapa.
