# REGRA DO LOTE-MICRO-V3 — escrita e commitada ANTES de olhar a coorte e as medições (D45)

Escrita a 25/09/2026, às 05:40 BRT, antes de abrir o conteúdo dos insumos. Até este commit, desses
ficheiros só se leram os nomes e o sha256. Quem aplicar a regra aplica-a **como está**: se ela der uma
escolha má, a escolha fica e escreve-se porquê. Não se reescreve a regra depois de ver.

## Insumos (fixados pelo sha256 do blob em `origin/integra-onda2-v1` @ d6faea85)

| Insumo | sha256 |
|---|---|
| coorte: `ferramentas/integra_onda2/ENSAIO-3-COORTE-CONGELADA-NA-COPIA.json` | `c168e19236136761369998d4c63272ea5eab8fa4b0d580c67c83a03225d7f4bb` |
| alvos novos D40: `scripts/capa_materia/MEDICAO-D40-V1.json` | `15ba6bc332d65833ee8217a0484eca06f61437c17cc10008df5c1cf70e215d0c` |
| a 1.ª onda (denominador e histórico): `ferramentas/big_collection/BC5-BIG-COLLECTION-1A-ONDA.json` | `972d6be105193e33b0d4cb7278cdd1ecd5bfe41a9d8d9d5d7f1753d9fdef5211` |

## O universo

As fontes da coorte congelada do ensaio integrado (a missão diz 28, com a ISTAT fora). Se o ficheiro
tiver a ISTAT (IT-T5-090), ela sai por decisão da missão, com o motivo escrito.

## A escolha: 6 fontes, por esta ordem

1. **Obrigatória:** IT-T10-018 (myfruit).
2. **≥ 2 agências de meteorologia/agrometeorologia julgadas pela régua T2:** fontes da coorte com
   UNIVERSO = T2 cujo dono é uma agência pública de ambiente ou meteorologia (ARPA/ARPAE/ARPAL/ARPAT
   ou equivalente). Escolhem-se as **2** melhores pelo critério C.
3. **≥ 1 julgada pela régua T1**, se a coorte tiver alguma fonte com UNIVERSO = T1. Se tiver, a melhor
   pelo critério C. Se não tiver, escreve-se `SEM_ELEGIVEL_T1` e a vaga passa ao passo 4.
4. **O resto, até 6:** pelo critério C, entre as que sobram.

**Restrição em todos os passos: no máximo 1 fonte por domínio registável** (D38). Duas fontes do mesmo
domínio dividem os 5 pedidos, e a segunda seria gasta à partida. Quando um passo esgota as candidatas
por causa desta restrição, escreve-se isso.

**Critério C** (ordenação, do melhor para o pior):
- (a) **mais alvos novos D40 medidos** para a fonte (`MEDICAO-D40-V1.json`: o número de alvos novos que
  a escolha «1.º alvo não coletado + até 3 novos» daria; se o ficheiro trouxer mais de um campo, vale
  o que conta alvos **novos** escolhidos). Fonte sem medição = 0, e fica `NAO_MEDIDA` escrito;
- (b) em empate, mais SIM históricos na 1.ª onda (BC5);
- (c) em empate, SOURCE_ID crescente.

## As previsões (escritas antes da corrida, por fonte)

- **Documentos novos previstos** = min(alvos novos D40 medidos, 3). O 3 vem do teto: robots (1) +
  índice (1) + até 3 matérias = 5 pedidos.
- **SIM previstos:**
  - fonte com histórico na 1.ª onda: documentos novos previstos × (SIM ÷ documentos julgados nessa fonte na BC5);
  - fonte sem histórico, ou com 0 documentos julgados na BC5: **`NAO_SEI`**. Nenhum número se inventa.
- **Não rodou ≠ 0 SIM.** Uma fonte que não correr (gate, egresso, TETO_DOMINIO, erro de transporte) fica
  `NAO_RODOU` com o motivo. Não conta como 0 SIM e não entra no denominador (ver abaixo).

## O critério D35 e o denominador

- Na 1.ª onda: **3 SIM em 18 fontes corridas = 16,7 %** (os 3 SIM são 3 documentos da mesma fonte, a
  myfruit). O denominador da D35 é, portanto, o **número de FONTES que correram**, e o numerador é o
  **número de DOCUMENTOS com SIM** na Admissão (linhas novas da `sala_de_espera`). Não são documentos
  admitidos, não são fontes com SIM.
  - Os outros denominadores possíveis dão números diferentes para a mesma onda: 3 SIM em 9 documentos
    julgados = 33 %; 1 fonte com SIM em 18 = 5,6 %.
- **Passa** se `documentos SIM ÷ fontes que correram > 16,7 %` **e** (regra do bot Luciano, para 6
  fontes) **≥ 2 documentos SIM**. Com 6 fontes corridas, 1 SIM = 16,7 %, que NÃO passa; 2 SIM = 33 %, que passa.
- Se correrem menos de 6, o resultado declara-se com o denominador real (por exemplo, 2 SIM em 5 = 40 %).
  Em qualquer caso é preciso ≥ 2 SIM.
