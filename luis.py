"""Interface to Microsoft's LUIS language understanding system.

John Wiseman
jjwiseman@gmail.com
"""

import collections
import logging
import pkg_resources

import requests

__version__ = pkg_resources.get_distribution('luis').version
logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class _LuisData():
    def __str__(self):
        classname = self.__class__.__name__
        slot_strs = ['%s=%r' % (s, v) for s, v in zip(self._fields, self)]
        return '<%s %s>' % (classname, ' '.join(slot_strs))

    def __repr__(self):
        return self.__str__()


class Intent(_LuisData,
             collections.namedtuple(
                 '_Intent',
                 ['intent', 'score'])):
    """Represents an intent, as identified by LUIS."""
    @classmethod
    def _from_json(klass, json):
        # Sometimes intents
        return Intent(intent=json['intent'], score=json['score'])

Intent.__new__.__defaults__ = (None, None)


class Entity(_LuisData,
             collections.namedtuple(
                 '_Entity',
                 ['entity', 'type', 'score', 'start_index', 'end_index', 'resolution'])):
    """Represents an entity, as identified by LUIS."""
    @classmethod
    def _from_json(klass, json):
        return Entity(entity=json['entity'],
                      type=json['type'],
                      score=json.get('score', None),
                      start_index=json.get('startIndex', None),
                      end_index=json.get('endIndex', None),
                      resolution=json.get('resolution', None))


class LuisResult(_LuisData,
                 collections.namedtuple(
                     '_LuisResult',
                     ['intents', 'entities', 'query'])):
    """Represents the result of LUIS analyzing a piece of text."""
    @classmethod
    def _from_json(klass, json):
        logger.info('Got response from LUIS: %s', json)
        intents = [Intent._from_json(i) for i in json.get('intents', [])]
        entities = [Entity._from_json(e) for e in json.get('entities', [])]
        entities = sorted(entities, key=lambda e: e.start_index or -1)
        return LuisResult(
            query=json['query'], intents=intents, entities=entities)

    def best_intent(self):
        """Returns the highest-scoring intent.

        Returns None if LUIS could not identify any intents. If any
        intents were identified but not scored, they will be
        considered to have the highest score.
        """
        if self.intents:
            return self.intents[0]
        else:
            return None


class Luis(object):
    """An interface to a LUIS app (webservice)."""
    def __init__(self, url=None):
        self._url = url
        if not url:
            raise Error('No url specified')
        # When you click "publish" on a LUIS app, the page gives you
        # back a URL that has an empty "&q=" param. Remove that if the
        # URL we're passed has it.
        self._url = self._url.replace('&q=', '')

    def analyze(self, text):
        """Sends text to LUIS for analysis.

        Returns a LuisResult.
        """
        logger.debug('Sending %r to LUIS app %s', text, self._url)
        r = requests.get(self._url, {'q': text})
        logger.debug('Request sent to LUIS URL: %s', r.url)
        logger.debug(
            'LUIS returned status %s with text: %s', r.status_code, r.text)
        r.raise_for_status()
        json_response = r.json()
        result = LuisResult._from_json(json_response)
        logger.debug('Returning %s', result)
        return result
