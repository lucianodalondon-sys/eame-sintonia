# CLAUDE.md — instruções permanentes do SINTONIA EAME

> ## ⚖️ LEI OBRIGATÓRIA DO PROJETO
>
> **Leia [`AGENTS.md`](AGENTS.md) antes de fazer qualquer alteração.**
>
> O SINTONIA System Map tem de continuar sincronizado com **toda** mudança
> relevante de arquitetura. **Rode o validador do System Map antes de fechar a
> tarefa:**
>
> ```bash
> py system-map/scripts/generate_system_map.py
> py system-map/scripts/validate_system_map.py
> ```
>
> A lei inteira vive em `AGENTS.md` e **não** é repetida aqui — uma lei em dois
> sítios diverge, e a partir daí nenhuma das duas vale.

---

Este arquivo é o **dono canônico** das instruções permanentes para o Claude Code neste
repositório. Regra registrada aqui vale para **todas as missões futuras** e não depende de
alguém lembrar dela na conversa.

Método, estados de evidência e disciplina `SOURCE → EVIDENCE → … → PORTAL` continuam em
[`README.md`](README.md). Este arquivo não os repete.

## MISSÕES SUBSTANCIAIS — CONTEXTO CURTO, PROVA FORTE

Para missões substanciais de engenharia, auditoria, arquitetura, integração, refactor,
Collection, Security, System Map, Scrap, Intelligence ou portal, use a skill de projeto
[`sintonia-mission-discipline`](.claude/skills/sintonia-mission-discipline/SKILL.md).

A skill é o dono do **método de execução da missão**: escopo estreito, autoridade apontada em
vez de repetida, diagnóstico separado de implementação quando há incerteza, contexto
progressivo, checkpoints em Git e poucos critérios objetivos de conclusão.

> **Tarefa longa não significa prompt longo.**
>
> O repositório carrega o conhecimento; a missão carrega a intenção; os testes carregam a
> prova; o Git carrega a continuidade.

---

## LEI DE DESIGN — O ADAMA DESIGN SYSTEM É A FONTE VISUAL OFICIAL

```
DESIGN_SOURCE_OF_TRUTH = ADAMA_DESIGN_SYSTEM
```

**Referência oficial — ADAMA DESIGN SYSTEM no Claude Design:**
<https://claude.ai/design/p/eb7480c7-6d86-43af-8315-a711143f8169?via=share>

Para qualquer trabalho de design, UI ou implementação visual do SINTONIA EAME, **consultar
primeiro** o ADAMA Design System nesse endereço. Componentes, padrões e ícones oficiais
devem ser reutilizados antes da criação de alternativas próprias.

### Quando esta lei se aplica

Sempre que a missão tocar em qualquer um destes: **design · UI · UX · casco · portal ·
componentes visuais · cards · navegação · tipografia · cores · espaçamentos · botões ·
ícones · ícones de culturas · ícones de doenças · padrões de interação · layout ·
responsividade · identidade visual.**

### NÃO INVENTAR ANTES DE CONSULTAR

Antes de criar qualquer componente visual novo:

1. **consultar** o ADAMA Design System no Claude Design;
2. **verificar** se já existe componente, padrão, ícone, estilo, comportamento, token visual
   ou solução equivalente;
3. **reutilizar ou adaptar** o padrão oficial quando ele existir.

Criar algo novo **somente** quando o Design System não possuir solução aplicável. Nesse caso,
declarar explicitamente na entrega:

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND
NEW_PATTERN_REQUIRED = YES
```

e escrever o motivo.

### Ícones

Regra especialmente importante. Havendo ícone oficial da ADAMA para **cultura, doença, praga,
categoria, produto ou funcionalidade**, usa-se o ícone oficial.

Não substituir por **emoji, ícone genérico, ícone inventado ou biblioteca externa** quando o
equivalente oficial existir.

### O link não é inspiração

O Design System não é referência visual opcional: é a fonte de verdade visual do projeto.
Decisão visual que se afaste dele precisa estar declarada e justificada na entrega — não
acontece em silêncio.

### O que está versionado aqui é extrato parcial, não a fonte

`italia-portale/client/_ds/adama-brandwell/` e `italia-portale/BASELINE/_ds/adama-brandwell/`
carregam apenas um extrato: tokens (`colors` · `typography` · `spacing` · `patterns` · `base`),
as fontes (LL Brown, Aleo) e `styles.css`. O próprio `_ds_manifest.json` descreve mais do que
está no repositório — componentes (`Button`, `Badge`, `Tag`, `Card`, `ProductIcon`),
guidelines, regras de marca, ícones de marca e de setor, logos, formas 'A' e templates **não
estão** versionados aqui. Esses vivem no Claude Design.

**Extrato local ≠ Design System.** O extrato serve para não divergir dos tokens em código; a
consulta continua sendo no Claude Design.

### Limite desta lei

O ADAMA Design System decide a **forma**. O
[`docs/design/CONTRATO-DE-DESIGN-SINTONIA.md`](docs/design/CONTRATO-DE-DESIGN-SINTONIA.md)
decide o que a forma **não pode esconder** (`NÃO SEI` visível, idade do dado ao lado do
número, fato ≠ interpretação ≠ ação). Em conflito entre os dois, o contrato de design vence:
nenhuma decisão visual revoga uma linha dele.
