from __future__ import annotations

import io

from typing import TYPE_CHECKING
from pathlib import Path


if TYPE_CHECKING:
    from pytest_console_scripts import ScriptRunner

import pytest


@pytest.fixture()
def console_script(tmp_path: Path) -> Path:
    """Python script to use in tests."""
    script = tmp_path / "script.py"
    script.write_text('#!/usr/bin/env python\nprint("foo")')
    return script


@pytest.mark.script_launch_mode("subprocess")
def test_stdin_1234(console_script: Path, script_runner: ScriptRunner) -> None:
    console_script.write_text(
        "#!/usr/bin/env python\nfrom checksum import main\nmain()"
    )
    console_script.chmod(0o755)
    stdin = io.StringIO("1234\n")
    result = script_runner.run(str(console_script), stdin=stdin)
    assert result.success
    assert result.stdout == "1be168ff837f043bde17c0314341c84271047b31  -\n"


@pytest.mark.script_launch_mode("subprocess")
def test_stdin_256(console_script: Path, script_runner: ScriptRunner) -> None:
    console_script.write_text(
        "#!/usr/bin/env python\nfrom checksum import main\nmain()"
    )
    stdin = io.StringIO("1234\n")
    result = script_runner.run([str(console_script), "-a", "256"], stdin=stdin)
    assert result.success
    assert (
        result.stdout[:-4]
        == "a883dafc480d466ee04e0d6da986bd78eb1fdd2178d04693723da3a8f95d42f4"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_stdin_md5(console_script: Path, script_runner: ScriptRunner) -> None:
    console_script.write_text(
        "#!/usr/bin/env python\nfrom checksum import main\nmain()"
    )
    stdin = io.StringIO("1234\n")
    result = script_runner.run([str(console_script), "-a", "md5"], stdin=stdin)
    assert result.success
    assert result.stdout == "e7df7cd2ca07f4f1ab415d457a6e1c13  -\n"


@pytest.mark.script_launch_mode("subprocess")
def test_blocksize_4k(script_runner: ScriptRunner) -> None:
    file = str(Path(__file__).with_name("fixtures") / "random_48.bin")
    result = script_runner.run(["python", "-m", "checksum", "-B", "4096", file])
    assert result.success
    assert result.stdout == "{}  {}\n".format(
        "ff25d384f6035f00f536ae7a2a1cbc553dd50366", file
    )


@pytest.mark.script_launch_mode("subprocess")
def test_check_sha256(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-a", "256", "-c", "sha256.sums"], cwd=fixd
    )
    assert result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_04.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_check_tag(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-c", "tag256.sums"], cwd=fixd
    )
    assert result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_04.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_check_missing(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-c", "missing-160.sums"], cwd=fixd
    )
    assert not result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_04.bin: OK\n"
        "random_05.bin: FAILED open or read\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )
    assert result.stderr == (
        "random_05.bin: No such file or directory\n"
        "1 listed file could not be read\n"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_check_ignore_missing(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        [
            "python",
            "-m",
            "checksum",
            "-c",
            "missing-160.sums",
            "--ignore-missing",
        ],
        cwd=fixd,
    )
    assert result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_04.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )
    assert result.stderr == ""


@pytest.mark.script_launch_mode("subprocess")
def test_check_missing_quiet(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        [
            "python",
            "-m",
            "checksum",
            "-c",
            "missing-160.sums",
            "--quiet",
        ],
        cwd=fixd,
    )
    assert not result.success
    assert result.stdout == ("random_05.bin: FAILED open or read\n")
    assert result.stderr == (
        "random_05.bin: No such file or directory\n"
        "1 listed file could not be read\n"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_check_status(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        [
            "python",
            "-m",
            "checksum",
            "-c",
            "missing-160.sums",
            "--status",
        ],
        cwd=fixd,
    )
    assert not result.success
    assert result.stdout == ("")
    assert result.stderr == ("random_05.bin: No such file or directory\n")


@pytest.mark.script_launch_mode("subprocess")
def test_check_improperly_formatted(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-c", "misformatted-160.sums"], cwd=fixd
    )
    assert result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )
    assert result.stderr == ("1 line is improperly formatted\n")


@pytest.mark.script_launch_mode("subprocess")
def test_check_improperly_formatted_strict(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-c", "misformatted-160.sums", "--strict"],
        cwd=fixd,
    )
    assert not result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )
    assert result.stderr == ("1 line is improperly formatted\n")


@pytest.mark.script_launch_mode("subprocess")
def test_check_improperly_formatted_warn(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "-c", "misformatted-160.sums", "--warn"],
        cwd=fixd,
    )
    assert result.success
    assert result.stdout == (
        "random_01.bin: OK\n"
        "random_08.bin: OK\n"
        "random_16.bin: OK\n"
        "random_48.bin: OK\n"
    )
    assert result.stderr == (
        "misformatted-160.sums: 2: improperly formatted checksum line\n"
        "1 line is improperly formatted\n"
    )


@pytest.mark.script_launch_mode("subprocess")
def test_tag_sha1(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        ["python", "-m", "checksum", "--tag", "random_01.bin", "random_48.bin"],
        cwd=fixd,
    )
    assert result.success
    assert result.stdout == (
        "SHA1 (random_01.bin) = ad911110e3239aedcd8a8dd7d572d0111ee71064\n"
        "SHA1 (random_48.bin) = ff25d384f6035f00f536ae7a2a1cbc553dd50366\n"
    )
    assert result.stderr == ("")


@pytest.mark.script_launch_mode("subprocess")
def test_sha1_zero(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        [
            "python",
            "-m",
            "checksum",
            "--zero",
            "random_01.bin",
            "random_48.bin",
        ],
        cwd=fixd,
    )
    assert result.success
    assert result.stdout == (
        "ad911110e3239aedcd8a8dd7d572d0111ee71064  random_01.bin\x00"
        "ff25d384f6035f00f536ae7a2a1cbc553dd50366  random_48.bin\x00"
    )
    assert result.stderr == ("")


@pytest.mark.script_launch_mode("subprocess")
def test_tag_sha1_zero(script_runner: ScriptRunner) -> None:
    fixd = Path(__file__).with_name("fixtures")
    result = script_runner.run(
        [
            "python",
            "-m",
            "checksum",
            "--tag",
            "--zero",
            "random_01.bin",
            "random_48.bin",
        ],
        cwd=fixd,
    )
    assert result.success
    assert result.stdout == (
        "SHA1 (random_01.bin) = ad911110e3239aedcd8a8dd7d572d0111ee71064\x00"
        "SHA1 (random_48.bin) = ff25d384f6035f00f536ae7a2a1cbc553dd50366\x00"
    )
    assert result.stderr == ("")
