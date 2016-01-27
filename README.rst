pyluis
======

This is a Python interface to `Microsoft LUIS <https://luis.ai/>`
(Language Understanding Intelligent Service).

How to use
----------

First you need to create and publish a LUIS application. Then you can
use it to analyze text.::

  >>> import luis

  # Use the URL LUIS gives you when you publish your app.
  >>> l = luis.Luis(url='https://https://api.projectoxford.ai/luis/...')

  # Send text to be analyzed:
  >>> r = l.analyze('fly forward 10 feet')

  # See all identified intents:
  >>> print r.intents
  [<Intent intent=u'TRANSLATE' score=1.0>,
   <Intent intent=u'None' score=0.015184097>,
   <Intent intent=u'ROTATE' score=0.00713030435>,
   ...]

  # See all identified entities:
  >>> print r.entities
  [<Entity entity=u'forward' type=u'FORWARD' score=0.9585199 start_index=4 end_index=10>,
   <Entity entity=u'10 feet' type=u'builtin.dimension' score=0.9829198 start_index=12 end_index=18>]

  # What was the highest-scored intent?
  >>> best = r.best_intent()
  >>> print best
  <Intent intent=u'TRANSLATE' score=1.0>
  >>> print best.intent
  u'TRANSLATE'
  >>> print best.score
  1.0
