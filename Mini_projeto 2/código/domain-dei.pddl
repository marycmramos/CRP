(define (domain exame_scheduling)
  (:requirements :strips :typing)

  (:types
    exame
    curso
    sala
    timeslot
    tamanho
  )

  (:predicates
    ;; Estado dos exames
    (unscheduled ?e - exame)
    (scheduled ?e - exame)
    ;; curso
    (exame-curso ?e - exame ?c - curso)

    ;; Atribuição exame-sala-horário
    (exame-at ?e - exame ?s - sala ?t - timeslot)

    ;; Disponibilidade das salas
    (sala-free ?s - sala ?t - timeslot)

    ;; Capacidades
    (exame-tamanho ?e - exame ?tam - tamanho)
    (sala-tamanho ?s - sala ?tam - tamanho)

    ;; Impede os estudantes de uma ano terem 2 exames ao mesmo tempo
    (course-free ?c - curso ?t - timeslot)
  )

  (:action schedule-exame
    :parameters (?e - exame ?s - sala ?t - timeslot ?tam - tamanho ?c - curso)
    :precondition (and
      (unscheduled ?e)
      (sala-free ?s ?t)
      (exame-tamanho ?e ?tam)
      (sala-tamanho ?s ?tam)
      (exame-curso ?e ?c)
      (course-free ?c ?t)
    )
    :effect (and
      (not (unscheduled ?e))
      (scheduled ?e)
      (exame-at ?e ?s ?t)
      (not (sala-free ?s ?t))
      (not (course-free ?c ?t))
    )
  )
)