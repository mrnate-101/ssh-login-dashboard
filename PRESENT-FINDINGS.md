# Presentation findings and demo

## Nathaniel: introduction and data

“Our project explores failed SSH login activity through an interactive dashboard. We use a public OpenSSH sample from Loghub. We have built a working Python prototype that prepares the data, displays charts, and lets users filter records and inspect original messages.”

“The source contains 2,000 log records. We identified 518 messages that explicitly report a failed password. Those records include 23 source IP addresses and 63 usernames. We keep repeat-summary messages separate.”

## Autenia: findings and demo

“The leading source address, 183.62.140.253, appears in 286 failed-password records—about 55% of the sample's 518 explicit failed-password records. This concentration gives us a starting point for investigation.”

Select that IP in the sidebar; show 286.

“Root appears in 368 failed-password records across all addresses—about 71%. Combining the leading IP address with root returns 276 records.”

Add root to the username filter; show 276.

“The timeline shows when the matching records occur. We can narrow the time range and inspect the original messages to check the evidence behind the charts.”

Show the timeline, then read a matching message. Reset afterward.

## Both: interpretation and next steps

“These are counts of log records, not unique attackers or sessions. Repeated failed passwords warrant investigation but do not prove an attack. Our next step is to compare the dashboard with a searchable table, measuring classmates' accuracy, completion time, and feedback. That evaluation has not been conducted yet.”

## Short answers

- Python is the language; pandas processes data, Plotly draws charts, and Streamlit provides the interface.
- Horizontal bars support comparing counts with readable category labels. Time bins show temporal activity, including empty intervals.
- Source clock times span December 10, 06:55:46–11:04:45; no year or timezone is supplied.
- All 518 explicit failed-password messages passed the current parsing checks.
- Ten repeat-summary messages are separate from the main counts.
- No machine learning or automatic attack classification is implemented.
- Code is on GitHub at https://github.com/mrnate-101/ssh-login-dashboard . Only claim cloud deployment once a public dashboard link is verified.
