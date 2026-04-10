from typer.testing import CliRunner

from unifi_protect_bridge.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Unofficial CLI scaffold" in result.stdout


def test_doctor() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "UniFi Protect Bridge doctor" in result.stdout
