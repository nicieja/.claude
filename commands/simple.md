---
description: Restate your last message, or a text file, in Simplified Technical English
argument-hint: "[path]"
allowed-tools: Read, Edit, Write
---

## Your task

Rewrite some text in ASD-STE100 Simplified Technical English. The user wants a version that is easier to read.

The argument is: `$ARGUMENTS`

- If the argument is empty, the text is your last message. Say it again in STE.
- If the argument is a file path, the text is the prose in that file. Read the file, rewrite the prose, and write the result back to the same file.

Follow the STE rules:

- Use short sentences. Keep procedural sentences to 20 words or fewer, and descriptive sentences to 25 words or fewer.
- Write one instruction per sentence.
- Use the active voice. Name the agent of each action.
- Use the simplest verb tense: present, past, or future. Do not use progressive or perfect tenses.
- Use only approved words, and use each word in one meaning only. Replace jargon with a plain equivalent, or define the term in a short sentence.
- Use articles (*a*, *an*, *the*) before nouns. Do not remove them.
- Do not use noun clusters of more than three words.
- Use vertical lists for steps and conditions.
- Keep paragraphs to six sentences or fewer.

Rules for the restatement:

- Keep the same content. Do not add new claims, and do not remove a caveat that changes the meaning. If a nuance cannot survive the simplification, keep the nuance and add a second sentence for it.
- Keep the technical terms that name real things — file paths, command names, identifiers, and API names. Simplify the prose around them.
- If the text is code, explain what the code does in Simplified Technical English. Do not rewrite the code.

Rules for the last-message mode:

- Give the restatement only. Do not add a preamble, and do not explain what you changed.

Rules for the file mode:

- Rewrite only the prose. Keep front matter, code blocks, tables, links, headings, and list structure as they are. Do not change the file format.
- Keep the file's own voice where STE allows it. The goal is a clearer file, not a different document.
- After you write the file, report in one or two sentences how many paragraphs you changed and where the rewrite lost a nuance, if any.
