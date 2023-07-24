import PySimpleGUI as sg
import pytest

from guichet import Guichet


# Elements in PySimpleGUI need to be in a window to be tested
# See https://github.com/PySimpleGUI/PySimpleGUI/issues/6450
def rendered_element(element):
    layout = [[element]]
    sg.Window("Test", layout, finalize=True)
    return element


class TestGuichet:
    def test_simple_function(self):
        def concat(word_1, word_2):
            return word_1 + word_2

        gui = Guichet(concat)
        assert len(gui.layout) == 4

        word_1_element = rendered_element(gui.layout[0][0])
        assert isinstance(word_1_element, sg.Text)
        assert word_1_element.get() == "word_1"

        word_2_element = rendered_element(gui.layout[1][0])
        assert isinstance(word_2_element, sg.Text)
        assert word_2_element.get() == "word_2"

        assert isinstance(gui.layout[0][1], sg.InputText)
        assert isinstance(gui.layout[1][1], sg.InputText)
        assert isinstance(gui.layout[2][0], sg.Button)
        assert isinstance(gui.layout[3][0], sg.Multiline)

    def test_function_with_int_annotation(self):
        def f(x: int):
            pass

        gui = Guichet(f)
        assert isinstance(gui.layout[0][1], sg.InputText)

    def test_function_with_float_annotation(self):
        def f(x: float):
            pass

        gui = Guichet(f)
        assert isinstance(gui.layout[0][1], sg.InputText)

    def test_function_with_str_annotation(self):
        def f(x: str):
            pass

        gui = Guichet(f)
        assert isinstance(gui.layout[0][1], sg.InputText)

    def test_function_with_bool_annotation(self):
        def f(x: bool):
            pass

        gui = Guichet(f)
        assert isinstance(gui.layout[0][1], sg.Checkbox)

    def test_function_with_int_default_value(self):
        default_value = 3

        def f(x: int = default_value):
            pass

        gui = Guichet(f)
        assert gui.layout[0][1].DefaultText == default_value

    def test_function_with_bool_default_value(self):
        default_value = True

        def f_true(x: bool = default_value):
            pass

        gui = Guichet(f_true)
        assert gui.layout[0][1].Text is default_value

        def f_false(x: bool = not default_value):
            pass

        gui.main_function = f_false
        assert gui.layout[0][1].Text is not default_value

    def test_function_with_ignored_parameter(self):
        def f(x: int, ignored=None):
            pass

        gui = Guichet(f, ignore_params=["ignored"])
        assert len(gui.layout) == 3

    def test_simple_lambda(self):
        gui = Guichet(lambda x: x)
        assert len(gui.layout) == 3

    def test_button_label(self):
        def f(x):
            pass

        gui1 = Guichet(f)
        assert gui1.layout[1][0].get_text() == "Run"

        gui2 = Guichet(f, button_label="Go")
        assert gui2.layout[1][0].get_text() == "Go"
        gui2.button_label = "Execute"
        assert gui2.layout[1][0].get_text() == "Execute"

    def test_theme(self):
        def f(x):
            pass

        gui1 = Guichet(f)
        assert gui1.theme == "Dark Blue 3"

        gui2 = Guichet(f, theme="DarkAmber")
        assert gui2.theme == "DarkAmber"
        gui2.theme = "DarkPurple"
        assert gui2.theme == "DarkPurple"

    def test_show_default(self):
        def f(x="foo"):
            pass

        gui1 = Guichet(f)
        assert gui1.layout[0][1].DefaultText == "foo"

        gui2 = Guichet(f, show_default=False)
        assert gui2.layout[0][1].DefaultText == ""
        gui2.show_default = True
        assert gui2.layout[0][1].DefaultText == "foo"

        def f2(x):
            pass

        gui3 = Guichet(f2)
        assert gui3.layout[0][1].DefaultText == ""

    @pytest.mark.skip(reason="Doesn't work. Don't know why.")
    def test_output_size(self):
        def f(x):
            pass

        gui1 = Guichet(f)
        output_element = rendered_element(gui1.layout[2][0])
        assert output_element.get_size() == (80, 20)

        gui2 = Guichet(f, output_size=(100, 40))
        assert gui2.layout[2][0].get_size() == (100, 40)
        gui2.output_size = (120, 60)
        assert gui2.layout[2][0].get_size() == (120, 60)


class TestRendering:
    def test_rendering_with_annotations(self):
        def happy_text(text: str, feeling_happy: bool):
            if feeling_happy:
                return text + "!!!"
            else:
                return text

        gui = Guichet(happy_text)
        gui.render()

    def test_rendering_without_annotations(self):
        def concat(text1, text2):
            return text1 + text2

        gui = Guichet(concat)
        gui.render()

    def test_rendering_with_simple_lambda(self):
        gui = Guichet(lambda x: x)
        gui.render()

    def test_print_one(self):
        def hello_world():
            print("Hello world!")

        gui = Guichet(hello_world)
        gui.render()

    def test_print_many(self):
        def print_many():
            for i in range(1000):
                print(i)

        gui = Guichet(print_many)
        gui.render()

    def test_rendering_slow_function(self):
        import time

        def slow_function():
            print(f"Running slow function at {time.time()}...")
            time.sleep(5)
            print("Done!")

        gui = Guichet(slow_function)
        gui.render()

    def test_rendering_slow_function_in_new_thread(self):
        import time

        def slow_function():
            print(f"Running slow function at {time.time()}...")
            time.sleep(5)
            print("Done!")

        gui = Guichet(slow_function, run_in_new_thread=True)
        gui.render()

    def test_progress_bar(self):
        def counter(win: sg.Window):
            n = 100
            for i in range(n):

                def progress_bar(
                    title="Progress bar", current_value=i + 1, max_value=n
                ):
                    return sg.one_line_progress_meter(title, current_value, max_value)

                win.write_event_value("-RUN-IN-GUICHET-", progress_bar)

        gui = Guichet(counter, window_param="win")
        gui.render()

    def test_theme(self):
        def hello_world():
            print("Hello world!")

        gui = Guichet(hello_world, theme="DarkAmber")
        gui.render()

    def test_output_size(self):
        def hello_world():
            print("Hello world!")

        gui = Guichet(hello_world, output_size=(30, 10))
        gui.render()
