import logging
import re
import html
import bisect

from Qt import QtCore


def log_color(level, dark_text=True):
    COLORS = ['gray', 'black', 'magenta', 'red', 'red'] if dark_text \
        else ['gray', 'white', 'magenta', 'red', 'red']
    index = bisect.bisect_left(
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR],
        level
    )
    return COLORS[index]


class TextEditHandler(logging.Handler):
    """Messages are guaranteed to be appended in main GUI thread."""

    # TODO: avoid dead textedit?
    HTML_RE = re.compile('<.+>')

    class Sender(QtCore.QObject):
        """Transition class."""
        _append = QtCore.Signal(str)

    def __init__(self, textedit, level=logging.DEBUG, dark_text=True):
        super(TextEditHandler, self).__init__(level)
        self._textedit = textedit
        self._sender = TextEditHandler.Sender()
        self._sender._append.connect(self._textedit.append)
        self.dark_text = dark_text

    def emit(self, record):
        msg = self.format(record)
        is_html = self.HTML_RE.search(msg)
        if not is_html:
            msg = html.escape(msg)
        formatted = u'<span style="color:{}">{}</span>'.format(
            log_color(record.levelno, dark_text=self.dark_text),
            msg.replace('\n', '<br>')
        )
        self._sender._append.emit(formatted)
