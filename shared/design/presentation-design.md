# Presentation Design — Stage & Pacing Knowledge

Trigger-word index for presentation-specific design judgment. Website principles
(`web-design-principles.md`) still apply — this file covers what changes when the medium is a
stage/screen, not a scrolling page.

## Stage vs. Projection Typography

- **Reading distance rule of thumb:** body text legible at the back of the room needs roughly 3-4×
  the type scale a website would use for equivalent content. Headlines scale even further.
- **Contrast over subtlety:** projector/screen colour reproduction and ambient room light erode
  low-contrast palettes that read fine on a monitor. Push contrast ratios higher than the website's.
- **Less text, more space:** a slide is glanced at for seconds, not read. One idea, max 3 bullets,
  generous whitespace — never a paragraph.

## Pacing & Beat Philosophy

- **Natural chunks, not mechanical taps.** Group animation reveals (fragments) around a spoken
  beat, not a fixed rhythm — the presenter shouldn't tap "next" several times for content that
  belongs together, nor have a single tap reveal three unrelated points at once.
- **Don't reveal before the point is made.** A build-up animation (bullet appears, chart line
  draws) should land in sync with the sentence that explains it — revealing early kills the reason
  for the animation.
- **Motion intensity ladder:** minimal (near-static, motion only where it earns its place) →
  moderate (purposeful transitions/reveals on the natural beats above) → dynamic (animation/3D as
  a visual signature, still gated by the same beat discipline — more motion, not less discipline).

## Presentation Psychology

- **The curiosity gap:** an opening that raises a question the close will answer creates narrative
  tension across the whole deck, not just the first slide — the visual design should echo this
  (a visual motif introduced on slide 1, resolved/completed on the closing slide).
- **Cognitive load budget:** each slide spends the audience's limited attention on exactly one
  thing — a slide with a chart AND three bullets AND a photo is asking for three different kinds of
  attention at once.
- **The proof slide is the credibility spike:** data/chart slides carry more weight than any other
  slide type — invest disproportionate craft here (real numbers over generic bar charts, an honest
  axis, a single highlighted data point rather than a dense dashboard).

## Accessibility

- `prefers-reduced-motion` gates all animation, same as website mockups — a presenter shouldn't be
  forced to disable an OS setting to review their own deck.
- Contrast ratios: verify against actual projector/screen conditions where possible (higher than
  WCAG AA website minimums is the safer default for presentations).
