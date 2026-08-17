# CJK Line-Break Defects

Applies whenever a rendering carries Korean, Japanese, or Chinese body or display text. Latin-script wrapping rules do not detect these defects: the Latin orphan check asks whether one stray word sits alone on a heading's last line, while these are phrases cut where the grammar does not allow a cut.

Two rules govern the whole pass:

- Every class below is blocking on its own merits. A high automated similarity score against a reference never clears one — reference and implementation can wrap badly at the same width, and the diff will call them identical.
- Check every page's rendering, never a sample. Line breaking is a function of the exact container width and the exact string, so a clean wrap on one page says nothing about the next.

## Defect classes

1. **Orphaned particle or grammatical ending** — a particle or inflectional ending pushed alone onto the next line, away from the word it attaches to. Rendered as `핵심 자료 / 도` or `끝에서 / 만난다`.
2. **Subject or topic phrase split from its predicate** — a short clause broken across lines where the whole clause would fit on one. Rendered as `두 강은 / 끝에서 만난다`.
3. **Connective or auxiliary expression split mid-phrase** — a multi-token grammatical construction cut in the middle, as in `쓸 수 / 있지만`; worse when the break lands inside a single word and its particle, as in `방 / 식이`.
4. **Parenthetical or citation string broken across lines** — a bracketed source or reference split at the wrap, as in `(Vaswani et al. 2017, Attention Is / All You Need)` or `(Schulman et al. 2017); AlphaGo (Silver et al. / 2016)`.
5. **Oversized heading or narrow container producing a fragment line** — a display size that strands a single character or a final syllable on the last line, or that splits a semantic phrase where the meaning breaks: `놀라운 변 / 화`, `에이전트 오케스트 / 레이션 현황 및 미 / 래`. This is a defect, not acceptable wrapping.
6. **Label detached from its content** — a bracketed or bracket-style label such as `[Image #1]` wrapping away from the item it labels.

## Glyph-level defects to flag in the same pass

While reading CJK text in a capture, also record: baselines or descenders clipped because the line box is too short for the script; missing glyphs rendering as tofu boxes; and font-metric mismatch, where CJK glyphs sit on a visibly different baseline or at a different optical size from the Latin text beside them.

## Reporting

Report each finding as `<class> — <the break, as rendered> — <page/region>`, quoting the two lines with a `/` at the wrap point exactly as the examples above do. The break position *is* the finding; a paraphrase ("the heading wraps awkwardly") loses the only detail a fix can act on.

## Provenance

The defect classes and their example strings are adapted from a third-party visual-QA rubric, restated here in this repository's words. The examples are Korean because the source's were; the classes apply to Japanese and Chinese text equally.
