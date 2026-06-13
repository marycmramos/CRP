import pathlib
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, get_environment
from unified_planning.engines.results import POSITIVE_OUTCOMES
from collections import defaultdict

base_path = pathlib.Path(__file__).parent.resolve()
get_environment().credits_stream = None

reader = PDDLReader()
domain_file = "domain-dei.pddl"
problem_file = "problem-dei.pddl"

problem = reader.parse_problem(base_path / domain_file, base_path / problem_file)

print("Domínio e problema PDDL carregados")
print("A resolver o agendamento de exames/aulas...\n")

with OneshotPlanner(name="pyperplan") as planner:
    result = planner.solve(problem)
print(f"Estado do planeamento: {result.status}\n")

horario = defaultdict(list)
formatar_horas = {
    "h9": "9h00",
    "h11": "11h00",
    "h14": "14h00",
    "h16": "16h00",
    "h18": "18h00"
}

if result.status in POSITIVE_OUTCOMES and result.plan is not None:
    print("Plano encontrado:\n")

    for action in result.plan.actions:
        exame, sala, tempo, tamanho , curso = action.actual_parameters
        horario[str(tempo)].append((str(exame), str(sala), str(curso)))
    
    print("Horário de Exames:\n")
    ordem_horarios = ["h9", "h11", "h14", "h16", "h18"]
    for tempo in ordem_horarios: 
        hora_formatada = formatar_horas.get(tempo, tempo)
        print(f"{hora_formatada}:")
        
        for exame, sala, curso in horario[tempo]:
            print(f"  - {exame.lower():<12} ({curso.lower()}) → {sala.lower()}")
        print()

else:
        print(" Não foi encontrado um plano válido.")