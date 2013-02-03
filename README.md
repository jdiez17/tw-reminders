tw-reminders is a simple twitter bot that lets users set reminders.

Usage
=====
To create a reminder request, tweet:

    @SendMeAReminder by <method> in <time>: <message>

Where `<method>` can be:
    * dm 
    * reply

You can use the following keywords to set the `<time>` paramter:
    * wk / weeks
    * d / days
    * h / hours
    * m / minutes 
    * s / seconds

`<text>` can be any string.

Full example:

    @SendMeAReminder by reply in 15m30s: go buy the milk.
