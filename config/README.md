# Configuration

- `default.yaml`: shared baseline committed to Git.
- `local.example.yaml`: copy to ignored `local.yaml` for per-machine overrides.
- `docker.yaml`: host-Ollama URL used from Docker.
- `colab.yaml`: Colab runtime overrides.
- `test.yaml`: tiny deterministic fixture configuration.

Never commit API keys, machine-specific absolute paths, or personal model settings. Supported
environment variables are documented in `.env.example` and override YAML model settings.
