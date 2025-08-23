from __future__ import annotations

from pathlib import Path

import aerolopa_crawler.cli as cli


class DummyHttpClient:
    def __init__(self, *args, **kwargs):  # noqa: D401, ANN001 - test double signature
        pass

    def get_text(self, url: str, headers=None) -> str:  # noqa: ARG002 - parity
        return "<html><title>CLI Test</title><body>ok</body></html>"


def test_cli_main_smoke(tmp_path: Path, monkeypatch):
    # Replace real HttpClient with dummy to avoid network
    monkeypatch.setattr(cli, "HttpClient", DummyHttpClient)

    outdir = tmp_path / "out"
    rc = cli.main(["--url", "https://example.invalid/", "--output-dir", str(outdir), "-v"])
    assert rc == 0
    assert (outdir / "results.jsonl").exists()

