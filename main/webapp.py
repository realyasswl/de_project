from flask import Flask, Response, request, jsonify
import main.graph2timetable_sqlite as g2ts

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = Flask(__name__, static_url_path="/static/", static_folder="../web/static")


@app.route("/")
def get_index():
    return app.send_static_file("index.html")


@app.route("/favicon.ico")
def get_favicon():
    return app.send_static_file("favicon.ico")


@app.route("/static/<file>")
def get_static(file):
    return app.send_static_file(file)


@app.route("/search")
def search():
    timestart = request.args["timestart"]
    timeend = request.args["timeend"]
    sid = request.args["sid"]
    eid = request.args["eid"]
    output = request.args["output"]
    reduce = request.args["reduce"]
    print("output %s year from %s to %s, author from %s to %s, reduce:%s" % (
        output, timestart, timeend, sid, eid, reduce))
    if output == "stream":
        stream = g2ts.get_stream(timestart=g2ts.year2timestamp(int(timestart)),
                                 timeend=g2ts.year2timestamp(int(timeend)),
                                 sid=int(sid), eid=int(eid))
        return Response(g2ts.tupleList2csv(stream, csvheader=["count,source,timestamp"]))
    else:
        linkheader = ['source', 'target', 'value', 'type']
        noderes, linkres = g2ts.get_snap(timestart=g2ts.year2timestamp(int(timestart)),
                                         timeend=g2ts.year2timestamp(int(timeend)),
                                         sid=int(sid), eid=int(eid))

        return Response(
            g2ts.tupleList2csv(g2ts.temprolGraph2generalGraph(linkres, reduce=reduce == "true"), csvheader=linkheader))


@app.route("/init")
def init():
    return Response(g2ts.tupleList2csv(g2ts.get_distribution_from_file(), csvheader=["count", "timestamp"]))


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(10000)
    IOLoop.instance().start()
