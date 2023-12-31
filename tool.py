#基礎設定#



"""
properties中models值的第一個數字
docs:https://optifine.readthedocs.io/cem_models.html#randomized-models
"""
#PROPERTIES_MODELS_FIRST_INDEX = 2

"""
properties中開始的N值
注意:optifine需求此數值必須為1
docs:https://optifine.readthedocs.io/random_entities.html#properties
"""
#PROPERTIES_FIRST_INDEX = 1

"""
角色後綴數字的數量
原來的properties文件中已經存在的後綴將會無視此數值
"""
#PROPERTIES_SUFFIX_COUNT = 0

import os
import sys
from configparser import ConfigParser
import re
import json

data_dir_name = "model_separate_data"



def make_config(config:object):
	config.read_dict(DEFALUT_CONFIG)
	set_config()

def open_config():
	return config.read("config.ini")

def set_config():
	with open('config.ini', 'w') as configfile:
		config.write(configfile)

def get_config(section:str, key:str):
	section = section.lower()
	key = key.lower()
	try:
		return config[section][key]
	except:
		return None

def userConfirm(default = False):
	try:
		s = input()
		if default and not s:
			return True
		return s[0].lower() == "y"
	except:
		return False

def get_root_dir():
	path = ""
	if not path or not "pack.mcmeta" in os.listdir(path):
		data_dir_split = os.path.abspath(os.getcwd()).split(os.sep)
		for i in range(len(data_dir_split)):
			if data_dir_split[i] == "resourcepacks":
				path = os.sep.join(data_dir_split[0:i + 2])
				break
	while not path or not "pack.mcmeta" in os.listdir(path):
		print("未找到resourcepack,請輸入位置")
		path = input()

	name = os.path.basename(path)
	print(f"resourcepack: {name}")

	return os.path.abspath(path)

def get_data_dir():
	for root, dirs, files in os.walk(root_dir):
		if data_dir_name in dirs:
			return os.path.abspath(os.path.join(root, data_dir_name))
	if data_dir_name in os.listdir(os.pardir):
		return os.path.abspath(os.path.join(os.pardir, data_dir_name))
	if not os.path.isdir(data_dir_name):
		os.mkdir(data_dir_name)
	return os.path.abspath(data_dir_name)

def get_data_dir_file_path(dir, filename, extension = "", type = ""):
	path = os.path.join(data_dir, dir)
	if type:
		path = os.path.join(path, type)
		if not os.path.isdir(path):
			os.mkdir(path)
	path = os.path.join(path, f"{filename}")

	if not extension:
		extension = get_data_dir_extension().get(dir)
	if extension is None:
		return path
	return path + "." + extension

def make_data_dir():
	for dir in get_data_dir_extension():
		if not dir in os.listdir(data_dir):
			os.mkdir(os.path.join(data_dir, dir))

def get_optifine_dir():
	return os.path.abspath(os.path.join(root_dir, "assets", "minecraft", "optifine"))

def get_data_dir_extension():
	return {
		"img_models":"json",
		"cem":"jem",
		"connection":"json",
		"char_models":"json",
		"parent_bones":"jem",
		"properties":"properties",
		"tsv":"tsv",
		"anim":None
		}


def convert_config_str(s:str):
	return json.loads(s.replace("'",'"'))


def check_path_extension(path, target):
	extension = os.path.splitext(path)[1]
	return extension[1:] in target


def read_json(path):
	return json.loads(read_file(path))
	
def read_file(path):
	with open(path, encoding="utf8") as file:
		return file.read()

def write_json(path, data):
	data = json.dumps(data, ensure_ascii=False, separators=(',',':'))
	write_file(path, data)

def write_file(path, data):
	with open(path, "w", encoding="utf8") as file:
			file.write(data)


def process_properties_list(properties_list):
	data_list = []

	for data in properties_list.split(" "):
		if not data:
			continue
		r = data.split("-")
		if len(r) == 2:
			minr = int(min(r))
			maxr = int(max(r))
			for i in range(minr, maxr + 1):
				data_list.append(str(i))
		else:
			data_list.append(data)
	return data_list





def get_target_entity_type(args:list = None):
	if args is None:
		args = sys.argv[1:]
	if args:
		target_entity_type_list = args
	else:
		entity_type_list = get_entity_type_list()
		target_entity_type_list = get_target(entity_type_list)
	return target_entity_type_list

def get_entity_type_list():
	dir = os.path.join(optifine_dir, "cem")

	entity_type_list = []
	for path in os.listdir(dir):
		if check_path_extension(path, "jem"):
			name = os.path.splitext(path)[0]
			name = re.findall("^([^\d]+)", name)[0]
			if name not in entity_type_list:
				entity_type_list.append(name)
	return entity_type_list

def get_target(entity_type_list):
	target_entity_type_list = []

	while not len(target_entity_type_list):
		print("選擇需要掃描的生物")
		for entity_type in entity_type_list:
			print(entity_type)
		print("輸入以上的生物名字, 或輸入'all'選擇所有")
		print("如需要選擇多個需以','隔開")

		select = input()
		select = select.lower().strip()
		if not select or select == "all":
			target_entity_type_list = entity_type_list
		else:
			select_list = select.split(",")
			for s in select_list:
				s = s.strip()
				if s in entity_type_list and not s in target_entity_type_list:
					target_entity_type_list.append(s)
	return target_entity_type_list

os.chdir(os.path.dirname(os.path.abspath(__file__)))

config = ConfigParser()
if open_config():
	root_dir = get_config("dir_path", "resourcepacks")
else:
	root_dir = get_root_dir()
print(f"resource pack: {root_dir}")

data_dir = get_data_dir()
optifine_dir = get_optifine_dir()

DEFALUT_CONFIG = {
	"dir_path": {
		"resourcepacks": root_dir
	},
	"image": {
		"type": ["jpg","png"]
	},
	"properties": {
		"name_regex": "\(?([^\(\)]*)\)?(?:-\(?([^\)]*)\)?)?",
		"model_first_index": 2,
		"first_index": 1,
		"suffix_count": 0
	}
}
make_config(config)

make_data_dir()
os.chdir(root_dir)