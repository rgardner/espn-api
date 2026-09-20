from unittest import mock, TestCase

from espn_api.football import League


class PlayerNewsTest(TestCase):
    def make_league(self):
        with mock.patch.object(League, "_fetch_league"):
            league = League(123, 2026)
        league.year = 2026
        league.finalScoringPeriod = 18
        league.player_map = {}
        league.get_team_data = mock.Mock()
        league._get_all_pro_schedule = mock.Mock(return_value={})
        league.espn_request = mock.MagicMock()
        return league

    @mock.patch("espn_api.football.league.Player")
    def test_player_info_does_not_fetch_news_by_default(self, player_class):
        league = self.make_league()
        league.espn_request.get_player_card.return_value = {"players": [{"id": 1001}]}

        league.player_info(playerId=1001)

        league.espn_request.get_player_news.assert_not_called()
        self.assertIsNone(player_class.call_args.kwargs["news"])

    @mock.patch("espn_api.football.league.Player")
    def test_player_info_fetches_news_for_each_player(self, player_class):
        league = self.make_league()
        cards = [{"id": 1001}, {"id": 1002}]
        league.espn_request.get_player_card.return_value = {"players": cards}
        news = {
            1001: {"news": {"feed": [{"headline": "One"}]}},
            1002: {"news": {"feed": [{"headline": "Two"}]}},
        }
        league.espn_request.get_player_news.side_effect = lambda player_id: news[
            player_id
        ]

        players = league.player_info(playerId=[1001, 1002], include_news=True)

        self.assertEqual(
            players, [player_class.return_value, player_class.return_value]
        )
        self.assertEqual(
            league.espn_request.get_player_news.call_args_list,
            [mock.call(1001), mock.call(1002)],
        )
        self.assertEqual(player_class.call_args_list[0].kwargs["news"], news[1001])
        self.assertEqual(player_class.call_args_list[1].kwargs["news"], news[1002])
