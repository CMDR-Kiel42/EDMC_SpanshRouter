import sys
import traceback
try:
    # Python 2
    from .updater import SpanshUpdater
    from .AutoCompleter import AutoCompleter
    from .PlaceHolderEntry import PlaceHolderEntry
    from SpanshRouter import SpanshRouter
except ModuleNotFoundError:
    # Python 3
    from SpanshRouter.updater import SpanshUpdater
    from SpanshRouter.AutoCompleter import AutoCompleter
    from SpanshRouter.PlaceHolderEntry import PlaceHolderEntry
    from SpanshRouter import SpanshRouter