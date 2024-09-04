import cProfile
from pathlib import Path
import pstats

from pyconverter.xml2py.cli import create_package  # noqa: F401

xml_path = Path("D:/repos/pyansys/mapdl-cmd-doc")
func_path = Path("./custom_functions")

cProfile.run("create_package(xml_path, custom_functions_path= func_path)", "output.pstats")

p = pstats.Stats("output.pstats")
p.sort_stats("cumulative").print_stats(10)
