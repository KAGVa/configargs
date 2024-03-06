import configargs

parser = configargs.ConfigArgParser('example.cfg')
args = parser.parse_args()
print(args.ARG1)
print(args.ARG2)
print(args.arg3)

print(parser.cfg['SOME_SECTION'].getboolean('VALUE_3'))
