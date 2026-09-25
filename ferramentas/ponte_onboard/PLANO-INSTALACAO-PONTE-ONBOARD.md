# Plano de instalação — PONTE-ONBOARD (quem instala: o coordenador; um escritor no vivo)

**Ensaiado numa cópia fiel** (`RELATORIO-PONTE-ONBOARD.md`, secção Ensaio). O writeset está em `WRITESET-PONTE-ONBOARD.json`: código, testes e mapa. **Não toca em nenhum livro.**

## 0 · Antes

- O vivo tem de estar em **7cdb7ea4** (a base deste ramo). Se não estiver, refazer o merge contra o vivo novo antes de instalar.
- `git status` do vivo: nenhum ficheiro do writeset pode aparecer sujo. Medido a 25/09: **nenhum** (os sujos são livros `curadoria/*.json`, `candidatas/`, `data/`).
- Guardar a tabela do coletor, que é a única coisa que o onboarding escreve:
  `copy regras\italy_contracts_onboarded.json <corte>\italy_contracts_onboarded.json` + o sha256.

## 1 · Instalar o código (bot quieto)

```
cd <arvore do bot>
git fetch origin ponte-onboard-v1
git merge --ff-only origin/ponte-onboard-v1        # ensaiado: 7cdb7ea4 e a base, fast-forward
```

Reiniciar o supervisor: ele só carrega o código novo ao arrancar (a Tarefa SINTONIA-Arranque, ou o procedimento habitual).

**Logo a seguir:** o diário do supervisor mostra um evento `ONBOARDING` com `NINGUEM_ENTROU`. As provas antigas não têm impressão, por isso ainda não entra ninguém.

## 2 · Provar as rotas uma vez (rede: portão de consenso PASS IT antes e depois; ≤ 1 fonte por domínio por ronda)

A lista das fontes é o `FICA` de `py curadoria/onboardar_rotas_provadas.py`, com o vivo daquele momento. A 25/09 eram 28. Agrupar por domínio em rondas, como em `ENSAIO-2`:

```
py medidas/canario_rotas_elegiveis.py --fontes=<ronda 1> --juntar
py medidas/canario_rotas_elegiveis.py --fontes=<ronda 2> --juntar
...
```

## 3 · Ver entrar (sem mais comandos)

Em ≤ 10 min, porque a prova mudou de bytes, o supervisor anota `ONBOARDING` / `ONBOARDOU` com `ESCRITAS`. No ensaio foram **17**.

Conferir: `py curadoria/onboardar_rotas_provadas.py` deve dar `ENTRA=0` (já estão todas na tabela).

## Desfazer

- **Só a entrada das fontes:** repor `regras/italy_contracts_onboarded.json` a partir do corte. O sha256 volta ao de antes (ensaio: 856f833f, 206 contratos).
- **O código:** `git reset --keep 7cdb7ea4` e reiniciar o supervisor. O canário volta a ler o Git HEAD e o onboarding volta a não ser chamado, como antes.
- Nenhum livro do Curator é escrito por esta instalação.
