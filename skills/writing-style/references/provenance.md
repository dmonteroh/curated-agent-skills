# Provenance

Credits and licence facts. Nothing here changes how an agent writes, which is why it is its own file: it is never worth loading during work.

## The ASD-STE100 licence

The standard's dictionary holds roughly 900 approved words, each restricted to one meaning and one part of speech, plus roughly 1,200 words to avoid with suggested replacements. It is free to obtain and **not** free to redistribute: reproduction requires written authority from ASD, granted freely only to a listed set of organisations that this library does not belong to. The dictionary therefore stays out of this repository.

The consequence is specific rather than cosmetic. Every rule defined by "use an **approved** word" degrades from a checkable standard into a preference for the plainer word. Rule L13 in the linter exists to stop any output claiming otherwise. For documentation that must actually conform, obtain the standard and check word by word against the real dictionary.

## Sources

- ASD-STE100 official site: `asd-ste100.org`, including its About page and its downloads request form.
- ASD Europe's Simplified Technical English page.
- The Wikipedia article "Simplified Technical English".
- TechScribe's ASD-STE100 summary.
- SKYbrary's Simplified Technical English entry.

Rule numbers cited in `writing-guide.md` (3.7, 8.1, 9.3) come from those public descriptions of Issue 9, January 2025. Verify them against the standard itself before quoting them anywhere that matters. This skill paraphrases rule categories and reproduces no part of the standard's text, and it cannot certify conformance. The sentence and paragraph caps are a chosen default measured from eight documents this library treats as good writing. The measurement lives in `scripts/writing_lint.py`.

**Absorbed rule sources**, 2026-08-26. The negation-pivot and emoji bans follow `company-copywriter`, an internal brand skill. Most structural tells follow this library's `prose-de-slopping` catalogue, adapted from Wikipedia's "Signs of AI writing". The tiered vocabulary of rules A08 and A20 — band one fires per hit, band two only in clusters — follows `conorbronsdon/avoid-ai-writing` (MIT). No frequency claim is carried from any of them: that third source states plainly that its own "5 to 20 times more common in machine text" figure is inherited and unmeasured. The word lists here are authored judgements, and severity was set by measuring each rule against prose this library already accepts.
