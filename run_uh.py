#!/usr/bin/env python

# ###################################################
# Copyright (C) 2012 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

"""TUTORIAL: Welcome to the Unknown Horizons in-code tutorial!
This is a guide for people who are interested in how the code works.
All parts of it are marked with 'TUTORIAL', and every entry contains
a pointer to the next step. Have fun :-)

This is the Unknown Horizons launcher; it looks for FIFE and tries
to start the game. You usually don't need to work with this directly.
If you want to dig into the game, continue to horizons/main.py. """

import functools
import gettext
import optparse
import os
import platform
import signal
import sys


def main():
	check_dependencies()

	# abort silently on signal
	signal.signal(signal.SIGINT, functools.partial(exithandler, 130))
	signal.signal(signal.SIGTERM, functools.partial(exithandler, 1))

	init_environment()
	create_user_dirs()

	options = get_option_parser().parse_args()[0]

	import horizons.main

	horizons.main.start(options)


def check_dependencies():
	"""Check if python2 is used and required libraries are available."""

	# python up to version 2.6.1 returns an int. http://bugs.python.org/issue5561
	if platform.python_version_tuple()[0] not in (2, '2'):
		show_error_message('Unsupported Python version', 'Python 2 is required to run Unknown Horizons.')

	try:
		import yaml
	except ImportError:
		headline = 'Error: Unable to find required library "PyYAML".'
		msg = ('PyYAML (a required library) is missing and needs to be installed.\n' +
		       'The Windows installer is available at http://pyyaml.org/wiki/PyYAML. ' +
		       'Linux users should find it using their package manager under the name ' +
			   '"pyyaml" or "python-yaml".')
		show_error_message(headline, msg)


def exithandler(exitcode, signum, frame):
	"""Handles a kill quietly"""
	signal.signal(signal.SIGINT, signal.SIG_IGN)
	signal.signal(signal.SIGTERM, signal.SIG_IGN)
	print('')
	print('Oh my god! They killed UH.')
	print('You bastards!')
	sys.exit(exitcode)


def init_environment():
	# install dummy translation
	gettext.install('', unicode=True)


def create_user_dirs():
	"""Creates the userdir and subdirs. Includes from horizons."""
	from horizons.constants import PATHS

	for directory in (PATHS.USER_DIR, PATHS.LOG_DIR, PATHS.SCREENSHOT_DIR):
		if not os.path.isdir(directory):
			os.makedirs(directory)
	

def get_option_parser():
	"""Returns inited OptionParser object"""
	from horizons.constants import VERSION

	p = optparse.OptionParser(usage="%prog [options]", version=VERSION.string())
	p.add_option("-d", "--debug", dest="debug", action="store_true",
	             default=False, help="Enable debug output to stderr and a logfile.")
	p.add_option("--fife-path", dest="fife_path", metavar="<path>",
	             help="Specify the path to FIFE root directory.")
	p.add_option("--restore-settings", dest="restore_settings", action="store_true", default=False,
	             help="Restores the default settings. "
	                  "Useful if Unknown Horizons crashes on startup due to misconfiguration.")
	p.add_option("--mp-master", dest="mp_master", metavar="<ip:port>",
	             help="Specify alternative multiplayer master server.")
	p.add_option("--mp-bind", dest="mp_bind", metavar="<ip:port>",
	             help="Specify network address to bind local network client to. "
	                  "This is useful if NAT holepunching is not working but you can forward a static port.")

	start_uh = optparse.OptionGroup(p, "Starting Unknown Horizons")
	start_uh.add_option("--start-map", dest="start_map", metavar="<map>",
	             help="Starts <map>. <map> is the mapname.")
	start_uh.add_option("--start-random-map", dest="start_random_map", action="store_true",
	             help="Starts a random map.")
	start_uh.add_option("--start-specific-random-map", dest="start_specific_random_map",
	             metavar="<seed>", help="Starts a random map with seed <seed>.")
	start_uh.add_option("--start-scenario", dest="start_scenario", metavar="<scenario>",
	             help="Starts <scenario>. <scenario> is the scenarioname.")
	start_uh.add_option("--start-dev-map", dest="start_dev_map", action="store_true",
	             default=False, help="Starts the development map without displaying the main menu.")
	start_uh.add_option("--load-game", dest="load_game", metavar="<game>",
	             help="Loads a saved game. <game> is the saved game's name.")
	start_uh.add_option("--load-last-quicksave", dest="load_quicksave", action="store_true",
	             help="Loads the last quicksave.")
	start_uh.add_option("--edit-map", dest="edit_map", metavar="<map>",
	             help="Edit map <map>.")
	start_uh.add_option("--edit-game-map", dest="edit_game_map", metavar="<game>",
	             help="Edit the map from the saved game <game>.")
	p.add_option_group(start_uh)

	ai_group = optparse.OptionGroup(p, "AI options")
	ai_group.add_option("--ai-players", dest="ai_players", metavar="<ai_players>",
	             type="int", default=0,
	             help="Uses <ai_players> AI players (excludes the possible human-AI hybrid; defaults to 0).")
	ai_group.add_option("--human-ai-hybrid", dest="human_ai", action="store_true",
	             help="Makes the human player a human-AI hybrid (for development only).")
	ai_group.add_option("--force-player-id", dest="force_player_id",
	             metavar="<force_player_id>", type="int", default=None,
	             help="Set the player with id <force_player_id> as the active (human) player.")
	ai_group.add_option("--ai-highlights", dest="ai_highlights", action="store_true",
	             help="Shows AI plans as highlights (for development only).")
	ai_group.add_option("--ai-combat-highlights", dest="ai_combat_highlights", action="store_true",
	             help="Highlights combat ranges for units controlled by AI Players (for development only).")
	p.add_option_group(ai_group)

	dev_group = optparse.OptionGroup(p, "Development options")
	dev_group.add_option("--debug-log-only", dest="debug_log_only", action="store_true",
	             default=False, help="Write debug output only to logfile, not to console. Implies -d.")
	dev_group.add_option("--debug-module", action="append", dest="debug_module",
	             metavar="<module>", default=[],
	             help="Enable logging for a certain logging module (for developing only).")
	dev_group.add_option("--logfile", dest="logfile", metavar="<filename>",
	             help="Writes log to <filename> instead of to the uh-userdir")
	dev_group.add_option("--fife-in-library-path", dest="fife_in_library_path", action="store_true",
	             default=False, help=optparse.SUPPRESS_HELP)
	dev_group.add_option("--profile", dest="profile", action="store_true",
	             default=False, help="Enable profiling (for developing only).")
	dev_group.add_option("--max-ticks", dest="max_ticks", metavar="<max_ticks>", type="int",
	             help="Run the game for <max_ticks> ticks.")
	dev_group.add_option("--no-freeze-protection", dest="freeze_protection", action="store_false",
	             default=True, help="Disable freeze protection.")
	dev_group.add_option("--string-previewer", dest="stringpreview", action="store_true",
	             default=False, help="Enable the string previewer tool for scenario writers")
	dev_group.add_option("--no-preload", dest="nopreload", action="store_true",
	             default=False, help="Disable preloading while in main menu")
	dev_group.add_option("--game-speed", dest="gamespeed", metavar="<game_speed>", type="float",
	             help="Run the game in the given speed (Values: 0.5, 1, 2, 3, 4, 6, 8, 11, 20)")
	dev_group.add_option("--gui-test", dest="gui_test", metavar="<test>",
	             default=False, help=optparse.SUPPRESS_HELP)
	dev_group.add_option("--gui-log", dest="log_gui", action="store_true",
	             default=False, help="Log gui interactions")
	dev_group.add_option("--sp-seed", dest="sp_seed", metavar="<seed>", type="int",
	             help="Use this seed for singleplayer sessions.")
	dev_group.add_option("--generate-minimap", dest="generate_minimap",
	             metavar="<parameters>", help=optparse.SUPPRESS_HELP)
	dev_group.add_option("--create-mp-game", action="store_true", dest="create_mp_game",
	             help="Create an multiplayer game with default settings.")
	dev_group.add_option("--join-mp-game", action="store_true", dest="join_mp_game",
	             help="Join first multiplayer game.")
	if VERSION.IS_DEV_VERSION:
		dev_group.add_option("--interactive-shell", action="store_true", dest="interactive_shell",
	             help="Starts an IPython kernel. Connect to the shell with: ipython console --existing")
		dev_group.add_option("--no-atlas-generation", action="store_false", dest="atlas_generation",
	             default=True, help="Disable atlas generation.")
	p.add_option_group(dev_group)

	return p


def show_error_message(title, message):
	print(title)
	print(message)

	try:
		import Tkinter
		import tkMessageBox
		window = Tkinter.Tk()
		window.wm_withdraw()
		tkMessageBox.showerror(title, message)
	except ImportError:
		# tkinter may be missing
		pass

	sys.exit(1)


if __name__ == '__main__':
	main()
