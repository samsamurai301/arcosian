# Skeletal and vector animation

Three ways to animate 2D: draw every frame, rig a skeleton from cut-up parts, or play vector animation driven by a state machine. This file compares the main tools (Spine, Rive, DragonBones, and the animation features built into Godot and Unity), states the licence rules to check before you commit, and ends with a decision table. Vendor facts were read from vendor pages in Oct 2026; items that could not be verified are labelled.

## Contents

1. Decision table: frame-by-frame, skeletal or vector
2. Spine
3. Rive
4. DragonBones
5. Engine-native options: Godot
6. Engine-native options: Unity
7. Procedure: pick and prove a tool in one day
8. Pitfalls
9. Sources

## 1. Decision table: frame-by-frame, skeletal or vector

| Question | Frame-by-frame | Skeletal (Spine, engine rigs) | Vector with state machine (Rive) |
|---|---|---|---|
| Look | Any style, pixel art, strong smears | Smooth, part-based, limited deformation without meshes | Clean shapes, UI and icons, flat character art |
| Memory | High: one image per frame | Low: parts once, animation as data | Very low: a small file, rendered at runtime |
| Content volume | Cost grows with frames x animations x directions | Cheap to add animations and recolour | Cheap to add states and blends |
| Skins and equipment swap | Redraw all frames | Natural: swap attachments | Possible in state-machine inputs; limited for large equipment sets |
| Pixel-perfect needed | Yes, best fit | Poor: rotation and scaling blur pixels | Poor |
| Runtime cost | Lowest (a texture swap) | Moderate (mesh deform, many parts; budget it) | Moderate to high (vector rendering on the GPU; test on the weakest device) |
| Engine support | Everywhere | Official runtimes for Unity and Godot (Spine); engine rigs everywhere | Official Unity runtime; no official Godot runtime found (Oct 2026) |
| Team skill | Drawing | Rigging skill plus drawing | Design-tool skill |

Rules of thumb (estimates, test on your art):

- Pixel art, fewer than about 20 animations, one or two directions: frame-by-frame.
- Many characters sharing animations, equipment or skin swaps, or a need for tiny download size: skeletal.
- Animated UI, icons, menus, loaders, interactive illustrations, anything that reacts to input values: vector state machine.
- Do not mix styles in one character. A rigged body with frame-by-frame effects is fine; a rigged face on a pixel body is not.

## 2. Spine

Spine (Esoteric Software) is a 2D skeletal animation editor with meshes, IK, constraints and skins.

Editions and prices (read from the vendor purchase page, Oct 2026; prices move):

- Essential: about $69. Exports in all formats, but cannot use or export Professional features such as meshes or IK.
- Professional: about $379. All features; you can upgrade from Essential for the difference.
- Enterprise: required for businesses with $500,000 USD or more in annual revenue; one-year licences with a per-user fee on top of a base price.
- Education: for accredited institutions; not for commercial products.
- Essential and Professional are licensed per named person; sharing with unaffiliated third parties is not allowed.

Runtime licence rule (the one that catches teams out): licensing the editor lets you integrate the Spine Runtimes into your software and distribute it. After the editor licence expires you may keep distributing products that already contain the runtimes, but you may not integrate them into new products without an active editor licence. Read the Spine Runtimes License itself before shipping; this file is a summary, not legal advice. Every person who integrates the runtime needs a licence, so a team of two artists and a programmer who wires it up should budget for it. Record the licence holder and edition in the studio manifest.

Command-line export (vendor CLI page):

```
Spine -i project.spine -o out/ -e json            # or: -e binary
Spine -i project.spine -o out/ -e export.json     # export settings file
Spine -i project.spine -o out/ -e json+pack       # also pack atlases, default settings
Spine -i project.spine -m                         # clean-up, saves the project
```

- On Windows run `Spine.com` (it waits and prints to the console); on macOS run `Spine.app/Contents/MacOS/Spine`; on Linux run `Spine.sh`.
- Most parameters work headless; image and video export need a windowing system and OpenGL.
- The page does not say which edition the CLI needs. Check before planning CI.
- Binary export is smaller and faster to load; JSON is easier to diff. Pick one per project.

Runtimes:

- spine-godot: two flavours (vendor page). The GDExtension is one package in `bin/`, works on every platform Godot supports, and integrates with AnimationPlayer in Godot 4; no dedicated C# bindings. The C++ engine module needs a custom editor build and matching export templates, includes C# bindings, and is unlikely to support consoles. Godot 3.5.x is supported by the module only. Tint black needs Spine 4.3 and Godot 4.3 or later.
- spine-unity: the official Unity runtime from Esoteric Software, distributed through its site and GitHub (check the Spine Unity page for the supported Unity versions).
- Version matching: the runtime version must match the editor version family you export from. After a major Spine upgrade, re-export every asset and replace the files.
- Consoles: the GDExtension claims every Godot platform; verify on your target SDK. Console toolchains often need a custom build, so test early.

Procedure:

1. Rig in Spine with the art-direction style lock. Name bones and slots consistently (`hand_r`, `weapon`).
2. Export JSON or binary plus an atlas (`json+pack`).
3. Import into the engine; check one animation plays and a skin swaps.
4. Measure on the weakest target device: draw calls, mesh vertices, CPU.
5. Commit the `.spine` source and record the version used.

## 3. Rive

Rive is a vector animation tool with a state machine: you design the states and the inputs (booleans, numbers, triggers), and code sets the inputs at runtime.

- Official runtimes (read from Rive's runtime page, Oct 2026): web (JS on npm), React, React Native, Apple (Swift Package Manager and CocoaPods), Android (Maven), Flutter, C++ (Mac, Linux, Windows), and C#. Rive's game runtimes page lists Unity, Unreal and Defold.
- Official runtimes are described as open source under the MIT licence.
- Godot: no official runtime was found. A community GDExtension wrapping the C++ runtime is mentioned in a Godot forum thread from the Godot 4.2 era; it is untested and may be out of date. Treat Godot as unsupported unless you test a build.
- Unity: the official package supports Unity LTS 2021 and later according to the docs; the repository and docs disagree about WebP and JPEG image support, so test any file that embeds images.
- The Rive editor has free and paid plans; plan details were not verified here. Check rive.app before committing a team.
- Use for: UI motion, HUD, store and menu animation, tutorial illustrations, interactive loading screens. Avoid for large cast characters at 60 fps on low-end phones until you have measured.

Recipe:

1. Design the file with named state machines and inputs. Document the input names in the art bible: code depends on them.
2. Export the `.riv` file and add it to the project.
3. In Unity, load the file and set inputs from a script; in other engines use the runtime for that platform.
4. Test on target hardware. Record frame time with a Rive element on screen versus off.

## 4. DragonBones

DragonBones was a free skeletal animation tool with runtimes for several engines. Its maintenance status could not be verified: a search found no sign that the official JavaScript repository is archived, but also no recent activity statement, and one documentation index recommends a different editor for creating assets. Treat DragonBones as unverified and unmaintained until you check the repository's last commit and the editor's current release yourself. Do not start a new project on it without that check. If you inherit DragonBones assets, convert them to Spine or an engine rig early, or freeze the runtime version you tested.

## 5. Engine-native options: Godot

Godot ships a free skeletal system that needs no extra licence.

- `Skeleton2D` with `Bone2D` nodes, and `Polygon2D` with bone weights for deformation. Animate bone transforms with `AnimationPlayer`.
- `AnimationPlayer` animates any property, including `AnimatedSprite2D` frames, sprite `frame` and `region_rect`, modulate and shader parameters. Use it to sync sound and hit boxes to frames (a call-method track).
- `AnimationTree` blends and switches animations with a state machine or blend spaces. Use it for movement blends and attack combos.
- `AnimatedSprite2D` with `SpriteFrames` is the simplest route for frame-by-frame (see `sheets-atlases-import.md`).
- Limits: rigging in the editor is manual and slower than a dedicated tool; weight painting is basic. Check the current Godot documentation for 2D skeletons before planning a large cast.
- IK for 2D: check the current Godot version's 2D IK options (unverified here).

## 6. Engine-native options: Unity

- 2D Animation package: a skinning editor for rigging sprites with bones and meshes, sprite swap and IK for 2D. Pair it with the PSD Importer to bring layered Photoshop files in as separate sprite parts, so artists keep one source file.
- Unity's Animator and Animation windows animate bones and properties. Animator Controller handles states.
- Aseprite Importer package (`com.unity.2d.aseprite`): imports `.aseprite` files directly; with more than one frame and the Animated Sprite mode, it can generate animation clips and an Animator Controller (read-only; see the package FAQ). Its versions follow Unity versions (package 6.x pairs with Unity 6.6, 5.x with 6.5, and so on; 1.0 and 1.1 serve Unity 6.0, 2022.3 and 2021.3).
- Limits: the 2D Animation tool is simpler than Spine for meshes and constraints. Check the package docs for your Unity version.

## 7. Procedure: pick and prove a tool in one day

1. Write down: number of characters, animations each, directions, skins, target platforms, lowest device.
2. Use the decision table to shortlist two options.
3. For each, build one character with one idle and one run, in the real style.
4. Import into the target engine and run on the lowest device. Record frame time, file size and artist hours.
5. Decide. Record the choice, the licence (edition, holder, term) and the version in the studio manifest.
6. Re-check the licence if revenue approaches a threshold (Spine Enterprise starts at $500,000 annual revenue).

## 8. Pitfalls

- Buying Essential, then needing meshes. Essential cannot save projects that use Professional features.
- Forgetting that the runtime licence follows the editor licence for new products.
- Version drift between editor and runtime: assets stop loading.
- Rotating pixel art in a skeleton: the pixels shear. Use frame-by-frame for pixel art.
- Vector animation hot on a low-end phone: measure before committing the whole UI.
- Naming bones or inputs after the artist's mood, not a convention: code breaks when they rename.

## 9. Sources

- Spine purchase and licences: https://esotericsoftware.com/spine-purchase
- Spine command line: https://esotericsoftware.com/spine-command-line-interface
- Spine for Godot: https://esotericsoftware.com/spine-godot
- Rive runtimes: https://rive.app/docs/runtimes/getting-started
- Rive Unity: https://rive.app/docs/game-runtimes/unity
- Unity Aseprite Importer: https://docs.unity3d.com/Packages/com.unity.2d.aseprite@7.0/manual/index.html
- Godot SpriteFrames: https://docs.godotengine.org/en/stable/classes/class_spriteframes.html
