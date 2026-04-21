# Currency Converter

A modern desktop currency converter built with PySide6, using real-time exchange rates from [open.er-api.com](https://open.er-api.com).

## Features

- 37 currencies including all EU non-euro members (CZK, HUF, PLN, RON, SEK, DKK, BGN) and major global currencies
- Editable `currencies.yaml` — add or remove currencies without recompiling
- Live exchange rates fetched on demand
- Forward and inverse rates displayed per result
- Resizable split-pane layout
- Dark theme

## Install — macOS

**Recommended: one-line installer** (handles Gatekeeper automatically)

```bash
curl -fsSL https://raw.githubusercontent.com/michaelabrowne/currency-converter/develop/install.sh | bash
```

This downloads the latest release, installs to `/Applications`, and removes the macOS quarantine flag so the app opens without any security warnings.

<details>
<summary>Manual install (download the DMG yourself)</summary>

1. Download `CurrencyConverter-macOS-*.dmg` from the [Releases](../../releases) page
2. Open the DMG and drag **Currency Converter** to your Applications folder
3. Try to open the app — macOS will block it with a security warning
4. Open **System Settings → Privacy & Security**, scroll to the bottom
5. Click **"Open Anyway"** next to the Currency Converter entry
6. Enter your password if prompted

> The warning appears because the app is not notarised with an Apple Developer certificate.
> The one-line installer above avoids this entirely.

</details>

## Install — Windows

1. Download `CurrencyConverter-Windows-*.zip` from the [Releases](../../releases) page
2. Extract the zip
3. Run `CurrencyConverter.exe` inside the extracted folder
4. If Windows SmartScreen warns you, click **More info → Run anyway**

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/michaelabrowne/currency-converter.git
cd currency-converter
uv sync
uv run python main.py
```

### Adding currencies

Edit `currencies.yaml` — no code changes needed. Valid codes must be supported by [open.er-api.com](https://open.er-api.com/v6/latest/USD). In the compiled app the file sits next to the executable and can be edited with any text editor.

### Release a new version

```bash
git tag v1.x.x
git push origin v1.x.x
```

GitHub Actions builds for macOS and Windows automatically and attaches binaries to a new Release.

### Regenerate icons

```bash
uv run python make_icons.py
```

## Architecture

MVC pattern across four modules:

| File | Role |
|------|------|
| `model.py` | Exchange rate fetching, data, loads `currencies.yaml` |
| `view.py` | All widgets and layout (`QMainWindow`) |
| `controller.py` | Wires model signals to view |
| `main.py` | Entry point |
