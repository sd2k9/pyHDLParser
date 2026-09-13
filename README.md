Hdlparse
========

Table of Contents
-----------------
[TOC]


Overview
--------
Hdlparse is a simple Python package implementing a rudimentary parser for SystemVerilog and VHDL.

It is not capable of fully parsing the entire language. Rather, it is meant to
extract enough key information from a source file to create generated
documentation.

This library is forked from [kevinpt](https://github.com/kevinpt/hdlparse) via
[zhelnio](https://github.com/zhelnio/hdlparse).


Installation
------------
1. Download or clone https://github.com/sd2k9/pyHDLParser
   to directory (e.g. `/opt/hdlparse`) as root
1. Create symbolic link  
    `cd /usr/local/bin; ln -s /opt/hdlparse/bin/sv_extract_port_param_as_markdown`


sv\_extract\_port\_param\_as\_markdown
--------------------------------------

The script `sv_extract_port_param_as_markdown` extracts port and parameter tables from a
SystemVerilog file and writes them as Markdown tables to separate output files.

When there are multiple modules in the file only the first one is parsed.


### Usage

```sh
python sv_extract_port_param_as_markdown \
  -i <input.sv> \
  --oport <ports_output.md> \
  --oparam <params_output.md> \
  [--force]
```

### Options

| Option             | Description                        |
|--------------------|------------------------------------|
| `-i`, `--ifile`    | Input SystemVerilog file            |
| `--oport`          | Output Markdown file for ports      |
| `--oparam`         | Output Markdown file for parameters |
| `--force`          | Overwrite existing output files     |
|  `-h`, `--help`    | Show help message and exit          |
| `-V`, `--version`  | Show program version and exit       |


### Output format

**Ports table** (`--oport`):

```markdown
| Direction | Width | Name  | Description |
|-----------|-------|-------|-------------|
| Input     | 1     | clk   | Clock input |
| Output    | [7:0] | data  |             |
```

**Parameters table** (`--oparam`):

```markdown
| Parameter Name | Default | Description         |
|----------------|---------|---------------------|
| DATA_WIDTH     | 8       | Width of data bus   |
```


When the module source code contains [section metacomments](#metacomments-and-sections)
the output is split into labelled sections with separate table headers.

Underscores in names are automatically escaped for LaTeX/Pandoc compatibility.



SystemVerilog Parsing
---------------------

#### Usage

Use the `VerilogExtractor` class to parse Verilog source files or strings.  
It also caches parsed objects.

```python
import hdlparse.verilog_parser as vlog

vlog_ex = vlog.VerilogExtractor()

# Parse from a file
vlog_mods = vlog_ex.extract_objects(fname='example.sv')

# Parse from a string
with open('example.sv', 'rt') as fh:
    code = fh.read()
vlog_mods = vlog_ex.extract_objects_from_source(text=code)
```
Both methods return a list of `VerilogModule` objects.


You can pass an optional object type to filter the results for just that type.
Currently only `VerilogModule` is supported:

```python
vlog_mods = vlog_ex.extract_objects(fname='example.sv',    type_filter=VerilogModule)
vlog_mods = vlog_ex.extract_objects_from_source(text=code, type_filter=VerilogModule)
```

If you don't require object caching you can use the following functions instead.

```python
vlog_ex = vlog.parse_verilog_file('example.sv')

vlog_ex = vlog.parse_verilog(code)
```



#### Accessing parsed objects

`VerilogModule` attributes:

| Attribute       | Description                                  |
|-----------------|----------------------------------------------|
| `name`          | Module name                                  |
| `generics`      | List of `VerilogParameter` (parameters)      |
| `ports`         | List of `VerilogParameter` (ports)           |
| `paramsections` | Dict mapping parameter index to [section label](#metacomments-and-sections) |
| `portsections`  | Dict mapping port index to [section label](#metacomments-and-sections)      |
| `desc`          | [Description](#description-comments)          |

Each `VerilogParameter` has:

| Attribute       | Description                                   |
|-----------------|-----------------------------------------------|
| `name`          | Parameter/port name                           |
| `mode`          | Ports: Port mode, e.g. `input`, `output`       |
|                 | Parameters: `param`                           |
| `data_type`     | Net/variable type, e.g. `wire`, `reg`          |
| `data_size`     | Vector range string or `None`, e.g. `[7:0]`    |
| `default_value` | Default value string or `None`                 |
| `desc`          | [Description](#description-comments)            |



Example code:

```python
for m in vlog_mods:
    print(f"Module {m.name}")

    print('  Parameters:')
    for p in m.generics:
        print('\t{:20}{:8}{}'.format(p.name, p.mode, p.data_type))

    print('  Ports:')
    for p in m.ports:
        print('\t{:20}{:8}{}'.format(p.name, p.mode, p.data_type))
```

Output:

```verilog
Module "modulename":
  Parameters:
    foo                 param   real
    bar                 param   real
    baz                 param   real
    zip                 param   signed [7:0]
  Ports:
    x                   input
    x2                  input
    y                   inout
    y2_long_output      inout
    z                   output  wire [4:1]
    z2                  output  wire [4:1]
```


#### Description Comments

Description comments can follow after a statement.

```verilog
parameter C_S_AXI_DATA_WIDTH     = 32, ///< AXI bus width, must be 32
```

They can also span multiple lines.

```verilog
   parameter PIXEL_WIDTH            = 10, ///< Width of pixel data inputs in bits.
                                          ///< Allowed values: 8, 10, 12
```

Or start on the following line.

```verilog
   parameter CONFIGURATION          = "VITOM_4K_HEAD",      // Optional source code comment not being extracted
        ///< Module configuration, see [section 8.2](#module-configuration-and-device-support)
```

And span multiple lines.

```verilog
   parameter logic [MGT_TX_CHANNELS-1:0] TX_FIFO_ENABLE  = {MGT_TX_CHANNELS{1'b0}},
        ///< Enable DownLink FIFOs (0:\ remove logic, 1:\ enable),
        ///< Bit position corresponds to channel
```


#### Metacomments and Sections

SystemVerilog source can include special comments to provide descriptions and logical sections.

```verilog
//# {{ My Name }}
```

When inside a port section it only applies to the following ports.  
When inside a parameter section it only applies to the following parameters.  
Outside ports and parameters it applies to both.

These section descriptions are accessible via the
dictionaries `paramsections` / `portsections` on the module.  
The key is the parameter or port index following the section metacomment, starting with 0.


#### File type detection

```python
vlog.is_verilog('design.sv')    # True
vlog.is_verilog('design.v')     # True
vlog.is_verilog('design.vlog')  # True
```


VHDL Parsing
------------

The VHDL parser can extract a variety of different objects from source code.
It can be used to access package definitions and component declarations, type and
subtype definitions, functions, and procedures found within a package. It will
not process entity declarations or nested subprograms and types.

Use the `VhdlExtractor` class to parse VHDL source files or source strings.  
It also caches parsed objects.

```python
import hdlparse.vhdl_parser as vhdl

vhdl_ex = vhdl.VhdlExtractor()

# Parse from a file
vhdl_objs = vhdl_ex.extract_objects(fname='example.vhdl')

# Parse from a string
import io
with io.open('example.vhdl', 'rt', encoding='latin-1') as fh:
    code = fh.read()
vhdl_objs = vhdl_ex.extract_objects_from_source(text=code)
```

Both methods return a list of parsed objects subclassed from `VhdlObject`.

You can pass an optional subclass of `VhdlObject` to filter the results for just that type:

```python
vhdl_comps = vhdl_ex.extract_objects(fname='example.vhdl', type_filter=VhdlComponent)
```

If you don't require object caching you can use the following functions instead

```python
vhdl_objs = parse_vhdl_file('example.vhdl')

vhdl_objs = parse_vhdl(code)
```


#### Accessing parsed objects

Each port and generic is an instance of `VhdlParameter` containing
the name, mode (input, output, inout) and type.

```python
for c in vhdl_comps:
    print('Component "{}":'.format(c.name))

    print('  Generics:')
    for p in c.generics:
        print('\t{:20}{:8} {}'.format(p.name, p.mode, p.data_type))

    print('  Ports:')
    for p in c.ports:
        print('\t{:20}{:8} {}'.format(p.name, p.mode, p.data_type))
```

Output:

```vhdl
Component "demo":
  Generics:
    GENERIC1            in       boolean
    GENERIC2            in       integer
  Ports:
    a                   in       std_ulogic
    b                   in       std_ulogic
    c                   out      std_ulogic_vector(7 downto 0)
    d                   out      std_ulogic_vector(7 downto 0)
    e                   inout    unsigned(7 downto 0)
    f                   inout    unsigned(7 downto 0)
```

#### VHDL Extracted Object Types

| Class            | `kind`       | Description                              |
|------------------|--------------|------------------------------------------|
| `VhdlPackage`    | `package`    | Package declaration                      |
| `VhdlComponent`  | `component`  | Component declaration (ports, generics)  |
| `VhdlEntity`     | `entity`     | Entity declaration (ports, generics)     |
| `VhdlFunction`   | `function`   | Function declaration with parameters     |
| `VhdlProcedure`  | `procedure`  | Procedure declaration with parameters    |
| `VhdlType`       | `type`       | Type definition (array, record, enum, …) |
| `VhdlSubtype`    | `subtype`    | Subtype definition                       |
| `VhdlConstant`   | `constant`   | Constant declaration                     |

Each port/generic/parameter is a `VhdlParameter` instance with the following attributes:

| Attribute       | Description                                      |
|-----------------|--------------------------------------------------|
| `name`          | Name of the port/generic/parameter              |
| `mode`          | Direction: `in`, `out`, `inout`, `buffer`        |
| `data_type`     | `VhdlParameterType`                               |
| `default_value` | Default value string, or `None`                  |
| `desc`          | Description from metacomments, or `None`         |
| `param_desc`    | Description of the parameter, or `None`          |

`VhdlParameterType` attributes:

| Attribute   | Description                                        |
|-------------|----------------------------------------------------|
| `name`      | Type name (e.g. `std_logic_vector`)                |
| `direction` | Array direction: `to` or `downto`                  |
| `l_bound`   | Left bound expression of array range               |
| `r_bound`   | Right bound expression of array range              |
| `arange`    | Full original array range string (e.g. `(7 downto 0)`) |


#### VHDL Array Type Tracking

`VhdlExtractor` automatically tracks array type definitions it encounters.  
Use `is_array()` to query whether a type name is an array:

```python
vhdl_ex = vhdl.VhdlExtractor()

code = '''
package foobar is
  type custom_array is array(integer range <>) of boolean;
  subtype custom_subtype is custom_array(1 to 10);
end package;
'''
vhdl_ex.extract_objects_from_source(text=code)

print(vhdl_ex.is_array('unsigned'))        # True (built-in)
print(vhdl_ex.is_array('custom_array'))    # True
print(vhdl_ex.is_array('custom_subtype'))  # True (subtype of array)
```

The following IEEE standard array types are recognised by default:
`std_ulogic_vector`, `std_logic_vector`, `signed`, `unsigned`, `bit_vector`.

You can persist and restore array type registries:

```python
# Save registry to file
vhdl_ex.save_array_types(fname='array_types.txt')

# Load registry from file
vhdl_ex.load_array_types(fname='array_types.txt')
```

This lets you parse one set of files for type definitions
and use the saved info for parsing other code at a different time.


You can also add array type definitions from source files.

```python
vhdl_ex.register_array_types_from_sources(source_files=list_of_file_names)
```

You can also seed the extractor with known array types at construction:

```python
vhdl_ex = vhdl.VhdlExtractor(array_types={'my_custom_vec', 'another_type'})
```

#### VHDL Subprogram Helpers

Two utility functions help work with functions and procedures.

Generate a canonical prototype string
- `vo` is either a `VhdlFunction` or `VhdlProcedure` object
- Example result: `function afunc(q : std_ulogic; h : unsigned) return std_ulogic;`


```python
from hdlparse.vhdl_parser import subprogram_prototype
proto = subprogram_prototype(vo)
```

Generate a signature string
- `vo` is either a `VhdlFunction` or `VhdlProcedure` object
- When `fullname` is `None` (default), use the name attribute from `vo`
- Example result: `afunc[std_ulogic,unsigned return std_ulogic]`

```python
from hdlparse.vhdl_parser import subprogram_signature
sig = subprogram_signature(vo, fullname)
```

#### File type detection

```python
vhdl.is_vhdl('design.vhd')     # True
vhdl.is_vhdl('design.vhdl')    # True
```


Changes
--------
- [Changelog](doc/changelog.md)


License
-------
Hdlparse is licensed under the terms of the [MIT License](LICENSE).

Copyright © 2017 Kevin Thibedeau.

Further contributions see Git logs.
