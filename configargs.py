# configargs - define default arguments in ArgumentParser with a special configargs section
# Copyright (c) 2024 Karl Rieger

# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import configparser as cp
import argparse as ap
import warnings
import sys
import pathlib


class ConfigArgParser(ap.ArgumentParser):

    def __init__(self,cfg_file:str='',*args,cfgArgs=(), cfgKwArgs={},_argParseSection:str="ARGPARSE",_positionalIdentifier='__',_splitChar="\\",_specialTypes=None,**kwargs):
        self.cfg=cp.ConfigParser(*cfgArgs,**cfgKwArgs)
        self.cfg.optionxform=lambda x:x #case sensitive
        cfg_file=pathlib.Path(cfg_file)
        self.cfg.read(cfg_file)

        self._argParseSection=_argParseSection
        self._splitChar=_splitChar
        self._positionalIdentifier = _positionalIdentifier
        self._specialTypes = _specialTypes
        super(ConfigArgParser,self).__init__(*args,**kwargs)

        self._add_configargs() #parse file and add arguments

    def _add_configargs(self):
        config=self.cfg
        try:
            for key,argline in config[self._argParseSection].items():
                self._add_selfarg(key,argline)
        except KeyError as e:
             warnings.warn('self._argParseSection {0} not found in config, skipping adding configargs'.format(self._argParseSection))

    def _add_selfarg(self,key,argline):
        str_argname=''
        if len(key)==1 or key.startswith(self._positionalIdentifier):
            str_argname=key.strip(self._positionalIdentifier)
        else:
            str_argname='--'+key
        self.kwdict=self._process_argline(argline)
        self.add_argument(str_argname,**self.kwdict)
        return str_argname,self.kwdict

    def _process_argline(self,argline):
        args=argline.split(self._splitChar)
        self.kwdict={}
        for arg_arg in args:
            arg_arg=arg_arg.strip()
            eq_ind=arg_arg.find("=")
            if eq_ind==-1:
                raise ValueError('configargs argument need to specified with "=" but none found in {0}, of all args {1}'.format(arg_arg,args))
            key=arg_arg[:eq_ind]
            val=arg_arg[eq_ind+1:]
            val=self._process_special(key,val)
            self.kwdict[key]=val
        return self.kwdict

    def _process_special(self,key,val):
        # now some special cases
        if key=='nargs':
            try:
                return int(val)
            except ValueError:
                return val #your own risk by using '*' or '+'
        if key=='default':
            val=val.strip('[').strip(']').split(',')
            try:
                val=[self.kwdict['type'](k) for k in val]
                return val
            except KeyError:
                warnings.warn("could not convert value {0} to type (not found), returning value as stringlist. Maybe type is defined after default?")
                return [k for k in val]
        if key=='type':
            if val in dir(sys.modules["builtins"]):
                return getattr(sys.modules["builtins"],val)
            #others could be implemented here
            if self._specialTypes is not None:
                val = self._specialTypes(val)
            else:
                raise NotImplementedError("type={0} is not implemented in _process_special, please implement it or provide _specialTypes argument.".format(val))
        return val
