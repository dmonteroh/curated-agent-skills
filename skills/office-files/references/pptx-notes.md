# PPTX Notes

Key parts:

- `ppt/slides/slide*.xml`: slides
- `ppt/presentation.xml`: slide ordering and metadata

Text nodes:

- `a:t`: text runs

Slides often have repeated decorative text placeholders; extraction is best-effort and may include repeated headers/footers.

## Slide order comes from the relationship graph, not from filenames

The `slide*.xml` glob above finds slide parts; it does not put them in order, and it is not the set of slides the deck shows. Resolve the graph instead:

1. Read `ppt/presentation.xml` and take its `p:sldId` entries in document order — that is the deck's order.
2. Each `p:sldId` carries an `r:id`. Resolve it through `ppt/_rels/presentation.xml.rels` to get the slide part.
3. Resolve each `.rels` target relative to the part that owns the `.rels` file (a target beginning with `/` is package-absolute instead).

After a deck has been reordered, `slide7.xml` can be the second slide. After a deletion, a slide part can stay in the package with no relationship pointing at it — present in the ZIP, absent from the deck. Numeric filename order is a guess, and where it happens to be right it is right by coincidence.

## Part map

| Need | Parts |
| --- | --- |
| Slide order | `ppt/presentation.xml`, `ppt/_rels/presentation.xml.rels` |
| Slide text and shapes | Slide parts resolved from the presentation relationships (commonly `ppt/slides/slideN.xml`) |
| A slide's layout, notes, images, and charts | `ppt/slides/_rels/slideN.xml.rels` |
| Template geometry | `ppt/slideLayouts/`, `ppt/slideMasters/` |
| Colors and fonts | Theme parts resolved from the presentation or master relationships (commonly under `ppt/theme/`) |
| Speaker notes and comments | `ppt/notesSlides/`, `ppt/comments/` |
| Media and embedded objects | `ppt/media/`, `ppt/embeddings/` |

A slide's own `.rels` file is where its layout, images, charts, and notes are found — a slide part alone does not name them.

## Theme colors are tokens

A shape fill is frequently a scheme reference (`accent1`, `dk2`, `lt1`) rather than a literal value, and its rendered color depends on the theme and on any layout or master override. Report the token as a token. Inventing a resolved hex value that was not read from the color scheme is a fabrication, and it is the fabrication most likely to be copied into a brand summary.

## What the deck reports about itself

Retain, per slide: the position in the resolved order, the resolved part name, the concatenated text, shape counts, notes, and the relationship types found. Hidden slides (`show="0"` on the `p:sldId`) count in the package and not in the delivered presentation — say which, rather than dropping them silently.
