# ###################################################
# Copyright (C) 2011 The Unknown Horizons Team
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

import os
import shutil
import os.path
import tempfile

from horizons.savegamemanager import SavegameManager
from horizons.util.python import decorators
from horizons.constants import VERSION
from horizons.util import DbReader

class SavegameUpgrader(object):
	"""The class that prepares saved games to be loaded by the current version."""

	def __init__(self, path):
		super(SavegameUpgrader, self).__init__()
		self.original_path = path
		self.using_temp = False
		self.final_path = None

	def _upgrade_to_rev44(self, db):
		# add trade history table
		db("CREATE TABLE IF NOT EXISTS \"trade_history\" (\"settlement\" INTEGER NOT NULL," \
		     "\"tick\" INTEGER NOT NULL, \"player\" INTEGER NOT NULL, " \
		     "\"resource_id\" INTEGER NOT NULL, \"amount\" INTEGER NOT NULL, \"gold\" INTEGER NOT NULL)")

	def _upgrade_to_rev45(self, db):
		# fix production queue table
		db("DROP TABLE production_queue")
		db("CREATE TABLE \"production_queue\" (object INTEGER NOT NULL, position INTEGER NOT NULL, production_line_id INTEGER NOT NULL)")

	def _upgrade(self):
		metadata = SavegameManager.get_metadata(self.original_path)
		rev = metadata['savegamerev']
		if rev == 0: # not a regular savegame, usually a map
			self.final_path = self.original_path
		elif rev == VERSION.SAVEGAMEREVISION: # the current version
			self.final_path = self.original_path
		else: # upgrade
			self.using_temp = True
			handle, self.final_path = tempfile.mkstemp(prefix='uh-savegame.' + os.path.basename(os.path.splitext(self.original_path)[0]) + '.', suffix='.sqlite')
			os.close(handle)
			shutil.copyfile(self.original_path, self.final_path)
			db = DbReader(self.final_path)

			if rev <= 44:
				self._upgrade_to_rev44(db)
			if rev <= 45:
				self._upgrade_to_rev45(db)

			db.close()

	def get_path(self):
		"""Return the path to the up-to-date version of the saved game."""
		if self.final_path is None:
			self._upgrade()
		return self.final_path

	def close(self):
		if self.using_temp:
			self.using_temp = False
			os.unlink(self.final_path)
		self.final_path = None

decorators.bind_all(SavegameUpgrader)