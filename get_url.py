import urllib.request
import json
import time
import subprocess

time.sleep(5)
try:
    r = urllib.request.urlopen('http://localhost:4040/api/tunnels')
    data = json.loads(r.read())
    for t in data['tunnels']:
        if t['public_url'].startswith('https'):
            url = t['public_url']
            print()
            print('  ================================================')
            print('  YOUR VISHNU GITA URL:')
            print()
            print('  ' + url)
            print()
            print('  Share this with anyone!')
            print('  ================================================')
            subprocess.Popen(['cmd', '/c', 'start', url])
            break
except Exception as e:
    print('  Could not get URL. Check the ngrok window.')
    print('  Error:', e)
