#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-

import hdlparse.verilog_parser as vlog
from pprint import pprint

vlog_ex = vlog.VerilogExtractor()

vl0 =  vlog_ex.extract_objects("test.v")
vl1 = vlog_ex.extract_objects("CREATEME.sv")

# pprint(vl0)
# print ("\n")
# pprint(vl1)

for m in vl0 + vl1:  # Concatenation of arrays with '+'
  print('Module "{}":'.format(m.name))

  if m.paramsections:
    print("Parameter Sections")
    pprint (m.paramsections)
  if m.portsections:
    print("Port Sections")
    pprint (m.portsections)
    print("")

  print('  Parameters:')
  for p in m.generics:
    # pprint(dir(p))
    if p.data_size is None:
      data_size = ''
    else:
      data_size = p.data_size
    print('\t{:35} / {:8} / {}{} = {} ({})'.format(p.name, p.mode, p.data_type, data_size, p.default_value, " ".join(p.desc)))

  print('  Ports:')
  for p in m.ports:
    if p.data_size is None:
      data_size = ''
    else:
      data_size = p.data_size
    print('\t{:35} / {:8} / {}{} ({})'.format(p.name, p.mode, p.data_type, data_size, " ".join(p.desc)))

# pprint(vl0)
# pprint(dir(vl0))
