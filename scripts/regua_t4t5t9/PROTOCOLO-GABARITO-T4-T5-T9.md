# PROTOCOLO DO GABARITO T4 / T5 / T9 — escrito ANTES dos rótulos e de qualquer palavra da régua nova

REGUAS-T4-T5-T9 · 2026-09-25 · mesmo método da T1 e da T2 (`scripts/regua_t1`, `scripts/regua_t2`):
primeiro o gabarito, depois a régua, e a régua é medida no gabarito. Este ficheiro é commitado antes
do primeiro rótulo e antes de qualquer alteração a `admissao/admissao.py`.

## Porque existe

Medido na REROUTE-D2 (`ferramentas/reroute/MEDICAO-REROUTE-V1.json`): perguntar às outras gavetas dá
**8 % de precisão** contra os rótulos humanos. Os destinos que acendem são quase todos T5, T9 e T4,
réguas antigas de palavras soltas que casam com o **menu** dos sites. Exemplo: um imposto de carro
acende T5 com pontuação 5.

**Rótulos humanos de T4/T5/T9 que já existem na casa: 0.** Os gabaritos existentes são de T2/T12
(`curadoria/GABARITO-T2-T12-V*`, 208), T10/T7 (`scripts/micro_coleta/GABARITO-MICRO-V1.json`, 10),
T1 e T2.

## As três perguntas (Atlas, `docs/fontes/ATLAS-DE-FONTES-EAME.md:40-60`)

O universo é uma pergunta ao **conteúdo**, não à fonte.

- **T4 · REGULATORY.** Este conteúdo trata de **registo ou autorização de produtos fitossanitários**
  (ou fertilizantes/sementes reguladas)? Por exemplo: registos, culturas autorizadas, alvos, substâncias
  ativas, titulares, validade, novas autorizações, revogações, retiradas, restrições de uso,
  derrogações e usos de emergência, LMR/resíduos máximos, rótulos.
  - **NÃO:** «registo» no sentido de inscrição num site, num evento ou num registo civil; ministérios
    e decretos que não tratam de produtos; burocracia de outro assunto (impostos, concursos, tarifas).
- **T5 · SCIENCE.** Este conteúdo **relata ou descreve investigação**? Por exemplo: estudo, ensaio de
  campo, experimentação, resultados, artigo científico, projeto de investigação com o seu objeto,
  linha de investigação de um instituto, tese, tecnologia ou prática agronómica nova apresentada pela
  investigação.
  - **NÃO:** um menu com «Ricerca», «Pubblicazioni» ou «Rivista»; uma notícia institucional que só
    cita uma universidade de passagem; um evento sem conteúdo científico; uma revista comercial sem
    investigação.
- **T9 · COMPETITORS.** Este conteúdo é **sobre uma empresa concorrente** do mercado de proteção de
  culturas (BASF, Bayer, Syngenta, Corteva, FMC, UPL, Nufarm, Sumitomo, Certis, Gowan, Belchim, Sipcam,
  Isagro… e ainda a ADAMA, a do próprio lado, que conta como empresa do setor), a sua comunicação, os
  seus produtos, os seus lançamentos, a sua presença em feiras?
  - **NÃO:** «evento», «prodotto», «novità» ou «fiera» sem empresa do setor. A régua antiga mede esse
    conceito genérico, que **não é o do Atlas**.

Rótulos por pergunta: **YES / NO / NAO_SEI** (NAO_SEI = texto curto ou mistura sem assunto dominante;
não conta nem como positivo nem como negativo). O texto é lido pelo CONTEÚDO: um menu que diz
«Ricerca» não faz o texto ser T5.

`SINTONIA_RELEVANT` não é medido aqui. Para a REROUTE usam-se os rótulos que já existem
(`scripts/regua_t2/GABARITO-T2-V1.json`).

## De onde vêm os textos (só acervo, sem rede)

Textos únicos por sha256 do texto:
- `%USERPROFILE%\sintonia-gabarito\REGUA-T2-V1\textos` (554) e `REGUA-T1-V1` (19);
- a **cópia** do armazém da Sala (`C:/ajustes/armazem-textos`, 782, inclui os 49 das ondas de hoje);
- `data/derivados/texto/*.txt` do Git (43).

Nenhum pedido à rede.

## A amostra: estratificada, sorteada ANTES de ler, e a prova cega separada ANTES de rotular

Estratos, cada um com a sua semente fixa, escrita aqui:
1. **SONDA-T4:** textos com um termo-sonda de T4: `sostanza attiva`, `sostanze attive`,
   `prodotto fitosanitario`, `prodotti fitosanitari`, `revoca`, `autorizzazione`,
   `registrazione`, `etichetta`, `LMR`, `limite massimo di residuo`, `deroga`.
2. **SONDA-T5:** `sperimentazione`, `sperimentale`, `prova di campo`, `risultati`, `doi`,
   `ricerca`, `studio`, `progetto di ricerca`, `tesi`.
3. **SONDA-T9:** os nomes das empresas acima (palavra inteira).
4. **ACASO:** o resto, ao acaso.

As sondas **não são a régua**: servem para achar candidatos num acervo onde quase tudo é T2/T12. Os
rótulos são **lidos**, e muitos candidatos das sondas vão sair NO. Por isso esse é o sítio certo para
medir a precisão.

- **Semente: 45945** (random.Random). Até **40 textos por estrato**, e por estrato **30 % vão para a
  PROVA CEGA** antes de rotular (sorteio pela mesma semente).
- A régua nova **só olha para o GABARITO** (os 70 %). A prova cega só se abre no fim.
- **Cada texto é rotulado nas três perguntas** (T4, T5, T9), sem olhar a régua (nem a antiga nem a nova).

## ADENDA 1 · 25/09 · escrita DEPOIS dos 86 rótulos e ANTES de ler os textos novos

**O que os 86 rótulos mediram:** T4 **0 YES**, T5 **4 YES**, T9 **1 YES**. Os três ficam `NAO PRONTO`.
A causa está no acervo: ~ 1.177 textos quase todos de agências de ambiente e clima, institucionais, e
títulos do YouTube. Só 3 textos em todo o acervo citam uma empresa do setor.

**Estrato novo, FONTE-DECLARADA:** os brutos do armazém da Sala das fontes declaradas T4, T5 e T9
(`armazem/XX/it-t4-*`, `it-t5-*`, `it-t9-*`, respetivamente 1, 46 e 8 documentos).
- São **copiados** (nada se lê no vivo) e o texto é extraído com os extratores da casa
  (`coleta/executor_texto_de_html.extrair`, `executor_texto_de_pdf.extrair`).
- Entram **todos**. Sorteio da prova cega pela mesma semente (45945), com 30 %.
- Os JSON e CSV entram como texto cru, com a sua forma dita.
- Rotulam-se nas três perguntas, como os outros.

Se, com este estrato, um universo continuar abaixo de 20 YES no gabarito, fica `NAO PRONTO` de vez
com estes números. O resto do acervo **não tem** esse conteúdo, e a rede está fechada.

## Regras

1. Rotulador: Claude (Opus 5.5). O trecho que decidiu fica citado. `VALIDADO_POR_HUMANO = NAO`.
2. **Nenhuma palavra da régua nova é escrita** para um universo cujo gabarito não tenha **≥ 20 YES e
   ≥ 20 NO**. Se não chegar: `NAO PRONTO` com o número, e **não se escreve régua**. Para esse universo
   propõe-se só **desligá-lo como destino do REROUTE**, o que não é uma régua nova.
3. **O menu não conta:** a régua nova só lê o **corpo** do texto. Tira-se o que é navegação,
   cabeçalho e rodapé (linhas curtas sem frase, sequências de títulos, `cookie`, `privacy`,
   `copyright`…). A regra do corpo é escrita e medida no gabarito, como as outras.
4. **Transversais:** os termos de T4, T5 e T9 **deixam de servir de prova** para dizer NÃO a outro
   universo (como T2 e T1). ⚠️ Isto **muda vereditos de outros universos** (NÃO → NÃO SEI). Não se
   esconde: cada mudança é contada e explicada. É uma regra que o dono pediu, e fica medida.
5. Precisão e recall no gabarito são medidos **dentro da amostra**, e ditos assim. Na prova cega, são
   de textos não usados.
6. **0 mudanças fora do que a regra 4 explica:** os 10.864 julgamentos da REROUTE, antes e depois.
7. Mutação: desligar cada peça da régua nova tem de reprovar os testes.
