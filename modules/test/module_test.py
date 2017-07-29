import json

def BEGIN():
	res = ["Name","Age"]
	return res


def RUN(file_name):
	result_file = file_name + "_result"
	with open(file_name + ".json", "r") as input_data:
		parameters = json.load(input_data)
	result = "Hello, my name is " + parameters["Name"] + " and I'm " + parameters["Age"] + " years old."
	print(result)

	with open(result_file + ".json", "w") as output_data:
		report = {}
		report["title"] = "Test from name: " + parameters["Name"] + " and age: " + parameters["Age"]
		report["result"] = result
		json.dump(report, output_data)