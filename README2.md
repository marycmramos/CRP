# Intelligent University Scheduling using Planning and Ontologies

An Artificial Intelligence project that combines Knowledge Representation, Ontologies and Automated Planning to solve university resource management and exam scheduling problems.

## Overview

This project explores symbolic AI techniques for managing academic resources and automatically generating valid exam schedules.

Two complementary approaches were developed:

- Ontology-based room management using OWL
- Automated planning using PDDL and AI planners

## Room Management Ontology

A university ontology was developed to represent:

- Rooms
- Students
- Teachers
- Courses
- Activities
- Equipment
- Bookings

The ontology supports reasoning over:

- Room capacities
- Equipment requirements
- Activity scheduling
- Resource allocation

## Automated Exam Scheduling

Exam scheduling was modeled as a planning problem using PDDL.

The planner automatically assigns:

- Exams
- Rooms
- Time slots

while respecting constraints such as:

- Room availability
- Room capacity
- Course conflicts
- Student overlap prevention

## Planning Model

### Domain

The planning domain defines:

- Exams
- Rooms
- Time slots
- Course constraints
- Scheduling actions

### Problem Instance

A realistic DEI examination schedule was modeled with:

- Multiple courses
- Different room capacities
- Availability constraints
- Conflict prevention rules

## Technologies

- Python
- OWLReady2
- Ontologies (OWL)
- PDDL
- Unified Planning
- Pyperplan

## Project Structure

```text
código/
│
├── management.py
├── unified-dei.py
├── domain-dei.pddl
└── problem-dei.pddl
```

## AI Topics Explored

- Knowledge Representation
- Ontologies
- Automated Planning
- Resource Scheduling
- Constraint Satisfaction
- Symbolic Artificial Intelligence

## Results

The system successfully generates valid exam schedules while satisfying resource and conflict constraints, demonstrating the application of symbolic AI techniques to real-world scheduling problems.

## Authors

Developed as part of the Artificial Intelligence curriculum at the University of Coimbra.
