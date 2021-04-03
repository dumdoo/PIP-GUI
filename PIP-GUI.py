import ctypes
import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except AttributeError:
    pass
PYTHON_PATH = sys.executable
PATH = r"c:\users\ro-fi\appdata\local\programs\python\python39\lib\site-packages"


def convert_list_to_dict(list_to_convert: list):
    iterable = iter(list_to_convert)
    resultant_dict = dict(zip(iterable, iterable))
    return resultant_dict


class Package:
    def __init__(self, name: str = None, icon: str = None, link: str = None, path: str = None, version: str = None):
        """A class for each package. `name` is the name of the package. `icon` is a link to the icon. `link` is the
        PyPi page link. `path` is the local path to the dir housing the package"""
        unknown: str = '<unknown>'
        self.name = name if name is not None else unknown
        self.icon = icon if icon is not None else './resources/unknown_icon.png'
        self.link = link if link is not None else unknown
        self.path = path if path is not None else unknown
        self.version = version if version is not None else unknown


def get_package_dist_info(path: str, package_name: str):
    """If a suitable package was found, the returned value would be a `Package` object with the data about the Package
    If it was not, a None-Type object would be returned
    """
    if not path.endswith('/') or not path.endswith('\\'):
        path += '\\'
    for item in os.listdir(path):
        try:
            if os.path.isdir(path + item) and item.split('-', maxsplit=1)[0] == package_name and item.endswith(
                    '.dist-info'):
                # Gets the .dist-info of the package,
                with open(path + item + r'\METADATA', 'rt', encoding='UTF-8') as f:
                    dist_info = f.read()
                    dist_info_dict = convert_list_to_dict(re.split(': |\n', dist_info))  # Separates ': ' and '\n' chars
                    package = Package(name=dist_info_dict['Name'],
                                      link=dist_info_dict['Home-page'], path=path + package_name,
                                      version=dist_info_dict['Version'])
                    return package
        except KeyError:
            return None


def is_package(package_name: str, path: str) -> bool:
    """Checks if the path provided is a package or not.
    Returns a bool

    Args:
        "package" would be the package's name
        "path" is the path to look for it
    """

    path_to_package = path + package_name

    if os.path.isdir(path_to_package) and '__init__.py' in os.listdir(path_to_package) and not path_to_package. \
            endswith('.dist-info'):
        # If the package is a dir, has a file called '__init__.py' inside of it, and does not end with '.dist-info'
        if get_package_dist_info(path=path, package_name=package_name) is not None:
            return True
    else:
        return False


def get_installed_packages(path: str):
    if not path.lower() == os.getcwd().lower() and os.path.isdir(path):  # if the path isn't the current directory and
        # is a directory

        if not path.endswith('\\') or not path.endswith('/'):
            path += '\\'

        contents = os.listdir(path)
        packages = []
        for item in contents:
            if is_package(path=path, package_name=item):
                dist_info = get_package_dist_info(path=path, package_name=item)
                packages.append(dist_info)
        return packages


class GUIApp:
    def __init__(self):
        self.root = tk.Tk()

        self._setupui(self.root)

    def start(self):
        self.root.mainloop()

    def _setupui(self, master):
        self.main_frame = tk.LabelFrame(master=master, text='Installed Packages')

        yscroll = ttk.Scrollbar(master=self.main_frame, orient='vertical')
        listbox = tk.Listbox(master=self.main_frame, yscrollcommand=yscroll.set)
        yscroll.configure(command=listbox.yview)
        yscroll.pack(side='right', fill=tk.Y)

        for i in get_installed_packages(PATH):
            listbox.insert(tk.END, i.name)

        listbox.pack(expand=True, fill=tk.BOTH)
        self.main_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.bottom_frame = tk.LabelFrame(master=master, text="Info")
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)
        self.bottom_text = tk.Text(master=self.bottom_frame)
        self.bottom_text.pack(expand=True, fill=tk.BOTH, side=tk.BOTTOM)
        listbox.bind("<<ListboxSelect>>", self._show_info)

    def _show_info(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.bottom_text.configure(state=tk.NORMAL)
            self.bottom_text.delete(index1='1.0', index2=tk.END)
            info = get_package_dist_info(path=PATH, package_name=data)
            self.bottom_text.insert(tk.END,
                                    f"Name: {info.name}\nVersion: {info.version}\nUrl: {info.link}\nPath to Package: {info.path}")
            self.bottom_text.configure(state=tk.DISABLED)


if __name__ == "__main__":
    m = GUIApp()
    m.start()
