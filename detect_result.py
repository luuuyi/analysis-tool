#! usr/bin/python
# encoding=utf8

import os, glob, shutil, sys

dst_file = u"./dst_recall_pre_result/"
hms_video_type = u"./bin/HMS_Video_Type.txt"
g_scene_csv_file = ""
g_video_csv_file = ""
g_fp_pic_info_csv_file = ""
global g_model_name
g_model_name = ""
global g_gt_obj_size_list
g_gt_obj_size_list = []
OVERLAP = 0.5
#g_conf_list = [0.5, 0.6, 0.7, 0.725, 0.75, 0.775, 0.8, 0.85, 0.9]
#g_label_size_category = [15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 300]
#g_fppi_category = [0.1, 0.2, 0.3, 0.4, 0.5]
g_conf_list = [ 0.8,0.9]
g_label_size_category = [15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 300]
g_fppi_category = [0.1, 0.2]
#g_fppi_category = [0.1, 0.2, 0.3, 0.4, 0.5]
g_scene_dict = {}


def init_csv_file(file_path):
    global g_scene_csv_file
    g_scene_csv_file = file_path + "scene_pre_recall.csv"
    with open(g_scene_csv_file, "a+") as f:
        save_str = u"模型, 置信度, 置信度大小, 目标大小, 场景类型, Gt_num, Det_num, 正检数目, 误检数目, recall, precision\n"
        f.write(save_str.encode("gb2312"))

    global g_video_csv_file
    g_video_csv_file = file_path + "video_pre_recall.csv"
    with open(g_video_csv_file, "a+") as f:
        save_str = u"模型, 置信度, 置信度大小, 目标大小, 视频名称, Gt_num, Det_num, 正检数目, 误检数目, recall, precision\n"
        f.write(save_str.encode("gb2312"))

    global g_fp_pic_info_csv_file
    g_fp_pic_info_csv_file = file_path + "fp_pic_info.csv"
    with open(g_fp_pic_info_csv_file, "a+") as f:
        save_str = u"模型, 视频名称, 视频帧号, 错误数目\n"
        f.write(save_str.encode("gb2312"))


def init_video_type_dict():
    global g_scene_dict
    if not os.path.exists(hms_video_type):
        print "Can't find ./HMS_Video_Type.txt!"
        exit(0)
    for str_line in open(hms_video_type, "r").readlines():
        str_line = str_line.strip().split(" ")
        if not g_scene_dict.has_key(str_line[0]):
            g_scene_dict[str_line[0]] = []
        g_scene_dict[str_line[0]].append(str_line[1])
    return g_scene_dict


def get_label_result(file_list, obj_type):
    label_result_dict = {}
    for txt_file in file_list:
        if not txt_file.split("\\")[-1].startswith(obj_type):
            continue
        for str_line in open(txt_file, "r").readlines():
            str_line_list = str_line.strip().split(" ")
            pic_name = str_line_list[0]
            obj_num = int(str_line_list[1])
            label_result_dict[pic_name] = []
            if 0 < obj_num:
                for i in xrange(obj_num):
                    start = 3 + 5 * i
                    obj_info = " ".join(str_line_list[start:start + 4])
                    label_result_dict[pic_name].append(obj_info)
    return label_result_dict


def get_detect_result(txt_file):
    detect_result_dict = {}
    total_det_pic_num = 0
    pic_name = ""
    for str_line in open(txt_file, "r").readlines():
        if ".jpg" in str_line:
            pic_name = str_line.strip().split(" ")[-1]
            detect_result_dict[pic_name] = []
            total_det_pic_num += 1
        else:
            detect_result_dict[pic_name].append(str_line.strip())
    return total_det_pic_num, detect_result_dict


def compute_overlap_objs(det_rect, label_rect):
    det_rect = det_rect.split(" ")
    label_rect = label_rect.split(" ")

    det_x1, det_y1, det_x2, det_y2 = int(det_rect[0]), int(det_rect[1]), int(det_rect[2]), int(det_rect[3])
    label_x1, label_y1 = int(label_rect[0]), int(label_rect[1])
    label_x2, label_y2 = int(label_rect[2]), int(label_rect[3])
    common_rect = [max(det_x1, label_x1), max(det_y1, label_y1),
                   min(det_x2, label_x2), min(det_y2, label_y2)]
    over_w = int(common_rect[2]) - int(common_rect[0]) + 1
    over_h = int(common_rect[3]) - int(common_rect[1]) + 1
    if over_w > 0 and over_h > 0:
        common_area = over_w * over_h
        merge_area = (det_x2 - det_x1 + 1) * (det_y2 - det_y1 + 1) +\
                     (label_x2 - label_x1 + 1) * (label_y2 - label_y1 + 1) - common_area
        over_lap = float(common_area) / merge_area
        return over_lap
    else:
        return 0


def compute_per_obj_info(detect_list, label_list):
    match_list = []
    pos_list = []
    neg_list = []
    for i in xrange(len(detect_list)):
        max_overlap = -1
        max_inx = -1
        for j in xrange(len(label_list)):
            overlap = compute_overlap_objs(detect_list[i], label_list[j])
            if overlap > OVERLAP:
                max_overlap = overlap
                max_inx = j
        if max_overlap != -1:
            if not max_inx in match_list:
                obj_info = detect_list[i] + " " + label_list[max_inx]
                match_list.append(max_inx)
                pos_list.append(obj_info)
            else:
                neg_list.append(detect_list[i])
        else:
            neg_list.append(detect_list[i])
    return pos_list, neg_list


def get_match_result(label_dict, detect_dict):
    match_dict = {}
    no_match_dict = {}
    for i in xrange(len(label_dict)):
        obj_name = label_dict.keys()[i]
        if not detect_dict.has_key(obj_name):
            continue
        pos_list, neg_list = compute_per_obj_info(detect_dict[obj_name], label_dict[obj_name])
        match_dict[obj_name] = pos_list
        no_match_dict[obj_name] = neg_list
    return match_dict, no_match_dict


def get_fppi_conf_list_by_fppi(no_match_dict, pic_num):
    global g_fppi_category
    neg_conf_list = []
    conf_list = []

    for value_list in no_match_dict.values():
        for value in value_list:
            conf = float(value.split(" ")[-1])
            neg_conf_list.append(conf)

    neg_conf_list = sorted(neg_conf_list, reverse=True)
    for value in g_fppi_category:
        inx = min(int(value * pic_num), len(neg_conf_list) - 1)
#        print(pic_num)
#        print(inx)
#        print("\n")
#        print(len(neg_conf_list))
#        print("\n")
        conf_list.append(neg_conf_list[inx])
    return conf_list


def get_gt_obj_size_list():
    global g_label_size_category
    obj_size_list = []
    for i in xrange(len(g_label_size_category)):
        if i == 0:
            obj_size_list.append(u"全部目标")
            obj_size_list.append(u"0--" + str(g_label_size_category[0]))
        else:
            size_name = str(g_label_size_category[i - 1]) + u"--" + str(g_label_size_category[i])
            obj_size_list.append(size_name)
    size_name = u"大于" + str(g_label_size_category[i])
    obj_size_list.append(size_name)
    return obj_size_list


def get_tp_gt_num_process(result_dict, min_size, max_size, conf_value=-1):
    tp_gt_num_dict = {}
    for pic_name in result_dict.keys():
        inx = pic_name.rfind("/")
        video_name = pic_name[:inx]
        if not tp_gt_num_dict.has_key(video_name):
            tp_gt_num_dict[video_name] = 0
        obj_list = result_dict[pic_name]
        for obj in obj_list:
            rect = obj.split(" ")

            # 根据conf，判断是提取tp_num还是gt_num
            if conf_value != -1:
                start_inx = 5
                if float(rect[4]) < conf_value:
                    continue
            else:
                start_inx = 0
            x1, y1 = int(rect[start_inx]), int(rect[start_inx + 1])
            x2, y2 = int(rect[start_inx + 2]), int(rect[start_inx + 3])
            if min_size < x2 - x1 <= max_size:
                tp_gt_num_dict[video_name] += 1
    return tp_gt_num_dict


def get_fp_num_process(result_dict, conf_value):
    tp_gt_num_dict = {}
    for pic_name in result_dict.keys():
        inx = pic_name.rfind("/")
        video_name = pic_name[:inx]
        if not tp_gt_num_dict.has_key(video_name):
            tp_gt_num_dict[video_name] = 0
        obj_list = result_dict[pic_name]
        for obj in obj_list:
            rect = obj.split(" ")
            if conf_value <= float(rect[4]):
                tp_gt_num_dict[video_name] += 1
    return tp_gt_num_dict


def video_pre_recall_process(match_result_dict, no_match_result_dict, label_result_dict, conf, inx):
    video_pre_recall_list = []

    if inx == 0:              # 全部目标
        min_size = 0
        max_size = 10000
    elif inx == 1:            #
        min_size = 0
        max_size = g_label_size_category[inx - 1]
    elif inx == len(g_label_size_category) + 1:
        min_size = g_label_size_category[inx - 2]
        max_size = 10000
    else:
        min_size = g_label_size_category[inx - 2]
        max_size = g_label_size_category[inx - 1]
    # video_name, gt_num, tp_num, fp_num
    gt_num_dict = get_tp_gt_num_process(label_result_dict, min_size, max_size)
    tp_num_dict = get_tp_gt_num_process(match_result_dict, min_size, max_size, conf)
    fp_num_dict = get_fp_num_process(no_match_result_dict, conf)
    video_pre_recall_list.append(gt_num_dict)
    video_pre_recall_list.append(tp_num_dict)
    video_pre_recall_list.append(fp_num_dict)
    return video_pre_recall_list


def scene_pre_recall_process(video_pre_recall_list):
    global g_scene_dict
    scene_pre_recall_dict = {}

    for scene in g_scene_dict.keys():
        gt_num, tp_num, fp_num = 0, 0, 0
        for video in g_scene_dict[scene]:
            gt_num += video_pre_recall_list[0][video]
            tp_num += video_pre_recall_list[1][video]
            fp_num += video_pre_recall_list[2][video]
        scene_pre_recall_dict[scene] = [gt_num, tp_num, fp_num]
    return scene_pre_recall_dict


def save_video_pre_recall_to_csv(video_pre_recall_list, conf_name, inx):
    global g_model_name, g_video_csv_file
    with open(g_video_csv_file, "a+") as f:
        all_video_gt_num, all_video_tp_num, all_video_fp_num = 0, 0, 0
        for video in video_pre_recall_list[0].keys():
            #print video
            gt_num, tp_num, fp_num = video_pre_recall_list[0][video], video_pre_recall_list[1][video], \
                                     video_pre_recall_list[2][video]

            # 全部视频数据统计
            all_video_gt_num += gt_num
            all_video_tp_num += tp_num
            all_video_fp_num = fp_num     # 因为不同大小的误检不好区分，故不同目标大小的误检数目都相同

            save_str = str(g_model_name) + "," + str(conf_name.split(" ")[-1]) + "," + str(conf_name.split(" ")[0]) + "," +\
                       str(g_gt_obj_size_list[inx].encode("gb2312")) + "," + str(video) + ","
            save_str += str(gt_num) + "," + str(tp_num + fp_num) + "," + \
                        str(tp_num) + "," + str(fp_num) + "," + \
                        str(float(tp_num) / max(0.00001, gt_num)) + "," + \
                        str(float(tp_num) / max(0.00001, fp_num + tp_num)) + "\n"
            f.write(save_str)

        save_str = str(g_model_name) + "," + str(conf_name.split(" ")[-1]) + "," + str(conf_name.split(" ")[0]) + "," + \
                   str(g_gt_obj_size_list[inx].encode("gb2312")) + "," + "all_video" + ","
        save_str += str(all_video_gt_num) + "," + str(all_video_tp_num + all_video_fp_num) + "," + \
                    str(all_video_tp_num) + "," + str(all_video_fp_num) + "," + \
                    str(float(all_video_tp_num) / max(0.00001, all_video_gt_num)) + "," + \
                    str(float(all_video_tp_num) / max(0.00001, all_video_fp_num + all_video_tp_num)) + "\n"
        f.write(save_str)


def save_scene_pre_recall_to_csv(scene_pre_recall_dict, conf_name, inx):
    global g_model_name, g_scene_csv_file
    with open(g_scene_csv_file, "a+") as f:
        total_gt_num, total_tp_num, total_fp_num = 0, 0, 0
        for scene in scene_pre_recall_dict.keys():
            gt_num, tp_num, fp_num = scene_pre_recall_dict[scene][0], scene_pre_recall_dict[scene][1], \
                                     scene_pre_recall_dict[scene][2]

            total_gt_num += gt_num
            total_tp_num += tp_num
            total_fp_num += fp_num

            save_str = str(g_model_name) + "," + str(conf_name.split(" ")[-1]) + "," + str(conf_name.split(" ")[0]) + "," + \
                       str(g_gt_obj_size_list[inx].encode("gb2312")) + "," + str(scene) + ","
            save_str += str(gt_num) + "," + str(tp_num + fp_num) + "," + \
                        str(tp_num) + "," + str(fp_num) + "," + \
                        str(float(tp_num) / max(0.00001, gt_num)) + "," + \
                        str(float(tp_num) / max(0.00001, fp_num + tp_num)) + "\n"
            f.write(save_str)

        total_video = u"全部视频"
        total_video = total_video.encode("gb2312")
        save_str = str(g_model_name) + "," + str(conf_name.split(" ")[-1]) + "," + str(conf_name.split(" ")[0]) + "," + \
                       str(g_gt_obj_size_list[inx].encode("gb2312")) + "," + str(total_video) + ","
        save_str += str(total_gt_num) + "," + str(total_tp_num + total_fp_num) + "," + \
                str(total_tp_num) + "," + str(total_fp_num) + "," + \
                str(float(total_tp_num) / max(0.00001, total_gt_num)) + "," + \
                str(float(total_tp_num) / max(0.00001, total_fp_num + total_tp_num)) + "\n"
        f.write(save_str)


def pre_recall_process(match_result_dict, no_match_result_dict, label_result_dict, conf_name, size_inx):

    video_pre_recall_list = video_pre_recall_process(match_result_dict, no_match_result_dict,\
                                                     label_result_dict, float(conf_name.split(" ")[0]), size_inx)
    #scene_pre_recall_dict = scene_pre_recall_process(video_pre_recall_list)
    save_video_pre_recall_to_csv(video_pre_recall_list, conf_name, size_inx)
    #save_scene_pre_recall_to_csv(scene_pre_recall_dict, conf_name, size_inx)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Parameter Error!"
        sys.exit()

    obj_type = sys.argv[1]
    #obj_type = u"person"

    detect_result_file = u"./src_detect_result/"
    detect_txt_list = glob.glob(os.path.join(detect_result_file, "*/*.txt"))

    label_result_file = u"./bin/label_result/"
    label_txt_list = glob.glob(os.path.join(label_result_file, "*.txt"))

    dst_file = dst_file[:-1] + "-" + obj_type + '/'
    if os.path.exists(dst_file[:-1]):
        shutil.rmtree(dst_file[:-1])
    if not os.path.exists(dst_file[:-1]):
        os.mkdir(dst_file[:-1])

    # 初始化csv file
    init_csv_file(dst_file)

    # 初始化type_dict
    #init_video_type_dict()

    # 标定结果字典
    label_result_dict = get_label_result(label_txt_list, obj_type)

    # 获得所分析的目标大小
    #global g_gt_obj_size_list
    g_gt_obj_size_list = get_gt_obj_size_list()

    for txt in detect_txt_list:
        if not txt.split("\\")[-1].startswith(obj_type):
            continue
        #global g_model_name
        g_model_name = obj_type + "-" + txt.strip().split("\\")[-2].encode("gb2312")

        print g_model_name

        # 检测结果字典
        det_pic_num, detect_result_dict = get_detect_result(txt)
        print det_pic_num
        #print detect_result_dict

        # 获得与label匹配上的目标信息
        match_result_dict, no_match_result_dict = get_match_result(label_result_dict, detect_result_dict)

        #print match_result_dict
        #print no_match_result_dict
        #pdb.set_trace()
        # 获得fppi对应的conf
        fppi_conf_list = get_fppi_conf_list_by_fppi(no_match_result_dict, det_pic_num)

        test_conf_list = g_conf_list + fppi_conf_list
        for conf_inx in xrange(len(test_conf_list)):
            if conf_inx >= len(g_conf_list):
                conf_name = str(test_conf_list[conf_inx]) + " fppi=" + \
                            str(g_fppi_category[conf_inx - len(g_conf_list)])
            else:
                conf_name = str(test_conf_list[conf_inx]) + " " + str(test_conf_list[conf_inx])
            for size_inx in xrange(len(g_gt_obj_size_list)):
                pre_recall_process(match_result_dict, no_match_result_dict, label_result_dict, conf_name, size_inx)




























