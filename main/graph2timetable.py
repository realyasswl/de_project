from neo4jrestclient.client import GraphDatabase
import datetime, math

# we assume each author spends 1 year on one paper
fixedLength = 12 * 30  # days
url = "http://localhost:7474/db/data"
gdb = GraphDatabase(url, username="neo4j", password="0okmNHY^")

# we know this before hand
record_count = 37973236

split = 100

# We cannot return all the records in one query, it will
# cause outofmemory exception, the option left is to do some kind of narrow time window query multiple times, but there
# will be performance issue, I believe one query scans the whole database despite the query condition
start_time = datetime.datetime.now()
query = "match(n:Author)-[r]-(n1:Author)return r order by n.authorId, r.timestamp limit " + str(
    math.ceil(record_count / split))
result = gdb.query(q=query)
print(datetime.datetime.now() - start_time)
print(result)
print(result[0])
