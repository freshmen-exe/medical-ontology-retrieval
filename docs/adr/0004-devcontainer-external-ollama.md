# ADR 0004: Dev Container for Python, External Ollama for Models

- Status: Accepted
- Date: 2026-07-12

## Decision

Use a Docker/VS Code Dev Container to standardize Python development. Run Ollama on the host or Google Colab rather than making it a required service inside the container.

## Rationale

The team needs consistent Python tooling, while GPU drivers and Ollama behavior vary across Windows, Linux, Docker, and Colab. Separating these concerns reduces environment failures.
