"""
ovos-skill-fart - make your voice assistant a little less well-mannered.
Copyright (C) 2020-2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Features
--------
* "fart"                -> plays a random fart, sometimes followed by a comment
* "did you fart?"       -> confesses if it farted recently, otherwise blames
                           someone else
* "fart randomly"       -> keeps farting at random intervals until told to stop
* "stop farting"/"stop" -> ends random mode

Settings (settings.json)
------------------------
* comment_chance      float 0..1, chance of a comment after a fart (default 0.5)
* random_min_minutes  shortest pause in random mode (default 5)
* random_max_minutes  longest pause in random mode (default 60)
* confess_window_sec  how long after a fart it will own up to it (default 120)
* sounds_dir          optional folder with your own .mp3/.wav/.ogg files
"""

import random
import time
from os import listdir
from os.path import dirname, isdir, join
from typing import List, Optional

from ovos_bus_client.message import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

SOUND_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac")
RANDOM_EVENT_NAME = "random_fart"

DEFAULT_COMMENT_CHANCE = 0.5
DEFAULT_RANDOM_MIN_MINUTES = 5
DEFAULT_RANDOM_MAX_MINUTES = 60
DEFAULT_CONFESS_WINDOW_SEC = 120


def find_sounds(folder: str) -> List[str]:
    """Return all playable sound files in ``folder`` (sorted, full paths)."""
    if not folder or not isdir(folder):
        return []
    return sorted(
        join(folder, f) for f in listdir(folder)
        if f.lower().endswith(SOUND_EXTENSIONS)
    )


class FartSkill(OVOSSkill):
    """Fart on request, at random, and deny everything."""

    def initialize(self):
        self.random_mode = False
        self.last_fart_ts: Optional[float] = None
        self.sounds = self._load_sounds()
        if not self.sounds:
            self.log.error("No fart sounds found - the skill will stay silent")

    # ------------------------------------------------------------------
    # settings helpers
    def _setting_float(self, key: str, default: float) -> float:
        try:
            return float(self.settings.get(key, default))
        except (TypeError, ValueError):
            return default

    @property
    def comment_chance(self) -> float:
        return min(1.0, max(0.0, self._setting_float("comment_chance", DEFAULT_COMMENT_CHANCE)))

    @property
    def random_interval_seconds(self) -> tuple:
        lo = max(1.0, self._setting_float("random_min_minutes", DEFAULT_RANDOM_MIN_MINUTES))
        hi = max(lo, self._setting_float("random_max_minutes", DEFAULT_RANDOM_MAX_MINUTES))
        return lo * 60, hi * 60

    @property
    def confess_window(self) -> float:
        return self._setting_float("confess_window_sec", DEFAULT_CONFESS_WINDOW_SEC)

    def _load_sounds(self) -> List[str]:
        custom = self.settings.get("sounds_dir")
        if custom:
            sounds = find_sounds(custom)
            if sounds:
                return sounds
            self.log.warning(f"sounds_dir '{custom}' has no sound files - using the built-in ones")
        return find_sounds(join(dirname(__file__), "sounds"))

    # ------------------------------------------------------------------
    # core behaviour
    def fart(self, comment: Optional[bool] = None) -> bool:
        """Play a random fart. Optionally follow it with a remark.

        Audio is queued with TTS, so the comment is spoken after the sound.
        Returns False if there is nothing to play.
        """
        if not self.sounds:
            return False
        self.play_audio(random.choice(self.sounds))
        self.last_fart_ts = time.time()
        if comment is None:
            comment = random.random() < self.comment_chance
        if comment:
            self.speak_dialog("fart_comment")
        return True

    def recently_farted(self) -> bool:
        return (self.last_fart_ts is not None
                and time.time() - self.last_fart_ts <= self.confess_window)

    def _schedule_next_random_fart(self):
        lo, hi = self.random_interval_seconds
        self.cancel_scheduled_event(RANDOM_EVENT_NAME)
        self.schedule_event(self._handle_random_fart,
                            time.time() + random.uniform(lo, hi),
                            name=RANDOM_EVENT_NAME)

    def _handle_random_fart(self, message: Optional[Message] = None):
        if not self.random_mode:
            return
        self.fart()
        self._schedule_next_random_fart()

    def _stop_random_mode(self) -> bool:
        """Leave random mode. Returns True if it was active."""
        was_active = self.random_mode
        self.random_mode = False
        self.cancel_scheduled_event(RANDOM_EVENT_NAME)
        return was_active

    # ------------------------------------------------------------------
    # intents
    @intent_handler("fart.intent")
    def handle_fart(self, message: Message):
        if not self.fart():
            self.speak_dialog("no_sounds")

    @intent_handler("accuse.intent")
    def handle_accuse(self, message: Message):
        self.speak_dialog("confess" if self.recently_farted() else "deny")

    @intent_handler("random_start.intent")
    def handle_random_start(self, message: Message):
        if not self.sounds:
            self.speak_dialog("no_sounds")
            return
        if self.random_mode:
            self.speak_dialog("random_already_running")
            return
        self.random_mode = True
        self.speak_dialog("random_started")
        self._schedule_next_random_fart()

    @intent_handler("random_stop.intent")
    def handle_random_stop(self, message: Message):
        if self._stop_random_mode():
            self.speak_dialog("random_stopped")
        else:
            self.speak_dialog("random_not_running")

    # ------------------------------------------------------------------
    # global stop ("stop") ends random mode
    def can_stop(self, message: Message) -> bool:
        return self.random_mode

    def stop(self):
        self._stop_random_mode()

    def shutdown(self):
        self._stop_random_mode()
