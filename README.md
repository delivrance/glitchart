# GlitchArt

> Media Glitch Library for Python

<div align="center">
  <img src="https://i.imgur.com/XTP3x8a.jpg" height="255">
  <img src="https://i.imgur.com/lyDldEX.jpg" height="255"> 
  <img src="https://i.giphy.com/media/QxkMG1dOFWMYi0OrY5/giphy.gif" height="255">
</div>

**GlitchArt** is a Python library that applies a glitch effect to image and video files.
It does so by corrupting JPEG frames on random bytes, without screwing up files.
Supported media formats: **JPEG**, **PNG**, **WebP**, **MP4**.

## Requirements

- `Pillow`, which is automatically installed.
- Videos require `ffmpeg` and `ffprobe` available in PATH.

## Installing

``` shell
$ pip3 install glitchart
```

## Usage

``` python
import glitchart

glitchart.jpeg("starrynight.jpg")
```

## Documentation

Read the source code for now, or use Python's `help()` built-in function. E.g.:

```python
>>> import glitchart
>>> help(glitchart.jpeg)
...
```

## License

MIT © 2019-2020 [Dan](https://github.com/delivrance)
