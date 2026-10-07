import unittest
from analysis import summarize, validate

def match(**kw):
    return dict(kills=20,deaths=10,assists=5,rounds=20,damage=3000,score=6000,headshots=10,bodyshots=30,legshots=0,**kw)

class AnalysisTests(unittest.TestCase):
    def test_weighted_stats_and_dominance(self):
        s=summarize({'matches':[match() for _ in range(10)]})
        self.assertEqual((s['kd'],s['acs'],s['adr'],s['hs']),(2,300,150,25))
        self.assertIn('10/10',s['signals'][0])
    def test_incomplete_is_not_profile(self):
        s=summarize({'matches':[match()]})
        self.assertEqual(len(s['signals']),1)
        self.assertIn('insuffisantes',s['signals'][0])
    def test_invalid_nonfinite_and_zero_rounds(self):
        for key,value in [('score',float('nan')),('rounds',0),('kills',-1)]:
            m=match();m[key]=value
            with self.assertRaises(ValueError):validate({'matches':[m]})
    def test_empty_and_zero_deaths(self):
        self.assertEqual(summarize({'matches':[]})['count'],0)
        m=match();m['deaths']=0
        self.assertEqual(summarize({'matches':[m]})['kd'],20)
