import sys
import json
from typing import Dict, List, Union, Any, Tuple

try:
    import pandas
    pandas_available = True
except ImportError:
    print("unable to import pandas, loading data from csv will not be possible", file=sys.stderr)
    pandas = None
    pandas_available = False

# PyParasol
# For more information on PyParasol and for a full API, refer to https://github.com/ParasolJS/pyparasol


# this class contains all the options for a single plot, and a method for writing all the plot specific attributes.
# instances of this class should not be made by the user, as there is no use for them except when called from
#   the PyParasol class.
# information about plot attributes can be found at https://github.com/ParasolJS/parasol-es/wiki/API-Reference


def __validate_color__(color_variable):
    if color_variable is None:
        return None
    if type(color_variable) is not str:
        print("hex code not valid, setting to default")
        return None
    # validating hex code is a six character string
    if color_variable[0] == "#":
        color_variable = color_variable[1:]
    if len(color_variable) != 6:
        print("hex code not valid, setting to default")
        return None
    color_variable = '#' + color_variable
    return color_variable


def is_valid_alpha(alpha):
    if alpha is None:
        return None
    try:
        float(alpha)
    except ValueError:
        raise ValueError(f"invalid alpha value {alpha}")
    if alpha < 0 or alpha > 1:
        raise ValueError(f"invalid alpha value {alpha}")
    return alpha


class ParasolPlot:
    num_plots = 0

    def __init__(self, data, columns=None, plot_id=None, title=None, axes_layout=None, columns_to_hide=None,
                 plot_color=None, alpha=None, alpha_on_brush=None, color_on_brush=None, reorderable=True,
                 axes_to_flip=None, column_values_to_select: Dict[str, Any] = None,
                 column_values_to_exclude: Dict[str, Any] = None,
                 variable_scales: Dict[str, Tuple[float, float]] = None):
        # only plot data information gets set to defaults
        # styling attributes remain None unless changed
        self.data = data
        self.columns = columns
        if pandas_available:
            df: pandas.DataFrame = None
        else:
            df = None
        if type(data) is str:
            if data.endswith(".csv"):
                df = pandas.read_csv(data)
            else:
                raise RuntimeError("Invalid value given for data: " + data)
        elif pandas_available and isinstance(data, pandas.DataFrame):
            df = data
        if df is not None:
            self.data = list(df.values.tolist())
            self.columns = list(df.columns)

        self.set_column_values_to_select(column_values_to_select or {})
        self.set_column_values_to_exclude(column_values_to_exclude or {})

        self.plot_id = str(plot_id or self.__class__.num_plots)
        self.__class__.num_plots += 1
        self.plot_title = title or ""
        self.axes_layout = axes_layout or []
        self.columns_to_hide = columns_to_hide or []
        self.variable_scales = variable_scales or {}
        self.variables_to_flip_list = axes_to_flip or []

        # styling attributes
        self.alpha = is_valid_alpha(alpha) if alpha else None
        self.color = __validate_color__(plot_color) if plot_color else None
        self.alpha_on_brush = is_valid_alpha(alpha_on_brush) if alpha_on_brush else None
        self.color_on_brush = __validate_color__(color_on_brush) if color_on_brush else None
        self.reorderable = reorderable

    def add_columns_to_hide(self, column_names: List[str]):
        self.columns_to_hide.extend(column_names)

    def apply_data_filter(self, column_values_to_filter, exclude=False):

        def matches_selection(row_entry, values_to_select):
            if type(values_to_select) in (tuple, list):
                return row_entry in values_to_select
            elif values_to_select is not None:
                return row_entry == values_to_select
            else:
                return exclude  # default action should be the same as exclude parameter

        for column_name, selection in column_values_to_filter.items():
            assert column_name in self.columns, f"invalid column {column_name} supplied, must be one of {self.columns}"
            data_idx = self.columns.index(column_name)
            if exclude:
                self.data = [row for row in self.data if not matches_selection(row[data_idx], selection)]
            else:
                self.data = [row for row in self.data if matches_selection(row[data_idx], selection)]

    def set_column_values_to_exclude(self, column_values_to_exclude: Dict[str, Any]):
        return self.apply_data_filter(column_values_to_filter=column_values_to_exclude, exclude=True)

    def set_column_values_to_select(self, column_values_to_select: Dict[str, Any]):
        return self.apply_data_filter(column_values_to_filter=column_values_to_select, exclude=False)

    # this function writes all the attributes specific to the plot.
    # plot id number is which 
    def write_self_attributes(self, plot_id_number):
        final_html_lines = "\nps.charts[" + str(plot_id_number) + "]"

        # if there is a color set for that plot, adds the color attribute
        if self.color is not None:
            final_html_lines += ".color('" + self.color + "')"

        # if there is an alpha set for that plot, adds the alpha attribute
        if self.alpha:
            final_html_lines += ".alpha(" + str(self.alpha) + ")"

        # if reorderable is true, adds reorderable keyword
        if self.reorderable:
            final_html_lines += ".reorderable()"

        # if brushed color was set, adds attribute
        if self.color_on_brush:
            final_html_lines += ".brushedColor('" + self.color_on_brush + "')"

        # if alpha on brushed was set, adds attribute
        if self.alpha_on_brush:
            final_html_lines += ".alphaOnBrushed(" + str(
                self.alpha_on_brush) + ")"

        if self.variable_scales:
            for variable, scale in self.variable_scales.items():
                if variable not in self.columns_to_hide:
                    final_html_lines += ".scale('" + str(variable) + "', " + str(list(scale)) + ")"

        if self.variables_to_flip_list:
            final_html_lines += ".flipAxes(" + str(self.variables_to_flip_list) + ")"

        final_html_lines += ";"
        return final_html_lines


class PyParasol:
    """ contains all attributes for a parasol plot as well as all methods for writing a parasol html file
         all class variables and functions with __ in front of them are intended to not be used by the user """
    def __init__(self, plots: List[ParasolPlot] = None, page_title="", tab_title="PyParasol", show_table=True,
                 link_plots_status=True, curve_smoothness=6., variable_weights: Dict[str, float] = None):
        # general attributes
        self.show_table = show_table
        self.__html_file_name = None
        # linking plots data
        self.__link_plots = None
        self.__linked_plots_list = None
        # color clustering data
        self.__number_of_cluster_colors = None
        self.__plots_to_cluster_list = None
        self.__variables_to_cluster = None
        # weighted sums variables
        self.__weighted_variable_list = list(variable_weights.keys()) if variable_weights is not None else None
        self.__weighted_weight_list = list(variable_weights.values()) if variable_weights is not None else None
        self.__weighted_plots_to_add_weights = None
        self.curve_smoothness = curve_smoothness

        # list of individual parasol plots
        self.plots = plots or []
        # in the form of variable names and text data for button
        self.__button_variable_names = []
        self.__button_text_names = []
        self.__cluster_status = False
        self.page_title = page_title
        self.page_tab_title = tab_title
        self.set_linked_status(link_plots_status)

    def add_plot(self, parasol_plot: ParasolPlot):
        self.plots.append(parasol_plot)

    def set_reorderable_status(self, reorder_status, plot_id_list=None):
        """ determines whether or not the plots will be reorderable. """
        if type(reorder_status) is not bool:
            print('Set reorder status to True or False')
            return
        ids_to_change = self.get_plots_indices(plot_id_list)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].reorderable = reorder_status

    def set_plot_alpha(self, plot_alpha: float, plot_ids: List[str] = None):
        """ sets the alpha level of the plots. """
        if not is_valid_alpha(plot_alpha):
            raise ValueError(f"Invalid value for plot_alpha: {plot_alpha}, must be a float in [0, 1]")
        ids_to_change = self.get_plots_indices(plot_ids)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].alpha = plot_alpha

    def set_alpha_on_brushed(self, alpha_on_brushed, plot_id_list=None):
        """ sets the brushed on alpha variable. """
        if not is_valid_alpha(alpha_on_brushed):
            return
        ids_to_change = self.get_plots_indices(plot_id_list)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].alpha_on_brush = alpha_on_brushed

    def set_linked_status(self, linked_status: bool, plot_id_list=None):
        """ specifies whether or not to link the plots together.
            linked plots defaults to yes, so plots are interactive with each other. """
        assert type(linked_status) is bool, 'linked_status must be either True or False'
        if plot_id_list is not None:
            plot_id_list = self.get_plots_indices(plot_id_list)
            if plot_id_list != 0:
                self.__linked_plots_list = plot_id_list
        self.__link_plots = linked_status

    def set_plot_color(self, plot_color, plot_id_list=None):
        """ sets the color of the plot.
             WARNING: setting an overall plot color will override a plot cluster """
        plot_color = __validate_color__(plot_color)
        if plot_color == 0:
            return
        ids_to_change = self.get_plots_indices(plot_id_list)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].color = plot_color

    def set_brushed_color(self, brushed_color, plot_id_list=None):
        """ this function sets the color when a plot is brushed. """
        brushed_color = __validate_color__(brushed_color)
        if brushed_color == 0:
            return
        ids_to_change = self.get_plots_indices(plot_id_list)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].color_on_brush = brushed_color

    def set_color_cluster(self, cluster_status, variables_to_cluster=None, number_colors=4, plot_ids=None):
        """ sets the color clustering functionality.
            plots to cluster needs to be entered as a list of integers associating plot number.
            if no variables to cluster attribute is added, it will cluster all of them. """
        if type(cluster_status) is not bool:
            print('Set cluster status to True or False')
            return
        try:
            int(number_colors)
            if number_colors < 1:
                raise Exception('invalid number of colors')
        except TypeError:
            print('set number of colors to a valid positive integer')
            return

        # validating variables to cluster if cluster status is true
        if cluster_status and variables_to_cluster is not None:
            variables_to_cluster = self.__validate_data_is_list_or_single__(variables_to_cluster, str)
            if variables_to_cluster == 0:
                raise RuntimeError("set variables to cluster to a valid list of names, or a single name")
        else:
            def is_valid(data_entry):
                return isinstance(data_entry, (int, float)) and data_entry != float("nan")
            variables_to_cluster = [*{c for plot in self.plots for ci, c in enumerate(plot.columns)
                                      if all(is_valid(row[ci]) for plt in self.plots for row in plt.data)}]
        if plot_ids is not None:
            plot_ids = self.get_plots_indices(plot_ids)
            if plot_ids != 0:
                self.__plots_to_cluster_list = plot_ids

        # setting data
        self.__cluster_status = cluster_status
        self.__number_of_cluster_colors = number_colors
        self.__variables_to_cluster = variables_to_cluster

    def assign_weighted_sums(self, variable_list, associated_weights, plot_id_list=None):
        """ assigns weights to certain variables to make a weighted sums variable.
             variable list is a list of the variables that will have a weight associated to them.
             associated weights is the list of weights that correspond the variable list.
        """
        variable_list = self.__validate_data_is_list_or_single__(variable_list, str)
        associated_weights = self.__validate_data_is_list_or_single__(associated_weights, float)
        if variable_list == 0 or associated_weights == 0:
            print("error in variable list or associated weights list")
            return
        if len(variable_list) != len(associated_weights):
            print("variable list and associated weights list are not the same length")
            return
        self.__weighted_variable_list = variable_list
        self.__weighted_weight_list = associated_weights
        if plot_id_list is not None:
            plot_id_list = self.get_plots_indices(plot_id_list)
            if plot_id_list != 0:
                self.__weighted_plots_to_add_weights = plot_id_list

    def set_variable_scale(self, variable_list: Union[str, List[str]], scale_list: Union[str, List[str]],
                           plot_id_list=None):
        """  assigns scales (lower and upper limits for axes) to a variable or list of variables. """
        variable_list = self.__validate_data_is_list_or_single__(variable_list, str)
        # validating that scale_list is a valid scale, or list of scales
        bad_data = False
        try:
            # determining if scale list is a single list or a list of lists
            temp = scale_list[0][0]
            # if scale list is a list of lists, validates every list in it
            for scale in scale_list:
                # if scale isn't a list in the form [min, max]
                if len(scale) != 2:
                    bad_data = True
                scale = self.__validate_data_is_list_or_single__(scale, float)
                if scale == 0:
                    bad_data = True
        except TypeError:
            scale_list = self.__validate_data_is_list_or_single__(scale_list, float)
            if scale_list == 0 or len(scale_list) != 2:
                bad_data = True
            scale_list = [scale_list]

        # if data is bad, exits function
        if bad_data:
            print("variable scale data inputted incorrectly")
            return
        if len(variable_list) != len(scale_list):
            print("variable list and scale list not the same length")
            return

        # changing scales for all entered ids
        ids_to_change = self.get_plots_indices(plot_id_list)
        if ids_to_change != 0:
            for plot_id in ids_to_change:
                self.plots[plot_id].variable_scales += variable_list
                self.plots[plot_id].variables_scale_limit_list += scale_list

    def add_export_brushed_button(self):
        """ sets the optional export brushed data button. """
        self.__button_text_names.append("Export Brushed Data")
        self.__button_variable_names.append("export_brushed")

    def add_export_marked_button(self):
        """ sets the optional export marked data button. """
        self.__button_text_names.append("Export Marked Data")
        self.__button_variable_names.append("export_marked")

    def add_export_all_button(self):
        """ sets the optional export all data button. """
        self.__button_text_names.append("Export All Data")
        self.__button_variable_names.append("export_all")

    def add_reset_brushed_button(self):
        """ sets the optional reset brushed data button. """
        self.__button_text_names.append("Reset Brushed Data")
        self.__button_variable_names.append("reset_brushed")

    def add_reset_marked_button(self):
        """ sets the optional reset brushed data button. """
        self.__button_text_names.append("Reset Marked Data")
        self.__button_variable_names.append("reset_marked")

    def ad_keep_selected_button(self):
        """ sets the optional keep selected data button. """
        self.__button_text_names.append("Keep Selected Data")
        self.__button_variable_names.append("keep_selected")

    def add_remove_selected_button(self):
        """ sets the optional remove selected data button. """
        self.__button_text_names.append("Remove Selected Data")
        self.__button_variable_names.append("remove_selected")

    @staticmethod
    def __validate_data_is_list_or_single__(input_data, data_type):
        """ checks to see if inputted data is a list, or if it's a single piece of data it returns
             the data as the only element inside a list.
             this function also checks to see that all inputted data is of the correct type.
             this function is set up so if a float is entered as the data type, it will validate integers. """
        if type(input_data) == list:
            for data in input_data:
                # validates if data type is float and input data is int
                if data_type == float and type(data) == int:
                    continue
                if type(data) != data_type:
                    return 0
            return input_data
        elif type(input_data) == data_type:
            return [input_data]
        # validates if data type is float and input data is int
        elif data_type == float and type(input_data) == int:
            return [input_data]
        else:
            return 0

    def get_plots_indices(self, id_to_find_list):
        """ returns the plot index of a plot id name
            if the plot id doesn't exist, returns 0
            if the id_to_find_list is None, returns a list of all indices
        """
        if id_to_find_list is None:
            # returns all indices
            id_index_list = list(range(len(self.plots)))
            return id_index_list
        # if just a single data point was entered, turns it into a list
        if type(id_to_find_list) != list:
            id_to_find_list = [id_to_find_list]
        bad_data = False
        id_index_list = []
        for id_to_find in id_to_find_list:
            # validates that all id's inputted are actual ids that have been specified
            try:
                id_to_find = str(id_to_find)
                for plot_number in range(len(self.plots)):
                    if self.plots[plot_number].plot_id == id_to_find:
                        id_index_list.append(plot_number)
            except ValueError:
                bad_data = True
        if bad_data:
            return 0
        else:
            return id_index_list

    def __write_button_initial_line__(self, variable_name, text):
        """ this function writes a line for making a button """
        final_html_line = "\n<button id='" + str(variable_name) + "'>" + str(text) + "</button>"
        return final_html_line

    def __write_button_setup_lines__(self):
        """ this function writes the initial lines for starting the button area """
        if self.__button_variable_names is None or self.__button_text_names is None:
            return ""
        final_html_lines = "\n<div class='widgets'>"
        for button_variable_name, button_text in zip(self.__button_variable_names, self.__button_text_names):
            final_html_lines += self.__write_button_initial_line__(button_variable_name, button_text)

        final_html_lines += "\n</div>"
        return final_html_lines

    def __write_plot_body_lines__(self):
        """ this function writes the html code for making the layout of the plots on the screen """
        # setting up plot id names
        plot_id_list = []
        for index in range(len(self.plots)):
            plot_id_list.append("p" + str(index))

        final_html_lines = ""
        # adding header and data association to each file
        for plot in range(len(self.plots)):
            final_html_lines += "\n<h2>" + self.plots[plot].plot_title + "</h2>"
            final_html_lines += '\n<div id="' + plot_id_list[plot] + \
                                '" class="parcoords" style="height:300px; width:100%;"></div>'
        # adding grid for data at the bottom
        if self.show_table:
            final_html_lines += '\n<div id="grid" style="width:100%;height:700px;" class="slickgrid-container"></div>'
        return final_html_lines

    def __write_setup_settings__(self, include_html_header=True, include_body_tag=True):
        """ this function sets up the titles, imports and styling settings """
        if include_html_header:
            final_html_lines = f"""<!doctype html>\n<head>\n<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">\n
    <title>{self.page_tab_title}</title>
    
    </head>"""
        else:
            final_html_lines = ""

        final_html_lines += f"""
{"<body>" if include_body_tag else ""}
<link rel="stylesheet" type="text/css" href="https://parasoljs.github.io/demo/parasol.css">
<script src="https://parasoljs.github.io/demo/lib/d3.v5.min.js"></script>
<script src="https://parasoljs.github.io/dist/parasol.standalone.js"></script>
<h1>{self.page_title}</h1>
"""
        return final_html_lines

    def __write_start_script__(self, data_keys_values: List[Dict[str, Union[float, int, str]]]):
        """ this function ends the body and starts the script lines """
        final_html_lines = '\n\n'
        data_json = json.dumps(data_keys_values)
        final_html_lines += f"\n<script>data = { data_json };</script>\n"
        final_html_lines += "<script>"
        return final_html_lines

    def __write_function_end__(self):
        """ this function writes the end of a function """
        final_html_lines = ";});\n"
        return final_html_lines

    def __write_script_end_body_end__(self, include_body_tag=True):
        """ this function writes the end of the script section """
        final_html_lines = "\n</script>"
        if include_body_tag:
            final_html_lines += '\n</body>'
        return final_html_lines

    def __write_parasol_variable__(self):
        """ this function writes the parasol variable lines of code """
        final_html_lines = """
var squaredEuclid = function(p, q) {
    let d = 0;
    for (let i = 0; i < p.length; i++) {
        if (isNaN(p[i]) || isNaN(q[i])){
            d += 1000;
        } else {
            d += (p[i] - q[i]) * (p[i] - q[i]);;
        }
    }
    return d;
}
        """

        final_html_lines += "\nps = Parasol(data)('.parcoords')"

        # adds the clustering statements if set to true
        final_html_lines += self.__write_cluster_attribute_line__()

        if self.__weighted_variable_list is not None:
            final_html_lines += self.__write_weighted_sum_line__()

        # always adds the axes to hide line, if there is only one plot it will be an empty set
        # setting hideAxes or setAxesLayout *LAST* will override the other one
        final_html_lines += "\n.hideAxes(axes_to_hide)"
        final_html_lines += f"\n.smoothness({self.curve_smoothness/100.})"

        if self.show_table:
            final_html_lines += "\n.attachGrid({container: '#grid'})"

        # adds linked line if option is set to true
        if self.__link_plots:
            if self.__linked_plots_list:
                final_html_lines += f"\n.linked({'chartIDs=' + str(self.__linked_plots_list)})"
            else:
                final_html_lines += "\n.linked()"

        final_html_lines += "\n.setAxesLayout(axes_layout)"

        final_html_lines += "\n.render()"

        final_html_lines += ";"
        return final_html_lines

    # this function writes all the attributes that are specific to plots
    # variables included: plot color, plot alpha
    def __write_specific_plot_attribute_lines__(self):
        final_html_lines = ""
        # loops through every plot that has been created
        for plot_id_number in self.get_plots_indices(None):
            final_html_lines += self.plots[plot_id_number].write_self_attributes(plot_id_number)
        return final_html_lines

    def __write_weighted_sum_line__(self):
        """ this function writes the .weightedSums line if called """
        final_html_line = "\n.weightedSum({ weights:weights"
        if self.__weighted_plots_to_add_weights is not None:
            final_html_line += ", displayIDs: " + str(self.__weighted_plots_to_add_weights)
        final_html_line += ", norm:false})"

        return final_html_line

    def __write_cluster_attribute_line__(self):
        """this function writes the .cluster line if called"""
        # if status is set to false, returns nothing
        if not self.__cluster_status:
            return ""
        final_html_line = "\n.cluster({k: " + str(self.__number_of_cluster_colors)
        # if there are display ids set, writes them
        if self.__plots_to_cluster_list is not None:
            final_html_line += ", displayIDs: " + str(self.__plots_to_cluster_list)
        # if there are certain variables to cluster set, writes them
        if self.__variables_to_cluster is not None:
            final_html_line += ", vars: " + json.dumps(self.__variables_to_cluster)
        final_html_line += ", options: {distanceFunction: squaredEuclid}})"
        return final_html_line

    def __write_weights_variable__(self):
        """this function writes the weights variables for the weighted sum option"""

        if self.__weighted_weight_list is None or self.__weighted_variable_list is None:
            return ""
        final_html_lines = "\nvar weights = {"
        for weighted_var_number in range(len(self.__weighted_weight_list)):
            final_html_lines += "\n'" + str(self.__weighted_variable_list[weighted_var_number]) + "': " + \
                                str(self.__weighted_weight_list[weighted_var_number]) + ","
        final_html_lines += "\n};"
        return final_html_lines

    def __write_axes_to_hide__(self, headers_per_plot_to_hide):
        """this function writes the axes_to_hide variable to display numerous plots of different data"""

        final_html_lines = "\nvar axes_to_hide = {"
        # for each plot, it adds the headers of every other data set besides itself
        for plot_number, plot in enumerate(self.plots):
            final_html_lines += "\n" + str(plot_number) + ": ["
            final_html_lines += ",".join([f'"{col}"' for col in headers_per_plot_to_hide[plot_number]])
            final_html_lines += ']'
            if plot_number != len(self.plots) - 1:
                final_html_lines += ','
        final_html_lines += "\n};"
        return final_html_lines

    def __write_axes_layout__(self):
        """this function writes the axes layout variable to specify order, which variables to display"""

        final_html_lines = "\nvar axes_layout = {"
        for plot in range(len(self.plots)):
            if self.plots[plot].axes_layout:
                final_html_lines += "\n" + str(plot) + ": "
                final_html_lines += str(self.plots[plot].axes_layout)
                if plot != len(self.plots) - 1:
                    final_html_lines += ","

        final_html_lines += "\n};"
        return final_html_lines

    def __write_button_function__(self, button_variable_name, action_item_line):
        """this function writes a button declaration line"""
        final_html_lines = "\nd3.select('#" + str(button_variable_name) + "').on('click',function() {"
        final_html_lines += str(action_item_line)
        final_html_lines += self.__write_function_end__()
        return final_html_lines

    def __write_button_functions_master__(self):
        """this function is the master function for assigning buttons to their actions"""
        # if there are no buttons, skips
        if self.__button_text_names is None or self.__button_variable_names is None:
            return ""
        final_html_lines = ""
        # loops through all variable names
        for button_variable_name in self.__button_variable_names:
            # gets buttons action and then writes the full button action function
            action = self.__get_button_action__(button_variable_name)
            if action is not None:
                final_html_lines += self.__write_button_function__(button_variable_name, action)

        return final_html_lines

    def __get_button_action__(self, variable_name):
        """this function contains the inventory for assigning button variable names with their actions"""
        # @@@@@@@@ BUTTON ACTION INVENTORY @@@@@@@@@
        if variable_name == "export_brushed":
            action = "\nps.exportData(type='brushed')"
        elif variable_name == "export_marked":
            action = "\nps.exportData(type='marked')"
        elif variable_name == "export_all":
            action = "\nps.exportData({exportAll: true})"
        elif variable_name == "reset_brushed":
            action = "\nps.resetSelections('brushed')"
        elif variable_name == "reset_marked":
            action = "\nps.resetSelections('marked')"
        elif variable_name == "keep_selected":
            action = "\nps.keepData('both')"
        elif variable_name == "remove_selected":
            action = "\nps.removeData('both')"
        else:
            action = None

        return action

    def get_parasol_html(self, headers_per_plot_to_hide, data_keys_values: List[Dict[str, Union[float, int, str]]],
                         include_html_header=True, include_body_tag=True):
        html_final = ""
        html_final += self.__write_setup_settings__(include_html_header=include_html_header,
                                                    include_body_tag=include_body_tag)
        html_final += self.__write_button_setup_lines__()
        html_final += self.__write_plot_body_lines__()
        html_final += self.__write_start_script__(data_keys_values)
        html_final += self.__write_axes_to_hide__(headers_per_plot_to_hide)
        html_final += self.__write_axes_layout__()
        html_final += self.__write_weights_variable__()
        html_final += self.__write_parasol_variable__()
        html_final += self.__write_specific_plot_attribute_lines__()
        html_final += self.__write_button_functions_master__()
        # html_final += self.__write_function_end__()
        html_final += self.__write_script_end_body_end__(include_body_tag=include_body_tag)

        return html_final

    def compile(self, include_html_header=True, include_body_tag=True):
        """ this function compiles the parasol html together with the provided data """
        assert len(self.plots) > 0, "no plots available for compilation"

        data_keys_values = []
        all_headers = {c for plot in self.plots for c in plot.columns}

        for plot in self.plots:
            plot_data = [{k: v for k, v in zip(plot.columns, row)} for row in plot.data]
            plot_data = [{c: row.get(c, -1.0) for c in all_headers} for row in plot_data]  # fill missing as -1
            data_keys_values.extend(plot_data)

        plot_ignore_columns = {i: {c for c in plot.columns_to_hide} for i, plot in enumerate(self.plots)}

        headers_per_plot_to_hide = [[c for c in all_headers if c in plot_ignore_columns[i] or c not in plot.columns]
                                    for i, plot in enumerate(self.plots)]

        return self.get_parasol_html(headers_per_plot_to_hide, data_keys_values,
                                     include_html_header=include_html_header,
                                     include_body_tag=include_body_tag)
