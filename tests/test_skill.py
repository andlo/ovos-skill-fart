"""Behaviour tests for the fart skill."""
import time
from pathlib import Path
from unittest.mock import MagicMock

import fart_skill


def test_builtin_sounds_are_found(skill):
    assert len(skill.sounds) == 12
    assert all(Path(s).is_file() for s in skill.sounds)


def test_custom_sounds_dir_used_when_it_has_sounds(skill, tmp_path):
    (tmp_path / "mine.ogg").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("ignore me")
    skill._settings["sounds_dir"] = str(tmp_path)
    assert skill._load_sounds() == [str(tmp_path / "mine.ogg")]


def test_empty_custom_sounds_dir_falls_back_to_builtin(skill, tmp_path):
    skill._settings["sounds_dir"] = str(tmp_path)
    assert len(skill._load_sounds()) == 12


def test_fart_intent_plays_a_sound(skill):
    skill._settings["comment_chance"] = 0
    skill.handle_fart(MagicMock())
    skill.play_audio.assert_called_once()
    assert skill.play_audio.call_args[0][0] in skill.sounds
    skill.speak_dialog.assert_not_called()


def test_fart_comment_always_when_chance_is_one(skill):
    skill._settings["comment_chance"] = 1
    skill.handle_fart(MagicMock())
    skill.speak_dialog.assert_called_once_with("fart_comment")


def test_bad_comment_chance_setting_falls_back_to_default(skill):
    skill._settings["comment_chance"] = "lots"
    assert skill.comment_chance == fart_skill.DEFAULT_COMMENT_CHANCE


def test_no_sounds_says_so(skill):
    skill.sounds = []
    skill.handle_fart(MagicMock())
    skill.play_audio.assert_not_called()
    skill.speak_dialog.assert_called_once_with("no_sounds")


def test_accused_right_after_farting_confesses(skill):
    skill.fart(comment=False)
    skill.handle_accuse(MagicMock())
    skill.speak_dialog.assert_called_once_with("confess")


def test_accused_without_farting_denies(skill):
    skill.handle_accuse(MagicMock())
    skill.speak_dialog.assert_called_once_with("deny")


def test_accused_long_after_farting_denies(skill):
    skill.last_fart_ts = time.time() - 3600
    skill.handle_accuse(MagicMock())
    skill.speak_dialog.assert_called_once_with("deny")


def test_random_start_schedules_within_interval(skill):
    skill._settings.update(random_min_minutes=2, random_max_minutes=3)
    before = time.time()
    skill.handle_random_start(MagicMock())
    assert skill.random_mode
    skill.speak_dialog.assert_called_once_with("random_started")
    when = skill.schedule_event.call_args[0][1]
    assert before + 120 <= when <= time.time() + 180
    assert skill.schedule_event.call_args.kwargs["name"] == fart_skill.RANDOM_EVENT_NAME


def test_random_interval_min_greater_than_max_is_clamped(skill):
    skill._settings.update(random_min_minutes=10, random_max_minutes=2)
    assert skill.random_interval_seconds == (600, 600)


def test_random_start_twice_says_already_running(skill):
    skill.handle_random_start(MagicMock())
    skill.speak_dialog.reset_mock()
    skill.handle_random_start(MagicMock())
    skill.speak_dialog.assert_called_once_with("random_already_running")


def test_random_event_farts_and_reschedules(skill):
    skill.handle_random_start(MagicMock())
    skill.schedule_event.reset_mock()
    skill._handle_random_fart()
    skill.play_audio.assert_called_once()
    skill.schedule_event.assert_called_once()


def test_random_event_after_stop_does_nothing(skill):
    skill.handle_random_start(MagicMock())
    skill.handle_random_stop(MagicMock())
    skill.schedule_event.reset_mock()
    skill._handle_random_fart()
    skill.play_audio.assert_not_called()
    skill.schedule_event.assert_not_called()


def test_random_stop_when_running(skill):
    skill.handle_random_start(MagicMock())
    skill.speak_dialog.reset_mock()
    skill.handle_random_stop(MagicMock())
    assert not skill.random_mode
    skill.cancel_scheduled_event.assert_called_with(fart_skill.RANDOM_EVENT_NAME)
    skill.speak_dialog.assert_called_once_with("random_stopped")


def test_random_stop_when_not_running(skill):
    skill.handle_random_stop(MagicMock())
    skill.speak_dialog.assert_called_once_with("random_not_running")


def test_global_stop_only_claims_while_random_mode(skill):
    assert skill.can_stop(MagicMock()) is False
    skill.handle_random_start(MagicMock())
    assert skill.can_stop(MagicMock()) is True
    skill.stop()
    assert not skill.random_mode
    assert skill.can_stop(MagicMock()) is False
