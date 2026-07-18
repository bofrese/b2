# 3D & visual effects

Activation index. Named thing + terse when/why. Not a tutorial. **Verify versions at build time.**

- **Three.js** — the WebGL workhorse. Custom 3D scenes, particles, shader materials. Heavy (~150KB+), steep. Use when 3D IS the product story.
- **React Three Fiber (R3F)** + **drei** helpers — Three.js declaratively in React. Default for React 3D. `drei` gives cameras/controls/loaders fast.
- **Babylon.js** — batteries-included engine (physics, editor, WebXR). Reach for: games, complex/interactive 3D, XR. Heavier than Three.
- **Spline** — no-code/low-code 3D design tool + web runtime. Reach for: designer-made 3D hero/objects without hand-coding shaders. Watch runtime weight and mobile perf.
- **WebGL / GLSL shaders** — raw fragment/vertex shaders for gradients, noise, distortion, custom post-fx. Max control, max effort. Reach for: signature visual effects not achievable in CSS.
- **Canvas 2D** — generative art, particles, data-driven visuals without 3D. Lightweight vs WebGL.

**When 3D helps:** product configurators, spatial storytelling, hero moments, brand differentiation (creative/gaming/luxury/tech). **When it distracts:** content-first sites, conversion funnels, accessibility-critical, low-power/mobile audiences. **Caveats:** lazy-load + code-split 3D, provide static fallback, budget for load/GPU, test mid-range mobile, `prefers-reduced-motion`.
