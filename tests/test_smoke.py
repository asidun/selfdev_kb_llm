from typer.testing import CliRunner

from kb.cli.main import app

runner = CliRunner()


def test_cli_help_boots():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "query" in result.stdout
    assert "reindex" in result.stdout


def test_query_markdown_mode_on_missing_notes_root(tmp_path, monkeypatch):
    monkeypatch.setenv("KB_NOTES_ROOT", str(tmp_path / "does-not-exist"))
    result = runner.invoke(app, ["query", "anything"])
    assert result.exit_code == 0
    assert "does not exist" in result.stdout
