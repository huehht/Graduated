import os
import string


def get_info(start, lines):
    res = {}
    tmp = lines[start]
    # lines.pop(start)
    cut_position = tmp.find("(")
    k, v = tmp[:cut_position], tmp[cut_position + 1:-2].split(",")
    for i, vv in enumerate(v):
        v[i] = vv.replace('(', '').replace(')', '').strip()
        if v[i].startswith("#"):
            v[i] = get_info(v[i], lines)
    res[k] = v
    return res


if __name__ == '__main__':
    file = open("test.STEP")
    s = file.read()
    file.close()
    s = s.replace('\r', '').replace('ISO-10303-21\n',
                                    '').replace('"END-ISO-10303-21\n"', '')
    # header = s[s.index('HEADER\n'):s.index('ENDSEC\n')]
    # data = s[s.index('DATA\n'):s.index('ENDSEC\n')]
    header = s[s.index('HEADER') + len('HEADER') + 2:s.index('ENDSEC')]
    data = s[s.index('DATA') + len('DATA') + 2:]
    step_root = {}
    header_root = {}
    data_root = {}
    data_lines = {}
    header_list = header.split('\n')
    for line in header_list:
        cut_position1 = line.find("(")
        cut_position2 = line.find(";")
        key = line[0:cut_position1]
        value = line[cut_position1:cut_position2]
        header_root[key] = value
    step_root["header"] = header_root
    data_list = data.split('\n')
    # print(data_list[0:10])
    for line in data_list:
        cut_position = line.find("=")
        if cut_position != -1:
            key = line[0:cut_position].strip()
            value = line[cut_position + 2:].strip()
            data_lines[key] = value.strip()
    for key in data_lines.keys():
        line = data_lines[key]
        cut_position1 = line.find("(")
        cut_position2 = line.find(";") - 1
        list = []
        if line.find('#') == -1: continue
        key1 = line[0:cut_position1].strip()
        if key1 != 'EDGE_LOOP': continue
        key = key + ' ' + key1
        print('******************************')
        temp = line[cut_position1 + 1:cut_position2]
        list = temp.split(',')
        list1 = temp.split(',')
        # print(list1)
        for i in range(len(list)):
            cur = list[i].replace('(', '').replace(')', '').strip()
            if cur[0] == "#":
                res = get_info(cur.strip(), data_lines)
                list1[i] = res
        data_root[key] = list1
        print(key, list1)
    step_root["data"] = data_root
    print(step_root)
