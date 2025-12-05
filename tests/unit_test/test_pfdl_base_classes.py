# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the PFDLBaseClasses class."""

import unittest
from unittest.mock import patch, MagicMock
from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses


class TestPFDLBaseClasses(unittest.TestCase):
    """Test the PFDLBaseClasses class."""

    def test_register_class(self):
        pfdl_base_classes = PFDLBaseClasses()
        mock_class = type("MockClass", (object,), {})

        pfdl_base_classes.register_class("MockClass", mock_class)

        # Verify that the class is registered
        self.assertEqual(pfdl_base_classes.get_class("MockClass"), mock_class)

    def test_get_class_default(self):
        pfdl_base_classes = PFDLBaseClasses()
        mock_class = type("MockClass", (object,), {})

        # Simulate default class registration
        pfdl_base_classes._default_classes["MockClass"] = "module.MockClass"

        with patch(
            "pfdl_scheduler.pfdl_base_classes.importlib.import_module"
        ) as mock_import_module:
            mock_import_module.return_value = MagicMock(MockClass=mock_class)

            # Verify that the default class can be retrieved
            self.assertEqual(pfdl_base_classes.get_class("MockClass"), mock_class)

    def test_get_instance(self):
        pfdl_base_classes = PFDLBaseClasses()
        mock_class = type(
            "MockClass", (object,), {"__init__": lambda self, x: setattr(self, "x", x)}
        )

        pfdl_base_classes.register_class("MockClass", mock_class)

        # Verify instance creation and reuse
        instance = pfdl_base_classes.get_instance("MockClass", 5)
        self.assertEqual(instance.x, 5)
        instance2 = pfdl_base_classes.get_instance("MockClass")
        self.assertIs(instance, instance2)

    def test_clear_registry(self):
        pfdl_base_classes = PFDLBaseClasses()
        mock_class = type("MockClass", (object,), {})

        pfdl_base_classes.register_class("MockClass", mock_class)
        pfdl_base_classes.get_instance("MockClass")

        # Clear registry and instances
        pfdl_base_classes.clear_registry()

        # Verify that both registry and instances are cleared
        self.assertNotIn("MockClass", pfdl_base_classes._class_registry)
        self.assertNotIn("MockClass", pfdl_base_classes._class_instances)

    def test_module_name_from_path(self):
        pfdl_base_classes = PFDLBaseClasses()
        module_name = pfdl_base_classes._module_name_from_path("fake_dir/module.py")
        self.assertEqual(module_name, "fake_dir.module")

        pfdl_base_classes = PFDLBaseClasses()
        module_name = pfdl_base_classes._module_name_from_path("/fake_dir/module.py")
        self.assertEqual(module_name, "fake_dir.module")

    @patch("pfdl_scheduler.pfdl_base_classes.importlib.import_module")
    def test_get_default_class(self, mock_import_module):
        pfdl_base_classes = PFDLBaseClasses()
        mock_class = type("MockClass", (object,), {})
        pfdl_base_classes._default_classes["MockClass"] = "module.MockClass"

        mock_import_module.return_value = MagicMock(MockClass=mock_class)

        # Verify default class retrieval
        self.assertEqual(pfdl_base_classes._get_default_class("MockClass"), mock_class)

    def test_get_default_class_nonexistent(self):
        pfdl_base_classes = PFDLBaseClasses()
        with self.assertRaises(ValueError) as context:
            pfdl_base_classes._get_default_class("NonExistentClass")

        self.assertEqual(str(context.exception), "Default class for 'NonExistentClass' not found.")
