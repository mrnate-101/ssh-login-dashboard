from datetime import time,timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from analysis import load_data,filter_records,clock_label
st.set_page_config(page_title='SSH Login Explorer',page_icon='🔎',layout='wide')
st.caption('GROUP 8 · WORKING PROTOTYPE')
st.title('SSH Login Explorer')
st.write('Explore failed-password activity and inspect the original records.')
raw,failed,summaries=load_data()
parsed=failed[failed.parsed].copy()
lo,hi=int(raw.second.min()),int(raw.second.max())
def to_time(s): return time(s//3600,s%3600//60,s%60)
def reset():
    st.session_state.ips=[]
    st.session_state.users=[]
    st.session_state.window=(to_time(lo),to_time(hi))
    st.session_state.version=st.session_state.get('version',0)+1
with st.sidebar:
    st.header('Explore the records')
    st.button('Reset all filters',on_click=reset)
    ips=st.multiselect('Source IP address',sorted(parsed.source_ip.unique()),key='ips')
    users=st.multiselect('Username',sorted(parsed.username.unique()),key='users')
    window=st.slider('Time window',to_time(lo),to_time(hi),(to_time(lo),to_time(hi)),step=timedelta(seconds=1),format='HH:mm:ss',key='window')
    seconds=tuple(t.hour*3600+t.minute*60+t.second for t in window)
    st.caption('December 10 · no year or timezone supplied')
    st.write('Nathaniel Addai Gyarteng · Autenia Murray')
base=filter_records(parsed,ips,users,seconds)
st.subheader('01 / Which source addresses appear most often?')
st.caption('Top 15 for the sidebar filters. Select a bar to narrow the lower views; reset to clear selections.')
rank=base.groupby('source_ip').size().reset_index(name='Records').sort_values(['Records','source_ip'],ascending=[False,True]).head(15)
fig=px.bar(rank,x='Records',y='source_ip',orientation='h',text='Records',custom_data=['source_ip'],color_discrete_sequence=['#48d9c5'])
fig.update_layout(clickmode='event+select',yaxis={'categoryorder':'array','categoryarray':rank.source_ip.tolist()[::-1]},yaxis_title=None,height=380)
event=st.plotly_chart(fig,use_container_width=True,key=f"ip_chart_{st.session_state.get('version',0)}",on_select='rerun',selection_mode='points')
chosen=[p['customdata'][0] for p in event.selection.points if p.get('customdata')]
view=filter_records(base,chosen)
if chosen: st.info('Chart selection: '+', '.join(chosen))
for col,label,n in zip(st.columns(4),['Matching failed-password records','Source IP addresses','Usernames','All source log records'],[len(view),view.source_ip.nunique(),view.username.nunique(),len(raw)]):
    col.metric(label,f'{n:,}')
st.caption(f'{len(view)} of {len(parsed)} parsed failed-password records shown. Counts describe records, not unique people or sessions.')
if view.empty: st.warning('No matching records. Clear filters or widen the time window.')
else:
    left,right=st.columns(2)
    with left:
        st.subheader('02 / Which usernames?')
        names=view.groupby('username').size().reset_index(name='Records').sort_values(['Records','username'],ascending=[False,True]).head(15)
        fig=px.bar(names,x='Records',y='username',orientation='h',text='Records')
        fig.update_layout(yaxis={'categoryorder':'array','categoryarray':names.username.tolist()[::-1]},yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.subheader('03 / When did activity occur?')
        interval=st.selectbox('Time bin',[1,5,10],index=1,format_func=lambda n:f'{n} minute(s)')
        step=interval*60
        bins=(view.second//step*step).value_counts().reindex(range(seconds[0]//step*step,seconds[1]//step*step+1,step),fill_value=0).sort_index()
        timeline=pd.DataFrame({'Time':[clock_label(s) for s in bins.index],'Records':bins.values})
        st.plotly_chart(px.bar(timeline,x='Time',y='Records',labels={'Time':'December 10 · source clock time'}),use_container_width=True)
st.subheader('04 / Inspect the evidence')
cols=['LineId','Time','username','source_ip','account_type','Content']
st.dataframe(view[cols],hide_index=True,use_container_width=True)
if not view.empty:
    record=st.selectbox('Read an original message',view.LineId.tolist(),format_func=lambda n:f'Record {n}')
    st.code(view.loc[view.LineId.eq(record),'Content'].iloc[0],language=None,wrap_lines=True)
st.download_button('Download matching records · CSV',view[cols].to_csv(index=False).encode(),file_name='filtered_failed_password_records.csv',mime='text/csv')
with st.expander('Data quality, scope, and source'):
    st.write(f'{len(raw)} source records; {raw.EventId.nunique()} categories; {len(failed)} explicit failed-password records; {int(failed.parsed.sum())} parsed; {int((~failed.parsed).sum())} parsing exceptions.')
    st.write(f'{len(summaries)} repeat-summary messages are shown separately and not added to the counts. Other event categories are excluded from the charts.')
    st.write('Static educational sample. Repeated failures warrant investigation but do not prove an attack. Named account means no invalid-user marker, not independent verification of account validity. User evaluation remains future work.')
    st.markdown('[Loghub OpenSSH dataset](https://github.com/logpai/loghub/tree/master/OpenSSH)')
    st.dataframe(summaries[['LineId','Time','Content']],hide_index=True)
    if (~failed.parsed).any(): st.dataframe(failed.loc[~failed.parsed,['LineId','Content']])
