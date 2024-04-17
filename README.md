# smithed-python
The python package for all things Smithed. Includes weld, cli, and libraries (via [`smithed-libraries`](https://github.com/Smithed-MC/Libraries)).

## Weld
> The fastest pack merger of the west 🚅, build on beet technologies™

- [Docs](https://wiki.smithed.dev/weld/)

```bash
pip install smithed
```

## Contributing

We use [rye](https://rye-up.com/) to manage this project's dependencies. This will handle every aspect from grabbing the correct python, downloading dependencies, and managing a virtual environment.

To get started, install rye:
- [smithed-python](#smithed-python)
  - [Weld](#weld)
  - [Contributing](#contributing)
    - [MacOS and Linux](#macos-and-linux)
    - [Windows](#windows)
  - [Developer Setup](#developer-setup)

### MacOS and Linux

```bash
curl -sSf https://rye-up.com/get | bash
```

### Windows

Check the guide [here](https://rye-up.com/guide/installation/#installing-rye) for an in-depth explanation.

## Developer Setup

Once installed, you can sync the project to generate a virtual environment and you'll be set!

```bash
git clone https://github.com/Smithed-MC/smithed-python
cd smithed-python
rye sync
```
