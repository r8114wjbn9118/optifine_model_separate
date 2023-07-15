from tool import *
import generate_properties

def main(entity_type_list):
	output_dir = os.path.join(data_dir, "properties")
	
	for entity_type in entity_type_list:
		data_dict = {}

		models_path = get_data_dir_file_path("tsv", f"{entity_type}-models_connection")
		models_data_list = read_file(models_path).split("\n")
		for i in range(len(models_data_list)):
			models_data_list[i] = models_data_list[i].split("\t")

		name_path = get_data_dir_file_path("tsv", f"{entity_type}-name")
		name_data_list = read_file(name_path).split("\n")
		for i in range(len(name_data_list)):
			name_data_list[i] = name_data_list[i].split("\t")

		suffix_list = models_data_list[0][3:]
		for models_data_index in range(1, len(models_data_list)):
			models_data = models_data_list[models_data_index]
			d = {}
			d["models"] = process_properties_list(models_data[1])
			d["skins"] = process_properties_list(models_data[2])
			d["connection"] = {}
			i = 3
			for suffix in suffix_list:
				skins = process_properties_list(models_data[i])
				if not skins:
					continue
				d["connection"][suffix] = skins
				for skin in skins:
					if skin not in d["skins"]:
						d["skins"].append(skin)
				
				i += 1
			data_dict[models_data[0]] = d
			
		for i in range(1, len(name_data_list)):
			name_data = name_data_list[i]
			data_dict[name_data[0]]["name"] = name_data[2:]

		char_data_list = []
		for key in data_dict:
			char_data_list.append(data_dict[key])
		generate_properties.process(entity_type, char_data_list)


if __name__ == "__main__":
	target_entity_type_list = ["wolf"]
	#target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)