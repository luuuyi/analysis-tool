#! usr/bin/python
#  encoding=utf-8

import os, glob, shutil

obj_type_list = [u'person', u'car', u'truck', u'bus',u'tricycle']
merge_type_list = [u'car', u'truck', u'bus']
# obj_type_list = ["car"]
# merge_type_list = [u'car']
#obj_type_list = [u'car', u'truck', u'bus']
#merge_type_list = [u'car', u'truck', u'bus']
ignore_video_list = [u"00001_上海博物馆外国人_20150521", u"00002_上海博物馆中国人_20150521", u"00002_茶水间_20150522",
                     u"00001_园区大雪外景_20151022", u"00005_混行卡口场景三_20150521", u"00006_混行卡口场景三_20150521"]
dst_file = u".\\dst_file\\"
save_file = dst_file
FILTER_CONF = 0.5


def init_label_dict():
    obj_dict = {}
    for obj_type in obj_type_list:
        obj_dict[obj_type] = []
    return obj_dict


def single_obj_type_process(str_line, obj_type):
    inx = str_line.find(obj_type)
    str_list = str_line[inx:].split(" ")
    obj_num = int(str_list[1])
    obj_info_list = []

    for i in xrange(obj_num):
        start_rect_inx = 2 + 5 * i
        conf = float(str_list[start_rect_inx])
        if conf >= FILTER_CONF:
            rect_info = str_list[start_rect_inx + 1:start_rect_inx + 5]
            rect_info.append(str_list[start_rect_inx])
            obj_info_list.append(rect_info)
    return obj_info_list


def save_obj_type_result(pic_name, obj_dict, txt_name):
    for obj_type in obj_type_list:
        # if obj_type != u"person":
        #     break
        with open(save_file + obj_type + txt_name, "a+") as f:
            num_name = str(len(obj_dict[obj_type])) + " " + pic_name
            f.write(num_name)
            f.write("\n")
            for i in xrange(int(len(obj_dict[obj_type]))):
                rect_info = " ".join(obj_dict[obj_type][i])
                f.write(rect_info)
                f.write("\n")


def save_merge_type_result(pic_name, obj_dict, txt_name):
    merge_type_num = 0
    merge_type_info_list = []
    for obj_type in merge_type_list:
        merge_type_num += int(len(obj_dict[obj_type]))
        for i in xrange(len(obj_dict[obj_type])):
            merge_type_info_list.append(obj_dict[obj_type][i])
    with open(save_file + txt_name, "a+") as f:
        num_name = str(merge_type_num) + " " + pic_name
        f.write(num_name)
        f.write("\n")
        for i in xrange(len(merge_type_info_list)):
            rect_info = " ".join(merge_type_info_list[i])
            f.write(rect_info)
            f.write("\n")


def single_pic_result_process(str_line):
    str_line = str_line.strip()
    str_list = str_line.split(" ")
    pic_name = str_list[0]
    obj_dict = init_label_dict()

    for obj_type in obj_type_list:
        obj_dict[obj_type] = single_obj_type_process(str_line.decode("gb2312"), obj_type)
    save_obj_type_result(pic_name, obj_dict, "_total_result.txt")
    save_merge_type_result(pic_name, obj_dict, "vehicle_total_result.txt")
    video = pic_name[0:pic_name.rfind("_")].decode("gb2312")

    # b_ignore = False
    # for ignore_video in ignore_video_list:
    #     if video == ignore_video:
    #         b_ignore = True
    # if not b_ignore:
    #     txt_name = "_total_result" + str(62 - len(ignore_video_list)) + ".txt"
    #     save_obj_type_result(pic_name, obj_dict, txt_name)
    #     txt_name = "vehicle_total_result" + str(62 - len(ignore_video_list)) + ".txt"
    #     save_merge_type_result(pic_name, obj_dict, txt_name)


if __name__ == '__main__':
    src_file = u".\\detect_result\\"

    if os.path.exists(dst_file):
        shutil.rmtree(dst_file)
    if not os.path.exists(dst_file):
        os.mkdir(dst_file)

    txt_list = glob.glob(os.path.join(src_file, "*txt"))
    for txt in txt_list:
        txt_name = txt.strip().split("\\")[-1][:-4]
        print txt_name
        save_file = dst_file + txt_name + "\/"
        os.mkdir(save_file)
        for str_line in open(txt, "r").readlines():
            single_pic_result_process(str_line)













