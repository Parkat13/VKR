# -*- coding: utf-8 -*-
import re
import os
date = 2017


def only_number(
        link):
    link = link[1:-1]
    number = 0
    list_of_numbers = []
    flag = 1
    for i in link:
        if flag == 1:
            if i.isdigit():
                number = number*10 + int(i)
            else:
                if number != 0:
                    list_of_numbers = list_of_numbers + [number]
                number = 0
                if i.isalpha():
                    flag = 0
        elif i == ',' or i == ';':
            flag = 1
    if number != 0:
        list_of_numbers = list_of_numbers + [number]
    return list_of_numbers


def stemming_author(
        auth):
    global endings
    author = auth.copy()
    fl = 1
    while fl:
        fl = 0
        for i in endings:
            if author[0][-len(i):] == i and len(author[0]) - len(i) >= 2:
                author[0] = author[0][0:len(author[0]) - len(i)]
                fl = 1
                break
    return author


def author_split(
        author):
    regular_string = r"([А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*)[\s,]*" \
                     r"((?:[А-ЯЁA-Z][а-яёa-z]?\.?\s*){1,2})" \
                     r"|((?:[А-ЯЁA-Z][а-яёa-z]?\.?\s*){1,2})" \
                     r"([А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\-)(?!\–))"
    split_auth = re.findall(regular_string, author)
    names = []
    if len(split_auth) == 0:
        return []
    for i in split_auth[0]:
        if i != '':
            if '.' in i:
                names = names + [i.replace(' ', '').replace('\xa0', '').replace('.', '').replace('\n', '')]
            else:
                names = [i.replace(' ', '').replace('\xa0', '').replace('.', '').replace('\n', '')] + names
    return names


def define_number(
        line):
    number = 0
    i = 0
    while True:
        if i == len(line):
            break
        if line[i].isdigit():
            number = number * 10 + int(line[i])
            i += 1
        else:
            if i == 0:
                i = 1
                continue
            break
    if number == 0:
        return -1
    return number


def transliteration(
        author):
    global words_transliteration
    i = 0
    rus_author = ''
    while i < len(author):
        for j in words_transliteration:
            if author[i: i + len(j[0])].upper() == j[0]:
                rus_author = rus_author + j[1]
                i += len(j[0])
                break
    return rus_author[0] + rus_author[1:].lower()


def words_correction(
        author):
    words = [['A', 'А'], ['C', 'С'], ['E', 'Е'], ['K', 'К'], ['O', 'О'], ['P', 'Р'], ['X', 'Х'],
             ['a', 'а'], ['c', 'с'], ['e', 'е'], ['k', 'к'], ['o', 'о'], ['p', 'р'], ['x', 'х'],
             ['H', 'Н'], ['B', 'В'], ['M', 'М'], ['T', 'Т']]
    new_author = ''
    for i in author:
        for j in words:
            if i == j[0]:
                new_author = new_author + j[1]
                break
        else:
            new_author = new_author + i
    return new_author


def save_data_of_authors(
        author, number):
    global set_author, dict_all_data, set_author_stemming
    list_author = [author[0] + ' ' + author[1]]
    set_author.update(set(list_author))
    dict_all_data[number][-1][0].update(set(list_author))
    author_stemming = stemming_author(author)
    list_author_stemming = [author_stemming[0] + ' ' + author_stemming[1]]
    set_author_stemming.update(set(list_author_stemming))
    dict_all_data[number][-1][1].update(set(list_author_stemming))
    return list_author_stemming


def define_author(
        line, number):
    global set_author, file_report1, file_report2, dict_all_data, set_author_stemming, refer
    authors_return = []
    regular_string = r'((?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s,]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2})|' \
                     r'(?:(?<!\w)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2}' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\-)(?!\–)))'
    set_upper = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    set_lower = set('abcdefghijklmnopqrstuvwxyz')
    if re.search(regular_string, line):
        authors = re.findall(regular_string, line)
        if number in dict_all_data:
            dict_all_data[number] = dict_all_data[number] + [[set(), set()]]
        else:
            dict_all_data[number] = [[set(), set()]]
        for i in authors:
            if i == '':
                continue
            ch = 0
            for j in i:
                if j in set_upper or j in set_lower:
                    ch += 1
                if j in set(' .,'):
                    continue
            if ch > 3 * len(i) / 4:
                i = words_correction(i)
            split_auth = author_split(i)
            ch = 0
            for k in split_auth[0]:
                if k in set_upper or k in set_lower:
                    ch += 1
            if ch > 3 * len(split_auth[0])/4:
                trans = [transliteration(split_auth[0]), transliteration(split_auth[1])]
                authors_return = authors_return + save_data_of_authors(trans, number)
            refer = refer + [split_auth[0] + ' ' + split_auth[1] + '; ']
            authors_return = authors_return + save_data_of_authors(split_auth, number)
        refer = refer + ['\n']
    else:
        refer = refer + ['нет\n']
        if number in dict_all_data:
            dict_all_data[number] += [[set(), set()]]
        else:
            dict_all_data[number] = [[set(), set()]]
    return authors_return


def define_date(
        line, number, authors):
    global dict_all_data, list_date, date, file_report1, classics, date, errors_in_date, refer
    if re.search(r'(?<!\d)(?:\d{4})(?!\d)', line):
        all_date = re.findall(r'(?<!\d)(?:\d{4})(?!\d)', line)
        for i in all_date:
            if (int(i) > 1500) and (int(i) <= date):
                for j in authors:
                    if j in classics or j.split()[0] in classics:
                        if date - int(i) >= 10:
                            dict_all_data[number][-1] = [dict_all_data[number][-1], i]
                            list_date = list_date + [int(i)]
                            refer = refer + [str(i) + '\n\n']
                            break
                        else:
                            errors_in_date = errors_in_date + ['Автор ' + j + ' - классик, неправильный год ' + i
                                                               + '\n\n']
                            list_date = list_date + [-1]
                            dict_all_data[number][-1] = [dict_all_data[number][-1], i]
                            refer = refer + [str(i) + '\n\n']
                            break
                else:
                    dict_all_data[number][-1] = [dict_all_data[number][-1], i]
                    list_date = list_date + [int(i)]
                    refer = refer + [str(i) + '\n\n']
                break
        else:
            list_date = list_date + [-1]
            dict_all_data[number][-1] = [dict_all_data[number][-1], -1]
            refer = refer + ['нет\n\n']
    else:
        list_date = list_date + [-1]
        dict_all_data[number][-1] = [dict_all_data[number][-1], -1]
        refer = refer + ['нет\n\n']


def is_in_list_bibliography(
        word):
    global list_bibliography
    fl_k = 0
    for lb in list_bibliography:
        if lb == word[0:len(lb)]:
            fl_k = 1
            break
    return fl_k


def def_flag_for_authors(
        authors, k):
    window = 10
    k_l = authors[k].split()
    k_r = authors[k + 1].split()
    j = k
    ch = 0
    while len(k_l) + ch < window:
        if j > 0:
            j -= 1
            k_l = authors[j].split() + k_l
            ch += 1
        else:
            break
    line = ' '.join(k_l)
    if '.' in line:
        line = line.split('.')[-1]
        k_l = line.split()
    for k_n in k_l[(-window+ch):]:
        is_k = is_in_list_bibliography(k_n)
        if is_k == 1:
            break
    else:
        ch = 0
        j = k + 1
        while len(k_r) + ch < window:
            if j < len(authors) - 2:
                j += 1
                k_r = k_r + authors[j].split()
                ch += 1
            else:
                break
        line = ' '.join(k_r)
        if '.' in line:
            line = line.split('.')[0]
            k_r = line.split()
        for k_n in k_r[:(window-ch)]:
            is_k = is_in_list_bibliography(k_n)
            if is_k == 1:
                break
        else:
            return 1
    return 0


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


def create_list_of_sources_from_all_parts(
        main_file):
    global names_bibliography, refer, set_author, list_date, date, not_in_the_text, file_report1, file_report2, \
        errors_in_date, names_bibliography, bibliography_subtitles, names_pril, all_penalty, error_links
    f_file = open(main_file, 'r', encoding='cp1251')
    text = f_file.read()
    f_file.close()
    text = text[text.find('</NOMORPH>') + 10:]
    text = text.replace('</table>', '@')
    text = delete_tag(text)
    introduction = 'введение'.lower()
    if introduction in text.lower():
        position = text.lower().find(introduction)
        text = text[position + len(introduction):]
        if introduction in text.lower():
            position = text.lower().find(introduction)
            char_text = text[position + len(introduction) + 1]
            if not (char_text.isalpha() and char_text.islower()) and text[position + len(introduction)] != ',' and \
                    text[position + len(introduction)].isspace():
                text = text[position + len(introduction):]
    flag_bibliography = 1
    for b in names_bibliography:
        if b.lower() in text.lower():
            test_text = text
            while test_text.lower().find(b.lower()) != -1:
                num = test_text.lower().find(b.lower())
                l_num = num + len(b)
                if (test_text[l_num] == ',') or (num-2 > 0 and test_text[num-2:num] == ', ') \
                        or (l_num+2 < len(test_text) and test_text[l_num: l_num+2] == ' ('):
                    test_text = test_text[l_num:]
                    continue
                while l_num < len(test_text):
                    if test_text[l_num] == ' ' or test_text[l_num] == ' ' or test_text[l_num] == '…' \
                            or test_text[l_num:l_num+2] == '..':
                        if test_text[l_num:l_num+2] == '..' or test_text[l_num] == '…':
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
                            if test_text[m_num] == ' ' and test_text[m_num-1].isalpha() \
                                    and test_text[m_num-1].islower():
                                test_text = test_text[num + len(b):]
                                break
                            while m_num >= 0:
                                if test_text[m_num] == ' ' or test_text[m_num] == ' ' or test_text[m_num] == '\n':
                                    m_num -= 1
                                    continue
                                else:
                                    if not test_text[m_num].isdigit():
                                        flag_bibliography = 0
                                        text = test_text[num + len(b):]
                                    test_text = test_text[num + len(b):]
                                    break
                            break
                if flag_bibliography == 0:
                    break
            if flag_bibliography == 0:
                break
    if flag_bibliography:
        file_report2.write('Нет списка литературы\n\n')
        return 1
    for p in names_pril:
        if p.lower() in text.lower():
            num_pril = text.lower().find(p.lower())
            text = text[:num_pril]
    text = text.replace('\xa0', '').replace('&quot;', '').lstrip().rstrip()
    ##################
    regular_string = r'(?<!\S)(?<!:\s)(?<!,\s)(?<!—\s)(?<!\w\s)(?<!§\s)(?<!\d)(?<!№\s)(?<!;\s)(?<!№\s\s)' \
                     r'(?<!\.\s\s)(?<!—\s\s)(?<!»\s)(?<!–\s)(?<!-\s)(?<!\.\s)(\d{1,3})(?![А-ЯЁа-яёA-Za-z0-9«\-])'
    text = text.split('\n')
    l_l = 0
    while len(text) > l_l:
        if len(text[l_l]) == 0:
            l_l += 1
            continue
        current_line = text[l_l].lstrip()
        if len(current_line.replace('.', '').replace(':', '').replace(';', '').replace(',', '').lstrip()) == 0:
            l_l += 1
            continue
        ch = 0
        for wl in current_line.split():
            for subt in bibliography_subtitles:
                if subt in wl.lower():
                    ch += 1
                    break
        if ch >= len(current_line.split()) / 2:
            l_l += 1
            continue
        number = define_number(current_line)
        if re.search(regular_string, text[l_l][3:]):
            text_line = re.split(regular_string, text[l_l][3:])
            current_line = str(number) + text_line[0]
            text[l_l] = ''.join(text_line[1:])
        else:
            while True:
                l_l += 1
                if len(text) <= l_l:
                    break
                if len(text[l_l]) == 0:
                    continue
                if re.search(regular_string, text[l_l]):
                    line_split = re.split(regular_string, text[l_l])
                    current_line = current_line + line_split[0]
                    text[l_l] = ''.join(line_split[1:])
                    break
                ch = 0
                for wl in text[l_l].split():
                    for subt in bibliography_subtitles:
                        if subt in wl.lower():
                            ch += 1
                            break
                if ch >= len(text[l_l].split()) / 2:
                    l_l += 1
                    break
                current_line = current_line + text[l_l]
        refer = refer + [str(number) + ': ' + current_line.replace('\n', '') + '\nАвторы: ']
        authors = define_author(current_line, number)
        not_in_the_text += [str(number)+'.'+str(len(dict_all_data[number])-1)]
        refer = refer + ['Год: ']
        define_date(current_line, number, authors)
        if re.search(r'http://[\S]+', current_line):
            error_link = re.split(r'http://[\S]+', current_line)
            for k in error_link:
                if re.search(r'[a-zA-Zа-яА-ЯёЁ]', k):
                    break
            else:
                error_links = error_links + [current_line.replace('\n', '') + '\n\n']
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', current_line):
            error_links = error_links + [current_line.replace('\n', '') + '\n\n']
        #############################
    for i in refer:
        file_report1.write(i)
    year5, year10, year20, non = 0, 0, 0, 0
    for i in list_date:
        if i >= date - 5:
            year5 += 1
        if i >= date - 10:
            year10 += 1
        if i >= date - 20:
            year20 += 1
        if i == -1:
            non += 1
    file_report2.write('Текущий год: ' + str(date) + '\n\n')
    file_report2.write('#1\nОбщее количество ресурсов: ' + str(len(list_date)) + '\n')
    file_report2.write('Ресурсы за последние 5 лет: ' + str(year5) + '\n')
    file_report2.write('Ресурсы за последние 10 лет: ' + str(year10) + '\n')
    file_report2.write('Ресурсы ранее 20 лет: ' + str(len(list_date) - year20) + '\n')
    file_report2.write('Ресурсы, в которых не указан год: ' + str(non) + '\n\n')
    for i in errors_in_date:
        file_report2.write(i)


def create_list_of_sources(
        references, line=''):
    global set_author, list_date, date, not_in_the_text, file_report1, file_report2, errors_in_date, \
        names_bibliography, bibliography_subtitles, names_pril, all_penalty, error_links, refer
    if len(line) == 0:
        file_references = open(references, 'r', encoding='cp1251')
        while True:
            line = file_references.readline()
            if '</NOMORPH>' in line:
                break
        line = file_references.readline()
        for i in names_pril:
            if i.lower() in line.lower():
                file_report2.write('Нет списка литературы\n')
                return
        line = line + file_references.read()
        file_references.close()
        line = line.replace('<b>', '').replace('</b>', '').replace('<p>', '').replace('</p>', '').replace('&quot;', '')
        flag_bibliography = 1
        for bibliography in names_bibliography:
            if bibliography.lower() in line.lower() and not (bibliography.lower() + ',' in line.lower()) \
                    and not (', ' + bibliography.lower() in line.lower()):
                if line.lower().find(bibliography.lower()) != line.lower().rfind(bibliography.lower()):
                    continue
                num = line.lower().find(bibliography.lower())
                l_num = num + len(bibliography)
                while l_num < len(line):
                    if line[l_num] == ' ':
                        l_num += 1
                        continue
                    else:
                        if line[l_num].isalpha():
                            break
                        else:
                            m_num = num - 1
                            while m_num >= 0:
                                if line[m_num] == ' ':
                                    m_num -= 1
                                    continue
                                else:
                                    if not line[m_num].isdigit():
                                        flag_bibliography = 0
                                        line = line[num + len(bibliography):]
                                    break
                            break
                if flag_bibliography == 0:
                    break
        if flag_bibliography:
            file_report2.write('Нет списка литературы\n\n')
            return
    new_line = delete_tag(line)
    for p in names_pril:
        if p.lower() in new_line.lower():
            num_pril = new_line.lower().find(p.lower())
            new_line = new_line[:num_pril]
    line = new_line.replace('\xa0', '').lstrip().rstrip().split('\n')
    l_l = 0
    k_ln = 1
    const_regular_string = r'(?<!\S)(?<!\d)(\d\d)\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
    while len(line) > l_l:
        if len(line[l_l]) == 0:
            l_l += 1
            continue
        current_line = line[l_l].lstrip()
        if len(current_line.replace('.', '').replace(':', '').replace(';', '').replace(',', '').lstrip()) == 0:
            l_l += 1
            continue
        ch = 0
        for wl in current_line.split():
            for subt in bibliography_subtitles:
                if subt in wl.lower():
                    ch += 1
                    break
        if ch >= len(current_line.split()) / 2:
            l_l += 1
            continue
        number = define_number(current_line)
        last_number = 0
        if number != last_number + k_ln:
            file_report2.write('Неправильная нумерация: \n' + current_line + '\n\n')
        last_number = number
        k_ln = 1
        regular_string = r'(?<!\S)(?<!\d)' + str(last_number + k_ln) + '\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
        if re.search(regular_string, current_line):
            line_split = re.split(regular_string, current_line)
            current_line = line_split[0]
            line[l_l] = str(last_number + k_ln) + '.' + str(last_number + k_ln).join(line_split[1:])
        else:
            while not re.search(regular_string, '\n'.join(line[l_l:])):
                if re.search(const_regular_string, '\n'.join(line[l_l+1:])):
                    num_maybe = re.findall(const_regular_string, '\n'.join(line[l_l+1:]))
                    for t in num_maybe:
                        if int(t) > last_number:
                            break
                    else:
                        break
                    k_ln += 1
                else:
                    break
                regular_string = r'(?<!\S)(?<!\d)' + str(last_number + k_ln) + \
                                 '\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
            while True:
                l_l += 1
                if len(line) <= l_l:
                    break
                if len(line[l_l]) == 0:
                    continue
                regular_string = r'(?<!\S)(?<!\d)' + str(last_number + k_ln) + \
                                 '\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
                if re.search(regular_string, line[l_l]):
                    line_split = re.split(regular_string, line[l_l])
                    current_line = current_line + line_split[0]
                    line[l_l] = str(last_number + k_ln) + '.' + str(last_number + k_ln).join(line_split[1:])
                    break
                ch = 0
                for wl in line[l_l].split():
                    for subt in bibliography_subtitles:
                        if subt in wl.lower():
                            ch += 1
                            break
                if ch >= len(line[l_l].split())/2:
                    l_l += 1
                    break
                current_line = current_line + line[l_l]
        refer = refer + [str(last_number) + ': ' + current_line.replace('\n', '') + '\nАвторы: ']
        authors = define_author(current_line, last_number)
        refer = refer + ['Год: ']
        define_date(current_line, last_number, authors)
        if re.search(r'http://[\S]+', current_line):
            error_link = re.split(r'http://[\S]+', current_line)
            for k in error_link:
                if re.search(r'[a-zA-Zа-яА-ЯёЁ]', k):
                    break
            else:
                error_links = error_links + [current_line.replace('\n', '') + '\n\n']
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', current_line):
            error_links = error_links + [current_line.replace('\n', '') + '\n\n']
    for i in refer:
        file_report1.write(i)
    not_in_the_text = list(i+1 for i in range(len(list_date)))
    year5, year10, year20, non = 0, 0, 0, 0
    for i in list_date:
        if i >= date - 5:
            year5 += 1
        if i >= date - 10:
            year10 += 1
        if i >= date - 20:
            year20 += 1
        if i == -1:
            non += 1
    file_report2.write('Текущий год: ' + str(date) + '\n\n')
    file_report2.write('#1\nОбщее количество ресурсов: ' + str(len(list_date)) + '\n')
    file_report2.write('Ресурсы за последние 5 лет: ' + str(year5) + '\n')
    file_report2.write('Ресурсы за последние 10 лет: ' + str(year10) + '\n')
    file_report2.write('Ресурсы ранее 20 лет: ' + str(len(list_date) - year20) + '\n')
    file_report2.write('Ресурсы, в которых не указан год: ' + str(non) + '\n\n')
    for i in errors_in_date:
        file_report2.write(i)


def analysis_links(
        line, i, new_line, flag_of_bracket, flag_of_type, authors_new_line=''):
    global set_author_stemming, dict_all_data, not_in_the_text, missing_links, set_of_missing_links
    ff = 0
    if flag_of_type:
        current_line = authors_new_line
    else:
        current_line = new_line
    for j in set_author_stemming:
        if j.split()[0] in words_correction(current_line):
            for d in dict_all_data:
                for sub_d in range(len(dict_all_data[d])):
                    if str(dict_all_data[d][sub_d][1]) in new_line:
                        if (j.split()[0] + ' ' + j.split()[1]) in dict_all_data[d][sub_d][0][1]:
                            ff = 1
                            if (str(d) + '.' + str(sub_d)) in not_in_the_text:
                                not_in_the_text.remove(str(d) + '.' + str(sub_d))
                            break
        if ff:
            break
    else:
        if i - len(new_line) - 2 < 150:
            lef = 0
        else:
            lef = i - 150 - len(new_line) - 2
        if len(line) < i + 150:
            rig = len(line)
        else:
            rig = i + 150
        mis_line = line[lef:rig]
        if flag_of_type:
            current_line += ' '
        else:
            current_line = ''
        if not flag_of_bracket:
            missing_links = missing_links + [current_line + '[' + new_line + ']\n' + mis_line + '\n\n']
        else:
            missing_links = missing_links + [current_line + '(' + new_line + ')\n' + mis_line + '\n\n']
        if not (new_line in set_of_missing_links):
            list_for_set = [current_line + new_line]
            set_of_missing_links.update(set(list_for_set))


def define_links(
        line, i, new_line, flag_of_bracket):
    global law
    regular_string = r'((?:(?:(?<!\w)(?<!\-)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*)(?:[А-ЯЁA-Z][а-яёa-z]?\.?\s*)?' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\w))(?!\-)(?!\–))|' \
                     r'(?:(?<!\.\s)(?<!\.)(?<!\.\s\s)(?<!<p>\s)(?<!<p>)' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.)\s?(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?:(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z])(?![а-яёa-z])))|' \
                     r'(?:(?<!\w)(?:(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s?)(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?!\s[А-ЯЁA-Z])(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z]))(?![а-яёa-z])(?!\w)))'
    for lp in law:
        if lp in new_line.lower():
            break
    else:
        if re.search(r'[А-Я][а-я]+', new_line) and re.search(r'(?<!\d)(?:\d{4})(?!\d)', new_line):
            analysis_links(line, i, new_line, flag_of_bracket, 0)
        else:
            if len(new_line) == 4 and new_line.isdigit():
                if not flag_of_bracket:
                    split_new_line = re.split(r'\[' + new_line + '\]', line)
                else:
                    split_new_line = re.split(r'\(' + new_line + '\)', line)
                all_authors_new_line = re.findall(regular_string, split_new_line[0])
                if len(all_authors_new_line) != 0:
                    analysis_links(line, i, new_line, flag_of_bracket, 1, all_authors_new_line[-1])


def search_links(
        line):
    regular_string = r'(\[(?:(?:\s*\d+\s*[,.][^\]]+)|(?:\s*\d+\s*))(?:(?:;\s*\d+\s*,[^\]]+)' \
                     r'|(?:[,.]\s*\d+\s*)|(?:;\s*\d+\s*))*\])'
    link_separation = re.split(regular_string, line)
    links = re.findall(regular_string, line)
    flag = 0
    new_line = ''
    for i in range(len(line)):
        if flag == 3:
            if line[i] == '(':
                flag = 6
                new_line = ''
            if line[i] == '[':
                flag = 3
                new_line = ''
            if line[i] == ']':
                flag = 0
                define_links(line, i, new_line, 0)
                new_line = ''
            else:
                new_line = new_line + line[i]
        elif flag == 6:
            if line[i] == '(':
                flag = 6
                new_line = ''
            if line[i] == '[':
                flag = 3
                new_line = ''
            if line[i] == ')':
                flag = 0
                define_links(line, i, new_line, 1)
                new_line = ''
            else:
                new_line = new_line + line[i]
        else:
            if line[i] == '(':
                flag = 6
            if line[i] == '[':
                flag = 3
    return [links, link_separation]


def analysis_text(
        text):
    global set_author, file_report2, not_in_the_text, string_line, grave, set_of_authors_without_links, \
        names_bibliography, list_bibliography, all_names, set_grave, list_of_invalid_links, links_on_many_sources
    file_text = open(text, 'r', encoding='cp1251')
    while True:
        line = file_text.readline()
        if line[:10] == '</NOMORPH>':
            line = line[10:]
            break
    line = line + file_text.read()
    line = line.replace('&#64285;', '').replace('&#1761;', '').replace('&#691;', '').\
        replace('&#703;', '').replace('&#694; ', '').replace('<p>', '').replace('</p>', '').\
        replace('<#SPACE#>', '').replace('\xa0', '')
    line = delete_tag(line)
    introduction = 'введение'.lower()
    if introduction in line.lower():
        position = line.lower().find(introduction)
        line = line[position + len(introduction):]
        if introduction in line.lower():
            position = line.lower().find(introduction)
            char_text = line[position + len(introduction) + 1]
            if not (char_text.isalpha() and char_text.islower()) and line[position + len(introduction)] != ',' and \
                    line[position + len(introduction)].isspace():
                line = line[position + len(introduction):]
    flag_bibliography = 1
    for bibliography in names_bibliography:
        if bibliography.lower() in line.lower() and not (bibliography.lower() + ',' in line.lower()) \
                and not (', ' + bibliography.lower() in line.lower()):
            num = line.lower().find(bibliography.lower())
            while (num != -1) and flag_bibliography:
                l_num = num + len(bibliography)
                while l_num < len(line):
                    if line[l_num] == ' ':
                        l_num += 1
                        continue
                    else:
                        if line[l_num].isalpha():
                            break
                        else:
                            m_num = num - 1
                            while m_num >= 0:
                                if line[m_num] == ' ':
                                    m_num -= 1
                                    continue
                                else:
                                    if not line[m_num].isdigit():
                                        flag_bibliography = 0
                                        line = line[:num]
                                    break
                            break
                num = line.lower().find(bibliography.lower(), num + 1)
        if flag_bibliography == 0:
            break
    line = line.replace('\n', ' ')
    list_of_links = search_links(line)
    links = list_of_links[0]
    link_separation = list_of_links[1]
    regular_string = r'((?:(?:(?<!\w)(?<!\-)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*)(?:[А-ЯЁA-Z][а-яёa-z]?\.?\s*)?' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\w))(?!\-)(?!\–))|' \
                     r'(?:(?<!\.\s)(?<!\.)(?<!\.\s\s)(?<!<p>\s)(?<!<p>)' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.)\s?(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?:(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z])(?![а-яёa-z])))|' \
                     r'(?:(?<!\w)(?:(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s?)(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?!\s[А-ЯЁA-Z])(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z]))(?![а-яёa-z])(?!\w)))'
    set_upper_russian = set('АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ')
    for i in link_separation:
        if i is not None:
            authors = re.findall(regular_string, i)
            authors_sep = re.split(regular_string, i)
            authors_sep = authors_sep[::2]
            for j in range(len(authors)):
                if authors[j] == '':
                    continue
                flag = def_flag_for_authors(authors_sep, j)
                if flag == 1:
                    continue
                split_auth = author_split(words_correction(authors[j]))
                split_auth_stemming = stemming_author(split_auth)
                if split_auth_stemming[0].lower() in all_names:
                    continue
                if split_auth[0][0] in set_upper_russian and \
                        not(split_auth[1][0] in set_upper_russian):
                    continue
                if split_auth[1][0] in set_upper_russian and \
                        not (split_auth[0][0] in set_upper_russian):
                    continue
                if not ((split_auth[0] + ' ' + split_auth[1]) in set_author):
                    if not ((split_auth_stemming[0] + ' ' + split_auth_stemming[1]) in set_author_stemming):
                        num = i.find(authors[j])
                        if num < 200:
                            lef = 0
                        else:
                            lef = num - 200
                        if num + len(authors[j]) + 200 > len(i):
                            rig = len(i)
                        else:
                            rig = num + len(authors[j]) + 200
                        for gg in string_line:
                            if (split_auth[0] + ' ' + split_auth[1] + '\n' + i[lef:rig] + '\n\n') in gg:
                                break
                        else:
                            add_string = str(len(string_line) + 1) + '. ' + split_auth[0] + ' ' + \
                                         split_auth[1] + '\n' + i[lef:rig] + '\n\n'
                            string_line = string_line + [add_string]
                        list_author_stemming = [split_auth_stemming[0] + ' ' + split_auth_stemming[1]]
                        set_of_authors_without_links.update(set(list_author_stemming))
    k_num = -1
    for i in range(len(links)):
        k_num += 1
        number = only_number(links[i])
        if len(number) > 3:
            string_cmp = links[i] + '\n' + link_separation[i][-150:] + links[i] + link_separation[i+1][:150] + '\n\n'
            if not (string_cmp in grave):
                grave = grave + [string_cmp]
            if not (links[i] in set_grave):
                list_link_for_set = [links[i]]
                set_grave.update(set(list_link_for_set))
        else:
            for j in number:
                if j in dict_all_data:
                    for c in range(len(dict_all_data[j])):
                        if str(j) + '.' + str(c) in not_in_the_text:
                            not_in_the_text.remove(str(j) + '.' + str(c))
                    if len(dict_all_data[j]) > 1:
                        links_on_many_sources += ['[' + str(j) + ']; ']
                else:
                    list_of_invalid_links += ['[' + str(j) + ']\n']
                    list_of_invalid_links += [link_separation[2+k_num][-200:] + '[' + str(j) + ']'] + \
                                             [link_separation[2*k_num + 2][:200] + '\n\n']
    file_text.close()


def analysis_references(
        args):
    global not_in_the_text, file_report2, string_line, all_penalty, set_of_missing_links, missing_links, error_links
    files = []
    main_file = ''
    file_bibliography = ''
    for i in args:
        if not ('.htm' in i[-4:]):
            continue
        f = open(i, 'r', encoding='cp1251')
        while True:
            line = f.readline().replace(' ', '')
            if line[:8] == 'VKR_SUB=':
                if line[8:12] == 'Main':
                    main_file = i
                if line[8:12] == 'bibl':
                    file_bibliography = i
                elif line[8:12] == 'intr' or line[8:12] == 'part' or line[8:12] == 'conc' or line[8:11] == 'toc' or \
                        line[8:9] == '@' or line[8:12] == 'Main':
                    files = files + [i]
                break
        f.close()
    #if file_bibliography == '':
     #   file_report2.write('#1\nОтсутствует список литературы\n\n')
      #  return
    #else:
     #   create_list_of_sources(file_bibliography)
    error = create_list_of_sources_from_all_parts(main_file)
    if error:
        return
    #for i in files:
     #   analysis_text(i)
    analysis_text(main_file)
    if len(list_date) - len(not_in_the_text) >= 20:
        penalty = 0
    else:
        penalty = (20 - len(list_date) + len(not_in_the_text)) / 20
    all_penalty += penalty
    file_report2.write('Штрафной балл (литературы, указанной в тексте, меньше 20): ' + str(penalty) + '\n\n')
    new_links_10, new_links_5 = [], []
    for i in dict_all_data:
        for j in range(len(dict_all_data[i])):
            if date - int(dict_all_data[i][j][1]) <= 10:
                new_links_10 = new_links_10 + [str(i)+'.'+str(j)]
            if date - int(dict_all_data[i][j][1]) <= 5:
                new_links_5 = new_links_5 + [str(i)+'.'+str(j)]
    num_10, num_5 = 0, 0
    file_report2.write('Ссылки за последние 5 лет, указанные в тексте: ')
    for i in new_links_5:
        if not (i in not_in_the_text):
            num_5 += 1
            if len(dict_all_data[int(i.split('.')[0])]) == 1:
                file_report2.write(str(i.split('.')[0]) + ', ')
            else:
                file_report2.write(str(i) + ', ')
    file_report2.write('\n\nВсего: ' + str(num_5) + '\n\n')
    file_report2.write('Ссылки за последние 10 лет, указанные в тексте: ')
    for i in new_links_10:
        if not (i in not_in_the_text):
            num_10 += 1
            if len(dict_all_data[int(i.split('.')[0])]) == 1:
                file_report2.write(str(i.split('.')[0]) + ', ')
            else:
                file_report2.write(str(i) + ', ')
    file_report2.write('\n\nВсего: ' + str(num_10) + '\n\n')
    if num_5 >= 5:
        penalty = 0
    else:
        penalty = (5 - num_5)/10
    all_penalty += penalty
    file_report2.write('Штрафной балл (литературы за последние 5 лет, упомянутой в тексте, меньше пяти): '
                       + str(penalty) + '\n\n')
    if num_10 >= 10:
        penalty = 0
    else:
        penalty = (10 - num_10) / 20
    all_penalty += penalty
    file_report2.write('Штрафной балл (литературы за последние 10 лет, упомянутой в тексте, меньше десяти): '
                       + str(penalty) + '\n\n\n')
    penalty2_3 = 0
    file_report2.write('#2\nНеправильно оформленные ссылки: \n')
    if len(error_links) == 0:
        file_report2.write('отсутствуют\n\n')
    else:
        for i in error_links:
            file_report2.write(i)
    penalty = len(error_links)/20
    if penalty > 0.5:
        penalty = 0.5
    penalty2_3 += penalty
    file_report2.write('Штрафной балл (Неправильно оформленные ссылки): ' + str(penalty) + '\n\n\n')
    if len(not_in_the_text) == 0:
        file_report2.write('#3\nВсе ссылки указаны во всем тексте\n\n')
    else:
        file_report2.write('#3\nСсылки, не указанные во всем тексте: ')
        for i in not_in_the_text:
            if len(dict_all_data[int(i.split('.')[0])]) == 1:
                file_report2.write(str(i.split('.')[0]) + ', ')
            else:
                file_report2.write(str(i) + ', ')
        file_report2.write('\nВсего: ' + str(len(not_in_the_text)) + '\n\n')
    penalty = len(not_in_the_text)/20
    if penalty > 0.5:
        penalty = 0.5
    penalty2_3 += penalty
    if penalty2_3 > 0.5:
        penalty2_3 = 0.5
    file_report2.write('Штрафной балл (ссылки, неописанные в тексте): ' + str(penalty) + '\n\n\n')
    penalty4_5_6 = 0
    file_report2.write('#4\nСсылки цифрой, которых нет в списке литературы: \n')
    if len(list_of_invalid_links) == 0:
        file_report2.write('отсутствуют\n\n')
    else:
        for j in list_of_invalid_links:
            file_report2.write(j)
        file_report2.write('Всего ссылок: ' + str(len(list_of_invalid_links)) + '\n\n')
    penalty = len(list_of_invalid_links) / 20
    if penalty > 0.5:
        penalty = 0.5
    penalty4_5_6 += penalty
    file_report2.write('Штрафной балл (неправильные ссылки): ' + str(penalty) + '\n\n\n')
    file_report2.write('#5\nСсылки в тексте, которых нет в списке литературы: \n')
    if len(missing_links) == 0:
        file_report2.write('отсутствуют\n\n')
    else:
        for j in missing_links:
            file_report2.write(j)
        file_report2.write('Всего уникальных ссылок: ' + str(len(set_of_missing_links)) + '\n\n')
    penalty = len(set_of_missing_links)/20
    if penalty > 0.5:
        penalty = 0.5
    penalty4_5_6 += penalty
    file_report2.write('Штрафной балл (неуказанные ссылки): ' + str(penalty) + '\n\n\n')
    file_report2.write('#6\nСсылки на несколько источников: \n')
    if len(links_on_many_sources) == 0:
        file_report2.write('отсутствуют\n\n')
    else:
        for j in links_on_many_sources:
            file_report2.write(j)
        file_report2.write('\n\nВсего: ' + str(len(links_on_many_sources)) + '\n\n')
    penalty = len(links_on_many_sources)/20
    if penalty > 0.5:
        penalty = 0.5
    penalty4_5_6 += penalty
    file_report2.write('Штрафной балл (ссылки на несколько источников): ' + str(penalty) + '\n\n\n')
    if len(string_line) > 0:
        file_report2.write('#7\nДолжны быть ссылки на авторов: \n')
        for i in string_line:
            file_report2.write(i)
        file_report2.write('Всего авторов: ' + str(len(set_of_authors_without_links)) + '\n\n')
    else:
        file_report2.write('#7\nНа всех авторов в тексе есть ссылки\n\n')
    penalty = len(set_of_authors_without_links)/20
    if penalty > 0.5:
        penalty = 0.5
    penalty4_5_6 += penalty
    file_report2.write('Штрафной балл (неописанные авторы): ' + str(penalty) + '\n\n\n')
    if len(grave) > 0:
        file_report2.write('#8\nВ работе есть "могила ссылок": \n')
        for i in grave:
            file_report2.write(i)
        file_report2.write('Всего: ' + str(len(set_grave)) + '\n\n')
    else:
        file_report2.write('#8\nВ работе нет "могил ссылок" \n\n')
    penalty = len(set_grave)/20
    if penalty > 0.5:
        penalty = 0.5
    if penalty4_5_6 > 0.5:
        penalty4_5_6 = 0.5
    file_report2.write('Штрафной балл ("могилы ссылок"): ' + str(penalty) + '\n\n\n')
    if all_chars != 0:
        file_report2.write('#9\nСреднее число ссылок в первой главе на количество страниц: '
                           + str(n_links/(all_chars/150)) + '\n\n\n')
    all_penalty += penalty2_3 + penalty4_5_6
    if all_penalty > 2:
        all_penalty = 2
    file_report2.write('Сумма штрафных баллов: ' + str(all_penalty) + '\n\n\n')


def file_rewrite(
        text):
    data = []
    file = open(text, 'r')
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        data = data + [line[:-1]]
    file.close()
    return data


endings = file_rewrite('endings.txt')
f_classic = open('classic.txt', 'r')
classics = []
while True:
    a = f_classic.readline()
    if len(a) == 0:
        break
    auth_sp = stemming_author(a.split())
    if len(auth_sp) == 2:
        classics = classics + [auth_sp[0] + ' ' + auth_sp[1]]
    else:
        classics = classics + auth_sp
f_classic.close()
names_bibliography = file_rewrite('names_bibl.txt')
names_pril = file_rewrite('names_pril.txt')
law = file_rewrite('law_paper.txt')
list_bibliography = []
file_bibl = open('list_bibl.txt', 'r')
while True:
    file_line = file_bibl.readline()
    if len(file_line) == 0:
        break
    list_bibliography = list_bibliography + [file_line.split()[1]]
file_bibl.close()
bibliography_subtitles = file_rewrite('bibl_subtitles.txt')
f_transl = open('transliteration.txt', 'r')
words_transliteration = []
while True:
    a = f_transl.readline()
    if len(a) == 0:
        break
    a = a.split()
    words_transliteration = words_transliteration + [[a[0], a[1]]]
f_transl.close()
all_names = []
f_woman = open('woman_names.txt', 'r')
while True:
    a = f_woman.readline()
    if len(a) == 0:
        break
    all_names = all_names + [stemming_author([a[:-1].lower(), ''])[0]]
f_woman.close()
f_man = open('man_names.txt', 'r')
while True:
    a = f_man.readline()
    if len(a) == 0:
        break
    all_names = all_names + [stemming_author([a[:-1].lower(), ''])[0]]
f_man.close()
#direct = '000000/'
direct = 'files/'
#direct = 'reorganized/'
list_of_files = sorted(os.listdir(path=direct))
n = 0
while True:
    if len(list_of_files) == n:
        break
    if not os.path.isdir(list_of_files[n]):
        split_name = list_of_files[n].split('_')
        m = split_name[0]
        analysis_list = [direct + list_of_files[n]]
        n += 1
        while True:
            if len(list_of_files) == n:
                break
            split_name = list_of_files[n].split('_')
            if m != split_name[0]:
                break
            if split_name[1][0].isdigit():
                analysis_list = analysis_list + [direct + list_of_files[n]]
            n += 1
        print(m)
        dict_all_data = {}
        set_author = set()
        set_author_stemming = set()
        list_date = []
        errors_in_date = []
        not_in_the_text = []
        string_line = []
        set_of_authors_without_links = set()
        set_of_missing_links = set()
        missing_links = []
        error_links = []
        grave = []
        set_grave = set()
        all_penalty = 0
        all_chars = 0
        n_links = 0
        refer = []
        list_of_invalid_links = []
        links_on_many_sources = []
        file_report1 = open(direct + m + '_bibl_list.txt', 'w')
        file_report2 = open(direct + m + '_bibl_remarks.txt', 'w')
        analysis_references(analysis_list)
        file_report1.close()
        file_report2.close()
    else:
        #os.chdir(list_of_files[n])
        list_of_new_files = sorted(os.listdir(path=(direct+list_of_files[n]+'/')))
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
            dict_all_data = {}
            set_author = set()
            set_author_stemming = set()
            list_date = []
            errors_in_date = []
            not_in_the_text = []
            string_line = []
            set_of_authors_without_links = set()
            set_of_missing_links = set()
            missing_links = []
            error_links = []
            grave = []
            set_grave = set()
            all_penalty = 0
            all_chars = 0
            n_links = 0
            refer = []
            list_of_invalid_links = []
            links_on_many_sources = []
            file_report1 = open(direct + list_of_files[n] + '/' + m + '_bibl_list.txt', 'w')
            file_report2 = open(direct + list_of_files[n] + '/' + m + '_bibl_remarks.txt', 'w')
            analysis_references(analysis_list)
            file_report1.close()
            file_report2.close()
        n += 1





    """
    k_ln = 1
    fl_end = 0
    last_number = 0
    regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
    const_regular_string = r'(?<!\S)(?<!\d)(?<!№\s)([\d]{1,3}\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
    while not re.search(regular_string, text):
        if re.search(const_regular_string, text[2:]):
            num_maybe = re.findall(const_regular_string, text[2:])
            for t in num_maybe:
                if int(t) > last_number:
                    break
            else:
                break
            k_ln += 1
        else:
            fl_end = 1
            break
        regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + \
                         r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
    if not fl_end:
        regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + \
                         r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
        text = re.split(regular_string, text)
        text = ((str(last_number + k_ln) + '. ') + (str(last_number + k_ln) + '. ').join(text[1:]).rstrip()).split('\n')
        l_l = 0
        while len(text) > l_l:
            if len(text[l_l]) == 0:
                l_l += 1
                continue
            current_line = text[l_l].lstrip()
            if len(current_line.replace('.', '').replace(':', '').replace(';', '').replace(',', '').lstrip()) == 0:
                l_l += 1
                continue
            ch = 0
            for wl in current_line.split():
                for subt in bibliography_subtitles:
                    if subt in wl.lower():
                        ch += 1
                        break
            if ch >= len(current_line.split()) / 2:
                l_l += 1
                continue
            number = define_number(current_line)
            if number != last_number + k_ln:
                file_report2.write('Неправильная нумерация: \n' + current_line + '\n\n')
            last_number = number
            k_ln = 1
            regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + \
                             r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
            if re.search(regular_string, current_line):
                line_split = re.split(regular_string, current_line)
                current_line = line_split[0]
                text[l_l] = str(last_number + k_ln) + '.' + str(last_number + k_ln).join(line_split[1:])
            else:
                while not re.search(regular_string, '\n'.join(text[l_l:])):
                    if re.search(const_regular_string, '\n'.join(text[l_l + 1:])):
                        num_maybe = re.findall(const_regular_string, '\n'.join(text[l_l + 1:]))
                        for t in num_maybe:
                            if int(t) > last_number:
                                break
                        else:
                            break
                        k_ln += 1
                    else:
                        break
                    regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + \
                                     r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
                while True:
                    l_l += 1
                    if len(text) <= l_l:
                        break
                    if len(text[l_l]) == 0:
                        continue
                    regular_string = r'(?<!\S)(?<!\d)(?<!№\s)' + str(last_number + k_ln) + \
                                     r'\s*[^\d\w]\s*(?=[А-ЯЁA-Zhf0-9«\.].[^\:])'
                    if re.search(regular_string, text[l_l]):
                        line_split = re.split(regular_string, text[l_l])
                        current_line = current_line + line_split[0]
                        text[l_l] = str(last_number + k_ln) + '.' + str(last_number + k_ln).join(line_split[1:])
                        break
                    ch = 0
                    for wl in text[l_l].split():
                        for subt in bibliography_subtitles:
                            if subt in wl.lower():
                                ch += 1
                                break
                    if ch >= len(text[l_l].split()) / 2:
                        l_l += 1
                        break
                    current_line = current_line + text[l_l]
            refer = refer + [str(last_number) + ': ' + current_line.replace('\n', '') + '\nАвторы: ']
            authors = define_author(current_line, last_number)
            not_in_the_text += [str(last_number)+'.'+str(len(dict_all_data[last_number])-1)]
            refer = refer + ['Год: ']
            define_date(current_line, last_number, authors)
            if re.search(r'http://[\S]+', current_line):
                error_link = re.split(r'http://[\S]+', current_line)
                for k in error_link:
                    if re.search(r'[a-zA-Zа-яА-ЯёЁ]', k):
                        break
                else:
                    error_links = error_links + [current_line.replace('\n', '') + '\n\n']
            if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', current_line):
                error_links = error_links + [current_line.replace('\n', '') + '\n\n'] """