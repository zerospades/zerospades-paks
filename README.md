# zerospades-paks

Official mod paks for ZeroSpades. Each `.pak` is a self-contained mod that the
game downloads and mounts as an overlay.

To install: open the main menu in ZeroSpades, go to the Mods tab, and choose
"Download official mods...". Every pak here is fetched into your local `Mods/`
folder. Enable the ones you want; changes take effect on the next launch.

Every change to the paks on `main` is also published as a
[release](https://github.com/zerospades/zerospades-paks/releases) named after
its date, such as `2026.10.31`, with all the paks in one zip.

Most of these mods were not made by the maintainers of this repo. They were
adapted to work on ZeroSpades, with some fixes along the way. Credit stays with
the original authors.

## Naming standard

Every pak follows a three-field pattern, separated by hyphens:

    TAG-NAME-AUTHOR.pak

- **TAG** — what the mod changes (see the list below).
- **NAME** — the mod's name, such as the weapon or font it provides.
- **AUTHOR** — the creator's handle. Leave this field empty when the author is
  unknown, but keep the trailing hyphen, for example `SFX-Killsounds-.pak`.

Each field is a single token: no spaces and no extra hyphens. Join words with
CamelCase, for example `KRISSVector` or `M4Magpul`. All three fields are always
present, so a pak name always contains exactly two hyphens.

The game reads these fields to lay out each mod in a table: a tag icon, the
name, and the author. A file that does not follow the pattern still works, but
is shown by its raw filename instead.

### Tags

Weapon tags show a matching icon in game:

- `SEMI` — semi-automatic rifle
- `SMG` — submachine gun
- `SHOTGUN` — shotgun
- `SPADE` — spade
- `GRENADE` — grenade

Other tags are shown as plain text:

- `FONT` — replacement UI font
- `SFX` — sound effects
- `VFX` — visual effects

## Contributing

Name your pak using the standard above and open a pull request. Keep the mod
self-contained: the folder layout inside the pak mirrors the game's resource
layout, for example `Gfx/Fonts/OpenSans.ttf` to replace the default font, or
`Sounds/...` for audio.

Porting a weapon mod from OpenSpades? Read [PORTING.md](PORTING.md) first. It
explains each rule below and how to meet it.

### Rules

Every pak:

- Follows the naming standard above.
- Ships sounds as `.opus`, never `.wav`. Sounds other players hear (the ones
  `ThirdPerson.as` plays) are mono; only `FireStereo` and the local player's
  own sounds may be stereo.
- Contains no `.weak` files, no system files, and no file that is neither
  loaded by its scripts nor a replacement for a base game file.
- Refers to every file by its exact name, including case.
- Names its own images after the mod, under `Gfx/Weapons/<Mod>/`, rather
  than with generic names such as `Gfx/1.png`.

Every weapon pak also:

- Supports left-handed view (`cg_viewWeaponSide`): the whole view weapon is
  mirrored, including every model, the hands and the sights.
- Draws charms when `cg_weaponCharms` is on.
- Supports reflex sights (`cg_reflexScope`) when the gun has iron sights.
- Returns `MuzzlePosition` and `CaseEjectPosition` in eye space, on the
  model, so tracers and casings leave from the gun.
- Keeps the hands on the gun through every animation.

### Checking a pak

The **Check paks** GitHub Actions workflow runs on every pull request and
checks the rules that can be checked without the game. Run it locally with:

    python3 tools/check_paks.py --base <path to zerospades>/Resources

Then try the pak in game before asking for a review:

    ZeroSpades --try-mod path/to/YOUR-Pak-.pak --replay-demo

and go through the checklist in the pull request template.

## Contact

Trouble finding a mod or installing one? Reach ZeroG on Discord: ZeroG#2020.
