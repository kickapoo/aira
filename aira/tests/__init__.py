import shutil
import tempfile

from django.test import override_settings


class RandomMediaRootMixin:
    """Override MEDIA_ROOT to a temporary directory.

    In setUp(), execute self.override_media_root(); in tearDown, execute
    self.end_media_root_override(). The result is approximately the same as
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp()), except that in the end it removes
    the temporary directory.
    """

    def override_media_root(self):
        self.tmpdir = tempfile.mkdtemp()
        self.overrider = override_settings(MEDIA_ROOT=self.tmpdir)
        self.overrider.enable()

    def end_media_root_override(self):
        self.overrider.disable()
        shutil.rmtree(self.tmpdir)
