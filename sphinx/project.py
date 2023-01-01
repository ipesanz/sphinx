"""Utility function and classes for Sphinx projects."""

from __future__ import annotations

import os
from glob import glob
from typing import Iterable

from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.matching import get_matching_files
from sphinx.util.osutil import SEP, path_stabilize, relpath

logger = logging.getLogger(__name__)
EXCLUDE_PATHS = ['**/_sources', '.#*', '**/.#*', '*.lproj/**']


class Project:
    """A project is the source code set of the Sphinx document(s)."""

    def __init__(self, srcdir: str, source_suffix: dict[str, str]) -> None:
        #: Source directory.
        self.srcdir = srcdir

        #: source_suffix. Same as :confval:`source_suffix`.
        self.source_suffix = source_suffix

        #: The name of documents belongs to this project.
        self.docnames: set[str] = set()

    def restore(self, other: "Project") -> None:
        """Take over a result of last build."""
        self.docnames = other.docnames

    def discover(self, exclude_paths: Iterable[str] = (),
                 include_paths: Iterable[str] = ("**",)) -> set[str]:
        """Find all document files in the source directory and put them in
        :attr:`docnames`.
        """
        self.docnames = set()
        for filename in get_matching_files(
            self.srcdir,
            include_paths,
            [*exclude_paths] + EXCLUDE_PATHS,
        ):
            docname = self.path2doc(filename)
            if docname:
                if docname in self.docnames:
                    pattern = os.path.join(self.srcdir, docname) + '.*'
                    files = [relpath(f, self.srcdir) for f in glob(pattern)]
                    logger.warning(__('multiple files found for the document "%s": %r\n'
                                      'Use %r for the build.'),
                                   docname, files, self.doc2path(docname), once=True)
                elif os.access(os.path.join(self.srcdir, filename), os.R_OK):
                    self.docnames.add(docname)
                else:
                    logger.warning(__("document not readable. Ignored."), location=docname)

        return self.docnames

    def path2doc(self, filename: str) -> str | None:
        """Return the docname for the filename if the file is a document.

        *filename* should be absolute or relative to the source directory.
        """
        if filename.startswith(self.srcdir):
            filename = relpath(filename, self.srcdir)
        for suffix in self.source_suffix:
            if filename.endswith(suffix):
                filename = path_stabilize(filename)
                return filename[:-len(suffix)]

        # the file does not have docname
        return None

    def doc2path(self, docname: str, basedir: bool = True) -> str:
        """Return the filename for the document name.

        If *basedir* is True, return as an absolute path.
        Else, return as a relative path to the source directory.
        """
        docname = docname.replace(SEP, os.path.sep)
        basename = os.path.join(self.srcdir, docname)
        for suffix in self.source_suffix:
            if os.path.isfile(basename + suffix):
                break
        else:
            # document does not exist
            suffix = list(self.source_suffix)[0]

        if basedir:
            return basename + suffix
        else:
            return docname + suffix
