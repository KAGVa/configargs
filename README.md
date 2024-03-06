# configargs
configargs - simple way to define arguments in a special section of a configparser file

# usage
copy file into project you want to use it and use
`import configargs`

# example
create a *ConfigArgParser* object. The object takes all the arguments of argparse.ArgumentParser and a few extra ones:
 - cfg_file (necessary): the config file to be read
 - cfgArgs=() and cfgKwArgs={} : arguments given to configparser
 - _argParseSection:str="ARGPARSE",_positionalIdentifier='__',_splitChar="\\" : define the special config section to be used for cmd arguments, special identifier for positional arguments and a splitChar to distinguish argparse arguments
 - _specialTypes=None : callable that will take care of non builtin types for the type argument of ArgumentParser
 - *args, **kwargs : args and kwargs forwarded to ArgumentParser

an example:

The example.cfg file

```
[SOME_SECTION]

VALUE_1 = 10
VALUE_2 = A_STRING
VALUE_3 = True

[ARGPARSE]

__ARG1=type=str\help=positional argument 1
__ARG2=type=int\help=positional argument 2
arg3=nargs=*\type=float\default=[10]\help=additional optional named argument
```

and the example.py script

```
import configargs

parser = configargs.ConfigArgParser('example.cfg')
args = parser.parse_args()
print(args.ARG1)
print(args.ARG2)
print(args.arg3)

print(parser.cfg['SOME_SECTION'].getboolean('VALUE_3'))
```

leads to the output:

```
python example.py 1 2 --arg3 11 112 114.5
1
2
[11.0, 112.0, 114.5]
True
```
