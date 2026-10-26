from pathlib import Path
import ipaddress
import re
import pandas as pd
DATA = Path(__file__).parent / 'data' / 'OpenSSH_2k.log_structured.csv'
PATTERN = re.compile(r'^Failed password for (?:(invalid user)\s+)?(\S+) from (\S+) port (\d+)(?: ssh\d*)?\s*$')
def load_data():
    raw = pd.read_csv(DATA)
    raw['second'] = pd.to_timedelta(raw['Time']).dt.total_seconds().astype(int)
    failed = raw.loc[raw.Content.str.startswith('Failed password for ', na=False)].copy()
    fields = failed.Content.str.extract(PATTERN)
    fields.columns = ['invalid_user','username','source_ip','port']
    failed = failed.join(fields)
    def valid_ip(value):
        try:
            ipaddress.ip_address(value)
            return True
        except (ValueError, TypeError):
            return False
    failed['parsed'] = failed.username.notna() & failed.source_ip.map(valid_ip)
    failed['account_type'] = failed.invalid_user.map(lambda x: 'Invalid user' if pd.notna(x) else 'Named account')
    summaries = raw[raw.Content.str.contains(r'message repeated|PAM \d+ more authentication failures',case=False,regex=True,na=False)].copy()
    return raw,failed,summaries
def filter_records(frame,ips=(),users=(),seconds=None):
    mask = pd.Series(True,index=frame.index)
    if ips: mask &= frame.source_ip.isin(ips)
    if users: mask &= frame.username.isin(users)
    if seconds is not None: mask &= frame.second.between(*seconds)
    return frame.loc[mask].copy()
def clock_label(second):
    second=int(second)
    return f'{second//3600:02}:{second%3600//60:02}:{second%60:02}'
