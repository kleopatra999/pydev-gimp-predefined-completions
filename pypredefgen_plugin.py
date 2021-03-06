# -*- coding: utf-8 -*-

"""
This module defines a GIMP plug-in to generate predefined completions for PyDev
(Eclipse IDE plug-in) for GIMP modules.
"""

from __future__ import absolute_import, print_function, division, unicode_literals

import io
import os

import importlib

import gimp
import gimpfu

import pypredefgen
import pypredefgen_pdb

#===============================================================================


def generate_predefined_completions_for_pydev(generate_for_modules, generate_for_pdb):
  if generate_for_modules:
    module_names = _get_module_names(pypredefgen.MODULES_FILE_PATH)
  else:
    module_names = []
  
  gimp_progress = GimpProgress(
    _get_num_progress_items(generate_for_modules, module_names, generate_for_pdb))
  gimp_progress.initialize()
  
  if generate_for_modules:
    _make_dirs(pypredefgen.PYPREDEF_FILES_DIR)
    
    pypredefgen.module_specific_processing_functions.update({
      module_name: [pypredefgen.remove_class_docstrings]
      for module_name in [
        "_gimpui", "gtk._gtk", "gtk.gdk", "gobject._gobject", "cairo._cairo", "pango",
        "pangocairo", "atk", "glib._glib", "gio._gio"]
    })
    
    for module_name in module_names:
      module = importlib.import_module(module_name)
      pypredefgen.generate_predefined_completions(module)
      gimp_progress.update()
  
  if generate_for_pdb:
    pypredefgen_pdb.generate_predefined_completions_for_gimp_pdb()
    gimp_progress.update()


def _get_module_names(modules_file_path):
  if os.path.isfile(modules_file_path):
    with io.open(
           modules_file_path, "r",
           encoding=pypredefgen.TEXT_FILE_ENCODING) as modules_file:
      return [line.strip() for line in modules_file.readlines()]
  else:
    return []


def _make_dirs(path):
  """
  Recursively create directories from the specified path.
  
  Do not raise exception if the path already exists.
  """
  
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == os.errno.EEXIST and os.path.isdir(path):
      pass
    elif exc.errno == os.errno.EACCES and os.path.isdir(path):
      # This can happen if `os.makedirs` is called on a root directory
      # in Windows (e.g. `os.makedirs("C:\\")`).
      pass
    else:
      raise


#===============================================================================


class GimpProgress(object):
  
  def __init__(self, num_total_tasks=0):
    self.num_total_tasks = num_total_tasks
    self._num_finished_tasks = 0
  
  @property
  def num_finished_tasks(self):
    return self._num_finished_tasks
  
  def initialize(self, message=None):
    gimp.progress_init(message if message is not None else "")
  
  def update(self, num_tasks=1):
    if self._num_finished_tasks + num_tasks > self.num_total_tasks:
      raise ValueError("number of finished tasks exceeds the number of total tasks")
    
    self._num_finished_tasks += num_tasks
    
    gimp.progress_update(self._num_finished_tasks / self.num_total_tasks)
  

def _get_num_progress_items(generate_for_modules, module_names, generate_for_pdb):
  num_progress_items = 0
  if generate_for_modules:
    num_progress_items += len(module_names)
  
  if generate_for_pdb:
    num_progress_items += 1
  
  return num_progress_items


#===============================================================================

gimpfu.register(
  proc_name="generate_predefined_completions_for_pydev",
  blurb=("Generate predefined completions for GIMP modules for PyDev "
         "(Eclipse IDE plug-in)"),
  help=('This plug-in generates separate .pypredef files for each module and '
        'for the GIMP procedural database in the "{0}" subdirectory '
        'of the directory where this plug-in is located.'
        .format(pypredefgen.PYPREDEF_FILES_DIRNAME)),
  author="khalim19",
  copyright="",
  date="",
  label="Generate Predefined Completions for PyDev",
  imagetypes="",
  params=[
    (gimpfu.PF_BOOL, "generate_for_modules", "Generate completions for modules?", True),
    (gimpfu.PF_BOOL, "generate_for_pdb",
     "Generate completions for GIMP procedural database (PDB)?", True)
  ],
  results=[],
  function=generate_predefined_completions_for_pydev,
  menu="<Image>/Filters/Languages/Python-Fu")

gimpfu.main()
