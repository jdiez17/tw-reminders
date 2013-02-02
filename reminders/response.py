from reminders.syntax import ReminderScanner
from reminders.objects import Reminder, Job
from reminders.language import gs
from reminders.database import r

import hashlib

class ResponseGenerator(object):
    _scanner = None
    _reminder = None

    def _split(self, prefix=None, text=None, length=140, reply_to=None):
        def pop_until_length():
            result = None
            while len(separator.join(l_package)) > length:
                result = l_package.pop()

            return result

        def append_list(l):
            text = separator.join(l)
            if text.strip() == prefix.strip():
                return

            if reply_to:
                l_tweets.append((text, reply_to))
            else:
                l_tweets.append(text)
        
        separator = " "

        if prefix != None:
            l_text = prefix + separator + text
        else:
            l_text = text

        l_package = []
        l_tweets = []
        elements = l_text.split(" ")
         
        for element in elements:
            l_package.append(element)
            last = pop_until_length()

            if last:
                l_package.append("...")
                append_list(l_package)
                l_package = [prefix, "...", last]

        append_list(l_package)

        return l_tweets
 
    def response(self, user, text, reply_to=None):
        self._scanner = ReminderScanner(text)
        response = "" 
        valid = True
        tweet_hash = hashlib.sha1()
        tweet_hash.update(text)
        tweet_hash = tweet_hash.hexdigest()[:6]

        try:
            self._reminder = self._scanner.extract()
        except:
            valid = False
            response += gs("PARSE_ERROR") 

            return self._split("@" + user, response, reply_to=reply_to) 

        if self._reminder.error != None:
            valid = False
            response += gs("ERROR_OCCURRED") % self._reminder.error
        elif self._reminder.timedelta == None:
            valid = False
            response += gs("NO_TIMEDELTA")
        elif self._reminder.text == None:
            response += gs("NO_REMINDER_TEXT") % tweet_hash
        if self._reminder.text != None and valid:
            response += gs("REMINDER_SET") % tweet_hash

        # Save the job in the scheduler
        if valid:
            j = Job(extra={'user': user}, payload=self._reminder)
            j.store(r)

        return self._split("@" + user, response, reply_to=reply_to) 
