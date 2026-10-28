# Porting an OpenSpades mod to ZeroSpades

Most weapon mods were written for OpenSpades. They load in ZeroSpades, but a
straight copy breaks things players notice: tracers start in the wrong place,
the gun ignores left-handed mode, charms and reflex sights never show, and
other players' shots can be heard across the whole map.

This guide lists what changes between the two engines and what a pak must do
before it is merged here.

The stock ZeroSpades scripts are the reference. When in doubt, copy the
structure of `Resources/Scripts/Skin/<Weapon>/View.as` from the
[zerospades](https://github.com/zerospades/zerospades) repo and move the mod's
models and offsets into it, rather than patching the OpenSpades script.

## Checklist

A weapon pak is ready when:

- [ ] `View.as` extends `BasicViewWeapon` and its `GetViewWeaponMatrix()`
      ends with the left-handed mirror.
- [ ] `MuzzlePosition` and `CaseEjectPosition` return eye-space positions
      (no `eyeMatrix *`).
- [ ] Hands are computed from the same matrix the gun model is drawn with.
- [ ] Charms are drawn when `cg_weaponCharms` is on.
- [ ] `cg_reflexScope` is honoured if the gun has iron sights.
- [ ] The aim-down-sight overlay respects `cg_pngScope`.
- [ ] Every sound is `.opus`, and every third-person sound is mono.
- [ ] Nothing in the pak is unused: no `.weak` files, no `old*` files, no
      leftover images or models.
- [ ] Every path in the scripts matches the file name in the pak exactly,
      including case.

## Scripts

### View matrix and left-handed mode

ZeroSpades mirrors the view weapon when `cg_viewWeaponSide` is negative. The
mirror happens at the very end of `GetViewWeaponMatrix()`, so everything that
uses that matrix (gun, hands, muzzle, charms) flips together.

If the mod does not override `GetViewWeaponMatrix()`, it inherits this from
`BasicViewWeapon` for free. If it does override it, as most OpenSpades mods
do, add the same lines the stock scripts use:

```as
Matrix4 GetViewWeaponMatrix() {
    Matrix4 mat;

    float weapSide = Clamp(cg_viewWeaponSide.FloatValue, -1.0F, 1.0F);
    bool leftHanded = weapSide < 0.0F;

    // ... sprint, raise, recoil, sway, reload ...

    // manual adjustment
    trans.x += cg_viewWeaponX.FloatValue * sp;
    trans.y += cg_viewWeaponY.FloatValue * sp;
    trans.z += cg_viewWeaponZ.FloatValue * sp;
    trans.x *= abs(weapSide);

    // ...

    // mirror geometry when left-handed
    if (leftHanded)
        mat = CreateScaleMatrix(Vector3(-1.0F, 1.0F, 1.0F)) * mat;

    return mat;
}
```

`cg_viewWeaponX/Y/Z` and `cg_viewWeaponSide` are already declared by
`BasicViewWeapon`; do not declare them again.

### Muzzle and case eject positions

This is the most common porting bug, and it is what makes tracers look broken.

In OpenSpades, `MuzzlePosition` and `CaseEjectPosition` return world space:

```as
// OpenSpades
Vector3 MuzzlePosition {
    get { return eyeMatrix * GetViewWeaponMatrix() * Vector3(0.0F, 0.7F, -0.05F); }
}
```

ZeroSpades multiplies the result by the eye matrix itself
(`ClientPlayer::GetMuzzlePositionInFirstPersonView`), so the script must
return eye space. Drop `eyeMatrix *`:

```as
// ZeroSpades
Vector3 MuzzlePosition {
    get { return GetViewWeaponMatrix() * (Vector3(0.0F, 80.0F, -11.5F) * globalScale); }
}
Vector3 CaseEjectPosition {
    get { return GetViewWeaponMatrix() * (Vector3(-3.0F, 20.0F, -12.0F) * globalScale); }
}
```

Express the point in the gun model's own voxel coordinates and scale it the
same way the model is scaled, so it stays on the barrel when the model moves.
Set `cg_debugToolSkinAnchors 1` to draw axes at both points and check that
the muzzle point sits at the end of the barrel.

If the mod leaves these out, it inherits the stock default
`(0, 0.35, -0.05)`, which only fits the stock gun.

### Hands

`LeftHandPosition` and `RightHandPosition` must be computed with the same
matrix the gun is drawn with. Many OpenSpades mods compute the hands with one
matrix (`GetViewWeaponMatrix() * CreateScaleMatrix(0.033F)`) and then draw the
model with extra scales, translations or rotations on top. The hands then
float away from the gun.

Build one matrix and use it for both:

```as
Matrix4 mat = GetViewWeaponMatrix() * CreateScaleMatrix(globalScale);
Matrix4 weapMatrix = eyeMatrix * mat;

leftHand = mat * GetLeftHandOffset();   // offsets in model voxel units
rightHand = mat * GetRightHandOffset();

param.matrix = weapMatrix;              // no extra transforms here
renderer.AddModel(gunModel, param);
```

If the model must be moved or rotated to fit, fix it in the `.kv6` pivot
(or apply the transform to `mat` before both uses), not to the model only.
Avoid non-uniform scales such as `CreateScaleMatrix(0.25F, 0.15F, 0.25F)`:
they stretch the voxels, and the hand offsets no longer match the model's
proportions.

When the player is aiming through a full-screen scope and the gun is hidden,
set both hands to `Vector3(0.0F, 0.0F, 0.0F)` as the stock scripts do.

### Charms

`BasicViewWeapon` loads the charm models and updates the charm springs. The
view script only needs to:

1. Draw the charm in `AddToScene()` when `cg_weaponCharms` is on, attached
   to a point on the gun's side. Copy the `// draw charms` block from the stock
   `View.as` and change the `CreateTranslateMatrix(...)` to the attachment
   point on the new model.
2. Kick the charm springs on events, the way the stock script does in
   `WeaponFired()`, `ReloadingWeapon()` and the reload animation:

   ```as
   charmHorizontalSwingSpring.velocity += (GetRandom() * 2 - 1) * 0.1F;
   charmVerticalSwingSpring.velocity += 0.3F;
   ```

3. Drive `charmSprintSpring` and `charmRaiseSpring` from `Update()`, and set
   `charmRaiseSpring.position = 1` in the constructor.

### Reflex sight (`cg_reflexScope`)

This applies to guns with iron sights. A gun with a built-in optic (sniper
scope, AUG-style scope) can skip it.

| Value | Meaning                               |
| ----- | ------------------------------------- |
| 0     | iron sights                           |
| 1     | reflex model, 3D dot sprite           |
| 2     | reflex model, 3D reflex sprite        |
| 3     | reflex model, 2D dot on screen        |
| 4     | reflex model, 2D reflex on screen     |

When it is non-zero:

- Draw a reflex sight model instead of the rear sight. A mod can ship its own
  `SightReflex.kv6`, or reuse the stock one.
- Aim at the reflex sight's height: pick the sight attachment from
  `cg_reflexScope` when computing `sightPos` in `GetViewWeaponMatrix()`.
- Draw the dot with the helpers in `BasicViewWeapon`:
  `DrawReflexSight3D(...)` in `AddToScene()` for modes 1–2, and
  `DrawReflexSight2D(GetViewWeaponMatrix())` in `Draw2D()` for modes 3–4.

The stock `SMG/View.as` shows all three pieces.

### Aim-down-sight overlays

Many OpenSpades mods draw their own full-screen image whenever the player
aims (`if (AimDownSightState > 0.6) DrawImage(...)`). In ZeroSpades this
overrides the player's choice of scope.

Only draw a full-screen scope image when `cg_pngScope` is on, and otherwise
let the 3D sights work. Fall through to `BasicViewWeapon::Draw2D()` so the
player's crosshair and scope settings still apply.

Name custom images after the mod, under the weapon's folder, for example
`Gfx/Weapons/Glock/Scope.png`. Do not use generic names such as `Gfx/1.png`,
and do not overwrite stock files such as `Gfx/SMG.png` unless the mod is meant
to replace them for every gun of that class.

### Other API differences

- `renderer.Color` still works, but the stock scripts use `renderer.ColorNP`
  (non-premultiplied) or `renderer.ColorP` (premultiplied). Prefer those.
- `BasicViewWeapon` already declares `cg_fov`, `cg_pngScope`,
  `cg_trueAimDownSight`, `cg_reflexScope`, `cg_weaponCharms` and the
  `cg_viewWeapon*` settings. Use them instead of declaring new ones.
- Prefix any setting the mod adds with the mod's name (for example
  `glock_skin`), so two mods cannot collide.

## Sounds

### Format

All sounds are Ogg Opus at 48 kHz, as in the base game. Convert with ffmpeg:

```sh
ffmpeg -i FireLocal.wav -c:a libopus -b:a 96k -ar 48000 FireLocal.opus
```

Then change every `RegisterSound("....wav")` in the scripts to `.opus`. The
engine looks files up by their exact extension and does not fall back from
one format to the other.

For scale: converting the WAVs in the recently added paks shrinks them from
about 13 MB to under 1 MB.

### Mono vs. stereo

The engine plays stereo samples with no distance attenuation and no
positioning. That is right for the local player's own sounds and wrong for
everyone else's. Follow the base game's convention:

| Played by                              | Example files                               | Channels |
| -------------------------------------- | ------------------------------------------- | -------- |
| `View.as` with `PlayLocal`             | `FireLocal`, `ReloadLocal`, `V2Local*`      | stereo is fine |
| `ThirdPerson.as` with `Play`           | `Fire*`, `V2Third*`, `FireFar`, `Reload`    | **mono** |
| `ThirdPerson.as`, wide stereo layer    | `FireStereo`                                | stereo   |

A stereo third-person fire sound means every shot from that gun is heard at
full volume anywhere on the map. Downmix it:

```sh
ffmpeg -i Fire.wav -ac 1 -c:a libopus -b:a 64k -ar 48000 Fire.opus
```

### Files the engine loads by itself

Some sounds are not registered by the skin scripts. The engine loads them
directly, by these exact names:

- `Sounds/Weapons/<Weapon>/RaiseLocal.opus`
- `Sounds/Weapons/<Weapon>/ShellDrop1.opus`, `ShellDrop2.opus`, `ShellWater.opus`
- `Sounds/Weapons/Spade/HitBlock.opus`, `HitPlayer.opus`, `Miss.opus`
- `Models/Weapons/<Weapon>/Casing.kv6`
- `Gfx/Killfeed/*.png`, `Gfx/Bullet/*.png`

A `.wav` or `.tga` copy of these is never loaded. Ship them as `.opus` and
`.png`, or leave them out to keep the base game's.

## Pak contents

- **No `.weak` files.** A `.weak` file loses to any plain file of the same
  name, including the base game's, so in a mod it is almost always dead
  weight.
- **No unused files.** Remove old takes (`oldFire.wav`), unused muzzle-flash
  frame sets (`Gfx/Flash/...`), duplicate formats (`b-SMG.tga` next to
  `b-SMG.png`), and models no script loads.
- **Match case exactly.** Lookups inside a pak ignore case, so `PUMP.kv6`
  loads when the script asks for `Pump.kv6`. Folder mods and other tools
  may not, so keep the script and the file name identical.
- **Third person.** Give `ThirdPerson.as` the same care as the view script:
  implement `IWeaponSkin2` so reverb follows the environment, and
  `IWeaponSkin3` so the muzzle point matches the third-person model.

## Testing before you open a pull request

Run through these with the mod enabled:

1. `cg_viewWeaponSide -1`: the gun, both hands and the charm are mirrored to
   the left, and nothing is drawn on the right.
2. `cg_weaponCharms 1` and `0`: the charm appears and disappears and swings
   on fire, reload and sprint.
3. `cg_reflexScope 0` to `4`, if the gun has iron sights: the sight model
   swaps and the dot lines up with where bullets land.
4. `cg_pngScope 0` and `1`: aiming uses the 3D sights or the scope image,
   respectively.
5. `cg_debugToolSkinAnchors 1`, then fire with tracers visible: the axes and
   the tracers start at the end of the barrel, while hip-firing, aiming and
   left-handed.
6. Reload and sprint: hands stay on the gun through the whole animation.
7. Ask another player to fire it, or use a second client: the shots get
   quieter with distance and come from the right direction.
