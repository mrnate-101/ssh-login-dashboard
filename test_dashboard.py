import unittest
from datetime import time
from analysis import load_data, filter_records
from analytics import time_counts, time_matrix, flows, case_report
from streamlit.testing.v1 import AppTest
from pathlib import Path

class DashboardTests(unittest.TestCase):
    def test_aggregation_preserves_counts(self):
        raw, failed, _ = load_data()
        self.assertEqual(len(raw), 2000)
        self.assertEqual(len(failed), 518)
        self.assertTrue(failed.parsed.all())
        self.assertEqual(flows(failed).Records.sum(), len(failed))
        for minutes in [1, 5, 10]:
            self.assertEqual(time_counts(failed, (int(raw.second.min()), int(raw.second.max())), minutes).Records.sum(), 518)
        matrix = time_matrix(failed, (int(raw.second.min()), int(raw.second.max())))
        self.assertEqual(matrix.to_numpy().sum(), len(failed[failed.source_ip.isin(matrix.index)]))
        f = filter_records(failed, ['183.62.140.253'], ['root'])
        self.assertEqual(len(f), 276)
        self.assertEqual(flows(f).Records.sum(), 276)
        self.assertIn('Matching records: 276', case_report(f, ['183.62.140.253'], ['root'], (24946, 39885), 'All records'))

    def test_pages_filters_and_patterns(self):
        app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '518')
        app.multiselect(key='ips').select('183.62.140.253').run()
        self.assertEqual(app.metric[0].value, '286')
        app.multiselect(key='users').select('root').run()
        self.assertEqual(app.metric[0].value, '276')
        for page in ['Investigation', 'Evidence', 'Pattern analysis']:
            app.radio(key='nav').set_value(page).run()
            self.assertFalse(app.exception, page)
            self.assertEqual(app.metric[0].value, '276')
        app.radio(key='nav').set_value('Investigation').run()
        app.text_area(key='case_notes').set_value('Evidence checked in the source message.').run()
        app.radio(key='nav').set_value('Evidence').run()
        app.radio(key='nav').set_value('Investigation').run()
        self.assertEqual(app.text_area(key='case_notes').value, 'Evidence checked in the source message.')
        app.radio(key='nav').set_value('Pattern analysis').run()
        app.button[0].click().run()
        for mode in ['Time heatmap', 'Address and username flow', 'Address profiles', 'Compare two addresses']:
            app.selectbox(key='pattern_view').set_value(mode).run()
            self.assertFalse(app.exception, mode)
        app.radio(key='nav').set_value('Evidence').run()
        app.text_input(key='evidence_query').set_value('a-message-that-does-not-exist').run()
        self.assertEqual(len(app.dataframe[0].value), 0)
        self.assertFalse(app.exception)
        app.slider(key='window').set_value((time(6,55,46), time(6,55,47))).run()
        self.assertEqual(app.metric[0].value, '0')
        app.radio(key='nav').set_value('Classroom').run()
        self.assertFalse(app.exception)
        app.text_input(key='quiz_ip').set_value('183.62.140.253')
        app.number_input(key='quiz_count').set_value(276)
        app.radio(key='quiz_claim').set_value('No')
        next(b for b in app.button if b.label == 'Check my answers').click().run()
        self.assertIn('3/3', app.success[0].value)
        app.radio(key='nav').set_value('Methodology').run()
        self.assertFalse(app.exception)

if __name__ == '__main__': unittest.main()
