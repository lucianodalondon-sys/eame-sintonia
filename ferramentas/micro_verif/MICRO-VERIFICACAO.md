# MICRO-VERIFICAÇÃO (D74) — plano de uma MICRO, não de uma onda

Ramo `micro-verif-v1`, a partir do vivo `e5cd691f` (PACOTE-TEMPO-LUGAR instalado).
- **Rede fechada nesta missão:** nenhum pedido. A Sala não foi lida.
- **Objetivo da MICRO** (quando o coordenador a mandar correr): provar que a coleta REAL, com o código
  instalado, faz chegar à Sala **itens novos** com publicação, lugar da fonte, data e lugar do facto,
  e as bases de cada um.

## 1 · A regra de escolha — escrita ANTES de medir (este commit vem antes de qualquer medida)

**Universo:** a coorte CONGELADA do vivo.
- Ficheiro: `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`, 28 fontes.
- `sha256` do blob no commit: `06f87b97761d73281bc341d87d7a644ec0c5014a291265db2b8372732bf4977f`. É o que
  `onda_web.py` confere.
- O ficheiro no disco tem outro sha (`5401845a…`), só por causa do fim de linha do Windows (CRLF). O JSON
  é o mesmo, e a `onda_web.py` compara o conteúdo.

**Categorias** (a mesma fonte pode cumprir mais de uma, mas conta para uma só):
- **A · myfruit:** `IT-T10-018`, obrigatória.
- **B · boletim ou agência T2:** as `IT-T2-*` da coorte.
- **C · instituição de pesquisa (CNR/CREA/ENEA):** `IT-T5-160` (ibba.cnr.it), `IT-T5-167` (crea.gov.it),
  `IT-T5-185/186/187` (enea.it).
- **D · publica a data na página:** JSON-LD `datePublished`, `<meta property="article:published_time">`
  ou `<time datetime=…>`.
  - Medido **sem rede** nas matérias já guardadas no armazém do vivo (`data/collection-store/italy/<SID>/`),
    só leitura.
  - Conta a fração de matérias guardadas que têm uma dessas marcas.
  - **Não pode ser a myfruit** (queremos um segundo site a provar a data).

**Como se escolhe dentro de cada categoria, por esta ordem:**
1. Mais **alvos novos D40**. A medida é `scripts/capa_materia/medir_d40.mjs`, com os índices guardados
   em 25/09 07:30Z (`INDICES-D40-V1.json`), contra uma **cópia** do livro de observações atual do vivo.
2. Para a D: maior fração de matérias com data marcada.
3. Desempate por `SOURCE_ID`.
4. Fonte sem índice guardado = alvos novos `NAO MEDIDO`, e fica atrás das medidas.
5. **Uma fonte com 0 alvos novos medidos não é escolhida** se houver outra na categoria com ≥ 1.

**Domínios diferentes (D38):**
- as fontes escolhidas têm domínios registáveis todos diferentes;
- se a melhor de uma categoria repetir o domínio de uma já escolhida, passa-se à seguinte.

**Quantas:**
- A + B + C + D = 4.
- Junta-se **uma 5.ª** só se houver outra fonte T2 com ≥ 1 alvo novo e domínio novo. A razão: os boletins
  T2 são a outra metade da data e lugar (D61).
- Nunca mais de 6.

**Previsão:** escrita por fonte **antes** de correr: documentos novos; publicação sim/não; lugar da
fonte sim/não; data e lugar do facto prováveis.
