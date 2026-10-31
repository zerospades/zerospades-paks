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

Porting a weapon mod from OpenSpades? Read [PORTING.md](PORTING.md) first. It
explains each rule below and how to meet it.

### Rules

Every pak:

- Follows the naming standard above.
- Ships sounds as `.opus`, never `.wav`. Sounds other players hear (the ones
  `ThirdPerson.as` plays) are mono; only `FireStereo` and the local player's
  own sounds may be stereo.
- Contains no `.weak` files, no system files, and no unused file. A file is
  used when its scripts load it, when it replaces a base game file, or when
  ZeroSpades loads its whole folder: fonts directly in `Fonts/`, `.ospfont`
  fonts and their images in `Gfx/Fonts/`, and kill sounds in
  `Sounds/Feedback/Killstreak/`.
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
checks the rules that can be checked without the game, on the paks the pull
request adds or changes. Run it locally with:

    python3 tools/check_paks.py --base <path to zerospades>/Resources YOUR-Pak-.pak

### Trying a pak before a pull request

`--try-mod` mounts one pak on top of the base game without touching your
enabled mods, and `--replay-demo` plays your latest demo, following a player.
The block below opens the game once per setting to check; close the game to
go to the next one, or press Ctrl-C to stop. Run it from the directory that
holds the ZeroSpades app (for a source build, `zerospades/build`), and set
`PAK` to your pak.

The demo shows the gun of the player it follows. If that is not your mod's
weapon class, set `PLAYER` to the id or name of a player who uses it.

```sh
PAK=path/to/YOUR-Pak-.pak
PLAYER=
try() {
  local what=$1; shift
  local args=(); for c in "$@"; do args+=(--override-cvar "$c"); done
  local pl=(); [ -n "$PLAYER" ] && pl=(--player "$PLAYER")
  printf '\n\033[1m▶ %s\033[0m  [%s]\n' "$what" "$*"
  ./bin/ZeroSpades.app/Contents/MacOS/ZeroSpades --try-mod "$PAK" --replay-demo "${pl[@]}" "${args[@]}"
}
try "it loads, and looks and sounds right"
try "left-handed: gun, hands, sights and charm mirrored" cg_viewWeaponSide=-1
try "muzzle and case eject axes on the gun; tracers leave the barrel" cg_debugToolSkinAnchors=1
try "no charm" cg_weaponCharms=0
try "reflex mode 0: iron sights, or the optic's own reticle" cg_reflexScope=0
try "reflex mode 1: 3D dot" cg_reflexScope=1
try "reflex mode 2: 3D reticle" cg_reflexScope=2
try "reflex mode 3: 2D dot" cg_reflexScope=3
try "reflex mode 4: 2D reticle" cg_reflexScope=4
try "png scope: the gun hides at full aim, the scope image shows" cg_pngScope=1
try "true aim down sight: the sight lines up with the crosshair" cg_trueAimDownSight=1
```

On macOS the app is `./bin/ZeroSpades.app/Contents/MacOS/ZeroSpades`; on other
systems use your `zerospades` binary instead. A script error stops the game
with a message naming the file and line, and `SystemMessages.log` has the
details. Then go through the checklist in the pull request template.

## Contact

Trouble finding a mod or installing one? Ask in the [ZeroSpades Discord](https://discord.gg/t64rKedpAu).
