#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import re
from subprocess import Popen, PIPE

from thumbor.engines.pil import Engine as PILEngine


GIFSICLE_SIZE_REGEX = re.compile(r'(?:logical\sscreen\s(\d+x\d+))')
GIFSICLE_IMAGE_COUNT_REGEX = re.compile(r'(?:(\d+)\simage)')

class Engine(PILEngine):
    @property
    def size(self):
        return self.image_size

    def run_gifsicle(self, command):
        p = Popen([self.context.server.gifsicle_path] + command.split(' '), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data = p.communicate(input=self.buffer)[0]
        return stdout_data

    def is_multiple(self):
        return self.frame_count > 1

    def update_image_info(self):
        self._is_multiple = False

        result = self.run_gifsicle('--info')
        size = GIFSICLE_SIZE_REGEX.search(result)
        self.image_size = size.groups()[0].split('x')
        self.image_size[0], self.image_size[1] = int(self.image_size[0]), int(self.image_size[1])

        count = GIFSICLE_IMAGE_COUNT_REGEX.search(result)
        self.frame_count = int(count.groups()[0])

    def load(self, buffer, extension):
        self.extension = self.get_mimetype(buffer)
        self.buffer= buffer
        self.operations = []
        self.update_image_info()

    def draw_rectangle(self, x, y, width, height):
        raise NotImplementedError()

    def resize(self, width, height):
        if width == 0 and height == 0:
            return

        if width > 0 and height == 0:
            arguments = "--resize-width %d" % width
        elif height > 0 and width == 0:
            arguments = "--resize-height %d" % height
        else:
            arguments = "--resize %dx%d" % (width, height)

        self.operations.append(arguments)

    def crop(self, left, top, right, bottom):
        arguments = "--crop %d,%d-%d,%d" % (left, top, right, bottom)
        self.operations.append(arguments)
        self.flush_operations()
        self.update_image_info()

    def rotate(self, degrees):
        if degrees not in [90, 180, 270]:
            return
        arguments = '--rotate-%d' % degrees
        self.operations.append(arguments)

    def flip_vertically(self):
        self.operations.append('--flip-vertical')

    def flip_horizontally(self):
        self.operations.append('--flip-horizontal')

    def flush_operations(self):
        if not self.operations:
            return

        self.buffer = self.run_gifsicle(" ".join(self.operations))

        self.operations = []

    def read(self, extension=None, quality=None):
        self.flush_operations()
        return self.buffer

    def convert_to_grayscale(self):
        self.operations.append('--use-colormap gray')
