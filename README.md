# SSH Login Explorer

Educational investigation workspace for Nathaniel Addai Gyarteng and Autenia Murray, Group 8. Built with Python, pandas, Plotly and Streamlit, with Codex assistance.

Public app: https://ssh-activity-group8.streamlit.app/

## Workspaces

- Overview: large source rankings, summary counts, time distribution, and a leading-address case shortcut.
- Investigation: username ranking, selectable time bins, original-message inspection, session notes, and a downloadable Markdown report.
- Pattern analysis: time heatmap, address-to-username Sankey flow, username-diversity profiles, and aligned two-address timelines.
- Evidence: literal message search, exact-subset CSV export, and downloadable filter metadata.
- Classroom: 30-minute lesson, three-question practice activity, worksheet download, instructor rubric, and proposed school rollout.
- Methodology: provenance, parser checks, separate repeat summaries, and interpretation limits.

The four analytical pages share IP, username, time, and message-account-label filters. Classroom exercises deliberately use the full sample. Small IP/username categories are grouped in the Sankey, preserving all selected records. Heatmaps show the leading 12 IPs and state that limit. No VM attack experiment is included.

## Verification

```sh
python -m unittest discover -s . -p 'test_dashboard.py' -v
```

Checks cover parser counts, aggregation conservation, all pages and chart modes, combined filters, empty results, evidence search, reset, and classroom answer checking. These are software checks, not user-study results.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows activate with `.venv\Scripts\activate`.

## Deploy

In Streamlit Community Cloud, select this repository, main branch, and app.py as the entry point. Choose Python 3.11 if offered. All data is included; no secrets are needed.

## Findings

2,000 source log records; 518 explicit failed-password records; 23 source IPs; 63 usernames. IP 183.62.140.253 appears in 286 failed-password records. Root appears in 368 overall; 276 records match both that IP and root. Ten repeat-summary messages are kept separate.

## Scope

These are record counts, not unique attackers or sessions. Repeated failures do not prove an attack. The source has no year or timezone. User evaluation is planned and has not been conducted.

## Data source

https://github.com/logpai/loghub/tree/master/OpenSSH

Original structured CSV downloaded October 25, 2026, retained unchanged. Consult upstream for dataset terms and citation information.
