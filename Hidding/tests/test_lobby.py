import json
from pathlib import Path
import unittest
from app import Hidding, build_demo_lobby, lobby_summary, observation_label

class LobbyTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads(Path('demo.json').read_text(encoding='utf-8'))
        self.lobby=build_demo_lobby(self.base)
    def test_five_profiles_and_input_unchanged(self):
        original=json.dumps(self.base,sort_keys=True)
        self.assertEqual(len(self.lobby),5)
        self.lobby[1]['matches'][0]['kills']=999
        self.assertEqual(json.dumps(self.base,sort_keys=True),original)
    def test_private_profiles_never_return_stats(self):
        self.assertIsNone(lobby_summary(self.lobby[0]))
        self.assertIsNone(lobby_summary(self.lobby[4]))
        self.lobby[0]['consent']=True
        self.assertEqual(lobby_summary(self.lobby[0])['count'],10)
        self.lobby[0]['consent']=False
        self.assertIsNone(lobby_summary(self.lobby[0]))
    def test_distinct_explained_scenarios(self):
        self.assertEqual(observation_label(lobby_summary(self.lobby[1])),'Domination régulière')
        self.assertEqual(observation_label(lobby_summary(self.lobby[2])),'Historique incomplet · 6/10')
        self.assertEqual(observation_label(lobby_summary(self.lobby[3])),'Hausse de performances')
    def test_cannot_consent_without_simulated_connection(self):
        a=Hidding.__new__(Hidding)
        a.lobby=self.lobby;a.simulated_connected=False
        a.apply_consent(True)
        self.assertFalse(a.lobby[0]['consent'])
    def test_revoke_immediately_hides_own_profile(self):
        a=Hidding.__new__(Hidding)
        a.lobby=self.lobby;a.simulated_connected=True;a.lobby[0]['consent']=True
        a.data={};a.navigate=lambda view:None
        a.revoke_consent()
        self.assertFalse(a.simulated_connected)
        self.assertIsNone(lobby_summary(a.lobby[0]))
