# Web animation & motion libraries

Activation index. Named thing + terse when/why. Not a tutorial. **Verify versions at build time.**

- **GSAP (+ ScrollTrigger)** - industry-standard timeline engine. **100% free incl. all Club plugins (SplitText, MorphSVG, DrawSVG, ScrollTrigger, ScrollSmoother, Inertia) since Apr 2025** (Webflow acquired GreenSock). Reach for: complex sequenced timelines, scroll-scrubbing, SVG morph/draw, precise easing choreography. Not React-idiomatic (imperative). ~50KB core.
- **Motion (formerly Framer Motion + Motion One, merged 2024-25)** - `npm i motion`, import `motion/react`. Best React DX: declarative `<motion.div>`, layout animations, `AnimatePresence` exit, gestures, shared-element/layoutId, scroll-linked. ~30KB+. Default for React product UI.
- **Motion One / `animate()`** - the tiny (~4KB) vanilla arm of Motion, built on WAAPI. Reach for: framework-free micro-interactions where bundle size matters. Fewer features than full Motion/GSAP.
- **anime.js v4** (2025 rewrite, ES modules, tree-shakeable) - lightweight vanilla timeline/stagger. Middle ground between Motion One and GSAP; good for SVG + DOM stagger without GSAP weight.
- **Web Animations API (WAAPI)** - native `element.animate()`. Zero-dep, compositor-friendly. Reach for: simple keyframe animations without a library. Underpins Motion One.
- **View Transitions API** - native crossfade/morph between DOM states. **Same-document = Baseline newly available (Oct 2025, all 3 engines).** Cross-document (MPA) still Chrome/Edge 126+ only (FF/Safari pending). Reach for: SPA route/state transitions, replaces JS transition libs. Pair with `view-transition-name`.
- **CSS scroll-driven animations** - `animation-timeline: scroll()` / `view()`. Compositor-driven, zero JS, smoother than IntersectionObserver. Reach for: reveal-on-scroll, progress bars, parallax. Chrome/Edge/FF shipping; Safari lagging - progressive-enhance.
- **Lenis** (darkroom.engineering) - smooth-scroll normalizer. Reach for: award-site "buttery" scroll feel, pairs with GSAP ScrollTrigger/scroll-driven anim. Caveat: overrides native scroll - accessibility/perf risk, respect `prefers-reduced-motion`, offer opt-out.

Rules: always gate motion behind `prefers-reduced-motion`. Prefer native (WAAPI/CSS/View Transitions) before adding a lib. GSAP for choreography, Motion for React, native for the rest.
