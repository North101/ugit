Inspired by [turfptax/ugit](https://github.com/turfptax/ugit)

# Micropython OTA Updates

Clones the configured github repo.

## Differences from [turfptax/ugit](https://github.com/turfptax/ugit)

* No hardcoded github
* Doesn't handle connecting to wifi
* Ignores folders
* Ignores files with a `.` prefix
* Ignores itself
* Only replaces files that haven't changed
* Works with non-UTF-8 files

## Getting Started

### Installation

Copy `ugit.py` to `/` or `/lib` folder of your device.

## Examples

### Without a config file
`/boot.py`
```python
import network
from ugit import Github

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID', 'Password')

Github(
  user='North101',
  repo='ugit',
  # Tag/Branch/SHA1
  ref='master',
  # Required if your repo is private
  token=None,
).pull(
  # Set if you want to pull only from a git subdirectory e.g. `/src/`
  git_root=None,
  # Files and Folders you want to ignore.
  # Folders must end with a `/`
  # Must be absolute i.e. full path from the root of the device
  ignore=[
    '/boot.py',
    '/my_folders/',
  ],
  # Whether or not to ignore files or folders that begin with `.`. Default: True
  ignore_dot_files=True,
)
```

### With a config file
`/.github.json`
```json
{
  "user": "North101",
  "repo": "ugit",
  "ref": "master",
  "token": null
}
```

`/boot.py`
```python
import network
from ugit import Github

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID', 'Password')

Github.from_config().pull(
  # Set if you want to pull only from a git subdirectory e.g. `/src/`
  git_root=None,
  # Files and Folders you want to ignore.
  # Folders must end with a `/`
  # Must be absolute i.e. full path from the root of the device
  ignore=[
    '/boot.py',
    '/my_folders/',
  ],
  # Whether or not to ignore files or folders that begin with `.`. Default: True
  ignore_dot_files=True,
)
```

### Update ugit.py

```python
import network
import ugit

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID', 'Password')

ugit.update()
```
