=======================
 Pristine Sphinx Theme
=======================

This is a theme for the Sphinx documentation generator (sphinx.pocoo.org).

Installation
============

Follow these steps to use this theme in your project's documentation:

1.  Put this as ``_themes`` folder into your documentation folder.

2.  Add the following code to your ``conf.py``::

        sys.path.append(os.path.abspath('_themes'))
        html_theme_path = ['_themes']
        html_theme = 'pristine'

Options
-------

The following theme options are available. Overwrite the default values below
using the ``html_theme_options`` dictionary in ``conf.py``:

``index_logo``
    Filename of an image in ``_static`` used as replacement for the ``<h1>``
    in ``index.rst``. No default.

``index_logo_height``
    Height of the ``index_logo`` image in pixels. No default.

``page_width``
    Page width in pixels. Defaults to ``960``.

``sidebar_width``
    Sidebar width in pixels. Defaults to ``260``.

``github_fork``
    Github repository URL for a fork-me ribbon (``user/repo``). No default.

``bitbucket_fork``
    Bitbucket repository URL for a fork-me ribbon (``user/repo``). No default.

Resources
=========

The resources used in this theme are:

* Ubuntu font family: http://font.ubuntu.com/

* Github ribbon: https://github.com/blog/273-github-ribbons

* Bitbucket ribbon: https://bitbucket.org/zgramana/bitbucket-ribbons
