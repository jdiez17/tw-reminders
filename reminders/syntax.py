from plex import *
from StringIO import StringIO
from datetime import timedelta

from reminders.objects import Reminder
from reminders.exceptions import UnknownMethodException

SingleDigit = Range("09")
Number = Rep1(SingleDigit)

class ReminderScanner(Scanner):
    _reminder = Reminder()
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    reminder_text = ""

    def set_method(self, text):
        try:
            self._reminder.method = text
        except UnknownMethodException:
            self._reminder.error = "Sorry, I don't know how to remind you by %s." % text

    def _digits(self, text):
        t = type(text)
        return int(t().join(filter(t.isdigit, text)))
        
    def set_weeks(self, text):
        self.weeks = self._digits(text)
    
    def set_days(self, text):
        self.days = self._digits(text)
    
    def set_hours(self, text):
        self.hours = self._digits(text) 
    
    def set_minutes(self, text):
        self.minutes = self._digits(text) 
        
    def set_seconds(self, text):
        self.seconds = self._digits(text)
    
    def reminder_append(self, c):
        self.reminder_text += c
    
    def commit_timedelta(self, text):
        try:
            self._reminder.timedelta = timedelta(
                weeks=self.weeks,
                days=self.days,
                hours=self.hours,
                minutes=self.minutes,
                seconds=self.seconds)
        except Exception, e:
            self._reminder.error = str(e)
            
        self.begin('reminder')
    
    def clean_reminder(self, text):
        self._reminder.text = self.reminder_text.strip()
        
    lex = Lexicon([
        (Str("by"), Begin('method')),
        State('method', [
            (Str("reply"), set_method),
            (Str("dm"), set_method),
            (Str("in"), Begin('timedelta')),
            (AnyChar, IGNORE)
        ]),
        State('timedelta', [
            (Number + Str("wk"), set_weeks),
            (Number + Str("d"), set_days),
            (Number + Str("h"), set_hours),
            (Number + Str("m"), set_minutes),
            (Number + Str("s"), set_seconds),
            (Number + Opt(Str(" ")) + Str("weeks"), set_weeks),
            (Number + Opt(Str(" ")) + Str("days"), set_days),
            (Number + Opt(Str(" ")) + Str("hours"), set_hours),
            (Number + Opt(Str(" ")) + Str("minutes"), set_minutes),
            (Number + Opt(Str(" ")) + Str("seconds"), set_seconds),
            (Eol, commit_timedelta),
            (Str(":"), commit_timedelta),
            (AnyChar, IGNORE)
        ]),
        State('reminder', [
            (AnyChar, reminder_append),
            (Eol, clean_reminder)
        ])
    ])
    
    def __init__(self, text):
        Scanner.__init__(self, self.lex, StringIO(text))
        
    def extract(self):
        token = self.read()
        while not token[0] == None:
            token = self.read()
        
        return self._reminder
