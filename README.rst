PyDita-AST
==========

A Python wrapper to convert XML documentation into RST files and the Sphinx documentation.

|pyansys| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/pydita-ast.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pydita_ast/

.. |codecov| image:: https://codecov.io/gh/ansys/pydita-ast/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pydita-ast

.. |GH-CI| image:: https://github.com/ansys/pydita-ast/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pydita-ast/actions/workflows/ci_cd.yml

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
  :target: https://github.com/psf/black
  :alt: black


Overview
--------

The PyDita-AST project aims to automatically generate a Python library and a related 
Sphinx documentation from an XML documentation.


Documentation and issues
------------------------

For more information, see the `Documentation <https://pydita-ast.docs.pyansys.com>`_ page.

Feel free to post issues and other questions at `PyDita-AST Issues
<https://github.com/ansys/pydita-ast/issues>`_.  This is the best place
to post questions and code.

Getting started
---------------

The XML documentation needs to be organized as follow:

Don't forget to close the image tag.

![Alt text](https://g.gravizo.com/svg?
   digraph "sphinx-ext-graphviz" {
      size="8,6";
      rankdir="LR";
      bgcolor="white";
      graph [
        fontname="Verdana", fontsize="10", color="black", fillcolor="white", splines=ortho, nodesep=0.2
      ];
      node [
        fontname="Verdana", fontsize="10", style="filled", color="black", fillcolor="#ffc107", shape="rarrow"
      ];
      edge[
       arrowsize="0.5"
      ]

      XML_directory [
        label="XML_documentation", shape="folder"
      ];

      terms [
        label="terms", shape="folder"
      ];

      character_directory [
        label="ent", shape="folder"
      ];

      cd_ent_files [
        label=".ent files", shape="file"
      ];

      glb [
        label="glb", shape="folder"
      ];

      manual_file [
        label="manuals.ent", shape="file"
      ];
     
      global_terms_file [
        label="terms_global.ent", shape="file"
      ];

      variable_file [
        label="build_variables.ent", shape="file"
      ];

      graphics [
        label="graphics", shape="folder"
      ];

      gifs [
        label="gifs", shape="file"
      ];

      images [
        label="images", shape="file"
      ];

      links [
        label="links", shape="folder"
      ];

      db_files [
        label=".db files", shape="file"
      ];

      xml [
        label="xml", shape="folder"
      ];

      subdirectorys [
        label="subdirectorys", shape="folder"
      ];

      mathgraphics_directory [
        label="mathgraphics_directory", shape="folder"
      ];

      svg_files [
        label=".svg files", shape="file"
      ];

      sub_xml_files[
        label=".xml files", shape="file"
      ];

      xml_xml_files [
        label=".xml files", shape="file"
      ];

      xml_ent_files [
        label=".ent files", shape="file"
      ];


   XML_directory -> terms
   XML_directory -> graphics
   XML_directory -> links
   XML_directory -> xml

   terms -> character_directory

   character_directory -> cd_ent_files

   terms -> glb
   
   glb -> manual_file
   glb -> global_terms_file
   glb -> variable_file

   graphics -> gifs
   graphics -> images

   links -> db_files

   xml -> subdirectorys
   xml -> xml_xml_files
   xml -> xml_ent_files

   subdirectorys -> mathgraphics_directory
   mathgraphics_directory -> svg_files

   subdirectorys -> sub_xml_files

  }
)
