#!/usr/bin/env python

GUI_CPARSER = False

from eoparser.helper import dir_files_get, abs_path_get, isC, isH, isXML
from eoparser.helper import _const
from eoparser.cparser import Cparser
from eoparser.cparser import GUI_CPARSER
from argparse import ArgumentParser
import sys

#creating instance to handle constants
const = _const()

def verbose_true(mes):
  print mes
def verbose_false(mes):
  pass

def main():
  if not GUI_CPARSER:
     print "Wrong cparser imported:"
     exit()
  print "Starting generation..."
  parser = ArgumentParser()
  parser.add_argument("-d", "--dir", dest="directory",
                  action="append", help="Source C-files to introspect", required=True)

  parser.add_argument("-o", "--outdir", dest="outdir",
                  action="store", help="Output directory", required=True)

  parser.add_argument("-t", "--typedefs", dest="typedefs",
                  action="store", help="Additional typedefs for parser")

  parser.add_argument("-X", "--xmldir", dest="xmldir", default = sys.path,
                  action="append", help="Directory to search for parent classes's XMLs")

  parser.add_argument("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose output")

  args = parser.parse_args()
  verbose_print = None

  if args.verbose is True:
    verbose_print = verbose_true
  else:
    verbose_print = verbose_false

  directories = []
  outdir = ""
  typedefs = ""
  xmldir = []

  directories = abs_path_get(args.directory)
  outdir = abs_path_get([args.outdir])[0]

  if args.xmldir is not None:
    xmldir = abs_path_get(args.xmldir, False)# not abort if dir doesn't exist

  if args.typedefs != None:
    typedefs = abs_path_get([args.typedefs])[0]

  files = dir_files_get(directories)
  c_files = filter(isC, files)
  h_files = filter(isH, files)

  cp = Cparser(args.verbose)
  cp.outdir_set(outdir)

  #adding typedefs from extern file
  if typedefs:
    cp.typedefs_add(typedefs)

  #fetching data from c-file
  for f in c_files:
  #  cp.c_file_data_get(f)
    cp.c_file_data_get2(f)

  #fetching data from h-file
  for f in h_files:
    cp.h_file_data_get(f)

  #remove records, which are not class, t.e. they don't have GET_FUNCTION key
  cl_data_tmp = dict(cp.cl_data) #deep copy of dictionary
  for k in cl_data_tmp:
    if const.GET_FUNCTION not in cp.cl_data[k]:
      print "Warning: no define for class: %s. Record will be excluded from tree"%k
      cp.cl_data.pop(k)
  del cl_data_tmp

  #mapping #defines, comments(@def) and op_ids together, to parse parameters
  for k in cp.cl_data:
    cp.parse_op_func_params(k)

  #cp.print_data()
  tup = cp.gui_parser_data_get()
  cp.typedef_file_create(tup)

  del cp

if __name__ == "__main__":
  
  main()


