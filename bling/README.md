# GitHub Contributions Graph - Bling!

## Requirements

- A [Bling!](https://unexpectedmaker.com/bling) from Unexpected Maker
- A "classic" GitHub token with `user:read` access from [here](https://github.com/settings/tokens)
- A WiFi network
- Get [MicroPython](https://micropython.org/download/UM_TINYS3/) on your Bling! (I used `tinyuf2-unexpectedmaker_tinys3-0.18.1.zip` and `UM_TINYS3-20231005-v1.21.0.uf2`)
- Put the last two into `secrets.py` and put the files into your Bling! ([maybe with ampy](https://pypi.org/project/adafruit-ampy/))

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

- Buttons A/B (left side) will force a refresh

- Buttons C/D (right side) adjust brightness (not very well)


## Result

![photo](./bling.jpg)
