from unittest import SkipTest
import matplotlib.pyplot as plt

from ..element.comparison import ComparisonTestCase
from ..styles import set_style
from . import magics
from .magics import ViewMagic, load_magics
from .display_hooks import animate, set_display_hooks
from .parser import Parser

from param import ipython as param_ext

try:    from matplotlib import animation
except: animation = None

all_line_magics = sorted(['%params', '%opts', '%view', '%compositor'])
all_cell_magics = sorted(['%%view', '%%opts', '%%labels'])
message = """Welcome to the HoloViews IPython extension! (http://ioam.github.io/holoviews/)"""
message += '\nAvailable magics: %s' % ', '.join(sorted(all_line_magics)
                                                + sorted(all_cell_magics))


def supported_formats(optional_formats):
    "Optional formats that are actually supported"
    supported = []
    for fmt in optional_formats:
        try:
            anim = animation.FuncAnimation(plt.figure(),
                                           lambda x: x, frames=[0,1])
            animate(anim, 72, *ViewMagic.ANIMATION_OPTS[fmt])
            supported.append(fmt)
        except: pass
    return supported


def update_matplotlib_rc():
    """
    Default changes to the matplotlib rc used by IPython Notebook.
    """
    import matplotlib
    rc= {'figure.figsize': (6.0,4.0),
         'figure.facecolor': 'white',
         'figure.edgecolor': 'white',
         'font.size': 10,
         'savefig.dpi': 72,
         'figure.subplot.bottom' : .125
         }
    matplotlib.rcParams.update(rc)



class IPTestCase(ComparisonTestCase):
    """
    This class extends ComparisonTestCase to handle IPython specific
    objects and support the execution of cells and magic.
    """

    def setUp(self):
        super(IPTestCase, self).setUp()
        try:
            import IPython
            from IPython.display import HTML, SVG
            self.ip = IPython.InteractiveShell()
            if self.ip is None:
                raise TypeError()
        except Exception:
                raise SkipTest("IPython could not be started")

        self.addTypeEqualityFunc(HTML, self.skip_comparison)
        self.addTypeEqualityFunc(SVG,  self.skip_comparison)

    def skip_comparison(self, obj1, obj2, msg):
        pass

    def get_object(self, name):
        obj = self.ip._object_find(name).obj
        if obj is None:
            raise self.failureException("Could not find object %s" % name)
        return obj


    def cell(self, line):
        "Run an IPython cell"
        self.ip.run_cell(line, silent=True)

    def cell_magic(self, *args, **kwargs):
        "Run an IPython cell magic"
        self.ip.run_cell_magic(*args, **kwargs)


    def line_magic(self, *args, **kwargs):
        "Run an IPython line magic"
        self.ip.run_line_magic(*args, **kwargs)



# Populating the namespace for keyword evaluation
from ..core.options import Cycle         # pyflakes:ignore (namespace import)
import numpy as np                       # pyflakes:ignore (namespace import)

Parser.namespace = {'np':np, 'Cycle':Cycle}

_loaded = False
def load_ipython_extension(ip, verbose=True):

    if verbose: print(message)

    global _loaded
    if not _loaded:
        _loaded = True

        param_ext.load_ipython_extension(ip, verbose=False)

        load_magics(ip)
        valid_formats = supported_formats(ViewMagic.optional_formats)
        ViewMagic.register_supported_formats(valid_formats)
        set_display_hooks(ip)
        update_matplotlib_rc()
        set_style('default')

def unload_ipython_extension(ip):
    global _loaded
    _loaded = False
