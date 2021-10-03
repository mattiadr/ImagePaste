import sublime
import sublime_plugin
import sys
import os
from os import path
import re
# os specific imports
if sys.platform.startswith("linux"):
	# linux
	import subprocess
elif sys.platform.startswith("win32"):
	# windows
	from .PIL import ImageGrab
	from .PIL.BmpImagePlugin import DibImageFile
	from .PIL.PngImagePlugin import PngImageFile
	VALID_IMAGE_TYPES = (DibImageFile, PngImageFile)


# name, string format pairs for available syntaxes
SYNTAX_DICT = {
	"Markdown": "![](imgs/{})"
}


def is_clip_image():
	if sys.platform.startswith("linux"):
		p = subprocess.Popen(["xclip", "-selection", "clipboard", "-t", "image/png", "-o"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		return p.returncode == 0, out
	elif sys.platform.startswith("win32"):
		# windows
		img = ImageGrab.grabclipboard()
		return img != None and type(img) in VALID_IMAGE_TYPES, img
	else:
		# non supported
		return False, None


def save_image(img, path):
	if sys.platform.startswith("linux"):
		# linux
		with open(path, "wb") as fout:
			fout.write(img)
	elif sys.platform.startswith("win32"):
		# windows
		img.save(path, "PNG")


class ImagePasteCommand(sublime_plugin.TextCommand):
	def run(self, edit, image_name=None):
		# if the clipboard contains an image then this returns an empty string
		# we need to do this check because if we try to get clipboard content
		# with sublime text as source with xclip, sublime will hang
		if sublime.get_clipboard():
			self.view.run_command("paste")
			return

		# check if clipboard contains an image
		is_image, img = is_clip_image()

		if not is_image:
			# default to normal paste
			self.view.run_command("paste")
			return

		# ask user to save if file is new before continuing
		if not self.view.file_name():
			self.view.run_command("save")

		# check if we support current syntax
		syntax_name = self.view.syntax().name
		if syntax_name not in SYNTAX_DICT:
			sublime.error_message(f"Syntax '{syntax_name}' not supported")
			return

		# if we have an image and not a name raise error to trigger TextInputHandler
		if image_name == None and is_image:
			raise TypeError("required positional argument")

		image_name = image_name.strip()

		if image_name:
			image_name = "-" + image_name

		# image in clipboard and valid filename, proceed
		folder = path.dirname(self.view.file_name())
		img_folder = path.join(folder, "imgs")

		# create imgs dir if it does not exist
		if not path.isdir(img_folder):
			os.mkdir(img_folder)
			sublime.message_dialog(f"Images will be stored in '{img_folder}'")

		# find the highest number prefix for png files in img_folder
		next_num = max([0] + [int(re.match(r"^\d+", f).group(0)) for f in os.listdir(img_folder) if re.search(r"^\d+.*\.png$", f, re.IGNORECASE)]) + 1

		# save image to dir
		file_name = f"{next_num:03}{image_name}.png"
		save_image(img, path.join(img_folder, file_name))

		# add markdown image to file
		img_string = SYNTAX_DICT[syntax_name].format(file_name)
		for reg in self.view.sel():
			self.view.replace(edit, reg, img_string)

		# place cursor at the end of all regions
		reg = [sublime.Region(s.end()) for s in self.view.sel()]
		self.view.sel().clear()
		self.view.sel().add_all(reg)


	def input(self, args):
		return ImageNameInputHandler()


class ImageNameInputHandler(sublime_plugin.TextInputHandler):
	def placeholder(self):
		return "Image Name"

	def validate(self, text):
		return True
