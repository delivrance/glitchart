# GlitchArt

> Media Glitch Library for Python

<div align="center">
  <img src="https://i.imgur.com/XTP3x8a.jpg" width="270">
  <img src="https://i.imgur.com/lyDldEX.jpg" width="270"> 
  <img src="https://media.giphy.com/media/28euAPLxdrhBaHOvmR/giphy.gif" width="270">
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

MIT © 2019 [Dan Tès](https://github.com/delivrance)
