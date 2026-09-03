# VOCI · o que falta para a voz pública entrar na prioridade comercial

> Estado: **NÃO ENTRA AINDA**, e por medição, não por prudência.
> A camada existe no pacote, é carregada pelo motor e **nunca foi indexada**.
> Este documento diz exatamente o que precisa acontecer para que ela possa
> entrar — e o que ela nunca poderá fazer, mesmo pronta.
>
> Nada aqui pede conserto de coletor. A camada V1.1 **não** mexeu no scraper.

---

## 1 · O que existe hoje, contado

| | |
|---|---:|
| vozes em `PUBLIC-VOICES.json` | **79** |
| client-safe | **65** |
| com `CROP_IDS` preenchido | **76** |
| com `ISSUE_IDS` preenchido | **0** |
| com `REGION_IDS` preenchido | **15** |

Por tipo: **58** `AUDIENCE_COMMENT` (comentário sob vídeo) e **21**
`IDENTIFIED_VOICE`. Por espécie declarada: `FIRST_PERSON_FIELD_REPORT` e
`TECHNICAL_REPLY` — relato de quem aplicou, e resposta técnica de quem
respondeu. **Nenhum boletim oficial carrega isso.**

**Cobertura por cultura**, e ela cai exatamente onde os casos comerciais são
mais finos em corroboração:

| cultura | vozes |
|---|---:|
| videira | 18 |
| maçã | 14 |
| milho | 13 |
| tomate | 12 |
| oliveira | 10 |
| arroz | 5 |
| **trigo duro** | **2** |
| soja · beterraba | 1 · 1 |

---

## 2 · Por que ela não entra: o motor nunca a chamou

`PUBLIC-VOICES.json` é carregado em `main()` de `v21_oportunidades.py` e
**nunca indexado por arquétipo nenhum**. A única referência a `PUBLIC_VOICE` em
todo o motor é uma regra de red team:

```python
if any(e.get('ENTITY_TYPE') == 'PUBLIC_VOICE' for e in ev) and len(ev) < 3:
    m.append('voz isolada tratada como incidencia')
```

Essa regra **nunca pode disparar**, porque nenhuma voz jamais entra como apoio.
É uma trava correta guardando uma porta que ninguém abre.

    UMA REGRA QUE NUNCA DISPARA NÃO PROTEGE NADA: ELA SÓ PARECE PROTEGER.

---

## 3 · Os três bloqueios, e o que cada um exige

### BLOQUEIO 1 · o alvo não está normalizado — `ISSUE_IDS` vazio em 79 de 79

O problema existe em texto livre, num campo próprio:

```
ISSUE:   FLAVESCENCE          CASE_ID: IT-VINE-FLAVESCENCE
ISSUE:   FUSARIUM             CASE_ID: IT-DURUM_WHEAT-FUSARIUM
```

O léxico canônico (`v21_normalizar.ISSUE_ALIAS`) já conhece
`ISSUE_FLAVESCENCE` e `ISSUE_FUSARIUM`. **A normalização simplesmente não foi
rodada sobre este campo.**

- **O que exige:** rodar `N.issue_id(r['ISSUE'])` sobre o campo declarado
  `ISSUE` — que é campo, não prosa — e gravar `ISSUE_IDS`.
- **O que NÃO exige:** ler o texto do comentário para adivinhar o alvo. O
  comentário é prova do que a pessoa escreveu, não campo de alvo.
- **Sem isto:** não há par cultura × alvo, e sem par a voz não se liga a caso
  nenhum. É o bloqueio que sozinho mantém a camada fora.

### BLOQUEIO 2 · a data é relativa

```
DATE:            NAO SEI
DATE_RELATIVE:   «1 year ago» · «4 years ago (edited)»
REFERENCE_DATE:  NAO SEI
DATE_NOTE:       «a rota devolve tempo RELATIVO. Converter inventaria precisão.»
```

O portão do tempo rejeita, **e tem razão**: uma voz de «4 anos atrás» não diz
nada sobre a pressão desta semana. E converter «1 year ago» numa data
inventa precisão que a rota não devolveu.

- **O que exige:** uma rota de coleta que devolva data absoluta, ou um campo
  `DATE_OBSERVED_AT` da própria coleta com a janela de incerteza declarada.
- **O que NÃO exige:** converter o relativo em absoluto no ingest.
  `NÃO SEI` é resposta.
- **Sem isto:** a voz pode corroborar *que o assunto existe*, nunca *que ele é
  de agora*.

### BLOQUEIO 3 · a região falta em 64 de 79

`REGION: NAO SEI` na maioria; `COUNTRY_OF_FACT: NOT_KNOWN` em boa parte.

- **O que exige:** região declarada pela própria voz ou pelo canal, com
  evidência — o mesmo contrato de `GEOGRAPHY_STATE` que os boletins já cumprem.
- **O que NÃO exige:** deduzir a região pelo canal, pelo sotaque ou pela cultura
  citada.
- **Sem isto:** a voz só sustenta alegação nacional — e uma voz que sustenta
  alegação nacional **promove geografia**, que é o defeito que o portão A existe
  para impedir.

---

## 4 · O que ela poderá fazer, resolvido isso

**Pode ser a segunda família independente.** Medido na auditoria: **30 dos 37
casos do V1 tinham UMA família externa**, 7 tinham duas, nenhum tinha três. A
voz é a única fonte do pacote que fala em **primeira pessoa do campo** — um
boletim oficial nunca carrega isso.

**Pode confirmar ou contradizer a DIREÇÃO.** A camada V1.1 lê o que o boletim
manda fazer (`NEED_DIRECTION`). Se o serviço diz «sospendere» e a voz de campo
diz que ainda há pressão, isso é **discordância mensurável entre serviço e
campo** — e é inteligência real, não ruído.

**Pode dirigir investigação.** Uma voz sobre um alvo que nenhum boletim cita é
uma pergunta a fazer, não uma resposta a publicar.

**Pode preencher o trigo duro.** As vozes trazem
`CASE_ID: IT-DURUM_WHEAT-FUSARIUM`. A necessidade do trigo duro já está aqui —
o que falta é o outro lado (ver `DURUM-WHEAT-VERDICT` no relatório da V1.1: os
14 produtos ADAMA com registro em trigo duro não têm nenhum par de rótulo
extraído).

---

## 5 · O que ela nunca poderá fazer

O próprio registro já escreve, em cada voz:

> «não prova que quem escreveu é produtor; não prova ocorrência no campo; não
> prova falha nem eficácia de produto; **não prova incidência regional**»

Portanto, quando a camada entrar:

- **voz isolada nunca é incidência** — a regra de red team que já existe passa a
  poder disparar, e deve;
- **voz nunca abre `SALES_READY` sozinha** — ela amplifica uma necessidade que
  um documento com direção já declarou;
- **contagem de vozes nunca é tendência** — dez comentários no mesmo canal são
  um canal, não uma região;
- **`PERSON_IDENTITY_STATE: NAO_ATRIBUIVEL`** continua valendo: o handle é
  pseudonimizado, e a fonte é o CANAL, nunca o autor.

    VOZ PÚBLICA NÃO É TENDÊNCIA REGIONAL.
    ELA É UMA PESSOA QUE ESCREVEU UMA FRASE, COM DATA E LUGAR OU SEM.

---

## 6 · O que já está pronto do lado do motor

A V1.1 deixou a porta preparada, sem abri-la:

- `PUBLIC_VOICE` já está em `TIPOS_QUE_OBSERVAM` — quando a voz tiver região,
  ela responderá pela geografia da afirmação como qualquer observação, e não
  será confundida com autorização de rótulo;
- a régua comercial **não conta famílias**: uma segunda família amplifica e
  ordena, não autoriza. A voz não precisará ser exigida para nada;
- `NEED_DIRECTION` já separa quem manda agir de quem manda parar, e a voz
  entrará nessa mesma leitura, com `NEED_EXCERPT` guardando a frase original —
  **que não será traduzida**, porque é prova.

Falta apenas o que os três bloqueios pedem. Nenhum deles é modelagem: os três
são **dado**.

---

## 7 · Ordem sugerida, e por quê

1. **Bloqueio 1 primeiro** (normalizar `ISSUE`) — é o único que não depende de
   coleta nova e sozinho já liga a voz a um par cultura × alvo. Custo: uma
   passagem do léxico que já existe.
2. **Bloqueio 3 depois** (região declarada) — decide se a voz pode sustentar
   alegação regional ou só nacional.
3. **Bloqueio 2 por último** (data absoluta) — é o que exige rota nova, e é o
   que separa «corrobora o assunto» de «corrobora agora».

Enquanto os três não fecham, a camada continua **carregada e não indexada** — e
isso deve estar escrito na tela, não escondido no código.

    A CAMADA QUE NÃO ENTRA TEM DE DIZER QUE NÃO ENTRA.
    SILÊNCIO PARECE AUSÊNCIA DE DADO, E AQUI HÁ 79.
