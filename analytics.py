import pandas as pd
from analysis import clock_label

def ranking(frame, column):
    return frame.groupby(column).size().reset_index(name='Records').sort_values(['Records', column], ascending=[False, True]).reset_index(drop=True)

def time_counts(frame, seconds, minutes=5):
    step = minutes * 60
    counts = (frame.second // step * step).value_counts().reindex(range(seconds[0] // step * step, seconds[1] // step * step + 1, step), fill_value=0).sort_index()
    return pd.DataFrame({'Time': [clock_label(s) for s in counts.index], 'Records': counts.values})

def time_matrix(frame, seconds, minutes=5):
    step = minutes * 60
    addresses = ranking(frame, 'source_ip').source_ip.head(12).tolist()
    f = frame[frame.source_ip.isin(addresses)].copy()
    f['Bucket'] = f.second // step * step
    m = pd.crosstab(f.source_ip, f.Bucket).reindex(index=addresses, columns=range(seconds[0] // step * step, seconds[1] // step * step + 1, step), fill_value=0)
    m.columns = [clock_label(s) for s in m.columns]
    return m

def flows(frame):
    ips = ranking(frame, 'source_ip').source_ip.head(6).tolist()
    users = ranking(frame, 'username').username.head(8).tolist()
    f = frame.copy()
    f['Address'] = f.source_ip.where(f.source_ip.isin(ips), 'Other source IPs')
    f['Username'] = f.username.where(f.username.isin(users), 'Other usernames')
    return f.groupby(['Address', 'Username']).size().reset_index(name='Records')

def case_report(frame, ips, users, seconds, account, notes=''):
    lines = ['# SSH investigation report', '', 'Dataset: Loghub OpenSSH 2k sample.',
        f'Time: December 10 {clock_label(seconds[0])}–{clock_label(seconds[1])}; year/timezone unavailable.',
        'IP filter: ' + (', '.join(ips) or 'All'), 'Username filter: ' + (', '.join(users) or 'All'),
        'Message account label: ' + account, f'Matching records: {len(frame)}',
        f'Source IPs: {frame.source_ip.nunique()}', f'Usernames: {frame.username.nunique()}', '']
    if not frame.empty:
        top = ranking(frame, 'source_ip').iloc[0]
        lines += [f'Leading address: {top.source_ip} ({int(top.Records)} records).', '', '## Example original message', str(frame.iloc[0].Content), '']
    return '\n'.join(lines + ['## Analyst observations', notes.strip() or 'No observations entered.', '', '## Limits',
        'Counts describe explicit failed-password records, not unique people, sessions, or proof of an attack. Repeat summaries are separate.',
        'https://github.com/logpai/loghub/tree/master/OpenSSH'])
