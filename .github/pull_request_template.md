## What this pak does

<!-- The mod, its original author, and where it comes from. -->

## Checklist

The **Check paks** workflow covers the file rules. Tick the rest after trying
the pak in game with the commands in README.md, "Trying a pak before a pull
request". Delete the weapon section
for fonts, sound packs and other non-weapon paks.

### Pak

- [ ] The name follows `TAG-NAME-AUTHOR.pak` (see README.md).
- [ ] Sounds are `.opus`; no `.wav`, no `.weak`, no unused files.
- [ ] The **Check paks** workflow passes.

### Weapon (see [PORTING.md](../PORTING.md))

- [ ] `cg_viewWeaponSide -1`: the gun, both hands, the sights and the charm
      are mirrored to the left.
- [ ] `cg_weaponCharms 1` and `0`: the charm shows and hides, and swings on
      fire, reload and sprint.
- [ ] `cg_reflexScope 0` to `4`, if the gun has iron sights: the sight model
      swaps and the dot lines up with where bullets land.
      Not applicable (built-in optic): [ ]
- [ ] `cg_pngScope 0` and `1`: aiming uses the 3D sights or the scope image.
- [ ] `cg_debugToolSkinAnchors 1`: the muzzle and case-eject axes sit on the
      gun, and tracers leave from the barrel, hip-firing, aiming and
      left-handed.
- [ ] Hands stay on the gun when idle, sprinting and through the whole
      reload.
- [ ] Another player's shots fade with distance and come from the right
      direction.
