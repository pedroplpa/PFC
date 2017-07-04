import importlib
import json
import os.path

#Initial configuration
with open("config.json") as config_file:
	config = json.load(config_file)
while True:
	#Showing Modules
	module_names = config.keys()
	print("\nChoose one of the modules: ")
	for name in module_names:
		print(" -> " + name)
	print(" -> exit")

	#Choosing module
	print
	choosen_module = raw_input("Module: ")
	
	#If exit is choosen
	if choosen_module == "exit":
		break
	
	#Module choosen
	if choosen_module in module_names:
		module = importlib.import_module(config[choosen_module])
		
		if os.path.isfile(choosen_module + ".json"):
			answer = raw_input("Use the last used parameters? [yes/no] ")
			if answer == "yes":
				module.RUN(choosen_module)
				continue

		querie = module.BEGIN()

		dic = {}
		for field in querie:
			dic[field] = raw_input(field + ": ")
		with open(choosen_module + ".json", "w") as parameters:
			json.dump(dic, parameters)

		module.RUN(choosen_module)

	#Invalid Module
	else:
		print("Invalid module!!")
print
print("PentIME")