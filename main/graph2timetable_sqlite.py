import sqlite3, pickle
import datetime as dt
import pytz
import os
import numpy as np
import math

base_dir = "."#"/home/liwang/STUDY/Y1Q3/de/coauthor/dblp_coauthor/"
project_dir = "."#"/home/liwang/PycharmProjects/dm_project/"
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
min_dt = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=min_time)
max_dt = dt.datetime.fromtimestamp(max_time)


all_timestamps = {883612861, 915148861, 1136073661, 1199145661, 1293840061, 1356998461, 1325376061, 1072915261, 1167609661, 1230768061, 1104537661, 1388534461, 1009843261, 1262304061, 1041379261, 788918461, 473385661, 694224061, 31536061, 978307261, 852076861, 946684861, 567993661, 631152061, 725846461, 662688061, 599616061, 536457661, 315532861, 157766461, 820454461, 757382461, 441763261, 504921661, 410227261, 378691261, 189302461, 347155261, 283996861, 126230461, -31535939, 61, 94694461, -126230339, 220924861, 252460861, -94694339, -157766339, -189388739, 63072061, -63158339, -252460739, -347155139, -283996739, -220924739, -315619139, -441849539, -378691139, -410227139, -504921539, -473385539, -757382339, -946771139, -568079939, -662687939, -1009843139, -883616339, -725846339, -631151939, -694310339, -599615939, -788918339}
# timestamps = [ts for ts in all_timestamps if min_time <= ts <= max_time]


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
    timestamp>=? and timestamp<=? and start_id>=? and start_id<=? and end_id>=? and end_id<=? order by start_id,timestamp'''

    linkset = c.execute(query_base, (timestart, timeend, sid, eid, sid, eid,))
    linkres = []
    noderes = []
    for row in linkset:
        linkres.append(row)
    nodeset = c.execute(query_author, (timestart, timeend, sid, eid, sid, eid,))
    for row in nodeset:
        noderes.append(row)
    return noderes, linkres


def get_stream(timestart, timeend, sid=0, eid=100):
    query_base = '''select count(*),start_id,timestamp from relationship
    where timestamp>=? and timestamp<=? and start_id>=? and start_id<=? and end_id>=? and end_id<=?
    group by start_id,timestamp order by start_id,timestamp'''
    resultset = c.execute(query_base, (timestart, timeend, sid, eid, sid, eid,))
    result = []
    for row in resultset:
        result.append(row)
    print("%d records" % len(result))
    return result


def temprolGraph2generalGraph(list, reduce=True):
    '''default header = ['source', 'target', 'value', 'ts']'''
    minyear = 0
    maxyear = 0
    nodelist = []
    resultlist = []
    sufnodelist = []
    for l in list:
        source = l[0]
        target = l[1]
        value = l[2]
        ts = l[3]
        year = timestamp2year(ts)
        sourcesuf = "%d.%d" % (source, year)
        resultlist.append([sourcesuf, "%d.%d" % (target, year), value, "coauthor"])
        if source not in nodelist:
            nodelist.append(source)
        if sourcesuf not in sufnodelist:
            sufnodelist.append(sourcesuf)
        maxyear = max(maxyear, year)
        if minyear == 0:
            minyear = year
        else:
            minyear = min(minyear, year)

        if minyear < maxyear:
            if reduce:
                tempnode = ""
                for id in sufnodelist:
                    if tempnode[:-5] == id[:-5]:
                        resultlist.append([tempnode, id, 1, "temporal"])
                    tempnode = id
            else:
                for i in range(minyear, maxyear):
                    for id in nodelist:
                        resultlist.append(["%d.%d" % (id, i), "%d.%d" % (id, i + 1), 1, "temporal"])

    return resultlist


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
    return dt.datetime(year, 1, 1, 0, 1, 1, 0, pytz.UTC).timestamp()


def timestamp2year(timestamp):
    '''in: integer
    '''
    return dt.datetime.fromtimestamp(timestamp).timetuple()[0]


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
    noderes, linkres = get_snap(timestart=year2timestamp(1984),
                                timeend=year2timestamp(1986),
                                sid=0, eid=1000)
    print("\n".join([",".join([str(x) for x in line]) for line in linkres]))

    resultlist = temprolGraph2generalGraph(linkres)
    print("\n".join([",".join([str(x) for x in line]) for line in resultlist]))
