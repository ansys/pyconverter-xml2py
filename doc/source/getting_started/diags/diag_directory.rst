.. graphviz::
    :caption: Pre-defined XML directory format.
    :alt: Pre-defined XML directory format.
    :align: center

     digraph "sphinx-ext-graphviz" {
         size="8,6";
         rankdir="LR";
         bgcolor="white";
         graph [
           fontname="Verdana", fontsize="10", color="black", fillcolor="white", splines=ortho
         ];
         node [
           fontname="Verdana", fontsize="10", style="filled", color="black", fillcolor="#ffc107"
         ];

         XML_directory [
           label="XML_documentation", shape="folder"
         ];

         graphics [
           label="graphics", shape="folder"
         ]

         gifs [
           label="gifs", shape="file"
         ]

         images [
           label="images", shape="file"
         ]

         links [
           label="links", shape="folder"
         ]

         db_files [
           label=".db files", shape="file"
         ]

         terms [
           label="terms", shape="folder"
         ]

         glb [
           label="glb", shape="folder"
         ]

         variable_file [
           label="build_variables.ent", shape="file"
         ]

         global_terms_file [
           label="terms_global.ent", shape="file"
         ]

         manual_file [
           label="manuals.ent", shape="file"
         ]

         character_directory [
           label="ent", shape="folder"
         ]

         cd_ent_files [
           label=".ent files", shape="file"
         ]

         xml [
           label="xml", shape="folder"
         ]

         subdirectorys [
           label="subdirectorys", shape="folder"
         ]

         sub_xml_files[
           label=".xml files", shape="file"
         ]

         mathgraphics_directory [
           label="mathgraphics_directory", shape="folder"
         ]

         svg_files [
           label=".svg files", shape="file"
         ]

         xml_xml_files [
           label=".xml files", shape="file"
         ]

         xml_ent_files [
           label=".ent files", shape="file"
         ]

      XML_directory -> graphics
      XML_directory -> links
      XML_directory -> terms
      XML_directory -> xml

      graphics -> gifs
      graphics -> images

      links -> db_files

      terms -> glb
      terms -> character_directory

      glb -> variable_file
      glb -> global_terms_file
      glb -> manual_file

      character_directory -> cd_ent_files

      xml -> subdirectorys
      xml -> xml_xml_files
      xml -> xml_ent_files

      subdirectorys -> sub_xml_files
      subdirectorys -> mathgraphics_directory

      mathgraphics_directory -> svg_files

     }



