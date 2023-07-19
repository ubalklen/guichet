import inspect

import PySimpleGUI as sg


class Guichet:
    """Represents an automatically generated Graphical User Interface (GUI).

    This GUI is oriented according to a function. The input controls represent the
    parameters of the function. There is also a button that, once pressed, call the
    function and any outputs are diplayed in a text field.
    """

    _TYPE_MAP = {
        int: sg.InputText,
        float: sg.InputText,
        str: sg.InputText,
        bool: sg.Checkbox,
    }

    def __init__(
        self,
        main_function,
        ignore_params: list = None,
        show_default: bool = True,
        title=None,
        theme: str = None,
        output_size=(80, 20),
    ):
        """Creates an object of the Guichet class.

        Args:
            main_function (_type_): the function in which the GUI is based.
            ignore_params (list, optional): parameters to be ignored and not shown in
                the GUI.
            show_default (bool, optional): whether to show the default value of the
                parameters in the GUI.
            title (str, optional): the window title.
            theme (str, optional): _description_.
        """
        self.main_function = main_function
        self.output_size = output_size
        self.ignore_params = ignore_params or []
        self.title = title or main_function.__name__
        self.layout = self._make_layout(output_size=self.output_size)

    @property
    def main_function(self):
        return self._function

    @main_function.setter
    def main_function(self, value):
        if not callable(value):
            raise TypeError("'main_function' must be a callable")

        self._function = value
        self._params = self._get_params()
        self.layout = self._make_layout(output_size=self.output_size)

    @property
    def ignore_params(self):
        return self._ignore_params

    @ignore_params.setter
    def ignore_params(self, value):
        self._ignore_params = value
        self._params = self._get_params()
        self.layout = self._make_layout(output_size=self.output_size)

    @property
    def output_size(self):
        try:
            return self._output_size
        except AttributeError:
            return None

    @output_size.setter
    def output_size(self, value):
        self._output_size = value
        self.layout = self._make_layout(output_size=value)

    def _get_params(self):
        try:
            self.ignore_params
        except AttributeError:
            self.ignore_params = []

        return [
            p
            for p in inspect.signature(self.main_function).parameters.values()
            if p.name not in self.ignore_params
        ]

    def render(self):
        self._output.reroute_stdout_to_here()
        self._output.reroute_stderr_to_here()
        window = sg.Window(self.title, self.layout)

        while True:
            event, values = window.read()

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "run":
                args = []

                # Convert args according to parameter annotations
                for p, v in zip(self._params, values.values()):
                    try:
                        args.append(p.annotation(v))
                    except ValueError:
                        args.append(v)

                # Call the function
                try:
                    window["output"].update(self.main_function(*args))
                except Exception as e:
                    window["output"].update(f"Error: {e}")

        window.close()
        self._output.restore_stdout()
        self._output.restore_stderr()

    def _make_layout(self, output_size):
        layout = []

        # Create the main layout with an appropriate sg element for each parameter
        for p in self._params:
            sg_element = Guichet._TYPE_MAP.get(p.annotation, sg.InputText)
            default_value = p.default if p.default != inspect._empty else None
            layout.append([sg.Text(p.name), sg_element(default_value, key=p.name)])

        # Add a button to call the function
        layout.append([sg.Button("Run", key="run")])

        # Add a multi-line text field to display the output of the function
        self._output = sg.Multiline(key="output", size=output_size)
        layout.append([self._output])

        return layout
