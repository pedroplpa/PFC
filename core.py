import importlib
import json
import os.path
import readline
import os
from datetime import datetime

def INIT():
	#Initial configuration
	with open("config.json") as config_file:
		config = json.load(config_file)
	return config

def CHOOSE_MODULES(config):
	#Showing Modules
	module_names = config.keys()
	readline.set_completer(SimpleCompleter(module_names).complete)
	print("\nChoose one of the modules: ")
	for name in module_names:
		print(" -> " + name)
	print(" -> Return to Main Menu")

	#Choosing module
	print
	choosen_module = input("Module: ")
	
	if choosen_module in ["Return", "return", "Quit", "quit", "Exit", "exit"]:
		return 0

	if choosen_module not in module_names:
		print("Invalid module!!")
		return -1

	return choosen_module

def CHOOSE_MODULES_REPORT(config):
	#Showing Modules
	module_names = config.keys()
	readline.set_completer(SimpleCompleter(list(module_names) + ["execute_report"]).complete)
	print("\nChoose the modules for the Report: ")
	print("\nTo execute the report choose [execute_report]")
	choosen_module = ""
	modules = []
	while choosen_module != "execute_report":
		for name in module_names:
			print(" -> " + name)
		print(" -> execute_report")
		print(" -> Return to Main Menu")

		#Choosing module
		print
		choosen_module = input("Module: ")

		if choosen_module in ["Return", "return", "Quit", "quit", "Exit", "exit"]:
			return 0

		if choosen_module not in module_names and choosen_module != "execute_report":
			print("Invalid module!!")
			continue

		if choosen_module in module_names:
			modules.append(choosen_module)

	return modules

def MODULE_EXECUTION(config, choosen_module):	
	#Module choosen
	module = importlib.import_module("modules." + config[choosen_module]["directory"] + "." + config[choosen_module]["name"])
		
	if os.path.isfile("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"] + ".json"):
		readline.set_completer(SimpleCompleter(["yes","no"]).complete)
		answer = input("Use the last used parameters? [yes/no] ")
		if answer == "yes":
			return module.RUN("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"])

	querie = module.BEGIN()

	dic = {}
	for field in querie:
		dic[field] = input(field + ": ")
	with open("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"] + ".json", "w") as parameters:
		json.dump(dic, parameters)

	return module.RUN("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"])

def REPORT(config, choosen_modules):
	str_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	report = "Report from " + str_time
	for module in choosen_modules:
		report = report + "\n\n" + MODULE_EXECUTION(config, module)
	
	filename = "reports/" + str_time + ".txt"
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	
	with open(filename,"w") as output_data:
		output_data.write(report)

def MAIN():
	config_string = "reload_configuration"
	module_string = "execute_module"
	report_string = "generate_report"
	exit_string = "exit"
	action = ""
	config = INIT()

	readline.parse_and_bind('tab: complete')

	while(action not in ["Exit", "exit", "Quit", "quit"]):
		readline.set_completer(SimpleCompleter([config_string, module_string, report_string, exit_string]).complete)
		print("\nChoose a action: ")
		print(" -> " + config_string)
		print(" -> " + module_string)
		print(" -> " + report_string)
		print(" -> " + exit_string)
	
		action = input("Action: ")
	
		if action == config_string:
			config = INIT()
		elif action == module_string:
			module = CHOOSE_MODULES(config)
			if module == 0 or module == 1:
				continue
			else:
				MODULE_EXECUTION(config, module)
		elif action == report_string:
			modules = CHOOSE_MODULES_REPORT(config)
			if modules == 0 or modules == 1:
				continue
			else:
				REPORT(config, modules)
		elif action not in ["Exit", "exit", "Quit", "quit"]:
			print("Invalid Action")

	print
	print("PentIME")	
	return

class SimpleCompleter(object):
    
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        
        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

MAIN()