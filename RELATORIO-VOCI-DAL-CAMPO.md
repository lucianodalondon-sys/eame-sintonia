# VOCI-DAL-CAMPO — o extrator de voz (ferramenta n.º 3 do casco)

Ramo `nuvem-voci-campo-v1`, base = produção `69b0e23f`. Sem rede externa, sem Sala, sem login, sem perfil.
Dados: só fixtures do repositório (47 transcritos) e casos sintéticos marcados `SOURCE_ID = 'SINTETICO'`.

## O que fiz

**Um extrator novo, `motor/voce_dal_campo.py` (944 linhas).** Ele lê um texto que já foi transcrito e devolve o
**item Voce**. Não transcreve (isso é de `ferramentas/fala_local.py`) e não coleta.

| campo do item | de onde vem | ficheiro:linha |
|---|---|---|
| `SPEAKER_ID` | `SPK-` + sha do nome **dito no transcrito**. Mesmo nome dá o mesmo id; homónimos não se resolvem (INT-LAW-083) | `motor/voce_dal_campo.py:361` (`apresentacoes`), `:407` (`falantes`) |
| papel + prova | declaração no transcrito, da própria pessoa (`AUTO_DECLARADO`) ou de quem a apresenta (`DECLARADO_POR_TERCEIRO`), com o trecho | léxico `:202`, apresentações `:261` |
| agrónomo ≠ influenciador | «inscreve-te no canal» é sinal de criador, não papel; sem papel profissional → `INFLUENCIADOR`; com os dois, fica o profissional e o sinal à vista | `:217`, `:407` |
| agricultor = T8 | só `AGRICULTOR` põe `UNIVERSO_DO_PAPEL = T8` | `:407` |
| organização | nome depois de «at/with/presso/de…» e o tipo (EMPRESA, UNIVERSIDADE_PESQUISA, INSTITUICAO_PUBLICA, ASSOCIACAO, MEDIA) | `_organizacao`, `TIPO_DE_ORG` |
| pessoa ≠ instituição | o canal é `PUBLISHER`, nunca o falante. Sem pessoa apresentada e com canal de organização, a voz é `INSTITUICAO`; sem nada disso, `NAO SEI` | `:671` (`tipo_do_publisher`), `:685` |
| citação | `QUOTE_ORIGINAL = texto[ini:fim]` **exacto**, com `QUOTE_POS_START/END` e, se houver segmentos, o segundo do áudio | `:685` |
| citação ≠ interpretação | a leitura nossa vai em `INTERPRETACAO`, assinada «SINTONIA · regra lexical» | `:685` |
| cultura e problema | **dono: `motor/matriz_recorte.py`** (`CROPS`, `ISSUES`, `_padrao`). Nenhum vocabulário novo | `:469` |
| `FACT_TIME` | só data escrita na frase da citação. «today / quest'anno / hoy» → `NAO SEI` com a expressão guardada. Data igual à publicação é descartada. Italiano: **dono `leis/fato_local.tempo_do_fato`** | `:506` |
| `FACT_LOCATION` | só com relato em primeira pessoa, na frase ou na **cena** até 3 frases antes (nunca atravessa a apresentação nem «>>»). Italiano: **dono `leis/fato_local.localizacoes_do_fato`** | `:557`, `FRASES_DA_CENA :99` |
| lugar da pessoa ≠ lugar do facto | o lugar dito na apresentação vai para `SPEAKER_PLACE` (espécie BASE), nunca para `FACT_LOCATION` | `falantes :407` |
| original ≠ tradução | **dono `regras/proveniencia.py`**: `TEXT_KIND` e `QUOTE_IS_SPEAKERS_WORDS` vêm dele. Título numa língua e texto noutra é só **suspeita** (`QUOTE_TRANSLATION_SUSPECT`), nunca carimbo — lei da C6 | `import :85`, `documento :601` |
| contrato | `validar_voce` reprova 20 espécies de violação (citação reescrita, publicação como tempo do facto, T8 sem agricultor, lugar da pessoa no lugar do facto, instituição com speaker, atribuição «provada» sem diarização, voz sem a ressalva «NAO E INCIDENCIA», …) | `CAMPOS_OBRIGATORIOS :802`, `validar_voce :812` |

**Testes, `tests/test_voce_dal_campo.py` (47 testes):**
- 29 sobre transcritos **reais** do repositório;
- 18 **sintéticos**, marcados como tal.

**Prova de mutação, `provas/voci_dal_campo/mutar.py`.** Planta um defeito de cada vez e repõe o ficheiro a partir
dos bytes guardados (nunca com `git checkout`).

**Mapa.** Criei duas peças novas em `system-map/data/architecture.declared.json`:
- `C-VOCI-DAL-CAMPO` (motor);
- `C-PROVA-VOCI-DAL-CAMPO` (prova).

### Correções pelo caminho (medidas, não suposições)
1. **1.ª corrida: 215 «falantes», quase todos falsos.** A regra «Nome, …» apanhava «However,», «Bueno,»,
   «Entonces,». Agora só vale se vier uma profissão logo a seguir. Resultado: 28 falantes. Há um teste e o mutante M18 a guardar isto.
2. **A legenda espanhola não tem pontuação.** Uma palestra de 70 mil letras era **uma** frase, e o lugar saía
   de qualquer ponto dela («Dios», «Bueno», nomes de gente). Agora, acima de 500 letras, a frase é cortada em **pedaços de 30
   palavras**, marcados `PEDACO_DE_LEGENDA_SEM_PONTUACAO`. Nesses pedaços só contam nomes de país e o gazetteer
   italiano.
3. **Frase curta de apresentação** («I'm Amber Bell.») emendava a seguinte e colava o papel de OUTRA pessoa na
   apresentadora. A emenda saiu (M16).
4. **Eu carimbava tradução por palpite** (`PROVAVEL_TRADUCAO`). A lei C6 (`tests/test_c6_especie_do_texto.py`) diz
   «quem infere pode suspeitar, não pode carimbar», e a espécie do texto tem dono. Passou a suspeita, em campo próprio.
   Ajuste **declarado** nos meus próprios testes, citando essa lei.

## Medida sobre os 47 transcritos (`provas/voci_dal_campo/MEDIDA-CORPUS.json`)

| | quantos |
|---|---|
| vozes (frases com cultura ou problema) | **922** em 47 documentos |
| violações do contrato | **0** em 922 |
| falante pessoa identificada | 49 em 922 |
| voz de instituição (canal de organização, ninguém se apresentou) | 478 em 922 |
| falante NÃO SEI | 395 em 922 |
| papel provado | 31 em 922 (27 investigador, 4 agricultor/T8) |
| relato em primeira pessoa | 44 em 922 |
| `FACT_TIME` preenchido | 13 em 922 |
| `FACT_LOCATION` preenchido | 6 em 922 |
| texto que é a fala da pessoa (`QUOTE_IS_SPEAKERS_WORDS = SIM`) | 11 em 922 (só o ASR local dos reels) |
| suspeita de tradução (título e texto em línguas diferentes) | 119 em 922 |

**Os casos reais que os testes prendem:**
- **`QXwvQiufKxg` · Ellisabeth, agricultora em Haut-France.** Papel AGRICULTOR, entra no T8. «In 2024, we encountered
  difficulties with the septoria» sai com `FACT_TIME = in 2024`. `SPEAKER_PLACE` diz Haut-France, e `FACT_LOCATION` fica **NÃO SEI**.
- **`EsdOflKtFIU` · Damon Smith, patologista da University of Wisconsin Madison.** Papel INVESTIGADOR, organização
  UNIVERSIDADE_PESQUISA. O relato do trigo com fusarium tem o lugar da cena, «Arlington Prairie», e não o da
  universidade. `EXPERTISE_TEMATICA = NAO_PROVADA`, porque a apresentação dele não nomeia trigo nem fusarium.
- **`VZGepvBdkoI` · Rory Cranston.** Foi apresentado pela apresentadora como «technical product lead with Bayer»:
  papel TÉCNICO, organização EMPRESA. Mas **nunca** vira quem fala, porque foi apresentado por outra pessoa. Frases depois de «>>» ficam sem falante.
- **`C-FanW_CYMz` · reel da Syngenta Italia.** Voz da INSTITUIÇÃO, porque ninguém se apresenta. Texto ASR_LOCAL, com o
  segundo do áudio.

## Testes antes/depois — pelo nome, com rede fechada (proxy numa porta morta)

Ficheiros: `provas/voci_dal_campo/antes.json` e `depois.json`. O script é `provas/voci_dal_campo/testes_por_nome.py`.
Ele corre os 12 módulos vizinhos (os donos que eu importo, a transcrição e o mapa) mais o novo.

| | antes (base 69b0e23f) | depois |
|---|---|---|
| testes corridos | 349 | 396 (+47 novos) |
| falhas **novas** | — | **0** |
| falhas herdadas (o mesmo nome nos dois lados) | 4 | 4 |

As 4 herdadas são:
- 3 em `test_c6_especie_do_texto`: `test_so_o_dono_declara_o_vocabulario`,
  `test_nao_existe_rejeicao_global_de_traduzido` e `test_nenhum_codigo_le_a_auditoria_para_decidir_especie`. Todas
  vêm do caminho `tests\` com barra do Windows, e nenhuma cita o meu ficheiro;
- 1 em `test_c5_transcript_gate`: `test_c3_as_quatro_capacidades_continuam_oficiais`.

⚠️ **Não corri a suíte inteira.** Corri os 13 módulos da lista. Sobre os outros módulos: **NÃO SEI**. Não alterei
nenhum ficheiro existente além de `architecture.declared.json`, que só ganhou 2 peças.

## Mutação — `provas/voci_dal_campo/MUTACAO.json`

**20 de 20 mutantes mortos**, e o ficheiro foi reposto igual (mesmo sha256 antes e depois). Entre eles:
- publicação aceite como tempo do facto;
- lugar da pessoa copiado para o facto;
- apresentado-por-outro vira falante;
- «>>» ignorado;
- T8 para qualquer papel;
- criador apaga o papel profissional;
- citação normalizada;
- suspeita de tradução apagada;
- rótulo do dataset carimbado como espécie original;
- suspeita promovida a fala da pessoa;
- «ieri/hoy» convertido pela publicação;
- legenda sem pontuação volta a ser uma frase;
- maiúscula aleatória vira lugar;
- canal vira pessoa;
- papel vira expertise;
- validador sem a conferência da citação e sem a do T8;
- segundo vocabulário de cultura;
- «Palavra,» vira pessoa.

## O que NÃO está provado (e fica dito)

- **Atribuição sem diarização.** Quem fala é **presumido**: o último que se apresentou a si próprio, sem «>>» pelo
  meio e a menos de 6000 caracteres. Os 6000 foram **escolhidos, não medidos**. Não há gabarito, e por isso a
  precisão da atribuição é **NÃO SEI**. O mesmo vale para `FRASES_DA_CENA = 3` e para `ALCANCE_AUTO/TERCEIRO = 160/80`.
- **Leitor de lugar/tempo em inglês e espanhol.** É mínimo e é novo: não havia dono para essas línguas. O italiano usa o
  dono (`leis/fato_local.py`). Os topónimos em inglês não são resolvidos num gazetteer, e a precisão só é dita quando é país.
- **Vocabulário.** «olive fly», «Dacus», «polilla» não estão em `matriz_recorte.ISSUES`, e por isso saem `ISSUE = NAO SEI`.
  Isto é lacuna do vocabulário do dono, não ausência de problema. Não o alarguei aqui, porque não é meu.
- **Nomes em minúsculas** da legenda espanhola só se leem depois de um marcador forte («me llamo», «el doctor
  ingeniero agrónomo …»).
- **O casco não foi ligado.** O item tem `WHAT_IT_PROVES` e `WHAT_IT_DOES_NOT_PROVE` com os nomes que o
  `publicVoices` do portal lê. A projeção para o portal fica para a missão do casco.
- **`medidas/voz.py`** é o contrato de campos **por vídeo** da coleta (o papel ali é do canal). Não o dupliquei: o item
  Voce é **por frase**, e o canal entra como `PUBLISHER`.

## SHA e o mapa — ESTADO: PRONTO-SEM-MAPA

⚠️ **O System Map NÃO foi regerado.** A cadeia (`correr_a_cadeia.py REGERAR`) é trabalho pesado e só corre com a
LOCK-PESADO. Esperei **3 horas**, de 10:55 a 13:56 de 26/09, conferindo a cada 10 segundos. A LOCK nunca ficou livre:
passou da REPROC-EXTRATORES para a ACERVO-PARA-SALA-2 e depois para a ROTULOS-T4, todas com dono vivo. Por isso,
nem REGERAR, nem VALIDAR, nem `--conferir-carimbo` correram: o estado deles é **NÃO SEI**.

O que já está feito para o mapa: as duas peças novas estão declaradas em `system-map/data/architecture.declared.json`
(`C-VOCI-DAL-CAMPO`, `C-PROVA-VOCI-DAL-CAMPO`), e todo o conteúdo já está no índice e commitado.

**Falta, com a LOCK-PESADO:**
1. `py system-map/scripts/correr_a_cadeia.py REGERAR`;
2. commitar os gerados;
3. `VALIDAR` = PASS;
4. `impressao_da_arvore.py --conferir-carimbo` = IGUAL.

O SHA final é o último commit deste ramo no GitHub, o que traz este relatório. Um commit não pode conter o próprio
SHA (AGENTS.md).

## EM PALAVRAS SIMPLES

Fiz uma peça que lê o que alguém falou num vídeo ou numa palestra (já passado para texto) e tira de lá uma
«ficha de voz»: **quem** falou, **o que essa pessoa é** (agrónomo, técnico, pesquisador, agricultor), **a frase exata que ela disse**, de
que **planta** e de que **praga** falou, e **quando** e **onde** aconteceu.

É como um repórter cuidadoso com um caderno:
- **Não inventa o crachá.** Só escreve «agricultora» se a pessoa disse «sou agricultora». O canal que publicou o vídeo
  é o dono da estante, não quem está falando.
- **Onde a pessoa mora não é onde a praga apareceu.** A agricultora de Haut-France contou que teve septoria em 2024. A
  ficha guarda «2024», mas o lugar da praga fica **NÃO SEI**, porque ela não disse onde foi.
- **A data do vídeo não é a data do fato.** Se ela diz «este ano», a ficha não adivinha que ano é.
- **Tradução não é a fala da pessoa.** Em 119 frases de 922, o título está numa língua e o texto noutra. A ficha
  desconfia e diz, mas não afirma. Só 11 frases de 922 estão provadamente nas palavras da própria pessoa.
- **Uma voz não é uma contagem.** Uma pessoa dizendo «vi praga» não mede quanto de praga há na região.

Testei com os 47 vídeos que já estavam guardados e com exemplos inventados (marcados como inventados). Depois
estraguei a peça de propósito 20 vezes, e os testes apanharam as 20. Nada do que já existia quebrou: 0 falhas novas
em 396 testes.

HARD STOP.
