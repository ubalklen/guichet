import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import PySimpleGUI as sg
from pydantic import SecretStr


class Guichet:
    """Represents an automatically generated Graphical User Interface (GUI).

    This GUI is oriented according to a function. The input controls represent the
    parameters of the function. There is also a button that, once pressed, call the
    function and any outputs are displayed in a text field.
    """

    _TYPE_MAP = {
        int: sg.InputText,
        float: sg.InputText,
        str: sg.InputText,
        bool: sg.Checkbox,
        SecretStr: (sg.InputText, {"password_char": "*"}),
    }

    def __init__(
        self,
        main_function: Callable,
        title: str = None,
        output_size: tuple = (80, 20),
        button_label: str = "Run",
        theme: str = "Dark Blue 3",
        show_default: bool = True,
        ignore_params: list = None,
        redirect_stdout: bool = True,
        run_in_new_thread: bool = False,
        wait_message: str = "Please wait...",
        refresh_time: int = 1000,
        window_param: str = None,
    ):
        """Creates an object of the Guichet class.

        Args:
            main_function (Callable): The function in which the GUI is based on.
            title (str, optional): The window title. Defaults to `None`, which means the
                name of the `main_function` will be used.
            output_size (tuple, optional): The size of the output field, which
                indirectly sets the size of the window. Defaults to `(80, 20)`.
            button_label (str, optional): The label of the button that calls
                `main_function`. Defaults to `"Run"`.
            theme (str, optional): The window theme. You can explore the list of
                available themes following these [instructions][1]. Defaults to
                `"Dark Blue 3"`.
            show_default (bool, optional): Whether to show the default values of the
                parameters in the GUI. Defaults to `True`.
            ignore_params (list, optional): Parameters to be ignored and not shown in
                the GUI. Defaults to `None`.
            redirect_stdout (bool, optional): Whether to redirect the standard output to
                the GUI's output field. If `True`, regular `print` calls in
                `main_function` will write to the output field. Defaults to `True`.
            run_in_new_thread (bool, optional): Whether to run the `main_function` in a
                new thread. This should only be `True` if the `main_function` is slow
                and you want to avoid blocking the GUI. Read the docs as some caveats
                apply when running a function in a separate thread. Defaults to `False`.
            wait_message (str, optional): The message to be shown in the output field.
            when a users presses the running button and the function has not yet
            finished. Applicable only if `run_in_new_thread` is `True`.
            Defaults to `"Please wait..."`.
            refresh_time (int, optional): Time (in milliseconds) for the window to check
                again for new events. Useful only in advanced scenarios where
                `run_in_new_thread` is `True`. Use the highest value you can afford.
                Defaults to `1000`.
            window_param (str, optional): The parameter of the `main_function` to where
                the GUI's main window object will be passed. Needed only in advanced
                scenarios where the `main_function` needs to communicate with the GUI.
                The parameter passed to `window` will not be shown in the GUI. Defaults
                to `None`.

        [1]: https://www.pysimplegui.org/en/latest/cookbook/#themes-window-beautification
        """
        self.main_function = main_function
        self.title = title or main_function.__name__
        self.output_size = output_size
        self.button_label = button_label
        self.theme = theme
        self.show_default = show_default
        self.ignore_params = ignore_params
        self.redirect_stdout = redirect_stdout
        self.run_in_new_thread = run_in_new_thread
        self.wait_message = wait_message
        self.refresh_time = refresh_time
        self.window_param = window_param
        self.layout = self._make_layout()

    @property
    def main_function(self):
        return self._function

    @main_function.setter
    def main_function(self, value):
        if not callable(value):
            raise TypeError("'main_function' must be a callable")

        self._function = value
        self._params = self._get_params()
        self.layout = self._make_layout()

    @property
    def output_size(self):
        try:
            return self._output_size
        except AttributeError:
            return None

    @output_size.setter
    def output_size(self, value):
        self._output_size = value
        self.layout = self._make_layout()

    @property
    def button_label(self):
        try:
            return self._button_label
        except AttributeError:
            return None

    @button_label.setter
    def button_label(self, value):
        self._button_label = value
        self.layout = self._make_layout()

    @property
    def show_default(self):
        try:
            return self._show_default
        except AttributeError:
            return None

    @show_default.setter
    def show_default(self, value):
        self._show_default = value
        self.layout = self._make_layout()

    @property
    def ignore_params(self):
        try:
            return self._ignore_params
        except AttributeError:
            self._ignore_params = []
            return self._ignore_params

    @ignore_params.setter
    def ignore_params(self, value):
        if value is None:
            self._ignore_params = []
        else:
            self._ignore_params = value
        self.layout = self._make_layout()

    @property
    def window_param(self):
        try:
            return self._window_param
        except AttributeError:
            return None

    @window_param.setter
    def window_param(self, value):
        self._window_param = value
        if value not in self.ignore_params:
            self.ignore_params.append(value)
        self.layout = self._make_layout()

    def _get_params(self):
        return [
            p
            for p in inspect.signature(self.main_function).parameters.values()
            if not self.ignore_params or p.name not in self.ignore_params
        ]

    def render(self):
        if self.redirect_stdout:
            self._output.reroute_stdout_to_here()
            self._output.reroute_stderr_to_here()

        sg.theme(self.theme)
        window = sg.Window(self.title, self.layout)

        if self.run_in_new_thread:
            executor = ThreadPoolExecutor()
            future = None

        while True:
            if self.run_in_new_thread:
                if future is not None and future.done():
                    try:
                        window["-OUTPUT-"].update(future.result())
                        future = None
                    except Exception as e:
                        window["-OUTPUT-"].update(f"Error: {e}")

                    continue

            event, values = window.read(timeout=self.refresh_time)

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "-RUN-":
                if self.run_in_new_thread:
                    if future is not None and not future.done():
                        print(self.wait_message)
                        continue

                # Convert args according to parameter annotations
                kwargs = {}
                for p, v in zip(self._get_params(), values.values()):
                    try:
                        kwargs[p.name] = p.annotation(v)
                    except TypeError:
                        kwargs[p.name] = v
                if self.window_param:
                    kwargs[self.window_param] = window

                if self.run_in_new_thread:
                    future = executor.submit(self.main_function, **kwargs)
                else:
                    try:
                        window["-OUTPUT-"].update(self.main_function(**kwargs))
                    except Exception as e:
                        window["-OUTPUT-"].update(f"Error: {e}")

            if event == "-RUN-IN-GUICHET-":
                values["-RUN-IN-GUICHET-"]()

        window.close()
        if self.run_in_new_thread:
            executor.shutdown(wait=False, cancel_futures=True)
        if self.redirect_stdout:
            self._output.restore_stdout()
            self._output.restore_stderr()

    def _make_layout(self):
        layout = []

        # Create the main layout with an appropriate sg element for each parameter
        for p in self._get_params():
            sg_element = Guichet._TYPE_MAP.get(p.annotation, sg.InputText)
            kwargs = {}
            if isinstance(sg_element, tuple):
                sg_element, kwargs = sg_element

            if p.default != inspect._empty and self.show_default:
                layout.append([sg.Text(p.name), sg_element(p.default, **kwargs)])
            else:
                layout.append([sg.Text(p.name), sg_element("", **kwargs)])

        # Add a button to call the function
        layout.append([sg.Button(self.button_label, key="-RUN-")])

        # Add a multi-line text field to display the output of the function
        self._output = sg.Multiline(key="-OUTPUT-", size=self.output_size)
        layout.append([self._output])

        return layout
