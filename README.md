# <img src='icon.png' card_color='#8BC34A' width='50' height='50' style='vertical-align:bottom'/> Fart

Makes your OpenVoiceOS assistant fart - on request, or quietly at random
until someone begs it to stop. Ask it who did it, and it will own up if it
really was guilty... or blame the dog.

A silly skill that should earn a laugh or two (and a few more from the
kids). Fully offline, 12 sounds, 8 languages.

[![Tests](https://github.com/andlo/ovos-skill-fart/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-fart/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-fart.svg)](https://pypi.org/project/ovos-skill-fart/)

## Usage

| Say | What happens |
|---|---|
| "fart" / "let one rip" | Plays a random fart, sometimes followed by a remark |
| "did you fart?" / "what is that smell?" | Confesses if it farted in the last two minutes - otherwise denies everything |
| "fart randomly" / "let one slip now and then" | Random mode: a fart every 5-60 minutes |
| "stop farting" - or just "stop" | Ends random mode |

In Danish: *"prut"*, *"var det dig der pruttede?"*, *"prut tilfældigt"*,
*"stop med at prutte"*.

## Languages

English, Danish, German, Spanish, French, Italian, Dutch and Portuguese.

All language files are generated from one table in
[`tools/gen_locale.py`](tools/gen_locale.py), so every language has the
same intents and dialogs. Native-speaker improvements are very welcome -
edit the table, run `python tools/gen_locale.py`, and open a PR.

## Settings

Optional, in the skill's `settings.json`:

| Key | Default | Meaning |
|---|---|---|
| `comment_chance` | `0.5` | Chance (0-1) of a remark after a fart |
| `random_min_minutes` | `5` | Shortest pause in random mode |
| `random_max_minutes` | `60` | Longest pause in random mode |
| `confess_window_sec` | `120` | How long after a fart it will own up to it |
| `sounds_dir` | - | Folder with your own `.mp3`/`.wav`/`.ogg`/`.flac` files |

## Install

```bash
pip install ovos-skill-fart
```

## Development

```bash
pip install -e . -r requirements-test.txt
pytest tests/
```

Releases are published to PyPI automatically when a `v*` tag is pushed.

## Credits

- Andreas Lorensen ([@andlo](https://github.com/andlo))
- Based on the original Mycroft farting skill by [@aussieW](https://github.com/aussieW)
- Sounds from [SoundBible.com](https://soundbible.com) - see
  [sounds/ATTRIBUTION.md](sounds/ATTRIBUTION.md)

## License

GPL-3.0-or-later

## Category
**Entertainment**

## Tags
#fun #humor #prank #fart
