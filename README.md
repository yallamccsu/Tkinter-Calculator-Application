# Tkinter Calculator Application

A Python desktop calculator application built with Tkinter. Features a 
fully event-driven button grid, a sanitized expression evaluation pipeline, 
and a structured component architecture separating input, logic, and rendering.

## Features

- Full arithmetic support including addition, subtraction, multiplication, and division
- Expression sanitized through a regex pipeline before evaluation
- Validates balanced expressions and catches division by zero before processing
- Token-based button classification drives color coding and routing automatically
- Reset button clears both the display and internal expression buffer
- Input validation rejects malformed expressions with a clean error state

## How to Run

```bash
python Calculator_Program.py
```

No external dependencies. Requires Python 3 with Tkinter, which is 
included in all standard Python installations.

## Technical Highlights

- `TokenType` enum classifies every button and drives the dispatch table
- `ButtonFactory` builds all widgets from a centralized schema
- `ExpressionEngine` manages the input buffer, evaluation, and session history
- Regex sanitization pipeline strips unsafe characters before `eval` is called
- `_resolve_command` dispatch table routes all button presses by token type
- Rendering and logic fully separated for clean, independently testable architecture

## Tech Stack

Python 3 | Tkinter | dataclasses | enums | functools | re
