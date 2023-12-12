# GitHub Contributions Graph - Galactic Unicorn

## Requirements

- A [Galatic Unicorn](https://shop.pimoroni.com/products/space-unicorns?variant=40842033561683) from Pimoroni
- A "classic" GitHub token with `user:read` access from [here](https://github.com/settings/tokens)
- A WiFi network
- Put the last two into `secrets.py` and put the files into your Galactic Unicorn ([maybe with ampy](https://pypi.org/project/adafruit-ampy/))

## Configuration

Edit `secrets.py`

```python
secrets = {
    # WiFi SSID
    'ssid': '',
    # WiFi password
    'password': '',
    # GitHub username
    'gh_user': 'disq',
    # GitHub token with user:read access
    'gh_token': ''
}
```

## Usage

- Refreshes the contributions graph every 5 minutes

- Buttons A/B/C/D (left side) will force a refresh

- Brightness keys adjust brightness


## Result

![photo](./galactic-unicorn.jpg)
