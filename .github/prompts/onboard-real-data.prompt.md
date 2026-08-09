---
description: Start a guided source-by-source onboarding of real work-environment data into the canonical site-analysis model.
agent: Agent M - Data Onboarding Facilitator
---

Start the real-data onboarding workflow for this cloned repository.

First:

1. Read `docs/COPILOT-WORK-ONBOARDING.md` and the required architecture/methodology documents referenced by Agent M.
2. Summarize the repository's canonical source domains, identity model and the rule that real source schemas remain unchanged while mappings/crosswalks adapt them into the canonical model.
3. Check whether a local onboarding inventory already exists under `data/onboarding/`; if it does, resume from it instead of restarting.
4. Check whether local mapping/crosswalk files already exist and preserve prior approved work.
5. Begin with the first unresolved source domain in the recommended onboarding order.

For that domain:

- explain what the canonical model expects;
- explain why this source matters to downstream analysis;
- ask me to identify the corresponding real local file/table/workbook/JSON/view;
- after I identify it, inspect its schema/attributes;
- propose mappings with confidence and mapping type;
- separate field mapping from identifier/value crosswalks;
- ask targeted questions for ambiguity;
- create only proposed local artifacts until I explicitly approve them.

Do not ask me to provide all sources at once.
Do not infer identity relationships from names/addresses without explicit validation.
Do not modify A/B/C/T/E/R to compensate for incomplete mappings.
Do not run Agent A until at least one real pilot building produces a trusted canonical `site_context.json` and I confirm the context is accurate.

Keep a concise onboarding status summary throughout the session.