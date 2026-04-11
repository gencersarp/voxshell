# Contributing to VoxShell

Thanks for taking the time to contribute!

## Getting started

```bash
git clone https://github.com/gencersarp/voxshell.git
cd voxshell
pip install -e .
pip install pytest
```

## Running the tests

```bash
pytest tests/ -v
```

All 25 tests should pass before you open a PR.

## What to work on

Check the [open issues](https://github.com/gencersarp/voxshell/issues) or the roadmap in the README. Good first areas:

- **Silence detection** — stop listening when the user stops speaking instead of waiting a fixed duration.
- **New voices** — test and document other [Piper voice models](https://github.com/rhasspy/piper/blob/master/VOICES.md).
- **Shell integration** — helper scripts for `.zshrc` / `.bashrc` aliases.

## Pull request checklist

1. Fork and branch from `master`.
2. Add tests for any new behaviour.
3. Run `pytest tests/ -v` — all green.
4. Open a PR with a short description of *what* and *why*.

## License

By contributing, you agree your code will be released under the [MIT License](LICENSE).
