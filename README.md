# PulseWrapper
Simple wrapper for controlling pulseaudio sink outputs. 
I wrote it to quickly switch between audio devices.

Beware: code is kinda dirty..

## Dependencies

- python 
- pacmd (pulseaudio)

## Install

Simply put the script into your PATH environment and give it execution rights.

## How To Use

```
pulse.py [options] [arg]
Options:
	--list-sinks or -l
	--list-apps
	--default-sink
	--setdefault= or -d with substring of sink name
		example: -d Hyper
	--toggle or -t arg to toggle between given sinks
		example: -t Hyper,Starship
	--help or -h
```
