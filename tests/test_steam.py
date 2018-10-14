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

    def test_resolve_vanity_url__when_valid_url__expect_steam_id_response(self):
        vals = {'https://steamcommunity.com/id/izdwuut/': {'response': {'steamid': '76561198011689582', 'success': 1}}}

        self._test_resolve_vanity_url(vals)

    def test_resolve_vanity_url__when_invalid_url__expect_no_match_response(self):
        vals = {'https://steamcommunity.com/profiles/6459068394824823': {'response': {'success': 42, 'message': 'No match'}}}

        self._test_resolve_vanity_url(vals)

    def _test_resolve_vanity_url(self, vals):
        def side_effect(method_path, **kwargs):
            return vals[kwargs['vanityurl']]

        self.mock_call.side_effect = side_effect

        for url, response in vals.items():
            result = self.steam.resolve_vanity_url(url)

            self.assertDictEqual(result, response['response'])
            self.mock_call.assert_called_with('ISteamUser.ResolveVanityURL', vanityurl=url)

    # TODO:
    #   * _when_profile_url (in- & valid)
    #   * _when_invalid_url (use steam.is_steam_url)
    @patch('picker.Steam.resolve_vanity_url')
    def test_get_id__when_valid_vanity_url__expect_steam_id(self, mock_resolve):
        vals = {'https://steamcommunity.com/id/izdwuut/': '76561198011689582'}

        side = {'izdwuut': {'steamid': '76561198011689582', 'success': 1}}

        self._test_get_id(vals, side, mock_resolve)

    def test_get_id__when_invalid_vanity_url__expect_none(self):
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

