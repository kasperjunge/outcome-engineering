# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and this project uses semantic versioning.

## [Unreleased]

## [0.1.1] - 2026-06-29

### Added

- Added GitHub Actions checks for tests, Ruff linting, ty type checking, and package builds.
- Added a tag-driven PyPI publish workflow that builds from `v*` tags, verifies the tag matches `pyproject.toml`, publishes through trusted publishing, and creates a GitHub Release from the changelog.
- Added the `oe-release` bundled skill for preparing, tagging, publishing, monitoring, and recovering Outcome Engineering releases.
- Added `CHANGELOG.md` as the source for GitHub Release notes.

### Fixed

- Fixed ty findings in the graph server request handler and bundled skill installer.

## [0.1.0] - 2026-06-29

### Added

- Initial Outcome Engineering CLI for validating, inspecting, serving, and editing repo-native product graphs.
