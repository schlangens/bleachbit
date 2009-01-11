# vim: ts=4:sw=4:expandtab

## BleachBit
## Copyright (C) 2009 Andrew Ziem
## http://bleachbit.sourceforge.net
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import ConfigParser

from globals import *

boolean_keys = ['auto_hide', 'check_online_updates', 'first_start', 'shred']

class Options:
    """Store and retrieve user preferences"""
    def __init__(self):
        # restore options from disk
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(options_file)
        if not self.config.has_section("bleachbit"):
            self.config.add_section("bleachbit")

        # set defaults
        self.__set_default("auto_hide", False)
        self.__set_default("check_online_updates", True)
        self.__set_default("shred", False)

        if not self.config.has_section('preserve_languages'):
            import locale
            import Unix
            __locale = locale.getdefaultlocale()[0]
            lang = Unix.locales.language_code(__locale)
            print "debug: automatically preserving language '%s'" % (lang,)
            self.set_language(lang, True)

        # BleachBit upgrade or first start ever
        if not self.config.has_option('bleachbit', 'version') or \
            self.get('version') != APP_VERSION:
            self.set('first_start', True)

        # set version
        self.set("version", APP_VERSION)


    def __flush(self):
        """Write information to disk"""
        if not os.path.exists(options_dir):
            os.makedir(options_dir, 0700)
        f = open(options_file, 'wb')
        self.config.write(f)


    def __set_default(self, key, value):
        """Set the default value"""
        if not self.config.has_option('bleachbit', key):
            self.set(key, value)


    def get(self, option):
        """Retrieve a general option"""
        if option in boolean_keys:
            return self.config.getboolean('bleachbit', option)
        return self.config.get('bleachbit', option)


    def get_language(self, id):
        """Retrieve value for whether to preserve the language"""
        if not self.config.has_option('preserve_languages', id):
            return False
        return self.config.getboolean('preserve_languages', id)


    def get_tree(self, parent, child):
        """Retrieve an option for the tree view.  The child may be None."""
        id = parent
        if None != child:
            id = id + "." + child
        if not self.config.has_option('tree', id):
            return False
        return self.config.getboolean('tree', id)


    def set(self, key, value):
        """Set a general option"""
        self.config.set('bleachbit', key, str(value))
        self.__flush()


    def set_language(self, id, value):
        """Set the value for a locale (whether to preserve it)"""
        if not self.config.has_section('preserve_languages'):
            self.config.add_section('preserve_languages')
        if self.config.has_option('preserve_languages', id) and not value:
            self.config.remove_option('preserve_languages', id)
        else:
            self.config.set('preserve_languages', id, str(value))
        self.__flush()


    def set_tree(self, parent, child, value):
        """Set an option for the tree view.  The child may be None."""
        if not self.config.has_section("tree"):
            self.config.add_section("tree")
        id = parent
        if None != child:
            id = id + "." + child
        if self.config.has_option('tree', id) and not value:
            self.config.remove_option('tree', id)
        else:
            self.config.set('tree', id, str(value))
        self.__flush()


    def toggle(self, key):
        """Toggle a boolean key"""
        self.set(key, not self.get(key))


options = Options()

import unittest

class TestOptions(unittest.TestCase):
    def test_Options(self):
        o = options
        v = o.get("check_online_updates")

        # toggle a boolean
        o.toggle('check_online_updates')
        self.assertEqual(not v, o.get("check_online_updates"))

        # restore original boolean
        o.set("check_online_updates", v)
        self.assertEqual(v, o.get("check_online_updates"))

        # these should always be set
        for b in boolean_keys:
            self.assert_(type(o.get(b)) is bool)

        # language
        value = o.get_language('en')
        self.assert_(type(value) is bool)
        o.set_language('en', True)
        self.assertEqual(o.get_language('en'), True)
        o.set_language('en', False)
        self.assertEqual(o.get_language('en'), False)
        o.set_language('en', value)

        # tree
        o.set_tree("parent", "child", True)
        self.assertEqual(o.get_tree("parent", "child"), True)
        o.set_tree("parent", "child", False)
        self.assertEqual(o.get_tree("parent", "child"), False)
        o.config.remove_option("tree", "parent.child")
        self.assertEqual(o.get_tree("parent", "child"), False)


if __name__ == '__main__':
        unittest.main()

