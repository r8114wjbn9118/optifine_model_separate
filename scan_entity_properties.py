from tool import *
from jproperties import Properties

def search_entity_properties_path(entity_type_list):
	entity_path_dict = {}
	for entity_type in entity_type_list:
		entity_path_dict[entity_type] = None
	for root, dirs, files in os.walk(os.path.join(optifine_dir, "random")):
		for file in files:
			file_split = os.path.splitext(file)
			if file_split[1] == ".properties":
				if file_split[0] in entity_type_list:
					entity_type = file_split[0]
					entity_path_dict[entity_type] = os.path.join(root, file)
	return entity_path_dict

def get_entity_properties_data(entity_properties_path):
	properties_data_list = {}

	properties = Properties()
	with open(entity_properties_path, 'rb') as file:
		properties.load(file)

	for item in properties.items():
		char = item[0].split(".")
		data = item[1].data
		if len(char) == 2:
			if not char[1] in properties_data_list:
				properties_data_list[char[1]] = {}
			properties_data_list[char[1]].update({char[0]:data})
	return properties_data_list

def get_character_data(properties_data_list):
	char_data_list = []

	models_index = int(get_config("properties", "model_first_index"))
	for pi in properties_data_list:
		properties_data = properties_data_list[pi]
		char = properties_data.get("name")
		if char:
			name_list = char.split(":")
			if name_list[0] == "iregex":
				char_index = len(char_data_list)

				name_list = name_list[1].split("|")
				for name in name_list:
					char_name = name.split("-")[0]
					for ci in range(len(char_data_list)):
						if char_name in char_data_list[ci]["name"]:
							char_index = ci
				
				if char_index == len(char_data_list):
					char_data_list.append({"skins":[], "name":[], "suffix":[], "value":[], "connection":{}, "models":[]})
				char_data = char_data_list[char_index]
				
				char_data["value"].append(pi)

				skins = process_properties_list(properties_data.get("skins"))
				
				for name in name_list:
					char_name = name.split("-")
					if len(char_name) < 1:
						continue
					n = char_name[0]
					if not n in char_data["name"]:
						char_data["name"].append(n)

					if len(char_name) < 2:
						continue
					s = char_name[1]
					if not s in char_data["suffix"]:
						char_data["suffix"].append(s)
					
					if not char_data["connection"].get(s):
						char_data["connection"][s] = []
					for skin in skins:
						if not skin in char_data["connection"][s]:
							char_data["connection"][s].append(skin)

				for skin in skins:
					if not skin in char_data["skins"]:
						char_data["skins"].append(skin)

				models = properties_data.get("models", "")
				if models:
					for model in models.split(" "):
						char_data["models"].append(model)
						if models_index <= int(model):
							models_index = model + 1
				elif not len(char_data["models"]):
					char_data["models"].append(str(models_index))
					models_index += 1


	return char_data_list



def main(target_entity_type_list):
	entity_properties_path_dict = search_entity_properties_path(target_entity_type_list)

	for target_entity_type in target_entity_type_list:
		print()
		print(f"{target_entity_type} - 開始掃描random文件夾內的properties檔")
			
		entity_properties_path = entity_properties_path_dict[target_entity_type]
		if not entity_properties_path:
			print(f"{target_entity_type} - 未找到properties檔, 略過此生物")
			continue

		entity_properties_data_list = get_entity_properties_data(entity_properties_path)

		character_data_list = get_character_data(entity_properties_data_list)
		if not character_data_list:
			print(f"{target_entity_type} - 未找到角色資料, 略過此生物")
			continue
		write_json(get_data_dir_file_path("connection", target_entity_type+"-properties"), entity_properties_data_list)
		write_json(get_data_dir_file_path("connection", target_entity_type+"-character"), character_data_list)

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)