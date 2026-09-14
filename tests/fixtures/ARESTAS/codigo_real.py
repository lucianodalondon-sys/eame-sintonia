"""Um writer de verdade."""
import json


def escrever(banco, derived_artifact_id):
    linha = banco.executa(
        "select sha256, storage_path from public.derived_artifact where id = %s"
        % derived_artifact_id)
    return json.dumps({'DERIVED': linha})
