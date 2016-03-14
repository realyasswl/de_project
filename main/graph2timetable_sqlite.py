import sqlite3, datetime

base_dir = "/home/liwang/STUDY/Y1Q3/de/coauthor/dblp_coauthor/"
conn = sqlite3.connect(base_dir + "sqlite3.db")
c = conn.cursor()

min_time = -1009843139;
max_time = 1388534461;

runs = 10
eachlen = (max_time - min_time) / runs
for i in range(runs):
    t0 = i * eachlen + min_time
    t1 = t0 + eachlen
    t = (t0, t1,)
    resultset = c.execute("select count(*) from relationship where timestamp>=? and timestamp<?", t)
    print("run %d,from %s to %s" % (i, datetime.datetime.fromtimestamp(
        t0
    ).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(
        t1
    ).strftime('%Y-%m-%d %H:%M:%S')))
    for row in resultset:
        print(row)


        # create table relationship(START_ID integer,END_ID integer,weight integer,timestamp integer);
        # create table author(authorId integer,name text);
        # create table timetable(START_ID integer,END_ID integer, weight integer, starttime integer,endtime integer,timelength integer);
