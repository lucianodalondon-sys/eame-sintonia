# DONO DO SYSTEM MAP — SINTONIA EAME · ITÁLIA

> **Para que serve esta página.** Quando uma missão futura precisar do System Map
> técnico da Itália, é esta a casa que deve usar. Uma linha, e não cinco.

```
SYSTEM_MAP_IT_CURRENT_OWNER_BRANCH   claude/system-map-reconciled-v1
SYSTEM_MAP_IT_CURRENT_OWNER_HEAD     cc476edd33378e67b902f227a55f427d299870f7
COUNTRY_SCOPE                        IT
PROMOTED_AT                          2026-09-15
```

---

## ⚠️ ISTO NÃO É PUBLICAÇÃO. SÃO DUAS COISAS, E CONFUNDI-LAS JÁ CUSTOU CARO.

Este repositório **já tem** convenção de promoção, e ela está inteira em
[`../../system-map/CANONICAL-PUBLICATION.json`](../../system-map/CANONICAL-PUBLICATION.json),
com portão próprio em `system-map/scripts/portao_da_promocao.py`. Ela responde a
outra pergunta:

```
CANONICAL-PUBLICATION.json   ->  que versão está NO AR, no endereço fixo
esta página                  ->  que linha um agente deve ABRIR para trabalhar
```

O próprio contrato de publicação escreve a diferença numa linha:

> `CANONICAL PUBLISHED != LATEST SOURCE`

O endereço oficial serve a versão **aprovada**, que por desenho não é a atual.
Promover código-fonte e promover um endereço são actos diferentes, com riscos
diferentes.

### Por que a convenção de publicação NÃO foi usada aqui — medido

A autoridade de promoção declarada é uma só: `release/canonical`. Entrar nela é
por *merge*, e o que entra **vai ao ar sozinho** pela Vercel. Medido em
2026-09-15, contra `cc476edd`:

| medida | valor |
|---|---|
| base comum das duas linhas | `1c99a48b`, de 2026-09-09 |
| esta linha avançou | **427 commits** |
| `release/canonical` avançou | **74 commits** |
| uma contém a outra? | **não** — são irmãs |
| ficheiros que divergem | **620**, dos quais **33** no portal |

E o próprio portão da promoção já escreveu o que aconteceria:

> *«O projecto Vercel serve o PORTAL INTEIRO. Promover um deployment do System
> Map promove o site todo com ele. Foi assim que a promoção directa deixou de ser
> uma opção: a linha do mapa tinha-se separado do portal há trinta commits, e
> pô-la no alias teria levado o portal de volta para antes da Label
> Intelligence.»*

Aqui não são trinta commits: são 427 contra 74, com 33 ficheiros do portal a
divergir. **Promover pela via da publicação levaria o portal para trás.** O
portão existe para recusar exactamente isto, e recusaria.

```
UMA LINHA DE CÓDIGO PRONTA  !=  UM PORTAL PRONTO PARA IR AO AR.
```

Por isso esta promoção é **de dono técnico**, por registo, e não de endereço.
O endereço fica onde está, com o dono que já tem.

---

## O QUE FOI PROMOVIDO, E COM QUE PROVA

`claude/system-map-reconciled-v1` @ `cc476edd`, com:

```
SYSTEM_MAP_CHECK = PASS          22 portões, P1_SEM_DRIFT e P8_UM_DONO incluídos
DETERMINISTIC    = SIM           duas corridas, conteúdo idêntico
LAW_046/047/048/049 = PASS
RED_TEAM_SURVIVORS = 0
COLLECTION · SALA · IDENTITY     regressão idêntica à base: 0 falhas novas
```

Nenhuma branch foi apagada. `main` não foi tocada. Nenhum caminho foi renomeado.

---

## O NOME DO PROJECTO

```
SINTONIA EAME            o guarda-chuva regional
SINTONIA EAME — ITÁLIA   o produto que existe hoje
COUNTRY_CODE             IT
```

Tudo o que for específico da Itália leva `IT`/`ITALIA` **quando isso puder ser
feito sem quebrar caminho ou contrato**. `EAME` sozinho fica reservado ao que for
comprovadamente partilhado entre dois ou mais países.

Enquanto o título do mapa dizia só «SINTONIA EAME», quem o abria contava as peças
de **um** país e concluía que eram as de **todos**.

---

## O SCRAP / AQUISIÇÃO

É uma capacidade própria, e a interface é esta:

```
IT — COLLECTION  pede
IT — SCRAP       escolhe e corre ferramentas MUTÁVEIS de aquisição
IT — SCRAP       devolve RAW + método + prova + erro/custo
IT — COLLECTION  aplica contratos, identidade, procedência e admissão
IT — SALA        recebe só pelo fluxo canónico
```

**O SCRAP não é uma segunda Collection.** Não é dono da admissão, nem da Sala,
nem da identidade, nem da verdade do dado.

No mapa de hoje a separação é feita pela **lente `SCRAP / aquisição`**: 14
componentes de aquisição mais 2 de fronteira (o orquestrador, que pede, e a porta
de admissão, que recebe). Sem os dois de fronteira o bloco flutuaria a falar com
o nada.

Não há faixa física, e o motivo está medido, não opinado — ver a nota na zona
`Z-EXECUCAO` do ficheiro declarado. A reorganização física do SCRAP é **missão
própria**, e não se faz de passagem.

---

## V1 E V2

```
SYSTEM MAP V1   o mapa técnico oficial da arquitetura IT   <- esta linha
SYSTEM MAP V2   visão paralela e complementar, outra pergunta e outro leitor
```

**V2 não substitui V1**, e quem o escreveu disse-o no primeiro commit: *«É a
ferramenta de quem programa, e continua intacta.»* V2 não foi apagado e não é o
técnico oficial.

---

## DÍVIDAS QUE FICAM VISÍVEIS — registadas, não corrigidas aqui

1. **`_gavetas.py` não tem dono declarado.** 252 ficheiros o importam. Não se lhe
   deu dono só para zerar um contador.
2. **A seta `C-ORQUESTRADOR → C-SCRAP-SOCIAL` continua `DECLARED`/`UNKNOWN`.**
   Fica assim até alguém a provar. Separar visualmente não promove nada a verde.
3. **Normalização física multi-país (`<gaveta>/it/`).** O padrão já existe para
   Espanha (`guarda/es/`, `coleta/es/`, `superficie/es/`); a Itália é que está
   implícita na raiz. Mexe em caminhos reais, com contratos e banco atrás —
   missão própria.
4. **`censo_de_escopo`** continua na linha `claude/italy-source-isolation-jb6wed`:
   é a ponta da funcionalidade de isolamento de fontes, e sozinha não corre.
5. **`control_plane` + `_dispor`** continuam em `claude/funny-hypatia-y7ho5s`:
   registo de autoridades, com `SUPERSEDES` e `DIVERGENT_COPIES`, e dependem de
   `controle/censo_do_controle.py` e `controle/portao_do_controle.py`, que não
   vivem nesta árvore.

---

## QUANDO ESTA PÁGINA DEIXA DE VALER

Ela envelhece em silêncio se ninguém a mudar. Quem promover outra linha a dona do
System Map IT **muda estas quatro linhas no mesmo commit** — senão passam a
existir dois donos, e:

> **Dois donos do mesmo endereço servem a versão errada sem ninguém perceber.**
