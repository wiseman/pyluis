import requests
import sys

import luis
import pytest


if sys.version < '3':
    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x


class MockResponse(object):
    def __init__(self, json, url):
        self._json = json
        self.url = url
        self.status_code = 200
        self.text = self._json

    def json(self):
        return self._json

    def raise_for_status(self):
        pass


resp_json = None
req_url = None
req_params = None


def test_no_url_errors():
    with pytest.raises(luis.Error):
        l = luis.Luis()


def test_analyze():
    old_get = requests.get
    try:
        def mock_get(url, params):
            global req_url, req_params
            req_url = url
            req_params = params
            return MockResponse(resp_json, url)
        requests.get = mock_get

        resp_json = {u('query'): None, u('intents'): [], u('entities'): []}
        l = luis.Luis(url='http://null/?x=1&q=')
        r = l.analyze('')

        assert req_url == 'http://null/?x=1'
        assert req_params == {'q': ''}
        assert len(r.intents) == 0
        assert len(r.entities) == 0
        assert r.best_intent() is None

        resp_json = {
            u('query'): u('set an alarm for tuesday'),
            u('intents'): [{
                u('intent'): u('builtin.intent.alarm.set_alarm'),
                u('score'): 1.0
            }],
            u('entities'): [{
                u('resolution'): {
                    u('date'): u('XXXX-WXX-2'),
                    u('resolution_type'): u('builtin.datetime.date')
                },
                u('type'): u('builtin.alarm.start_date'),
                u('entity'): u('tuesday')
            }
            ]
        }
        l = luis.Luis(url='http://null/?x=1')
        r = l.analyze('set an alarm for tuesday')

        assert req_url == 'http://null/?x=1'
        assert req_params == {'q': 'set an alarm for tuesday'}
        assert (r.intents[0].intent ==
                'builtin.intent.alarm.set_alarm')
        assert r.intents[0].score == 1.0
        assert (r.best_intent().intent ==
                'builtin.intent.alarm.set_alarm')
    finally:
        requests.get = old_get
