import sqlite3, pickle
import datetime as dt
import pytz
import os

base_dir = "/home/liwang/STUDY/Y1Q3/de/coauthor/dblp_coauthor/"
project_dir = "/home/liwang/PycharmProjects/dm_project/"
conn = sqlite3.connect(base_dir + "sqlite3.db")
c = conn.cursor()
'''
        create table relationship(START_ID integer,END_ID integer,weight integer,timestamp integer);
        create table author(authorId integer,name text);
        create table timetable(START_ID integer,END_ID integer, weight integer, starttime integer,endtime integer,timelength integer);
'''
# we approximately use 365 as the number of days in one year
one_year = 60 * 60 * 24 * 365
one_month = 60 * 60 * 24 * 30
min_time = -1009843139;
max_time = 1388534461;
min_dt = dt.datetime.fromtimestamp(min_time)
max_dt = dt.datetime.fromtimestamp(max_time)


def dump_relationship_dist(min=min_dt, max=max_dt):
    t0 = min
    t1 = 0
    i = 0
    result = []
    while t0 < max:
        t1 = t0.replace(day=t0.day + 1)
        t = (dt.datetime.timestamp(t0), dt.datetime.timestamp(t1),)
        resultset = c.execute("select count(*) from relationship where timestamp>=? and timestamp<?", t)
        print("from %s to %s" % (t0.strftime('%Y-%m-%d %H:%M:%S'),
                                 t1.strftime('%Y-%m-%d %H:%M:%S')))

        for row in resultset:
            result.append((t0, row[0]))
            print(row[0])

        t0 = t1
        i += 1
    try:
        f = open("/home/liwang/PycharmProjects/dm_project/coauthordist", "wb")
        pickle.dump(result, f)
        f.close()
    except FileNotFoundError:
        print("FileNotFoundError")


def get_snap(timestart, timeend, sid=0, eid=100):
    query_base = '''select start_id,end_id,weight,timestamp from relationship
    where timestamp>=? and timestamp<=? and start_id>=? and start_id<=? and end_id>=? and end_id<=? order by start_id,timestamp'''

    query_author = '''select r.start_id,a.name from relationship r,author a
    where a.authorid=r.start_id and
    r.timestamp>=?-? and r.timestamp<=? and start_id>=? and start_id<=? order by r.start_id,r.timestamp'''

    linkset = c.execute(query_base, (timestart, timeend, sid, eid, sid, eid,))
    linkres = []
    noderes = []
    for row in linkset:
        linkres.append(row)
    # nodeset = c.execute(query_author, (time_point, time_length, time_point, sid, eid,))
    # for row in nodeset:
    #     noderes.append(row)
    return noderes, linkres


def get_distribution():
    query = "select count(*),timestamp from relationship group by timestamp order by timestamp"
    rs = c.execute(query)
    result = []
    for row in rs:
        result.append(row)
    return result


def tupleList2csv(list, csvheader):
    return "\n".join([",".join(csvheader),
                      "\n".join([",".join([str(x) for x in row]) for row in list])
                      ])


def year2timestamp(year):
    '''the timestamp at which papers are published are all 61 seconds after 01/01/year @ 12:00am (UTC)
    we use year parameter to generate the timestamp
    '''
    return dt.datetime(int(year), 1, 1, 0, 1, 1, 0, pytz.UTC).timestamp()


def get_distribution_from_file():
    try:
        f = open("%sdistribution" % project_dir, "rb")
        return pickle.load(f)
    except FileNotFoundError:
        print("FileNotFoundError")
        result = get_distribution()
        os.mknod("%sdistribution" % project_dir)
        f1 = open("%sdistribution" % project_dir, "wb")
        pickle.dump(result, f1)
        f1.close()
        return result


if __name__ == "__main__":
    re = get_distribution_from_file()
    print(re)