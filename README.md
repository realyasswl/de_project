#About the project
Data engineering project on dblp_coauthor

http://konect.uni-koblenz.de/networks/dblp_coauthor
#How to run
currently we are using sqlite3, can always switch to other RDBMS with no cost. 

There are two tables, use statements below to create these tables:
  
  create table relationship(START_ID integer,END_ID integer,weight integer,timestamp integer);
  
  create table author(authorId integer,name text);
  
and

  sqlite> .separator ","

  sqlite> .import xxx.csv relationship

to import file into sqlite3, maybe need to remove the first line
