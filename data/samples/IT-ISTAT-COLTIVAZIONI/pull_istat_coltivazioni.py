import urllib.request, time, sys, os

BASE = 'https://esploradati.istat.it/SDMXWS/rest/'
OUT = os.path.dirname(os.path.abspath(__file__))
H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9',
    'Accept': 'application/vnd.sdmx.data+csv;version=1.0.0;labels=both',
}

REGIONS = ['IT', 'ITC1', 'ITC2', 'ITC3', 'ITC4', 'ITDA', 'ITD1', 'ITD2', 'ITD3',
           'ITD4', 'ITD5', 'ITE1', 'ITE2', 'ITE3', 'ITE4', 'ITF1', 'ITF2',
           'ITF3', 'ITF4', 'ITF5', 'ITF6', 'ITG1', 'ITG2']

DT = ['ART', 'PA', 'TP_QUIN_EXT', 'HP_Q_EXT', 'TP_HECT_EXT', 'TPT']

CROPS = sys.argv[1].split(',')
START = sys.argv[2] if len(sys.argv) > 2 else '2024'
TAG = sys.argv[3] if len(sys.argv) > 3 else 'pull'

key = 'A.%s.%s.%s.' % ('+'.join(REGIONS), '+'.join(DT), '+'.join(CROPS))
u = BASE + 'data/IT1,101_1015,1.0/' + key + '?startPeriod=' + START
t = time.time()
try:
    r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=180)
    b = r.read()
    p = os.path.join(OUT, TAG + '.csv')
    with open(p, 'wb') as f:
        f.write(b)
    print('OK %s HTTP %s %d bytes %ss -> %s' % (u, r.status, len(b), round(time.time() - t, 1), p))
except Exception as e:
    print('ERR %s %s %s' % (u, type(e).__name__, str(e)[:300]))
