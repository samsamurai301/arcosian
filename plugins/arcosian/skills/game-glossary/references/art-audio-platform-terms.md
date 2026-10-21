# Art, Audio, Platform and Store Terms

This file defines visual art direction and rendering-art terms, audio production and implementation terms, and mobile, PC and console platform terms: store packaging, signing, accessibility APIs, lifecycle and device constraints. Use it when a style bible, an audio spec, a build pipeline or a store submission uses a term you need to pin down. Entries are alphabetical; each entry is one line in the form **Term** — definition — see: related term or skill. Platform entries describe concepts; check the current platform documentation for exact rules and requirements before relying on them.

## Contents
- 0-9: 9-slice (nine-slice scaling) through 9-slice (nine-slice scaling)
- A: Adaptive music through Audio middleware
- B: Background execution limits through Bump map
- C: CC0 (public domain dedication) through Crossfade
- D: Data safety disclosure through Dynamic Type (iOS)
- E: Early reflections (audio) through Event (audio)
- F: Fog through Force update
- G: Game Center and Play Games services through Google Play Console
- H: Haptics (haptic feedback) through HRTF (head-related transfer function)
- I: Icon (game icon) through Internal testing track
- K: Kerning through Key light and fill light
- L: Leading through LUT (lookup table)
- M: Mastering (audio) through Music stem
- N: Normal map through Notarization (macOS)
- O: Obstruction and occlusion (audio) through Obstruction and occlusion (audio)
- P: Palette through Push notification (APNs, FCM)
- Q: Quad (overdraw unit) through Quad (overdraw unit)
- R: Reduced motion through RTL (right-to-left) layout
- S: Safe area through Subsurface scattering (SSS)
- T: TestFlight through Typography
- U: Universal input (action map) through Universal input (action map)
- V: Vector art through VO localization
- W: WebGL and web builds through Wwise / FMOD
- X: Xcode Cloud and other CI services through Xcode Cloud and other CI services
- Z: Zoning (level streaming) through Zoning (level streaming)

## 0-9

**9-slice (nine-slice scaling)** — Splitting a UI image into nine regions so corners stay fixed and edges stretch; keeps panels crisp at any size. — see: `mobile-ux`

## A

**Adaptive music** — Music that changes with game state through layers, stingers or transitions instead of playing one loop. — see: `audio-direction`
**Age gate** — Question or check that restricts access by age, shaped by privacy and youth-protection law. — see: `legal-ethics`
**Age rating questionnaire** — Store form whose answers set the content rating; inaccurate answers risk removal. — see: `legal-ethics`
**Albedo** — Base colour map in a physically based material with no lighting baked in. — see: `technical-art`
**Ambient occlusion (AO)** — Darkening in creases and contact areas that approximates blocked light; cheap as a baked map on mobile. — see: `technical-art`
**Ambisonics** — Full-sphere audio format that encodes sound direction for playback over speakers or headphones. — see: `audio-direction`
**ANR (Android Not Responding)** — Android error raised when the main thread is blocked too long; a store-visible stability metric. — see: `mobile-performance`
**Anti-aliasing (MSAA, FXAA, TAA)** — Techniques that smooth jagged edges; each trades cost, sharpness and temporal artefacts differently. — see: `technical-art`
**APK (Android package)** — Installable Android binary format; direct installs and some tests use it, while store uploads use the app bundle. — see: `store-release`
**App bundle (AAB)** — Android upload format from which the store generates device-specific APKs; the usual Play submission format. — see: `store-release`
**App Store Connect** — Apple's portal for app records, builds, metadata, TestFlight distribution and review submissions. — see: `store-release`
**App thinning (split delivery)** — Store delivery of only the resources a device needs, which reduces download size. — see: `store-release`
**Art bible (style bible)** — Document defining palette, silhouettes, shape language, materials and do/don't examples so every asset matches. — see: `art-direction`
**Art direction** — Set of visual decisions that gives a game a consistent look and communicates its tone and readability. — see: `art-direction`
**Asset brief** — Per-asset spec with purpose, size, budget, references and acceptance checks sent to an artist or generator. — see: `art-direction`
**Asset QA** — Checks that imported assets meet naming, format, budget and licence rules before they reach the build. — see: `technical-art`
**Attenuation (audio)** — Reduction of sound level with distance, shaped by a curve; defines audible range. — see: `audio-direction`
**Audio bus (mix bus)** — Routing group that applies shared volume and effects to sounds of one category, such as music or voice. — see: `audio-direction`
**Audio middleware** — Authoring tool and runtime, such as FMOD or Wwise, for mixing, events and adaptive audio in engines. — see: `ai-audio-pipeline`

## B

**Background execution limits** — OS rules that suspend or throttle backgrounded apps; save state early and do not assume the process keeps running. — see: `mobile-performance`
**Battery budget** — Power allowance per session; sustained high frame rates and GPU load drain batteries and trigger throttling. — see: `mobile-performance`
**Binaural audio** — Two-channel spatial audio designed for headphones, using head-related cues. — see: `audio-direction`
**Bit depth** — Number of bits per audio sample, which sets dynamic range; 16 and 24 bit are common delivery formats. — see: `audio-production`
**BPM (beats per minute)** — Tempo unit used to align loops, stingers and transitions to musical time. — see: `audio-direction`
**Build number** — Monotonically increasing number on each upload; each new submission needs a higher value. — see: `store-release`
**Bump map** — Greyscale height texture that fakes small surface relief under lighting; cheaper than normal maps but less accurate. — see: `technical-art`

## C

**CC0 (public domain dedication)** — Licence that waives rights to a work as far as law allows; attribution is not required but provenance should be recorded. — see: `legal-ethics`
**CC BY (attribution licence)** — Licence allowing reuse with credit to the creator; the credit must be shipped where the licence requires it. — see: `legal-ethics`
**Cel shading (toon shading)** — Quantized lighting that gives flat colour bands; a readable stylized look that is cheap to render. — see: `art-direction`
**Chargeback** — Card-network reversal of a payment initiated by the cardholder; costly, and a fraud signal. — see: `monetization`
**Chromatic aberration** — Colour fringing at edges that imitates lens effects; a stylistic choice that can hurt readability and comfort. — see: `art-direction`
**Cloud build** — Remote build service that compiles the project on managed machines, removing local setup. — see: `store-release`
**Cloud save** — Synchronizing progress across devices through a platform service or your backend; handle conflicts explicitly. — see: `game-architecture`
**Code signing** — Cryptographic signing that proves a build's origin and integrity; unsigned builds cannot be installed or submitted. — see: `store-release`
**Color grading** — Adjusting overall colour and contrast across a scene or the whole game, often through a LUT. — see: `technical-art`
**Color script (keyframes)** — Small thumbnail sequence that plans colour and lighting across key moments of a level or sequence. — see: `art-direction`
**Color temperature** — Warmth or coolness of a light source in kelvin; use it to separate mood and time of day. — see: `art-direction`
**Concept art** — Early visual exploration of characters, environments and props used to set direction before production. — see: `art-direction`
**Consent banner** — Dialog that collects consent for tracking or data use; it must match legal and store requirements per region. — see: `legal-ethics`
**Contact shadow** — Small high-detail shadow where objects touch; adds grounding that low-resolution shadow maps miss. — see: `technical-art`
**Crash-free sessions** — Share of sessions without a crash; a release-health metric and a store-vitals input. — see: `production`
**Crash reporting (symbolication)** — Mapping crash stack traces to readable names using uploaded debug symbols. — see: `production`
**Crossfade** — Gradual fade between two audio sources over time; the basic transition in adaptive music. — see: `audio-direction`

## D

**Data safety disclosure** — Store-required declarations of data collected and shared; they must match what the SDKs actually do. — see: `legal-ethics`
**Dataset rights** — Permission status of the training data behind a generative tool; a key question for AI-generated art or audio in shipped games. — see: `ai-asset-pipeline`
**Decal** — Projected texture applied on top of surfaces, used for damage, markings and footprints. — see: `technical-art`
**Deep link (app link, universal link)** — URL that opens a specific screen in the installed app; needs domain verification on each platform. — see: `marketing-ua`
**Depth of field (DoF)** — Blurring of out-of-focus areas; a strong readability cost in fast games, so keep it optional on mobile. — see: `technical-art`
**Dialogue system** — Runtime that selects, queues and plays lines by condition, interruption and priority. — see: `narrative-design`
**Dithering (ordered)** — Pattern-based transparency or gradient technique that avoids banding and can fake transparency cheaply. — see: `technical-art`
**Ducking** — Lowering one audio group, usually music, while another, such as dialogue, plays. — see: `audio-direction`
**Dynamic range (audio)** — Difference between the quietest and loudest meaningful levels; too little causes fatigue, too much hides quiet detail on phones. — see: `audio-production`
**Dynamic range (image)** — Range of brightness an image or display can represent; HDR output extends it. — see: `technical-art`
**Dynamic Type (iOS)** — System text-size setting; layouts must grow with it rather than clip. — see: `accessibility-localization`

## E

**Early reflections (audio)** — First echoes from room surfaces that tell the listener the space's size and material. — see: `audio-direction`
**Entitlement** — Capability granted in the signed app configuration, such as push notifications or in-app purchase. — see: `store-release`
**Event (audio)** — Named trigger in audio middleware that plays, stops or alters sounds in response to game code. — see: `audio-direction`

## F

**Fog** — Distance-based blending toward a colour; hides pop-in and sets mood at low cost. — see: `technical-art`
**Foley** — Recorded or synthesized everyday sounds, such as footsteps and cloth, that give actions physical weight. — see: `audio-direction`
**Font fallback** — Substitute font for glyphs missing from the primary font; essential for multi-script localization. — see: `accessibility-localization`
**Force update** — Requiring a minimum app version through remote config or a server check before play continues. — see: `liveops`

## G

**Game Center and Play Games services** — Platform achievements, leaderboards and sign-in services; use them when platform identity is part of the product. — see: `multiplayer-backend`
**Gamepad mapping** — Assigning actions to controller buttons following each platform's layout conventions. — see: `mobile-ux`
**Gamut** — Range of colours a display or format can show; sRGB and wider gamuts differ in what they can represent. — see: `technical-art`
**Global illumination (GI)** — Lighting that includes indirect light bounced between surfaces; expensive, so usually baked or approximated on mobile. — see: `technical-art`
**Google Play Console** — Google's portal for app records, releases, testing tracks, policy forms and store listing. — see: `store-release`

## H

**Haptics (haptic feedback)** — Vibration patterns that confirm input or events; use platform APIs and keep them short and optional. — see: `mobile-ux`
**HDR (high dynamic range)** — Pipeline or display mode that represents brighter and darker values than standard range; needs tonemapping for output. — see: `technical-art`
**Hit target** — Touchable area of a control; mobile guidelines commonly set a minimum size, and the visual size can be smaller. — see: `mobile-ux`
**Horizontal re-sequencing** — Changing the order of music segments in response to state, rather than layering stems. — see: `audio-direction`
**HRTF (head-related transfer function)** — Model of how the head and ears change sound, used for convincing 3D positional audio on headphones. — see: `audio-direction`

## I

**Icon (game icon)** — Small image representing the game on stores and home screens; needs multi-size exports and a safe area. — see: `store-release`
**Iconography** — Set of symbols used for UI actions and states; keep them consistent in meaning and paired with labels. — see: `mobile-ux`
**Impostor (billboard)** — Flat textured quad that stands in for a distant 3D object, a cheap way to fill crowds and forests. — see: `technical-art`
**Impulse response (convolution reverb)** — Recorded acoustic signature of a space used to add realistic reverb; costlier than algorithmic reverb. — see: `audio-direction`
**Internal testing track** — Google Play track for small invited groups before wider release; quick to distribute. — see: `store-release`

## K

**Kerning** — Spacing between specific character pairs in a typeface; adjust it for headlines and display text. — see: `art-direction`
**Keychain and Keystore** — Platform secure storage for keys and tokens; never keep secrets in plain files or in the build. — see: `legal-ethics`
**Keyframe (animation)** — Pose at a specific time in an animation, with interpolation between keys. — see: `technical-art`
**Key light and fill light** — Main light sets form and direction; fill light lifts shadows to control contrast. — see: `art-direction`

## L

**Leading** — Vertical space between lines of text; affects readability and layout density. — see: `art-direction`
**Light probe** — Captured lighting sample in a volume used to light dynamic objects in baked scenes. — see: `technical-art`
**Lipsync** — Mapping of speech to facial animation through phonemes or visemes; quality strongly affects perceived voice quality. — see: `narrative-design`
**Local notification** — Notification scheduled on the device without a server; reliable for timed reminders. — see: `liveops`
**LOD bias** — Adjustment that makes level-of-detail switching happen closer or farther; a quality and performance control. — see: `technical-art`
**Loop point** — Start and end positions of a looping sound or music track set so the seam is inaudible. — see: `audio-production`
**Loudness (LUFS)** — Integrated loudness measure in loudness units relative to full scale; use it to match levels across assets and platforms. — see: `audio-production`
**Low memory warning** — OS signal to free memory; release caches and textures in response. — see: `mobile-performance`
**LUT (lookup table)** — Table that remaps input colours to output colours; the usual format for colour grading. — see: `technical-art`

## M

**Mastering (audio)** — Final balancing, limiting and format export of an audio mix for delivery. — see: `audio-production`
**Mesh budget** — Per-asset and per-scene limits on triangles, vertices and draw calls set by platform tier. — see: `technical-art`
**Metallic (map)** — Material channel that separates metal from non-metal surfaces in physically based shading. — see: `technical-art`
**Minimum OS version** — Lowest platform version the app supports; raising it cuts devices and may unlock features. — see: `store-release`
**Mood board** — Curated image collection that communicates intended tone, palette and references before production. — see: `art-direction`
**Motion blur** — Blur along movement direction; can add speed or hide flicker, but adds cost and comfort concerns. — see: `technical-art`
**Music stem** — Separate audio track of one musical element, such as drums or pads, that can be mixed in or out adaptively. — see: `audio-direction`

## N

**Normal map** — Texture storing surface direction used to simulate fine detail under lighting without extra geometry. — see: `technical-art`
**Notarization (macOS)** — Apple's automated scan of a signed macOS app before distribution outside the store. — see: `store-release`

## O

**Obstruction and occlusion (audio)** — Sound blocked by geometry; obstruction affects the direct path, occlusion affects the whole signal. — see: `audio-direction`

## P

**Palette** — Set of colours defined for the game, often with roles such as background, accent and warning. — see: `art-direction`
**Parallax occlusion mapping** — Technique that fakes surface depth by offsetting texture lookups per view angle; costly on mobile. — see: `technical-art`
**PBR (physically based rendering)** — Shading model that uses energy-conserving materials such as albedo, roughness and metallic maps. — see: `technical-art`
**Permissions (runtime)** — OS prompts for camera, microphone, location and notifications; ask in context and explain the reason. — see: `legal-ethics`
**Pivot point** — Origin an asset rotates and scales around; set it correctly during modelling to avoid import fixes. — see: `technical-art`
**Pixel art** — Art made on a fixed pixel grid; requires nearest-neighbour filtering and integer scaling to stay crisp. — see: `art-direction`
**Platform certification** — Required technical and content checks a console or other platform owner runs before release; plan time for it. — see: `store-release`
**Pointer input** — Mouse, trackpad or stylus input; add hover and secondary-click support where players expect it. — see: `mobile-ux`
**Provisioning profile** — Apple file linking an app ID, certificates and devices or distribution rules; expired profiles block builds. — see: `store-release`
**Push notification (APNs, FCM)** — Server-to-device message channel; Apple Push Notification service and Firebase Cloud Messaging are the usual transports. — see: `liveops`

## Q

**Quad (overdraw unit)** — Group of four pixels that the GPU shades together; tiny triangles waste work on quads. — see: `mobile-performance`

## R

**Reduced motion** — System setting asking for less animation; respect it by limiting shake, parallax and transitions. — see: `accessibility-localization`
**Refresh rate (adaptive)** — Display rate that varies by device and content; pace frames for several targets. — see: `mobile-performance`
**Retopology** — Rebuilding a mesh with cleaner topology for animation or LOD; often needed after sculpting or scanning. — see: `technical-art`
**Rigging** — Building a skeleton and controls so a model can be posed and animated. — see: `technical-art`
**Rim light** — Light from behind that outlines a subject and separates it from background. — see: `art-direction`
**Roughness** — Material channel controlling how sharply reflections spread; one of the core PBR inputs. — see: `technical-art`
**RTL (right-to-left) layout** — Mirroring UI for Arabic and Hebrew; test icons, progress bars and text alignment. — see: `accessibility-localization`

## S

**Safe area** — Screen region clear of notches, rounded corners, home indicators and system bars; keep critical UI inside it. — see: `mobile-ux`
**Sample rate** — Number of audio samples per second; 44.1 and 48 kHz are common delivery rates. — see: `audio-production`
**Sandbox (store test environment)** — Store-provided test accounts and test purchases; never real money. — see: `monetization`
**Scene lifecycle** — Sequence of app states (active, inactive, background, suspended) that drives pausing and saving. — see: `mobile-performance`
**Screen reader (VoiceOver, TalkBack)** — Platform assistive technology that reads UI aloud; games must expose labels and focus order to support it. — see: `accessibility-localization`
**Screen-space reflection (SSR)** — Reflections computed from on-screen depth and colour; cheap but misses off-screen geometry. — see: `technical-art`
**SFX (sound effects)** — Non-musical sounds that signal events, feedback or environment. — see: `audio-direction`
**Shadow cascade** — Splitting the shadow map into ranges by distance so near shadows stay sharp; more cascades cost more. — see: `technical-art`
**Shadow map** — Depth texture rendered from a light's view to decide what is shadowed. — see: `technical-art`
**Sidechain compression** — Ducking one signal from the level of another, typically kick drum controlling the bass. — see: `audio-production`
**Sign in with Apple** — Sign-in option that apps offering third-party sign-in usually must include; check current policy text. — see: `legal-ethics`
**Silhouette** — Outline shape of a character or object; a core readability test when viewed as a solid black shape. — see: `art-direction`
**Skybox** — Background environment rendered at infinite distance, often a cube or sphere texture. — see: `technical-art`
**Socket (attachment point)** — Named transform on a skeleton where items or effects attach, such as a hand or muzzle. — see: `technical-art`
**Sprite sheet** — Sequence of frames packed into one image for animation; efficient for 2D and particle effects. — see: `technical-art`
**Staged rollout (Play)** — Gradual release to rising percentages of users, with the ability to halt. — see: `store-release`
**Steam and PC storefronts** — PC distribution with its own depots, branches and review process; check current documentation. — see: `store-release`
**Stinger** — Short musical cue played on an event, such as a victory or a warning; short enough to layer over music. — see: `audio-direction`
**Stock asset** — Pre-made art or audio bought under a licence; check its licence terms for games and redistribution. — see: `legal-ethics`
**Store listing** — Title, description, screenshots, video, rating and keywords shown on the store page. — see: `marketing-ua`
**Style lock** — Fixed set of references and parameters that keeps generated or outsourced assets in one visual style. — see: `ai-asset-pipeline`
**Subscription sandbox** — Test environment for subscription purchases, renewals and cancellations. — see: `monetization`
**Subsonic** — Frequencies below about 20 Hz that most small speakers cannot reproduce; they are used sparingly for impact. — see: `audio-production`
**Subsurface scattering (SSS)** — Light diffusing under translucent surfaces such as skin; a costly effect to approximate on mobile. — see: `technical-art`

## T

**TestFlight** — Apple's beta distribution service for builds to invited testers before public release. — see: `store-release`
**Texel density** — Texture pixels per world unit; keeping it consistent prevents some assets looking blurrier than others. — see: `technical-art`
**Thermal throttling** — OS lowering CPU and GPU clocks as the device heats; sustained frame rate can fall after minutes. — see: `mobile-performance`
**Three-point lighting** — Key, fill and back light setup; a common baseline for character presentation. — see: `art-direction`
**Tonemapping** — Mapping of high dynamic range values into displayable range, preserving highlights and contrast. — see: `technical-art`
**Touch input** — Multitouch gestures and latency; keep controls thumb-reachable and avoid clashing with system gestures. — see: `mobile-ux`
**Trim sheet** — Texture atlas of reusable edge and surface patterns that lets many meshes share one texture. — see: `technical-art`
**Typography** — Choice and arrangement of typefaces, sizes and spacing; sets hierarchy and tone in UI. — see: `mobile-ux`

## U

**Universal input (action map)** — Abstraction over keyboard, touch, gamepad and pointer so one action map serves every platform. — see: `game-architecture`

## V

**Vector art** — Art defined by mathematical shapes that scale without loss; useful for UI icons at many densities. — see: `art-direction`
**Version name** — User-facing version string, distinct from the build number. — see: `store-release`
**Vertex color** — Per-vertex colour attribute used to tint, blend or mark surfaces without extra textures. — see: `technical-art`
**Vertical remixing** — Adding or removing stems on a running track to match intensity. — see: `audio-direction`
**Vibration API** — Platform call for vibration patterns; prefer the haptics APIs where available. — see: `mobile-ux`
**Vignette** — Darkened screen edge that focuses attention; stylistic, and should be disableable for readability. — see: `art-direction`
**Voice cloning (consent)** — Synthesizing a real person's voice; requires documented consent and a rights agreement. — see: `legal-ethics`
**Voice-over (VO)** — Recorded spoken dialogue; plan casting, recording, localization and file naming together. — see: `narrative-design`
**VO localization** — Recording or generating dialogue per language, with timing and lipsync reviewed per locale. — see: `accessibility-localization`

## W

**WebGL and web builds** — Browser builds with memory and threading limits; test in each target browser. — see: `mobile-performance`
**Wireframe** — Low-fidelity layout sketch of screens with no visual style; use it to test flow before art. — see: `mobile-ux`
**Wwise / FMOD** — Named audio middleware products; choose by team skill, engine integration and licence cost. — see: `ai-audio-pipeline`

## X

**Xcode Cloud and other CI services** — Hosted build services for iOS and cross-platform builds; choose by signing workflow and cost. — see: `store-release`

## Z

**Zoning (level streaming)** — Dividing a level into zones or cells that load and unload to limit memory. — see: `mobile-performance`
