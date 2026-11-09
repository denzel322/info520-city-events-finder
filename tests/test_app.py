import unittest
from unittest.mock import patch
from app import event, merge, ticketmaster, predicthq, date_bounds

class MergeTests(unittest.TestCase):
    def test_duplicate_retains_both_sources_and_links(self):
        a=event('Ticketmaster','1','A Great Show!','2030-01-03','19:00','The Hall','https://example.org/a')
        b=event('PredictHQ','2','a great show','2030-01-03','19:00','THE HALL','https://example.org/b')
        result=merge([a,b])
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['sources'],['PredictHQ','Ticketmaster'])
        self.assertEqual(len(result[0]['links']),2)
    def test_same_title_different_date_or_venue_kept(self):
        rows=[event('A',str(i),'Show',date,'19:00',venue) for i,(date,venue) in enumerate([
            ('2030-01-01','Hall'),('2030-01-02','Hall'),('2030-01-01','Park')])]
        self.assertEqual(len(merge(rows)),3)
    def test_missing_venue_not_merged_across_sources(self):
        self.assertEqual(len(merge([event('A','1','Show','2030-01-01'),event('B','2','Show','2030-01-01')])),2)
    def test_sort_date_then_time(self):
        rows=[event('A','1','Late','2030-01-02','21:00','Hall'),event('A','2','Early','2030-01-01','20:00','Hall')]
        self.assertEqual(merge(rows)[0]['title'],'Early')
    def test_local_date_bounds_include_daylight_saving_transition(self):
        self.assertEqual(date_bounds({'timezone':'America/New_York'},'2026-11-01','2026-11-01'),
                         ('2026-11-01T04:00:00Z','2026-11-02T04:59:59Z'))

    @patch.dict('os.environ', {'TICKETMASTER_API_KEY':'test-only'})
    @patch('app.fetch')
    def test_ticketmaster_normalizes_and_skips_cancelled(self, fetch):
        fetch.return_value={'_embedded':{'events':[{'id':'1','name':'Show','dates':{'start':{'localDate':'2030-01-01','localTime':'19:00:00'}},'_embedded':{'venues':[{'name':'Hall'}]}},{'id':'2','dates':{'status':{'code':'cancelled'}}}]}}
        result=ticketmaster({'latitude':1,'longitude':2},'2030-01-01','2030-01-07')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['venue'],'Hall')
    @patch.dict('os.environ', {'PREDICTHQ_API_TOKEN':'test-only'})
    @patch('app.fetch')
    def test_predicthq_converts_to_local_date(self, fetch):
        fetch.return_value={'results':[{'id':'1','title':'Show','start':'2030-01-02T01:00:00Z','timezone':'America/New_York','entities':[{'type':'venue','name':'Hall'}]}]}
        result=predicthq({'latitude':1,'longitude':2},'2030-01-01','2030-01-07')
        self.assertEqual(result[0]['date'],'2030-01-01')
        self.assertEqual(fetch.call_args.args[1]['limit'],50)

if __name__=='__main__':unittest.main()
