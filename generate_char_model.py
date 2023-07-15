from tool import *

def generate_char_model(entity_type, img_model_data, character_data_list):
	model_data = read_json(os.path.join(optifine_dir,"cem",f"{entity_type}.jem"))

	img_name_list = list(img_model_data.keys())
	img_name_index = {}
	for index in range(len(img_name_list)):
		name = os.path.splitext(img_name_list[index])[0]
		r = re.findall("(\d+)", name)
		if len(r):
			ini = r[0]
			if not isinstance(img_name_index, list):
				img_name_index[ini] = []
			img_name_index[ini].append(index)

	parent_bones_models = get_parent_bones_models(entity_type)
	
	for ci in range(len(character_data_list)):
		character_data = character_data_list[ci]
		if not character_data:
			continue
		character_name = character_data["name"][0]

		model_index = {}

		skins = character_data["skins"]
		for skin in skins:
			index_list = img_name_index[skin]
			for index in index_list:
				d = img_model_data[img_name_list[index]]
				update_models(model_index, d)

		write_json(get_data_dir_file_path("char_models", entity_type+"-"+character_name), model_index)
		#write_json(get_data_dir_file_path("cem", entity_type+(ci+1)), model_data)
		
		char_model_data = get_char_model_data(parent_bones_models, model_data, model_index)
		write_json(get_data_dir_file_path("cem", entity_type+character_data["models"][0]), char_model_data)
		
def get_parent_bones_models(entity_type):
	path = get_data_dir_file_path("parent_bones", entity_type)
	dir = os.path.dirname(path)
	while not os.path.isfile(path):
		print(f"{entity_type} - 缺少父骨骼, 請使用Blockbench生成該生物的jem檔放置到以下文件夾")
		print(dir)
		print("注意: 缺少父骨骼可能會讓optifine無法讀取模型")
		print("按enter重新讀取或按下右上角按鈕關閉")
		input()
	parent_bones_models = read_json(path)
	return parent_bones_models.get("models", {})

def update_models(data, update):
	for key in data:
		if key in update.keys():
			if len(update[key].get("submodels", {})):
				update_models(data[key]["submodels"], update[key]["submodels"])
			
			data[key]["boxes"] = (data[key]["boxes"] or data[key]["boxes"])
		 
	for key in update:
		if key not in data.keys():
			data[key] = update[key]

	return data

def get_char_model_data(parent_bones_models, model_data, model_index):
	char_model_data = {}

	for key in model_data:
		used_boxes_name_list = []
		if key == "models":
			char_model_data[key] = parent_bones_models
			data_list, used_boxes_name_list = get_char_model(model_data[key], model_index, used_boxes_name_list)

			char_model_list = char_model_data[key]
			for data in data_list:
				for char_model in char_model_list:
					if data.get("id") == char_model.get("id"):
						char_model.update(data)
		else:
			char_model_data[key] = model_data[key]

	return char_model_data

def get_char_model(model_data_dict, model_index_dict, used_boxes_name_list):
	char_model_data = []

	for index_key in model_index_dict:
		model_index = model_index_dict[index_key]

		for model_data in model_data_dict:
			if model_data["id"] == index_key:
				data = {}
				for data_key in model_data:
					if data_key == "submodels" and len(model_index[data_key]):
						data[data_key], used_boxes_name_list = (get_char_model(model_data[data_key], model_index[data_key], used_boxes_name_list))
					else:
						if data_key == "animations":
							continue
						if data_key == "boxes":
							if not model_index["boxes"]:
								continue
							else:
								used_boxes_name_list.append(index_key)
						data[data_key] = model_data[data_key]

				if model_data.get("animations"):
					data["animations"] = get_char_anim(model_data["animations"], used_boxes_name_list)

				if len(data):
					char_model_data.append(data)
	return char_model_data, used_boxes_name_list

def get_char_anim(anim_data_list, used_boxes_name_list):
	data = []
	for anim_data in anim_data_list:
		d = {}
		for key in anim_data:
			for boxes_name in used_boxes_name_list:
				if boxes_name in key:
					d[key] = anim_data[key]
		data.append(d)
	return data

def main(target_entity_type_list):
	for target_entity_type in target_entity_type_list:
		character_data_list = read_json(get_data_dir_file_path("connection", target_entity_type+"-character"))
		
		print(f"{target_entity_type} - 開始生成角色模型")

		img_model_data = read_json(get_data_dir_file_path("img_models", target_entity_type))
		generate_char_model(target_entity_type, img_model_data, character_data_list)

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)