from owlready2 import *
import sys
import os
import contextlib
from datetime import datetime

owlready2.JAVA_EXE = "java"
owlready2.set_log_level(0)

onto = get_ontology("http://dei.uc.pt/room_management.owl")


#silenciar stdout e stderr para evitar mensagens do reasoner
@contextlib.contextmanager
def silence_stdout_stderr():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


with onto:
    # --- CLASSES BASE ---
    class Room(Thing): pass
    class RoomBooking(Thing): pass
    class Person(Thing): pass
    class Teacher(Person): pass
    class Student(Person): pass
    class Activity(Thing): pass
    class Lecture(Activity): pass
    class Exam(Activity): pass
    class Course(Thing): pass
    class Equipment(Thing): pass

    # --- PROPRIEDADES DE OBJETO ---
    class MadeBy(RoomBooking >> Person, FunctionalProperty):
        python_name = "made_by"
    class AssignedToRoom(RoomBooking >> Room, FunctionalProperty): 
        python_name = "assigned_to_room"
    class ForActivity(RoomBooking >> Activity, FunctionalProperty): 
        python_name = "for_activity"
    class HasEquipment(Room >> Equipment): 
        python_name = "has_equipment"
    class RequiresEquipment(Activity >> Equipment): 
        python_name = "requires_equipment"
    class InvolvesCourse(Activity >> Course, FunctionalProperty):
        python_name = "involves_course"

    # --- PROPRIEDADES DE DADOS ---
    class HasCapacity(Room >> int, FunctionalProperty): 
        python_name = "has_capacity"
    class StudentCount(Activity >> int, FunctionalProperty): 
        python_name = "student_count"
    class HasStartTime(RoomBooking >> int, FunctionalProperty): 
        python_name = "start_time"
    class HasEndTime(RoomBooking >> int, FunctionalProperty): 
        python_name = "end_time"
    class HasDay(RoomBooking >> str, FunctionalProperty): 
        python_name = "has_day"
    class HasPriority(RoomBooking >> int, FunctionalProperty): 
        python_name = "has_priority"
    class HasComputerCount(Room >> int, FunctionalProperty):
        python_name = "has_computer_count"
    class RequiresPCs(Activity >> int, FunctionalProperty):
        python_name = "requires_pcs"

    # Propriedades de Estado para Agentes 
    class BookingStatus(RoomBooking >> str, FunctionalProperty): python_name = "booking_status"
    class IsConfirmed(RoomBooking >> bool, FunctionalProperty): python_name = "is_confirmed"
    class HoursSinceCleaning(Room >> int, FunctionalProperty): python_name = "hours_since_cleaning"
    class TotalUsageHours(Room >> int, FunctionalProperty): python_name = "total_usage_hours"
    class IsCritical(Equipment >> bool, FunctionalProperty): python_name = "is_critical"
    class IsBroken(Equipment >> bool, FunctionalProperty): python_name = "is_broken"

    # --- CLASSES INFERIDAS ---
    class PendingBooking(RoomBooking):
        equivalent_to = [RoomBooking & BookingStatus.value("Pendente")]

    class RoomNeedsCleaning(Room):
        equivalent_to = [Room & HoursSinceCleaning.some(ConstrainedDatatype(int, min_inclusive=8))]

    class RoomNeedsRevision(Room):
        equivalent_to = [Room & TotalUsageHours.some(ConstrainedDatatype(int, min_inclusive=50))]

    class InoperableRoom(Room):
        equivalent_to = [Room & HasEquipment.some(Equipment & IsBroken.value(True) & IsCritical.value(True))]

    class UnavailableRoom(Room):
        equivalent_to = [RoomNeedsCleaning | RoomNeedsRevision | InoperableRoom]

    class LargeRoom(Room):
        equivalent_to = [Room & HasCapacity.some(ConstrainedDatatype(int, min_inclusive=50))]

    AllDisjoint([Lecture, Exam])



# AGENTE 1: GESTOR DE RESERVAS 

class BookingAgent:
    def __init__(self, ontology):
        self.onto = ontology

    def run(self):
        print("\n[Agente 1] Processando pedidos...")
        try:
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception: pass
        
        pedidos = list(self.onto.PendingBooking.instances())
        if not pedidos:
            print("[Agente 1] Nada para processar.")
            return

        pedidos.sort(key=lambda x: x.has_priority or 99)
        for p in pedidos:
            self.process_request(p)

    def process_request(self, booking):
        try:
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception:
            pass

        old_room = booking.assigned_to_room
        activity = booking.for_activity
        req_cap = activity.student_count or 0
        req_eq = set(activity.requires_equipment)
        req_pcs = activity.requires_pcs or 0
        
        # Se houver sala específica, valida apenas essa; senão, procura em todas
        if booking.assigned_to_room:
            candidate_rooms = (
                [booking.assigned_to_room] +
                [r for r in self.onto.Room.instances() if r != booking.assigned_to_room]
            )
            print(f"> Tentando sala solicitada e alternativas para: {booking.name}")
        else:
            candidate_rooms = list(self.onto.Room.instances())
            print(f"> Procurando sala automática para: {booking.name}")

        for room in candidate_rooms:
            if any(e.is_broken and e.is_critical for e in room.has_equipment):
                continue
            if (room.has_computer_count or 0) < req_pcs:
                continue
            if room in self.onto.UnavailableRoom.instances(): continue
            if room.has_capacity < req_cap: continue
            if not req_eq.issubset(set(room.has_equipment)): continue
            
            if not self.has_conflict(room, booking):
                booking.assigned_to_room = room
                booking.booking_status = "Confirmada"
                booking.is_confirmed = True
                if old_room and old_room != room:
                    print(f"[⟳] Reserva '{booking.name}' remarcada de {old_room.name} para {room.name}")
                else:
                    print(f"[✔] Reserva '{booking.name}' confirmada em {room.name}")
                return
        
        booking.assigned_to_room = None
        booking.booking_status = "Rejeitada"
        print(f"[✘] Falha: Sala indisponível ou requisitos não cumpridos para {booking.name}")

    def has_conflict(self, room, b1):
        for b2 in self.onto.RoomBooking.instances():
            if b2.is_confirmed and b2.assigned_to_room == room and b2.has_day == b1.has_day:
                if b1.start_time < b2.end_time and b1.end_time > b2.start_time:
                    return True
        return False



# AGENTE 2: MANUTENÇÃO E LOGÍSTICA

class MaintenanceAgent:
    def __init__(self, ontology, booking_agent):
        self.onto = ontology
        self.booking_agent = booking_agent
        self.tarefas = {}

    def update_usage(self, room, duration):
        room.hours_since_cleaning = (room.hours_since_cleaning or 0) + duration
        room.total_usage_hours = (room.total_usage_hours or 0) + duration
        try: 
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception: 
            pass
        
        if room in self.onto.RoomNeedsCleaning.instances() and room.name not in self.tarefas:
            self.tarefas[room.name] = {"tipo": "Limpeza", "ciclos": 1}
        if room in self.onto.RoomNeedsRevision.instances():
            self.tarefas[room.name] = {"tipo": "Revisão", "ciclos": 2}

    def report_failure(self, room, equipment):
        print(f"\n[Agente 2] Avaria em {equipment.name} na {room.name}")
        equipment.is_broken = True
        try:
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception: 
            pass
        
        critico_avariado = any(
            e.is_broken and e.is_critical
            for e in room.has_equipment
        )

        if critico_avariado:
            print("[CRÍTICO] Realocando reservas...")
            self.relocate(room)
            self.tarefas[room.name] = {"tipo": "Reparação", "ciclos": 3}
            room.hours_since_cleaning = 999
            room.total_usage_hours = 999
            try:
                with silence_stdout_stderr():
                    sync_reasoner()
            except:
                pass

    def relocate(self, room):
        reservas = [
            b for b in self.onto.RoomBooking.instances()
            if b.assigned_to_room == room and b.is_confirmed
        ]

        for b in reservas:
            b.assigned_to_room = None
            b.booking_status = "Pendente"
            b.is_confirmed = False

        try:
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception:
            pass

        for b in reservas:
            self.booking_agent.process_request(b)


    def run_simulation(self):
        print("\n--- Ciclo de Manutenção ---")
        concluidas = []
        for name, info in self.tarefas.items():
            info["ciclos"] -= 1
            print(f"  {info['tipo']} em {name}: {info['ciclos']} restantes")
            if info["ciclos"] <= 0: concluidas.append((name, info["tipo"]))
        for n, t in concluidas:
            self.finish(n, t)
            del self.tarefas[n]

    def finish(self, name, tipo):
        r = self.onto.search_one(iri=f"*{name}")
        if tipo == "Limpeza": r.hours_since_cleaning = 0
        elif tipo == "Revisão": r.total_usage_hours = 0; r.hours_since_cleaning = 0
        elif tipo == "Reparação":
            for e in r.has_equipment:
                e.is_broken = False
            r.hours_since_cleaning = 0
            r.total_usage_hours = 0
        try: 
            with silence_stdout_stderr():
                sync_reasoner()
        except Exception: pass
        print(f"[✔]{tipo} concluída em {name}")


def criar_reservas_teste(onto):
    print("\n[SETUP] A criar reservas automáticas de teste...")

    with onto:
        # Pessoas
        prof1 = Teacher("Prof_Ana_Silva")
        prof2 = Teacher("Prof_Joao_Costa")

        # Cursos
        ei = Course("EI")
        iacd = Course("IACD")

        # Atividades
        act1 = Exam(
            "Act_Exame_EI",
            student_count=120,
            requires_pcs=0,
            involves_course=ei
        )

        act2 = Lecture(
            "Act_Aula_IACD",
            student_count=30,
            requires_pcs=25,
            involves_course=iacd
        )

        act3 = Lecture(
            "Act_Aula_EI_PC",
            student_count=40,
            requires_pcs=35,
            involves_course=ei
        )

        # Reservas
        RoomBooking(
            "Reserva_Exame_EI",
            made_by=prof1,
            for_activity=act1,
            has_day="20/01/2026",
            start_time=9,
            end_time=12,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=1
        )

        RoomBooking(
            "Reserva_Aula_IACD",
            made_by=prof2,
            for_activity=act2,
            has_day="20/01/2026",
            start_time=10,
            end_time=12,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=2
        )

        RoomBooking(
            "Reserva_Aula_EI_PC",
            made_by=prof1,
            for_activity=act3,
            has_day="20/01/2026",
            start_time=11,
            end_time=13,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=2
        )

        # Reserva que vai causar conflito com a primeira
        RoomBooking(
            "Reserva_Exame_EI_Conflito",
            made_by=prof2,
            for_activity=Exam(
                "Act_Exame_EI_Conflito",
                student_count=110,
                requires_pcs=0,
                involves_course=ei
            ),
            has_day="20/01/2026",
            start_time=10,
            end_time=13,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=1
        )

        # Reserva que vai causar conflito com a segunda
        RoomBooking(
            "Reserva_Aula_IACD_Conflito",
            made_by=prof1,
            for_activity=Lecture(
                "Act_Aula_IACD_Conflito",
                student_count=40,
                requires_pcs=40,
                involves_course=iacd
            ),
            has_day="20/01/2026",
            start_time=10,
            end_time=12,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=2
        )

        # Reserva com pcs insuficientes
        RoomBooking(
            "Reserva_Aula_IACD_PC_Falha",
            made_by=prof1,
            for_activity=Lecture(
                "Act_Aula_IACD_PC_Falha",
                student_count=45,
                requires_pcs=45,
                involves_course=iacd
            ),
            has_day="20/01/2026",
            start_time=11,
            end_time=13,
            booking_status="Pendente",
            is_confirmed=False,
            has_priority=2
        )

    print("[SETUP] Reservas criadas com sucesso.\n")



# INTERFACE INTERATIVA 

def menu():
    ag1 = BookingAgent(onto)
    ag2 = MaintenanceAgent(onto, ag1)
    
    criar_reservas_teste(onto)

    with onto:
        def projetor_fixo(nome):
            return Equipment(nome, is_critical=True, is_broken=False)

        def projetor_movel(nome):
            return Equipment(nome, is_critical=False, is_broken=False)

        
        # Anfiteatros (Grande Capacidade)
        Room("Anfiteatro_A1", has_capacity=150, has_equipment=[projetor_fixo("Proj_A1")], hours_since_cleaning=0, has_computer_count=0, total_usage_hours=0)
        Room("Anfiteatro_B1", has_capacity=100, has_equipment=[projetor_fixo("Proj_B1")], hours_since_cleaning=0, has_computer_count=0, total_usage_hours=0)
        Room("Anfiteatro_A2", has_capacity=120, has_equipment=[projetor_fixo("Proj_A2")], hours_since_cleaning=0, has_computer_count=0, total_usage_hours=0)
        Room("Anfiteatro_B2", has_capacity=110, has_equipment=[projetor_fixo("Proj_B2")], hours_since_cleaning=0, has_computer_count=0, total_usage_hours=0)

        # Salas de Aula/Laboratórios (Média/Pequena Capacidade)
        Room("Sala_C.5.1", has_capacity=25, has_equipment=[projetor_fixo("Proj_C.5.1")], hours_since_cleaning=0, has_computer_count=22, total_usage_hours=0)
        Room("Sala_C.5.2", has_capacity=40, has_equipment=[projetor_movel("Proj_C.5.2")], hours_since_cleaning=0, has_computer_count=36, total_usage_hours=0)
        Room("Sala_C.5.3", has_capacity=30, has_equipment=[], hours_since_cleaning=0, has_computer_count=27, total_usage_hours=0)
        Room("Sala_C.5.4", has_capacity=45, has_equipment=[projetor_fixo("Proj_C.5.4"), projetor_movel("Proj_C.5.4")], hours_since_cleaning=0, has_computer_count=45, total_usage_hours=0)
        Room("Sala_C.5.5", has_capacity=20, has_equipment=[projetor_movel("Proj_C.5.5")], hours_since_cleaning=0, has_computer_count=19, total_usage_hours=0)
        Room("Sala_C.5.6", has_capacity=35, has_equipment=[], hours_since_cleaning=0, has_computer_count=33, total_usage_hours=0)
        Room("Sala_C.6.1", has_capacity=25, has_equipment=[projetor_fixo("Proj_C.6.1")], hours_since_cleaning=0, has_computer_count=22, total_usage_hours=0)
        Room("Sala_C.5.8", has_capacity=40, has_equipment=[projetor_movel("Proj_C.5.8")], hours_since_cleaning=0, has_computer_count=36, total_usage_hours=0)
        Room("Sala_C.6.2", has_capacity=30, has_equipment=[projetor_fixo("Proj_C.6.2")], hours_since_cleaning=0, has_computer_count=27, total_usage_hours=0)
        Room("Sala_C.6.3", has_capacity=45, has_equipment=[projetor_movel("Proj_C.6.3")], hours_since_cleaning=0, has_computer_count=45, total_usage_hours=0)
        Room("Sala_C.6.4", has_capacity=20, has_equipment=[projetor_fixo("Proj_C.6.4"), projetor_movel("Proj_C.6.4")], hours_since_cleaning=0, has_computer_count=19, total_usage_hours=0)
        Room("Sala_C.6.5", has_capacity=35, has_equipment=[], hours_since_cleaning=0, has_computer_count=33, total_usage_hours=0)
        Room("Sala_C.6.6", has_capacity=40, has_equipment=[projetor_fixo("Proj_C.6.6"), projetor_movel("Proj_C.6.6")], hours_since_cleaning=0, has_computer_count=39, total_usage_hours=0)

    main_running = True
    while main_running:
        print(" ")
        print(">> SISTEMA DE GESTÃO DE SALAS - DEI <<")
        print(" ")
        entidade = input("Identifique-se (S para Estudante, T para Professor, 0 para Sair): ").upper()

        while entidade not in ["S", "T", "0"]:
            entidade =  input("[✘] Opção inválida. Tente novamente: ").upper()

        if entidade == "0":
            break

        menu_running = True
        while menu_running:
            print(f"\n--- MENU PRINCIPAL --- \n->(Sessão: {'Professor' if entidade == 'T' else 'Estudante'})<-\n")
            print("1. Criar Pedido de Reserva" if entidade == "T" else "1. [BLOQUEADO] Criar Reserva")
            print("2. Processar Pendentes")
            print("3. Reportar Avaria")
            print("4. Ver Estado do Sistema")
            print("0. Terminar Sessão / Sair")
            print(" ")
            print("---------------------")
            print(" ")
            print("9. Testar ciclo / Simular tempo")
            
            opcao = input("\nEscolha uma opção: ")

            while opcao not in ["1", "2", "3", "4", "9", "0"]:
                opcao = input("[✘] Opção inválida. Tente novamente: ")

            if opcao == "1":
                if entidade != "T":
                    print(f"[✘] Apenas Professores podem solicitar salas.")
                else:
                    while True:
                        nome_reserva = input("Nome da reserva: ").strip()
                        exists = onto.search_one(iri=f"*{nome_reserva}")
                        if exists:
                            print(f"[✘] Esse nome de reserva já existe. Escolha outro.")
                        elif not nome_reserva:
                            print(f"[✘] O nome não pode ser vazio.")
                        else:
                            break
                    while True:
                        print("\nTipo de Atividade:")
                        print("1. Exame (Prioridade Alta)")
                        print("2. Aula (Prioridade Normal)")
                        tipo_act = input("Escolha a opção: ").strip()
                        
                        if tipo_act == "1":
                            classe_atividade = Exam
                            prioridade = 1
                            prefixo = "Exame"
                            break
                        elif tipo_act == "2":
                            classe_atividade = Lecture
                            prioridade = 2
                            prefixo = "Aula"
                            break
                        print("[✘] Opção inválida.")

                    # 1. Nome completo
                    while True:
                        nome_user = input("Seu nome completo (Primeiro e Último): ").strip()
                        if len(nome_user.split()) >= 2:
                            break
                        print(f"[✘] Introduza pelo menos o primeiro e o último nome.")

                    with onto:
                        utilizador = onto.search_one(iri=f"*{nome_user.replace(' ', '_')}")
                        if not utilizador:
                            utilizador = Teacher(nome_user.replace(' ', '_'))

                    # 2. Data
                    while True:
                        data_str = input("Dia da reserva (dd/mm/yyyy): ")
                        try:
                            datetime.strptime(data_str, "%d/%m/%Y")
                            break
                        except ValueError:
                            print(f"[✘] Formato inválido! Use dd/mm/yyyy (ex: 15/01/2026).")
                    # 3. Hora de Início e Fim
                    while True:
                        try:
                            h_ini_str = input("Hora de início (ex: 09h00): ")
                            h_fim_str = input("Hora de fim (ex: 11h00): ")
                            
                            h_ini = int(h_ini_str.split('h')[0])
                            h_fim = int(h_fim_str.split('h')[0])
                            
                            if h_fim <= h_ini:
                                print("[✘] Erro: A hora de fim deve ser posterior à de início.")
                            else:
                                break
                        except:
                            print("[✘] Formato inválido! Use o formato 00h00.")
                    
                    # 4. Nome do Curso
                    while True:
                        nome_curso = input("Curso da atividade (ex: EI, IACD): ").strip()
                        nome_curso = nome_curso.upper()
                        break

                    # 5. Número de alunos
                    while True:
                        try:
                            n_alunos = int(input("Número de alunos: "))
                            if n_alunos > 0: break
                            print("[✘] O número deve ser superior a zero.")
                        except ValueError:
                            print("[✘] Introduza um número inteiro válido.")

                    # 6. Requisitos de Equipamento
                    while True:
                        try:
                            n_pcs = int(input("Número de computadores necessários: "))
                            break
                        except ValueError: print("[✘] Introduza um número.")

                    while True:
                        proj_input = input("Projetor necessário? (Sim/Não): ").strip().lower()
                        if proj_input in ["sim", "s", "si"]:
                            precisa_projetor = True
                            break
                        elif proj_input in ["nao", "não", "n"]:
                            precisa_projetor = False
                            break
                        else:
                            print("[✘] Opção inválida. Escolha Sim ou Não.")

                    print(f"\n--- Procurando salas adequadas ---")
                    
                    with silence_stdout_stderr():
                        sync_reasoner()
                    
                    salas_adequadas = []
                    for sala in list(onto.Room.instances()):
                        # 1. Ignorar salas bloqueadas pelo Agente 2
                        if sala in onto.UnavailableRoom.instances():
                            continue
                        
                        # 2. Verificar Capacidade
                        if (sala.has_capacity or 0) < n_alunos:
                            continue
                        
                        # 3. Verificar Número de PCs
                        if (sala.has_computer_count or 0) < n_pcs:
                            continue
                        
                        # 4. Verificar Projetor (Se pediu Sim, procura a palavra "projetor" nos equipamentos)
                        if precisa_projetor:
                        # Se o utilizador PRECISA, verificamos se a sala tem algum projetor
                            tem_algum_projetor = any("projetor" in e.name.lower() for e in sala.has_equipment)
                            if not tem_algum_projetor:
                                continue  # Se precisa e não tem, descarta a sala

                        salas_adequadas.append(sala)

                    if not salas_adequadas:
                        print(f"[✘] Nenhuma sala encontrada com esses requisitos.")
                    else:
                        print("\nSalas Disponíveis:")
                        for s in salas_adequadas:
                            print(f" - {s.name} (Capacidade: {s.has_capacity})")
                        
                        while True:
                            escolha = input("\nEscreva o nome da sala que pretende: ").strip()
                            sala_selecionada = next((s for s in salas_adequadas if s.name == escolha), None)
                            
                            if sala_selecionada:
                                with onto:
                                    curso = onto.search_one(iri=f"*{nome_curso}")
                                    if not curso:
                                        curso = Course(nome_curso)

                                    equip_reqs = []
                                    if precisa_projetor:
                                        equip_reqs.append( projetor_fixo(f"Proj_Req_{nome_reserva}"))

                                    atividade = classe_atividade(
                                        f"Act_{nome_reserva}",
                                        student_count=n_alunos,
                                        requires_pcs=n_pcs,
                                        requires_equipment=equip_reqs,
                                        involves_course=curso
                                    )

                                    nova_reserva = RoomBooking(
                                        nome_reserva,
                                        made_by=utilizador,
                                        assigned_to_room=sala_selecionada,
                                        for_activity=atividade,
                                        has_day=data_str,
                                        start_time=h_ini,
                                        end_time=h_fim,
                                        booking_status="Pendente",
                                        is_confirmed=False,
                                        has_priority=prioridade
                                    )
                                
                                ag1.process_request(nova_reserva)

                                if nova_reserva.is_confirmed:
                                    print(f"[✔] Reserva '{nome_reserva}' confirmada na {nova_reserva.assigned_to_room.name}!")
                                else:
                                    print(f"[✘] Reserva '{nome_reserva}' não pôde ser confirmada.")
                                break
                            else:
                                print("[✘] Nome da sala incorreto ou sala não listada. Tente novamente.")

            elif opcao == "2": ag1.run()
            elif opcao == "3":
                print("\n--- Reportar Avaria ---")
                print(" ")

                salas = list(onto.Room.instances())
                for i, s in enumerate(salas):
                    print(f"{i+1}. {s.name}")

                print(" ")
                idx = int(input("Escolha a sala: ")) - 1

                while idx < 0 or idx >= len(salas):
                    print(" ")
                    idx = int(input("[✘] Opção inválida. Tente novamente: ")) - 1

                sala = salas[idx]

                if not sala.has_equipment:
                    print(" ")
                    print("[✘] Esta sala não tem equipamentos.")
                    continue

                for i, e in enumerate(sala.has_equipment):
                    print(f"{i+1}. {e.name}")

                print(" ")
                idx_e = int(input("Escolha o equipamento avariado: ")) - 1
                equipamento = sala.has_equipment[idx_e]

                ag2.report_failure(sala, equipamento)
            elif opcao == "9":
                todas_reservas = list(onto.RoomBooking.instances())
                count_reservas = len(todas_reservas)

                if count_reservas < 3:
                    print(f"\n[✘] SIMULAÇÃO BLOQUEADA")
                    print(f"Motivo: São necessárias pelo menos 3 reservas registadas para simular o tempo.")
                    print(f"Estado atual: {count_reservas} reserva(s) encontrada(s).")
                else:
                    print(f"\n--- Simulando ciclo de tempo ({count_reservas} reservas processadas) ---")
                    print(" ")
                    
                    reservas_para_processar = [x for x in onto.RoomBooking.instances() if x.booking_status == "Confirmada"]
                    
                    if not reservas_para_processar:
                        print("[!] Aviso: Existem reservas no sistema, mas nenhuma está com estado 'Confirmada'.")
                    else:
                        for b in reservas_para_processar:
                            duracao = b.end_time - b.start_time
                            ag2.update_usage(b.assigned_to_room, duracao)
                            
                            b.booking_status = "Concluída"
                            b.is_confirmed = False
                        
                        ag2.run_simulation() 
                        print("\n[✔] Ciclo de tempo concluído e contadores atualizados.")

            elif opcao == "4":
                try:
                    with silence_stdout_stderr():
                        sync_reasoner()
                except:
                    print("[!] Aviso: Ontologia inconsistente. Estado aproximado apresentado.")

                print("\nESTADO DAS SALAS:")

                for r in onto.Room.instances():
                    indisponivel = (
                        r in onto.UnavailableRoom.instances()
                        or (r.hours_since_cleaning or 0) >= 8
                        or (r.total_usage_hours or 0) >= 50
                        or any(e.is_broken and e.is_critical for e in r.has_equipment)
                    )

                    status = "[✘] Indisponível" if indisponivel else "[✔] Disponível"
                    print(f"- {r.name}: {status} (Uso: {r.hours_since_cleaning}h/8h)")

            elif opcao == "0":
                print("\nO que deseja fazer?")
                print("1. Voltar ao Início (Trocar Utilizador)")
                print("2. Sair do Programa")
                print(" ")
                sub_opcao = input("Escolha: ")

                while sub_opcao not in ["1", "2"]:
                    sub_opcao = input("[✘] Opção inválida. Tente novamente: ")

                if sub_opcao == "1":
                    menu_running = False

                if sub_opcao == "2" :
                    print(" ")
                    print("A encerrar sistema...")
                    main_running = False
                    menu_running = False

    onto.save(file="dei_rooms_final.owl", format="rdfxml")
    print("Ontologia guardada. Adeus!")

if __name__ == "__main__":
    menu()