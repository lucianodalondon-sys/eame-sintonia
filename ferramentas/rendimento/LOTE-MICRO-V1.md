# LOTE-MICRO-V1 — o lote fixo da micro de prova da próxima onda

Escrito **antes da rede** a 24/09/2026 (bot vivo 55b50a63, régua T2 instalada; R1 **não** instalada).
Ficheiro: `LOTE-MICRO-V1.json` · sha256 `e9d86a44f1fb350b24b70b4d319dd8ba2e7fbe0a694497248e7a756ef5b2b339`. **Não foi corrido**: corre o coordenador, depois de instalar a R1.

## Em palavras simples

Escolhemos **3 fontes**, antes de ir buscar nada, e escrevemos já:
- que endereços a coleta vai pedir;
- quantos SIM esperamos.

Depois compara-se o que se previu com o que aconteceu. Assim ninguém escolhe as fontes depois de ver o resultado.

| # | Fonte | Porque entra | Precisa de | Documentos | SIM esperado |
|---|---|---|---|---|---|
| 1 | **IT-T10-018 myfruit** | tem **11 notícias novas** na janela do contrato (a corrida traz 3, por cortesia). É a fonte que mais rende: 19 SIM em 46 textos (41%). | nada: já está pronta | 3 | ~1 (0 a 3) |
| 2 | **IT-T2-002 ARPAV Agrometeo…informa** | é **a T2 de janela**, o boletim agrometeorológico por zona (fenologia, defesa integrada, evapotranspiração). A régua T2 de hoje dá **SIM a 4 de 4** textos já colhidos. | ⚠️ **ser revalidada no Curator** (hoje está READY_LEGACY e o portão recusa-a). **Não é a R1.** | 4 | ~3 (0 a 4) |
| 3 | **IT-T7-041 Bonifica Romagna** | a única da R1 com várias notícias novas na janela (7) | R1 instalada | 3 | ~0,4 (0 a 1) |

- **Previsão:** 10 documentos e ~4 SIM, ou seja **~44%**. Se a ARPAV não for revalidada: 6 documentos e ~1,6 SIM, **~27%**. Nos dois casos passa os **16,7%** da 1.ª onda, **se a estimativa estiver certa**.
- ⚠️ **A estimativa é frágil.** Vem de 46 textos na myfruit, 4 na ARPAV e 1 na Bonifica. **0 SIM continua possível.**
- ⚠️ **ARPAV: não sei se há boletim novo.** A data da edição não aparece na página de entrada (é carregada por JavaScript). Nas 3 visitas anteriores (07, 14 e 18/09) havia sempre versão nova. Por isso estimei 70% de hipótese, mas **não está provado**.
- **Regra decidida já:** uma fonte cuja condição falhar **não conta como 0 SIM**, conta como «não correu». Fica escrito antes, para ninguém a escolher depois.

## O que o coordenador pediu e não consegui cumprir à letra

**«Pelo menos 1 T2 de janela, das que já estão prontas ou ficam prontas só com a R1»: não existe.**
- As T2 que estão prontas são notícias das ARPA:
  - ARPAE: «30 anni per l'ambiente»;
  - ARPA Marche: um evento num parque, já guardado;
  - as 6 T2 da R1: pólen, campos eletromagnéticos, águas subterrâneas, acreditação de laboratórios.
  Nenhuma tem ligação agrícola. Com a régua T2, que pede **tempo E cultura juntos**, sairiam NAO_SEI. A régua de hoje, sobre os textos já colhidos delas, dá **NAO**.
- Os boletins de janela verdadeiros são dois:
  - **ARPAV (IT-T2-002)**, que o coletor sabe colher;
  - **ARPAE agrometeo (IT-T2-001)**, para a qual o coletor **não tem rota**.
  Os dois estão em **READY_LEGACY**: aprovados pela régua antiga e nunca revistos.
- Por isso a T2 do lote tem uma **condição fora da R1**: revalidar a IT-T2-002. A decisão é do coordenador.

## Ficam de fora, e porquê (decidido antes da rede)

| Fonte | Porque fica de fora |
|---|---|
| IT-T7-141 CIA Toscana | o endereço que a corrida pediria é uma **listagem** («comunicati-stampa-2026/»), não uma notícia |
| IT-T2-051 ARPAE notícias | «30 anni per l'ambiente», sem ligação agrícola: histórico 1 NÃO em 1 |
| IT-T2-034 ARPA Marche | o primeiro link já está guardado: 0 novas na janela |
| IT-T7-031 FederBio (R1) | 1 notícia (projeto europeu); histórico 1 NÃO em 1. Baixaria a taxa |
| T2 da R1 (032, 033, 037, 050, 063, 070) | sem contrato no coletor, e sem ligação agrícola |

## Provas no ramo (`ferramentas/rendimento/`)

- `LOTE-MICRO-V1.json` (+ `.sha256`): o lote, os endereços previstos, a previsão e o **antes da rede**:
  - bot 55b50a63;
  - estado do portão das 3 fontes;
  - a Sala 69 / 1425 / 927 / 402;
  - o sha256 do livro do coletor;
  - o egresso PASS.
- `medidas/entrada-lote.json`: as capas medidas hoje, com o portão de egresso PASS antes e depois (26 pedidos).
- `medidas/lote-regua-offline.json`: a régua instalada sobre os textos já colhidos, sem rede.
- `lote_micro.mjs` e `regua_offline.py`: para refazer.
