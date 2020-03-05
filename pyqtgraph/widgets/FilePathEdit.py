
from ..Qt        import QtGui
from ..python2_3 import asUnicode
from .FileDialog import FileDialog
from os          import path

__all__ = ['FilePathEdit']

#----------------------------------------
class FilePathEdit(QtGui.QLineEdit):
#----------------------------------------
    """
    QLineEdit specialized in giving filenames and directories.
    On double click it opens a FileDialog for selecting a file or directory.
    """

    def __init__( self, *args, **kwArgs ):
        """
        =======================      =========================================================
        **Keyword Arguments:**
        caption                      The caption string for the FileDialog
        dir                          If there's no content yet, the FileDialog's working
                                       directory is set to dir.
        filter                       The file filters used in the FileDialog.
                                     These can be given as a string or a list of strings.
        selectDir                    If this bool-flag (default: False) is set True the
                                       FileDialog will open for selecting a directory.
        tooltip                      The widget's tooltip string, by default giving a hit for
                                       trying double click to open a FileDialog.
        =======================      =========================================================
        """
        tooltip = kwArgs.get( 'tooltip', 'double click to select by dialog' )

        self._selectDir = kwArgs.get( 'selectDir', False )
        self._caption   = kwArgs.get( 'caption', '' )
        self._dir       = kwArgs.get( 'dir', None )

        filter = kwArgs.get( 'filter', '' )
        try   : self._filter = filter.strip()
        except: self._filter = ';;'.join( filter )

        super(FilePathEdit, self).__init__( *args )
        self.setStyleSheet( 'border: 0px' )
        self.setToolTip( tooltip )


    def value( self ):
        """get the edit's text as unicode string."""
        return asUnicode( self.text() )


    def setValue( self, val ):
        """converts the given value to unicode and sets it as the edit's text."""
        self.setText( asUnicode( val ) )


    def mouseDoubleClickEvent( self, event ):
        """Extends double click handling by opening a FileDialog for selecting either a file or a directory.
        """
        super(FilePathEdit, self).mouseDoubleClickEvent( event )

        dir = self._dir or path.dirname( self.text() ) or '.'
        if self._selectDir:
            filePath = FileDialog.getExistingDirectory( self.parent(), self._caption, dir )
        else:
            filePath = FileDialog.getOpenFileName( self.parent(), self._caption, dir, self._filter )[0]

        if filePath:
            self.setText( filePath )

