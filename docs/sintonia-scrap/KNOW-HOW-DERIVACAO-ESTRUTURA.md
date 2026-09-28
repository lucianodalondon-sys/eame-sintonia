# KNOW-HOW · DERIVACAO-ESTRUTURA (28/09/2026, D131)

> `KNOW_HOW_DELTA` da capability «parsing técnico inicial» (Scrap Engineer especificou,
> a Collection implementou no ficheiro dela). A integrar em `SINTONIA-EAME-KNOW-HOW.md`
> no próximo § livre pelo coordenador — não se numera aqui para não colidir com as
> outras linhas. Prova: `DERIVACAO-ESTRUTURA.md` na raiz do ramo
> `claude/derivacao-estrutura-v1-girw5u`.

**`limpar()` achatava a estrutura, e a régua de extração não estava na receita.**
`coleta/texto_fonte.py::limpar` trocava TODA etiqueta HTML por espaço: o RAW 2272 (CREA,
Xylella/oliveira, 186 `</div>`, 28 `<p>`) saía como UMA linha de 8 988 caracteres, e tudo o
que lê por linha a jusante (`leis/fato_do_texto.py::corpo`) ficava cego — corpo = 0. O HTML
guardado estava inteiro; quem destruía a estrutura era a derivação, e por isso o conserto é
ali, não no leitor que a recebe achatada (etiqueta de BLOCO → `\n`, inline → espaço; 1 → 80
linhas, corpo 0 → 7 705). O segundo erro era mais fundo e silencioso: a receita do derivado
(`executor_texto_de_html.receita`, que vira `parameters_hash`) dizia QUEM extrai
(`TEXT_OWNER`) mas nunca COMO — mudar o algoritmo mudava o texto e deixava a identidade igual,
e o derivado achatado e o estruturado do mesmo RAW seriam os dois `texto-de-html` "2". Agora
a régua entra na receita com nome (`TEXT_RULE`) e com a impressão do comportamento
(`TEXT_RULE_PROBE_SHA256` = sha256 do que `limpar()` devolve para uma SONDA fixa), a versão
subiu para "3", e `tests/test_a_receita_tem_versao.py` reprova quem mudar o comportamento de
`limpar()` sem subir a versão (mutação provada). **Quem muda o COMO de uma derivação muda a
identidade do derivado; se a régua não está na receita, a receita mente.** E o limite, medido:
devolver a estrutura não separa menu de corpo — `corpo()` filtra por linha, deixa passar menu
longo e passa a largar linhas curtas que antes viajavam coladas (ex.: «Wine Paris – 9-11
febbraio 2026»); isso é do elo seguinte, não desta régua.
