# A pilot lesson for beginning cybersecurity analysts

## Goal

Students will distinguish a log event from an attack claim, combine filters correctly, and cite original evidence. This is a proposed teaching use, not a completed deployment in a school or a validated training program.

## Thirty-minute lesson

1. Five minutes: identify the username, network address, time, and outcome in an original message. Explain that OpenSSH concerns remote access.
2. Ten minutes: find the leading source address; add username root; compare timing. Visit the heatmap and explain what darker cells represent.
3. Ten minutes: write a short observation supported by a source LineId, then explain what cannot be concluded. Inspect how grouping affects the Sankey view.
4. Five minutes: submit the matching CSV, filter metadata, and Markdown investigation report.

## Suggested rubric

Correct filters: 2 points. Traceable evidence: 2 points. Interpretation including limitations: 2 points. The built-in three-question practice score is formative feedback, not a verified measure of analyst competence.

## Pilot rollout

One instructor first rehearses the activity and verifies the public app or local installation. Students work with the same included public sample. Pair work can support students unfamiliar with Python. No Python installation is needed for browser use. Students download work before closing the session. The app has no roster, persistent gradebook, or institution login. A school should evaluate accessibility and learner feedback before wider use. The underlying source is public; a real organization’s private logs should not be substituted into a public deployment without an appropriate separate data-handling design.

## Proposed evaluation

Compare the dashboard and searchable table using equivalent questions. Alternate the interface order. Record correctness and task completion time, then collect usability feedback. A task start/end time should measure active task work consistently. Report participant count, task details, limitations, and anonymized aggregate results. No such results are available yet.

## Answer key

Leading source address: 183.62.140.253. Its explicit failed-password count: 286. With username root: 276. Overall explicit failed-password records: 518. All source records: 2,000. Repeated failures alone do not prove an attack.
