from tool import *
import time
import numpy
from PIL import Image

img = None

def open_img(path):
	global img
	img = numpy.array(Image.open(path))

def get_img_path_list(entity_type_list):
	img_type = str_list_to_list(get_config("image", "type"))

	img_path_list = {}
	for entity_type in entity_type_list:
		img_path_list[entity_type] = []

	dir = os.path.join(get_config("dir_path", "optifine"), "random")
	for root, dirs, files in os.walk(dir):
		is_entity_type_dir = ""

		for entity_type in entity_type_list:
			if entity_type in root:
				is_entity_type_dir = entity_type
				break

		for file in files:
			if check_path_extension(file, img_type):
				if is_entity_type_dir:
					is_entity_type = is_entity_type_dir
				else:
					is_entity_type = get_entity_type_for_img(file, entity_type_list)
					if not is_entity_type:
						continue

				path = os.path.join(root, file)
				img_path_list[is_entity_type].append(path)

	return img_path_list

def get_entity_type_for_img(file, entity_type_list):
	for entity_type in entity_type_list:
		if entity_type in file:
			return entity_type
	return ""

def check_img_model(entity_type_list, img_path_list):
	check_entity_type_list = get_check_entity_type_list(entity_type_list)
	if not len(check_entity_type_list):
		print("所有圖片的生物模型已掃描,需要重新掃描嗎?(y/N)")

		if userConfirm():
			check_entity_type_list = entity_type_list
		else:
			return

	t = time.time()

	entity_type_len = len(check_entity_type_list)
	entity_type_count = 0
	for entity_type in check_entity_type_list:
		entity_type_count += 1

		data = read_json(os.path.join(optifine_dir, "cem", f"{entity_type}.jem"))
		
		img_models = {}

		img_len = len(img_path_list[entity_type])
		img_count = 0
		for img_path in img_path_list[entity_type]:
			img_count += 1
			
			img_name = os.path.basename(img_path)

			open_img(img_path)
			id_list = process_models(data["models"])
			img_models[img_name] = id_list

			print(f"{entity_type_count}/{entity_type_len}: {entity_type} {img_count}/{img_len}: {img_name}")
		
		write_json(get_data_dir_file_path("img_models", entity_type), img_models)

	print(f"掃描完成, 耗時{int(time.time() - t)}秒")
	
def get_check_entity_type_list(entity_type_list):
	check_entity_type_list = []
	listdir = os.listdir(os.path.join(get_config("dir_path", "data"), "img_models"))
	for entity_type in entity_type_list:
		if not f"{entity_type}.json" in listdir:
			check_entity_type_list.append(entity_type)
	return check_entity_type_list

def process_models(data_list):
	id_list = {}
	for data in data_list:
		d = {}

		submodels = data.get("submodels")
		if submodels:
			d["submodels"] = process_models(submodels)

		d["boxes"] = process_boxes(data.get("boxes", {}))

		if d["boxes"] or len(d.get("submodels", {})):
			id_list[data["id"]] = d

	return id_list

def process_boxes(boxes):
	for box in boxes:
		for i in box:
			if "uv" in i:
				if check_color(box[i]):
					return True
	return False

def check_color(box):
	minY = round(min(box[0], box[2]))
	maxY = round(max(box[0], box[2]))
	minX = round(min(box[1], box[3]))
	maxX = round(max(box[1], box[3]))

	return img[minX:maxX, minY:maxY].any()

def main(target_entity_type_list):
	img_path_list = get_img_path_list(target_entity_type_list)

	print()
	print("開始掃描圖片所需的生物模型, 需時可能較長, 請勿關閉")
	check_img_model(target_entity_type_list, img_path_list)

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)