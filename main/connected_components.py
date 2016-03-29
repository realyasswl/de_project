# load data  infile '/tmp/rd/out.dblp_coauthor' into table edges  fields terminated by ' '  enclosed by '"'  lines terminated by '\n' ignore 1 lines  (`in`,`out`,@weight,`timestamp`);
import MySQLdb
from pprint import pprint
db=MySQLdb.connect(user="root",passwd="678922e03",db="dataeng")

def components():
    c=db.cursor()
    c.execute("select `id` from authors order by rand()")
    nodes = set([item[0] for item in c.fetchall()])
    c.execute("SET GLOBAL general_log = 'OFF';")
    cnum = 0;

    # Loop until all the nodes have been processed
    while len(nodes) > 0:
        node = nodes.pop()
        component = {node}
        format_strings = ','.join(['%s'] * len(component))
        try:
            c.execute("select `out` from edges2 where `in` in (%s)" % format_strings + " and `out` not in (%s)" % format_strings, tuple(2 * list(component)))
            #c.execute("select `out` from edges2 where FIND_IN_SET(`in`,@list) > 0 and FIND_IN_SET(`out`,@list) < 1")
        except:
            print(c._last_executed)
            raise
        bfs = {item[0] for item in c.fetchall()}

        # Loop until there are no more new edges in this component
        while len(bfs) > 0:
            component |= bfs
            format_strings = ','.join(['%s'] * len(component))
            try:
                #c.execute("set @list = '%s'" % format_strings, tuple(component))
                c.execute("select `out` from edges2 where `in` in (%s)" % format_strings + " and `out` not in (%s)" % format_strings, tuple(2 * list(component)))
            except:
                print(c._last_executed)
                raise
            bfs = {item[0] for item in c.fetchall()}

        nodes -= component

        # Save the component number to all the edges
        format_strings = ','.join(['%s'] * len(component))
        c.execute("SET GLOBAL general_log = 'ON';")
        c.execute("update edges2 set `component` = '" + str(cnum) + "' where `in` in (%s)" % format_strings, tuple(component))
        c.execute("SET GLOBAL general_log = 'OFF';")
        db.commit()
        #fcomponent = frozenset(component)
        #cs.add(fcomponent)
        print(str(len(component)))
        cnum += 1
    c.close()

components()
db.close()