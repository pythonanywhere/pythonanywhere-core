from email.parser import BytesParser
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

from packaging.requirements import Requirement
import pytest

from pythonanywhere_core import __version__

try:
    import tomllib
except ImportError:
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def manifest():
    return tomllib.loads((ROOT / "pyproject.toml").read_text())


@pytest.fixture(scope="module")
def distributions(tmp_path_factory):
    output = tmp_path_factory.mktemp("distributions")
    subprocess.run(
        ["uv", "build", "--python", sys.executable, "--no-build-logs", "--out-dir", str(output), str(ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    return output


def test_build_uses_setuptools(manifest):
    assert manifest["build-system"]["build-backend"] == "setuptools.build_meta"
    assert manifest["tool"]["setuptools"]["packages"] == ["pythonanywhere_core"]


def test_uv_replaces_poetry_configuration():
    assert (ROOT / "uv.lock").is_file()
    assert not (ROOT / "poetry.lock").exists()
    assert not (ROOT / "poetry.toml").exists()


def test_package_version_matches_imported_version(manifest):
    assert manifest["project"]["version"] == __version__


def test_runtime_dependencies_preserve_supported_versions(manifest):
    requirements = {
        requirement.name: requirement
        for value in manifest["project"]["dependencies"]
        for requirement in [Requirement(value)]
    }
    assert set(requirements) == {"python-dateutil", "requests", "typing_extensions"}
    assert "2.9.0.post0" in requirements["python-dateutil"].specifier
    assert "3.0.0" not in requirements["python-dateutil"].specifier
    assert "2.34.2" in requirements["requests"].specifier
    assert "3.0.0" not in requirements["requests"].specifier
    assert "4.16.0" in requirements["typing_extensions"].specifier
    assert "5.0.0" not in requirements["typing_extensions"].specifier


def test_wheel_preserves_runtime_modules_and_metadata(distributions, manifest):
    wheel = next(distributions.glob("*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        modules = {name for name in archive.namelist() if name.startswith("pythonanywhere_core/")}
        expected = {path.relative_to(ROOT).as_posix() for path in (ROOT / "pythonanywhere_core").glob("*.py")}
        assert modules == expected
        for name in modules:
            assert archive.read(name) == (ROOT / name).read_bytes()
        assert not any(name.startswith(("tests/", "docs/")) for name in archive.namelist())
        metadata_path = next(name for name in archive.namelist() if name.endswith("/METADATA"))
        metadata = BytesParser().parsebytes(archive.read(metadata_path))
        assert metadata["Name"] == manifest["project"]["name"]
        assert metadata["Version"] == manifest["project"]["version"]
        assert metadata["License-Expression"] == "MIT"
        runtime = {
            str(Requirement(value)) for value in metadata.get_all("Requires-Dist") if Requirement(value).marker is None
        }
        assert runtime == {str(Requirement(value)) for value in manifest["project"]["dependencies"]}
        assert set(metadata.get_all("Provides-Extra")) == {"test", "docs"}
        license_path = next(name for name in archive.namelist() if name.endswith("/licenses/LICENSE"))
        assert archive.read(license_path) == (ROOT / "LICENSE").read_bytes()


def test_source_archive_contains_complete_test_suite(distributions):
    with tarfile.open(next(distributions.glob("*.tar.gz"))) as archive:
        paths = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        expected = {path.relative_to(ROOT).as_posix() for path in (ROOT / "tests").glob("*.py")}
        assert expected <= paths
        assert {
            "pyproject.toml",
            "uv.lock",
            "README.rst",
            "LICENSE",
            ".github/workflows/test.yml",
            ".github/workflows/release.yml",
        } <= paths


def test_source_archive_builds_the_same_runtime_wheel(distributions, tmp_path):
    source = next(distributions.glob("*.tar.gz"))
    subprocess.run(
        [
            "uv",
            "build",
            "--python",
            sys.executable,
            "--wheel",
            "--no-build-logs",
            "--out-dir",
            str(tmp_path),
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    with zipfile.ZipFile(next(distributions.glob("*.whl"))) as original:
        with zipfile.ZipFile(next(tmp_path.glob("*.whl"))) as rebuilt:
            for name in original.namelist():
                if name.startswith("pythonanywhere_core/") or name.endswith("/METADATA"):
                    assert original.read(name) == rebuilt.read(name)


def test_wheel_imports_from_installation_outside_checkout(distributions, tmp_path, manifest):
    target = tmp_path / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
            "--target",
            str(target),
            str(next(distributions.glob("*.whl"))),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(target)!r}); "
        "from pathlib import Path; "
        "import pythonanywhere_core; "
        "from pythonanywhere_core.exceptions import SlowStartupException; "
        "from pythonanywhere_core.webapp import Webapp; "
        f"assert Path(pythonanywhere_core.__file__).resolve().is_relative_to(Path({str(target)!r})); "
        f"assert pythonanywhere_core.__version__ == {manifest['project']['version']!r}; "
        "assert 'startup could not be confirmed' in str(SlowStartupException())"
    )
    subprocess.run([sys.executable, "-I", "-c", code], cwd=tmp_path, check=True, capture_output=True, text=True)


def test_development_commands_and_workflows_use_uv():
    paths = [ROOT / "README.rst", ROOT / "docs/index.rst"]
    paths.extend((ROOT / ".github/workflows").glob("*.yml"))
    for path in paths:
        assert "poetry" not in path.read_text().lower(), path
