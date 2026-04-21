"""CurrencyModel — data, network, and domain logic. No UI dependencies."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

_API_BASE = "https://open.er-api.com/v6/latest"


def _load_currencies() -> tuple[list[tuple[str, str]], str]:
    """Locate and parse currencies.yaml, searching next to the executable first.

    Supports two sections:
      major_currencies — appear first, in YAML order
      currencies       — appended after, sorted alphabetically by name
    Also reads the optional `default` key for the default From currency.
    """
    candidates = [
        Path(sys.argv[0]).parent / "currencies.yaml",  # compiled: next to binary
        Path(__file__).parent / "currencies.yaml",     # dev: next to source
        Path.cwd() / "currencies.yaml",
    ]
    for path in candidates:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            majors = list((data.get("major_currencies") or {}).items())
            rest   = sorted(
                (data.get("currencies") or {}).items(),
                key=lambda kv: kv[1],
            )
            currencies = majors + rest
            default = str(data.get("default", currencies[0][0])).upper()
            return currencies, default
    raise FileNotFoundError(
        "currencies.yaml not found. Expected it next to the application executable."
    )


CURRENCIES: list[tuple[str, str]]
DEFAULT_CURRENCY: str
CURRENCIES, DEFAULT_CURRENCY = _load_currencies()


class ConversionResult:
    __slots__ = ("code", "name", "rate", "converted", "inverse")

    def __init__(
        self,
        code: str,
        name: str,
        rate: float,
        converted: float,
        inverse: float,
    ) -> None:
        self.code = code
        self.name = name
        self.rate = rate
        self.converted = converted
        self.inverse = inverse


class CurrencyModel(QObject):
    rates_ready = Signal(str, float, list)   # base, amount, list[ConversionResult]
    fetch_error = Signal(str)
    loading_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._net = QNetworkAccessManager(self)
        self._net.finished.connect(self._on_reply)
        self._pending_base = ""
        self._pending_amount = 0.0
        self._pending_targets: list[str] = []
        self._name_map: dict[str, str] = {code: name for code, name in CURRENCIES}

    @property
    def currencies(self) -> list[tuple[str, str]]:
        return CURRENCIES

    def fetch(self, base: str, amount: float, targets: list[str]) -> None:
        self._pending_base = base
        self._pending_amount = amount
        self._pending_targets = list(targets)
        self.loading_changed.emit(True)
        self._net.get(QNetworkRequest(QUrl(f"{_API_BASE}/{base}")))

    def _on_reply(self, reply: QNetworkReply) -> None:
        self.loading_changed.emit(False)

        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.fetch_error.emit(reply.errorString())
            reply.deleteLater()
            return

        try:
            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
        except Exception as exc:
            self.fetch_error.emit(f"Parse error: {exc}")
            reply.deleteLater()
            return
        finally:
            reply.deleteLater()

        if payload.get("result") != "success":
            self.fetch_error.emit("API returned a failure response.")
            return

        all_rates = payload.get("rates", {})
        results: list[ConversionResult] = [
            ConversionResult(
                code=code,
                name=self._name_map.get(code, code),
                rate=(r := all_rates[code]),
                converted=r * self._pending_amount,
                inverse=1.0 / r if r else 0.0,
            )
            for code in self._pending_targets
            if code in all_rates
        ]
        self.rates_ready.emit(self._pending_base, self._pending_amount, results)
