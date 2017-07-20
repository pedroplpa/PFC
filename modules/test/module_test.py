import json

def BEGIN():
	res = ["Name","Age"]
	return res


def RUN(file_name):
	with open(file_name + ".json", "r") as input_data:
		parameters = json.load(input_data)
	result = "Hello, my name is " + parameters["Name"] + " and I'm " + parameters["Age"] + " years old."
	print(result)
	return result