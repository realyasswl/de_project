# load data  infile '/tmp/rd/out.dblp_coauthor' into table edges  fields terminated by ' '  enclosed by '"'  lines terminated by '\n' ignore 1 lines  (`in`,`out`,@weight,`timestamp`);
import MySQLdb
import networkx as nx
db=MySQLdb.connect(user="root",passwd="678922e03",db="dataeng")

def maxdepthcomponent(depth, author_id):
    c=db.cursor()
    # c.execute("select `id` from authors order by rand() limit 1")
    # nodes = set([item[0] for item in c.fetchall()])
    component = []
    bfs = {author_id}
    c.execute("SET GLOBAL general_log = 'OFF';")
    cnum = 0

    min_time = 1230768061 - 5 * 31536000
    max_time = 1230768061 + 5 * 31536000
    # Loop until there are no more new edges in this component
    while len(bfs) > 0 and depth > 0:
        format_strings = ','.join(['%s'] * len(bfs))
        print(len(bfs))
        try:
            # SELECT id, out, timestamp FROM edges2 WHERE `in` IN (S) AND timestamp <= ? and timestamp >= ?

            c.execute("select `id`, `in`, `out`, `timestamp` from edges2 where (`in` in (%s)" % format_strings + " or `out` in (%s)" % format_strings + ") and `timestamp` >= %s and `timestamp` <= %s", tuple(2 * list(bfs) + [min_time, max_time]))
        except:
            print(c._last_executed)
            raise
        result = [item for item in c.fetchall()]
        component += result
        bfs = {item[2] for item in result}
        depth -= 1

    print(len(component))
    c.close()
    return component



# component will contain all the link-edges between nodes in the max-depth induced graph
author_id=705102
component = maxdepthcomponent(depth=3, author_id=author_id)



# nodes will get all the unique node ids
# nodes = {(item[1],item[3]) for item in component} | {(item[2],item[3]) for item in component}
node_ids = {item[1] for item in component} | {item[2] for item in component}

print(len(node_ids))
c=db.cursor()

# get accurate timestamp values
min_time = 1230768061 - 5 * 31536000
max_time = 1230768061 + 5 * 31536000
c.execute("select distinct `timestamp` from edges2 where `timestamp` >= %s and `timestamp` <= %s", tuple([min_time, max_time]))

timestamps = [item[0] for item in c.fetchall()]

print(timestamps)
c.close()

# get temporal nodes

nodes = {(nid, ts) for nid in node_ids for ts in timestamps}

# create directed temporal edges between all the nodes
temporal_edges = {((nid, timestamps[idx]), (nid, timestamps[idx + 1])) for nid in node_ids for idx in range(len(timestamps) - 2)}

# create bi-directional directed edges for all the links
collab_edges = {((item[1],item[3]),(item[2],item[3])) for item in component}

# use graph data structures to run algorithms
G=nx.DiGraph()

G.add_nodes_from(nodes)
G.add_edges_from(temporal_edges)
G.add_edges_from(collab_edges)

bt = nx.betweenness_centrality(G, normalized=False)


# get all the temporal nodes of the author
author_tnodes = {(author_id, ts) for ts in timestamps}

# get the sum of values
author_score = sum({bt[node] for node in author_tnodes})
print(author_score)

#todo hard-code the timestamps query, this is silly

db.close()