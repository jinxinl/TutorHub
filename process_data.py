import os
import re
import json


def getTutorID():
    tutorID_dict = {}
    folder_path = 'dataset\\raw\\TutorBasic'
    count = 1
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path,file)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()  # 去除行末的换行符
                if line == "":
                    continue
                separator_pattern = r'[:：]'  # 使用冒号分割每行的键值对
                tmp_key, tmp_value = re.split(separator_pattern, line, maxsplit=1)

                key = re.sub(r'\s+', '', tmp_key)
                value = re.sub(r'\s+', '', tmp_value)

                if key == '姓名':
                    tutorID_dict[f'{value}'] = count
                    count += 1
                    break

    return tutorID_dict

def prepare_data(folder_path='', file_name=''):
    data_list = []
    if folder_path != '':
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                elem_dict = {}
                for line in f:
                    line = line.strip()  # 去除行末的换行符
                    if line == "":
                        continue
                    separator_pattern = r'[:：]'  # 使用冒号分割每行的键值对
                    tmp_key, tmp_value = re.split(separator_pattern, line, maxsplit=1)

                    key = re.sub(r'\s+', '', tmp_key)
                    value = re.sub(r'\s+', '', tmp_value)

                    if key =='姓名':
                        key = 'Name'
                    if key == '职称':
                        key = 'Title'
                    if key == '学科':
                        continue
                    if key == '专业':
                        key = 'Major'
                    if key == '研究方向':
                        key = 'Field'
                    if key == '导师类型':
                        continue
                    if key == '电子邮件':
                        key = 'Email'
                    if key == '联系电话':
                        key = 'Phone'
                        if value =='':
                            value = ''
                    if key == '通讯地址':
                        continue
                    if key == '个人简介':
                        key = 'Introduction'

                    # 保存键值对信息
                    if key == "Introduction":
                        value1 = value
                        for pattern in [r'</.*?>', r'<.*?>']:
                            value = re.sub(pattern, '', value1)
                            value1 = value

                    if key == 'Name' or key == 'Title' or key == 'Major' or key == 'Field' or key == 'Phone' or key == 'Email' or key == 'Introduction':
                        elem_dict[key] = value
                    elem_dict['School'] = '同济大学'

            data_list.append(elem_dict)

        return data_list

    elif file_name != '':
        with open(file_name, 'r', encoding='utf-8') as f:
            data_dict = {}
            for line in f.readlines():
                line = line.strip()
                line = line.replace('(', '')
                line = line.replace(')', '')

                target, _, name = line.split(',')
                if target != 'none' and name != 'none':
                    if target not in data_dict.keys():
                        data_dict[target] = [name]
                    else:
                        if name not in data_dict[target]:
                            data_dict[target].append(name)

        return data_dict

# 将txt合并为json文件
def convert_to_json():
    # 导师基本信息
    tutor_basic_list = prepare_data(folder_path='dataset\\raw\\TutorBasic')
    print(tutor_basic_list)

    with open('dataset/processed/TutorBasic.json', 'w', encoding='utf-8') as f:
        json.dump(tutor_basic_list, f, indent=4, ensure_ascii=False)


    # 导师毕业学校信息
    alumni_dict = prepare_data(file_name='dataset\\raw\\AlumniRelationSet.txt')
    print(alumni_dict)
    with open('dataset/processed/AlumniRelation.json', 'w', encoding='utf-8') as f:
        json.dump(alumni_dict, f, indent=4, ensure_ascii=False)


    # 师承信息
    tutor_dict = prepare_data(file_name='dataset\\raw\\TutorRelationSet.txt')
    print(tutor_dict)
    
    with open('dataset/processed/TutorRelation.json', 'w', encoding='utf-8') as f:
        json.dump(tutor_dict, f, indent=4, ensure_ascii=False)
