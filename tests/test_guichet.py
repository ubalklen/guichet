from guichet import Guichet


def test_simple_function():
    def concat(word_1, word_2):
        return word_1 + word_2

    gui = Guichet(concat)
    assert len(gui.layout) == 4


def test_function_with_int_anottation():
    def f(x: int):
        pass

    gui = Guichet(f)
    assert gui.layout


def test_function_with_float_anottation():
    def f(x: float):
        pass

    gui = Guichet(f)
    assert gui.layout


def test_function_with_str_annotation():
    def f(x: str):
        pass

    gui = Guichet(f)
    assert gui.layout


def test_function_with_bool_annotation():
    def f(x: bool):
        pass

    gui = Guichet(f)
    assert gui.layout


def test_function_with_int_default_value():
    default_value = 3

    def f(x: int = default_value):
        pass

    gui = Guichet(f)
    assert gui.layout[0][1].DefaultText == default_value


def test_function_with_bool_default_value():
    default_value = True

    def f_true(x: bool = default_value):
        pass

    gui = Guichet(f_true)
    assert gui.layout[0][1].Text is default_value

    def f_false(x: bool = not default_value):
        pass

    gui.main_function = f_false
    assert gui.layout[0][1].Text is not default_value


def test_function_with_ignored_parameter():
    def f(x: int, ignored=None):
        pass

    gui = Guichet(f, ignore_params=["ignored"])
    assert len(gui.layout) == 3


def test_simple_lambda():
    gui = Guichet(lambda x: x)
    assert len(gui.layout) == 3


def test_rendering_with_annotations():
    def happy_text(text: str, feeling_happy: bool):
        if feeling_happy:
            return text + "!!!"
        else:
            return text

    gui = Guichet(happy_text)
    gui.render()


def test_rendering_without_annotations():
    def concat(text1, text2):
        return text1 + text2

    gui = Guichet(concat)
    gui.render()


def test_rendering_with_simple_lambda():
    gui = Guichet(lambda x: x)
    gui.render()


def test_print():
    def hello_world():
        print("Hello world!")

    gui = Guichet(hello_world)
    gui.render()
