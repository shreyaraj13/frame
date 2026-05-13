# Sample Explorer output

This is the actual `ExplorationResult` Explorer produced on its first end-to-end run with real Claude Sonnet 4.6 + Tavily, 2026-05-14. No hand-edits — the rendering below is just the JSON reformatted into readable Markdown.

**Input idea (verbatim):**
> "Productivity apps have the highest churn rate out of all B2C apps, so users are not finding productivity apps useful."

**Why this is an interesting test:** the input isn't a clean product concept — it's a problem observation with an embedded causal claim ("high churn → users don't find them useful"). One of Explorer's hard rules (#10) is that it must surface assumptions like this *as assumptions to test*, not as accepted premises. The output below shows it did.

**Run stats:** ~$0.30 Anthropic + 6 Tavily searches, 4 min wall clock, 22 KB of structured output. Source diversity: 11 Reddit threads across 7 subs, 2 HN posts, 4 blogs, 2 academic / clinical sources (NCBI, UCL CHI paper), 1 review site. No single source contributes more than 2 of 22 signals.

Raw JSON: `/tmp/frame_exploration_001.json` (not committed — regenerate via `make explore IDEA="..." CONFIRM=yes`).

---

## Context auto-detection

```json
{ "geography": "global", "inferred": true, "confidence": "high" }
```

No India-context signals in the input — defaulted to global, high confidence.

---

## Adjacent problems (7)

Explorer surfaced 7 distinct problems in the idea's neighborhood. Each is phrased as user-felt pain (per rule: not a solution, not a symptom). Each carries a `relationship_to_idea` explaining why Synthesizer should care.

1. **System-maintenance becomes a second job.** Users spend more time configuring than working. *Distinct from "not finding value" — they found value conceptually, but maintenance cost exceeded the benefit.*

2. **Neurodivergent users are systematically failed.** Apps built for neurotypical linear planning leave ADHD / anxiety / executive-dysfunction users unserved. *Their failure modes are categorically different from neurotypical users'.*

3. **App-shopping IS the procrastination.** Searching for and setting up new apps substitutes for actual work. *Acquiring high-intent app-switchers may mean acquiring the least retainable cohort by design.*

4. **Shame-and-guilt cycles drive abandonment.** Churn is an emotional coping mechanism, not a preference signal. *A solution would need to design for recovery from failure states, not just initial onboarding.*

5. **Apps can't ingest behavioral context.** Energy, interruptions, cognitive load — tools feel divorced from real life. *A modeling problem, not a UI problem.*

6. **Power-user over-investment churn.** Notion / Obsidian power users abandon elaborate systems because maintenance complexity outpaces value. *Distinct churn pattern from casual users — solutions for one will exacerbate the other.*

7. **Useful → finite → churn (lifecycle signal).** Apps that genuinely helped during a deadline crunch get abandoned afterward. *Directly challenges the idea's framing that churn equals "not useful."*

---

## Context constraints (4 of 4 max)

Problems that shape viability without being directly solvable:

1. **Behavior change requires more than software** — environmental redesign, social accountability, iterative steps. App-only solutions have a structural retention ceiling.
2. **App-store ranking incentives are misaligned** — downloads + short-term engagement get rewarded, not long-term behavior change.
3. **Market saturation creates user skepticism** — accumulated failed-app priors make every new entrant fight uphill.
4. **Productivity is culturally loaded** — tied to identity and self-worth; failure carries psychological weight that suppresses rational switching demand.

---

## Stakeholders (5 of 5 max, 3+ distinct types as required)

| # | Name | Type | Relationship to problem | Internal tensions |
|---|------|------|------------------------|-------------------|
| 1 | Knowledge workers & individual productivity seekers | `user` | Download to solve overwhelm; churn when process overhead exceeds felt progress | Want "just works" vs. drawn to feature-rich setup; seek accountability while resisting control |
| 2 | Neurodivergent users (ADHD, executive dysfunction) | `user` | Disproportionate share of high-churn — mainstream apps built for neurotypical linear planners | Most motivated to try AND most likely to abandon; abandonment triggers shame spirals |
| 3 | Productivity-app founders & indie devs | `competitor` | Build into a high-churn landscape where user behavior-change failures are attributed to the product | DAU/WAU demanded by investors may indicate the app generates busywork |
| 4 | App Store platforms (Apple / Google) | `gatekeeper` | Control discoverability; high churn depresses rankings, creating a visibility penalty | — |
| 5 | Behavioral scientists & productivity influencers | `influencer` | Shape user expectations via GTD / PARA / Atomic Habits; their systems get adopted wholesale but aren't validated against general user capacity | Commercial benefit from teaching complex systems vs. what users actually need |

---

## Assumptions (6)

The 4-test bar: each assumption is **specific** to this idea's framing, **testable** through evidence, **consequential** if wrong, **buried** in the original framing.

| # | Assumption | Criticality | Failure consequence |
|---|------------|-------------|---------------------|
| 1 | Users abandon productivity apps primarily because the apps are poorly designed | **high** | If churn is behavioral/psychological, better design fixes nothing |
| 2 | **High churn reliably signals "users aren't finding value"** *← the user's exact causal claim, surfaced as an assumption* | **high** | If churn is often a lifecycle signal (need ended), the problem definition is wrong |
| 3 | A standalone app can address productivity needs without coaching / accountability / environmental design | **high** | If lasting change requires systemic scaffolding, app-alone retention has a hard ceiling |
| 4 | Frequent app-switchers are retainable for a well-designed new entrant | medium | Switchers may BE the procrastination behavior — structurally low-value cohort |
| 5 | The productivity-failure problem is homogeneous enough for one design | medium | ADHD vs. minimalist vs. GTD power-users fail for categorically different reasons |
| 6 | Users genuinely want behavior change and will sustain habits with the right tool | medium | If many prefer to *feel* productive over *being* productive, app efficacy doesn't move retention |

**Notable:** Assumption #2 is exactly what we wanted Explorer to surface. The user's input said *"so users are not finding productivity apps useful"* as a causal claim. Rule #10 says Explorer must not reframe the idea — it must surface assumptions like this as testable. It did.

---

## Contradictions (2)

Structural conflicts between signals — flagged with the specific signal ids supporting each side.

### 1. Complex apps fail vs. simple apps fail
*Genuine user-segment split, not a design error.*

- **Claim:** Too complex / feature-heavy / maintenance-intensive → users abandon. *Signals: s4, s5, s6, s7, s18*
- **Counter:** Too simple → power users abandon because they lack depth. *Signals: s8, s19*
- **Note:** Different populations fail for opposite reasons. Optimizing for one worsens churn for the other.

### 2. Psychology problem vs. UX problem
*Two distinct theories of failure with supporting signals on each side.*

- **Claim:** Apps fail because they don't address behavior change — the problem is inside the user. *Signals: s1, s12, s13, s14, s20*
- **Counter:** Apps fail from concrete UX issues — onboarding, confusing UI, missing features. *Signals: s16, s2, s7*
- **Note:** Both have supporting signals. Conflating leads to misdiagnosed solutions.

---

## Signals (sample of 22, verbatim with sources)

The full set is 22 quotes spanning 7 subreddits, 2 HN threads, 4 blogs, 2 academic / clinical sources, 1 review site. Six representative ones:

- **s1** — *"The fundamental problem with most productivity apps, trackers, and to-do list software is that they don't address the psychology behind productivity."* — [r/ProductivityApps](https://www.reddit.com/r/ProductivityApps/comments/1eys2l5/whats_wrong_with_productivity_apps_rant/) (forum)
- **s5** — *"I found myself spending more time organizing everything in Notion than actually getting things done. It was becoming a bit of a productivity drain."* — [r/Notion](https://www.reddit.com/r/Notion/comments/1axwg6n/why_i_ditched_notion_after_5_years_my_experience/) (forum)
- **s9** — *"due dates and checkboxes had turned my task list into a scoreboard I was always losing"* — [xda-developers](https://www.xda-developers.com/no-to-do-list-experiment/) (blog)
- **s12** — *"When our autonomy is threatened, we feel constrained by our lack of choices and often rebel against doing the new behavior. Psychologists call this 'reactance.'"* — [Nir and Far](https://www.nirandfar.com/why-behavior-change-apps-fail-to-change-behavior/) (blog)
- **s14** — *"Most productivity apps assume unlimited self-control... This assumption contradicts decades of behavioral science. Self-control is a limited resource."* — [readunwritten.com](https://www.readunwritten.com/2026/02/04/why-productivity-apps-fail/) (blog)
- **s18** — *"Where are the second brain apps that don't feel like a second job?"* — [r/ObsidianMD](https://www.reddit.com/r/ObsidianMD/comments/1eglzk7/where_are_the_second_brain_apps_that_dont_feel/) (forum)

---

## What this would feed Synthesizer (next agent, not yet built)

Synthesizer's job is to take this output and draft **3 candidate problem statements** with tradeoffs, then recommend one — for human approval at Gate 1 before the pipeline moves into solution space.

From this output, the natural problem-statement candidates split along the contradictions and high-criticality assumptions:

- **"Productivity apps fail to model human behavioral context"** — anchored in problems 5, 4, 7 + assumption 1
- **"Productivity apps over-deliver complexity to under-served populations"** — anchored in problems 1, 2, 6 + contradiction 1
- **"App churn is a lifecycle signal, not a failure signal"** — anchored in problem 7 + assumption 2 (challenging the user's framing directly)

The user picks one at Gate 1, Synthesizer locks it, and the pipeline proceeds to Ideator. Killed candidates remain visible in the final PRD's "Alternatives Considered" appendix.
