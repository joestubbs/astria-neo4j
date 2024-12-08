#!/bin/bash 

docker run -it --rm --name neo4j4.4 -p 7474:7474 -p 7687:7687 -v $(pwd)/data:/data -v $(pwd)/import:/import -e NEO4J_AUTH=neo4j/tapis4ever -e NEO4J_dbms_allow__upgrade=true -e NEO4J_apoc_export_file_enabled=true -e NEO4J_apoc_import_file_enabled=true -e NEO4J_apoc_import_file_use__neo4j__config=true -e NEO4JLABS_PLUGINS=\[\"apoc\"\] -e dbms_security_procedures_unrestricted="algo.*,apoc.*" neo4j:4.4
