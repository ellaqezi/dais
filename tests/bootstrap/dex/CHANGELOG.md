# Changelog

All notable changes to devexnet are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Rename CLI entry point from `devexnet` to `dex` (package: `dex`, repo dir: `devexnet`)

### Added
- Initial project scaffold via DAIS bootstrap
- loom-reed-light spec/tasks structure
- CLAUDE.md project-scoped configuration (dotclaude integration)
- AGENTS.md unified inventory (DAIS agents + loom-reed-light commands)
- CI pipeline: pre-commit + LOOM schema validator + shellcheck
- ADR-0001: stack choices (Python CLI, Click, PyYAML)
- ADR-0003: git worktree strategy
- Security threat model with prompt injection as first-class threat
- FinOps token routing strategy mapping S/M tasks to Haiku/Sonnet
