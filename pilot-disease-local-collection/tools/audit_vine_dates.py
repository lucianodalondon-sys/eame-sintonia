import datetime, re

# decode the UTF-16BE /Title octal-escaped strings found in both files
raw_title = b'\xfe\xff\x00B\x00o\x00l\x00l\x00e\x00t\x00t\x00i\x00n\x00o\x00 \x00i\x00n\x00f\x00e\x00z\x00i\x00o\x00n\x00i\x00 \x00p\x00e\x00r\x00o\x00n\x00o\x00s\x00p\x00o\x00r\x00a'
print('decoded /Title (both files):', repr(raw_title.decode('utf-16-be')))
print()

it_days = ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi', 'sabato', 'domenica']

for label, d, visible_day, visible_date in [
    ('5d0669adb9c4 (peronospora)', datetime.date(2019, 6, 17), 'lunedi', '17 giugno'),
    ('e0e176fb1a87 (oidio)',       datetime.date(2019, 7, 4),  'giovedi', '4 luglio'),
]:
    actual = it_days[d.weekday()]
    print('%s' % label)
    print('   PDF CreationDate ->', d.isoformat())
    print('   visible text says -> "%s %s"' % (visible_day, visible_date))
    print('   weekday of that date in 2019 ->', actual)
    print('   MATCH:', actual == visible_day)
    # what weekday would it be in the Plone published_at years?
    for y in (2013, 2014):
        try:
            alt = d.replace(year=y)
            print('   same day/month in %d would be %s' % (y, it_days[alt.weekday()]))
        except ValueError:
            pass
    print()
