from tool import *
from PIL import Image

ANIM_DATA = [
	{
		"x": 9,
		"y": [12, 15, 12],
		"w": 1,
		"h": [4, 1, 1]
	},
	{
		"x": 14,
		"y": [12, 15, 12],
		"w": 1,
		"h": [4, 1, 1]
	}
]

def get_img_path(entity_type):
	img_type = get_config("image", "type")
	img_type = convert_config_str(img_type)
	
	path_list = []
	print(f"{entity_type} - 開始生成動畫")

	dir = os.path.join(optifine_dir, "random")
	for root, dirs, files in os.walk(dir):
		for file in files:
			if check_path_extension(file, img_type):
				name = os.path.splitext(file)[0]
				r = re.match(entity_type, name)
				if r:
					path_list.append(os.path.relpath(os.path.join(root,file), dir))
	return path_list

def crop_image(entity_type, img_path):
	for data_index in range(len(ANIM_DATA)):
		order = data_index + 1

		data = ANIM_DATA[data_index]
		x = data["x"]
		y = data["y"]
		w = data["w"]
		h = data["h"]

		# 開啟原始圖片
		with Image.open(os.path.join(optifine_dir, "random", img_path)) as img:
			merged_img = Image.new("RGB", (w, sum(h)))
			y_offset = 0
			for i, (y, h) in enumerate(zip(y, h)):
				# 裁剪並保存為對應的圖片
				cropped_img = img.crop((x, y, x + w, y + h))
				merged_img.paste(cropped_img, (0, y_offset))
				y_offset += cropped_img.size[1]
			
			# 合併三張裁剪後的圖片並儲存
			filename = os.path.basename(img_path)
			if order > 1:
				splitext = os.path.splitext(filename)
				filename = f"{splitext[0]}_{order}{splitext[1]}"
			output_path = get_data_dir_file_path("anim", filename, type=entity_type)
			merged_img.save(output_path)

def generate_properties(entity_type, img_path):
	data_list = [
		{"x": 9, "y": 12, "w": 1, "h": 3},
		{"x": 14, "y": 12, "w": 1, "h": 3}
	]

	template_path = get_data_dir_file_path("anim", f"{entity_type}-template.properites")
	while not os.path.isfile(template_path):
		print(f"{entity_type} - 缺少模板, 請在以下文件夾生成 {entity_type}-template.properites 檔")
		print(os.path.dirname(template_path))
		print("按enter重新讀取或按下右上角按鈕關閉")
		input()
	template = read_file(template_path)
	
	for data_index in range(len(data_list)):
		data = data_list[data_index]
		order = data_index + 1

		dir, filename = os.path.split(img_path)
		if order > 1:
			splitext = os.path.splitext(filename)
			filename = f"{splitext[0]}_{order}{splitext[1]}"
		dir = dir.replace(os.sep, "/")

		s_l = []
		s_l.append(f"from=./{filename}")
		s_l.append(f"to=optifine/random/{dir}/{filename}")
		s_l.append("x={}".format(data["x"]))
		s_l.append("y={}".format(data["y"]))
		s_l.append("w={}".format(data["w"]))
		s_l.append("h={}".format(data["h"]))
		
		s_l.append(template)

		output_path = os.path.splitext(filename)[0] + ".properties"
		output_path = get_data_dir_file_path("anim", output_path, type=entity_type)
		write_file(output_path, "\n".join(s_l))
		
def main(target_entity_type_list):
	for entity_type in target_entity_type_list:
		img_path_list = get_img_path(entity_type)
		for img_path in img_path_list:
			print(f"{entity_type} - 開始生成動畫圖片")
			crop_image(entity_type, img_path)

			print(f"{entity_type} - 開始生成動畫properties檔")
			generate_properties(entity_type, img_path)

if __name__ == "__main__":
	target_entity_type_list = get_target_entity_type()
	main(target_entity_type_list)