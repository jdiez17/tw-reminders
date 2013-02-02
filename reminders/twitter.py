import tweepy
import redis
import threading

from reminders.response import ResponseGenerator
from reminders.config import config, logger
from reminders.scheduler import run as scheduler_run

def data_receiver(frontend):
    r = redis.Redis()
    ps = r.pubsub()
    ps.subscribe('reminders')

    logger.debug("Data receiver thread started")
    while True:
        for m in ps.listen():
            frontend.tweet(m['data'])

class TwitterFrontEnd(tweepy.StreamListener):
    def __init__(self):
        t = threading.Thread(target=data_receiver, args=(self,))
        t.setDaemon(True)
        t.start()

        sched = threading.Thread(target=scheduler_run)
        sched.setDaemon(True)
        sched.start()

        tweepy.StreamListener.__init__(self)
        self._generator = ResponseGenerator()

        self.username = config.get('twitter', 'username')
        ck = config.get('twitter', 'client_key')
        cs = config.get('twitter', 'client_secret')
        ak = config.get('twitter', 'access_key')
        asec = config.get('twitter', 'access_secret')

        auth = tweepy.OAuthHandler(ck, cs)
        auth.set_access_token(ak, asec)

        self._api = tweepy.API(auth)
        streaming = tweepy.streaming.Stream(auth, self, timeout=60)
        streaming.userstream()
        logger.info('Reminder bot started')

    def tweet(self, message, id=None):
        if isinstance(message, basestring):
            text = message
        else: 
            text = message[0]
            id = message[1]
       
        text = text.decode('utf-8')
        try:
            self._api.update_status(text[:140], id)
            pass
        except Exception, e:
            logger.error("Sending tweet: " + str(e))
            
        logger.info("Sending tweet: " + text.encode('utf-8'))

    def on_status(self, status):
        if status.in_reply_to_screen_name == self.username:
            status.text = status.text[len(self.username)+1:].strip()
            logger.debug("Got tweet '%s' from '%s'" % (status.text, status.author.screen_name))

            response = self._generator.response(status.author.screen_name, status.text, status.id)
            for r in response:
                self.tweet(r)
