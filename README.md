# zerospades-paks

Official mod paks for ZeroSpades. Each `.pak` is a self-contained mod that the
game downloads and mounts as an overlay.

To install: open the main menu in ZeroSpades, go to the Mods tab, and choose
"Download official mods...". Every pak here is fetched into your local `Mods/`
folder. Enable the ones you want; changes take effect on the next launch.

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

## Contact

Trouble finding a mod or installing one? Reach ZeroG on Discord: ZeroG#2020.
