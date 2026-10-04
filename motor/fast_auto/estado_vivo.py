# SINTONIA FAST - ESTADO VIVO ACUMULADO (ordem do dono 04/10: "ULTIMA RODADA != ESTADO ATUAL DA INTELIGENCIA").
#
# Le uma rodada FAST-AUTO/<RUN_ID>/CRUZAMENTO-COMERCIAL.json (conferida contra o SHA256SUMS.txt dela) e
# atualiza FAST-AUTO/INTELLIGENCE-CURRENT.json. A rodada NUNCA e editada (fica como historico/evidencia).
#
# Regras (so o minimo pedido pelo dono, nenhuma cognicao nova):
#  1. IDENTIDADE PERSISTENTE gerada por codigo, nunca pelo LLM nem pelo C01/C02 da rodada:
#       ID = "VIVO-" + sha256( conjunto ordenado de ANCORAS )[:16]
#       ANCORA = URL da evidencia + "|" + trecho literal normalizado (minusculas, espacos colapsados).
#     Usa a URL (estavel numa recaptura) e NAO o DOCUMENT_ID/RAW (muda a cada recaptura).
#     URL sozinha nao serve: Melinda e Invitalia (FAST-20261004T004228) tem a MESMA URL e o MESMO
#     DOCUMENT_ID e sao dois itens. O conjunto de trechos citados e o que os separa.
#  2. Mesmas ancoras outra vez -> ATUALIZA o item (nunca cria outro card).
#     Ancoras so parcialmente iguais -> NAO funde (semelhanca nao prova identidade); fica registado em
#     POSSIVEIS_DUPLICADOS para auditoria.
#  3. Rodada com NAO_PUBLICAR, vazia ou irrelevante NAO apaga nada. Item ausente da rodada seguinte continua vivo.
#  4. Item so sai da superficie por MOTIVO EXPLICITO registado: o proprio cerebro reclassificar O MESMO item
#     como NAO_PUBLICAR (motivo RECLASSIFICADO_NAO_PUBLICAR), ou `retirar` com um motivo da lista fechada.
#     Nada e apagado do arquivo: sai de DESTINOS e vai para FORA_DA_SUPERFICIE com o motivo.
#  5. NAO_PUBLICAR nunca entra em DESTINOS (nenhuma superficie de cliente).
#  6. Escrita atomica (tmp + os.replace); falha = o INTELLIGENCE-CURRENT.json anterior fica intacto.
#
# Uso:  python estado_vivo.py aplicar <FAST_AUTO_DIR> <RUN_ID> [<RUN_ID> ...] [--saida <arquivo>]
#       python estado_vivo.py retirar <FAST_AUTO_DIR> <ID_VIVO> <MOTIVO> "<porque>" [--saida <arquivo>]
import datetime, hashlib, json, os, sys

NOME = "INTELLIGENCE-CURRENT.json"
VERSAO = "ESTADO-VIVO/v1"
GAVETAS = ["OPPORTUNITY_RADAR", "FUTURE_RADAR", "PORTAFOGLIO", "COMPETITION", "MARKET_PULSE", "RESEARCH",
           "CROP_WINDOWS", "LABEL_INTELLIGENCE", "FIELD", "ARCHIVE"]
NAO_PUBLICAR = "NAO_PUBLICAR"
MOTIVOS_DE_SAIDA = ["ARCHIVED", "EXPIRED", "SUPERSEDED", "CONTRADICTED", "RETRACTED", "RESOLVED"]
REGRA_ID = ("VIVO- + sha256(ancoras ordenadas)[:16]; ancora = URL + '|' + trecho literal normalizado "
            "(minusculas, espacos colapsados); DOCUMENT_ID/RAW e C01.. da rodada NAO entram")


class RodadaRecusada(Exception):
    pass


def _sha_arquivo(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _norm(t):
    return " ".join((t or "").lower().split())


def ancoras(obj):
    out = set()
    for e in obj.get("EVIDENCIAS") or []:
        url = (e.get("URL") or "").strip()
        tr = _norm(e.get("trecho") or e.get("TRECHO"))
        if url and tr:
            out.add(url + "|" + tr)
    return sorted(out)


def id_vivo(obj):
    a = ancoras(obj)
    if not a:
        return None  # sem ancora verificavel = sem identidade: o item nao entra (registado, nunca inventado)
    return "VIVO-" + hashlib.sha256("\n".join(a).encode("utf-8")).hexdigest()[:16]


def _destinos_validos(obj):
    d = obj.get("DESTINO_FERRAMENTA") or []
    if isinstance(d, str):
        d = [d]
    return [x for x in d if x in GAVETAS or x == NAO_PUBLICAR]


def ler_rodada(raiz, run_id):
    pasta = os.path.join(raiz, run_id)
    pc = os.path.join(pasta, "CRUZAMENTO-COMERCIAL.json")
    ps = os.path.join(pasta, "SHA256SUMS.txt")
    if not os.path.exists(pc) or not os.path.exists(ps):
        raise RodadaRecusada("%s sem CRUZAMENTO-COMERCIAL.json ou SHA256SUMS.txt" % run_id)
    somas = {}
    for linha in open(ps, encoding="utf-8"):
        p = linha.strip().split(" ", 1)
        if len(p) == 2:
            somas[p[1].lstrip("*")] = p[0]
    s = _sha_arquivo(pc)
    if somas.get("CRUZAMENTO-COMERCIAL.json") != s:
        raise RodadaRecusada("%s CRUZAMENTO-COMERCIAL.json nao confere com SHA256SUMS.txt" % run_id)
    c = json.load(open(pc, encoding="utf-8"))
    if "DESTINOS" not in c:
        raise RodadaRecusada("%s sem DESTINOS (formato anterior ao destino por ferramenta)" % run_id)
    return c, s


def vazio():
    return {"TIPO": "INTELLIGENCE-CURRENT", "VERSAO": VERSAO,
            "ESTADO": "EXPERIMENTAL / NAO_PARA_CLIENTE",
            "O_QUE_E": "Estado vivo acumulado: o que o Sintonia sabe e considera publicavel AGORA. "
                       "Nao e a ultima rodada; as rodadas ficam intactas em FAST-AUTO/<RUN_ID>/.",
            "REGRA_DE_IDENTIDADE": REGRA_ID,
            "REGRA_DE_SAIDA": "item so sai da superficie por motivo explicito (RECLASSIFICADO_NAO_PUBLICAR ou " +
                              "/".join(MOTIVOS_DE_SAIDA) + "); ausencia numa rodada nao remove nada",
            "ATUALIZADO_EM": None, "ULTIMA_RODADA_APLICADA": None,
            "DESTINOS": {g: [] for g in GAVETAS}, "OBJETOS": [], "FORA_DA_SUPERFICIE": [],
            "POSSIVEIS_DUPLICADOS": [], "SEM_IDENTIDADE": [], "RODADAS_APLICADAS": []}


def carregar(arq):
    if os.path.exists(arq):
        return json.load(open(arq, encoding="utf-8"))
    return vazio()


def _recalcular_destinos(est):
    dest = {g: [] for g in GAVETAS}
    fora = []
    for o in est["OBJETOS"]:
        v = o["VIVO"]
        if v["SITUACAO"] != "ATIVO":
            fora.append({"ID": o["ID"], "MOTIVO": v["MOTIVO_DE_SAIDA"], "DESDE": v["SAIU_EM"]})
            continue
        for g in o.get("DESTINO_FERRAMENTA") or []:
            if g in dest:
                dest[g].append(o["ID"])
    est["DESTINOS"] = dest
    est["FORA_DA_SUPERFICIE"] = fora


def aplicar(est, run_id, c, sha_c, agora=None):
    """Aplica UMA rodada ao estado (em memoria). Devolve o resumo da aplicacao."""
    agora = agora or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    por_id = {o["ID"]: o for o in est["OBJETOS"]}
    por_ancora = {}
    for o in est["OBJETOS"]:
        for a in o["VIVO"]["ANCORAS"]:
            por_ancora.setdefault(a, set()).add(o["ID"])
    novos, atualizados, sem_mudanca, saidas = [], [], [], []
    for obj in c.get("OBJETOS") or []:
        iid = id_vivo(obj)
        local = obj.get("ID")
        dest = _destinos_validos(obj)
        if iid is None:
            est["SEM_IDENTIDADE"].append({"RUN_ID": run_id, "ID_NA_RODADA": local, "DESTINO": dest})
            continue
        anc = ancoras(obj)
        marca = {"RUN_ID": run_id, "ID_NA_RODADA": local, "CLASSE": obj.get("CLASSE"), "DESTINO": dest,
                 "CODIGO_HEAD": c.get("CODIGO_HEAD"), "CRUZAMENTO_SHA256": sha_c}
        so_publicar = [g for g in dest if g in GAVETAS]
        if iid not in por_id:
            if not so_publicar:
                # NAO_PUBLICAR novo: nao entra no estado vivo; fica so na rodada. MAS se partilha ancora com um
                # item vivo, o juizo contrario fica VISIVEL nesse item (nao o retira: semelhanca nao prova
                # identidade -- Invitalia e um subconjunto de Melinda e sao dois itens).
                for a in anc:
                    for outro in sorted(por_ancora.get(a, ())):
                        reg = {"NOVO": iid, "EXISTENTE": outro, "RUN_ID": run_id, "ID_NA_RODADA": local,
                               "TIPO": "NAO_PUBLICAR_PARTILHA_ANCORA", "ANCORA_EM_COMUM": a[:160]}
                        est["POSSIVEIS_DUPLICADOS"].append(reg)
                        por_id[outro]["VIVO"].setdefault("CONFLITOS", []).append(reg)
                sem_mudanca.append(iid)
                continue
            # parecido mas nao igual -> registo, nunca fusao silenciosa
            for a in anc:
                for outro in por_ancora.get(a, ()):
                    est["POSSIVEIS_DUPLICADOS"].append({"NOVO": iid, "EXISTENTE": outro, "RUN_ID": run_id,
                                                        "ANCORA_EM_COMUM": a[:160]})
            novo = dict(obj)
            novo["ID"] = iid
            novo["ID_NA_RODADA"] = local
            novo["DESTINO_FERRAMENTA"] = so_publicar
            novo["VIVO"] = {"SITUACAO": "ATIVO", "MOTIVO_DE_SAIDA": None, "SAIU_EM": None,
                            "ANCORAS": anc, "PRIMEIRA_RODADA": run_id, "ULTIMA_RODADA": run_id,
                            "CRIADO_EM": agora, "ATUALIZADO_EM": agora, "HISTORICO": [marca]}
            est["OBJETOS"].append(novo)
            por_id[iid] = novo
            for a in anc:
                por_ancora.setdefault(a, set()).add(iid)
            novos.append(iid)
            continue
        atual = por_id[iid]
        v = atual["VIVO"]
        if any(h["RUN_ID"] == run_id and h["ID_NA_RODADA"] == local for h in v["HISTORICO"]):
            sem_mudanca.append(iid)  # mesma rodada reaplicada: idempotente
            continue
        v["HISTORICO"].append(marca)
        if run_id < v["ULTIMA_RODADA"]:
            sem_mudanca.append(iid)  # rodada mais antiga que a ultima que tocou o item: so historico
            continue
        anterior = {"CLASSE": atual.get("CLASSE"), "DESTINO": atual.get("DESTINO_FERRAMENTA"),
                    "RUN_ID": v["ULTIMA_RODADA"]}
        if not so_publicar:
            # o cerebro reclassificou O MESMO item como NAO_PUBLICAR -> motivo explicito, nada apagado
            if v["SITUACAO"] == "ATIVO":
                v.update(SITUACAO="FORA_DA_SUPERFICIE", MOTIVO_DE_SAIDA="RECLASSIFICADO_NAO_PUBLICAR em " + run_id,
                         SAIU_EM=agora)
                saidas.append(iid)
            v["ULTIMA_RODADA"] = run_id
            v["ATUALIZADO_EM"] = agora
            continue
        guardar = {k: atual[k] for k in ("ID", "VIVO")}
        atual.clear()
        atual.update(obj)
        atual.update(guardar)
        atual["ID_NA_RODADA"] = local
        atual["DESTINO_FERRAMENTA"] = so_publicar
        if v["SITUACAO"] != "ATIVO" and v["MOTIVO_DE_SAIDA"].startswith("RECLASSIFICADO_NAO_PUBLICAR"):
            v.update(SITUACAO="ATIVO", MOTIVO_DE_SAIDA=None, SAIU_EM=None)  # o cerebro voltou a publica-lo
        v["ULTIMA_RODADA"] = run_id
        v["ATUALIZADO_EM"] = agora
        if anterior["CLASSE"] != atual.get("CLASSE") or anterior["DESTINO"] != so_publicar:
            v.setdefault("MUDANCAS", []).append({"ANTES": anterior, "DEPOIS": {
                "CLASSE": atual.get("CLASSE"), "DESTINO": so_publicar, "RUN_ID": run_id}})
        atualizados.append(iid)
    resumo = {"RUN_ID": run_id, "CRUZAMENTO_SHA256": sha_c, "CODIGO_HEAD": c.get("CODIGO_HEAD"),
              "APLICADA_EM": agora, "OBJETOS_NA_RODADA": len(c.get("OBJETOS") or []),
              "NOVOS": novos, "ATUALIZADOS": atualizados, "SEM_MUDANCA": sem_mudanca, "SAIRAM": saidas}
    est["RODADAS_APLICADAS"].append(resumo)
    if not est["ULTIMA_RODADA_APLICADA"] or run_id > est["ULTIMA_RODADA_APLICADA"]:
        est["ULTIMA_RODADA_APLICADA"] = run_id
    est["ATUALIZADO_EM"] = agora
    _recalcular_destinos(est)
    return resumo


def retirar(est, iid, motivo, porque, agora=None):
    if motivo not in MOTIVOS_DE_SAIDA:
        raise ValueError("motivo fora da lista fechada %s" % MOTIVOS_DE_SAIDA)
    if not (porque or "").strip():
        raise ValueError("retirar exige o porque")
    agora = agora or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    for o in est["OBJETOS"]:
        if o["ID"] == iid:
            o["VIVO"].update(SITUACAO="FORA_DA_SUPERFICIE", MOTIVO_DE_SAIDA="%s: %s" % (motivo, porque), SAIU_EM=agora)
            est["ATUALIZADO_EM"] = agora
            _recalcular_destinos(est)
            return
    raise KeyError(iid)


def gravar(est, arq):
    tmp = arq + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(est, f, ensure_ascii=False, indent=1)
    os.replace(tmp, arq)
    with open(arq + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write("%s *%s\n" % (_sha_arquivo(arq), os.path.basename(arq)))


def aplicar_rodadas(raiz, run_ids, arq=None):
    arq = arq or os.path.join(raiz, NOME)
    est = carregar(arq)
    resumos = []
    for r in run_ids:
        c, s = ler_rodada(raiz, r)
        resumos.append(aplicar(est, r, c, s))
    gravar(est, arq)
    return est, resumos


def main(argv):
    saida = None
    if "--saida" in argv:
        i = argv.index("--saida")
        saida = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) >= 3 and argv[0] == "aplicar":
        est, rs = aplicar_rodadas(argv[1], argv[2:], saida)
        for r in rs:
            print("APLICADA %s novos=%d atualizados=%d sem_mudanca=%d sairam=%d" % (
                r["RUN_ID"], len(r["NOVOS"]), len(r["ATUALIZADOS"]), len(r["SEM_MUDANCA"]), len(r["SAIRAM"])))
        print("ESTADO_VIVO " + " ".join("%s=%d" % (g, len(x)) for g, x in est["DESTINOS"].items() if x) +
              " | OBJETOS=%d FORA=%d" % (len(est["OBJETOS"]), len(est["FORA_DA_SUPERFICIE"])))
        return 0
    if len(argv) == 5 and argv[0] == "retirar":
        arq = saida or os.path.join(argv[1], NOME)
        est = carregar(arq)
        retirar(est, argv[2], argv[3], argv[4])
        gravar(est, arq)
        print("RETIRADO %s %s" % (argv[2], argv[3]))
        return 0
    print(__doc__ or "uso: ver cabecalho")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
