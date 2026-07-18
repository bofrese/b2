# Illustration Knowledge

Reference for constructing world-class image prompts. Load before proposing any directions or prompts.

---

## Prompt Construction

**Structure every prompt in this order:**
`[Subject + action]` `[environment/setting]` `[composition notes]` `[medium and movement]` `[colour palette]` `[lighting]` `[texture and finish]` `[mood]` `[quality markers]`

**Rules:**
- Subject first, always. Be specific: "a lone developer hunched over a glowing terminal" not "a person working"
- Name the medium explicitly: "flat vector illustration" / "gouache on textured paper" / "linocut print" / "risograph-printed editorial" / "ink wash with watercolour"
- Palette by name or adjective: "muted sage green and warm terracotta on cream" — not "colourful" or "vibrant"
- Lighting quality: "flat graphic" / "warm diffused backlight" / "high contrast chiaroscuro" / "even northern light" / "dappled through foliage"
- Weave constraints into the prompt as style properties: "no photorealism" / "no gradients" / "no faces" / "no text" — do not use a separate negative prompt field
- End with quality markers that match the medium: "editorial quality" / "award-winning book cover illustration" / "hand-crafted warmth" / "studio ghibli production sketch quality"
- Avoid empty adjectives: "beautiful", "stunning", "amazing", "highly detailed" — be specific instead

**Composition guidance by use case:**
- **Hero/banner (16:9):** Wide breathing room; subject offset to left or right third; space for headline text overlay on the open side
- **Article header (3:2):** Strong central composition; emotion readable at thumbnail size (100px test)
- **Spot illustration (1:1):** Simple; one focal point; works at small sizes; often benefits from white or transparent background
- **Social card (1:1 or 4:5):** Bold, high contrast; readable text-free at 200px
- **Portrait/mobile (4:5 or 9:16):** Vertical energy; subject fills frame; strong silhouette

---

## Illustration Styles and Movements

**Editorial:** NYT, New Yorker, Guardian style — conceptual, witty, often metaphor-driven; figures frequently stylised or abstracted; limited palette; confident line

**Print techniques:** Risograph (halftone dots, limited colours, slight misregistration), screen print (flat opaque areas, high contrast), linocut/woodcut (bold black marks, gouged texture), letterpress

**Painterly media:** Gouache (opaque, matte, flat areas with painted edges), watercolour (transparent washes, bleeds), ink wash (gestural, calligraphic), oil pastel (textured, saturated)

**Vector / graphic:** Flat vector (geometric, clean, scalable), isometric (objects in 3/4 view, no perspective distortion), paper cut (layered flat shapes, slight drop shadows only between layers)

**Historical movements:**
- **Bauhaus** — geometric forms, primary colours, typography as structure, rational composition
- **Constructivism** — diagonal energy, strong silhouettes, worker-heroic scale, limited palette
- **Art Deco** — symmetry, gilded luxury, stepped forms, sunburst motifs, stylised figures
- **Memphis/Post-Modern** — chaotic pattern, pastel + primaries, squiggles, confetti, 1980s optimism
- **Swiss International Style** — grid, Helvetica, asymmetric balance, photography + typography; when applied to illustration: structured negative space, disciplined type integration
- **Japanese minimalism (Ma)** — negative space as active element, sparse marks, natural textures, restraint
- **Mid-century modern** — Saul Bass-style geometric reductionism; Paul Rand's playful geometry; limited palette; texture from era printing

**Narrative / character:** Children's book (friendly, rounded, expressive), graphic novel (panel energy, motion lines, high contrast), folk art (flat, patterned, culturally specific texture), botanical illustration (precise, scientific, beauty through accuracy)

**Contemporary web/product:** Claymation/3D inflated (glossy, rounded, pastel), glassmorphism illustration (frosted panels, blur overlays), gradient mesh (photorealistic colour), Lo-fi/Vaporwave (retrowave palette, CRT nostalgia), Cottagecore (soft watercolour, botanical, domestic warmth)

---

## Colour Principles

- **Limited palette** — 3–5 colours maximum for editorial work. More colours ≠ more interesting.
- **Analogous** — adjacent hues (e.g. blue → teal → green). Creates calm, cohesion.
- **Complementary** — opposite hues (e.g. orange + blue). Creates tension and energy.
- **Triadic** — three hues equally spaced (e.g. red + yellow + blue). Playful, balanced.
- **Split-complementary** — one hue + two adjacent to its complement. More nuanced than full complementary.
- **Monochromatic** — single hue in multiple tints/shades. Sophisticated, focused.
- **Warm/cool contrast** — push foreground warm, background cool (or vice versa) to create depth without literal perspective
- **Neutral base** — cream, off-white, warm grey, or paper tone as background reads more human than pure white
- **Accent discipline** — one accent colour used sparingly carries more weight than multiple competing ones

---

## Lighting Vocabulary

- **Flat graphic** — no lighting simulation; objects are local colour only
- **Chiaroscuro** — dramatic dark/light; Renaissance drama
- **Rim lighting** — subject lit from behind/side; strong silhouette; cinematic
- **Dappled/filtered** — light through foliage or blinds; pattern of shadow and light
- **Silhouette against light source** — subject dark against bright background; high impact, ambiguous detail
- **Ambient northern light** — even, diffused, no strong shadows; illustrator's preferred neutral
- **Warm diffused backlight** — golden hour feeling; cosy, optimistic

---

## Metaphor and Concept

Literal depictions are the last resort. Always ask: is there a metaphor that carries the idea better?

Examples:
- "Information overload" → a figure drowning in paper, not a person at a computer
- "Business growth" → a plant growing from a spreadsheet, not a rising bar chart
- "Collaboration" → two distinct visual systems fitting together like puzzle pieces, not people shaking hands
- "Decision paralysis" → a figure frozen at a fork with a thousand paths, not a person looking confused

The best editorial illustrations make the viewer think for a beat before they get it. That delay is the pleasure.

---

## Quality Checklist (apply before finalising any prompt)

- [ ] Subject is specific and vivid — not generic
- [ ] Medium is named explicitly
- [ ] Palette described with colour names or precise adjectives
- [ ] Lighting quality specified
- [ ] Constraints embedded as style properties (no X, avoid Y)
- [ ] Composition noted for intended use (text overlay space, thumbnail readability)
- [ ] Quality marker appropriate to the medium
- [ ] Prompt tested against style brief — palette, line quality, and mood all consistent
