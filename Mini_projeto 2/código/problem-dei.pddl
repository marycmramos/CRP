(define (problem exame_scheduling_instance)
  (:domain exame_scheduling)

  (:objects
    ;; Exames
    exame_CRP exame_VD exame_ECAC
    exame_TIA exame_SRSA exame_AC
    exame_AMI exame_IECD exame_POO - exame

    ;; Cursos
    LIACD_1 LIACD_2 LIACD_3 - curso

    ;; Salas
    Anfiteatro_A Anfiteatro_B
    Sala_C_4_5 Sala_C_4_6 
    Sala_E_5_2 Sala_E_5_3 - sala

    ;; Horários
    h9 h11 h14 h16 h18 - timeslot

    ;; Tamanhos
    pequena media grande - tamanho
  )

  (:init
    ;; Estado inicial dos exame
    (unscheduled exame_CRP)
    (unscheduled exame_VD)
    (unscheduled exame_ECAC)
    (unscheduled exame_TIA)
    (unscheduled exame_SRSA)
    (unscheduled exame_AC)
    (unscheduled exame_AMI)
    (unscheduled exame_IECD)
    (unscheduled exame_POO) 

    ;; Salas livres em todos os horários
    (sala-free Anfiteatro_A h9)
    (sala-free Anfiteatro_A h11)
    (sala-free Anfiteatro_A h14)
    (sala-free Anfiteatro_A h16)
    (sala-free Anfiteatro_A h18)

    (sala-free Anfiteatro_B h9)
    (sala-free Anfiteatro_B h11)
    (sala-free Anfiteatro_B h14)

    (sala-free Sala_C_4_5 h9)
    (sala-free Sala_C_4_5 h14)
    (sala-free Sala_C_4_5 h16)
    (sala-free Sala_C_4_5 h18)


    (sala-free Sala_C_4_6 h9)
    (sala-free Sala_C_4_6 h11)
    (sala-free Sala_C_4_6 h14)
    (sala-free Sala_C_4_6 h16)

    (sala-free Sala_E_5_2 h9)
    (sala-free Sala_E_5_2 h11)
    (sala-free Sala_E_5_2 h14)
    (sala-free Sala_E_5_2 h18)

    (sala-free Sala_E_5_3 h9)
    (sala-free Sala_E_5_3 h11)
    (sala-free Sala_E_5_3 h14)
    (sala-free Sala_E_5_3 h16)
    (sala-free Sala_E_5_3 h18)


    ;; Capacidade das salas
    (sala-tamanho Anfiteatro_A grande) (sala-tamanho Anfiteatro_A media) 
    (sala-tamanho Anfiteatro_B grande) 
    (sala-tamanho Sala_C_4_5 media)
    (sala-tamanho Sala_C_4_6 media) (sala-tamanho Sala_C_4_6 pequena)
    (sala-tamanho Sala_E_5_2 pequena)
    (sala-tamanho Sala_E_5_3 pequena)

    ;; Tamanho dos exame (número de alunos)
    (exame-tamanho exame_CRP media)
    (exame-tamanho exame_VD pequena)
    (exame-tamanho exame_ECAC grande)
    (exame-tamanho exame_TIA media)
    (exame-tamanho exame_SRSA grande)
    (exame-tamanho exame_AC grande)
    (exame-tamanho exame_AMI grande)
    (exame-tamanho exame_IECD pequena)
    (exame-tamanho exame_POO media)

    ;; Respetivo curso(ano)
    (exame-curso exame_CRP LIACD_3)
    (exame-curso exame_VD LIACD_3)
    (exame-curso exame_ECAC LIACD_3)
    (exame-curso exame_TIA LIACD_2)
    (exame-curso exame_SRSA LIACD_2)
    (exame-curso exame_AC LIACD_2)
    (exame-curso exame_AMI LIACD_1)
    (exame-curso exame_IECD LIACD_1)
    (exame-curso exame_POO LIACD_1)


    ;; DISPONIBILIDADE DOS CURSOS
    (course-free LIACD_1 h9) (course-free LIACD_1 h11) (course-free LIACD_1 h14) (course-free LIACD_1 h16) (course-free LIACD_1 h18)
    (course-free LIACD_2 h9) (course-free LIACD_2 h11) (course-free LIACD_2 h14) (course-free LIACD_2 h16) (course-free LIACD_2 h18)
    (course-free LIACD_3 h9) (course-free LIACD_3 h11) (course-free LIACD_3 h14) (course-free LIACD_3 h16) (course-free LIACD_3 h18)
  )



  (:goal
    (and
      (scheduled exame_CRP)
      (scheduled exame_VD)
      (scheduled exame_ECAC)
      (scheduled exame_TIA)
      (scheduled exame_SRSA)
      (scheduled exame_AC)
      (scheduled exame_AMI)
      (scheduled exame_IECD)
      (scheduled exame_POO)
    )
  )
)
