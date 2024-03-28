"""
skill farting-skill
Copyright (C) 2020  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import time
from datetime import datetime, timedelta
from os import listdir, path
from os.path import abspath, dirname, isfile, join, splitext
#from tinytag import TinyTag


from ovos_bus_client.message import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill

#from mycroft import MycroftSkill, intent_file_handler
#from mycroft.skills.audioservice import AudioService


class Farting(OVOSSkill):
    """Make your voice assistant sound smelly. Beware...you might laught"""

    @property
    def sounds_dir(self) -> str:
        """Path to the sounds directory."""
        default = join(dirname(__file__), "sounds")
        if not self.settings.get("sounds_dir"):
            self.sounds_dir = default
        return self.settings.get("sounds_dir", default)

    @sounds_dir.setter
    def sounds_dir(self, value) -> None:
        """Setter for sounds_dir property."""
        self.settings["sounds_dir"] = value

#    def initialize(self):
#        # Search the sounds directory for sound files and load into a list.
#        valid_codecs = ['.mp3']
#        self.path_to_sound_files = path.join(abspath(dirname(__file__)), 'sounds')
#        self.sound_files = [f for f in listdir(self.path_to_sound_files) if splitext(f)[1] in valid_codecs]
#        self.audio_service = AudioService(self.bus)
#        self.random_farting = False  # flag to indicate whether random farting mode is active
        self.counter = 0  # variable to increment to make the scheduled event unique

    def initialize(self) -> None:
        """Initialize the skill."""
        self.random_fart = False
        self.sounds = {"male": [], "female": [], "robot": []}

        # Example adjustment: Verifying sound directories exist before populating `sounds`
        sounds_dir =self.sounds_dir
        if isdir(sounds_dir):  # Ensure the directory exists
            self.sounds = [
                join(sounds_dir, sound)
                for sound in listdir(sounds_dir)
                if sound.endswith((".wav", ".mp3"))
            ]
        else:
            self.log.warning("Sounds directory does not exist: %s", sounds_dir)

        # stop farts for speech execution
        self.add_event("speak", self.stop)

        self.add_event("skill-fart.openvoiceos.home", self.handle_homescreen)

    def handle_homescreen(self, message: Message) -> None:  # noqa
        """Handle the homescreen event."""
        self.fart()

    def fart(self):
        """Make the voice assistant fart."""
        sound = random.choice(self.sounds)

        #self.gui.clear()
        #pic = random.randint(0, 3)
        #self.gui.show_image(join(dirname(__file__), "ui", "images", str(pic) + ".jpg"))
        #self.play_audio(sound)
        #self.gui.clear()

#    def handle_fart_event(self, message):
#        # create a scheduled event to fart at a random interval between 1 minute and half an hour
#        self.log.info("Handling fart event")
#        if not self.random_farting:
#            return
#        self.cancel_scheduled_event('randon_fart'+str(self.counter))
#        self.counter += 1
#        self.schedule_event(self.handle_fart_event, datetime.now() 
#                            + timedelta(seconds=random.randrange(60, 1800)),
#                            name='random_fart'+str(self.counter))
#        self.fart_and_comment()


    @intent_file_handler('accuse.intent')
    def handle_accuse_intent(self, message):
        # make a comment when accused of farting
        self.speak_dialog('apologise')

    @intent_handler("Random.intent")
    def handle_random_intent(self, message: Message) -> None:  # noqa
        """Initiate random farting."""
        self.log.info("Farting skill: Triggering random farting")
        self.random_farting = True
        self.handle_fart_event(message)

#    @intent_file_handler('random.intent')
#    def handle_random_intent(self, message):
#        # initiate random farting
#        self.log.info("Triggering random farting")
#        self.speak_dialog('random_farting')
#        self.random_farting = True
#        self.schedule_event(self.handle_fart_event, datetime.now()
#                            + timedelta(seconds=random.randrange(30, 60)),
#                            name='random_fart'+str(self.counter))
    @intent_handler(IntentBuilder("StopFarting").require("Stop").require("Fart"))
    def halt_laughing(self, message: Message) -> None:
        """Stop the random farting."""
        self.log.info("Farting skill: Stopping")
        # if in random fart mode, cancel the scheduled event
        if self.random_fart: 
            self.log.info("Farting skill: Stopping random fart event")
            self.random_fart = False
            self.cancel_scheduled_event("random_fart")
            self.speak_dialog("cancel")
        else:
            self.speak_dialog("cancel_fail")

    def handle_laugh_event(self, message: Optional[Message]) -> None:
        """Create a scheduled event for random farting."""
        if not self.random_fart:
            return
        self.log.info("Farting skill: Handling fart event")
        self.laugh()
        self.cancel_scheduled_event("random_fart")
        self.schedule_event(
            self.handle_fart_event,
            datetime.now() + timedelta(seconds=random.randrange(200, 10800)),
            name="random_fart",
        )



#    @intent_file_handler('farting.intent')
#    def fart_and_comment(self):
#        # play a randomly selected fart noise and make a comment
#        self.log.info("Fart and comment")
#        sound_file = path.join(self.path_to_sound_files,
#                               random.choice(self.sound_files))
#        sound_url = 'file://' + path.join(self.path_to_sound_files,
#                                          random.choice(self.sound_files))
#        tag = TinyTag.get(sound_file)
#        self.audio_service.play(tracks=sound_url)
#        self.log.info("Fart duration " + str(int(tag.duration)))
#        time.sleep(int(tag.duration))
#        self.speak_dialog('noise')

#    @intent_file_handler('halt_farting.intent')
#    def halt_farting(self, message):
#        self.log.info("Stopping")
#        # if in random fart mode, cancel the scheduled event
#        if self.random_farting:
#            self.log.info("Stopping random farting event")
#            self.speak_dialog('cancel')
#            self.random_farting = False
#            self.cancel_scheduled_event('random_fart'+str(self.counter))

