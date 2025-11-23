# Hacking

Install the linters (once):

```bash
pip3 install -U micropython-unix-stubs --no-user --target ./.typings
pip3 install mypy==1.16.1 ruff==0.12.1
```

Run the linters:

```bash
ruff check
mypy
```

Run micropython in a container:

```
podman run --platform linux/amd64 --rm -it -v "$PWD":/remote -w /remote micropython/unix
```

This mounts the source to `/remote` and starts micropython in `/remote`.

Run the example:

```bash
podman run --platform linux/amd64 --rm -it -v "$PWD":/remote -w /remote micropython/unix micropython -m example
```
