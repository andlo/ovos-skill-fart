"""Every language must ship the same set of resource files, none empty,
and every dialog/intent the code references must exist."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"
LANGS = sorted(p.name for p in LOCALE.iterdir() if p.is_dir())
EXPECTED_LANGS = {"en-us", "da-dk", "de-de", "es-es", "fr-fr", "it-it", "nl-nl", "pt-pt"}


def _files(lang):
    return {p.name for p in (LOCALE / lang).iterdir()}


def test_expected_languages_present():
    assert set(LANGS) == EXPECTED_LANGS


@pytest.mark.parametrize("lang", LANGS)
def test_same_files_as_english(lang):
    assert _files(lang) == _files("en-us")


@pytest.mark.parametrize("lang", LANGS)
def test_no_empty_resource_files(lang):
    for f in (LOCALE / lang).iterdir():
        if f.suffix in (".intent", ".dialog"):
            lines = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
            assert lines, f"{lang}/{f.name} is empty"


@pytest.mark.parametrize("lang", LANGS)
def test_skill_json_valid(lang):
    data = json.loads((LOCALE / lang / "skill.json").read_text(encoding="utf-8"))
    assert data["skill_id"] == "ovos-skill-fart.andlo"
    assert data["examples"] and data["name"]


def test_code_references_existing_resources():
    code = (ROOT / "__init__.py").read_text(encoding="utf-8")
    dialogs = set(re.findall(r'speak_dialog\(\s*"([a-z_]+)"', code))
    dialogs |= set(re.findall(r'"(confess|deny)"', code))
    intents = set(re.findall(r'intent_handler\("([a-z_]+\.intent)"\)', code))
    en = _files("en-us")
    for d in dialogs:
        assert f"{d}.dialog" in en, d
    for i in intents:
        assert i in en, i
