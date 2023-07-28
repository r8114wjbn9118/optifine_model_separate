from tool import *
import numpy
from PIL import Image

ANIM_IMG_DATA = [
	{
		"x": [9],
		"y": [12, 15, 12],
		"w": [1],
		"h": [4, 1, 1]
	},
	{
		"x": [14],
		"y": [12, 15, 12],
		"w": [1],
		"h": [4, 1, 1]
	}
]

ANIM_PROPERITES_DATA = [
	{"x": 9, "y": 12, "w": 1, "h": 3},
	{"x": 14, "y": 12, "w": 1, "h": 3}
]

reduce_image = False
img_dir = os.path.join(optifine_dir, "random", "entity")

def set_reduce_image(bool):
	global reduce_image
	reduce_image = bool

def get_img_path_simple_search(entity_type):
	img_type = get_config("image", "type")
	img_type = convert_config_str(img_type)
	
	file_list = []

	dir = os.path.join(img_dir, entity_type)
	for file in os.listdir(dir):
		if check_path_extension(file, img_type):
			for path in file_list:
				if file == os.path.basename(path):
					continue
			name = os.path.splitext(file)[0]
			r = re.match(entity_type, name)
			if r:
				file_list.append(file)
	return file_list

def get_img_path(entity_type):
	img_type = get_config("image", "type")
	img_type = convert_config_str(img_type)
	
	file_list = []

	dir = os.path.join(img_dir, entity_type)
	for root, dirs, files in os.walk(dir):
		for file in files:
			if check_path_extension(file, img_type):
				for path in file_list:
					if file == os.path.basename(path):
						continue
				name = os.path.splitext(file)[0]
				r = re.match(entity_type, name)
				if r:
					file_list.append(os.path.relpath(os.path.join(root,file), dir))
	return file_list

def generate_image(entity_type, img_filename, img_dict):
	anim_img_name_list = []

	for data_index in range(len(ANIM_IMG_DATA)):
		filename = os.path.basename(img_filename)
		order = data_index + 1

		data = ANIM_IMG_DATA[data_index]
		x_list = data["x"]
		y_list = data["y"]
		w_list = data["w"]
		h_list = data["h"]

		# 開啟原始圖片
		with Image.open(os.path.join(img_dir, entity_type, img_filename)) as original_img:
			merged_img = Image.new("RGB", (sum(w_list), sum(h_list)))
			x_offset = 0
			y_offset = 0
			for (x, w) in list(zip(x_list, w_list)):
				for (y, h) in list(zip(y_list, h_list)):
					# 裁剪並保存為對應的圖片
					cropped_img = original_img.crop((x, y, x + w, y + h))
					merged_img.paste(cropped_img, (x_offset, y_offset))

					y_offset += h
				x_offset += w

		if reduce_image:
			merged_img_np = numpy.array(merged_img)
			existed = False
			for img_name in img_dict:
				img = img_dict[img_name]
				if (merged_img_np == img).all():
					filename = img_name
					existed = True
					break
			else:
				print(img_filename)
				splitext = os.path.splitext(img_filename)
				filename = f"{entity_type}{len(img_dict)+1}{splitext[1]}"
				img_dict[filename] = merged_img_np

			anim_img_name_list.append(filename)
			
			if existed:
				continue

		else:
			# 合併三張裁剪後的圖片並儲存
			if order > 1:
				splitext = os.path.splitext(filename)
				filename = f"{splitext[0]}_{order}{splitext[1]}"
			anim_img_name_list.append(filename)

		output_path = get_data_dir_file_path("anim", filename, type=entity_type)
		merged_img.save(output_path)

	return img_dict, anim_img_name_list

def generate_properties(entity_type, img_filename, anim_img_name_list):
	template_path = get_data_dir_file_path("anim", f"{entity_type}-template.properites")
	while not os.path.isfile(template_path):
		print(f"{entity_type} - 缺少模板, 請在以下文件夾生成 {entity_type}-template.properites 檔")
		print(os.path.dirname(template_path))
		print("按enter重新讀取或按下右上角按鈕關閉")
		input()
	template = read_file(template_path)
	
	for data_index in range(len(ANIM_PROPERITES_DATA)):
		data = ANIM_PROPERITES_DATA[data_index]
		order = data_index + 1

		s_l = []
		s_l.append(f"from=./{anim_img_name_list[data_index]}")
		s_l.append(f"to=optifine/random/entity/{entity_type}/{img_filename}")
		s_l.append("x={}".format(data["x"]))
		s_l.append("y={}".format(data["y"]))
		s_l.append("w={}".format(data["w"]))
		s_l.append("h={}".format(data["h"]))
		
		s_l.append(template)

		output_path = os.path.splitext(os.path.basename(img_filename))[0]
		if order > 1:
			output_path += f"_{order}"
		output_path += ".properties"
		output_path = get_data_dir_file_path("anim", output_path, type=entity_type)
		write_file(output_path, "\n".join(s_l))
		
def main(target_entity_type_list):
	print("需要限制相同圖片的數量嗎? (Y/n)")
	set_reduce_image(userConfirm(True))

	for entity_type in target_entity_type_list:
		print(f"{entity_type} - 開始生成動畫")

		img_filename_list = get_img_path(entity_type)
		
		img_dict = {}
		for img_filename in img_filename_list:
			img_dict, anim_img_name_list = generate_image(entity_type, img_filename, img_dict)

			generate_properties(entity_type, img_filename, anim_img_name_list)
		print(len(img_dict))

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)