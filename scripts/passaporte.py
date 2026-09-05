#!/usr/bin/env python3
"""
PASSAPORTE DA INFORMAÇÃO — o dono canônico da identidade, do estado e do histórico.

O defeito que este arquivo fecha
---------------------------------
Até 2026-09-05 o acervo tinha 2.960 unidades de informação e nenhuma delas tinha
identidade própria. Um vídeo era "a linha 37 de ES-T8-001-videos.json". A transcrição do
mesmo vídeo era "a linha 4 de TRANSCRICOES-A.json", e as duas só se reconheciam por uma
URL. Quando a pergunta era "onde está esta informação agora?", a resposta exigia abrir
arquivo por arquivo.

O incidente que forçou este contrato: **1.005.157 caracteres de transcrição**
(705.149 em ES-T8-001 + 300.008 no SENSOR-PILOT) existiam no repositório, tinham sido
pagos, e **nenhum estado do sistema dizia que ninguém os tinha lido**. Não havia mentira
em lugar nenhum — havia ausência. E ausência de selo era indistinguível de reprovação.

    AUSÊNCIA DE PRÓXIMO SELO NUNCA SIGNIFICA REPROVAÇÃO.

As cinco leis deste arquivo
-----------------------------
1. **UM ITEM, UMA IDENTIDADE PERMANENTE.** `ITEM_ID` nasce na entrada e nunca muda —
   nem quando o item é normalizado, transcrito, cruzado ou consumido. Arquivo, caminho e
   URL são REFERÊNCIA, nunca identidade. Derivado ganha ID próprio e aponta para o pai.

2. **O HISTÓRICO É O DONO, O ESTADO É PROJEÇÃO.** `data/passaporte/EVENTOS.jsonl` é o
   único artefato canônico gravado. O passaporte de um item é o resultado de dobrar os
   eventos dele, em ordem. Não existe um segundo arquivo onde o mesmo estado possa
   envelhecer em silêncio — é a mesma disciplina de D-009 (número declarado tem de ser
   número derivado), aplicada a estado em vez de número.
   **Selo novo não apaga selo antigo:** o log é append-only e há portão que prova isso.

3. **PARAR EXIGE MOTIVO.** Nenhum item para em silêncio. Item que não avança carrega
   `REASON_CODE` e `NEXT_ACTION`. Um item parado sem motivo é `UNEXPLAINED_STAGE_DROP` e
   derruba o portão. Não é aviso: é falha.

4. **NÃO EXISTE "SERVE / NÃO SERVE" UNIVERSAL.** A primeira peneira pergunta apenas
   *"este material é tecnicamente utilizável?"* (`PASS`/`DEFER`/`REJECT`/`ERROR`). A
   pergunta *"para quais capacidades isto é relevante?"* é outra, é plural, e vive no
   roteamento. Um item pode alimentar SCIENCE e COMPETITOR e não ter nada a ver com
   OPPORTUNITY — e continuar valendo.

5. **FALHA FECHADA.** `admitir()` recusa item sem identidade, origem, coleção ou data de
   captura. Recusa é `REJECT_PIPELINE`, nunca `WARN_AND_CONTINUE`. Claim sem item, rota
   sem claim e consumo sem rota são recusados pela mesma porta.

O que este arquivo NÃO faz
----------------------------
Não lê conteúdo, não classifica, não interpreta e não decide relevância. Ele guarda
identidade, estado, histórico e motivo. Quem lê e quem classifica são outros processos —
e cada um deles precisa **selar** o que fez, aqui, para que o que fizeram exista.

    python3 scripts/passaporte.py            # resumo legível
    python3 scripts/passaporte.py --json     # máquina
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PASSAPORTE_DIR = os.path.join(ROOT, 'data', 'passaporte')
EVENTOS = os.path.join(PASSAPORTE_DIR, 'EVENTOS.jsonl')

# Versão da régua. Regra que muda ganha número novo; evento antigo mantém o número com que
# foi selado. Sem isso, mudar a régua reescreveria o passado em silêncio.
RULE_VERSION = 'PASSPORT-1.0'

UNKNOWN = 'UNKNOWN'
PENDING = 'PENDING'


class PassaporteRecusado(RuntimeError):
    """Porta fechada. Levantar isto é o comportamento correto, não uma falha do sistema."""


# ── 1 · IDENTIDADE ────────────────────────────────────────────────────────────────
#
# ITEM_ID é derivado do IDENTITY_BASIS, e o IDENTITY_BASIS é GLOBAL — não carrega coleção
# nem arquivo. Consequência deliberada: o mesmo vídeo recolhido por duas missões é UM item
# com dois eventos de captura, nunca dois itens. É assim que duplicata entre coleções deixa
# de ser invisível.
#
# O ID é opaco de propósito. Um ID legível vira caminho na cabeça de quem lê, e caminho não
# é identidade.

def item_id(identity_basis):
    if not identity_basis or not str(identity_basis).strip():
        raise PassaporteRecusado('IDENTITY_BASIS vazio — item sem identidade não entra')
    h = hashlib.sha1(str(identity_basis).encode('utf-8')).hexdigest()
    return 'ITEM-' + h[:16].upper()


def claim_id(item, ordinal):
    return 'CLAIM-%s-%02d' % (item.split('-', 1)[1], int(ordinal))


# ── 2 · VOCABULÁRIOS DE ESTADO ────────────────────────────────────────────────────
#
# Todo campo de estado tem vocabulário FECHADO. Valor fora do vocabulário é recusado na
# selagem — não é normalizado, não é aceito com aviso. A alternativa (aceitar string livre)
# produziria, em seis meses, quatro grafias para o mesmo estado e nenhuma contagem confiável.
#
# O default de cada campo está declarado ao lado, e ele carrega uma decisão:
# `CONTENT_READ_STATE` começa em NOT_READ, não em UNKNOWN. Num sistema onde LER É UM ATO QUE
# DEIXA SELO, a ausência do selo não é ignorância sobre o que aconteceu — é a informação de
# que não aconteceu. Foi exatamente isto que faltou nos 1.005.157 caracteres.

ESTADOS = {
    'RAW_STATE':           (('PRESERVED', 'NOT_PRESERVED', 'ERROR', UNKNOWN), UNKNOWN),
    'NORMALIZATION_STATE': (('NORMALIZED', PENDING, 'ERROR', UNKNOWN), PENDING),
    'DEDUP_STATE':         (('UNIQUE', 'DUPLICATE', PENDING, UNKNOWN), PENDING),
    'CONTENT_STATE':       (('AVAILABLE', 'REQUESTED_EMPTY', 'NOT_TESTED', 'ABSENT',
                             'ERROR', UNKNOWN), UNKNOWN),
    'CONTENT_READ_STATE':  (('READ', 'LEXICALLY_SCANNED', 'NOT_READ', UNKNOWN), 'NOT_READ'),
    'IDENTITY_STATE':      (('PROVED', 'PLAUSIBLE', 'NOT_PROVED', 'NOT_APPLICABLE',
                             UNKNOWN), UNKNOWN),
    'CLAIM_STATE':         (('EXTRACTED', 'NO_USABLE_CLAIM', 'NOT_APPLICABLE', PENDING,
                             UNKNOWN), PENDING),
    'GEOGRAPHY_STATE':     (('PROVED', 'NOT_KNOWN', 'NOT_APPLICABLE', UNKNOWN), UNKNOWN),
    'TIME_STATE':          (('PROVED', 'RELATIVE_ONLY', 'NOT_KNOWN', UNKNOWN), UNKNOWN),
    'CROP_STATE':          (('DECLARED', 'NOT_KNOWN', 'NOT_APPLICABLE', UNKNOWN), UNKNOWN),
    'ISSUE_STATE':         (('DECLARED', 'NOT_KNOWN', 'NOT_APPLICABLE', UNKNOWN), UNKNOWN),
    'LINEAGE_STATE':       (('ROOT', 'RESOLVED', 'BROKEN', UNKNOWN), UNKNOWN),
    'INTELLIGENCE_STATE':  (('PRODUCED', 'NOT_APPLICABLE', PENDING, UNKNOWN), PENDING),
    'ROUTING_STATE':       (('ROUTED', 'NOT_APPLICABLE', PENDING, UNKNOWN), PENDING),
    'CONSUMPTION_STATE':   (('CONSUMED', 'READY_NOT_CONSUMED', 'BLOCKED',
                             'ORPHAN_INTELLIGENCE', PENDING, UNKNOWN), PENDING),
}

CAMPOS_DE_ESTADO = tuple(ESTADOS)

# ── 3 · A ESCADA DE ESTÁGIOS ───────────────────────────────────────────────────────
#
# Oito estágios, em ordem. `CURRENT_STAGE` é o PRIMEIRO estágio que ainda não passou —
# derivado, nunca digitado. Um item só é contado na entrada de um estágio se passou por
# todos os anteriores; é isso que faz a contabilidade por estágio fechar de verdade em vez
# de somar o mesmo item em dois lugares.

ESTAGIOS = (
    'CAPTURE',
    'NORMALIZATION',
    'DEDUP',
    'CONTENT_ACQUISITION',
    'INTELLIGENCE_READING',
    'CLAIM_EXTRACTION',
    'ROUTING',
    'CONSUMPTION',
)

# Motivos. Todo motivo tem NEXT_ACTION — um motivo sem próxima ação é uma desculpa.
MOTIVOS = {
    'DUPLICATE':              'nenhuma — o item canônico já existe e carrega o histórico',
    'CONTENT_NOT_AVAILABLE':  'reexecutar a rota de conteúdo, ou declarar a rota fechada',
    'TRANSCRIPT_PENDING':     'pedir a transcrição; nunca concluir sem pedir',
    'CONTENT_NOT_PROCESSED':  'ler o conteúdo e selar CONTENT_READ com evidência',
    'IDENTITY_UNRESOLVED':    'cruzar camadas para provar a origem; nunca ler o texto com mais boa vontade',
    'GEOGRAPHY_UNRESOLVED':   'procurar lugar NOMEADO no conteúdo; idioma não é país',
    'NO_USABLE_CLAIM':        'nenhuma — lido e sem afirmação utilizável é resultado válido',
    'FALSE_POSITIVE':         'nenhuma — o termo casou e o assunto não',
    'OUTSIDE_SCOPE':          'nenhuma — fora do recorte declarado da coleção',
    'WAITING_INTELLIGENCE':   'extrair claim antes de rotear',
    'READY_NOT_CONSUMED':     'apresentar a inteligência à capacidade roteada, ou declarar por que ela não serve',
    'CAPTURE_ERROR':          'reexecutar a captura; item em ERROR nunca conta como reprovado',
    'NORMALIZATION_PENDING':  'normalizar o bruto, ou declarar que esta fonte não tem projeção normalizada',
    'NOT_ROUTED':             'rotear o claim para as capacidades em que ele é relevante',
}

# ── 4 · CAPACIDADES ────────────────────────────────────────────────────────────────
#
# Dezesseis. Não existe destino único, e OPPORTUNITY é UMA delas — nunca o funil.
# Um item pode ser DIRECT em SCIENCE, SUPPORTING em COMPETITOR e NOT_APPLICABLE em
# OPPORTUNITY ao mesmo tempo, e isso é um resultado saudável, não uma reprovação.

CAPACIDADES = (
    'OPPORTUNITY', 'EARLY_SIGNAL', 'PHYTOSANITARY', 'WINDOWS', 'REGULATORY', 'PORTFOLIO',
    'COMPETITOR', 'SCIENCE', 'HUMAN_SENSORS', 'MARKET_DEVELOPMENT', 'COMMERCIAL',
    'MARKETING', 'SUPPLY', 'COUNTRY_CROP_PULSE', 'FUTURE_PLANNING', 'ASK_SINTONIA',
)

RELEVANCIA = ('DIRECT', 'SUPPORTING', 'CONTEXT', 'BLOCKED', 'NOT_APPLICABLE')
RELEVANTES = ('DIRECT', 'SUPPORTING', 'CONTEXT')
CONSUMO = ('CONSUMED', 'READY_NOT_CONSUMED', 'BLOCKED')

# ── 5 · EVENTOS ────────────────────────────────────────────────────────────────────
#
# Cada tipo de evento declara QUAL campo de estado ele tem direito de escrever. Um evento
# não pode escrever um campo que não é dele — é o que impede que "roteado" comece a mexer
# em "lido" porque foi conveniente num sábado.

ESCRITA = {
    'ITEM_CAPTURED':          'RAW_STATE',
    'CAPTURE_FAILED':         'RAW_STATE',
    'NORMALIZED':             'NORMALIZATION_STATE',
    'DEDUP_RESOLVED':         'DEDUP_STATE',
    'CONTENT_AVAILABLE':      'CONTENT_STATE',
    'TRANSCRIPT_AVAILABLE':   'CONTENT_STATE',
    'CONTENT_UNAVAILABLE':    'CONTENT_STATE',
    'CONTENT_SCANNED':        'CONTENT_READ_STATE',
    'CONTENT_READ':           'CONTENT_READ_STATE',
    'TRANSCRIPT_READ':        'CONTENT_READ_STATE',
    'IDENTITY_PROVED':        'IDENTITY_STATE',
    'IDENTITY_NOT_PROVED':    'IDENTITY_STATE',
    'GEOGRAPHY_PROVED':       'GEOGRAPHY_STATE',
    'GEOGRAPHY_NOT_PROVED':   'GEOGRAPHY_STATE',
    'TIME_RESOLVED':          'TIME_STATE',
    'CROP_DECLARED':          'CROP_STATE',
    'ISSUE_DECLARED':         'ISSUE_STATE',
    'LINEAGE_RESOLVED':       'LINEAGE_STATE',
    'CLAIMS_EXTRACTED':       'CLAIM_STATE',
    'NO_USABLE_CLAIM':        'CLAIM_STATE',
    'INTELLIGENCE_PRODUCED':  'INTELLIGENCE_STATE',
    'ROUTED_TO_CAPABILITY':   'ROUTING_STATE',
    'CONSUMED_BY_CAPABILITY': 'CONSUMPTION_STATE',
    'CONSUMPTION_BLOCKED':    'CONSUMPTION_STATE',
    # STOPPED_WITH_REASON não escreve estado: ele DECLARA por que o estado não avançou.
    'STOPPED_WITH_REASON':    None,
}

CAMPOS_EVENTO = ('EVENT_ID', 'ITEM_ID', 'EVENT_TYPE', 'TIMESTAMP', 'ACTOR', 'RULE_VERSION',
                 'FROM_STATE', 'TO_STATE', 'REASON', 'EVIDENCE_REFERENCE')


class Registro:
    """O acervo de passaportes. Um `Registro` é uma lista de eventos e nada mais.

    Tudo o que se pergunta a ele é DERIVADO dessa lista no momento da pergunta. Ele aceita
    um caminho de log (o canônico, por padrão) ou nenhum — e aí vive em memória, que é como
    os testes e as sondas de contrato o exercem sem tocar no acervo real.
    """

    def __init__(self, eventos=None, caminho=EVENTOS):
        self.caminho = caminho
        self.eventos = list(eventos or [])
        # Contador de selos por item. Ele existe por uma razão só: `EVENT_ID` é derivado
        # da posição do evento no histórico DAQUELE item, e recontar o log inteiro a cada
        # selagem transformaria 33.886 eventos em 1,1 bilhão de comparações.
        self._seq = {}
        for e in self.eventos:
            self._seq[e['ITEM_ID']] = self._seq.get(e['ITEM_ID'], 0) + 1

    # ---- leitura e escrita do log ------------------------------------------------
    @classmethod
    def carregar(cls, caminho=EVENTOS):
        ev = []
        if os.path.exists(caminho):
            with open(caminho, encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        ev.append(json.loads(linha))
        return cls(ev, caminho)

    def gravar(self):
        """Reescreve o log a partir da lista em memória.

        Só existe para o backfill, que constrói o log inteiro de uma vez. O caminho normal
        de operação é `append()`, que nunca reabre o passado.
        """
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        tmp = self.caminho + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for e in self.eventos:
                f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + '\n')
        os.replace(tmp, self.caminho)

    def append(self, evento):
        os.makedirs(os.path.dirname(self.caminho), exist_ok=True)
        with open(self.caminho, 'a', encoding='utf-8') as f:
            f.write(json.dumps(evento, ensure_ascii=False, sort_keys=True) + '\n')

    # ---- porta de entrada --------------------------------------------------------
    def admitir(self, *, identity_basis, collection_id, source_id, source_family,
                source_reference, captured_at, content_type, item_class='CONTENT',
                actor, parent_item_id=None, derived_from=None, evidence_reference=None,
                raw_state='PRESERVED', timestamp=None):
        """A ÚNICA porta pela qual informação entra no Sintonia.

        Recusa — `REJECT_PIPELINE`, não `WARN_AND_CONTINUE` — quando falta identidade,
        coleção, origem, data de captura ou tipo. Derivado sem pai é recusado pela mesma
        porta: é o que impede transcrição órfã, que foi metade do incidente.
        """
        faltando = [n for n, v in (
            ('IDENTITY_BASIS', identity_basis), ('COLLECTION_ID', collection_id),
            ('SOURCE_ID', source_id), ('SOURCE_FAMILY', source_family),
            ('SOURCE_REFERENCE', source_reference), ('CAPTURED_AT', captured_at),
            ('CONTENT_TYPE', content_type), ('ACTOR', actor),
        ) if not v]
        if faltando:
            raise PassaporteRecusado(
                'REJECT_PIPELINE — campo obrigatório ausente: %s' % ', '.join(faltando))
        if derived_from and not parent_item_id:
            raise PassaporteRecusado(
                'REJECT_PIPELINE — derivado declara DERIVED_FROM=%s sem PARENT_ITEM_ID'
                % derived_from)
        if parent_item_id and not derived_from:
            raise PassaporteRecusado(
                'REJECT_PIPELINE — derivado tem pai e não declara DERIVED_FROM')
        iid = item_id(identity_basis)
        ev = self._evento(
            iid, 'ITEM_CAPTURED', timestamp or captured_at, actor,
            from_state=None, to_state=raw_state,
            reason='entrada no Sintonia', evidence_reference=evidence_reference,
            extra={'IDENTITY_BASIS': str(identity_basis), 'COLLECTION_ID': collection_id,
                   'SOURCE_ID': source_id, 'SOURCE_FAMILY': source_family,
                   'SOURCE_REFERENCE': str(source_reference), 'CAPTURED_AT': captured_at,
                   'CONTENT_TYPE': content_type, 'ITEM_CLASS': item_class,
                   'PARENT_ITEM_ID': parent_item_id, 'DERIVED_FROM': derived_from})
        self.eventos.append(ev)
        return iid

    def selar(self, item, event_type, *, to_state=None, actor, timestamp,
              reason=None, evidence_reference=None, from_state=None, extra=None):
        """Acrescenta um selo. Nunca apaga, nunca reescreve, nunca reordena."""
        if event_type not in ESCRITA:
            raise PassaporteRecusado('EVENT_TYPE desconhecido: %s' % event_type)
        campo = ESCRITA[event_type]
        if campo:
            permitido = ESTADOS[campo][0]
            if to_state not in permitido:
                raise PassaporteRecusado(
                    '%s escreve %s e %r não está no vocabulário %s'
                    % (event_type, campo, to_state, permitido))
        elif event_type == 'STOPPED_WITH_REASON' and reason not in MOTIVOS:
            raise PassaporteRecusado(
                'STOPPED_WITH_REASON exige REASON_CODE declarado; %r não é' % reason)
        ev = self._evento(item, event_type, timestamp, actor, from_state, to_state,
                          reason, evidence_reference, extra)
        self.eventos.append(ev)
        return ev

    def _evento(self, item, tipo, timestamp, actor, from_state, to_state, reason,
                evidence_reference, extra=None):
        if not timestamp:
            raise PassaporteRecusado('evento sem TIMESTAMP — tempo é medido, não inferido')
        if not actor:
            raise PassaporteRecusado('evento sem ACTOR — toda selagem tem dono')
        seq = self._seq.get(item, 0)
        self._seq[item] = seq + 1
        semente = '%s|%d|%s|%s|%s' % (item, seq, tipo, timestamp, to_state)
        ev = {
            'EVENT_ID': 'EVT-' + hashlib.sha1(semente.encode('utf-8')).hexdigest()[:16].upper(),
            'ITEM_ID': item,
            'EVENT_TYPE': tipo,
            'TIMESTAMP': timestamp,
            'ACTOR': actor,
            'RULE_VERSION': RULE_VERSION,
            'FROM_STATE': from_state,
            'TO_STATE': to_state,
            'REASON': reason,
            'EVIDENCE_REFERENCE': evidence_reference,
        }
        for k, v in (extra or {}).items():
            if v is not None:
                ev[k] = v
        return ev

    # ---- claims, rotas e consumo -------------------------------------------------
    def extrair_claims(self, item, claims, *, actor, timestamp, evidence_reference):
        """Registra claims de um item. Claim sem item não existe — não há como criar um."""
        if item not in self.itens():
            raise PassaporteRecusado('REJECT_PIPELINE — claim sem ITEM_ID rastreável')
        if not claims:
            raise PassaporteRecusado('extrair_claims sem claim; use selar(NO_USABLE_CLAIM)')
        ids = []
        for i, texto in enumerate(claims, 1):
            cid = claim_id(item, i)
            ids.append(cid)
            self.selar(item, 'CLAIMS_EXTRACTED', to_state='EXTRACTED', actor=actor,
                       timestamp=timestamp, reason=texto,
                       evidence_reference=evidence_reference, extra={'CLAIM_ID': cid})
        return ids

    def rotear(self, item, cid, capability, relevance, *, actor, timestamp, why,
               blocker=None):
        if capability not in CAPACIDADES:
            raise PassaporteRecusado('capacidade desconhecida: %s' % capability)
        if relevance not in RELEVANCIA:
            raise PassaporteRecusado('relevância fora do vocabulário: %s' % relevance)
        if cid not in self.claims_de(item):
            raise PassaporteRecusado('REJECT_PIPELINE — rota sem CLAIM_ID existente')
        if not why:
            raise PassaporteRecusado('rota sem WHY — roteamento sem motivo não é roteamento')
        return self.selar(item, 'ROUTED_TO_CAPABILITY', to_state='ROUTED', actor=actor,
                          timestamp=timestamp, reason=why,
                          evidence_reference=None,
                          extra={'CLAIM_ID': cid, 'CAPABILITY_ID': capability,
                                 'RELEVANCE': relevance, 'BLOCKER': blocker})

    def consumir(self, item, cid, capability, *, actor, timestamp, evidence_reference):
        """Consumo EXIGE prova. Aparecer numa pasta de inteligência não é consumo."""
        rotas = self.rotas_de(item)
        if (cid, capability) not in rotas:
            raise PassaporteRecusado('REJECT_PIPELINE — consumo sem rota declarada')
        if rotas[(cid, capability)]['RELEVANCE'] not in RELEVANTES:
            raise PassaporteRecusado('consumo de rota %s não é consumo'
                                     % rotas[(cid, capability)]['RELEVANCE'])
        if not evidence_reference:
            raise PassaporteRecusado('REJECT_PIPELINE — consumo sem EVIDENCE_REFERENCE')
        return self.selar(item, 'CONSUMED_BY_CAPABILITY', to_state='CONSUMED', actor=actor,
                          timestamp=timestamp, reason='consumido com prova',
                          evidence_reference=evidence_reference,
                          extra={'CLAIM_ID': cid, 'CAPABILITY_ID': capability})

    # ---- projeções ----------------------------------------------------------------
    def itens(self):
        return {e['ITEM_ID'] for e in self.eventos if e['EVENT_TYPE'] == 'ITEM_CAPTURED'}

    def eventos_de(self, item):
        return [e for e in self.eventos if e['ITEM_ID'] == item]

    def claims_de(self, item):
        return {e['CLAIM_ID']: e for e in self.eventos_de(item)
                if e['EVENT_TYPE'] == 'CLAIMS_EXTRACTED'}

    def rotas_de(self, item):
        r = {}
        for e in self.eventos_de(item):
            if e['EVENT_TYPE'] == 'ROUTED_TO_CAPABILITY':
                r[(e['CLAIM_ID'], e['CAPABILITY_ID'])] = {
                    'CLAIM_ID': e['CLAIM_ID'], 'CAPABILITY_ID': e['CAPABILITY_ID'],
                    'RELEVANCE': e['RELEVANCE'], 'WHY': e['REASON'],
                    'BLOCKER': e.get('BLOCKER'), 'STATE': 'READY_NOT_CONSUMED',
                }
        for e in self.eventos_de(item):
            k = (e.get('CLAIM_ID'), e.get('CAPABILITY_ID'))
            if e['EVENT_TYPE'] == 'CONSUMED_BY_CAPABILITY' and k in r:
                r[k]['STATE'] = 'CONSUMED'
                r[k]['EVIDENCE'] = e['EVIDENCE_REFERENCE']
            elif e['EVENT_TYPE'] == 'CONSUMPTION_BLOCKED' and k in r:
                r[k]['STATE'] = 'BLOCKED'
        for k, rota in r.items():
            if rota['RELEVANCE'] not in RELEVANTES and rota['STATE'] == 'READY_NOT_CONSUMED':
                rota['STATE'] = 'BLOCKED' if rota['RELEVANCE'] == 'BLOCKED' else 'NOT_APPLICABLE'
        return r

    def _claims_e_rotas(self):
        """Uma passagem só pelo log. A versão por item era O(n²) e levava 26 segundos
        num acervo de 33.886 eventos — a mesma resposta, em menos de um."""
        claims, rotas = {}, {}
        for e in self.eventos:
            iid, tipo = e['ITEM_ID'], e['EVENT_TYPE']
            if tipo == 'CLAIMS_EXTRACTED':
                claims.setdefault(iid, {})[e['CLAIM_ID']] = e
            elif tipo == 'ROUTED_TO_CAPABILITY':
                rotas.setdefault(iid, {})[(e['CLAIM_ID'], e['CAPABILITY_ID'])] = {
                    'CLAIM_ID': e['CLAIM_ID'], 'CAPABILITY_ID': e['CAPABILITY_ID'],
                    'RELEVANCE': e['RELEVANCE'], 'WHY': e['REASON'],
                    'BLOCKER': e.get('BLOCKER'), 'STATE': 'READY_NOT_CONSUMED',
                }
            elif tipo in ('CONSUMED_BY_CAPABILITY', 'CONSUMPTION_BLOCKED'):
                k = (e.get('CLAIM_ID'), e.get('CAPABILITY_ID'))
                rota = rotas.get(iid, {}).get(k)
                if rota:
                    rota['STATE'] = ('CONSUMED' if tipo == 'CONSUMED_BY_CAPABILITY'
                                     else 'BLOCKED')
                    if tipo == 'CONSUMED_BY_CAPABILITY':
                        rota['EVIDENCE'] = e['EVIDENCE_REFERENCE']
        for porrota in rotas.values():
            for rota in porrota.values():
                if (rota['RELEVANCE'] not in RELEVANTES
                        and rota['STATE'] == 'READY_NOT_CONSUMED'):
                    rota['STATE'] = ('BLOCKED' if rota['RELEVANCE'] == 'BLOCKED'
                                     else 'NOT_APPLICABLE')
        return claims, rotas

    def passaporte(self, item):
        return self.passaportes()[item]

    def passaportes(self):
        """Dobra o log inteiro. É a única fonte de estado que este sistema tem."""
        p = {}
        for e in self.eventos:
            iid = e['ITEM_ID']
            if e['EVENT_TYPE'] == 'ITEM_CAPTURED':
                base = {c: ESTADOS[c][1] for c in CAMPOS_DE_ESTADO}
                base.update({
                    'ITEM_ID': iid,
                    'IDENTITY_BASIS': e['IDENTITY_BASIS'],
                    'COLLECTION_ID': e['COLLECTION_ID'],
                    'SOURCE_ID': e['SOURCE_ID'],
                    'SOURCE_FAMILY': e['SOURCE_FAMILY'],
                    'SOURCE_REFERENCE': e['SOURCE_REFERENCE'],
                    'CAPTURED_AT': e['CAPTURED_AT'],
                    'CONTENT_TYPE': e['CONTENT_TYPE'],
                    'ITEM_CLASS': e.get('ITEM_CLASS', 'CONTENT'),
                    'PARENT_ITEM_ID': e.get('PARENT_ITEM_ID'),
                    'DERIVED_FROM': e.get('DERIVED_FROM'),
                    'RECOLLECTED': 0,
                    'DECLARED_STOP': None,
                    'CONTENT_CHARS': None,
                })
                if iid in p:
                    # Reencontro: o item já entrou antes. NÃO nasce item novo — o histórico
                    # ganha um selo e o contador de recoletas sobe. Duplicata entre coleções
                    # passa a ser visível em vez de virar dois itens.
                    p[iid]['RECOLLECTED'] += 1
                    continue
                base['RAW_STATE'] = e['TO_STATE'] or UNKNOWN
                p[iid] = base
                continue
            if iid not in p:
                # Selo sobre item que nunca entrou: o log está corrompido. Não se inventa
                # um passaporte para acomodá-lo.
                raise PassaporteRecusado('evento %s sobre item sem ITEM_CAPTURED: %s'
                                         % (e['EVENT_ID'], iid))
            campo = ESCRITA[e['EVENT_TYPE']]
            if campo and e['TO_STATE']:
                p[iid][campo] = e['TO_STATE']
            if e.get('CONTENT_CHARS') is not None:
                # O tamanho do conteúdo é PROJETADO, não recontado: é o número que o selo
                # de disponibilidade mediu. É por ele que o portão prova que nenhum
                # caractere de transcrição ficou fora de um passaporte.
                p[iid]['CONTENT_CHARS'] = e['CONTENT_CHARS']
            if e['EVENT_TYPE'] == 'STOPPED_WITH_REASON':
                # Parada DECLARADA — a que a máquina não deriva sozinha. FALSE_POSITIVE e
                # OUTSIDE_SCOPE são julgamento, não estado técnico: só existem se alguém
                # os selar, e o selo diz quem e com que evidência.
                p[iid]['DECLARED_STOP'] = e['REASON']

        claims, rotas = self._claims_e_rotas()
        for iid, item in p.items():
            item['CLAIMS'] = sorted(claims.get(iid, {}))
            r = rotas.get(iid, {})
            item['ROUTES'] = [r[k] for k in sorted(r)]
            # CONSUMPTION_STATE de um item é a soma do consumo das rotas dele. Item roteado
            # e não consumido NÃO fica PENDING: fica READY_NOT_CONSUMED, com nome, porque é
            # exatamente essa a dívida que precisa aparecer.
            consumo = _consumo_do_item(item)
            if consumo and item['CONSUMPTION_STATE'] == PENDING:
                item['CONSUMPTION_STATE'] = consumo
            item.update(_derivar(item))
        return p


# ── 6 · A MÁQUINA DE ESTADOS ───────────────────────────────────────────────────────
#
# Cada estágio devolve (VEREDITO, MOTIVO). Quatro veredictos e nada mais:
#
#   PASSED · STOPPED_WITH_REASON · PENDING · ERROR
#
# STOPPED e PENDING SEMPRE devolvem motivo. Um estágio que devolvesse STOPPED com motivo
# None seria exatamente o defeito que este contrato existe para tornar impossível — e por
# isso `contabilidade()` conta esse caso como UNEXPLAINED_STAGE_DROP e reprova o portão.

def _estagio(item, nome):
    if nome == 'CAPTURE':
        if item['RAW_STATE'] == 'ERROR':
            return 'ERROR', 'CAPTURE_ERROR'
        if item['RAW_STATE'] in ('PRESERVED', 'NOT_PRESERVED'):
            return 'PASSED', None
        return 'PENDING', 'CAPTURE_ERROR'

    if nome == 'NORMALIZATION':
        if item['NORMALIZATION_STATE'] == 'NORMALIZED':
            return 'PASSED', None
        if item['NORMALIZATION_STATE'] == 'ERROR':
            return 'ERROR', 'CAPTURE_ERROR'
        return 'PENDING', 'NORMALIZATION_PENDING'

    if nome == 'DEDUP':
        if item['DEDUP_STATE'] == 'UNIQUE':
            return 'PASSED', None
        if item['DEDUP_STATE'] == 'DUPLICATE':
            return 'STOPPED_WITH_REASON', 'DUPLICATE'
        return 'PENDING', 'NORMALIZATION_PENDING'

    if nome == 'CONTENT_ACQUISITION':
        if item['CONTENT_STATE'] == 'AVAILABLE':
            return 'PASSED', None
        if item['CONTENT_STATE'] == 'ERROR':
            return 'ERROR', 'CAPTURE_ERROR'
        if item['CONTENT_STATE'] == 'REQUESTED_EMPTY':
            return 'STOPPED_WITH_REASON', 'CONTENT_NOT_AVAILABLE'
        if item['CONTENT_STATE'] == 'ABSENT':
            return 'STOPPED_WITH_REASON', 'CONTENT_NOT_AVAILABLE'
        # NOT_TESTED é o estado mais caro do acervo: ninguém sequer PERGUNTOU se havia
        # conteúdo. Ele não é reprovação e nunca vira uma.
        return 'PENDING', 'TRANSCRIPT_PENDING'

    if nome == 'INTELLIGENCE_READING':
        if item['CONTENT_READ_STATE'] == 'READ':
            return 'PASSED', None
        # LEXICALLY_SCANNED é o selo que impede a mentira mais confortável do acervo:
        # existir classificador que tocou o texto NÃO é o texto ter sido lido.
        return 'PENDING', 'CONTENT_NOT_PROCESSED'

    if nome == 'CLAIM_EXTRACTION':
        if item['CLAIM_STATE'] == 'EXTRACTED':
            return 'PASSED', None
        if item['CLAIM_STATE'] == 'NO_USABLE_CLAIM':
            return 'STOPPED_WITH_REASON', 'NO_USABLE_CLAIM'
        if item['CLAIM_STATE'] == 'NOT_APPLICABLE':
            return 'STOPPED_WITH_REASON', 'OUTSIDE_SCOPE'
        return 'PENDING', 'WAITING_INTELLIGENCE'

    if nome == 'ROUTING':
        if item['ROUTING_STATE'] == 'ROUTED':
            return 'PASSED', None
        return 'PENDING', 'NOT_ROUTED'

    if nome == 'CONSUMPTION':
        if item['CONSUMPTION_STATE'] == 'CONSUMED':
            return 'PASSED', None
        if item['CONSUMPTION_STATE'] == 'BLOCKED':
            return 'STOPPED_WITH_REASON', 'READY_NOT_CONSUMED'
        return 'PENDING', 'READY_NOT_CONSUMED'
    # ORPHAN_INTELLIGENCE nunca chega aqui: um item sem rota para em ROUTING, com
    # NOT_ROUTED. Ele fica ACTIVE e visível — nunca concluído, nunca reprovado.

    raise PassaporteRecusado('estágio desconhecido: %s' % nome)


def veredictos(item):
    """Veredicto por estágio, parando de contar no primeiro que não passou."""
    out, alcancou = {}, True
    for nome in ESTAGIOS:
        if not alcancou:
            out[nome] = (None, None)
            continue
        v, motivo = _estagio(item, nome)
        out[nome] = (v, motivo)
        if v != 'PASSED':
            alcancou = False
    return out


def _derivar(item):
    """CURRENT_STAGE, TRIAGE, LIFECYCLE, BLOCKER_CODES — todos derivados, nenhum digitado."""
    v = veredictos(item)
    atual = ESTAGIOS[-1]
    veredicto, motivo = 'PASSED', None
    for nome in ESTAGIOS:
        ver, mot = v[nome]
        if ver != 'PASSED':
            atual, veredicto, motivo = nome, ver, mot
            break
    else:
        atual, veredicto, motivo = ESTAGIOS[-1], 'PASSED', None

    concluido = veredicto == 'PASSED' and v[ESTAGIOS[-1]][0] == 'PASSED'

    # BLOCKER_CODES não é só o motivo do estágio atual. Identidade e geografia não
    # bloqueiam a escada, mas bloqueiam a inteligência — e some do radar quem não as vê.
    blockers = []
    if motivo:
        blockers.append(motivo)
    if item['IDENTITY_STATE'] in ('NOT_PROVED', UNKNOWN):
        blockers.append('IDENTITY_UNRESOLVED')
    if item['GEOGRAPHY_STATE'] in ('NOT_KNOWN', UNKNOWN):
        blockers.append('GEOGRAPHY_UNRESOLVED')

    declarado = item.get('DECLARED_STOP')
    if declarado in ('FALSE_POSITIVE', 'OUTSIDE_SCOPE'):
        # Parada declarada vence a derivada: alguém olhou e disse por quê. O item não
        # desaparece — ele fica REJECTED com nome e com autor no histórico.
        motivo = declarado
        blockers = sorted(set(blockers + [declarado]))

    if veredicto == 'ERROR':
        triage, lifecycle = 'ERROR', 'ERROR'
    elif motivo == 'DUPLICATE':
        triage, lifecycle = 'REJECT', 'REJECTED'
    elif motivo in ('FALSE_POSITIVE', 'OUTSIDE_SCOPE'):
        triage, lifecycle = 'REJECT', 'REJECTED'
    elif motivo in ('CONTENT_NOT_AVAILABLE', 'TRANSCRIPT_PENDING'):
        # DEFER é "não utilizável AINDA". Não é reprovação e não fecha o item.
        triage, lifecycle = 'DEFER', 'DEFERRED'
    elif concluido:
        triage, lifecycle = 'PASS', 'COMPLETED'
    else:
        triage, lifecycle = 'PASS', 'ACTIVE'

    return {
        'CURRENT_STAGE': atual,
        'STAGE_VERDICT': veredicto,
        'NEXT_REQUIRED_STAGE': None if concluido else atual,
        'BLOCKER_CODES': sorted(set(blockers)),
        'TRIAGE': triage,
        'LIFECYCLE': lifecycle,
        'REASON_CODE': motivo,
        'NEXT_ACTION': MOTIVOS.get(motivo) if motivo else None,
        'STAGE_VERDICTS': {k: list(val) for k, val in v.items()},
    }


# ── 7 · CONTABILIDADE FECHADA ──────────────────────────────────────────────────────

def contabilidade(passaportes, collection_id=None):
    """A invariável permanente. Se não fechar, GATE = FAIL — sem exceção e sem versão."""
    itens = [p for p in passaportes.values()
             if collection_id is None or p['COLLECTION_ID'] == collection_id]
    ciclo = {k: 0 for k in ('ACTIVE', 'COMPLETED', 'DEFERRED', 'REJECTED', 'ERROR')}
    for p in itens:
        ciclo[p['LIFECYCLE']] += 1

    estagios, drops = {}, []
    for nome in ESTAGIOS:
        c = {'INPUT_TO_STAGE': 0, 'PASSED': 0, 'STOPPED_WITH_REASON': 0,
             'PENDING': 0, 'ERROR': 0}
        for p in itens:
            ver, motivo = p['STAGE_VERDICTS'][nome]
            if ver is None:
                continue
            c['INPUT_TO_STAGE'] += 1
            c[ver] += 1
            if ver in ('STOPPED_WITH_REASON', 'PENDING') and not motivo:
                drops.append({'ITEM_ID': p['ITEM_ID'], 'STAGE': nome, 'WHY': 'sem REASON_CODE'})
        c['FECHA'] = (c['INPUT_TO_STAGE'] ==
                      c['PASSED'] + c['STOPPED_WITH_REASON'] + c['PENDING'] + c['ERROR'])
        estagios[nome] = c

    # A segunda prova de que não há queda inexplicada: quem entra num estágio é exatamente
    # quem passou no anterior. Uma diferença aqui é item que sumiu entre dois estágios.
    for i in range(1, len(ESTAGIOS)):
        ant, atual = ESTAGIOS[i - 1], ESTAGIOS[i]
        if estagios[atual]['INPUT_TO_STAGE'] != estagios[ant]['PASSED']:
            drops.append({'STAGE': atual, 'WHY': 'entrada (%d) != aprovados do anterior (%d)'
                          % (estagios[atual]['INPUT_TO_STAGE'], estagios[ant]['PASSED'])})

    total = len(itens)
    soma = sum(ciclo.values())
    return {
        'COLLECTION_ID': collection_id or 'TODAS',
        'TOTAL_ENTERED': total,
        'LIFECYCLE': ciclo,
        'LIFECYCLE_SOMA': soma,
        'LIFECYCLE_FECHA': soma == total,
        'STAGES': estagios,
        'STAGES_FECHAM': all(e['FECHA'] for e in estagios.values()),
        'UNEXPLAINED_STAGE_DROPS': drops,
        'GATE': ('PASS' if (soma == total and all(e['FECHA'] for e in estagios.values())
                            and not drops) else 'FAIL'),
    }


# ── 8 · DÍVIDA VISÍVEL ─────────────────────────────────────────────────────────────
#
# Uma dívida é um par de estados que, junto, denuncia trabalho comprado e não usado.
# Ela não é uma exceção nem um alerta: é uma FILA, com nome, e ela existe até alguém a
# resolver. Nunca fica invisível.

def filas_de_divida(passaportes):
    f = {'TRANSCRIPT_AVAILABLE_NOT_READ': [], 'CONTENT_AVAILABLE_NOT_READ': [],
         'READ_WITHOUT_CLAIM': [], 'CLAIMS_WITHOUT_ROUTING': [],
         'ROUTED_NOT_CONSUMED': [], 'ORPHAN_INTELLIGENCE': []}
    for iid, p in sorted(passaportes.items()):
        if p['CONTENT_STATE'] == 'AVAILABLE' and p['CONTENT_READ_STATE'] != 'READ':
            f['CONTENT_AVAILABLE_NOT_READ'].append(iid)
            if p['CONTENT_TYPE'] == 'TRANSCRIPT':
                # A fila do incidente, separada da geral de propósito: era ela que não
                # existia, e é ela que precisa ser lida em voz alta toda vez.
                f['TRANSCRIPT_AVAILABLE_NOT_READ'].append(iid)
        if p['CONTENT_READ_STATE'] == 'READ' and p['CLAIM_STATE'] == PENDING:
            f['READ_WITHOUT_CLAIM'].append(iid)
        if p['CLAIM_STATE'] == 'EXTRACTED' and p['ROUTING_STATE'] == PENDING:
            f['CLAIMS_WITHOUT_ROUTING'].append(iid)
        if p['ROUTING_STATE'] == 'ROUTED' and p['CONSUMPTION_STATE'] == 'READY_NOT_CONSUMED':
            f['ROUTED_NOT_CONSUMED'].append(iid)
        if p['CLAIM_STATE'] == 'EXTRACTED' and not [
                r for r in p['ROUTES'] if r['RELEVANCE'] in RELEVANTES]:
            f['ORPHAN_INTELLIGENCE'].append(iid)
    return f


def _consumo_do_item(p):
    rel = [r for r in p['ROUTES'] if r['RELEVANCE'] in RELEVANTES]
    if not rel:
        # Inteligência válida SEM consumidor não pode ficar PENDING: PENDING seria
        # "ainda não se sabe", e aqui se sabe — não há para onde ela ir. ORPHAN_INTELLIGENCE
        # é um estado com nome, e é ele que impede que ela desapareça do painel.
        return 'ORPHAN_INTELLIGENCE' if p['CLAIM_STATE'] == 'EXTRACTED' else None
    if any(r['STATE'] == 'CONSUMED' for r in rel):
        return 'CONSUMED'
    if all(r['STATE'] == 'BLOCKED' for r in rel):
        return 'BLOCKED'
    return 'READY_NOT_CONSUMED'


def main():
    reg = Registro.carregar()
    ps = reg.passaportes()
    c = contabilidade(ps)
    if '--json' in sys.argv:
        print(json.dumps({'CONTABILIDADE': c,
                          'DIVIDA': {k: len(v) for k, v in filas_de_divida(ps).items()}},
                         ensure_ascii=False, indent=1))
        return 0
    print('PASSAPORTES        %d' % c['TOTAL_ENTERED'])
    print('EVENTOS            %d' % len(reg.eventos))
    for k, v in c['LIFECYCLE'].items():
        print('  %-10s %6d' % (k, v))
    print('GATE               %s' % c['GATE'])
    return 0 if c['GATE'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
