import machine
import neopixel

import network
import json
import sys
import time
import urequests
from secrets import secrets

num_pixels = 320
row_count = 40
brightness = 0.02

on_off_pin = machine.Pin(6, machine.Pin.OUT)
on_off_pin.value(1)

button_A = machine.Pin(11, machine.Pin.IN)
button_B = machine.Pin(10, machine.Pin.IN)
button_C = machine.Pin(33, machine.Pin.IN)
button_D = machine.Pin(34, machine.Pin.IN)

neo_pin = machine.Pin(18, machine.Pin.OUT)
np = neopixel.NeoPixel(neo_pin, num_pixels)
weeks = None

legend_pens = [
# light mode
#    (0xeb, 0xed, 0xf0),
#    (0x9b, 0xe9, 0xa8),
#    (0x40, 0xc4, 0x63),
#    (0x30, 0xa1, 0x4e),
#    (0x21, 0x6e, 0x39),

# dark mode
    (0x16, 0x1b, 0x22),
    (0x0e, 0x44, 0x29),
    (0x00, 0x6d, 0x32),
    (0x26, 0xa6, 0x41),
    (0x39, 0xd3, 0x53),
]

# returns the id of the button that is currently pressed or
# None if none are
def pressed():
    global button_A, button_B
    if button_A.value() == 1:
        return button_A
    if button_B.value() == 1:
        return button_B
    return None

def clear():
    global np, num_pixels
    for i in range(num_pixels):
        np[i] = (0, 0, 0)
    np.write()

def show_text(line1, line2="", pen=None):
    clear()

def error(line1, line2=""):
    print('Error:', line1, line2)
    show_text(line1, line2)
    while True:
        pass

def connect_to_wifi(ssid, password):
    if ssid == '' or password == '':
        error('NO CONFIG')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        show_text('CONNECT...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network connected!')
    show_text('', 'OK!')

def graphql_query(url, query, variables, token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'User-Agent': 'micropython/{}; urequests/unknown'.format(sys.version),
    }
    payload = {
        'query': query,
        'variables': variables
    }
    response = urequests.post(url, data=json.dumps(payload), headers=headers)
    try:
        response_data = response.json()
    except Exception as e:
        print('Exception:', e)
        print('Response body:', response.text)
        error('ERROR IN', 'RESPONSE')
    response.close()
    return response_data

def get_contributions(user, token):
    # https://medium.com/@yuichkun/how-to-retrieve-contribution-graph-data-from-the-github-api-dc3a151b4af
    query = """
query($userName:String!) {
  user(login: $userName){
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""
    return graphql_query('https://api.github.com/graphql', query, {'userName': user}, token)

def find_range_index(limits, number):
    for i in range(len(limits) - 1):
        if limits[i] <= number < limits[i + 1]:
            return i
    return -1

def pixel(ofs, col):
    global np, brightness
    np[ofs] = (
               int(col[0]*brightness),
               int(col[1]*brightness),
               int(col[2]*brightness),
            )

def draw(debug=False):
    global np, num_pixels, row_count, weeks

    skip_weeks = 13
    limits = [ 0, 1, 20, 30, 40 ]

    for i in range(num_pixels):
        np[i] = (0, 0, 0)

    # Iterate over each week
    for week_number, week in enumerate(weeks, start=1):
        if week_number <= skip_weeks:
            continue

        if debug:
            print(f"Week {week_number}:")

        # Iterate over each day in the week
        for day_index, day in enumerate(week['contributionDays']):
            date = day['date']
            count = day['contributionCount']

            idx = find_range_index(limits, count)
            if idx == -1:
                idx = len(limits) - 1

            pix_ofs = day_index*row_count + (week_number-skip_weeks-1)
            if debug:
                print(f"  Date: {date}, Contribution Count: {count}, Index: {idx}, Offset: {pix_ofs}")
            pixel(pix_ofs, legend_pens[idx])

    np.write()

def update(show_pixel=True):
    global np, weeks, brightness

    if show_pixel:
        pixel(0, (0x53, 0x39, 0xd3))
        np.write()

    # Make HTTPS request and get JSON data
    contrib_data = get_contributions(secrets['gh_user'], secrets['gh_token'])
    #print(contrib_data)

    weeks = contrib_data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    draw(debug=True)

clear()
pixel(80, (0x53, 0x39, 0xd3))
np.write()

# Connect to WiFi
connect_to_wifi(secrets['ssid'], secrets['password'])

if secrets['gh_user'] == '':
    error('NO GH USER')
if secrets['gh_token'] == '':
    error('NO GH TOKEN')

show_text('', 'LOADING...')
update(show_pixel=True)
last_update = time.time()

while True:
    if (time.time() - last_update > 300) or (pressed() != None):
        update()
        last_update = time.time()

    # brightness up/down
    if button_C.value() == 1:
      brightness+=0.005
      if brightness > 0.02:
        brightness = 0.02
      print("brightness up", brightness)
      draw()
      time.sleep(0.25)
      continue
    elif button_D.value() == 1:
      brightness-=0.005
      if brightness < 0.01:
        brightness = 0.01
      print("brightness down", brightness)
      draw()
      time.sleep(0.25)
      continue

    time.sleep(0.5)
    pass
