# RELATÓRIO — YT3 · CANAIS DE PESSOAS DO AGRO (D24)

Branch `canais-pessoas-v1`, a partir de `origin/unificacao-v1` @ `de4dec2b`, 2026-09-23.
VPN IT (20 portões, 20 PASS) · sem login/cookie/pago · robots respeitado · ≤ 3 pedidos por
host · nenhum banco de teste aberto · nada na Sala.

## ENTREGA

```
SEMENTES          151 hosts = candidatas IT ORGANIZACAO/CIENCIA/IMPRENSA (esta linha 123 + P1 18 + P2 10)
LIDOS             117 (99 + 18 na 2.a passagem pelo curl) · 22 ilegiveis · 12 fechados/erro
ACHADOS           YouTube 54 (28 ja conhecidos) · podcast 1 · newsletter 42 (4 ja conhecidas)
CANDIDATAS NOVAS  14 — 13 canais YouTube + 1 podcast (CAND-0477..0490), tipo YOUTUBE / IMPRENSA
                  identidade: a pagina oficial do dono liga ao canal (sha256 na NOTA)
                  territorio: IT 13 (ccTLD da semente, P.IVA ou morada) · NAO SEI 1 (declarado)
PESSOAS           0 · DEPARTAMENTOS/GRUPOS 0 — as paginas de departamento ligam ao canal do ateneo
FREQUENCIA        YouTube NAO_MEDIDA 13/13 (so a Data API lista videos; chave so no GitHub)
                  podcast NAO_MEDIDA (Spotify sem RSS) · newsletters: 19/21 so inscricao
TECNICO           NAO_MEDIDO (sem rota para ler os videos aqui)
FICAM FORA        51, cada um com motivo em scripts/canais_pessoas/DECISOES-YT3-V1.json
TESTS             tests/test_canais_pessoas.py 9/0 · testes da fila 0 falhas antes/depois
```

## Lista (os 14)

Agroalimentare News · Agroter/Italiafruit · Myfruit · Sherwood (canal + podcast) ·
PSR Calabria · Biolchim · Diachem · Sipcam Italia · FederUnacoma · Nomisma ·
Consorzio del Parmigiano Reggiano · Terremerse · UNAITALIA.

## O que falta para o objectivo da D24 (pessoas)

Nenhuma página oficial lida ligava ao canal de uma PESSOA. Para as pessoas é preciso
outra entrada: a página pessoal do investigador ou do agrónomo no site da universidade ou
da ordem (a P1 e a P4 trabalham aí) e, para medir frequência, a fase `canal-youtube` com a
chave da Data API (GitHub).

Detalhe: §209 do `SINTONIA-EAME-KNOW-HOW.md`.
