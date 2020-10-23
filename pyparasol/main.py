import gzip
from argparse import ArgumentParser
from pathlib import Path

from flask import Flask, make_response

from pyparasol.html_rendering import PyParasol, ParasolPlot


def send_compressed(content):
    content = gzip.compress(content.encode('utf8'), compresslevel=5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


def run_server(parasol: PyParasol, debug=False, host="localhost", port=5000, background=False):
    if background:
        from multiprocessing import Process
        proc = Process(target=run_server, kwargs=dict(parasol=parasol, debug=debug, host=host,
                                                      port=port, background=False))
        proc.daemon = True
        proc.start()
        return proc
    else:
        app = Flask(parasol.page_title)
        app.route("/")(lambda: send_compressed(parasol.compile()))
        app.jinja_env.auto_reload = False
        app.run(debug=debug, host=host, port=port)


def main(csv_file_paths=None, n_clusters: int = None, title=None, port=5000, host="localhost"):
    if type(csv_file_paths) is str:
        csv_file_paths = [csv_file_paths]

    if csv_file_paths is None:  # if not given as parameter, read from command line arguments
        parser = ArgumentParser(description="Commandline interface for exploring hyper-parameter "
                                            "configurations stored as .csv")

        parser.add_argument("csv_file", nargs="+", help="path to csv file (one or more)")
        parser.add_argument("--clusters", type=int, default=None,
                            help="The number of clusters to use for k-means clustering")
        parser.add_argument("--port", type=int, default=port, help="the port to use for the web server")
        parser.add_argument("--host", type=str, default=host, help="the hostname or ip to use for the web server")

        args = parser.parse_args()
        csv_file_paths = args.csv_file
        n_clusters = args.clusters
        port = args.port
        host = args.host

    parasol = PyParasol(plots=[ParasolPlot(file, title=Path(file).stem) for file in csv_file_paths],
                        page_title=title)

    if title is None and len(csv_file_paths) == 1:
        parasol.page_title = Path(csv_file_paths[0]).stem

    if n_clusters:
        parasol.set_color_cluster(True, number_colors=n_clusters)

    run_server(parasol=parasol, debug=False, host=host, port=port)


if __name__ == "__main__":
    main()
