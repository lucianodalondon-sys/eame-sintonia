#!/usr/bin/env python3
"""
DISEASE INTELLIGENCE · OBSERVATIONAL · THE HUMAN READING

Every sentence below is assembled from a field of the structured cell. There is no free text
and no LLM: if a fact is not in the model, no sentence can carry it. The renderer is not
allowed to know anything the model does not.

The last block is the one that matters most, and it is generated, not written by hand:
WHAT WE CANNOT CONCLUDE.
"""

CANNOT_CONCLUDE = [
    "that the infestation will rise or fall - this tool contains no forecast of any kind",
    "that an outbreak is coming",
    "anything about groves nobody visited: the panel is the monitored network, not a random "
    "sample of the region",
    "that there is a commercial opportunity - a disease-pressure reading is not an opportunity "
    "and this tool may not turn it into one",
]


def render_province(cell, adama, attention, lang="pt"):
    o, a, q = cell["observation"], cell["analysis"], cell["quality"]
    L = []
    L.append(f"{cell['region'].upper()} · {cell['province'].upper()} · "
             f"OLIVEIRA · MOSCA-DA-AZEITONA")
    L.append(f"data de referência: {cell['as_of']}")
    L.append("")

    L.append("O QUE FOI OBSERVADO")
    if o.get("value_pct") is None:
        L.append("  nada: nenhuma visita utilizável na janela.")
    else:
        L.append(f"  {o['value_pct']}% das azeitonas amostradas com "
                 f"{'infestação viva' if o['metric']=='ACTIVE_INFESTATION_COUNT' else 'dano registado'}")
        L.append(f"  ({o['infested_drupes']} de {o['drupes_sampled']} azeitonas dissecadas)")
        L.append(f"  banda da própria fonte: {o['source_band']['label']} "
                 f"({o['source_band']['meaning']})")
        L.append(f"  base: {o['n_visits']} visitas a {o['n_sites']} olivais, "
                 f"{o['n_orgs']} organizações")
        L.append(f"  janela: {o['window'][0]} a {o['window'][1]}")
        L.append(f"  última observação: {o['last_observation']}")
        if o.get("n_visits_excluded_by_sanity_rules"):
            L.append(f"  visitas excluídas por regra de sanidade: "
                     f"{o['n_visits_excluded_by_sanity_rules']}")
    L.append("")

    L.append("CONTRA A PRÓPRIA HISTÓRIA")
    L.append(f"  {a['historical_state']}")
    L.append(f"  {a['historical_reason']}")
    if a.get("historical_state_unmatched") and \
            a["historical_state_unmatched"] != a["historical_state"]:
        L.append(f"  (sem emparelhar os olivais daria "
                 f"{a['historical_state_unmatched']} — não é o que publicamos)")
    L.append(f"  safras comparáveis: {a['matched_panel_seasons']}")
    L.append("")

    L.append("MUDANÇA OBSERVADA")
    L.append(f"  {a['observed_trend']}")
    L.append(f"  {a['observed_trend_reason']}")
    L.append("")

    L.append("CONFIANÇA")
    L.append(f"  observação publicável: {'sim' if q['observation_publishable'] else 'não'}"
             f" — {q['publishable_reason']}")
    L.append(f"  comparação histórica publicável: "
             f"{'sim' if q['historical_comparison_publishable'] else 'não'}")
    L.append("")

    L.append("RELEVÂNCIA ADAMA")
    L.append(f"  {adama['relevance']}")
    L.append(f"  {adama['reason']}")
    L.append(f"  classe de atenção interna: {attention['attention_class']} "
             f"(regra: {attention['rule_applied'][0]})")
    L.append("")

    L.append("O QUE NÃO PODEMOS CONCLUIR")
    for c in CANNOT_CONCLUDE:
        L.append(f"  - {c}")
    if a["matched_panel_seasons"] < cell["params"]["MIN_BASELINE_SEASONS"]:
        L.append("  - nada sobre como isto se compara com o passado desta província: "
                 "os olivais monitorizados hoje não são os de então")
    return "\n".join(L)


def render_region(cells, adama, lang="pt"):
    pub = [c for c in cells if c["quality"]["observation_publishable"]]
    hist = [c for c in pub if c["quality"]["historical_comparison_publishable"]]
    below = [c for c in hist if c["analysis"]["historical_state"] == "BELOW_HISTORICAL"]
    above = [c for c in hist if c["analysis"]["historical_state"] == "ABOVE_HISTORICAL"]
    rising = [c for c in pub if c["analysis"]["observed_trend"] == "INCREASING_OBSERVED"]
    bands = {}
    for c in pub:
        b = (c["observation"].get("source_band") or {}).get("meaning", "?")
        bands[b] = bands.get(b, 0) + 1
    drupes = sum(c["observation"].get("drupes_sampled", 0) for c in pub)
    visits = sum(c["observation"].get("n_visits", 0) for c in pub)
    last = max((c["observation"].get("last_observation") or "") for c in pub) if pub else None
    L = [f"TOSCANA · OLIVEIRA · MOSCA-DA-AZEITONA · {cells[0]['as_of']}", ""]
    L.append("O QUE FOI OBSERVADO")
    L.append(f"  {len(pub)} de {len(cells)} províncias com observação publicável")
    L.append(f"  {visits} visitas, {drupes} azeitonas dissecadas")
    L.append(f"  última observação: {last}")
    L.append(f"  bandas da fonte: {bands}")
    L.append("")
    L.append("CONTRA A PRÓPRIA HISTÓRIA (só onde os olivais são comparáveis)")
    L.append(f"  {len(hist)} de {len(cells)} províncias têm safras comparáveis suficientes")
    L.append(f"  abaixo do histórico: {[c['province'] for c in below]}")
    L.append(f"  acima do histórico: {[c['province'] for c in above]}")
    L.append(f"  sem comparação possível: "
             f"{[c['province'] for c in cells if c not in hist]}")
    L.append("")
    L.append("MUDANÇA OBSERVADA")
    L.append(f"  a subir nas janelas já ocorridas: {[c['province'] for c in rising]}")
    L.append("")
    L.append("RELEVÂNCIA ADAMA")
    L.append(f"  {adama['relevance']} — {adama['reason'][:200]}")
    L.append("")
    L.append("O QUE NÃO PODEMOS CONCLUIR")
    for c in CANNOT_CONCLUDE:
        L.append(f"  - {c}")
    return "\n".join(L)
