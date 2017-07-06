#! usr/bin/python
#  encoding=utf-8

import os,glob,shutil

dst_file = u'.\\detect_result\\'

obj_type_list = ["bus", "car", "person", "truck","tricycle"]
#obj_type_list = ["car"]
#obj_type_list = ["bus", "car", "truck"]
filter_info_list = [u"00001_园区东北角快球_CVR_SEQNBR871_20150804"]
filter_rect = [0, 0, 650, 560]


def get_area_overlap(rect):
    common_rect = [max(rect[0], filter_rect[0]), max(rect[1], filter_rect[1]),
                   min(rect[2], filter_rect[2]), min(rect[3], filter_rect[3])]
    over_w = int(common_rect[2]) - int(common_rect[0])
    over_h = int(common_rect[3]) - int(common_rect[1])
    if over_w > 0 and over_h > 0:
        return True
    else:
        return False


def filter_str_context(obj_info):
    filter_str = []
    for i in xrange(len(obj_info)):
        if i < 2:
            filter_str.append(obj_info[i])
        else:
            rect = obj_info[i].split(" ")
            overlap = get_area_overlap(rect[1:])
            if not overlap:
                filter_str.append(obj_info[i])
    filter_str[1] = str(len(filter_str) - 2)
    return " ".join(filter_str)


def get_filter_str_line(str_line):
    filter_str_line = []
    jpg_inx = str_line.find(".jpg")
    pic_name = str_line[0:jpg_inx + 4]
    filter_str_line.append(pic_name)
    for i in xrange(len(obj_type_list)):
        obj_info = []
        obj_inx = str_line.find(obj_type_list[i])
        str_left = str_line[obj_inx:].split(" ")
        obj_num = str_left[1]
        obj_info.append(obj_type_list[i])
        obj_info.append(obj_num)
        i = 0
        while i < int(obj_num):
            temp = " ".join(str_left[2 + i * 5 + j] for j in xrange(5))
            obj_info.append(temp)
            i += 1
        obj_info_filter = filter_str_context(obj_info)
        filter_str_line.append(obj_info_filter)
    return filter_str_line


def filter_txt_context(txt):
    print txt
    dst_txt = dst_file + txt.split(u"\\")[-1][:-4] + ".txt"
    for str_line in open(txt, 'r').readlines():
        for filter_info in filter_info_list:
            if filter_info in str_line.decode("gb2312"):
                filter_str_line = get_filter_str_line(str_line)
                str_line = " ".join(filter_str_line)
        with open(dst_txt, "a+") as f:
            f.write(str_line.strip() + "\n")


if __name__ == '__main__':
    src_file = u".\\src_txt\\"

    if os.path.exists(dst_file):
        shutil.rmtree(dst_file)
    os.mkdir(dst_file)

    src_txt_list = glob.glob(os.path.join(src_file, '*.txt'))

    for txt in src_txt_list:
        filter_txt_context(txt)