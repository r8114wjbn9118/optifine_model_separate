from tool import *

TSV_FIRST_LINE_STR = ["角色","模組"]

def join_skins(skins):
	skins_list = []
	minr = 0
	maxr = 0

	skins.sort(key=lambda a:int(a) )
	for s in skins:
		n = int(s)
		if not minr:
			minr = n
			maxr = n
		elif n == maxr + 1:
			maxr = n
		else:
			if minr == maxr:
				skins_list.append(f"{str(minr)}")
			else:
				skins_list.append(f"{str(minr)}-{str(maxr)}")
			minr = n
			maxr = n
	if minr == maxr:
		skins_list.append(f"{str(minr)}")
	else:
		skins_list.append(f"{str(minr)}-{str(maxr)}")

	return " ".join(skins_list)


def write_weights_str(link_index, skins_str, weights_str = ""):
	str_list = []
	str_list.append(join_properties_skins_str(link_index, " ".join(skins_str)))

	w_s = join_weights_str(link_index, weights_str)
	if not weights_str:
		w_l = ["1" for i in skins_str]
		w_s += " ".join(w_l)
	str_list.append(w_s)
	return str_list

def join_properties_models_str(link_index, models_str):
	s = f"models.{link_index}={models_str}"
	return s

def join_properties_skins_str(link_index, skin_str):
	s = f"skins.{link_index}={skin_str}"
	return s

def join_properties_name_str(link_index, name, suffix = ""):
	s = f"name.{link_index}=iregex:"

	name_list = []
	for n in name:
		n_s = n
		if suffix:
			n_s += f"-{suffix}"
		name_list.append(n_s)
		
	s += "|".join(name_list)
	return s.encode("unicode_escape").decode("utf8")

def join_weights_str(link_index, weights_str):
	s = f"weights.{link_index}={weights_str}"
	return s

def join_properties_str(link_index, models_str, skin_str, name, suffix = ""):
	str_list = []
	str_list.append(join_properties_models_str(link_index, models_str))
	str_list.append(join_properties_skins_str(link_index, skin_str))
	str_list.append(join_properties_name_str(link_index, name, suffix))
	str_list.append("")

	return str_list


def sort_charactor_models_connection_key(keys):
	n_l = []
	s_l = []
	for key in keys:
		if key == "":
			continue
		try:
			value = int(key)
			n_l.append(value)
		except:
			s_l.append(key)

	n_l.sort()

	for i in range(len(n_l)):
		n_l[i] = str(n_l[i])

	return n_l + s_l

def join_charactor_models_connection(connection, keys):
	keys = sort_charactor_models_connection_key(keys)
	l = TSV_FIRST_LINE_STR
	for key in keys:
		if key == "0":
			l.append("all")
		else:
			l.append(key)
	str_list = []
	str_list.append("\t".join(l))
	for name in connection:
		data = connection[name]
		l = [name, data["models"]]
		for key in keys:
			l.append(data.get(key, ""))
		str_list.append("\t".join(l))

	return "\n".join(str_list)



def join_charactor_name(charactor_name_dict):
	str_list = []
	str_list.append("\t".join(TSV_FIRST_LINE_STR))
	for charactor_name in charactor_name_dict:
		name = charactor_name["name"][0]
		model = charactor_name["model"]

		l = [name, model]
		l += charactor_name["name"]

		str_list.append("\t".join(l))
	
	return "\n".join(str_list)

def process(entity_type, char_data_list):
	properties_path = get_data_dir_file_path("properties", f"{entity_type}")
	models_connection_path = get_data_dir_file_path("tsv", f"{entity_type}-models_connection")
	name_path = get_data_dir_file_path("tsv", f"{entity_type}-name")

	if os.path.isfile(properties_path) or os.path.isfile(models_connection_path) or os.path.isfile(name_path):
		if os.path.isfile(properties_path):
			print(f"{os.path.basename(properties_path)} 已存在")
		if os.path.isfile(models_connection_path):
			print(f"{os.path.basename(models_connection_path)} 已存在")
		if os.path.isfile(name_path):
			print(f"{os.path.basename(name_path)} 已存在")

		print("按enter覆蓋文件或按下右上角按鈕關閉")
		input()

	link_index = int(get_config("properties", "first_index"))
	suffix_count = int(get_config("properties", "suffix_count"))

	charactor_models_connection_key = []
	charactor_models_connection_dict = {}
	charactor_name_dict = []

	totle_skins_list = []

	data_str_list = []
	for data in char_data_list:
		if not data:
			continue

		skins = data["skins"]
		name = data["name"]
		connection = data["connection"]
		models = data["models"]

		models_str = " ".join(models)

		charactor_models_connection = {}
		charactor_models_connection["models"] = models_str
		charactor_models_connection["name"] = "|".join(name)

		charactor_name_dict.append({"name":name, "model":models_str})

		for skin in skins:
			if skin not in totle_skins_list:
				totle_skins_list.append(skin)

		used_connection = []
		for i in range(suffix_count+1):
			i_s = str(i)
			if i == 0:
				skin_str = join_skins(skins)
			elif connection.get(i):
				skin_str = join_skins(connection[i])
			else:
				skin_str = skins[0]

			data_str_list += join_properties_str(link_index, models_str, skin_str, name, i)
			link_index += 1
			used_connection.append(i_s)

			if i_s not in charactor_models_connection_key:
				charactor_models_connection_key.append(i_s)
			charactor_models_connection[i_s] = skin_str

		for ci in connection:
			if ci in used_connection:
				continue
			skin_str = join_skins(connection[ci])

			data_str_list += join_properties_str(link_index, models_str, skin_str, name, ci)
			link_index += 1

			if ci not in charactor_models_connection_key:
				charactor_models_connection_key.append(ci)
			charactor_models_connection[ci] = skin_str

		charactor_models_connection_dict[name[0]] = charactor_models_connection

		#data_str_list += join_properties_str(link_index, models_str, skin_str, name, "\\d{1,2}")
		#link_index += 1



	data_str_list += write_weights_str(link_index, totle_skins_list)




	write_file(properties_path, "\n".join(data_str_list))

	write_file(models_connection_path, join_charactor_models_connection(charactor_models_connection_dict, charactor_models_connection_key))

	write_file(name_path, join_charactor_name(charactor_name_dict))

	print("請檢查properties及tsv文件夾")

def main(target_entity_type_list):
	for entity_type in target_entity_type_list:
		print(f"{entity_type} - 開始生成properties檔")

		char_path = get_data_dir_file_path("connection", f"{entity_type}-character")
		char_data_list = read_json(char_path)
		process(entity_type, char_data_list)

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)