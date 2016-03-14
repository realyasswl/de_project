import sqlite3, pickle
import datetime as dt

base_dir = "/home/liwang/STUDY/Y1Q3/de/coauthor/dblp_coauthor/"
conn = sqlite3.connect(base_dir + "sqlite3.db")
c = conn.cursor()
'''
        create table relationship(START_ID integer,END_ID integer,weight integer,timestamp integer);
        create table author(authorId integer,name text);
        create table timetable(START_ID integer,END_ID integer, weight integer, starttime integer,endtime integer,timelength integer);
'''
# we approximately use 365 as the number of days in one year
one_year = 60 * 60 * 24 * 365
min_time = -1009843139;
max_time = 1388534461;
min_dt = dt.datetime.fromtimestamp(min_time)
max_dt = dt.datetime.fromtimestamp(max_time)


def dump_relationship_dist():
    t0 = min_dt
    t1 = 0
    i = 0
    result = []
    while t0 < max_dt:
        t1 = t0.replace(year=t0.year + 1)
        t = (dt.datetime.timestamp(t0), dt.datetime.timestamp(t1),)
        resultset = c.execute("select count(*) from relationship where timestamp>=? and timestamp<?", t)
        print("run %d,from %s to %s" % (i,
                                        t0.strftime('%Y-%m-%d %H:%M:%S'),
                                        t1.strftime('%Y-%m-%d %H:%M:%S')))

        for row in resultset:
            result.append((t0, row[0]))
            print((t0, row[0]))

        t0 = t1
        i += 1
    try:
        f = open("/home/liwang/PycharmProjects/dm_project/coauthordist", "wb")
        pickle.dump(result, f)
        f.close()
    except FileNotFoundError:
        print("FileNotFoundError")


def get_snap(time_point, time_length=one_year, easy_id=14000):
    query_base = '''select start_id,end_id,weight,timestamp from relationship
    where timestamp>=? and timestamp<=?+? and start_id<? order by start_id,timestamp'''

    query_author = '''select r.start_id,a.name from relationship r,author a
    where r.timestamp>=? and r.timestamp<=?+? and start_id<? order by r.start_id,r.timestamp'''

    print("from %d to %d" % (time_point, time_length + time_point))
    linkset = c.execute(query_base, (time_point, time_length, time_point, easy_id,))
    linkres = []
    noderes = []
    for row in linkset:
        linkres.append(row)
    # nodeset = c.execute(query_author, (time_point, time_length, time_point, easy_id,))
    # for row in nodeset:
    #     noderes.append(row)
    return noderes, linkres


def get_snap_count(time_point, time_length=one_year, easy_id=14000):
    query = "select count(*) from relationship where timestamp>=? and timestamp<=?+? and start_id<%d" % (easy_id)
    print("from %d to %d" % (time_point, time_length + time_point))
    resultset = c.execute(query, (time_point, time_length, time_point,))
    a = resultset.fetchone()
    for row in resultset:
        print(row)
    return a[0]


if __name__ == "__main__":
    get_snap_count(dt.datetime.strptime("20000101000000", "%Y%m%d%H%M%S").timestamp())
# test