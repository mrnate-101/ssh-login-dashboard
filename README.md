# SSH Login Explorer

Working educational prototype for Nathaniel Addai Gyarteng and Autenia Murray, Group 8. Built with Python, pandas, Plotly and Streamlit, with Codex assistance.

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
