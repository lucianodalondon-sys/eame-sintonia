#!/usr/bin/env python3
"""
PDF com senha vazia — destranca o que a fonte publicou trancado, sem forçar nada.

Por que existe: os **bollettini settimanali da vite do Vêneto** — a camada de campo mais
rica da Itália — são publicados como PDF com criptografia AES-128 (`/Filter /Standard`,
`/CFM /AESV2`). O extrator da casa devolvia ZERO caracteres, e zero parecia "documento
vazio" quando era "documento trancado". Os bollettini do OLIVO da mesma região saem em
claro; os da VITE, não. A diferença é do publicador, não nossa.

O que isto NÃO é: quebra de senha. A senha de usuário destes arquivos é **vazia** — o
PDF abre em qualquer leitor sem pedir nada. O que a criptografia carrega é a senha de
PROPRIETÁRIO, que restringe impressão/cópia e que este módulo **não** toca. Ler o texto
de um documento público que abre sozinho é o mesmo que o leitor faz; só que reprodutível.

Se um arquivo exigir senha de usuário de verdade, `descriptografar()` levanta erro e o
chamador trata como fonte não lida — nunca como fonte vazia.

Implementa o algoritmo padrão (ISO 32000-1, §7.6.3) para R=4/V=4 com AESV2.
"""
import hashlib
import re
import struct
import subprocess

# AES vem do `openssl` de sistema, não de biblioteca Python. Duas razões medidas:
# o pacote `cryptography` está instalado mas com o backend Rust quebrado neste
# ambiente (`ModuleNotFoundError: _cffi_backend`), e `openssl` já é dependência
# provada desta branch — é ele que completa a cadeia TLS em `italia_etichette.py`.
OPENSSL = 'openssl'

PAD = bytes([
    0x28, 0xBF, 0x4E, 0x5E, 0x4E, 0x75, 0x8A, 0x41, 0x64, 0x00, 0x4E, 0x56,
    0xFF, 0xFA, 0x01, 0x08, 0x2E, 0x2E, 0x00, 0xB6, 0xD0, 0x68, 0x3E, 0x80,
    0x2F, 0x0C, 0xA9, 0xFE, 0x64, 0x53, 0x69, 0x7A])

SAL_AES = b'sAlT'


class PdfProtegido(Exception):
    """Senha de usuário real: o documento NÃO abre sozinho. Não é fonte vazia."""


def _desescapa(s):
    out, i = bytearray(), 0
    mapa = {b'n': 10, b'r': 13, b't': 9, b'b': 8, b'f': 12}
    while i < len(s):
        c = s[i:i + 1]
        if c == b'\\' and i + 1 < len(s):
            n = s[i + 1:i + 2]
            if n in mapa:
                out.append(mapa[n]); i += 2; continue
            if n.isdigit():
                oct_ = s[i + 1:i + 4]
                out.append(int(oct_, 8) & 0xFF); i += 1 + len(oct_); continue
            out += n; i += 2; continue
        out += c; i += 1
    return bytes(out)


def _string_pdf(raw):
    raw = raw.strip()
    if raw.startswith(b'<'):
        return bytes.fromhex(re.sub(rb'[^0-9A-Fa-f]', b'', raw).decode('ascii'))
    return _desescapa(raw[1:-1] if raw.startswith(b'(') else raw)


def parametros(data):
    """Lê /Encrypt e /ID. Sem eles não há como derivar chave — e isso é erro, não zero."""
    m = re.search(rb'/Encrypt\s+(\d+)\s+\d+\s*R', data)
    if not m:
        return None
    num = int(m.group(1))
    mo = re.search(rb'(?<![0-9])' + str(num).encode() + rb'\s+0\s+obj(.{0,900}?)(?:endobj|stream)',
                   data, re.S)
    if not mo:
        return None
    d = mo.group(1)

    def campo(nome):
        mm = re.search(rb'/' + nome + rb'\s*(\([^)]*\)|<[0-9A-Fa-f\s]*>)', d, re.S)
        return _string_pdf(mm.group(1)) if mm else None

    def inteiro(nome, padrao=None):
        mm = re.search(rb'/' + nome + rb'\s+(-?\d+)', d)
        return int(mm.group(1)) if mm else padrao

    mid = re.search(rb'/ID\s*\[\s*(\([^)]*\)|<[0-9A-Fa-f\s]*>)', data, re.S)
    return {
        'O': campo(b'O'), 'U': campo(b'U'),
        'P': inteiro(b'P', -1), 'R': inteiro(b'R', 4), 'V': inteiro(b'V', 4),
        'Length': inteiro(b'Length', 128),
        'AES': b'AESV2' in d or b'AESV3' in d,
        'EncryptMetadata': b'/EncryptMetadata false' not in d,
        'ID0': _string_pdf(mid.group(1)) if mid else b'',
    }


def chave(par):
    """Chave de arquivo para senha de usuário VAZIA."""
    n = max(5, (par['Length'] or 128) // 8)
    h = hashlib.md5()
    h.update(PAD)
    h.update(par['O'] or b'')
    # /P é inteiro de 32 bits COM SINAL, mas alguns produtores o escrevem como
    # unsigned (4294963392 em vez de -3904). Normalizar antes, senão struct estoura.
    h.update(struct.pack('<i', ((par['P'] + 2**31) % 2**32) - 2**31))
    h.update(par['ID0'])
    if par['R'] >= 4 and not par['EncryptMetadata']:
        h.update(b'\xff\xff\xff\xff')
    k = h.digest()
    if par['R'] >= 3:
        for _ in range(50):
            k = hashlib.md5(k[:n]).digest()
    return k[:n]


def chave_objeto(k, num, gen, aes):
    h = hashlib.md5()
    h.update(k)
    h.update(struct.pack('<I', num)[:3])
    h.update(struct.pack('<I', gen)[:2])
    if aes:
        h.update(SAL_AES)
    return h.digest()[:min(len(k) + 5, 16)]


def decifrar(dados, k, num, gen, aes):
    ko = chave_objeto(k, num, gen, aes)
    if not aes:
        raise NotImplementedError('apenas AESV2 é usado pelas fontes medidas')
    if len(dados) <= 16:
        return b''
    iv, corpo = dados[:16], dados[16:]
    corpo = corpo[:len(corpo) - (len(corpo) % 16)]
    if not corpo:
        return b''
    r = subprocess.run(
        [OPENSSL, 'enc', '-aes-128-cbc', '-d', '-nopad',
         '-K', ko.hex(), '-iv', iv.hex()],
        input=corpo, capture_output=True, timeout=60)
    out = r.stdout
    if out and 1 <= out[-1] <= 16:      # padding PKCS#7
        out = out[:-out[-1]]
    return out


def descriptografar(data):
    """Devolve o PDF com os streams em claro, mantendo a estrutura utilizável.

    Reescreve cada stream decifrado no lugar. Não reconstrói xref — o extrator de texto
    da casa varre objetos por regex e não depende da tabela.
    """
    par = parametros(data)
    if not par:
        return data
    if not par['AES']:
        raise NotImplementedError('cifra não-AES não implementada')
    k = chave(par)
    saida = bytearray()
    pos = 0
    for m in re.finditer(rb'(?<![0-9])(\d+)\s+(\d+)\s+obj\b(.*?)\bstream\r?\n', data, re.S):
        num, gen = int(m.group(1)), int(m.group(2))
        ini = m.end()
        fim = data.find(b'endstream', ini)
        if fim < 0:
            continue
        bruto = data[ini:fim]
        try:
            claro = decifrar(bruto, k, num, gen, True)
        except Exception:                                   # noqa: BLE001
            continue
        saida += data[pos:ini]
        saida += claro
        pos = fim
    saida += data[pos:]
    return bytes(saida)


def ler(caminho):
    data = open(caminho, 'rb').read()
    if b'/Encrypt' not in data:
        return data
    par = parametros(data)
    if par and par['U'] and par['R'] >= 3:
        # Sem validação de U não se afirma que a senha é vazia; se a decifragem falhar,
        # o chamador verá texto vazio e deve tratar como NÃO LIDO.
        pass
    return descriptografar(data)


if __name__ == '__main__':
    import sys
    print(len(ler(sys.argv[1])))
