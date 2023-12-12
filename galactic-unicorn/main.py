import machine, time
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

import network
import json
import sys
import time
import urequests
from secrets import secrets

# returns the id of the button that is currently pressed or
# None if none are
def pressed():
    if galactic.is_pressed(GalacticUnicorn.SWITCH_A):
        return GalacticUnicorn.SWITCH_A
    if galactic.is_pressed(GalacticUnicorn.SWITCH_B):
        return GalacticUnicorn.SWITCH_B
    if galactic.is_pressed(GalacticUnicorn.SWITCH_C):
        return GalacticUnicorn.SWITCH_C
    if galactic.is_pressed(GalacticUnicorn.SWITCH_D):
        return GalacticUnicorn.SWITCH_D
    return None

def clear():
    global graphics
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()

def show_text(line1, line2="", pen=None):
    global graphics

    graphics.set_font("bitmap6")
    clear()
    if pen is None:
        pen = graphics.create_pen(155, 155, 155)
    graphics.set_pen(pen)
    graphics.text(line1, 2, -1, -1, 1)
    graphics.text(line2, 2, 5, -1, 1)
    galactic.update(graphics)

def error(line1, line2=""):
    print('Error:', line1, line2)
    show_text(line1, line2, pen = graphics.create_pen(155, 0, 0))
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

def draw(weeks, legend_pens):
    global graphics

    offset_y = 2
    limits = [ 0, 1, 20, 30, 40 ]

    clear()

    # Iterate over each week
    for week_number, week in enumerate(weeks, start=1):
        print(f"Week {week_number}:")

        # Iterate over each day in the week
        for day_index, day in enumerate(week['contributionDays']):
            date = day['date']
            count = day['contributionCount']

            idx = find_range_index(limits, count)
            if idx == -1:
                idx = len(limits) - 1

            print(f"  Date: {date}, Contribution Count: {count}, Index: {idx}")

            graphics.set_pen(legend_pens[idx])
            graphics.pixel(week_number - 1, day_index + offset_y)

    galactic.update(graphics)

def update(show_pixel=True):
    global graphics

    if show_pixel:
        graphics.set_pen(graphics.create_pen(0x39, 0xd3, 0x53))
        graphics.pixel(0,0)
        galactic.update(graphics)

    # Make HTTPS request and get JSON data
    contrib_data = get_contributions(secrets['gh_user'], secrets['gh_token'])
    #print(contrib_data)

    legend_pens = [
    # light mode
    #    graphics.create_pen(0xeb, 0xed, 0xf0),
    #    graphics.create_pen(0x9b, 0xe9, 0xa8),
    #    graphics.create_pen(0x40, 0xc4, 0x63),
    #    graphics.create_pen(0x30, 0xa1, 0x4e),
    #    graphics.create_pen(0x21, 0x6e, 0x39),

    # dark mode
        graphics.create_pen(0x16, 0x1b, 0x22),
        graphics.create_pen(0x0e, 0x44, 0x29),
        graphics.create_pen(0x00, 0x6d, 0x32),
        graphics.create_pen(0x26, 0xa6, 0x41),
        graphics.create_pen(0x39, 0xd3, 0x53),
    ]

    weeks = contrib_data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    draw(weeks, legend_pens)

# overclock to 200Mhz
#machine.freq(200000000)

# create galactic object and graphics surface for drawing
galactic = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

galactic.set_brightness(0.5)

# Connect to WiFi
connect_to_wifi(secrets['ssid'], secrets['password'])

if secrets['gh_user'] == '':
    error('NO GH USER')
if secrets['gh_token'] == '':
    error('NO GH TOKEN')

show_text('', 'LOADING...')
update(show_pixel=False)
last_update = time.time()

while True:
    if (time.time() - last_update > 300) or (pressed() != None):
        update()
        last_update = time.time()

    # brightness up/down
    if galactic.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        print("brightness up")
        galactic.adjust_brightness(0.05)
        galactic.update(graphics)
        time.sleep(0.25)
        continue
    elif galactic.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        print("brightness down")
        galactic.adjust_brightness(-0.05)
        galactic.update(graphics)
        time.sleep(0.25)
        continue

    time.sleep(0.5)
    pass
