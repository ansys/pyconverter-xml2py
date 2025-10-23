Customized functions
====================

If generated functions need to be customized, the following steps can be followed:

1. Identify the function to be customized.
2. Create a separated file for the customized function, typically in a `function_name.py` file.
   You can add specific logic in its code, import necessary modules, or create an example section
   in its docstring for instance.
3. Repeat the process for any additional functions that need customization.
4. Add all those function files in a specific folder, such as `custom_functions/`.
5. Pass the path to this folder in the `custom_functions` argument when running the code generation
   command.
