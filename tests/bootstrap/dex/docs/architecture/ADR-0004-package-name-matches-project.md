# ADR-0004: Python Package Name Matches Project Name

Date: 2026-06-18
Status: Accepted

## Context

The initial scaffold placed source files in a directory named `src/` — a common
Python layout convention. The pyproject.toml entry point was `src.main:cli` and
setuptools was configured with `include = ["src*"]`.

When installed in editable mode (`pip install -e .`), setuptools registers a
`sys.meta_path` finder that maps the literal string `"src"` to the absolute path of
the source directory. This works only as long as the finder is active in the current
Python session.

Running `dex` from any directory other than the project root produced:

```
ModuleNotFoundError: No module named 'src'
```

Root cause: `src` is a generic name with no uniqueness guarantee. If the editable
finder registration is absent or stale (e.g. after `git mv`, in a fresh shell, or
when Python resolves imports before the finder activates), Python falls back to
scanning `sys.path` for a directory literally named `src`, finds none, and raises
`ModuleNotFoundError`. Any other project installed in the same environment that also
uses `src/` as its source directory would shadow or conflict.

## Decision

**The Python package directory must be named after the project: `dex/`.**

- Source moved from `src/` to `dex/` via `git mv`
- pyproject.toml entry point: `dex.main:cli`
- setuptools package discovery: `include = ["dex*"]`

## Consequences

- `dex` works from any working directory — the module name is unique and unambiguous
- No conflict risk with other packages in the same virtualenv
- Import paths (`from dex.main import cli`) are self-documenting
- Applied as: `git mv src dex` + pyproject.toml update + `pip install -e .` reinstall
