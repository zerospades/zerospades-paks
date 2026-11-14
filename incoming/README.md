# Incoming mods — upload folder

Drop your mods here (`.pak`, `.zip`, `.7z`, or unpacked folders — any format
they come in, OpenSpades or otherwise). This folder is the inbox for the
conversion queue.

## What happens to each mod

1. You upload a mod into this folder.
2. It gets converted to ZeroSpades spec, following
   [PORTING.md](../PORTING.md) exactly:
   - scripts rewritten against the stock `BasicViewWeapon` API
     (left-handed mirror, eye-space muzzle/case-eject, hands bound to the
     gun matrix, charms, `cg_reflexScope`, `cg_pngScope`),
   - every sound converted to `.opus` 48 kHz, mono for anything other
     players hear,
   - unused/`old*`/`.weak`/duplicate files removed, paths matched by
     exact case, custom images moved under `Gfx/Weapons/<Mod>/`,
   - packaged as `TAG-NAME-AUTHOR.pak` in the repo root and validated with
     `python3 tools/check_paks.py --base <base list> <pak>` until it reports
     **0 errors**.
3. The converted pak lands in the repository root, ready for the PR.
4. **A mod that cannot be converted is deleted** from this folder — it does
   not ship.

## Notes

- Files dropped here are ignored by git (see `.gitignore` in this folder);
  only this README is tracked. The converted `.pak` files in the repo root
  are the deliverable.
- The original upload is removed once its conversion is done (success or
  delete), so this folder stays empty between batches.
- Tag naming follows the README standard: `TAG-NAME-AUTHOR.pak`, where TAG
  is one of `SEMI`, `SMG`, `SHOTGUN`, `SPADE`, `GRENADE`, `FONT`, `SFX`,
  `VFX`. Tell me the mod name and author if they are not obvious from the
  files.
