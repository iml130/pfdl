# PFDL Plugin System
The PFDL plugin system can be used to create plugins that extends the grammar and the underlying logic of the PFDL.
In the following, the different steps for creating your own plugin will be explained in detail.

## The Plugin Loader - modify PFDL code
The core of the plugin system is the `PluginLoader` class. This class can be used to load the desired plugins and for returning the overwritten classes.
The PFDL code base was designed in a way such that its base classes can be changed. Thus, the plugin loader returns a `PFDLBaseClasses` object which contains all base classes of the PFDL overwritten by the plugins (See the example below).

The plugin loader's `load_plugins` method requries a list of strings which are essentially the paths to the plugin folders in which he will search for classes with the decorator `@base_class("<name of the class that should be overwritten>")`. Important here is that the name of the overwritten base class must match with the acutal class. If a class has a decorator and is inside a folder in the plugins folder it will be used for overwritting the base respective base class. Additionally, the overwritten classes needs to inherit from the base class so that the new combined class receives all methods and attributes.

```python
@base_class("Instance")
class Instance(pfdl_scheduler.model.instance.Instance):
    ...
```

 An example of how to load plugins and receive the overwritten base classes is shown here:

```python
plugin_loader = PluginLoader()
plugin_loader.load_plugins(["plugins/sample_plugin_folder"])

pfdl_base_classes = plugin_loader.get_pfdl_base_classes()
```

The `Scheduler` class, which is the entry point for using the PFDL, has an optional paramter for the base classes which can be used with the newly created plugin base classes. This way, the user made changes will be directly inserted into the PFDL base code. If you want to also modify the Scheduler class a complete example would look like this:

```python
scheduler = pfdl_base_classes.scheduler_class(
    ...
    pfdl_base_classes=pfdl_base_classes,
)
```

## Merging Grammars
If you want to make changes to the base grammar of the PFDL you can do that by creating a custom Lexer and Parser file in the antlr `.g4` format. You only need to define your required rules.
If the rule names are not in the base grammar they will just be added as new rules.
If they already exists they will be added as an alternative to the old rule.

To generate a new grammar that contains the old rules and the newly or overwritten rules of the plugins, the `grammar_merge.py` script has to be executed inside the `plugins` folder.
The script requires a list of parser and subsequently a list of lexer files so that you can define which plugins should be used to create a combined grammar.
The order of the passed grammar files can change the overall result so keep that in mind. Moreover, due to the nature of such systems, some plugins might be not working when used together!

### The Parser folder
The `grammar_merge.py` script will call the ANTLR build script to generate Lexer, Parser, and Visitor python files that can be used by the plugin and stores them inside the `parser` folder inside the `plugins` folder. 
Internally, the newly generated clases will be inserted into the base classes which are then used by the PFDL base code.
In addition, if you want to check the merged grammar or want to manually edit it, the parser folder also contains the merged `.g4` files from which the parser files are generated.