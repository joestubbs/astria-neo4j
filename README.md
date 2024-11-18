In this project, we explore the use of Neo4j for the purposes of a potential collaboration with the ATRIAGraph project.

Initial Commands
=================

1) Start the neo4j container:
 docker run -it --rm -p 7474:7474 -p 7687:7687 -v $(pwd)/data:/data -e NEO4J_AUTH=neo4j/tapis4ever --name=neo neo4j:5.22.0

2) Monitor cpu and memory usage:
  docker stats neo

3) Generate test csv files to import into the db (this was already done but can be run again as needed)
  python generate_test_data.py
 *  Copy new files into the container directory 
  sudo cp test_data_100k.csv data/

4) Load csv file into Neo4j -- NOTE: neo4 container should NOT be running. The following runs a new container just to do the import:

```
docker run -it --rm -p 7474:7474 -p 7687:7687 -v $(pwd)/data:/data -v $(pwd)/import:/import -e NEO4J_AUTH=neo4j/tapis4ever neo4j:5.22.0 neo4j-admin database import full neo4j --nodes=/import/test_data_100k.csv --overwrite-destination
```

100K example
------------
 Imported:
  100000 nodes
  0 relationships
  300000 properties
Peak memory usage: 518.0MiB


500k example
-------------
IMPORT DONE in 2s 597ms.
Imported:
  500000 nodes
  0 relationships
  1500000 properties
Peak memory usage: 519.5MiB


10M example
-----------
IMPORT DONE in 11s 580ms. 
Imported:
  10000000 nodes
  0 relationships
  30000000 properties
Peak memory usage: 632.1MiB




Timing results of some queries
-------------------------------

To time queries, first exec into the container:

```
docker exec -it neo
```

Then, from within the container:

```
# return total number of nodes 
cypher-shell --database=neo4j -u neo4j -p tapis4ever "MATCH (n) RETURN count(n) as nodes"

# return all distinct properties across all nodes 
cypher-shell --database=neo4j -u neo4j -p tapis4ever "MATCH (n) RETURN distinct keys(n)"

# property_1 is unique for each node 
cypher-shell --database=neo4j -u neo4j -p tapis4ever "MATCH (n) WHERE n.property_1 = 'prp_1' RETURN count(n) as nodes"

# property 2 is random so there should be a number of nodes returned for any given value
cypher-shell --database=neo4j -u neo4j -p tapis4ever "MATCH (n) WHERE n.property_2 = 10 RETURN count(n) as nodes"
```

Memory Usage
-------------

Usage started out a little under 500MB after server start up, even with the 10M data set. 
Queries did increase the usage temporarily though. For example, 
  * The simple count of all nodes increased usage to a peak of around ~850MB; usage went back down to around 550MB
  * The return distinct keys query and property_1 query increased usage to a peak of ~1.62GB; usage went down to around 1.41GB
  * The property_2 query increased usage to a peak of almost 1.7GB; usage went back down to around 1.45GB


ASTRIA Data Experiments
========================


Importing the Data
-------------------

The high-level strategy that seems to work is this:
1. Start with a v3 dump file
2. Start a v4.0 noe4j instance to use to import the data (this is multiple steps, see below).
3. Once the data has been imported to a 4.0 instance, run a 4.4 instance "on top of" the data directory. This seems to work. 

Work directory: `~/tmp/ASTRIA` and assumes a directory, `~/tmp/ASTRIA/data` and `~/tmp/ASTRIA/import`. The `~/tmp/data` contains the Neo4j database while `~/tmp/import` contains a dump file, `graph.db.dump`.

First, need to start container to create the initial database shell

```
docker run -it --rm -p 7474:7474 -p 7687:7687 -v $(pwd)/data:/data -v $(pwd)/import:/import -e NEO4J_AUTH=neo4j/tapis4ever -e NEO4J_dbms_allow__upgrade=true neo4j:4.0
```

Shut down this container so the server stops, and then create a new container to load data:

```
docker run -it --entrypoint=bash --rm -p 7474:7474 -p 7687:7687 -v $(pwd)/data:/data -v $(pwd)/import:/import -e NEO4J_AUTH=neo4j/tapis4ever -e NEO4J_dbms_allow__upgrade=true neo4j:4.0
```

Next, import the data from the dump file:

```
neo4j-admin load --database=neo4j --from=/import/graph.db.dump --force
```

Finally, exit the shell to stop that container and start up Neo4j as normal. Here, we specify `neo4j:4.0`.

```
docker run \
  -it --rm \
  --name neo4j4.4 \
  -p 7474:7474 -p 7687:7687 \
  -v $(pwd)/data:/data -v $(pwd)/import:/import \
  -e NEO4J_AUTH=neo4j/tapis4ever \
  -e NEO4J_dbms_allow__upgrade=true \ 
  -e NEO4J_apoc_export_file_enabled=true \
  -e NEO4J_apoc_import_file_enabled=true \
  -e NEO4J_apoc_import_file_use__neo4j__config=true \
  -e NEO4JLABS_PLUGINS=\[\"apoc\"\] \
  -e dbms_security_procedures_unrestricted=algo.*,apoc.* \
  neo4j:4.0
```

Once the server has started and imported the data correctly, one can run the same command above, replacing `neo4j:4.0` with `neo4j:4.4`.