#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CANDIDATOS, IMPLEMENTADOS EXACTAMENTE COMO FORAM CONGELADOS.

    python3 provas/implementacoes_candidatas.py     (auto-teste, sem corpus)

Nenhum destes le o conjunto de avaliacao. Eles recebem UM item e devolvem UMA
decisao, na lingua da porta.

    O CONTRATO DE SAIDA NAO SE INVENTA AQUI.
    Ele ja existe: `admissao.Decisao`, com `resultado` em `admissao.RESULTADOS`.
    Um candidato que devolvesse `True/False` perdia a diferenca entre «nao» e
    «nao sei» — que e exactamente onde o custo assimetrico vive.
"""
import hashlib
import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402

DICIONARIO_EPPO = "data/samples/ES-T4-001/eppo-dictionary.json"
UNIVERSO = "T3"


def _normal(t):
    """Minuscula e sem acento. NAO lematiza — a decisao de nao lematizar e
    deliberada e tem prova externa dos dois lados (ver a ficha de C1)."""
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _por_palavra(termo, texto):
    """Fronteira de palavra — o oposto do substring cru da porta de hoje.

    E ISTO que separa `lancio` de `bilancio`. A porta actual usa
    `termo in texto`; aqui o termo tem de estar sozinho.
    """
    return re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(termo), texto)


class Candidato:
    """A interface comum. Recebe item, devolve `admissao.Decisao`."""
    CANDIDATE_ID = ""
    DETERMINISTICO = True

    def classificar(self, item):
        raise NotImplementedError

    def _decisao(self, item, resultado, motivo, evidencia=None):
        return adm.Decisao(
            item=str(item.get("id") or "?"), universo=UNIVERSO,
            resultado=resultado, regra=self.CANDIDATE_ID, motivo=motivo,
            evidencia=dict(evidencia or {}, candidato=self.CANDIDATE_ID))

    @staticmethod
    def _texto(item):
        """SO `texto`. Medido: e o unico campo de conteudo povoado."""
        return _normal(item.get("texto") or "")


# ══════════════════════════════════════════════════════════════════════════
# C1 · REGRA LEXICAL ESTRUTURADA — o controlo
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ O INVENTARIO E O DE HOJE, DE PROPOSITO. Este candidato isola UMA
# variavel: o casamento. Se eu trocasse tambem a lista, deixava de saber qual
# das duas coisas explicou a diferenca.
#
#     TROCAR DUAS COISAS E MEDIR UMA
#     E NAO MEDIR NENHUMA.
#
# O que muda face a porta de hoje, e so isto:
#   · fronteira de palavra em vez de substring cru;
#   · escopo de negacao — um termo dentro de «assenza di X» nao conta;
#   · peso: um termo isolado nao decide; e preciso evidencia acumulada.
NEGACOES = ("assenza", "assenti", "assente", "nessun", "nessuna", "senza",
            "non", "nao", "sem", "ausencia", "ausente")
JANELA_DE_NEGACAO = 4          # palavras antes do termo
LIMIAR_DE_PESO = 2             # termos distintos para afirmar


class C1LexicalEstruturada(Candidato):
    CANDIDATE_ID = "C1-LEXICAL-STRUCTURED"
    DETERMINISTICO = True

    def __init__(self):
        # A lista de hoje, lida do dono dela. NAO copiada para aqui.
        self.termos = {u: [_normal(t) for t in ts]
                       for u, ts in adm.PERGUNTAS_DO_UNIVERSO.items()}

    def _negado(self, texto, pos):
        antes = texto[:pos].split()[-JANELA_DE_NEGACAO:]
        return any(n in antes for n in NEGACOES)

    def _achados(self, texto, universo):
        fora = []
        for termo in self.termos.get(universo, []):
            m = _por_palavra(termo, texto)
            if m and not self._negado(texto, m.start()):
                fora.append(termo)
        return fora

    def classificar(self, item):
        texto = self._texto(item)
        if not texto.strip():
            return self._decisao(item, adm.NAO_SEI,
                                 "o item veio sem texto: nao da para olhar")
        meus = self._achados(texto, UNIVERSO)
        if len(meus) >= LIMIAR_DE_PESO:
            return self._decisao(
                item, adm.SIM,
                "%d termos deste universo, cada um como palavra inteira e "
                "fora de escopo de negacao" % len(meus),
                {"termos": meus[:8], "peso": len(meus)})
        outros = {u: self._achados(texto, u)
                  for u in self.termos if u != UNIVERSO}
        outros = {u: t for u, t in outros.items() if len(t) >= LIMIAR_DE_PESO}
        if outros and not meus:
            return self._decisao(
                item, adm.NAO,
                "nao fala deste universo e fala de outro com peso: %s"
                % ", ".join(outros), {"achado_noutro": outros})
        return self._decisao(
            item, adm.NAO_SEI,
            "evidencia abaixo do limiar (%d de %d termos necessarios). "
            "Ausencia de evidencia nao e evidencia de ausencia."
            % (len(meus), LIMIAR_DE_PESO), {"termos": meus})


# ══════════════════════════════════════════════════════════════════════════
# C2 · TAXONOMIA CONTROLADA — o conceito, nao a palavra
# ══════════════════════════════════════════════════════════════════════════
# O alvo da decisao e o CONCEITO. O nome cientifico e latim: nao muda de
# lingua, e por isso atravessa o problema de idioma nao resolvido sem deteccao
# de idioma nenhuma.
#
#     `Lobesia botrana` e `Erwinia amylovora` leem-se igual
#     em italiano, em ingles e em portugues.
#
# O inventario vem de FORA desta casa — tabelas oficiais — e nao da memoria de
# ninguem. E essa a resposta ao defeito que King, Lam & Roberts mediram: o
# problema nunca foi a pessoa lembrar-se mal, foi pedir-lhe que se lembrasse.
#
# ⚠️ LIMITE MEDIDO E DECLARADO: o dicionario local veio de tabelas espanholas.
# Generos so italianos podem nao estar la. Isso nao se esconde — conta-se.
GRUPOS_DE_ALVO = ("insect", "fungi", "bacteri", "virus", "nemato", "acar",
                  "hongo", "insecto", "bacteria", "nematodo", "ácaro", "acaro")
LIMIAR_DE_CONCEITOS = 2


class C2TaxonomiaConceito(Candidato):
    CANDIDATE_ID = "C2-TAXONOMY-CONCEPT"
    DETERMINISTICO = True

    def __init__(self):
        with open(os.path.join(RAIZ, DICIONARIO_EPPO), encoding="utf-8") as f:
            d = json.load(f)
        # Conceitos de ALVO (praga/doenca) — o universo T3 em linguagem de
        # taxonomia. Sao nomes cientificos, e por isso neutros de lingua.
        self.alvos = {}
        for codigo, v in d["pests"].items():
            cientifico = _normal(v.get("scientific") or "")
            # So binomios/generos reais: entradas de GRUPO nao sao conceitos.
            if not cientifico or " " not in cientifico and len(cientifico) < 5:
                continue
            if codigo.startswith("3"):      # os codigos de grupo comecam por 3
                continue
            self.alvos[codigo] = cientifico
        # Conceitos de CULTURA — sozinhos nao decidem T3, mas com um alvo ao
        # lado dizem «isto e um documento de praga NUMA cultura».
        self.culturas = {c: _normal(v.get("scientific") or "")
                         for c, v in d["crops"].items()
                         if v.get("scientific") and not c.startswith(("1", "3"))}
        self.total_conceitos = len(self.alvos)
        self._idx_alvos = self._indexar(self.alvos)
        self._idx_culturas = self._indexar(self.culturas)

    # ⚠️ ISTO FOI REESCRITO POR MEDICAO, E NAO POR GOSTO.
    # A primeira versao corria uma expressao regular POR CONCEITO sobre o
    # texto inteiro: 1348 varreduras. Medido: 15,8 s num texto de 340 mil
    # caracteres — e o corpus real tem um ficheiro de 7,9 MILHOES. Seriam
    # minutos por documento.
    #
    #     UM CANDIDATO QUE NAO CORRE NO CORPUS REAL
    #     NAO E UM CANDIDATO: E UMA INTENCAO.
    #
    # Agora o texto e percorrido UMA vez e os conceitos estao indexados pela
    # primeira palavra. A DECISAO E A MESMA — ha teste que compara as duas
    # implementacoes e exige resposta identica.
    @staticmethod
    def _indexar(inventario):
        por_primeira = {}
        for codigo, nome in inventario.items():
            if not nome or len(nome) < 5:
                continue
            partes = nome.split()
            por_primeira.setdefault(partes[0], []).append((codigo, nome, partes))
        return por_primeira

    def _conceitos(self, texto, inventario):
        indice = (self._idx_alvos if inventario is self.alvos
                  else self._idx_culturas)
        fichas = re.findall(r"[a-z0-9]+", texto)
        achados, vistos = [], set()
        for i, palavra in enumerate(fichas):
            for codigo, nome, partes in indice.get(palavra, ()):
                if codigo in vistos:
                    continue
                if fichas[i:i + len(partes)] == partes:
                    achados.append((codigo, nome))
                    vistos.add(codigo)
                elif len(partes) > 1 and len(palavra) >= 6:
                    # o genero sozinho tambem e um conceito (Erwinia, Lobesia)
                    achados.append((codigo, palavra))
                    vistos.add(codigo)
        return achados

    def classificar(self, item):
        texto = self._texto(item)
        if not texto.strip():
            return self._decisao(item, adm.NAO_SEI,
                                 "o item veio sem texto: nao da para olhar")
        alvos = self._conceitos(texto, self.alvos)
        if len(alvos) >= LIMIAR_DE_CONCEITOS:
            return self._decisao(
                item, adm.SIM,
                "%d conceitos de alvo do vocabulario controlado, pelo nome "
                "cientifico" % len(alvos),
                {"conceitos": [c for c, _n in alvos[:8]],
                 "nomes": [n for _c, n in alvos[:8]]})
        culturas = self._conceitos(texto, self.culturas)
        if alvos and culturas:
            return self._decisao(
                item, adm.SIM,
                "um conceito de alvo com cultura ao lado — praga numa cultura",
                {"conceitos": [c for c, _n in alvos[:4]],
                 "culturas": [c for c, _n in culturas[:4]]})
        # ⚠️ AQUI NAO SE DIZ «NAO». O vocabulario tem cobertura medida e
        # incompleta; a ausencia de conceito e confissao do inventario, nao
        # prova sobre o documento.
        return self._decisao(
            item, adm.NAO_SEI,
            "nenhum conceito de alvo acima do limiar (%d de %d). O "
            "vocabulario local e de origem espanhola e a sua cobertura em "
            "generos so italianos esta medida como incompleta — ausencia de "
            "conceito e confissao do inventario, nao prova sobre o documento."
            % (len(alvos), LIMIAR_DE_CONCEITOS),
            {"conceitos": [c for c, _n in alvos]})


# ══════════════════════════════════════════════════════════════════════════
# C3 · MODELO DE LINGUAGEM — e por que ele nao corre aqui
# ══════════════════════════════════════════════════════════════════════════
class C3ModeloDeLinguagem(Candidato):
    CANDIDATE_ID = "C3-LLM-STRUCTURED"
    DETERMINISTICO = False

    def disponivel(self):
        """MEDIDO, nao presumido: sem credencial, a API responde 401."""
        return bool(os.environ.get("ANTHROPIC_API_KEY")
                    or os.environ.get("ANTHROPIC_AUTH_TOKEN"))

    def classificar(self, item):
        if not self.disponivel():
            # Falha de execucao e ERRO. NUNCA NAO, nunca NAO_SEI — uma falha
            # de infraestrutura nao e uma opiniao sobre o documento.
            return self._decisao(
                item, adm.ERRO,
                "sem credencial de modelo neste ambiente: ninguem chegou a "
                "olhar para este documento",
                {"dependencia": "ANTHROPIC_API_KEY", "medido": "HTTP 401"})
        raise NotImplementedError(
            "o caminho com credencial nao foi exercitado neste ambiente e "
            "nao se declara o que nao se correu")


# ══════════════════════════════════════════════════════════════════════════
# C4 · CASCATA — conceito primeiro, leitura depois
# ══════════════════════════════════════════════════════════════════════════
class C4Cascata(Candidato):
    CANDIDATE_ID = "C4-HYBRID-CASCADE"
    DETERMINISTICO = False        # o segundo andar nao e deterministico

    def __init__(self):
        self.andar1 = C2TaxonomiaConceito()
        self.andar2 = C3ModeloDeLinguagem()

    # ⚠️ NEM TUDO O QUE O PRIMEIRO ANDAR NAO RESOLVE DEVE SUBIR.
    # A primeira versao escalava TODA abstencao — e um documento sem texto
    # nenhum subia para o segundo andar e voltava ERRO. Isso e trocar uma
    # confissao limpa («nao ha o que ler») por uma falha de execucao, que o
    # gate conta noutra caixa e com custo muito maior.
    #
    #     UMA CASCATA QUE ESCALA TUDO
    #     TRANSFORMA ABSTENCAO EM ERRO.
    #
    # Escala-se o que o VOCABULARIO nao alcancou. Nao se escala o que nao
    # tem conteudo: ai nao ha leitor que ajude.
    def classificar(self, item):
        if not self._texto(item).strip():
            d = self.andar1.classificar(item)
            d.evidencia = dict(d.evidencia, andar="1-TAXONOMIA",
                               candidato=self.CANDIDATE_ID,
                               nao_escalou="sem texto: nao ha o que ler")
            d.regra = self.CANDIDATE_ID
            return d
        d = self.andar1.classificar(item)
        if d.resultado in (adm.SIM, adm.NAO):
            # resolvido deterministicamente, e o registo NOMEIA o andar
            d.evidencia = dict(d.evidencia, andar="1-TAXONOMIA",
                               candidato=self.CANDIDATE_ID)
            d.regra = self.CANDIDATE_ID
            return d
        # escalado: e aqui que a indisponibilidade do segundo andar aparece
        e = self.andar2.classificar(item)
        e.evidencia = dict(e.evidencia, andar="2-ESCALADO",
                           candidato=self.CANDIDATE_ID,
                           porque_escalou=d.motivo[:120])
        e.regra = self.CANDIDATE_ID
        return e


CANDIDATOS_VIVOS = {
    "C1-LEXICAL-STRUCTURED": C1LexicalEstruturada,
    "C2-TAXONOMY-CONCEPT": C2TaxonomiaConceito,
    "C3-LLM-STRUCTURED": C3ModeloDeLinguagem,
    "C4-HYBRID-CASCADE": C4Cascata,
}


def impressao_da_implementacao():
    """O hash do ficheiro que implementa. Muda-o, e o benchmark sabe."""
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    print("IMPLEMENTACOES CANDIDATAS")
    print("=" * 70)
    print("  impressao do ficheiro: %s" % impressao_da_implementacao()[:40])
    exemplo = {"id": "auto-teste", "texto":
               "Bollettino con Lobesia botrana e Erwinia amylovora su Vitis"}
    for cid, classe in CANDIDATOS_VIVOS.items():
        try:
            c = classe()
            d = c.classificar(exemplo)
            print("  %-24s %-10s %s" % (cid, d.resultado, d.motivo[:64]))
        except Exception as e:                          # noqa: BLE001
            print("  %-24s ERRO NA CONSTRUCAO: %s" % (cid, e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
