# Hacking

Install the linters (once):

```bash
pip3 install -U micropython-unix-stubs --no-user --target ./.typings
pip3 install mypy==1.16.1 ruff==0.12.1
```

Run the linters:

```
ruff check
mypy
```
