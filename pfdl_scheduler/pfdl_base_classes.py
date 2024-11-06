# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PFDLBaseClasses class."""

import os
import importlib
import inspect


class PFDLBaseClasses:
    def __init__(self, base_dir="pfdl_scheduler"):
        self._class_registry = {}
        self._class_instances = {}
        self._base_dir = base_dir  # Base directory for project scanning
        self._default_classes = self._scan_project_classes()

    def register_class(self, name, class_reference):
        """Register a custom class with a specific name."""
        self._class_registry[name] = class_reference

    def get_class(self, name):
        """Return the registered class if available, otherwise the default class."""
        # Check if the class is registered
        if name in self._class_registry:
            return self._class_registry[name]

        # Fall back to default if not registered
        return self._get_default_class(name)

    def get_instance(self, name, *args, **kwargs):
        """Instantiate the class dynamically if not already instantiated."""
        if name not in self._class_instances:
            class_ref = self.get_class(name)
            if class_ref is None:
                raise ValueError(f"Class '{name}' not found.")
            self._class_instances[name] = class_ref(*args, **kwargs)  # Instantiate with args
        return self._class_instances[name]

    def _scan_project_classes(self):
        """Scan the project folder for all available classes, ignoring 'plugins' folder."""
        class_map = {}
        for root, dirs, files in os.walk(self._base_dir):
            # Skip the 'plugins' folder if encountered
            dirs[:] = [d for d in dirs if d != "plugins"]

            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    # Create the module path by converting file path to importable module
                    module_path = os.path.join(root, file)
                    module_name = self._module_name_from_path(module_path)

                    try:
                        # Dynamically import the module
                        module = importlib.import_module(module_name)

                        # Find all classes defined in the module
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # Map class name to its full module path
                            class_map[name] = f"{module_name}.{name}"
                    except Exception as e:
                        # Handle any import errors
                        print(f"Failed to import {module_name}: {e}")
        return class_map

    def _module_name_from_path(self, path):
        """Convert a file path to a valid module import path."""
        module_name = path.replace(os.sep, ".")[:-3]
        if module_name.startswith("."):
            module_name = module_name[1:]
        return module_name

    def _get_default_class(self, name):
        """Dynamically load the default class based on the component name."""
        if name not in self._default_classes:
            raise ValueError(f"Default class for '{name}' not found.")

        # Extract the module path and class name
        full_class_path = self._default_classes[name]
        module_path, class_name = full_class_path.rsplit(".", 1)

        # Dynamically import the class from the module
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def clear_registry(self):
        """Clear the registry and instances."""
        self._class_registry.clear()
        self._class_instances.clear()
