#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ESPINHA COMUM DA INTELLIGENCE — máquina de estados descartável.

    MISSAO   C-INT-SPINE-01
    ESPECIE  PROVA EXECUTAVEL DE CONTRATO. NAO E RUNTIME PRODUTIVO.
    ESTADO   DEFINED + PROVED_IN_DISPOSABLE.  IMPLEMENTED = NO.

    python3 provas/espinha_da_intelligence.py          # demonstração
    python3 -m unittest tests.test_espinha_da_intelligence -v

O QUE ESTE FICHEIRO É
---------------------
A forma executável da espinha arbitrada em
`research/intelligence/INTELLIGENCE-SPINE-CONTRACT-V1.md`. Ele existe para que
a próxima missão não tenha de reinventar estados nem fronteiras, e para que as
doze provas do enunciado tenham onde morder.

O QUE ESTE FICHEIRO **NÃO** É
-----------------------------
    NAO le a Sala de Espera real.       NAO escreve em lado nenhum.
    NAO importa Collection runtime.     NAO chama rede, banco nem coletor.
    NAO e o INTELLIGENCE_RUN produtivo. Esse e a missao seguinte.

O `ItemPronto` daqui segue o contrato de saída do dono da Sala
(`admissao/sala_de_espera.py::CAMPOS_READY`, COL-LAW-043). ⚠️ Até
INT-CONSERTOS-EXP isto era uma **cópia declarada** de 19 campos; o dono cresceu
para 23 e a cópia não o soube. A lista passou a ser LIDA do dono (ver
`campos_do_dono`), sem executar runtime da Collection. Se o
contrato upstream mudar, `CAMPOS_DO_READY` muda com ele; se o dono deixar de
o declarar, a espinha rebenta ao ser importada — a divergência aparece em vez
de se esconder.

⚠️ **E JÁ FICOU ERRADO UMA VEZ — O AVISO FUNCIONOU.** A cópia nasceu com doze
campos contra `f888776d`. Ao reconciliar com o trunk, `C-COL-PRESERVE-FACTS-V1`
tinha acrescentado **sete**, e o teste que confere a cópia contra o contrato
real falhou, que é exactamente o que se lhe pediu. Nenhum dos doze antigos
desapareceu: a fronteira só **cresceu**.

    ESTAGIO · PUBLISHED_AT · OBSERVED_AT · FACT_TIME_BASIS ·
    FACT_LOCATION_BASIS · SOURCE_DECLARED_EVIDENCE_CLASS · FATO

AS TRÊS LEIS QUE O CÓDIGO IMPÕE, E NÃO SÓ DESCREVE
--------------------------------------------------
    1. A Intelligence NAO CUNHA identidade upstream.       (INT-LAW-031)
    2. NAO SEI nunca vira FALSO, nem vira AUSENCIA.        (INT-LAW-112)
    3. Falta de matéria-prima produz REQUISITO, nunca rota. (INT-LAW-020/151)
"""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

CONTRATO = "ESPINHA_DA_INTELLIGENCE/v1"

# ── O VOCABULÁRIO DA IGNORÂNCIA ─────────────────────────────────────────────
# Uma só palavra, porque duas divergem. É a mesma que a porta da Collection
# escreve quando não sabe (`admissao.pronto_para_inteligencia`).
NAO_SEI = "NAO SEI"


class LeiViolada(Exception):
    """A máquina recusou-se a fazer o que lhe pediram, e diz porquê.

    Não é um erro de programação: é o portão a funcionar. Um portão que só
    regista e deixa passar não é um portão.
    """


# ═══════════════════════════════════════════════════════════════════════════
# 0 · A FRONTEIRA — O QUE A COLLECTION ENTREGA, MEDIDO
# ═══════════════════════════════════════════════════════════════════════════
#: Os campos do READY, **lidos do dono da Sala** — `admissao/sala_de_espera.py`,
#: `CAMPOS_READY` —, e nao escritos aqui. A Intelligence LÊ isto. Não escreve,
#: não completa, não inventa.
#:
#: ⚠️ D8 (INT-CONSERTOS-EXP). Isto ERA uma cópia de 19 campos, com um teste que
#: fixava o número 19. A migration 033 fez o dono crescer para 23
#: (`PUBLISHED_AT_BASIS`, `SOURCE_LOCATION_BASIS`, `COMPLETUDE_TEMPO_LUGAR`,
#: `TEMPO_LUGAR_EVIDENCIA`) e a cópia ficou para trás — e o teste, pregado em 19,
#: continuou verde. Uma cópia com alarme que olha para si própria não avisa nada.
#:
#:     DUAS LISTAS DO MESMO CONTRATO DIVERGEM. UMA NAO.
#:
#: Lê-se pela ÁRVORE SINTÁTICA do ficheiro do dono, e não por `import`: esta
#: espinha continua a NÃO executar runtime da Collection (banco, psql, telemetria)
#: — só lê o literal que o dono escreveu. Se o literal sumir ou deixar de ser uma
#: tupla de textos, a importação REBENTA: falhar fechado, nunca cair para uma
#: lista de reserva.
DONO_DOS_CAMPOS = Path(__file__).resolve().parents[1] / "admissao" / "sala_de_espera.py"


def campos_do_dono(caminho: Path = DONO_DOS_CAMPOS,
                   nome: str = "CAMPOS_READY") -> Tuple[str, ...]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    for no in arvore.body:
        if (isinstance(no, ast.Assign) and len(no.targets) == 1
                and isinstance(no.targets[0], ast.Name) and no.targets[0].id == nome):
            valor = ast.literal_eval(no.value)
            if (isinstance(valor, tuple) and valor
                    and all(isinstance(c, str) for c in valor)):
                return valor
            break
    raise LeiViolada(f"o dono {caminho.name} deixou de declarar {nome} como tupla "
                     "de campos — a espinha nao inventa uma lista de reserva")


CAMPOS_DO_READY = campos_do_dono()

#: O que a Intelligence agrícola PRECISA e que hoje **não atravessa** a
#: fronteira. Medido em `provas/auditoria_agro_fronteira.py` (missão
#: C-INT-AGRO-BENCH-01): 0 destes campos existe no contrato de saída.
#: Estão aqui nomeados para que a falta seja contável, e não uma impressão.
CAMPOS_QUE_NAO_ATRAVESSAM = (
    "EVIDENCE_SPECIES",   # OBSERVED_FIELD_SIGNAL · AGROCLIMATIC_SIGNAL · ...
    "SUBJECT_ID",         # EPPO, CAS, registration_id
    "METHOD", "UNIT", "SCALE",
    "DENOMINATOR", "TARGET_POPULATION",
    "PPP_USE",            # a tupla de seis eixos
)

#: ⚠️ O QUASE-HOMÓNIMO. NÃO APAGAR ESTA NOTA.
#: A fronteira passou a transportar `SOURCE_DECLARED_EVIDENCE_CLASS`, e o nome
#: parece o `EVIDENCE_SPECIES` que está na lista acima. **Não é**, e o dono do
#: campo escreveu porquê em `admissao/admissao.py`:
#:
#:     DECLARADO PELA FONTE != MEDIDO NO DOCUMENTO.
#:
#: É a expectativa de quem PUBLICA, sobre o que costuma publicar — texto livre,
#: e pode trazer duas espécies de uma vez («OBSERVED_FIELD_SIGNAL +
#: TECHNICAL_GUIDELINE»). `EVIDENCE_SPECIES` é a espécie DESTE item, uma só, do
#: vocabulário fechado `ESPECIES_DE_EVIDENCIA`. Ler o primeiro como o segundo
#: faria um boletim agroclimático da ARPAV virar relato de campo — que é
#: precisamente a confusão que `AGROCLIMATIC_NAO_PROVA` existe para impedir.
#:
#: O bloqueio G0 **continua de pé**, e continua por medida, não por sorte: o
#: que chegou foi a expectativa da fonte, não a espécie do item.
QUASE_ESPECIE = "SOURCE_DECLARED_EVIDENCE_CLASS"

#: As espécies de evidência que os contratos de fonte declaram. A espécie é do
#: DONO DA FONTE — a Intelligence lê-a, nunca a atribui por leitura do texto.
ESPECIES_DE_EVIDENCIA = (
    "OBSERVED_FIELD_SIGNAL",      # alguém viu, e afirma-o
    "AGROCLIMATIC_SIGNAL",        # o tempo permitiria
    "MODEL_OUTPUT",               # um modelo calculou
    "CONFIRMED_INCIDENCE",        # diagnóstico, com método
    "REGULATORY_AUTHORIZATION",   # um registo, de uma autoridade
    "COMPANY_CLAIM",              # alguém que vende, a dizer
    "SCIENTIFIC_RESULT",          # ensaio, com método
)

#: ⚠️ A LEI QUE A ESPÉCIE CARREGA, E QUE O ENUNCIADO CHAMA «CASO A».
#: Está escrita nos contratos IT-T2-001/002 e não atravessa a fronteira hoje.
AGROCLIMATIC_NAO_PROVA = (
    "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE. "
    "Condicoes favoraveis dizem que o tempo PERMITIRIA. "
    "Nao dizem que aconteceu, nem onde, nem quanto."
)


@dataclass(frozen=True)
class ItemPronto:
    """Uma unidade READY pousada na Sala de Espera. **Dono: COLLECTION.**

    Congelada de propósito: a Intelligence não tem como lhe mexer, nem por
    engano. `especie` e `sujeito_declarado` entram separados porque **hoje não
    fazem parte do contrato de saída** — quem os passar aqui está a simular o
    TARGET, e os testes dizem qual dos dois estão a correr.
    """
    ITEM_ID: str
    UNIVERSO: str
    TEXTO: str
    SOURCE_ID: str
    FACT_TIME: str = NAO_SEI
    FACT_LOCATION: str = NAO_SEI
    SOURCE_LOCATION: str = NAO_SEI
    RAW_OBSERVATION_ID: str = NAO_SEI
    CAPTURED_AT: str = NAO_SEI
    CORRIDA: str = NAO_SEI
    ADMITIDO_POR: str = NAO_SEI
    ESTADO: str = "PRONTO_PARA_INTELIGENCIA"

    # ── os sete de `C-COL-PRESERVE-FACTS-V1` ──────────────────────────────
    # Chegaram com o trunk. `NAO SEI` por omissão, como todos os outros: um
    # campo que passou a existir não é um campo que passou a estar preenchido.
    ESTAGIO: str = NAO_SEI
    FACT_TIME_BASIS: str = NAO_SEI
    FACT_LOCATION_BASIS: str = NAO_SEI
    PUBLISHED_AT: str = NAO_SEI
    OBSERVED_AT: str = NAO_SEI
    SOURCE_DECLARED_EVIDENCE_CLASS: str = NAO_SEI   # ⚠️ ver QUASE_ESPECIE
    FATO: Any = NAO_SEI

    # ── os quatro da migration 033 (TEMPO-E-LUGAR) ────────────────────────
    # Chegaram com o dono da Sala. `NAO SEI` por omissão, pela mesma razão.
    PUBLISHED_AT_BASIS: str = NAO_SEI
    SOURCE_LOCATION_BASIS: str = NAO_SEI
    COMPLETUDE_TEMPO_LUGAR: Any = NAO_SEI
    TEMPO_LUGAR_EVIDENCIA: Any = NAO_SEI

    # ── fora do contrato de hoje ──────────────────────────────────────────
    especie: str = NAO_SEI          # CAMPOS_QUE_NAO_ATRAVESSAM[0]
    sujeito_declarado: str = NAO_SEI  # CAMPOS_QUE_NAO_ATRAVESSAM[1]

    def dentro_do_contrato_de_hoje(self) -> Dict[str, str]:
        """Só os campos do contrato. É isto que a Intelligence recebe em produção."""
        return {c: getattr(self, c) for c in CAMPOS_DO_READY}


# ═══════════════════════════════════════════════════════════════════════════
# 1 · A HISTÓRIA — APPEND-ONLY, E É ISSO QUE A TORNA HISTÓRIA
# ═══════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Evento:
    """Um facto acontecido na corrida. Imutável, ordenado, com motivo.

    `ORDEM` é tempo lógico, não relógio de parede: uma prova que depende da
    hora do dia não é uma prova, é um horário.
    """
    ORDEM: int
    OBJETO: str
    DE: str
    PARA: str
    PORTAO: str
    MOTIVO: str
    REGRA: str
    PROVENIENCIA: Tuple[str, ...] = ()


class Historia:
    """O livro da corrida. Escreve-se no fim; não se apaga, não se reescreve.

        CORRECAO NAO APAGA ESTADO ANTERIOR.   (INT-LAW-210)
    """

    def __init__(self) -> None:
        self._eventos: List[Evento] = []

    def escrever(self, **kw: Any) -> Evento:
        e = Evento(ORDEM=len(self._eventos), **kw)
        self._eventos.append(e)
        return e

    def de(self, objeto: str) -> List[Evento]:
        return [e for e in self._eventos if e.OBJETO == objeto]

    def estados_de(self, objeto: str) -> List[str]:
        ev = self.de(objeto)
        return ([ev[0].DE] if ev else []) + [e.PARA for e in ev]

    def __len__(self) -> int:
        return len(self._eventos)

    def __iter__(self):
        return iter(self._eventos)


# ═══════════════════════════════════════════════════════════════════════════
# 2 · OS OBJETOS ANALÍTICOS
# ═══════════════════════════════════════════════════════════════════════════
SINAL_ESTADOS = ("SINAL", "RASTREADO", "DESCARTADO")
HIPOTESE_ESTADOS = ("HIPOTESE", "EM_VALIDACAO", "REJEITADA", "PROMOVIDA")
ACHADO_ESTADOS = ("CONFIRMADO", "REBAIXADO", "REABERTO", "REJEITADO",
                  "SUBSTITUIDO")

#: Estados do cruzamento. `NOT_POSSIBLE` não é falha: é resposta. (INT-LAW-091)
CRUZAMENTO_ESTADOS = ("PROVADO", "PARCIAL", "NOT_POSSIBLE", "UNKNOWN")

#: A validação é um ESTADO DO OBJETO, não uma caixa de entrada. A «fila» é a
#: projeção `[h for h in hipoteses if h.validacao == PENDENTE]`, e mais nada.
VALIDACAO = ("NAO_EXIGIDA", "PENDENTE", "APROVADA", "RECUSADA")


@dataclass
class Sinal:
    """Uma leitura tipada de UM item READY, dentro de UMA corrida.

    Não é um registo novo (o registo é o item, e é da Collection).
    Não é uma interpretação (isso é o julgamento, e nasce na hipótese).
    É uma **classificação com proveniência**, e não cria facto nenhum.
    """
    SIGNAL_ID: str
    ITEM_ID: str          # aponta para cima; não substitui
    SOURCE_ID: str
    ESPECIE: str
    SUJEITO: str
    MATCH_TYPE: str       # EXACT · UNRESOLVED · ABSENT
    FACT_TIME: str
    FACT_LOCATION: str
    PRECISAO_GEO: str
    PRECISAO_TEMPO: str
    PRECISAO_SEMANTICA: str
    REGRA: str
    ESTADO: str = "SINAL"
    RASTREIO: Dict[str, str] = field(default_factory=dict)
    MOTIVO_DO_DESCARTE: str = ""


@dataclass
class Cruzamento:
    """Coincidência estrutural com chave de junção provada. **Sem julgamento.**

    Repare no que esta classe **não** tem: nenhum campo diz `apoia`,
    `contradiz` ou `suficiente`. Essa é a fronteira do §8.2 do enunciado, e ela
    está desenhada em vez de prometida — um cruzamento que julgasse teria de
    ganhar um campo, e ganhar esse campo é a alteração que o red team procura.
    """
    CROSSING_ID: str
    SINAIS: Tuple[str, ...]
    PERGUNTA: str
    JOIN_KEY: Dict[str, str]
    ESTADO: str
    PRECISAO_GEO: str
    PRECISAO_TEMPO: str
    PRECISAO_SEMANTICA: str
    ORIGENS_INDEPENDENTES: int
    ORIGENS_TOTAIS: int
    MOTIVO: str = ""


@dataclass
class Aresta:
    """SUPPORTS / CONTRADICTS. Dirigida, com proveniência própria."""
    TIPO: str             # APOIA · CONTRADIZ
    EVIDENCIA: str        # SIGNAL_ID ou CROSSING_ID
    REGRA: str
    MOTIVO: str


@dataclass
class Hipotese:
    """O **candidate finding**, com o nome que esta casa já lhe deu.

    `CANDIDATE_FINDING` e `ANALYTIC_HYPOTHESIS` são o mesmo objeto. Manter os
    dois nomes seria manter dois donos da mesma coisa.
    """
    HYPOTHESIS_ID: str
    PERGUNTA: str
    APOIA_SE_EM: Tuple[str, ...]
    PREMISSAS: Tuple[str, ...]
    O_QUE_A_DERRUBA: str
    NIVEL: str
    ARESTAS: List[Aresta] = field(default_factory=list)
    ESTADO: str = "HIPOTESE"
    VALIDACAO: str = "NAO_EXIGIDA"
    MOTIVO_DA_REJEICAO: str = ""

    def contraditorio(self) -> List[Aresta]:
        return [a for a in self.ARESTAS if a.TIPO == "CONTRADIZ"]


@dataclass
class Achado:
    """FINDING. Só nasce de uma hipótese promovida por um portão."""
    FINDING_ID: str
    HYPOTHESIS_ID: str
    PERGUNTA: str
    NIVEL: str
    ESTADO: str
    TRACO_DE_DECISAO: Dict[str, Any]
    ACTIVE: bool = True


@dataclass(frozen=True)
class Requisito:
    """INTELLIGENCE_REQUIREMENT — a única saída da Intelligence em direção à
    Collection, e ela é uma **pergunta**, não um pedido de rota.

    Os campos são os de `leis/gestao_da_coleta.py::CAMPOS_DA_NECESSIDADE`, que
    já tem dono. Escrever aqui um vocabulário novo criaria o segundo dono da
    mesma coisa.
    """
    REQUIREMENT_ID: str
    O_QUE: str
    JANELA: str
    FRESCURA_EXIGIDA: str
    GRAO: str
    PORQUE_IMPORTA: str
    POLICY_VERSION: str
    LEVANTADO_POR: str     # RUN_ID


#: O que a Intelligence **não pode** escrever num requisito. O GAP, a DECISÃO e
#: a ROTA são de `GESTAO_DA_COLETA/v1`. Um requisito que trouxesse qualquer
#: destes seria a Intelligence a decidir a coleta por dentro.
PALAVRAS_QUE_O_REQUISITO_RECUSA = (
    "GAP_ID", "SATISFACTION_STATE", "DECISION", "DECISION_ID",
    "ROTA", "ROUTE", "EXECUTOR", "COLETOR", "COLLECTOR", "SCRAPER",
    "API", "URL", "ENDPOINT", "PRIORITY",
)


# ═══════════════════════════════════════════════════════════════════════════
# 3 · O PACOTE DE DOMÍNIO — O QUE MUDA ENTRE DOMÍNIOS, E SÓ ISSO
# ═══════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class PacoteDeDominio:
    """Um domínio traz léxico, critérios e chaves. **Não traz máquina.**

    Se um domínio precisasse de um estado próprio, de um portão próprio ou de
    uma ordem própria, ele não seria um pacote: seria uma segunda arquitetura.
    O teste P11 existe exactamente para medir isso.
    """
    NOME: str
    ONTOLOGIA: Dict[str, Tuple[str, ...]]   # termo local -> códigos possíveis
    CRITERIOS_DE_RASTREIO: Tuple[str, ...]
    CRITERIOS_DUROS: Tuple[str, ...]
    CHAVES_DE_CRUZAMENTO: Tuple[str, ...]
    VALIDACAO_HUMANA_EXIGIDA: bool
    NIVEIS: Tuple[str, ...]
    #: A RÉGUA. Cada nível exige uma **espécie de evidência** que o anterior não
    #: exigia. É a única parte que muda entre domínios, e é DADO — se um domínio
    #: precisasse de um portão próprio, deixaria de ser um pacote.
    NIVEL_EXIGE: Dict[str, Tuple[str, ...]] = field(default_factory=dict)


DOMINIO_DOENCA = PacoteDeDominio(
    NOME="DOENCA",
    ONTOLOGIA={
        # 1:1 — verificado contra a EPPO Global Database
        "peronospora della vite": ("PLASVI",),
        "vite": ("VITVI",),
        # 1:N — e é **por isso** que existe o caso E do enunciado.
        # «Peronospora» sozinho é o nome comum de vários organismos.
        "peronospora": ("PLASVI", "PERO1", "BREMLA"),
        "cereali a paglia": ("TRZAX", "HORVX", "AVESA", "SECCE"),
    },
    CRITERIOS_DE_RASTREIO=("hospedeiro", "entrada", "estabelecimento",
                           "dispersao", "impacto"),
    CRITERIOS_DUROS=("hospedeiro",),
    CHAVES_DE_CRUZAMENTO=("SUJEITO", "AREA", "JANELA"),
    VALIDACAO_HUMANA_EXIGIDA=True,
    NIVEIS=("NIVEL_0", "NIVEL_1", "NIVEL_2", "NIVEL_3", "NIVEL_4"),
    NIVEL_EXIGE={
        "NIVEL_0": (),
        "NIVEL_1": ("OBSERVED_FIELD_SIGNAL",),
        "NIVEL_2": ("OBSERVED_FIELD_SIGNAL", "AGROCLIMATIC_SIGNAL"),
        "NIVEL_3": ("MODEL_OUTPUT",),
        "NIVEL_4": ("CONFIRMED_INCIDENCE",),
    },
)

DOMINIO_REGULATORIO = PacoteDeDominio(
    NOME="REGULATORIO",
    ONTOLOGIA={
        "protioconazolo": ("PROTHIOCONAZOLE",),
        "metiram": ("METIRAM",),
        "rame": ("COPPER_CU", "COPPER_HYDROXIDE", "COPPER_OXYCHLORIDE"),
    },
    CRITERIOS_DE_RASTREIO=("autoridade", "vigencia", "pais"),
    CRITERIOS_DUROS=("autoridade", "vigencia"),
    CHAVES_DE_CRUZAMENTO=("SUJEITO", "PAIS"),
    VALIDACAO_HUMANA_EXIGIDA=True,
    NIVEIS=("REGISTO", "USO_AUTORIZADO"),
    NIVEL_EXIGE={
        "REGISTO": ("REGULATORY_AUTHORIZATION",),
        # exige ainda a tupla de seis eixos (`PPP_USE`), que hoje não existe
        # como objeto — e por isso este nível está bloqueado na matéria-prima.
        "USO_AUTORIZADO": ("REGULATORY_AUTHORIZATION",),
    },
)

DOMINIOS = {d.NOME: d for d in (DOMINIO_DOENCA, DOMINIO_REGULATORIO)}


# ═══════════════════════════════════════════════════════════════════════════
# 4 · PRECISÃO — E A LEI QUE MANDA HERDAR O PIOR LADO
# ═══════════════════════════════════════════════════════════════════════════
ESCADA_GEO = ("PAIS", "REGIAO", "PROVINCIA", "MUNICIPIO", "PARCELA")
ESCADA_TEMPO = ("CAMPANHA", "MES", "SEMANA", "DIA")
ESCADA_SEMANTICA = ("GRUPO", "GENERO", "ESPECIE")


def _pior(a: str, b: str, escada: Sequence[str]) -> str:
    """O menos preciso dos dois. `NAO SEI` ganha a qualquer coisa — porque não
    saber é menos preciso do que qualquer precisão conhecida."""
    if a == NAO_SEI or b == NAO_SEI:
        return NAO_SEI
    if a not in escada or b not in escada:
        return NAO_SEI
    return a if escada.index(a) <= escada.index(b) else b


def e_falso(valor: Any) -> bool:
    """A única forma legítima de perguntar «isto é falso?».

        UNKNOWN != REJECTED != ERROR != NOT_RUN.   (INT-LAW-112)

    Um `if not valor:` trata `NAO SEI` como falso em silêncio, e é assim que a
    ignorância se transforma em ausência sem ninguém decidir nada.
    """
    if valor == NAO_SEI or valor is None:
        raise LeiViolada(
            "NAO SEI nao e FALSO. Nao se colapsa ignorancia em ausencia: "
            "declare NOT_FOUND_IN_SCANNED_UNIVERSE, ou meça."
        )
    return valor is False


# ═══════════════════════════════════════════════════════════════════════════
# 5 · A CORRIDA — INTELLIGENCE_RUN
# ═══════════════════════════════════════════════════════════════════════════
class Corrida:
    """Uma execução analítica identificada. Tudo o que ela produz aponta para
    ela, e ela preserva a configuração efetiva. (INT-LAW-051/052)"""

    def __init__(self, run_id: str, pergunta: str, dominio: str,
                 regras_versao: str = "v1",
                 contrato_de_entrada: str = "COL-LAW-043/12-campos") -> None:
        if dominio not in DOMINIOS:
            raise LeiViolada("dominio sem pacote declarado: %s" % dominio)
        self.RUN_ID = run_id
        self.PERGUNTA = pergunta
        self.DOMINIO = DOMINIOS[dominio]
        self.CONFIG = {
            "CONTRATO": CONTRATO,
            "RULESET_VERSION": regras_versao,
            "CONTRATO_DE_ENTRADA": contrato_de_entrada,
            "DOMINIO": dominio,
            "PERGUNTA": pergunta,
        }
        self.historia = Historia()
        self.sinais: Dict[str, Sinal] = {}
        self.cruzamentos: Dict[str, Cruzamento] = {}
        self.hipoteses: Dict[str, Hipotese] = {}
        self.achados: Dict[str, Achado] = {}
        self.requisitos: List[Requisito] = []
        self.selecao: List[str] = []      # EVIDENCE_SELECTION: só os ITEM_IDs
        self._n = 0

    # ── contadores de identidade, e nenhum deles é upstream ──────────────
    def _id(self, prefixo: str) -> str:
        self._n += 1
        return "%s-%s-%03d" % (prefixo, self.RUN_ID, self._n)

    # ── G0 · IDENTIDADE E ESPÉCIE ────────────────────────────────────────
    def g0_sinal(self, item: ItemPronto) -> Optional[Sinal]:
        """Item READY → SINAL, ou recusa com nome.

        Três portões duros, e nenhum deles é opinável:
            [1] a ESPECIE da evidência é conhecida (vem da fonte, não do texto)
            [2] FACT_TIME existe e é tempo do FACTO
            [3] a identidade do sujeito resolve, ou fica UNRESOLVED — e
                UNRESOLVED **não** é um empate desfeito à sorte.
        """
        self.selecao.append(item.ITEM_ID)

        if item.especie not in ESPECIES_DE_EVIDENCIA:
            self.historia.escrever(
                OBJETO=item.ITEM_ID, DE="READY", PARA="BLOQUEADO_EM_G0",
                PORTAO="G0", REGRA=self.CONFIG["RULESET_VERSION"],
                MOTIVO=("especie da evidencia ausente ou desconhecida: %r. "
                        "O contrato de entrada de hoje nao a transporta."
                        % item.especie),
                PROVENIENCIA=(item.ITEM_ID,))
            self.pedir_a_coleta(
                o_que="a especie da evidencia (%s) para o item %s"
                      % (" | ".join(ESPECIES_DE_EVIDENCIA), item.ITEM_ID),
                janela="a mesma do item",
                frescura="a mesma do item",
                grao="campo do contrato READY",
                porque=("sem especie, um boletim agroclimatico e um relato de "
                        "campo sao o mesmo texto — e " + AGROCLIMATIC_NAO_PROVA))
            return None

        if item.FACT_TIME == NAO_SEI:
            self.historia.escrever(
                OBJETO=item.ITEM_ID, DE="READY", PARA="BLOQUEADO_EM_G0",
                PORTAO="G0", REGRA=self.CONFIG["RULESET_VERSION"],
                MOTIVO="FACT_TIME = NAO SEI. PUBLICATION_TIME nao o substitui.",
                PROVENIENCIA=(item.ITEM_ID,))
            return None

        sujeito, match = self._resolver(item)
        sid = self._id("SIG")
        s = Sinal(
            SIGNAL_ID=sid, ITEM_ID=item.ITEM_ID, SOURCE_ID=item.SOURCE_ID,
            ESPECIE=item.especie, SUJEITO=sujeito, MATCH_TYPE=match,
            FACT_TIME=item.FACT_TIME, FACT_LOCATION=item.FACT_LOCATION,
            PRECISAO_GEO=_precisao_geo(item.FACT_LOCATION),
            PRECISAO_TEMPO=_precisao_tempo(item.FACT_TIME),
            PRECISAO_SEMANTICA=("ESPECIE" if match == "EXACT" else NAO_SEI),
            REGRA=self.CONFIG["RULESET_VERSION"])
        self.sinais[sid] = s
        self.historia.escrever(
            OBJETO=sid, DE="READY", PARA="SINAL", PORTAO="G0",
            REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="especie %s · identidade %s" % (item.especie, match),
            PROVENIENCIA=(item.ITEM_ID,))
        return s

    def _resolver(self, item: ItemPronto) -> Tuple[str, str]:
        """A ontologia responde, ou declara que não desfez o empate.

            SIMILARIDADE TEXTUAL NAO PROVA EQUIVALENCIA.  (INT-LAW-081)
        """
        termo = (item.sujeito_declarado or "").strip().lower()
        if not termo or termo == NAO_SEI.lower():
            return NAO_SEI, "ABSENT"
        candidatos = self.DOMINIO.ONTOLOGIA.get(termo)
        if not candidatos:
            return termo, "UNRESOLVED"
        if len(candidatos) == 1:
            return candidatos[0], "EXACT"
        # 1:N. O termo original PRESERVA-SE; não se escolhe o primeiro.
        return termo, "UNRESOLVED"

    # ── G1 · RASTREIO BARATO, FEITO PARA DESCARTAR ───────────────────────
    def g1_rastrear(self, sinal: Sinal, respostas: Dict[str, str]) -> Sinal:
        """Um rastreio que nunca descarta não é um rastreio.

        `NAO SEI` num critério **não** vira «médio». Fica NAO SEI, e um critério
        duro em NAO SEI não passa — porque passar seria transformar ignorância
        em aprovação.
        """
        sinal.RASTREIO = dict(respostas)
        duros = self.DOMINIO.CRITERIOS_DUROS
        reprovados = [c for c in duros
                      if respostas.get(c, NAO_SEI) in ("NAO", NAO_SEI)]
        if reprovados:
            sinal.ESTADO = "DESCARTADO"
            sinal.MOTIVO_DO_DESCARTE = (
                "criterio duro sem SIM: %s" % ", ".join(reprovados))
            self.historia.escrever(
                OBJETO=sinal.SIGNAL_ID, DE="SINAL", PARA="DESCARTADO",
                PORTAO="G1", REGRA=self.CONFIG["RULESET_VERSION"],
                MOTIVO=sinal.MOTIVO_DO_DESCARTE,
                PROVENIENCIA=tuple(sorted(respostas)))
            return sinal
        sinal.ESTADO = "RASTREADO"
        self.historia.escrever(
            OBJETO=sinal.SIGNAL_ID, DE="SINAL", PARA="RASTREADO", PORTAO="G1",
            REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="todos os criterios duros responderam SIM",
            PROVENIENCIA=tuple(sorted(respostas)))
        return sinal

    # ── G2 · CRUZAMENTO ──────────────────────────────────────────────────
    def g2_cruzar(self, sinais: Sequence[Sinal], pergunta: str) -> Cruzamento:
        """Coincidência estrutural com chave provada. Nada mais.

        O cruzamento **preserva** os sinais que o compõem (P3), herda o pior
        lado de cada eixo de precisão, e conta origens independentes em vez de
        contar evidências.
        """
        cid = self._id("CRX")
        ids = tuple(s.SIGNAL_ID for s in sinais)

        if any(s.MATCH_TYPE != "EXACT" for s in sinais):
            return self._cruzamento_recusado(
                cid, ids, pergunta,
                "identidade nao resolvida em pelo menos um lado: o cruzamento "
                "nao tem chave de juncao semantica")

        chaves = {s.SUJEITO for s in sinais}
        if len(chaves) != 1:
            return self._cruzamento_recusado(
                cid, ids, pergunta,
                "sujeitos diferentes: %s" % ", ".join(sorted(chaves)))

        areas = {_area(s.FACT_LOCATION) for s in sinais}
        if NAO_SEI in areas or len(areas) != 1:
            return self._cruzamento_recusado(
                cid, ids, pergunta,
                "sem area comum conferivel: %s" % ", ".join(sorted(areas)))

        janelas = {_janela(s.FACT_TIME) for s in sinais}
        if NAO_SEI in janelas or len(janelas) != 1:
            return self._cruzamento_recusado(
                cid, ids, pergunta,
                "sem janela temporal comum: %s" % ", ".join(sorted(janelas)))

        geo = tempo = sem = None
        for s in sinais:
            geo = s.PRECISAO_GEO if geo is None else _pior(geo, s.PRECISAO_GEO, ESCADA_GEO)
            tempo = s.PRECISAO_TEMPO if tempo is None else _pior(tempo, s.PRECISAO_TEMPO, ESCADA_TEMPO)
            sem = s.PRECISAO_SEMANTICA if sem is None else _pior(sem, s.PRECISAO_SEMANTICA, ESCADA_SEMANTICA)

        origens = {s.SOURCE_ID for s in sinais}
        c = Cruzamento(
            CROSSING_ID=cid, SINAIS=ids, PERGUNTA=pergunta,
            JOIN_KEY={"SUJEITO": chaves.pop(), "AREA": areas.pop(),
                      "JANELA": janelas.pop()},
            ESTADO="PROVADO", PRECISAO_GEO=geo, PRECISAO_TEMPO=tempo,
            PRECISAO_SEMANTICA=sem,
            ORIGENS_INDEPENDENTES=len(origens), ORIGENS_TOTAIS=len(ids))
        self.cruzamentos[cid] = c
        self.historia.escrever(
            OBJETO=cid, DE="SINAIS", PARA="PROVADO", PORTAO="G2",
            REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="chave de juncao completa; %d origens em %d evidencias"
                   % (len(origens), len(ids)),
            PROVENIENCIA=ids)
        return c

    def _cruzamento_recusado(self, cid, ids, pergunta, motivo) -> Cruzamento:
        c = Cruzamento(
            CROSSING_ID=cid, SINAIS=ids, PERGUNTA=pergunta, JOIN_KEY={},
            ESTADO="NOT_POSSIBLE", PRECISAO_GEO=NAO_SEI,
            PRECISAO_TEMPO=NAO_SEI, PRECISAO_SEMANTICA=NAO_SEI,
            ORIGENS_INDEPENDENTES=0, ORIGENS_TOTAIS=len(ids), MOTIVO=motivo)
        self.cruzamentos[cid] = c
        self.historia.escrever(
            OBJETO=cid, DE="SINAIS", PARA="NOT_POSSIBLE", PORTAO="G2",
            REGRA=self.CONFIG["RULESET_VERSION"], MOTIVO=motivo,
            PROVENIENCIA=ids)
        return c

    # ── G3 · HIPÓTESE (o candidate finding) ──────────────────────────────
    def g3_hipotese(self, apoia_se_em: Sequence[str], pergunta: str,
                    premissas: Sequence[str], o_que_a_derruba: str,
                    nivel: str) -> Hipotese:
        """A primeira vez que a Intelligence pode dizer «isto aponta para».

        Uma hipótese que nada derruba não é uma hipótese: é uma opinião com
        identificador.
        """
        if not o_que_a_derruba.strip():
            raise LeiViolada(
                "hipotese sem falsificador: escreva o que a derrubaria, ou nao "
                "a abra")
        if nivel not in self.DOMINIO.NIVEIS:
            raise LeiViolada("nivel fora da regua do dominio %s: %r"
                             % (self.DOMINIO.NOME, nivel))

        # A RÉGUA. Nenhum salto é grátis: nem por revisão humana, nem por mais
        # fontes do mesmo, nem por o texto parecer convincente.
        tem = self._especies_sob(apoia_se_em)
        faltam = [e for e in self.DOMINIO.NIVEL_EXIGE.get(nivel, ())
                  if e not in tem]
        if faltam:
            raise LeiViolada(
                "nivel %s exige %s e a evidencia so tem %s. %s"
                % (nivel, ", ".join(faltam),
                   ", ".join(sorted(tem)) or "nada",
                   AGROCLIMATIC_NAO_PROVA
                   if "AGROCLIMATIC_SIGNAL" in tem else
                   "Um nivel nao se alcanca por apresentacao."))
        hid = self._id("HIP")
        h = Hipotese(
            HYPOTHESIS_ID=hid, PERGUNTA=pergunta,
            APOIA_SE_EM=tuple(apoia_se_em), PREMISSAS=tuple(premissas),
            O_QUE_A_DERRUBA=o_que_a_derruba, NIVEL=nivel,
            VALIDACAO=("PENDENTE" if self.DOMINIO.VALIDACAO_HUMANA_EXIGIDA
                       else "NAO_EXIGIDA"))
        self.hipoteses[hid] = h
        self.historia.escrever(
            OBJETO=hid, DE="CRUZAMENTO", PARA="HIPOTESE", PORTAO="G3",
            REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="nivel %s · %d premissas · falsificavel" % (nivel, len(premissas)),
            PROVENIENCIA=tuple(apoia_se_em))
        return h

    def _especies_sob(self, apoios: Sequence[str]) -> set:
        """As espécies de evidência que sustentam estes apoios.

        Um cruzamento não tem espécie própria: ele tem as dos sinais que o
        compõem — e é por isso que o cruzamento **preserva** os sinais.
        """
        especies = set()
        for a in apoios:
            if a in self.sinais:
                especies.add(self.sinais[a].ESPECIE)
            elif a in self.cruzamentos:
                for sid in self.cruzamentos[a].SINAIS:
                    if sid in self.sinais:
                        especies.add(self.sinais[sid].ESPECIE)
            else:
                raise LeiViolada(
                    "apoio %r nao resolve nesta corrida: uma hipotese nao se "
                    "apoia em identificadores que ninguem consegue seguir" % a)
        return especies

    def julgar(self, h: Hipotese, tipo: str, evidencia: str,
               motivo: str) -> Aresta:
        """APOIA ou CONTRADIZ, com proveniência própria por decisão (P4).

        É aqui — e não no cruzamento — que a Intelligence julga.
        """
        if tipo not in ("APOIA", "CONTRADIZ"):
            raise LeiViolada("aresta de julgamento so pode APOIAR ou CONTRADIZER")
        if not motivo.strip():
            raise LeiViolada("julgamento sem motivo nao e auditavel")
        a = Aresta(TIPO=tipo, EVIDENCIA=evidencia,
                   REGRA=self.CONFIG["RULESET_VERSION"], MOTIVO=motivo)
        h.ARESTAS.append(a)
        self.historia.escrever(
            OBJETO=h.HYPOTHESIS_ID, DE=h.ESTADO, PARA=h.ESTADO,
            PORTAO="G3.JULGAMENTO", REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="%s: %s" % (tipo, motivo), PROVENIENCIA=(evidencia,))
        return a

    # ── A «FILA» DE VALIDAÇÃO, QUE É UMA PROJEÇÃO ────────────────────────
    def fila_de_validacao(self) -> List[Hipotese]:
        """Não há tabela, não há caixa de entrada, não há ferramenta.

        A fila é isto: uma leitura do estado que já vive no objeto. Se amanhã
        alguém a quiser ver noutra ordem, ordena a lista — não cria um store.
        """
        return [h for h in self.hipoteses.values()
                if h.VALIDACAO == "PENDENTE" and h.ESTADO == "HIPOTESE"]

    def validar(self, h: Hipotese, aprovada: bool, quem: str,
                motivo: str) -> Hipotese:
        h.VALIDACAO = "APROVADA" if aprovada else "RECUSADA"
        self.historia.escrever(
            OBJETO=h.HYPOTHESIS_ID, DE="HIPOTESE", PARA="HIPOTESE",
            PORTAO="G4.VALIDACAO", REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="%s por %s: %s" % (h.VALIDACAO, quem, motivo),
            PROVENIENCIA=(quem,))
        return h

    # ── G4 · PROMOÇÃO / REJEIÇÃO ─────────────────────────────────────────
    def g4_promover(self, h: Hipotese) -> Achado:
        """Hipótese → Achado. Três portões, e todos sabem recusar."""
        if self.DOMINIO.VALIDACAO_HUMANA_EXIGIDA and h.VALIDACAO != "APROVADA":
            raise LeiViolada(
                "este dominio exige validacao humana e ela esta %s. "
                "Promover aqui seria o carimbo a substituir a prova."
                % h.VALIDACAO)
        if h.NIVEL in (NAO_SEI, ""):
            raise LeiViolada("achado sem NIVEL declarado falsifica-se sozinho")
        if not h.APOIA_SE_EM:
            raise LeiViolada("achado sem evidencia de apoio")

        fid = self._id("ACH")
        traco = {
            "RUN_ID": self.RUN_ID,
            "PERGUNTA": h.PERGUNTA,
            "EVIDENCIAS": list(h.APOIA_SE_EM),
            "PREMISSAS": list(h.PREMISSAS),
            "O_QUE_A_DERRUBA": h.O_QUE_A_DERRUBA,
            "ARESTAS": [vars(a) for a in h.ARESTAS],
            "CONTRADITORIO": [vars(a) for a in h.contraditorio()],
            "REGRA": self.CONFIG["RULESET_VERSION"],
            "VALIDACAO": h.VALIDACAO,
            "CONFIG": dict(self.CONFIG),
        }
        a = Achado(FINDING_ID=fid, HYPOTHESIS_ID=h.HYPOTHESIS_ID,
                   PERGUNTA=h.PERGUNTA, NIVEL=h.NIVEL, ESTADO="CONFIRMADO",
                   TRACO_DE_DECISAO=traco)
        self.achados[fid] = a
        h.ESTADO = "PROMOVIDA"
        self.historia.escrever(
            OBJETO=fid, DE="HIPOTESE", PARA="CONFIRMADO", PORTAO="G4",
            REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="promovida com %d evidencias e %d contraditorios ligados"
                   % (len(h.APOIA_SE_EM), len(h.contraditorio())),
            PROVENIENCIA=(h.HYPOTHESIS_ID,))
        return a

    def g4_rejeitar(self, h: Hipotese, motivo: str) -> Hipotese:
        """Rejeitar é um destino, e não produz achado nenhum."""
        h.ESTADO = "REJEITADA"
        h.MOTIVO_DA_REJEICAO = motivo
        self.historia.escrever(
            OBJETO=h.HYPOTHESIS_ID, DE="HIPOTESE", PARA="REJEITADA",
            PORTAO="G4", REGRA=self.CONFIG["RULESET_VERSION"], MOTIVO=motivo)
        return h

    # ── REVERSÃO ─────────────────────────────────────────────────────────
    CAUSAS_DE_REVERSAO = {
        "RECORD_INVALIDATED": "REJEITADO",
        "NO_LONGER_PRESENT": "REBAIXADO",
        "NORMALIZATION_REVISED": "REABERTO",
        "SOURCE_RETRACTED": "REJEITADO",
        "DEPENDENCY_DISCOVERED": "REBAIXADO",
        "AUTHORIZATION_CHANGED": "SUBSTITUIDO",
        "WINDOW_CLOSED": "REBAIXADO",
    }

    def reverter(self, achado: Achado, causa: str, evidencia: str,
                 motivo: str) -> Achado:
        """O achado anda para trás, e o que ele foi continua legível.

            HISTORIA E APPEND-ONLY. UMA CORRECCAO QUE APAGA NAO E CORRECCAO.
        """
        if causa not in self.CAUSAS_DE_REVERSAO:
            raise LeiViolada("causa de reversao sem nome canonico: %r" % causa)
        anterior = achado.ESTADO
        achado.ESTADO = self.CAUSAS_DE_REVERSAO[causa]
        achado.ACTIVE = achado.ESTADO not in ("REJEITADO", "SUBSTITUIDO")
        self.historia.escrever(
            OBJETO=achado.FINDING_ID, DE=anterior, PARA=achado.ESTADO,
            PORTAO="DEMOTED_BY", REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO="%s: %s" % (causa, motivo), PROVENIENCIA=(evidencia,))
        return achado

    # ── OPORTUNIDADE — O LIMITE PÚBLICO → COMERCIAL ──────────────────────
    NIVEIS_DE_OPORTUNIDADE = {
        "A": "OPORTUNIDADE AGRONOMICA",
        "B": "OPORTUNIDADE DE PORTFOLIO REGISTADO",
        "C": "OPORTUNIDADE COMERCIAL",
        "D": "OPORTUNIDADE DE VENDA",
    }
    NIVEIS_QUE_EXIGEM_DADO_PRIVADO = ("C", "D")

    def oportunidade(self, achado: Achado, nivel: str,
                     fontes: Sequence[str],
                     contrato_de_dado_privado: str = "") -> Dict[str, Any]:
        """Dado público prova agronomia e regulação. Não prova venda.

        E o pior erro possível não é falhar o nível: é **não o declarar**.
        """
        if nivel not in self.NIVEIS_DE_OPORTUNIDADE:
            raise LeiViolada("nivel de oportunidade tem de ser A, B, C ou D")
        so_publico = all(f == "PUBLICO" for f in fontes)
        if nivel in self.NIVEIS_QUE_EXIGEM_DADO_PRIVADO:
            if so_publico or not contrato_de_dado_privado:
                raise LeiViolada(
                    "nivel %s (%s) exige dado interno com contrato. Dado "
                    "publico prova, no maximo, o nivel B."
                    % (nivel, self.NIVEIS_DE_OPORTUNIDADE[nivel]))
        return {
            "OPPORTUNITY_ID": self._id("OPP"),
            "FINDING_ID": achado.FINDING_ID,
            "NIVEL": nivel,
            "NIVEL_NOME": self.NIVEIS_DE_OPORTUNIDADE[nivel],
            "FONTES": list(fontes),
            "CLIENT_SAFE": False,
        }

    # ── O CAMINHO DE VOLTA, E É O ÚNICO ──────────────────────────────────
    def pedir_a_coleta(self, o_que: str, janela: str, frescura: str,
                       grao: str, porque: str) -> Requisito:
        """A Intelligence declara uma NECESSIDADE. Mais nada.

        O GAP, a DECISÃO e a ROTA são de `GESTAO_DA_COLETA/v1`. Esta função
        recusa-se a escrever qualquer palavra que pertença a esse dono — e
        recusa-se **em código**, para que a fronteira não dependa de boa vontade.
        """
        texto = " ".join((o_que, janela, frescura, grao, porque)).upper()
        for proibida in PALAVRAS_QUE_O_REQUISITO_RECUSA:
            if proibida in texto:
                raise LeiViolada(
                    "um requisito da Intelligence nao nomeia %r: o COMO e por "
                    "onde sao do orquestrador da Collection "
                    "(GESTAO_DA_COLETA/v1)." % proibida)
        r = Requisito(
            REQUIREMENT_ID=self._id("REQ"), O_QUE=o_que, JANELA=janela,
            FRESCURA_EXIGIDA=frescura, GRAO=grao, PORQUE_IMPORTA=porque,
            POLICY_VERSION=self.CONFIG["RULESET_VERSION"],
            LEVANTADO_POR=self.RUN_ID)
        self.requisitos.append(r)
        self.historia.escrever(
            OBJETO=r.REQUIREMENT_ID, DE="INTELLIGENCE", PARA="GESTOR_DA_COLETA",
            PORTAO="REQUISITO", REGRA=self.CONFIG["RULESET_VERSION"],
            MOTIVO=o_que, PROVENIENCIA=(self.RUN_ID,))
        return r


# ── auxiliares de precisão ──────────────────────────────────────────────────
def _precisao_geo(loc: str) -> str:
    if loc == NAO_SEI or not loc:
        return NAO_SEI
    n = len([p for p in loc.split("-") if p])
    return {1: "PAIS", 2: "REGIAO", 3: "PROVINCIA"}.get(n, "MUNICIPIO")


def _precisao_tempo(t: str) -> str:
    if t == NAO_SEI or not t:
        return NAO_SEI
    return {1: "CAMPANHA", 2: "MES", 3: "DIA"}.get(len(t.split("-")), NAO_SEI)


def _area(loc: str) -> str:
    """A área comparável é a REGIÃO — o degrau em que os boletins falam."""
    if loc == NAO_SEI or not loc:
        return NAO_SEI
    p = [x for x in loc.split("-") if x]
    return "-".join(p[:2]) if len(p) >= 2 else NAO_SEI


def _janela(t: str) -> str:
    """A janela comparável é o MÊS, e dizer isso é herdar o pior lado."""
    if t == NAO_SEI or not t:
        return NAO_SEI
    p = t.split("-")
    return "-".join(p[:2]) if len(p) >= 2 else NAO_SEI


# ═══════════════════════════════════════════════════════════════════════════
# 6 · DEMONSTRAÇÃO
# ═══════════════════════════════════════════════════════════════════════════
def _demonstracao() -> int:
    print("CONTRATO %s" % CONTRATO)
    print("dominios: %s" % ", ".join(sorted(DOMINIOS)))
    print()

    c = Corrida("DEMO", "ha peronospora relatada no Veneto em Maio?", "DOENCA")

    clima = ItemPronto(
        ITEM_ID="IT-CLIMA-1", UNIVERSO="T2", TEXTO="piogge e umidita elevate",
        SOURCE_ID="IT-T2-001", FACT_TIME="2026-05-02",
        FACT_LOCATION="IT-Veneto-Verona",
        especie="AGROCLIMATIC_SIGNAL",
        sujeito_declarado="peronospora della vite")
    campo = ItemPronto(
        ITEM_ID="IT-CAMPO-1", UNIVERSO="T3",
        TEXTO="sintomi di peronospora segnalati", SOURCE_ID="IT-T3-005",
        FACT_TIME="2026-05-04", FACT_LOCATION="IT-Veneto-Verona",
        especie="OBSERVED_FIELD_SIGNAL",
        sujeito_declarado="peronospora della vite")

    s1 = c.g0_sinal(clima)
    s2 = c.g0_sinal(campo)
    c.g1_rastrear(s1, {"hospedeiro": "SIM"})
    c.g1_rastrear(s2, {"hospedeiro": "SIM"})
    x = c.g2_cruzar([s1, s2], "o clima permitia quando o campo relatou?")
    print("cruzamento %s · %s · %d origens em %d evidencias"
          % (x.CROSSING_ID, x.ESTADO, x.ORIGENS_INDEPENDENTES, x.ORIGENS_TOTAIS))

    h = c.g3_hipotese(
        [x.CROSSING_ID], "ha pressao de peronospora em Verona em Maio?",
        ["a area do boletim e a area do relato"],
        "um boletim de sanidade que declare ausencia na mesma janela",
        "NIVEL_2")
    c.julgar(h, "APOIA", x.CROSSING_ID, "clima e relato compativeis no tempo e no lugar")
    print("fila de validacao: %d" % len(c.fila_de_validacao()))
    c.validar(h, True, "agronomo", "nivel 2 esta correctamente declarado")
    a = c.g4_promover(h)
    print("achado %s · %s · %s" % (a.FINDING_ID, a.NIVEL, a.ESTADO))

    c.reverter(a, "SOURCE_RETRACTED", "IT-T3-005",
               "o boletim foi corrigido: o sintoma era carencia nutricional")
    print("apos reversao: %s · estados na historia: %s"
          % (a.ESTADO, " -> ".join(c.historia.estados_de(a.FINDING_ID))))
    print("eventos na corrida: %d · requisitos levantados: %d"
          % (len(c.historia), len(c.requisitos)))
    print()
    print(json.dumps({"RUN_ID": c.RUN_ID, "CONFIG": c.CONFIG,
                      "EVIDENCE_SELECTION": c.selecao},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demonstracao())
