import io
import logging

from datetime import datetime

## todo
# proper logging for multi processing


class PrintInfo(object):
    def setup(
        self,
        print_nam=None,
        print_verbose=False,
        print_level=logging.INFO,
    ):

        if print_nam is None:
            print_nam = self.__class__.__name__

        self._print_nam = print_nam
        self._print_verbose = print_verbose
        self._print_level = print_level

        return self

    def print(self, *args, **kwargs):
        """info printer"""
        self._print(logging.INFO, *args, **kwargs)

    def print_d(self, *args, **kwargs):
        """debug printer"""
        self._print(logging.DEBUG, *args, **kwargs)

    def print_i(self, *args, **kwargs):
        """info printer"""
        self._print(logging.INFO, *args, **kwargs)

    def print_v(self, *args, **kwargs):
        """verbose printer"""
        if self._print_verbose:
            self._print(logging.INFO, *args, **kwargs)

    def print_w(self, *args, **kwargs):
        """warn printer"""
        self._print(logging.WARN, *args, **kwargs)

    def print_e(self, *args, **kwargs):
        """error printer"""
        self._print(logging.ERROR, *args, **kwargs)

    def print_c(self, *args, **kwargs):
        """critical printer"""
        self._print(logging.CRITICAL, *args, **kwargs)

    def print_ex(self, *args, **kwargs):
        """exception printer"""
        self._print_log.exception(*args, **kwargs)

    def _print(self, level, *args, **kwargs):
        # print( level, *args, **kwargs )
        if self._print_level == logging.NOTSET:
            return

        if level >= self._print_level:
            msg = self._prints(*args, **kwargs)
            try:
                dt = self._print_pre()
                print(f"{dt}:{logging.getLevelName(level)}:", msg)
            except Exception as ex:
                print(ex)

    def _print_pre(self):
        now = datetime.utcnow()
        dt = now.strftime("%Y%m%d-%H%M%S.%f")
        return dt

    def _prints(self, *args, end=" "):
        s = io.StringIO()
        _ident = ""
        for a in args:
            s.write(_ident)
            s.write(a)
            _ident = end

        return s.getvalue()


if __name__ == "__main__":
    p = PrintInfo().setup(
        print_verbose=True,
    )
    p.print("test")
    p.print_i("test")
    p.print_d("test")
    p.print_w("test")
    p.print_e("test")
    p.print_c("test")
    p.print("test")
