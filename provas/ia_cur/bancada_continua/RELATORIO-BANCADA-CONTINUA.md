# FILA-PRECISA-DE-IA contínua + canário de 30 casos de janela (D29) — 25/09/2026

Ramo `curador-ate-pronta-v1`. **NÃO instalado.** Ele depende da CUR-PRONTA e da D32, que também
não estão instaladas: a produção 7cdb7ea4 não tem `bancada_ia.py` nem `janela_de_cultura.py`.

## 1 · O que foi construído

- **A fila é refeita a cada volta.** `ciclo_continuo.uma_volta` refaz a FILA-PRECISA-DE-IA em
  todas as voltas, sem rede. Escreve-a ao lado do livro de estados e anota no diário `FILA_IA`
  com o total, o total por pergunta e os casos D29. Se isso falhar, a volta não morre.
- **Achado:** dentro de um teste, a volta escrevia a fila em `curadoria/` — uma fuga para a árvore
  real. Consertado: a fila vai para o sítio do livro, e nos testes esse sítio é a pasta descartável.
- **`curadoria/bancada_continua.py`** trabalha por lotes. Só o robô vai à rede:
  - `preparar` — escolhe N casos (D29 primeiro) e busca no máximo 2 páginas por caso. Usa o
    portão de consenso IT (no início e de 20 em 20 pedidos) e respeita o robots, 2 s e no
    máximo 5 pedidos por anfitrião.
  - `extra` — busca no máximo 2 páginas a mais por caso, a pedido do agente.
  - `ingerir` — só aceita respostas que citem páginas **do lote**, com o sha256 que o robô
    registou, e escreve pelas portas da `bancada_ia`: RECEITA ou SEM_RECEITA.
- **D41.3 (regra nova):**
  - a bancada **recusa ir à rede** sem `--rede-autorizada "<missão>"`, e o nome da missão fica
    escrito no lote;
  - o teto de 5 pedidos conta o **domínio** (`www.site` e `site` são um só), como pede a D38;
  - as duas cópias que usei (`C:/cur/banc30` e `C:/cur/t2`) tinham a fila inteira copiada da
    produção (4.133 e 2.430 tarefas). **O robô não correu em nenhuma das duas**, mas esvaziei-as;
    o sha256 de antes está em `C:/cur/banc30-lotes/fila-copiada-antes-de-esvaziar.sha256`.
- **Testes:**
  - 124 verdes na cópia (bancada, ciclo, supervisor, guarda de isolamento), mais 2 da D41.3;
  - mutação 8 de 8 (sem autorização de rede · teto volta a ser por anfitrião · a volta não refaz a fila · escreve na árvore real · aceita página fora do
    lote · sem teto por anfitrião · sem teto de extras · sem portão de egresso).
- **A guarda de isolamento estava vermelha desde a D32** (o `test_bancada_ia` não mostrava
  `F.FILA =`). Foi falha minha: na D32 não corri essa guarda. Consertado.

## 2 · O canário: 30 casos de janela D29

Cópia `C:/cur/banc30` (código fef85aa3 + livros vivos de 7cdb7ea4, só lidos). Bytes em
`C:/cur/banc30-lotes/LOTE-20260925T072003Z/` (40 ficheiros, 7 MB, fora do Git; o sha256 de cada
página está em `LOTE-20260925T072003Z.json`).

- **Rede:** 41 pedidos para 30 casos (37 no `preparar` + 4 no `extra`), portão de consenso PASS IT.
- **Fila antes, na mesma cópia:** 535 casos, 58 deles D29, todos RECEITA (o reparo R1 desistiu deles).
- **Respostas:** as 30 entraram pela porta (0 recusadas); nenhuma receita HTML passaria a régua.

| o que o agente encontrou | casos |
|---|---:|
| a página **é o boletim** (rota fixa: ARSAC ×2, LaMMA, ARPA Lombardia, ARPAE ×2, CAAR Liguria, vigilância Liguria) | 8 |
| boletins montados por **JavaScript** (a lista não está no HTML) | 6 |
| boletins em **PDF**, com receita escrita (SFN, ERSA FVG, Campania) | 3 |
| NÃO SEI (as páginas lidas não mostram o boletim) | 2 |
| fonte genérica (não publica boletins) | 2 |
| 1 cada: folha Excel · casca vazia · PDF fixo · sem itens no HTML · links mortos (404) · site encerrado · espera o robots RFC · serviço com login · páginas temáticas | 9 |

**Depois:** fila da cópia 535 → 505; os 30 saíram, como «respondida SEM_RECEITA depois da última prova
(espera prova nova)»; os D29 pendentes passaram de 58 para 28.

## 3 · O que isto diz (decisões para o dono)

O agente não falhou por não achar receitas: **a porta de receita só sabe fazer «lista HTML →
item HTML»**, e as fontes de janela publicam de outras três maneiras.

1. **Boletins em PDF (3 de 30).** O canário PDF e a régua PDF já existem (D32 (4)). Falta a porta
   de receita aceitar `OUTPUT_TYPE=PDF` na proposta (hoje o `reparar_contrato.aplicar` só muda a
   ACQUISITION). Com isso, SFN, ERSA e Campania têm receita escrita e prova.
2. **A página é o boletim (8 + 1 PDF fixo).** Precisa de um canário para `STATIC_ENDPOINT` HTML
   (a rota fixa já existe no validador; o canário só conhece HTML_LINK_DISCOVERY) e de uma régua
   de «boletim numa página fixa» — a da régua T1/T2 janela (regua-t1-janela-v1 / regua-t2-v1).
3. **JavaScript (6).** Precisa de uma capacidade de renderização (navegador) — fora do âmbito sem
   decisão.

O agente continua sem ir à rede e sem API paga. O próximo passo contínuo é **agendar** o
`preparar` e o `ingerir` com uma sessão da assinatura (ex.: `claude -p` por tarefa agendada) —
**não construído**; é decisão do dono, e só vale a pena depois das decisões 1 e 2.
