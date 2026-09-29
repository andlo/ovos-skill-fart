"""Shared pytest fixtures for the fart skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("fart_skill", ROOT / "__init__.py")
_module = importlib.util.module_from_spec(_spec)
sys.modules["fart_skill"] = _module
_spec.loader.exec_module(_module)

FartSkill = _module.FartSkill


@pytest.fixture
def skill():
    """A FartSkill instance without a bus - OVOS plumbing is mocked out."""
    s = FartSkill.__new__(FartSkill)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-fart.andlo"
    s.status = MagicMock()
    s._settings = {}
    type(s).settings = property(lambda self: self._settings)
    s.play_audio = MagicMock()
    s.speak_dialog = MagicMock()
    s.schedule_event = MagicMock()
    s.cancel_scheduled_event = MagicMock()
    s.initialize()
    return s
