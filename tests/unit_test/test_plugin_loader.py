# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the PluginLoader class."""

import unittest
import os
from unittest.mock import patch, MagicMock
from pfdl_scheduler.plugins.plugin_loader import PluginLoader, base_class, apply_plugin_to_base


class TestPluginLoader(unittest.TestCase):
    """Test the PluginLoader class."""

    def test_apply_plugin_to_base(self):
        class BaseClass:
            def method(self):
                return "base"

        @base_class("BaseClass")
        class PluginClass:
            def method(self):
                return "plugin"

        combined_class = apply_plugin_to_base(BaseClass, PluginClass)
        instance = combined_class()

        # Check if method is overridden correctly
        self.assertEqual(instance.method(), "plugin")

    def test_class_name_to_property_name(self):
        plugin_loader = PluginLoader()
        property_name = plugin_loader._class_name_to_property_name("TestClassName")

        # Check if conversion is correct
        self.assertEqual(property_name, "test_class_name_class")
