import importlib
import json
import os.path
import readline
#from Completer import BufferAwareCompleter

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
	choosen_module = raw_input("Module: ")
	
	if choosen_module in ["Return", "return", "Quit", "quit", "Exit", "exit"]:
		return 0

	if choosen_module not in module_names:
		print("Invalid module!!")
		return -1

	return choosen_module

def MODULE_EXECUTION(config, choosen_module):	
	#Module choosen
	module = importlib.import_module("modules." + config[choosen_module]["directory"] + "." + config[choosen_module]["name"])
		
	if os.path.isfile("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"] + ".json"):
		readline.set_completer(SimpleCompleter(["yes","no"]).complete)
		answer = raw_input("Use the last used parameters? [yes/no] ")
		if answer == "yes":
			module.RUN("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"])
			return

	querie = module.BEGIN()

	dic = {}
	for field in querie:
		dic[field] = raw_input(field + ": ")
	with open("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"] + ".json", "w") as parameters:
		json.dump(dic, parameters)

	module.RUN("modules/" + config[choosen_module]["directory"] + "/" + config[choosen_module]["name"])

def MAIN():
	config_string = "reload_configuration"
	module_string = "execute_module"
	exit_string = "exit"
	action = ""
	config = INIT()

	readline.parse_and_bind('tab: complete')

	while(action not in ["Exit", "exit", "Quit", "quit"]):
		readline.set_completer(SimpleCompleter([config_string, module_string, exit_string]).complete)
		print("\nChoose a action: ")
		print(" -> " + config_string)
		print(" -> " + module_string)
		print(" -> " + exit_string)
	
		action = raw_input("Action: ")
	
		if action == config_string:
			config = INIT()
		elif action == module_string:
			module = CHOOSE_MODULES(config)
			if module == 0 or module == 1:
				continue
			else:
				MODULE_EXECUTION(config, module)
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