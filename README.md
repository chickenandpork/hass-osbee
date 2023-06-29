# hass-osbee

Simple integration for OpenSprinkler Bee (OSBee) irrigation controller in Home Assistant

This is currently a hack-together integration for the OpenSprinkler "OSBee" in the most basic sense.
It has limited configurability, and sub-optimal config, but it's a start.  Using this integration,
one or more OSBee should appear as:
 - Sensor showing Wifi RSSI power
 - Binary Sensor for each zone, showing whether it's running
 - Switch for each zone, allowing to turn on/off.

In current form, one OSBee creates one sensor, 3 binary_sensors, 3 switches, all named
"osbee <MacAddress> <thing>"; for example, with MacAddreaa c4:5b:be:12:34:56, you'll see:
 - sensor "osbee c45bbe123456 rssi" showing Received Signal strength (in dB) (so -20dB is 1% of full power, -30dB is 0.1%)
 - binary_sensor "osbee c45bbe123456 zone 0" showing whether zone 1 is running/open/on
 - binary_sensor "osbee c45bbe123456 zone 2" showing whether zone 2 is running/open/on
 - binary_sensor "osbee c45bbe123456 zone 3" showing whether zone 3 is running/open/on
 - switch "osbee c45bbe123456 zone 0" through which you can turn on zone 1
 - switch "osbee c45bbe123456 zone 1" through which you can turn on zone 2
 - switch "osbee c45bbe123456 zone 2" through which you can turn on zone 3

OSBee runs sprinklers for a preset time, so these switches turn on until turned off, or until 30
minutes has passed.  Every time you turn on or off a zone, the 30-minute max is reset.

Currently, the auth token is hard-coded to the default, and the logs are REALLY SPAMMY; I'll clean
those up soon.  Yes, that default token is in the documentation for OSBee.


## Errors, feature-requests

Please file a github issue: https://github.com/chickenandpork/hass-osbee/issues/new

This is volunteer work, but I want to improve this integration to help more people.  If there's a
bug, issue, or feature-request, please file it as a github issue.  If there sparse documentation
doesn't explain, file an issue, and we can figure it out together, perhaps improving the code to be
more intuitive, perhavps adding more documentation.


## How to Use

This is currently a hack-together integration for the OpenSprinkler "OSBee" to appear as sensor(s),
switches, and binary sensor; it's currently tested as YAML config because that's currently the
easiest way to unittest.  More details in the file "docs/YAML-CONFIGS.md" in the repo.

### Where I Want the Config to Be

My goal was to configure as a simple `osbee:` block like this, but we're not there yet:

```yaml
osbee:
  - host: 192.168.1.77
    token: BobIsAGiant
  - host: 192.168.2.44
    token...

```

To reiterate, we're not there yet, but that's where I'd like to be.  I know that YAML concerns some
people, and Home-Assistant seems to be eliminating all text config, but until it's completely
banned, this is what works so very well.


### Configuring the Current Code

Right now, this current release, you will need to make redundant platform configs per-entity.  For
example, assuming you have two OSBees (on 192.168.1.44 and 192.168.1.45):

```yaml

binary_sensor:
  - platform: osbee
    host: 192.168.1.44
  - platform: osbee
    host: 192.168.1.45

sensor:
  - platform: osbee
    host: 192.168.1.44
  - platform: osbee
    host: 192.168.1.45

switch:
  - platform: osbee
    host: 192.168.1.44
  - platform: osbee
    host: 192.168.1.45
```

Currently, in THIS release, the token is set to the default.  If you want configurability sooner,
please file an issue in this GitHub Project.  Yes, it tells me what's important, and tells me "hey,
someone uses this, it's a useful thing".


### What about Config Flow?

I found the most difficulty in config_flow.  Really, it's documented in a way that likely makes
sense once you know it, but it's hard for a beginning Home-Assistant Integration-Developer to
decipher (I've been coding a long long time, not necessarily well, but new to Home-Assistant's
flavour of python).

As well, the examples don't work, and there's a lot of magic stuff that's not explained.  I don't
think my coding preferences align with Python in general (I like strong-typing both to catch errors
AT BUILD TIME plus as a documentation benefit) and python is really the other extreme.  ...so I'm
doing my best.

This was maybe the 7th or 8th iteration of building this as an integration.  I don't know if I got
the config schema for config_flow correct in every one.

If you really want Config-Flow, please file a Github Issue discussing it.  I'll know you use this
integration, get a brief ego-boost, and get an idea of what you're doing and how I can maybe help.


## Text-Based Configs

see "docs/YAML-CONFIGS.md" in the repo.
