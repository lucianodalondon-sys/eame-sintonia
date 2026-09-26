# TRAVA-SEDE-V2 — a trava de plataforma sobre o vivo 83de0ccd

**Ramo:** `trava-sede-v2` = `83de0ccd` + cherry-pick de `002a8a35` (trava-sede-v1). **Conflitos:** 0. Os 3 ficheiros não tinham mudado entre `e5cd691f` e `83de0ccd`. **Gerados:** nenhum tocado. O mapa fica para a INTEGRA.

## O que a trava faz
`leis/lugar_da_organizacao.py`: `PLATAFORMAS` + `e_plataforma(host)`. Um endereço de plataforma (YouTube, Instagram, LinkedIn, Facebook, X, TikTok, Threads, Vimeo, Spotify, Spreaker, anchor.fm, Apple/Google Podcasts, SoundCloud, Podbean, Buzzsprout, Libsyn, Megaphone, Podtrac, Loquis) sai
`SOURCE_LOCATION = NAO SEI` · `NAO DECLARADA` · `BASIS = "NAO SEI: <host> e endereco de plataforma; a sede de uma conta nao se herda de outras contas do mesmo host — so pelo site oficial que aponta a conta"`.
Antes: `youtube.com/…` e `instagram.com/…` davam `ITALY/COUNTRY`, com o país de OUTRAS fontes do Atlas.

## Provas contra o vivo 83de0ccd
- **Testes novos (3)**, em `tests/test_soc_tempo_publicacao_e_lugar.py`: sem a trava dão FAIL, FAIL e ERROR; com a trava dão ok, ok e ok.
- **Mutação** `provas/_mutantes_soc_tempo.py`: **8/8 mortos**, incluindo o mutante «conta de plataforma herda a sede do vizinho (DA-16)».
- **Os 917 testes de local da fonte** (28 ficheiros: `git grep -l SOURCE_LOCATION|lugar_da_organizacao|lugar_da_fonte` em `tests/test_*.py` e `curadoria/test_*.py`), comparados **por nome** (`unittest -v`, 893 linhas legíveis dos 917; 24 nomes quebram linha e não entram no emparelhamento):
  - mudaram de resultado: **só os 3 novos** (FAIL/ERROR → ok);
  - falhas com a trava: **20**, todas iguais sem a trava (herdadas da base nesta máquina).
- Efeito lateral: um teste reescreve `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`. Não entra no commit; cópia guardada em `stash «trava-sede-v2-censo-reescrito-pelo-teste»`.

## Coordenação com a SEDE-37-PREP (term_a5e50162, ramo `sede-37-v1`)
Medido na worktree `reparo-fontes-v1` (ramo `sede-37-v1` = `83de0ccd`, **sem commit**, só `ferramentas/sede37/` por rastrear):
- `achar_paginas_de_sede.py` procura links de contatti/dove-siamo/chi-siamo **no mesmo domínio registável da fonte**.
- Hoje: 65 fontes, 146 endereços em `PAGINAS-DE-SEDE.json`, **0 de plataforma**. Sem efeito hoje.
- **Risco quando entrarem fontes sociais:** o domínio de um canal é `youtube.com`, e o «contatti» achado seria o do YouTube.
- **Pedido à SEDE-37 (não editei o trabalho dela):** antes de procurar páginas de sede, usar a trava:

```python
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import lugar_da_organizacao as LO
if LO.e_plataforma(LO.host(index_url)):
    # sede NAO SEI: conta de plataforma; so pelo site oficial que aponta a conta
    continue
```

E, quando a regra de sede dela gravar `SOURCE_LOCATION`, passar pelo mesmo `LO.lugar_da_organizacao(site_oficial)` ou pelo mesmo `e_plataforma`, para haver **um dono só** da lista de plataformas.
