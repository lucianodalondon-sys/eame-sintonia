# Fixtures da escada de conexao

Os dois ficheiros aqui existem para reproduzir o atalho que a M1 removeu:

    so_comentario.py   cita `derived_artifact` APENAS num docstring e num comentario
    codigo_real.py     consulta `public.derived_artifact` em codigo executavel

Antes, `_liga()` era um grep e devolvia `True` para os dois. `ARCHITECTURE_CLOSED`
aceitava esse positivo como ligacao suficiente — enquanto o proprio censo escrevia
que grep positivo era frouxo.

    GREP POSITIVO NAO E EDGE PROVADA.

Nao apagar: sao a prova viva de que a escada distingue os dois casos.
