# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PluginLoader class for dynamically loading plugins for the PFDL."""

from functools import wraps
import importlib.util
import os
import sys
import inspect
from typing import List
from pathlib import Path

from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses

base_classes_registry = {}


def base_class(existing_class_name):
    """A Decorator to mark a class that will extend an existing class.

    Registers the class in the base_classes_registry.
    """

    def decorator(cls):
        if existing_class_name not in base_classes_registry:
            base_classes_registry[existing_class_name] = []
        base_classes_registry[existing_class_name].append(cls)
        return cls

    return decorator


def wrap_method(original_method, new_methods):
    """Chains multiple methods together, calling them in order."""

    @wraps(original_method)
    def wrapper(*args, **kwargs):
        for method in new_methods:
            result = method(*args, **kwargs)
        return result

    return wrapper


def apply_plugin_to_base(base_class, plugin_class):
    """Applies the methods and attributes of the plugin_class to the base_class.

    Handles method overwrites with different argument counts, including class methods.
    """

    class CombinedClass(base_class, plugin_class):
        def __init__(self, *args, **kwargs):
            plugin_class.__init__(self, *args, **kwargs)

    # Method containers for chaining
    method_overrides = {}

    for name, method in plugin_class.__dict__.items():
        # Handle instance methods and class methods separately
        if callable(method):
            if name in method_overrides:
                method_overrides[name].append(method)
            else:
                method_overrides[name] = [getattr(base_class, name, None), method]
        elif not name.startswith("__"):
            # Add class attributes (non-callable)
            setattr(CombinedClass, name, method)

    # Add or override instance methods in CombinedClass
    for name, methods in method_overrides.items():
        original_method = methods[0] if methods[0] is not None else None
        combined_methods = methods[1:]  # Plugins' methods

        if original_method:
            setattr(CombinedClass, name, wrap_method(original_method, combined_methods))
        else:
            setattr(
                CombinedClass, name, wrap_method(lambda *args, **kwargs: None, combined_methods)
            )

    # Add class-level attributes
    for name, attr in plugin_class.__dict__.items():
        if not callable(attr) and not name.startswith("__"):
            if not hasattr(CombinedClass, name):
                setattr(CombinedClass, name, attr)

    CombinedClass.__name__ = base_class.__name__
    CombinedClass.__qualname__ = CombinedClass.__name__

    return CombinedClass


class PluginLoader:
    """Loads plugins and applies them to the existing classes in the main project.

    The PluginLoader class is responsible for dynamically loading plugins from the plugin folder
    and applying them to the existing classes in the main project. It automatically detects all
    classes in the main project and combines them with the plugin classes to create the final classes.
    """

    def __init__(self):
        self.existing_classes = self.get_existing_classes()

    def get_existing_classes(self):
        """Automatically detect and load all classes in the main project, excluding the plugin folder."""
        existing_classes = {}
        main_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        plugins_path = os.path.abspath(os.path.dirname(__file__))  # Path to the plugin folder

        # Walk through the project files to find Python files excluding the plugins folder
        for root, _, files in os.walk(main_project_path):
            if root.startswith(plugins_path):
                continue  # Skip files inside the plugins folder

            for file in files:
                if file.endswith(".py"):
                    module_name = os.path.splitext(file)[0]
                    module_path = os.path.join(root, file)

                    if module_name == "__init__":
                        continue

                    # Convert file path to importable module name
                    relative_path = os.path.relpath(module_path, main_project_path)
                    module_import_name = relative_path.replace(os.path.sep, ".")[
                        :-3
                    ]  # Remove '.py'

                    try:
                        # Dynamically import the module
                        spec = importlib.util.spec_from_file_location(
                            module_import_name, module_path
                        )
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_import_name] = module
                        spec.loader.exec_module(module)

                        # Inspect the module for classes
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if obj.__module__ == module_import_name:
                                existing_classes[name] = obj

                    except Exception as e:
                        print(f"Error loading module {module_import_name}: {e}")

        return existing_classes

    def load_plugin_modules(self, module_name, module_path):
        """Dynamically import a module given its path and register any classes that overwrite base classes."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    def load_plugins(self, plugins: List[str]):
        """Recursively load all Python files from plugin folders."""
        for plugin_folder in plugins:
            plugin_path = Path(__file__).parent / plugin_folder

            if not plugin_path.is_dir():
                raise ValueError("given plugin could not be found")

            # Walk through all files in the plugin folder
            for root, _, files in os.walk(plugin_path):
                for file in files:
                    if file.endswith(".py"):
                        module_name = f"{plugin_folder}.{file[:-3]}"  # Plugin folder + filename without .py
                        module_path = os.path.join(root, file)
                        self.load_plugin_modules(module_name, module_path)

    def get_final_classes(self):
        """Return a dictionary of final classes after applying plugins."""
        final_classes = {}

        for class_name, base_class in self.existing_classes.items():
            if class_name in base_classes_registry:
                # Combine the existing class with the plugin classes
                combined_class = base_class
                for plugin_class in base_classes_registry[class_name]:
                    combined_class = apply_plugin_to_base(combined_class, plugin_class)

                final_classes[class_name] = combined_class
            else:
                final_classes[class_name] = base_class

        return final_classes

    def get_pfdl_base_classes(
        self, pfdl_base_classes_path: str = "pfdl_scheduler"
    ) -> PFDLBaseClasses:
        """Return an instance of `PFDLBaseClasses` populated with final classes after applying plugins.

        Class names are dynamically handled. The base classes are populated with the final classes
        after applying plugins, and the registry is updated with any new classes that are not already
        present in the base classes.

        Args:
            pfdl_base_classes_path: The path to the PFDL base classes module.

        Returns:
            An instance of `PFDLBaseClasses` populated with the final classes after applying plugins.
        """
        final_classes = self.get_final_classes()
        base_classes = PFDLBaseClasses(base_dir=pfdl_base_classes_path)

        for class_name, class_ref in final_classes.items():
            # Try to find a matching property on the base class
            # Convert class_name to its lower_snake_case form to match typical property naming conventions
            property_name = self._class_name_to_property_name(class_name)

            # If the property exists, set it dynamically
            if hasattr(base_classes, property_name):
                setattr(base_classes, property_name, class_ref)
            else:
                base_classes.register_class(class_name, class_ref)

        return base_classes

    def _class_name_to_property_name(self, class_name: str) -> str:
        """Converts a class name to a property name by converting CamelCase to snake_case.

        Args:
            class_name: The name of the class to convert.

        Returns:
            The converted property name.
        """
        import re

        # Convert CamelCase to snake_case, and append '_class' to the name
        s1 = re.sub("([a-z])([A-Z])", r"\1_\2", class_name).lower()
        return f"{s1}_class"
