# -*- coding: utf-8 -*-

__all__ = ['_', 'C_', 'ngettext']

program = 'radiotray'

import locale
LC_ALL = locale.setlocale(locale.LC_ALL, '')

try:
    import gettext
    from gettext import gettext as _, ngettext
    gettext.install(program, str=True)
    gettext.textdomain(program)
    if hasattr(locale, 'textdomain'):
        locale.textdomain(program)

    def C_(ctx, s):
        """Provide qualified translatable strings via context.
            Taken from gnome-games.
        """
        translated = gettext.gettext('%s\x04%s' % (ctx, s))
        if '\x04' in translated:
            # no translation found, return input string
            return s
        return translated
    import builtins
    builtins.__dict__['ngettext'] = ngettext
    builtins.__dict__['C_'] = C_
except ImportError:
    import sys
    print(("You don't have gettext module, no " \
        "internationalization will be used."), file=sys.stderr)
    import builtins
    builtins.__dict__['_'] = lambda x: x
    builtins.__dict__['ngettext'] = lambda x, y, n: (n == 1) and x or y
