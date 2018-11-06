# -*- coding: utf-8 -*-
import re
import os
file_report = ''


def delete_tag(
        text):
    flag = 0
    new_line = ''
    for i in text:
        if flag:
            if i == '>':
                flag = 0
        else:
            if i == '<':
                flag = 1
            else:
                new_line = new_line + i
    return new_line


def delete_table_and_footnotes(
        text):
    regular_string = r'#Сноска:\[.+\]'
    new_text = ''
    while '<table>' in text:
        ind = text.find('<table>')
        new_text += text[:ind]
        ind = text.find('</table>')
        text = text[ind + len('</table>'):]
    text = new_text + text
    if '#Сноска:' in text:
        split_text = re.split(regular_string, text)
        text = ''.join(split_text)
    return text


def split_all_text_on_parts(
        text):
    global names_bibliography
    text = text[text.find('</NOMORPH>') + 10:]
    text = delete_table_and_footnotes(text)
    text = text.replace('&#64285;', '').replace('&#1761;', '').replace('&#691;', '').replace('&#703;', '').\
        replace('&#694; ', '')
    text = text.replace(u'\xa0', u' ')
    text = delete_tag(text)
    introduction = 'введение'.lower()
    main = ''
    if introduction in text.lower():
        position = text.lower().find(introduction)
        text = text[position + len(introduction):]
        if introduction in text.lower():
            position = text.lower().find(introduction)
            char_text = text[position + len(introduction) + 1]
            if not (char_text.isalpha() and char_text.islower()) and text[position + len(introduction)] != ',' and \
                    (text[position-1] == '\n' or text[position-1].isspace() and not text[position-2].isalpha()) \
                    and text[position - 2] != ',':
                text = text[position + len(introduction):]
                if introduction in text.lower():
                    position = text.lower().find(introduction)
                    char_text = text[position + len(introduction) + 1]
                    if not (char_text.isalpha() and char_text.islower()) and text[position + len(introduction)] != ',' \
                            and text[position - 2] != ',' and \
                            (text[position-1] == '\n' or text[position-1].isspace() and not text[position-2].isalpha()):
                        text = text[position + len(introduction):]
    flag_bibliography = 1
    for b in names_bibliography:
        if b.lower() in text.lower():
            test_text = text
            while test_text.lower().find(b.lower()) != -1:
                num = test_text.lower().find(b.lower())
                l_num = num + len(b)
                if (test_text[l_num] == ',') or (num - 2 > 0 and test_text[num - 2:num] == ', ') \
                        or (l_num + 2 < len(test_text) and test_text[l_num: l_num + 2] == ' ('):
                    test_text = test_text[l_num:]
                    continue
                while l_num < len(test_text):
                    if test_text[l_num] == ' ' or test_text[l_num] == ' ' or test_text[l_num] == '…' \
                            or test_text[l_num:l_num + 2] == '..':
                        if test_text[l_num:l_num + 2] == '..' or test_text[l_num] == '…':
                            test_text = test_text[num + len(b):]
                            break
                        else:
                            l_num += 1
                        continue
                    else:
                        if test_text[l_num].isdigit() or (test_text[l_num].isalpha() and test_text[l_num].islower()):
                            test_text = test_text[num + len(b):]
                            break
                        else:
                            m_num = num - 1
                            if test_text[m_num] == ' ' and test_text[m_num - 1].isalpha() \
                                    and test_text[m_num - 1].islower():
                                test_text = test_text[num + len(b):]
                                break
                            if test_text[m_num-4:num] == '     ' and test_text[m_num - 5] == '.':
                                test_text = test_text[num + len(b):]
                                break
                            while m_num >= 0:
                                if test_text[m_num] == ' ' or test_text[m_num] == ' ' or test_text[m_num] == '\n':
                                    m_num -= 1
                                    continue
                                else:
                                    if not test_text[m_num].isdigit():
                                        flag_bibliography = 0
                                        main += text[:(len(text) - len(test_text) + num)]
                                        text = test_text[num + len(b):]
                                    test_text = test_text[num + len(b):]
                                    break
                            break
                if flag_bibliography == 0:
                    break
            if flag_bibliography == 0:
                break
    if flag_bibliography:
        return [0, text]
    return [0, main]


def if_link(
        text):
    ind = len(text) - 1
    while ind >= 0 and text[ind] != ' ':
        ind -= 1
    if text[ind+1:ind+5] == 'http':
        return 1
    return 0


def analysis_text(
        text):
    global file_report
    regular_string = r'(?<!\[)(?<!\d)\d{1,}(?!\.)(?!\d)(?!\])'
    numbers = re.findall(regular_string, text)
    split_text = re.split(regular_string, text)
    for i in range(len(numbers)):
        if if_link(''.join(split_text[:i+1])):
            continue
        file_report.write(numbers[i] + '\n' + ''.join(split_text[:i+1])[-200:] + numbers[i] +
                          ''.join(split_text[i+1:])[:200] + '\n\n')


def analysis_references(
        args):
    main_file = ''
    for i in args:
        if not ('.htm' in i[-4:]):
            continue
        f = open(i, 'r', encoding='cp1251')
        while True:
            line = f.readline().replace(' ', '')
            if line[:8] == 'VKR_SUB=':
                if line[8:12] == 'Main':
                    main_file = i
                break
        f.close()
    file_text = open(main_file, 'r', encoding='cp1251')
    line = file_text.read()
    file_text.close()
    line = split_all_text_on_parts(line)
    analysis_text(line[1])


def file_rewrite(
        text):
    list_of_data = []
    file = open(text, 'r')
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        list_of_data = list_of_data + [line[:-1]]
    file.close()
    return list_of_data


def main_analysis_references(
        direct):
    global file_report
    list_of_files = sorted(os.listdir(path=direct))
    n = 0
    while True:
        if len(list_of_files) == n:
            break
        list_of_new_files = sorted(os.listdir(path=(direct + list_of_files[n] + '/')))
        nn = 0
        while True:
            if len(list_of_new_files) == nn:
                break
            split_name = list_of_new_files[nn].split('_')
            m = split_name[0]
            analysis_list = [direct + list_of_files[n] + '/' + list_of_new_files[nn]]
            nn += 1
            while True:
                if len(list_of_new_files) == nn:
                    break
                split_name = list_of_new_files[nn].split('_')
                if m != split_name[0]:
                    break
                if split_name[1][0].isdigit():
                    analysis_list = analysis_list + [direct + list_of_files[n] + '/' + list_of_new_files[nn]]
                nn += 1
            print(m)
            file_report = open(direct + list_of_files[n] + '/' + m + '_preproc.txt', 'w')
            analysis_references(analysis_list)
            file_report.close()
        n += 1


names_bibliography = file_rewrite('names_bibl.txt')
main_analysis_references('anketa_docs_60_out_reorg/')
main_analysis_references('60_МГПУ_МГППУ_out_reorg/')