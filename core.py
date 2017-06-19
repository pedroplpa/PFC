import importlib
name = raw_input("Choose the module: ")

module_test = importlib.import_module(name)

querie = module_test.BEGIN()

dic = {}
for field in querie:
	dic[field] = raw_input(field + ": ")

module_test.RUN(dic)