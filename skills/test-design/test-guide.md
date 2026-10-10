# Test guide

The reference `test-design` loads every run. It defines the purpose of a test and the choice of what to test. It also covers the automation and the ruling on a test that already exists. Tune it over time, because it is the spec.

## The purpose of a test

The goal is fast, trustworthy feedback on the behaviors users actually depend on. Coverage is only a proxy, and suite size is vanity. Defects released to production are the only metric that maps end-to-end to user pain.

**Quality is a property of the whole process.** It emerges from how the team writes, reviews, tests, and releases code. A separate QA phase at the end of a sprint is a sign the rest of the process is leaking.

**Test capabilities, not features.** Brainstorm what a feature *lets users do* and what it *prevents them from doing*. "Feature X works" is a checkbox. But "users can recover their account when they've lost their phone and their backup email" is a capability, and a far better organising principle for tests.

**Test behavior rather than the code beneath it.** Ask "how would I know if this works *well*?" before "does it run?" Define what "good enough" means in user-visible terms before tying it to a technical solution.

**Risk drives investment.** A payments flow with thin coverage is an emergency. A rarely-touched internal admin tool with thin coverage is a shrug. Map test investment to consequence × likelihood, not to lines of code.

**Document trust boundaries.** Before designing tests for a feature, state how much you trust adjacent teams and third parties. State the same for upstream services. Then write checks within the boundary. A "test" of someone else's API is a contract assertion rather than a unit test. Treat it as a contract assertion.

**A flake is a failure.** "Rerun and merge" trains the team to ignore real failures. Track flake rate, treat it like any other broken test, and quarantine before it corrupts the team's relationship with the suite.

## Designing tests

**Start with always/never.** Absolute statements about a feature reveal key risks fast. "An order can never be dispatched without payment" / "A session always expires within 24h": each one is a test (or a family of tests) waiting to be written.

**Explore the user-state paths.** The happy path is the floor, not the ceiling. Also test these paths:

- the scary path (what makes the user nervous)
- the angry path (what a frustrated user does)
- the delinquent path (the bad-faith actor)
- the embarrassing path (data they don't want exposed)
- the desolate path (zeros, nulls, blanks, missing data)
- the forgetful path (interrupted flows)
- the indecisive path (back-and-forth, abandoned carts)
- the greedy path (max sizes, abuse)
- the stressful path (load, time pressure)

**Focus on key examples, and contrast them with counter-examples.** Too many examples or overly complex ones are a symptom that some business concept isn't explicitly described. Counter-examples (what *shouldn't* happen) provide the contrast that makes the rule clear.

**Describe what, not how.** The most common acceptance-criteria mistake is mixing the purpose of the test with the mechanics of executing it. Capture *what should be true*, and leave the mechanics of the check to the test code.

**Each test covers one topic.** Multiple actions in one test, or sequences run with slightly different parameters, are signs of unfocused tests. Split them.

**Write assertions first.** Starting from the outputs makes it hard to test many things at once and hard to hide wrong assumptions. The more concrete the output, the less room for vague verification.

**Split technical and business checks.** One overarching test that mixes "the API returned 200" with "the customer was charged the right amount" is harder to read, harder to maintain, and obscures which layer broke.

**Snoop on the competition.** Investigating competing products and the bugs they released is a cheap source of testing ideas grounded in things that *actually happened* rather than theoretical risks.

**Use classical techniques where they fit.** Most production bugs come from edges, not the middle of the input distribution.

- Equivalence partitioning: group inputs by class, and test one of each.
- Boundary value analysis: test the edges (0, max, max+1, off-by-one).
- Decision tables: use them for combinatorial conditions.
- State transitions: use them for orders, sessions, and accounts.
- Pairwise testing: use it when full combinatorics explode.

**Treat too many boundaries as a modelling problem.** If a feature is hard to test because it has dozens of edge cases, the issue is usually the model, not the tests. Push back on the design before adding more tests.

## Building the automation

**Wait for events, not time.** `sleep(2)` is the most common cause of flake. Use completion notifications, polling-with-timeout, or the framework's `waitFor` primitives. If the system has no event to wait for, that's a design gap to raise with the team.

**Split data generators from tests.** Generators belong outside the test body. Each component gets maintained separately. Generators can then be replaced with better versions without touching tests, and tests stop being landfills of setup boilerplate.

**Minimise UI interactions.** Even when a test must run through the UI, limit the UI portion to the steps that need it and push the rest to the API or service layer. UI tests are slow, fragile, and often catch the same bugs an API test catches in a fraction of the time.

**Isolate aggressively.** Each test creates and controls its data. Never depend on order or shared mutable state. Containerize where possible, pin versions. Tests that pass on one box and fail on another are not tests, they're environmental dice rolls.

**Frameworks hide boilerplate and surface failures clearly.** Use a Page Object Model or an equivalent abstraction for UI tests, and fixtures and factories over inline setup.

**Optimise for reading, not writing.** Tests that are easy to understand are easy to update and easy to trust when green. They are also fast to debug when red. A clever framework nobody understands is worse than a verbose scripted one. Descriptive names (`test_password_reset_with_expired_token_returns_410` beats `test_pwd_3`) and assertion messages that explain what went wrong without reading the test source pay for themselves.

**Organise by behavior or feature, not by work item.** Tests grouped by "ticket JIRA-1234" rot the moment the ticket closes. Tests grouped by user workflow, business area, or component survive feature growth.

**Some things shouldn't be automated.** Truly exploratory testing, accessibility nuance, visual judgment calls, one-time validation. Don't burn a week automating a check the team runs once a quarter.

## Coverage and what it means

**Decouple coverage from purpose.** Decide what each test is *for* first, then choose the format that fits. A coverage number with no purpose is a vanity metric. A purpose with no measurement is unverifiable.

**Avoid strict coverage targets in isolation.** A 90%-line-coverage gate produces shallow tests written to satisfy the gate. Use coverage as one signal among several, never as proof that something is well-tested.

**Mutation coverage reveals what line coverage hides.** Line coverage shows what executed. Mutation coverage shows whether tests actually fail when the code is wrong, and that is the measure that matters.

## Judging a test that already exists

A test stays when it protects a behavior that a user or a caller depends on, and no other kept test already protects that behavior. Cheap tests of real behavior stay too. A test is surplus when one of these is true:

- It tests the framework, a library, or the language instead of this code.
- It restates what the type system or the schema already guarantees.
- It pins internal details instead of behavior.
- It builds a state that no production caller can produce. That test is armor, the same as a guard for that state (see `~/.claude/AGENTS.md` and `/code-unguard`).
- It is green whether or not the change is present, so it does not exercise the change.
- It covers several topics at once and a focused test already covers the one that matters.
- It is a near-duplicate of a clearer test.

When near-duplicates compete, the clearest one stays. A test that would stay but reads badly gets a one-line rewrite suggestion, and the ruling does not depend on the rewrite.
