from unittest import TestCase
from unittest.mock import patch, Mock
from picker import Steam
import configparser


class TestSteam(TestCase):
    @classmethod
    def setUpClass(cls):
        settings = configparser.ConfigParser()
        settings.read('settings.ini')
        cls.steam = Steam(settings['steam'])
        cls.mock_call_patcher = patch('picker.steam.WebAPI.call')
        cls.mock_call = cls.mock_call_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.mock_call_patcher.stop()

    # TODO: split into a possitive and negative tests
    # TODO: extract method
    def test_resolve_vanity_url(self):
        vals = {'https://steamcommunity.com/profiles/6459068394824823': {'response': {'success': 42, 'message': 'No match'}},
                'https://steamcommunity.com/id/izdwuut/': {'response': {'steamid': '76561198011689582', 'success': 1}}}

        def side_effect(method_path, **kwargs):
            return vals[kwargs['vanityurl']]

        self.mock_call.side_effect = side_effect

        for url, response in vals.items():
            result = self.steam.resolve_vanity_url(url)

            self.assertDictEqual(result, response['response'])
            self.mock_call.assert_called_with('ISteamUser.ResolveVanityURL', vanityurl=url)



    # TODO: split into:
    #   * _when_profile_url (in- & valid)
    #   * _when_invalid_url (use steam.is_steam_url)
    @patch('picker.Steam.resolve_vanity_url')
    def test_get_id_when_valid_vanity_url(self, mock_resolve):
        vals = {'https://steamcommunity.com/id/izdwuut/': '76561198011689582'}

        side = {'izdwuut': {'steamid': '76561198011689582', 'success': 1},
                     '6$$$$55545435jj': {'success': 42, 'message': 'No match'}}

        self._test_get_id(vals, side, mock_resolve)

    def test_get_id_when_invalid_vanity_url(self):
        urls = {'https://steamcommunity.com/id/6$$$$55545435jj'}
        for url in urls:
            result = self.steam.get_id(url)

            self.assertIsNone(result)

    def _test_get_id(self, vals, side, mock_resolve: Mock):
        def side_effect(url):
            return side[url]

        mock_resolve.side_effect = side_effect
        for url, id in vals.items():
            result = self.steam.get_id(url)

            self.assertEqual(result, id)
            mock_resolve.assert_called_with(url)

