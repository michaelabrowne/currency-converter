# Currency Converter

A modern desktop currency converter built with PySide6, using real-time exchange rates from [open.er-api.com](https://open.er-api.com).

## Features

- 16 currencies including USD, EUR, GBP, JPY, VND, SGD, HKD, THB and more
- Live exchange rates fetched on demand
- Forward and inverse rates displayed per result
- Resizable split-pane layout
- Dark theme

## Install

Download the latest release for your platform from the [Releases](../../releases) page:

| Platform | File |
|----------|------|
| macOS | `CurrencyConverter-macOS-vX.X.X.dmg` |
| Windows | `CurrencyConverter-Windows-vX.X.X.zip` |

**macOS:** Open the `.dmg`, drag the app to Applications. On first launch right-click → Open to bypass the unidentified developer warning (app is not yet code-signed).

**Windows:** Extract the `.zip` and run `CurrencyConverter.exe` inside the folder. Windows SmartScreen may warn on first run — click "More info" → "Run anyway".

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/michaelabrowne/currency-converter.git
cd currency-converter
uv sync
uv run python main.py
```

## Release a new version

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build for macOS and Windows automatically and attach the binaries to a new Release.

## Architecture

MVC pattern across four modules:

| File | Role |
|------|------|
| `model.py` | Exchange rate fetching and data (`QNetworkAccessManager`) |
| `view.py` | All widgets and layout (`QMainWindow`) |
| `controller.py` | Wires model signals to view |
| `main.py` | Entry point |
