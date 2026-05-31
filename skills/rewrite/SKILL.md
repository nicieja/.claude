---
name: rewrite
version: 1.0.0
description: |
  Rewrite an English working draft so it reads like a native speaker wrote it,
  in the author's own literary voice (distilled into voice-guide.md). Polishes 
  and re-voices prose — fixing first-language interference and sharpening rhythm, 
  register, and imagery — without changing what the draft means. Use to finish 
  drafts faster. Outputs the rewrite.
allowed-tools:
  - Read
  - Write
---

# Rewrite

Take an English working draft and rewrite it so it (1) reads like fluent native English and (2) carries the author's own voice — the fingerprint distilled in `voice-guide.md` (rhythm dial, em-dash habits, register collision, understatement, rationed imagery, ironic self-aware narrator, reframing last line). The draft's **meaning, plot, facts, POV, and intent stay fixed.** You re-voice; you don't co-author.

This exists to help the author finish drafts faster: hand it rough English, get back prose that sounds like them at their best.

## Arguments

- `/rewrite <text>` — rewrite the pasted text.
- `/rewrite <file path>` — read the file and rewrite it. **Output to chat; never overwrite the source** unless explicitly told to save.
- `/rewrite` (bare) — rewrite the draft under discussion in the current conversation. If there's no obvious draft, ask once: "What should I rewrite?"
- Add a steer in plain words: `/rewrite --light ...` or "light touch" (fluency + gentle rhythm only), "go further" / "make it sing" (full voice), "keep my paragraph breaks," "this is non-fiction," etc. Default intensity = **match the source** (see Step 2).

## When this is the wrong skill

- They want feedback or a critique of the writing, not a rewrite → just discuss it; don't invoke.
- They want something written from scratch (no draft exists) → this skill polishes existing prose; write it directly instead.
- The text is code, config, or a structured doc → out of scope; this voice is for prose.

## Instructions

Follow in order.

### Step 0: Get the draft

Resolve the input per **Arguments**. If it's a file path, Read it. If bare and there's a clear draft in the conversation, use that. If nothing is available, ask once what to rewrite — then stop and wait.

If the path is under `~/Library/Mobile Documents/` (iCloud) and the Read fails with a permission error, tell the user: the iCloud path is blocked by macOS privacy controls — ask them to paste the text, or point at a non-iCloud copy (e.g. under `~/Documents/…`).

### Step 1: Load the voice

Read `~/.claude/skills/rewrite/voice-guide.md` in full **before rewriting**. It is the spec. Do not rewrite from memory of it — load it every run, because it's the thing the author tunes over time.

### Step 2: Read the draft and set the dial

Read the draft closely and decide, briefly (don't narrate this to the user):

- **What it's trying to do** — genre, POV, tense, mood, who's speaking. These are constraints you preserve.
- **What it means** — the literal content, the facts, the beats. These are fixed.
- **Where it's reaching** — which passages are lyrical (can take the full voice) and which are functional or load-bearing-plain (fluency + light rhythm only).
- **Its problems** — non-native phrasings, flat rhythm, register that's all one note, buried or over-explained moments, a weak opening/closing.
- **Styling intensity** — default to *match the source*. A spare scene stays spare (sharpened); a rich passage can take more. Respect any explicit steer from the args. Err toward restraint — over-stylization is the documented #1 failure mode.

If the draft is non-fiction or functional text, apply the **fluency pass** and only the lightest voice touches (rhythm, em-dash, cut filler) — not imagery or metafiction.

### Step 3: Rewrite — two integrated passes

Work through the draft applying both, together:

**a. Native-fluency pass.** Fix first-language interference and anything that reads as non-native or stiff — articles, prepositions, collocations, calqued idioms, aspect→tense, word order/emphasis, comma habits, pronoun handling, diminutives. See "Sounding native" in the voice guide. Make these fixes invisible.

**b. Voice pass.** Apply the fingerprint *with restraint*, matched to the dial from Step 2:
- The rhythm dial — build long, then detonate short; isolate the decisive beat.
- The em-dash as the master joint; the punctuation habits.
- Sharpen the register collision instead of flattening it.
- Understate the emotional/violent peaks.
- Ration imagery around the draft's own center; cut ornament.
- Keep the narrator's ironic, self-aware distance where it fits.
- Strengthen the opening and the closing — short, reframing last line; ring composition if the draft invites it.

**Hard constraints (carry these the whole way):**
- Preserve meaning, facts, events, character actions, and the content of dialogue.
- Keep the author's POV and tense unless they're broken or internally inconsistent.
- Invent nothing — no new plot, characters, lines, or details.
- Tighten by default; don't let the rewrite balloon.
- It's the author's creative work. When a choice is genuinely ambiguous (is this awkwardness a mistake or intentional?), prefer the lighter change and flag it rather than overwrite it.

### Step 4: Self-check

Before outputting, reread your rewrite against the draft and the guide:
- **Meaning intact?** Same facts, beats, POV, tense. Nothing invented.
- **Native?** Would a native reader catch any L1 interference? No calques, article slips, stiff inversions.
- **Voice present but not parody?** The fingerprint shows, but no paragraph is overloaded with tics. Fragments are earned by surrounding length. Imagery is load-bearing.
- **Right intensity?** You matched the source's reach; you didn't gild the plain parts or flatten the rich ones.
- **Tighter or even?** Not padded.

Fix anything that fails, silently.

### Step 5: Output

Output the rewritten prose in a fenced code block (so the raw markdown — italics, em-dashes, paragraph breaks — copies clean into an editor like Obsidian). Put a short lead-in line above it ("Rewritten:").

Keep commentary minimal — the author wants speed. After the block, add notes **only if they matter**: a genuinely ambiguous choice you made, a spot you left alone on purpose, or a place where the draft's meaning was unclear. At most a line or two. Don't produce a change-log unless asked ("what did you change?").

If the user asked to save to a file, Write it to a **new** path (never the source), confirm the path, and still show the result.

## Key Rules

1. **Re-voice, never co-author.** Meaning, facts, plot, POV, tense, and dialogue content are fixed. Invent nothing.
2. **Load `voice-guide.md` every run.** It's the spec and the author tunes it; don't work from memory.
3. **Restraint is the whole game.** Over-stylization is the documented #1 failure. Match intensity to the source; when unsure, do less.
4. **Native fluency + voice, together.** Fix L1 interference invisibly *and* apply the fingerprint — both, in one rewrite.
5. **The voice is a range, not a costume.** Find the register the draft is reaching for and sharpen it; don't impose one mode.
6. **Tighten by default.** A good rewrite is usually shorter.
7. **Output clean and copy-ready.** Fenced block, minimal commentary, no forced change-log. Never overwrite the author's source files.
