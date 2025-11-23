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

> [!NOTE]
>
> The following commands require the Unix port of `micropython`. The simplest way is to create a container:
> ```bash
> podman run --platform linux/amd64 --rm -it -v "$PWD":/remote -w /remote micropython/unix bash
> ```
> This mounts the source to `/remote`. The `micropython` executable should be in the `PATH`.

Run the example:

```bash
micropython -m examples.roses_are_red # see examples/ for more examples
```
