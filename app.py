from datetime import time, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analysis import load_data, filter_records, clock_label
from analytics import ranking, time_counts, time_matrix, flows, case_report

st.set_page_config(page_title='SSH Login Explorer', page_icon='🔎', layout='wide')
st.markdown('''<style>
[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#fff;color:#132b40}
[data-testid="stSidebar"]{background:#f3f7fb;border-right:1px solid #d9e3ec}
.block-container{padding-top:2.4rem;max-width:1550px}
h1,h2,h3{color:#132b40;letter-spacing:-.5px}
[data-testid="stMetric"]{padding:16px;background:#f3f8fb;border:1px solid #dce9ee;border-radius:12px}
[data-testid="stMetricValue"]{color:#087f8c}
</style>''', unsafe_allow_html=True)
@st.cache_data
def dataset(): return load_data()
raw, failed, summaries = dataset()
parsed = failed[failed.parsed].copy()
lo, hi = int(raw.second.min()), int(raw.second.max())
PAGES = ['Overview', 'Investigation', 'Pattern analysis', 'Evidence', 'Classroom', 'Methodology']
def to_time(s): return time(s // 3600, s % 3600 // 60, s % 60)
for key, value in {'ips': [], 'users': [], 'window': (to_time(lo), to_time(hi)), 'account': 'All records'}.items():
    if key not in st.session_state: st.session_state[key] = value
def reset():
    st.session_state.ips = []
    st.session_state.users = []
    st.session_state.window = (to_time(lo), to_time(hi))
    st.session_state.account = 'All records'
def open_case():
    reset()
    st.session_state.ips = [ranking(parsed, 'source_ip').iloc[0].source_ip]
    st.session_state.nav = 'Investigation'
def save_notes():
    st.session_state.notes_draft = st.session_state.case_notes
with st.sidebar:
    st.markdown('## SSH Login Explorer')
    st.caption('An investigation workspace for learning')
    page = st.radio('Workspace', PAGES, key='nav')
    st.divider()
    st.markdown('### Shared filters')
    st.caption('Apply across the four analysis pages. Classroom exercises use the full sample.')
    st.button('Reset all filters', on_click=reset, use_container_width=True)
    ips = st.multiselect('Source IP address', sorted(parsed.source_ip.unique()), key='ips')
    users = st.multiselect('Username', sorted(parsed.username.unique()), key='users')
    window = st.slider('Time window', to_time(lo), to_time(hi), step=timedelta(seconds=1), format='HH:mm:ss', key='window')
    account = st.selectbox('Message account label', ['All records', 'Invalid user', 'Named account'], key='account')
    st.caption('Named account means no invalid-user marker, not independent verification. December 10; no year or timezone supplied.')
    st.divider()
    st.caption('Nathaniel Addai Gyarteng and Autenia Murray\n\nIT 7176 · Group 8')
    st.markdown('[Project code](https://github.com/mrnate-101/ssh-login-dashboard)')
seconds = tuple(t.hour * 3600 + t.minute * 60 + t.second for t in window)
view = filter_records(parsed, ips, users, seconds)
if account != 'All records': view = view[view.account_type.eq(account)].copy()
def plot(fig, height=580):
    fig.update_layout(template='plotly_white', height=height, paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Arial', size=17, color='#20384e'), margin=dict(l=25, r=45, t=40, b=65),
        hoverlabel=dict(bgcolor='white', font_size=16), colorway=['#087f8c', '#3266cb', '#d17740', '#7757a6'])
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False, 'toImageButtonOptions': {'format': 'png', 'scale': 2}})
def metrics(frame):
    for col, label, value in zip(st.columns(4), ['Matching failed-password records', 'Source IP addresses', 'Usernames', 'All source log records'],
        [len(frame), frame.source_ip.nunique(), frame.username.nunique(), len(raw)]): col.metric(label, f'{value:,}')
    st.caption(f'{len(frame):,} of {len(parsed):,} parsed explicit failed-password records. Source total remains fixed. Counts describe records, not unique people or sessions.')
def bars(frame, column, count=15):
    data = ranking(frame, column).head(count)
    fig = px.bar(data, x='Records', y=column, orientation='h', text='Records', color_discrete_sequence=['#087f8c'])
    fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': data[column].tolist()[::-1]}, yaxis_title=None, xaxis_title='Explicit failed-password records')
    fig.update_traces(textposition='outside', cliponaxis=False)
    return fig
st.caption('LOGHUB OPENSSH SAMPLE / EDUCATIONAL INVESTIGATION')
st.title('SSH Login Explorer' if page == 'Overview' else page)
if page in PAGES[:4]: metrics(view)
empty = view.empty
if empty and page in PAGES[:4]: st.warning('No matching records. Clear a filter or widen the time window.')

if page == 'Overview':
    st.write('See the overall activity, focus on a question, and follow each pattern back to its original records.')
    if not empty:
        top = ranking(view, 'source_ip').iloc[0]
        st.subheader(f'{top.source_ip} appears in {int(top.Records):,} matching records')
        st.write(f'This address represents {top.Records / len(view):.1%} of the selection. A repeated address is a starting point for investigation, not an attack verdict.')
        plot(bars(view, 'source_ip', 12), 620)
        st.caption('Top 12 addresses. Hover for exact counts. Use the shared filters to focus the analysis. Fullscreen and image export are available in each chart toolbar.')
        st.subheader('Activity across the selected time window')
        bins = time_counts(view, seconds, 5)
        plot(px.bar(bins, x='Time', y='Records', labels={'Time': 'December 10 · five-minute bin start'}, color_discrete_sequence=['#3266cb']), 430)
        st.caption('Zero-count bins remain visible. Boundary bins can contain only part of the selected window.')
    st.button('Open the leading-address case', on_click=open_case, help='Resets filters, selects the leading address in the full sample, and opens Investigation.')

elif page == 'Investigation':
    st.write('Ask a focused question, inspect the messages, and record what the evidence supports.')
    if not empty:
        st.subheader('Which usernames appear?')
        plot(bars(view, 'username'), 610)
        interval = st.selectbox('Time bin', [1, 5, 10], index=1, format_func=lambda n: f'{n} minute(s)', key='investigation_bin')
        bins = time_counts(view, seconds, interval)
        st.subheader('When do the matching records occur?')
        plot(px.bar(bins, x='Time', y='Records', labels={'Time': f'December 10 · {interval}-minute bin start'}, color_discrete_sequence=['#3266cb']), 520)
        peak = bins.loc[bins.Records.idxmax()]
        st.info(f'Largest displayed bin: {peak.Time}, with {int(peak.Records)} records. This is a descriptive count, not an alert threshold.')
        record = st.selectbox('Read an original message', view.LineId.tolist(), format_func=lambda n: f'Record {n}', key='case_record')
        st.code(view.loc[view.LineId.eq(record), 'Content'].iloc[0], language=None, wrap_lines=True)
    notes = st.text_area('Your investigation notes', value=st.session_state.get('notes_draft', ''), key='case_notes', on_change=save_notes, placeholder='What did you observe? Which records support it? What remains uncertain?')
    st.download_button('Download investigation report', case_report(view, ips, users, seconds, account, notes), 'ssh-investigation.md', 'text/markdown')
    st.caption('Notes stay in this browser session until downloaded. The report includes the filter settings and observations; it does not assign an attack label.')

elif page == 'Pattern analysis' and not empty:
    st.write('Explore timing, relationships, and username diversity. All views use the shared filters.')
    mode = st.selectbox('Pattern view', ['Time heatmap', 'Address and username flow', 'Address profiles', 'Compare two addresses'], key='pattern_view')
    if mode == 'Time heatmap':
        st.subheader('When does each address appear?')
        interval = st.selectbox('Heatmap time bin', [1, 5, 10], index=1, format_func=lambda n: f'{n} minute(s)')
        matrix = time_matrix(view, seconds, interval)
        fig = px.imshow(matrix, aspect='auto', color_continuous_scale=['#f2f8fa', '#7ec8cc', '#087f8c'], labels={'x': 'December 10 · bin start', 'y': 'Source IP', 'color': 'Records'})
        fig.update_traces(hovertemplate='IP: %{y}<br>Bin start: %{x}<br>Records: %{z}<extra></extra>')
        plot(fig, 650)
        st.caption('Top 12 addresses by matching count. Darker cells mean more records; the palest cells have zero. This is a time matrix, not a geographic map.')
    elif mode == 'Address and username flow':
        st.subheader('Which addresses and usernames appear together?')
        links = flows(view)
        left, right = links.Address.unique().tolist(), links.Username.unique().tolist()
        fig = go.Figure(go.Sankey(arrangement='snap', node={'label': ['IP: ' + v for v in left] + ['User: ' + v for v in right],
            'pad': 20, 'thickness': 20, 'color': ['#087f8c'] * len(left) + ['#3266cb'] * len(right)},
            link={'source': [left.index(v) for v in links.Address], 'target': [len(left) + right.index(v) for v in links.Username],
                  'value': links.Records.tolist(), 'color': 'rgba(8,127,140,0.18)'}))
        plot(fig, 720)
        st.caption(f'Flow width represents record counts, not network traffic or a causal path. Leading 6 IPs and 8 usernames retain their names; remaining values are grouped. All {len(view):,} matching records remain represented.')
    elif mode == 'Address profiles':
        st.subheader('Frequency and username diversity')
        profiles = view.groupby('source_ip').agg(Records=('LineId', 'size'), Usernames=('username', 'nunique'), First=('second', 'min'), Last=('second', 'max')).reset_index()
        fig = px.scatter(profiles, x='Records', y='Usernames', size='Records', hover_name='source_ip', size_max=65, color_discrete_sequence=['#087f8c'], labels={'Records': 'Failed-password records', 'Usernames': 'Distinct usernames'})
        fig.update_yaxes(dtick=1)
        plot(fig, 650)
        st.caption('Each bubble is one address. Larger bubbles mean more records. Username diversity is a descriptive measure, not a risk score.')
        st.dataframe(profiles.assign(First=profiles.First.map(clock_label), Last=profiles.Last.map(clock_label)), hide_index=True, use_container_width=True)
    else:
        options = ranking(view, 'source_ip').source_ip.tolist()
        if len(options) < 2: st.info('Include at least two addresses in the shared filters to compare them.')
        else:
            first = st.selectbox('First address', options, key='compare_first')
            second = st.selectbox('Second address', [v for v in options if v != first], key='compare_second')
            frames = []
            for address in [first, second]:
                bins = time_counts(view[view.source_ip.eq(address)], seconds, 5)
                bins['Source IP'] = address
                frames.append(bins)
            plot(px.line(pd.concat(frames), x='Time', y='Records', color='Source IP', markers=True, labels={'Time': 'December 10 · five-minute bin start'}), 600)
            st.caption('Identical five-minute intervals retain zero bins. Values are raw counts, not normalized rates.')

elif page == 'Evidence':
    st.write('Search the original evidence and export the exact selected records.')
    query = st.text_input('Search original messages', placeholder='For example: root or an address', key='evidence_query')
    evidence = view[view.Content.str.contains(query, case=False, regex=False, na=False)] if query else view
    st.caption(f'{len(evidence):,} records after message search. The table and CSV use this exact subset.')
    columns = ['LineId', 'Time', 'username', 'source_ip', 'account_type', 'port', 'Content']
    st.dataframe(evidence[columns], hide_index=True, use_container_width=True, height=520)
    if not evidence.empty:
        record = st.selectbox('Inspect record', evidence.LineId.tolist(), format_func=lambda n: f'Record {n}', key='evidence_record')
        st.code(evidence.loc[evidence.LineId.eq(record), 'Content'].iloc[0], language=None, wrap_lines=True)
    st.download_button('Download matching records · CSV', evidence[columns].to_csv(index=False).encode(), 'filtered_failed_password_records.csv', 'text/csv')
    metadata = {'dataset': 'Loghub OpenSSH 2k', 'source_ips': ips, 'usernames': users, 'time_seconds': seconds, 'account_label': account,
        'literal_message_search': query, 'exported_records': len(evidence), 'count_unit': 'explicit failed-password log records', 'year': None, 'timezone': None}
    st.download_button('Download filter details · JSON', json.dumps(metadata, indent=2), 'filter-details.json', 'application/json')

elif page == 'Classroom':
    st.write('A guided lesson for students beginning authentication-log analysis.')
    st.info('Exercises use the complete sample, independent of sidebar filters. This is practice, not a completed usability study or certification.')
    st.subheader('A 30-minute classroom activity')
    st.markdown('''1. **Understand the record (5 minutes):** identify time, username, source address, and outcome.
2. **Investigate (10 minutes):** find the leading address, combine filters, and read supporting messages.
3. **Interpret (10 minutes):** distinguish a recorded failure from an attack claim. Explain what more evidence is needed.
4. **Submit evidence (5 minutes):** export matching CSV records and an investigation report.''')
    with st.expander('Basic terms'):
        st.write('A log records an event. Authentication checks identity. SSH provides secure remote access. A source IP is a network address, not proof of a person’s identity. A failed password is an event; a false-positive alert incorrectly flags benign activity.')
    st.subheader('Practice: follow the evidence')
    top_ip = ranking(parsed, 'source_ip').iloc[0].source_ip
    expected_both = len(filter_records(parsed, [top_ip], ['root']))
    with st.form('student_exercise'):
        answer_ip = st.text_input('1. Which source IP has the most explicit failed-password records?', key='quiz_ip')
        answer_count = st.number_input('2. How many records match that IP and username root?', min_value=0, step=1, key='quiz_count')
        answer_claim = st.radio('3. Do these counts alone prove an attack?', ['Choose an answer', 'Yes', 'No'], key='quiz_claim')
        submitted = st.form_submit_button('Check my answers')
    if submitted:
        score = int(answer_ip.strip() == top_ip) + int(answer_count == expected_both) + int(answer_claim == 'No')
        st.success(f'Practice result: {score}/3 correct')
        st.write(f'The leading IP is {top_ip}. It has {expected_both} records naming root. Counts alone do not prove an attack; inspect messages and seek additional context.')
    with st.expander('Instructor guide and suggested assessment'):
        st.write('Use the same public sample for all students. Ask for selected filter details, matching CSV, and an explanation citing at least one original LineId. Suggested rubric: correct filtering (2), traceable evidence (2), interpretation with limitations (2).')
        st.write('For future evaluation, use comparable tasks with a searchable table and the dashboard. Alternate interface order and measure accuracy, task time, and feedback. No participant results have been collected for this project.')
        st.write('Suggested school rollout: a teacher-led pilot, accessibility feedback, then revision before wider use. The app has no roster, gradebook, or student-account system. Download work before leaving the browser session.')
    lesson = '# SSH investigation worksheet\n\nUse the full Loghub OpenSSH sample.\n\n1. Identify the leading source IP.\n2. Find its count with username root.\n3. Cite an original message by LineId.\n4. Describe timing.\n5. Explain why these observations alone do not establish an attack.\n\nSubmit matching CSV, filter metadata, and investigation report.\n'
    st.download_button('Download student worksheet', lesson, 'ssh-classroom-worksheet.md', 'text/markdown')

elif page == 'Methodology':
    st.write('Source, counting rules, preparation process, and interpretation limits.')
    st.subheader('Data provenance and parsing checks')
    st.dataframe(pd.DataFrame({'Check': ['Source records', 'Event categories', 'Explicit failed-password messages', 'Successfully parsed', 'Parsing exceptions', 'Separate repeat summaries'],
        'Count': [len(raw), raw.EventId.nunique(), len(failed), int(failed.parsed.sum()), int((~failed.parsed).sum()), len(summaries)]}), hide_index=True, use_container_width=True)
    st.markdown('[Original Loghub OpenSSH source](https://github.com/logpai/loghub/tree/master/OpenSSH)')
    st.write('We preserve the original structured CSV. Python selects messages beginning with “Failed password for”, extracts username, address, port and the optional invalid-user marker, and checks username extraction and IP syntax. Summary messages remain separate and are not expanded into extra attempts.')
    st.subheader('What the data supports')
    st.write('Static educational sample: December 10, 06:55:46–11:04:45. No year or timezone is supplied. Time bins use seconds since midnight for this single-day sample. Named account means the message lacks an invalid-user marker, not independent account verification.')
    st.write('Counts do not identify people or sessions, establish attack intent, or show successful access. No risk score or geographic attribution is attempted. User benefit has not yet been measured. This project uses Loghub data and does not include a VM attack experiment.')
    st.subheader('Implementation and contribution')
    st.write('Python and pandas prepare records, Plotly draws interactive charts, and Streamlit supplies the interface. The contribution is a focused educational workflow, connected evidence, transparent counting rules, and classroom practice. These design choices do not establish that the approach is the first of its kind. Codex assisted with implementation.')
    with st.expander('Separate repeat-summary messages'):
        st.dataframe(summaries[['LineId', 'Time', 'Content']], hide_index=True, use_container_width=True)
    if (~failed.parsed).any():
        st.error('Some explicit messages did not parse and are excluded from charts.')
        st.dataframe(failed.loc[~failed.parsed, ['LineId', 'Content']])
st.divider()
st.caption('SSH Login Explorer · Educational sample · Repeated failures warrant investigation, not an automatic attack label.')
