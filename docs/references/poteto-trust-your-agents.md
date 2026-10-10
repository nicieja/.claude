# Lauren Tan on trusting agents (2,000 PRs in a month)

Lauren Tan (@poteto) gave this talk. She works on Grokbot at SpaceX AI and came from Cursor and, before that, the React team. She prepared it for Cursor Compile London and posted it on X on 2026-09-21 instead: https://x.com/poteto/status/2102050467505430555 (38:01).

These notes paraphrase X's auto-generated captions, with timestamps. The post claims 2,500 PRs and the talk claims 2,000.

Caption errors to read through: "Potato" is poteto, "Boone" is Dune, "GraphBot" is Grokbot, "bug bot" is Cursor's Bugbot, "lit rules" is lint rules. The names of the plugin ("PStack" / "PSNAC") and the control skill ("Control Glass") come from the captions and are unconfirmed.

## Thesis (00:00)

The PR count comes from trust in agents to produce high-quality work while she is away. Set up the agents' environment well enough and one person or a team can run what people call a software factory. She prefers the image of a Michelin kitchen, because the work is creative and nothing like an assembly line. Agents now cook the components. You still own the dish and the kitchen setup, down to the ratio of line cooks to dishwashers.

## Origin: performance work at Cursor (02:05)

Six months earlier she joined Cursor, before it became part of SpaceX AI, to fix performance in the new agents window that replaced the Cursor IDE. PRs landed faster than she could check them for regressions by hand with Chrome DevTools traces and heap snapshots. Frustration led to verification skills. With one, the agent runs the app and takes the traces itself, then finds hotspots and hill-climbs performance.

She never set the PR count as a goal. The skills, tools, and codebase changes added up to one idea: she was the bottleneck and had to move her engineering knowledge into her agents.

## The trust graph (05:14)

At one to five agents you babysit every chat and keep course-correcting. When you step away, the agents go wrong. She calls this the hardest stage to leave because the way out is unclear. The reason you cannot jump to a hundred agents is missing trust. Spawn a hundred anyway and you get slop PRs, regressions, and bugs in production.

## Verification (06:51)

Verification is a spectrum:

- Low end: verification skills. A skill gives the agent a way to run the app over the Chrome DevTools Protocol (or whatever debug protocol you have) and capture performance traces and heap snapshots.
- High end: formal verification with Lean or TLA+, proving business-logic invariants always hold. Still an open problem, and few teams can do it.

Verification skills alone get you far.

## The control skill: CLI plus feature map (08:37)

Her first Cursor skill let the agent run the app and take traces over CDP. It converged on two parts:

1. **A CLI inside the skill directory.** Agents call it to run the app and collect empirical evidence the same way in every session. It needs ongoing investment to cover more use cases.
2. **A feature map.** It works like a sitemap for agents, and she calls it materialized memory. It records what each feature does and how a user reaches it, down to keyboard shortcuts and the DOM elements to click. It lives in the skill directory in the codebase, and an automation updates it. She built it after vague Slack reports, such as a cropped screenshot captioned "???", where the agent ran the app but had to guess which part of the UI the user meant.

Together, agents can reproduce and interpret reports from internal and external users. The control skills became critical infrastructure the team maintains.

## Correctness is not quality (12:33)

Verification answers whether the feature does what you want (does the checkout button check out). It says nothing about performance or code quality. For that she built a plugin of skills (captioned "PStack") encoding her own playbooks for debugging, feature development, and prototyping. Senior engineers can contribute to a shared team repository of skills like this. Quality skills plus verification give work that is both correct and high quality, backed by real performance numbers and telemetry.

## Agent-friendly architecture (14:56)

She calls this possibly the most important investment. If agents will write all the code, the codebase has to make the right thing the default. The slide shows five layers, ordered from hard enforcement to soft guidance:

- **The codebase**, "the best form of memory". Agents extend the patterns they see in their context window. They will not refactor in every PR.
- **Making mistakes categorically impossible** through architecture, data structures, and algorithms. When an agent repeats a mistake, this works better than a lint rule.
- **Static analysis**: linters, compiler diagnostics, CI. Each repeated correction is a candidate lint rule.
- **Rules, Bugbot, skills**: guidance. Agents mostly follow it but can skip a rule, and the person piloting can ignore it.
- **The style guide**, enforced only by humans in review. At this PR rate humans cannot read every line, so do not rely on it. Use human review comments to find what the other layers are missing.

## Dune, Grokbot's framework (18:57)

Dune grew out of the agents window's performance problems. It starts from the observation that agents love taking shortcuts, so it makes the shortcut the right path. The result is locked down and annoying for humans, and ideal for agents with little context. That matters because contributors now include designers, PMs, and CEOs whose agents are piloted by busy people.

## Anti-patterns spread like a virus (20:31)

The reverse also holds. One workaround, or one comment explaining a workaround, gets copied, and within days or weeks it is the de facto pattern. Her second image is a garden: innocent workarounds multiply into a vibe-coded codebase that is painful to maintain and slow. The ideal agent codebase is so conventional and standardized that it is annoying for humans to write in.

Her best example is code comments (22:52). She first saw agent comments as harmless, since humans leave notes on edge cases and workarounds too. At Cursor she saw agents cite the surrounding comments as justification for papering over a problem instead of fixing it. Dune bans comments for that reason.

## The gardener role (24:28)

She wants a gardener on each team: someone who watches for unwanted growth and nips it in the bud before it propagates.

## Dune's three principles (25:14)

1. Delete the tech debt you already have.
2. Enforce one paved path for blessed patterns, so agents do not guess. Put enough guidance in the codebase, CI, and lint rules to hold them to it.
3. When you see tech debt or a bad pattern, the first instinct is a lint rule. It stops the bleeding before any cleanup. Then have agents clean up. The goal is a codebase you would be happy for an agent to copy.

## Dune's structure (26:42)

Dune has strict conventions on where code lives and what may import what. The captions name five concepts:

- Features, each co-located in one folder.
- An entry point in the React layer, which works like a route.
- Transcript pods, which render in the Grokbot app.
- A host, which runs on the Grokbot VM.
- A client, which powers the whole app.

One boundary keeps Electron main-process code out of the renderer, and the import dependency graph enforces it. In Cursor's agents window, slow code leaked into the renderer by accident. The renderer must chunk its work to stay under 16 ms per frame at 60 fps, or 8 ms at 120 fps.

## The lesson behind Dune (29:18)

She says any team can benefit from its own agent-friendly framework. It encodes your best engineers' tribal knowledge, the kind that used to live in style-guide review comments, into the codebase itself. The codebase is the materialized snapshot of the state you want agents to extend. A pristine codebase makes the next agent likely to continue the good pattern.

## Compounding layers (30:38)

The layers compound into trust. In a codebase where bad code is almost impossible to write, even an agent with little context or little reasoning writes good code. Kitchen version: if a cook keeps tripping over something, remove the hazard so nobody else trips.

## Grokbot as the outer loop (32:34)

Grokbot supplies the outer loop. Connect it to Slack, Datadog, Sentry, PlanetScale, and other services, and it aggregates that information to make decisions. Some people call this a brain for the company. She thinks plain tool use is enough, because agents are good at using tools. Grokbot routines subscribe to Slack threads and Sentry alerts and start cloud agents. Cursor automations and the SDK add more bots that reuse the same agent infrastructure. Her screenshots show automations that reproduce bug reports and open pull requests on their own.

## Close (35:15)

Climb the trust graph and you can parallelize, and the whole team can build on the agent infrastructure. She names one slide as the takeaway. Each correction you give an agent belongs in one of the five layers, and you check them in order. Make the pattern impossible through the codebase, architecture, and data structures. Failing that, use static analysis. Then layer rules, Bugbot, and skills on top, plus skills for code quality. Do all of it and you trust the environment enough to let agents run free. Her caveat is that it is not really a secret, and "it's a lot of hard work."
