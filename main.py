from tool import *
import scan_image_model
import scan_entity_properties
import generate_char_model
import generate_properties
import tsv_to_properties


def close_entity_type_list(target_entity_type_list):
	set_entity_type_list(None)

def get_entity_type_list():
	set_entity_type_list(get_target_entity_type())

def set_entity_type_list(value):
	global entity_type_list
	entity_type_list = value


def all(target_entity_type_list):
	scan_image_model.main(target_entity_type_list)

	scan_entity_properties.main(target_entity_type_list)

	generate_char_model.main(target_entity_type_list)

	generate_properties.main(target_entity_type_list)

def main():
	while True:
		if not entity_type_list:
			get_entity_type_list()

		print()
		print("0.重新選擇生物")
		print("1.all")
		print("2.掃描圖片使用的模型")
		print("3.掃描properties檔")
		print("4.生成角色模型")
		print("5.生成properties檔及tsv檔")
		print("6.轉換tsv檔為properties檔")
		print("輸入數字以選擇行動")

		try:
			i = int(input())
		except:
			i = -1
		
		if not i == -1:
			action[i](entity_type_list)
			print("執行完成")
			print("")

action = [
	close_entity_type_list,
	all,
	scan_image_model.main,
	scan_entity_properties.main,
	generate_char_model.main,
	generate_properties.main,
	tsv_to_properties.main
	]

entity_type_list = None

if __name__ == "__main__":
	main()