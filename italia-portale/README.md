# SINTONIA ITALY · ENGINEERING TAKEOVER

Baseline: `SINTONIA EAME - ITALIA PILOTO (8).zip`.

| pasta | o que é |
|---|---|
| `BASELINE/` | cópia congelada do ZIP 8. **Nunca editar.** Hashes em `audit/BASELINE-SHA256.txt`. |
| `client/` | o pacote de trabalho — é isto que vai para o cliente. |
| `audit/` | os instrumentos de medição e os relatórios. Não vai para o cliente. |

## Rodar as verificações

```
node audit/run.mjs            # tabela legível
node audit/run.mjs --verbose  # com todos os detalhes
node audit/run.mjs --json     # para máquina
node audit/run.mjs --only=D1  # só uma
```

Sai com código 0 apenas quando todas passam.

## Como a contagem `D.*` funciona

`audit/lib/scan.mjs` não procura pela letra `D`. Ele primeiro descobre **todo
identificador ligado a `window.ITALY_DEMO`** e depois conta as leituras por
qualquer um deles — renomear a fixture para escapar da contagem faz a contagem
**subir**, não descer.

Toda leitura é `DATA_BEARING_CORE` por padrão. Só desce de classe com um marcador
escrito no código, imediatamente antes da leitura:

```js
/*@VISUAL_ONLY apenas a cor da categoria*/ D.CAT[k].color
/*@EXPLICIT_DEMO modo demonstrativo, desligado por padrão*/ D.SIGNALS
```

O marcador precisa de um motivo escrito (verificação `D2`), para que a
classificação seja revisável em vez de afirmada.
