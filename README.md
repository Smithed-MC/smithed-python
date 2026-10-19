# smithed-python
The python package for all things Smithed. Includes weld, cli, and libraries (via [`smithed-libraries`](https://github.com/Smithed-MC/Libraries)).

## Weld
> The fastest pack merger of the west 🚅, build on beet technologies™

- [Docs](https://wiki.smithed.dev/weld/)

```bash
pip install smithed
```

## Contributing

We use [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage Python and project dependencies, [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [ty](https://docs.astral.sh/ty/) for type checking.

### Developer Setup

Once installed, you can sync the project to generate a virtual environment and you'll be set!

```bash
git clone https://github.com/Smithed-MC/smithed-python
cd smithed-python
uv sync --locked
```

Add dependencies with `uv add <package>` or `uv add --dev <package>` for development tools. Commit both `pyproject.toml` and `uv.lock` when dependencies change.

Run the same checks used by CI:

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check
uv run --locked pytest -v
```
