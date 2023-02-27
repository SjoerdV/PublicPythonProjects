#!/usr/bin/env python3

"""
License:
This file is part of the 'PublicPythonProjects' distribution (https://github.com/sjoerdv or http://sjoerdv.github.io).
Copyright (C) 2022  Sjoerd de Valk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Description:
This is an Captcha generator program, which outputs a png image file based on some input text.

Prerequisites:
* Python3 3.9+
* pip install captcha

References:
https://www.makeuseof.com/python-captcha-create/

Image Sources:

Tested on:
* Linux
** OS: LMDE 5 (elsie) x86_64
** Kernel: 6.0.0-0.deb11.2-amd64
** WM: Cinnamon 5.4.12
** Python3: 3.9.2
* Windows
** OS: Windows 10 21H2
** Python3: 3.9.5

Example:
captcha_generator.py
"""

# Import modules
from __future__ import annotations
from datetime import datetime
from captcha.image import ImageCaptcha

# specify dimensions
image = ImageCaptcha(width = 300, height = 100)

# enter the text to create its captcha
captcha_text = input("Please enter text: ")

# generate the text-based captcha
data = image.generate(captcha_text)

# generate the text-based captcha
file_name = str(datetime.now().isoformat(timespec="seconds"))

# save the captcha image file
image.write(captcha_text, (file_name) + ".png")
