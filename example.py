import os
from pyparasol.html_rendering import PyParasol, ParasolPlot
from pyparasol.main import run_server, main


def very_simple_example():
    data_folder = os.path.dirname(__file__) + "/data"
    parasol = main(csv_file_paths=[f"{data_folder}/lrgv.csv"], n_clusters=3,
                   title="Very Simple Example")


def complex_example():
    plots = []
    data_views = dict(
        Objectives=['rel. (-)', 'crit. rel. (-)', 'leases (#)', 'surplus (af)', 'cost ($)', 'dropped (af)',
                    'cost var. (-)', 'dr. trans. ($)'],
        Decisions=['rights (af)', 'opt. low (af)', 'opt. high (af)', 'xi (-)', 'alpha 1-4 (-)', 'beta 1-4 (-)',
                   'alpha 5-12 (-)', 'beta 5-12 (-)', 'cost ($)', 'dropped (af)', 'cost var. (-)', 'dr. trans. ($)']
    )
    for name, axes_entries in data_views.items():
        plot = ParasolPlot(data="data/lrgv.csv", title=name,
                           axes_layout=axes_entries)
        plots.append(plot)

    parasol = PyParasol(plots, link_plots_status=True, page_title="LRGV Analysis", tab_title="LRGV Analysis")

    parasol.add_reset_brushed_button()
    parasol.add_export_brushed_button()
    parasol.add_export_marked_button()
    parasol.add_remove_selected_button()
    parasol.add_export_all_button()

    parasol.set_color_cluster(True, number_colors=3, plot_ids=None)
    parasol.set_plot_alpha(.65, plot_ids=None)

    run_server(parasol, host="localhost", port=5001, background=True)


if __name__ == "__main__":
    import time
    import sys

    print("Starting complex example in a background process\n")
    complex_example()
    time.sleep(2)

    print("\nStarting simple example in the main process\n")

    sys.stderr.flush()
    sys.stdout.flush()

    very_simple_example()
