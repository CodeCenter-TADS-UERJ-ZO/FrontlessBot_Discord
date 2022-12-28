# Frontless Bot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Configurar o ambiente de desenvolvimento

installe o virtualenv e inicialize o venv:

```plaintext
python3.11 -m pip install virtualenv
python3.11 -m virtualenv .venv
```

depois, ative usando:

- `source .venv/bin/active` para sistemas UNIX.
- `source .venv/bin/active.bat` para Windows via CMD.

deve aparencer `(.venv)` no prompt do seu shell.

após isso instale o `requirements.txt` usando `python3.11 -m pip install -U requirements.txt`.

e instale o `pre-commit` com `pre-commit install`.

eu recomendo executar o black na pasta `src` sempre que for executar, assim você já formata e executa, e para fins de legibilidade costumo adicionar um `clear` no início:

- Windows: `cls && python3.11 -m black ./src/ && python3.11 ./src/app.py`
- UNIX: `clear && python3.11 -m black ./src/ && python3.11 ./src/app.py`
