# Guichet
Quickly create simple GUIs in Python.

```python
def happy_text(text: str, feeling_happy: bool):
    if feeling_happy:
        return text + "!!!"
    else:
        return text

gui = Guichet(happy_text)
gui.render()
```
The code above renders the following GUI:

![Alt text](assets/image.png)

You can also customize the layout by accessing the `layout` attribute of the `Guichet` object.

Guichet is based on the awesome [PySimpleGUI](https://www.pysimplegui.org/) library.