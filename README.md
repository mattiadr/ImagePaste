# ImagePaste

Sublime text package that allows you to paste images stored in the clipboard directly in markdown.

When pressing the shortcut (default `ctrl+alt+v`) you will be prompted for a name, the image will be saved in the folder `imgs` in the same directory as the current file and a link will be pasted.
If no image is found in the clipboard this will fallback to the default paste command.

Currently only supports markdown and works on Windows and Linux.

## Installation

Clone this repository in the `Data/Packages` directory.

## Requirements

[Pillow](https://github.com/python-pillow/Pillow) is required for this script to work on windows and is already shipped with this repository.
