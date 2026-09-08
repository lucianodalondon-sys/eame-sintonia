"""O ajudante e quem toca a tabela."""


def persistir(banco, x):
    return banco.executa(
        "select sha256 from public.derived_artifact where id = %s" % x)
