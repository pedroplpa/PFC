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

	return config[choosen_module]

def CHOOSE_MODULES_REPORT(config):
	#Showing Modules
	module_names = config.keys()
	readline.set_completer(SimpleCompleter(list(module_names) + ["execute_report"]).complete)
	print("\nChoose the modules for the Report: ")
	print("\nTo execute the report choose [execute_report]")
	choosen_module = {}
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
			modules.append(config[choosen_module])

	return modules

def MODULE_EXECUTION(config, choosen_module):	
	#Module choosen
	module = importlib.import_module("modules." + choosen_module["directory"] + "." + choosen_module["name"])
		
	if os.path.isfile("modules/" + choosen_module["directory"] + "/" + choosen_module["name"] + ".json"):
		readline.set_completer(SimpleCompleter(["yes","no"]).complete)
		answer = input("Use the last used parameters? [yes/no] ")
		if answer == "yes":
			return module.RUN("modules/" + choosen_module["directory"] + "/" + choosen_module["name"])

	querie = module.BEGIN()

	dic = {}
	for field in querie:
		dic[field] = input(field + ": ")
	with open("modules/" + choosen_module["directory"] + "/" + choosen_module["name"] + ".json", "w") as parameters:
		json.dump(dic, parameters)

	return module.RUN("modules/" + choosen_module["directory"] + "/" + choosen_module["name"])

def REPORT(config, choosen_modules):
	str_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
	report = {}
	report["time"] = str_time
	report["result"] = {}
	answer = ""
	for module in choosen_modules:
		if os.path.isfile("modules/" + module["directory"] + "/" + module["name"] + "_result.json"):
			readline.set_completer(SimpleCompleter(["yes","no"]).complete)
			while(answer != "no" and answer != "yes"):
				answer = input("Use the last generated report? [yes/no] ")
				if answer != "yes" and answer != "no":
					print("Invalid answer")
		
		if answer != "yes":
			MODULE_EXECUTION(config, module)
		
		with open("modules/" + module["directory"] + "/" + module["name"] + "_result.json","r") as module_report:
			report_dict = json.load(module_report)
			report["result"][report_dict["title"]] = report_dict["result"]
		answer = ""

	filename = "reports/" + str_time + ".json"
	os.makedirs(os.path.dirname(filename), exist_ok=True)
	
	with open(filename,"w") as output_data:
		json.dump(report, output_data)

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
	print("$$$$$$$\                      $$\     $$$$$$\ $$\      $$\ $$$$$$$$\ ")
	print("$$  __$$\                     $$ |    \_$$  _|$$$\    $$$ |$$  _____|")
	print("$$ |  $$ | $$$$$$\  $$$$$$$\$$$$$$\     $$ |  $$$$\  $$$$ |$$ |      ")
	print("$$$$$$$  |$$  __$$\ $$  __$$\_$$  _|    $$ |  $$\$$\$$ $$ |$$$$$\    ")
	print("$$  ____/ $$$$$$$$ |$$ |  $$ |$$ |      $$ |  $$ \$$$  $$ |$$  __|   ")
	print("$$ |      $$   ____|$$ |  $$ |$$ |$$\   $$ |  $$ |\$  /$$ |$$ |      ")
	print("$$ |      \$$$$$$$\ $$ |  $$ |\$$$$  |$$$$$$\ $$ | \_/ $$ |$$$$$$$$\ ")
	print("\__|       \_______|\__|  \__| \____/ \______|\__|     \__|\________|")


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