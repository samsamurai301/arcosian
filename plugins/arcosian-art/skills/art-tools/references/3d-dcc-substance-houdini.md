# 3D tools beyond Blender: Substance 3D and Houdini (research note)

This is a research note, not a recipe set. It says what Adobe Substance 3D and SideFX Houdini automate, what their licences allow, when each is worth it for a small team, and whether an official MCP server or command-line route exists. Facts come from vendor pages read in Oct 2026; anything that could not be verified is labelled. Blender has its own adapter (`arcosian-blender`); start there for modelling and cleanup.

## Contents

1. Summary and decision table
2. Substance 3D: Painter, Designer, Automation Toolkit
3. Substance licences
4. Houdini: hython, PDG/TOPs, Houdini Engine
5. Houdini licences
6. MCP and CLI routes
7. When each is worth it
8. Security and provenance
9. Open questions to verify
10. Sources

## 1. Summary and decision table

| Need | Tool | Scriptable without a GUI? | Official MCP? |
|---|---|---|---|
| Hand-painted PBR textures on a mesh | Substance 3D Painter | Python plugins inside the app; external automation limited (see section 2) | None found |
| Procedural, parametric materials and batch variations | Substance 3D Designer plus Automation Toolkit | Yes, command-line tools and a Python library (pysbs) | None found |
| Procedural level, terrain, destruction, VFX generation, batch asset variation | Houdini (Indie or commercial) | Yes: `hython`, PDG/TOPs | None found |
| Procedural assets running inside the engine | Houdini Engine for Unity or Unreal | Via the plugin | Not applicable |
| Godot | Community Houdini plugin only | Needs commercial Houdini (see section 4) | None |

A small team often needs none of these. Blender plus a texture-painting tool covers most indie 3D. Add Substance when material quality is the bottleneck. Add Houdini when you must generate many procedural variations or large environments.

## 2. Substance 3D: Painter, Designer, Automation Toolkit

Substance 3D Painter:

- A Python API exists (Adobe's Experience League documentation). The `substance_painter` package gives access to Painter functions and runtime data, with modules such as `event` for event handling, `textureset`, and a `substance_painter_plugins` module that loads Python plugins from a configured path. A `js` module evaluates JavaScript in Painter's embedded engine.
- It is for plugins running inside Painter (for example a custom exporter or a UI panel). The documentation landing page notes an ongoing overhaul and points to tutorials, including one on exporting channels from a texture set. The version of the Python API follows the Painter version (the changelog ties 0.3.7 to Painter 12.1.0).
- Unattended batch use: search results did not confirm a headless route for Painter. Treat Painter as an interactive tool; batch baking and variations belong to Designer and the Automation Toolkit. Unverified.
- Output for games: export presets to PNG or TGA for the target engine (albedo or base colour, normal, ORM or separate metallic, roughness and ambient occlusion). Define the engine preset once and reuse it.

Substance 3D Designer and the Automation Toolkit (SAT):

- Designer builds node-graph materials saved as `.sbs` and published as `.sbsar` (parametric archives).
- The Automation Toolkit has command-line tools (for example `sbsbaker`, `sbscooker`, `sbsrender`) and the Python API `pysbs`. The `batchtools` module wraps the command-line tools as Python functions (options become keyword arguments with dashes turned to underscores). A demo chains bake, template fill, cook and render. A recent changelog notes the Vulkan engine can render on a GPU server without a display.
- Typical pipeline: bake mesh maps (`sbsbaker`), cook a material (`sbscooker`), render texture sets with parameters (`sbsrender`), then register outputs in the studio manifest.
- Designer also has its own Python scripting API for plugins and graph editing; check Adobe's Designer documentation for the module and version (unverified here).
- Runtime use of `.sbsar` in engines: engine plugins have changed over time and Adobe has changed support; verify the current Unity and Unreal status before designing around runtime-parametric materials. In Godot there is no verified first-party route; bake to textures instead.

## 3. Substance licences

- Adobe sells Substance 3D through subscription plans (a collection, and individual apps). Painter and Designer have also been sold on other storefronts; availability, price and terms change. All of this is unverified here; read the current Adobe licence and the Substance 3D product pages.
- Check, before buying: who may use the licence (named user), whether automation or server rendering needs a different licence than interactive use, and whether the Automation Toolkit is included with your plan.
- Output licence: textures you author are yours, but check Adobe's terms for assets from the Substance source library and the Substance 3D Assets library (licences differ per library). Record the source of each starter material in the manifest.
- If the subscription lapses, you keep exported textures but lose the ability to re-edit; keep exported PNGs and `.sbsar` outputs in the repo, plus source files.

## 4. Houdini: hython, PDG/TOPs, Houdini Engine

- `hython` is Houdini's Python interpreter for headless scripting. Use it to build or cook networks from a script and run in CI. Which licence tiers permit `hython` was not verified here; check the SideFX licence page for your tier before planning CI.
- PDG and TOPs: Houdini's task graph for running many work items in parallel (batch variation, simulation caches, asset pipelines). Tier availability is unverified here.
- Houdini Engine: plug-ins that load Houdini Digital Assets in a host application. SideFX lists Autodesk Maya, 3ds Max, Unity and Unreal Engine. The Unity and Unreal plug-ins are free for commercial customers (up to 10 licences per studio through the SideFX site; more via an account manager). Running them on machines without an interactive Houdini licence needs a Houdini Engine licence, and a free Houdini Engine Indie licence covers up to 3 computers.
- Godot: SideFX's Houdini Engine page does not list Godot. A community C++ GDExtension that exposes Houdini nodes to GDScript exists, is described by its author as work in progress, and needs a commercial Houdini licence; forum comments say the free or Indie edition cannot load third-party plug-ins. This is a forum report, not a vendor statement. For Godot, bake Houdini output to glTF, textures and scenes and import those.
- Common game uses: modular building and level kits, terrain and scattering, destruction, vertex-animation and flipbook textures for VFX, batch LOD generation.

## 5. Houdini licences

- Houdini Indie: $299 for one year or $449 for two (SideFX page, Oct 2026). Commercial use is limited to organisations with annual gross revenue of $100,000 USD or less and with less than $1,000,000 USD of funding in the last 24 months. Up to 3 Indie and 3 Engine Indie licences per commercial entity. Indie cannot be used in the same pipeline as commercial Houdini and saves in its own file format.
- Houdini Apprentice: free and for non-commercial use only. It cannot be used with Houdini Engine or Engine Indie, cannot share a pipeline with commercial Houdini, saves in a non-commercial format, renders with a watermark, and has a render resolution cap (SideFX's FAQ says 1080p, another source says 720p; check the EULA). The licence runs for 30 days and renews with an internet connection. You may not ship a commercial game from Apprentice work; use it to learn and prototype only.
- Houdini FX and Core (commercial): price and terms on the SideFX site; not read here.
- Revenue gates: when revenue crosses the Indie limit, you must move to a commercial licence. Plan the date. Do not mix Indie assets into a commercial pipeline.

## 6. MCP and CLI routes

- No official Adobe or SideFX MCP server was found in searches (Oct 2026). Search results showed third-party MCP projects for Substance 3D Designer; they are independent, not Adobe's, and only claim support for one Designer version. This plugin registers none. Treat any third-party server as untrusted code that can drive a licensed application and read your files; vet it (maintainer, licence, recent release, pinned version) before use.
- CLI routes that are official: the Substance Automation Toolkit command-line tools and `pysbs`; `hython` and Houdini's command-line tools. Write scripts for these and run them in your normal shell with a reviewed script file, as with the Blender headless route.
- Claude can write and review those scripts. It should not be given an interactive session that runs arbitrary Python inside Painter or Houdini.

## 7. When each is worth it

Use questions with numbers:

- Substance: how many unique materials will you ship? Under about 20 simple materials, a free tool or hand-painted textures is cheaper. Over 50, or many variants of the same material (damage, colour), Designer with batch rendering pays back (estimate).
- Houdini: how many procedural variations or how much environment content? One-off hero assets belong in Blender. Hundreds of kit variants, terrain tools or VFX caches justify Houdini.
- Team: who will learn it? Both have steep learning curves. If nobody on the team has the skill, hire for the task or buy assets instead.
- Pipeline: can you run it unattended? If not, it will not scale.
- Licence: is your revenue under the Indie ceiling? Is Apprentice only for learning?

## 7a. Evaluation procedure (half a day each)

Substance:

1. Pick one real asset from your game and one material you need in five variants.
2. Build or open a Designer graph, publish a `.sbsar`, then render the five variants from a Python script with `pysbs` batchtools (check the installed SAT version's help for the exact tool options).
3. Import the textures into the engine and compare to your current look at the game camera.
4. Count artist hours and compare to the alternative. Record the result.

Houdini:

1. Pick one repeatable need (for example a modular wall kit with ten variants).
2. Build it in Houdini Indie or Apprentice (Apprentice for learning only), then cook it from a `hython` script and export glTF.
3. Import into the engine. If the target is Unity or Unreal, also try the Engine plug-in with a Houdini Digital Asset.
4. Check the licence tier against the revenue ceiling and the pipeline rule (no mixing Indie and commercial).
5. Record hours, output quality and what had to be redone by hand.

If the half-day test does not beat the current method by a clear margin, do not adopt the tool.

## 8. Security and provenance

- Scripts from forums run with your user's rights: read before running.
- Do not open untrusted `.hip` or `.sbs` files from unknown sources in a production machine.
- Record in the manifest: tool and version, edition and licence holder, source files, starter assets and their licences, and the script used.
- Generated textures from asset libraries inherit those libraries' terms.

## 9. Open questions to verify

- Whether Painter can run headless in your version.
- Which Houdini tiers include `hython` and PDG.
- Current Substance runtime plugin support in Unity and Unreal.
- Current Houdini Engine status for Godot (community only as of this note).
- Adobe and SideFX MCP announcements.

## 10. Sources

- Painter Python API: https://experienceleague.adobe.com/en/docs/substance-3d-dev/painter-python/substance-3d-painter-python
- Automation Toolkit batchtools: https://helpx.adobe.com/substance-3d-sat/pysbs-python-api/overview/pysbs-batchtools-module.html
- Houdini Engine: https://www.sidefx.com/products/houdini-engine/
- Houdini Indie: https://www.sidefx.com/products/houdini-indie/
- Houdini Apprentice restrictions: https://www.sidefx.com/faq/question/435/
