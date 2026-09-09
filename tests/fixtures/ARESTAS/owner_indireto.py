"""Um owner que delega. Nao cita o artefato em lugar nenhum."""
from ajudante import persistir


def receber(x):
    return persistir(x)
