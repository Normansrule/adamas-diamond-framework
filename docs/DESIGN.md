# Website design rules

The rules the website (`web/`) follows, so new labs look and behave like the existing ones. Tokens live in `web/assets/style.css` (`:root`); shared behavior in `web/assets/site.js`.

## Non-negotiables

- 60 frames per second on a mid-range laptop: animate `transform` and `opacity` only, draw simulations on `<canvas>` inside one `requestAnimationFrame` loop, and batch DOM updates (the equation-in-the-loop panel renders at most once per frame).
- Contrast at least WCAG AA (4.5:1 for text, 3:1 for large text and chart marks) on the dark background.
- Everything works from the keyboard: real `<button>` and `<input>` elements, visible `:focus-visible` rings, Escape closes overlays, focus returns to the control that opened them.
- `prefers-reduced-motion: reduce` turns off decorative motion and transitions; simulations still step, without easing.

## Type and numbers

- Inter for text, JetBrains Mono for code and figures, STIX Two Text for equations. All three are bundled for the offline app.
- Numbers that update live use tabular figures (`font-variant-numeric: tabular-nums`) so they do not jitter.
- Very small values are shown in scientific notation (`1.50×10⁻³`); values below 10⁻¹² display as 0.

## Color

Tokens: `--teal`, `--cyan`, `--violet`, `--gold`, `--green`, `--red` on `--bg`. Teal is diamond everywhere; gold is silicon carbide; violet is gallium nitride; red marks a limit or a failure. Color never carries meaning alone: every colored mark also has a label, a line style, or a legend entry.

## What we avoid

- Small uppercase "eyebrow" labels above headings, gradient text, and decorative motion running behind data.
- Emoji and dingbat glyphs as icons. Use `icon(name)` from `site.js` (inline SVG), or `data-icon="name"` on static markup.
- Text drawn over a plot's data. Labels and heads-up displays sit in reserved space; check every lab at 1280 and 390 pixels wide.

## Motion

- Interface transitions (hover, press, open, close): 150 to 250 ms, ease-out for entering, ease-in for leaving. Nothing animates on a keyboard action that repeats (arrow keys).
- Physics animations run at the model's own time scale, stated on screen ("slowed down about a million times").

## Every number is traceable

A lab's numbers come from a tested JavaScript module in `web/assets/sim/` that is checked against the Python package, and each lab lists its sources. A new equation panel is added to `adamas.loop` first: `tests/test_loop.py` fails until every symbol has a unit, range, and source, and `web/tests/loop.test.mjs` (run by `tests/test_web.py`) fails until every assumption has a checker and the browser arithmetic matches the Python golden values.
