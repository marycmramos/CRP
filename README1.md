# Intelligent Pacman: Knowledge-Based Ghost Agents

A Pacman-inspired environment featuring intelligent ghost agents capable of perception, reasoning and strategic decision-making. The project explores different Artificial Intelligence paradigms, including propositional reasoning, first-order logic and pathfinding algorithms.

## Overview

The objective of this project is to develop intelligent ghost agents that can perceive the environment, maintain internal knowledge and make decisions to capture Pacman.

Three distinct ghost strategies were implemented:

- Propositional Logic Chaser
- Patrol and Interception Agent
- First-Order Logic Strategic Agent

The environment includes randomly generated mazes, pellets, obstacles and real-time interaction.

## Implemented Agents

### PropGhostChaser

A propositional logic-based ghost that:

- Maintains a knowledge base of observed cells
- Detects Pacman using line-of-sight perception
- Stores Pacman's last known position
- Uses BFS pathfinding to chase the target

### PropGhostPatrol

A patrol-based agent that:

- Follows predefined patrol routes
- Switches to interception mode when Pacman is detected
- Uses path planning to reach target locations efficiently

### FOLGhostStrategic

A First-Order Logic inspired agent that:

- Stores facts about the environment
- Infers potential future positions of Pacman
- Predicts movement patterns
- Performs strategic interception

## Features

- Random maze generation
- Real-time gameplay
- Line-of-sight perception
- Knowledge representation
- Strategic reasoning
- BFS pathfinding
- Multi-agent behavior

## Technologies

- Python
- Artificial Intelligence
- Propositional Logic
- First-Order Logic
- Breadth-First Search (BFS)

## Project Structure

```text
código/
│
├── environment.py
├── main.py
├── utils.py
│
└── ghosts/
    ├── ghost_base.py
    ├── ghost1.py
    ├── ghost2.py
    └── ghost3.py
```

## Learning Outcomes

- Knowledge Representation
- Logical Reasoning
- Intelligent Agents
- Search Algorithms
- Multi-Agent Systems

## Authors

Developed as part of the Artificial Intelligence curriculum at the University of Coimbra.
