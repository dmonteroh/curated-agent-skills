# Named layout primitives

A shared vocabulary for spatial structure, used to compose shells instead of re-deriving an ad-hoc flex or grid arrangement per screen. Naming the primitive makes a spec and a handoff precise: "wrap it in a `sidebar` with a narrow fixed aside" beats "put it on the left, roughly". A primitive describes a spatial job, never a product category — see "Choose a layout by spatial shape, not by product label" in `SKILL.md`.

| Primitive | Spatial job | Core mechanic |
| --- | --- | --- |
| `stack` | Vertical rhythm between siblings | flex column + `gap`, or `> * + *` margin |
| `cluster` | Wrapping row of items (tags, actions) | `flex-wrap: wrap` + `gap`; wraps before it overflows |
| `content-limiter` | Readable prose measure inside a fluid parent | `max-inline-size` at a readable measure + `margin-inline: auto` |
| `sidebar` | Narrow aside beside fluid main, wraps when tight | flex; aside on a fixed basis, main with a `min-inline-size` floor, both allowed to wrap |
| `switcher` | N equal regions: a row when roomy, a stack when tight, with no breakpoint | flex with a `min()` basis, so it flips at a content threshold rather than a viewport width |
| `cover` | Centred region between optional header and footer, at least viewport tall | grid rows `auto 1fr auto` + a viewport-height floor |
| `frame` | Media held to an aspect ratio | `aspect-ratio` + `object-fit: cover` |
| `reel` | Row that scrolls horizontally instead of wrapping | inline-axis `overflow: auto` + `scroll-snap`; keyboard access declared explicitly |
| `imposter` | Overlay centred over a parent without changing document order | `position: absolute` + translate; never used to reorder focus |
| `overlay-stack` | Several layers deliberately occupying one cell | one grid cell, every child on `grid-area: 1/1` |
| `scroll-body-shell` | Fixed shell regions, only the body scrolls | the bounded scroll shell in `SKILL.md` |
| `fixed-sidenav-shell` | Side nav stays put, main scrolls | grid columns `auto 1fr`; main is the scroll owner |
| `list-detail` | Explorable list beside its detail region | two-column grid, with each pane's scroll ownership named |
| `sticky-aside` | Support content stays visible through a long read | `position: sticky` on the aside, document scroll |

Every primitive that scrolls (`reel`, `scroll-body-shell`, `fixed-sidenav-shell`, `list-detail`) inherits the scroll-ownership and `min-height: 0` rules from `SKILL.md`. Composing two of them does not compose their scroll containers: the region still declares one owner.

## Chosen defaults

Two starting values appear when these primitives are written out: a readable measure of roughly 65 characters for `content-limiter`, and roughly 20rem for a narrow aside in `sidebar` or `fixed-sidenav-shell`. Both are chosen defaults, not measured thresholds — set them against the type scale and content in use, and treat a different value as a normal outcome rather than a deviation.

## Boundary

A primitive owns spatial structure only. It sets no color, typography, shadow, radius, or motion value; those come from the visual system defined earlier in the workflow. Reaching to put a brand color on a primitive is the signal that the styling should wrap or compose around it instead of being folded into it.

## Lineage

The primitive set follows the layout vocabulary published in Every Layout (Heydon Pickering and Andy Bell) and in web.dev's one-line layouts, restated here in this skill's terms.
