# Instruções para agentes neste repositório

**A lei deste repositório vive em [`../AGENTS.md`](../AGENTS.md). Leia-a antes
de alterar qualquer coisa.**

Este ficheiro é apenas um **ponteiro**. Ele não repete a lei de propósito: uma
lei escrita em dois sítios diverge, e a partir daí nenhuma das duas vale.

Um dono. Múltiplos ponteiros.

O resumo mínimo, para não haver desculpa:

- o SINTONIA System Map (`system-map/`) é uma projeção da arquitetura real;
- toda mudança relevante de arquitetura **tem de** atualizar o mapa na mesma mudança;
- antes de fechar a tarefa:

```bash
python3 system-map/scripts/generate_system_map.py
python3 system-map/scripts/validate_system_map.py
```

- ligação sem prova não existe; verde sem evidência não existe; **NÃO SEI é um
  resultado válido e obrigatório** quando é o caso;
- o mapa é derivado do repo — o repo não é derivado do mapa.
