from ..Qt import QtGui, QtCore
from .Exporter import Exporter
from ..parametertree import group, param
from .. import PlotItem
from .. import functions as fn

__all__ = ['MatplotlibExporter']

"""
It is helpful when using the matplotlib Exporter if your
.matplotlib/matplotlibrc file is configured appropriately.
The following are suggested for getting usable PDF output that
can be edited in Illustrator, etc.

backend      : Qt4Agg
text.usetex : True  # Assumes you have a findable LaTeX installation
interactive : False
font.family : sans-serif
font.sans-serif : 'Arial'  # (make first in list)
mathtext.default : sf
figure.facecolor : white  # personal preference
# next setting allows pdf font to be readable in Adobe Illustrator
pdf.fonttype : 42   # set fonts to TrueType (otherwise it will be 3
                    # and the text will be vectorized.
text.dvipnghack : True  # primarily to clean up font appearance on Mac

The advantage is that there is less to do to get an exported file cleaned and ready for
publication. Fonts are not vectorized (outlined), and window colors are white.

"""

class MatplotlibExporter(Exporter):
    Name = "Matplotlib Window"

    def __init__( self, item ):
        super(MatplotlibExporter, self).__init__( item )
        self.makeParameters( 'params',
            param( 'style file', file,  value='',  filter=['Style File (*.sty)', 'Text File (*.txt)', 'All Files (*.*)'] ),
            param( 'dpi',        int,   value=100, limits=(10,1000) ),
            param( 'size X',     float, value=5.0, limits=(1.0,100.0) ),
            param( 'size Y',     float, value=4.0, limits=(1.0,100.0) ),
            param( 'tight layout', bool, value=True ),
            group( 'marker',
                param( 'edgecolor', 'color', value='k' ),
                param( 'symbol',     str,    value='o' ),
                param( 'size',       int,    value=5, limits=(1,None) ),
                param( 'every' ,     int,    value=0, limits=(0,None) )),
            group( 'grid',
                param( 'show',   bool,   value=True ),
                param( 'spine',  bool,   value=True ),
                param( 'color', 'color', value='k' ))
            )


    def _cleanAxes( self, axl, gridCol ):
        if not isinstance( axl, list ):
            axl = [axl]

        if self.parameters()['grid','spine']:
            spineCol = gridCol
        else:
            spineCol = 'none'

        for ax in filter( bool, axl ):
            ax.clear()
            for loc, spine in ax.spines.items():
                spine.set_color( spineCol )


    def export( self, fileName=None) :
        plot, params = self.item, self.parameters()

        if isinstance( plot, PlotItem):
            mplWin  = MatplotlibWindow( dpi=params['dpi'], size=(params['size X'], params['size Y'] ) )
            mplPlot = mplWin.getFigure().add_subplot( 111 )
            gridCol = params['grid','color'].getRgbF()

            self._cleanAxes( mplPlot, gridCol )
            if params['grid','show']:
                mplPlot.grid( linestyle=':', color=gridCol )

            mplWin.loadStyle( params['style file'] )
            for curve in plot.curves:
                x, y = curve.getData()
                opts = curve.opts
                pen  = fn.mkPen( opts['pen'] )

                plotOpts = dict(
                    color     = pen.color().getRgbF(),
                    linestyle = ('-','')[pen.style() == QtCore.Qt.NoPen],
                    linewidth = pen.width() )

                if params['marker','every']:
                    symbol      = params['marker','symbol'] or opts['symbol']
                    symbolPen   = fn.mkPen( opts['symbolPen'] )
                    symbolBrush = fn.mkBrush( opts['symbolBrush'] )

                    plotOpts.update(
                        markeredgecolor = params['marker','edgecolor'].getRgbF(),
                        markerfacecolor = pen.color().getRgbF(),
                        markersize      = params['marker','size'] or opts['symbolSize'],
                        markevery       = params['marker','every'],
                        marker          = dict( t='^' ).get( symbol, symbol ) )

                if opts['fillLevel'] is not None and opts['fillBrush'] is not None:
                    fillcolor = fn.mkBrush( opts['fillBrush'] ).color()
                    mplPlot.fill_between( x=x, y1=y, y2=opts['fillLevel'], facecolor=fillcolor.getRgbF() )

                xr, yr  = plot.viewRange()
                mplPlot.plot( x, y, **plotOpts )
                mplPlot.set_xbound( *xr )
                mplPlot.set_ybound( *yr )

            # get labels from the graphic item
            mplPlot.set_title( plot.titleLabel.text )
            mplPlot.set_xlabel( plot.axes['bottom']['item'].label.toPlainText() ) #< attribute labelText misses units!
            mplPlot.set_ylabel( plot.axes['left']['item'].label.toPlainText() )
            mplPlot.figure.set_tight_layout( params['tight layout'] )
            mplWin.draw()
        else:
            raise Exception("Matplotlib export currently only works with plot items")

MatplotlibExporter.register()


class MatplotlibWindow(QtGui.QMainWindow):
    _instances = []

    def __init__( self, **kwArgs ):
        from ..widgets import MatplotlibWidget
        super(MatplotlibWindow, self).__init__()
        self.mpl = MatplotlibWidget.MatplotlibWidget( **kwArgs )
        self.setCentralWidget(self.mpl)
        self.show()
        type(self)._instances.append( self )

    def __getattr__( self, attr ):
        return getattr( self.mpl, attr )

    def closeEvent( self, ev ):
        self.__class__._instances.remove( self )
        self.deleteLater()

    def loadStyle( self, style ):
        import matplotlib as mpl
        if style:
            mpl.style.use( style )
        else:
            mpl.rcParams.update( mpl.rcParamsDefault )

