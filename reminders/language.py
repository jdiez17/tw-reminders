LANGUAGE = {
    'ERROR_OCCURRED': "Sorry, I have encountered an uncaught exception: '%s'",
    'NO_TIMEDELTA': "You haven't specified a timedelta.",
    'NO_REMINDER_TEXT': "You haven't specified a reminder text, but I'll remind you anyway. #%s",
    'REMINDER_SET': "Reminder set, thank you. #%s",
    'PARSE_ERROR': "Error during the parsing stage. I couldn't understand what you said, sorry.",
    'REMINDER_PLACEHOLDER': "(no reminder specified)"
}

def gs(s):
    return LANGUAGE.get(s, "Language string not found.")
