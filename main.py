# -*- coding: utf-8 -*-
import re
import os
import argparse
import json


class ConstLists:
    def __init__(self):
        f_classic = open('classic.txt', 'r')
        self.classics = []
        while True:
            a = f_classic.readline()
            if len(a) == 0:
                break
            auth_sp = stemming_author(a.split())
            if len(auth_sp) == 2:
                self.classics = self.classics + [auth_sp[0] + ' ' + auth_sp[1]]
            else:
                self.classics = self.classics + auth_sp
        f_classic.close()
        self.names_bibliography = file_rewrite('names_bibl.txt')
        self.names_pril = file_rewrite('names_pril.txt')
        self.law = file_rewrite('law_paper.txt')
        self.not_the_author = file_rewrite('not_the_author.txt')
        self.list_bibliography = []
        file_bibl = open('list_bibl.txt', 'r')
        while True:
            file_line = file_bibl.readline()
            if len(file_line) == 0:
                break
            self.list_bibliography = self.list_bibliography + [file_line.split()[1]]
        file_bibl.close()
        self.bibliography_subtitles = file_rewrite('bibl_subtitles.txt')
        f_transl = open('transliteration.txt', 'r')
        self.words_transliteration = []
        while True:
            a = f_transl.readline()
            if len(a) == 0:
                break
            a = a.split()
            self.words_transliteration = self.words_transliteration + [[a[0], a[1]]]
        f_transl.close()
        self.all_names = []
        f_woman = open('woman_names.txt', 'r')
        while True:
            a = f_woman.readline()
            if len(a) == 0:
                break
            self.all_names = self.all_names + [stemming_author([a[:-1].lower(), ''])[0]]
        f_woman.close()
        f_man = open('man_names.txt', 'r')
        while True:
            a = f_man.readline()
            if len(a) == 0:
                break
            self.all_names = self.all_names + [stemming_author([a[:-1].lower(), ''])[0]]
        f_man.close()


class DataOfVKR:
    def __init__(self, file1, file2):
        self.dict_all_data = {}
        self.data_footnotes = {}
        self.set_author = set()
        self.set_author_stemming = set()
        self.list_date = []
        self.errors_in_date = []
        self.not_in_the_text = []
        self.string_line = []
        self.set_of_authors_without_links = set()
        self.set_of_missing_links = set()
        self.missing_links = []
        self.error_links = []
        self.grave = []
        self.found_footnotes = []
        self.set_grave = set()
        self.all_penalty = 0
        self.all_chars = 0
        self.n_links = 0
        self.list_of_invalid_links = []
        self.links_on_many_sources = []
        self.footnotes_write = {}
        self.without_penalty = []
        self.references_write = {}
        self.numbers_of_references = {}
        self.file_report1 = open(file1, 'w')
        self.file_report2 = open(file2, 'w')

    def files_close(self):
        self.file_report1.close()
        self.file_report2.close()

    def print_report_1(self, date):
        if len(self.list_date) - len(self.not_in_the_text) >= 20:
            penalty = 0
        else:
            penalty = (20 - len(self.list_date) + len(self.not_in_the_text)) / 20
        self.all_penalty += penalty
        self.file_report2.write('Штрафной балл (литературы, указанной в тексте, меньше 20): ' + str(penalty) + '\n\n')
        new_links_10, new_links_5 = [], []
        for i in self.dict_all_data:
            for j in range(len(self.dict_all_data[i])):
                if date - int(self.dict_all_data[i][j][1]) <= 10:
                    new_links_10 = new_links_10 + [str(i) + '.' + str(j)]
                if date - int(self.dict_all_data[i][j][1]) <= 5:
                    new_links_5 = new_links_5 + [str(i) + '.' + str(j)]
        num_10, num_5 = 0, 0
        self.file_report2.write('Ссылки за последние 5 лет, указанные в тексте: ')
        for i in new_links_5:
            if not (i in self.not_in_the_text):
                num_5 += 1
                if len(self.dict_all_data[int(i.split('.')[0])]) == 1:
                    self.file_report2.write(str(i.split('.')[0]) + ', ')
                else:
                    self.file_report2.write(str(i) + ', ')
        self.file_report2.write('\n\nВсего: ' + str(num_5) + '\n\n')
        self.file_report2.write('Ссылки за последние 10 лет, указанные в тексте: ')
        for i in new_links_10:
            if not (i in self.not_in_the_text):
                num_10 += 1
                if len(self.dict_all_data[int(i.split('.')[0])]) == 1:
                    self.file_report2.write(str(i.split('.')[0]) + ', ')
                else:
                    self.file_report2.write(str(i) + ', ')
        self.file_report2.write('\n\nВсего: ' + str(num_10) + '\n\n')
        if num_5 >= 5:
            penalty = 0
        else:
            penalty = (5 - num_5) / 10
        self.all_penalty += penalty
        self.file_report2.write('Штрафной балл (литературы за последние 5 лет, упомянутой в тексте, меньше пяти): '
                                + str(penalty) + '\n\n')
        if num_10 >= 10:
            penalty = 0
        else:
            penalty = (10 - num_10) / 20
        self.all_penalty += penalty
        self.file_report2.write('Штрафной балл (литературы за последние 10 лет, упомянутой в тексте, меньше десяти): '
                                + str(penalty) + '\n\n\n')

    def print_report_23(self):
        penalty2_3 = 0
        self.file_report2.write('#2\nНеправильно оформленные ссылки: \n')
        if len(self.error_links) == 0:
            self.file_report2.write('отсутствуют\n\n')
        else:
            for i in self.error_links:
                self.file_report2.write(i)
        penalty = len(self.error_links) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty2_3 += penalty
        self.file_report2.write('Штрафной балл (Неправильно оформленные ссылки): ' + str(penalty) + '\n\n\n')
        if len(self.not_in_the_text) == 0:
            self.file_report2.write('#3\nВсе ссылки указаны во всем тексте\n\n')
        else:
            self.file_report2.write('#3\nСсылки, не указанные во всем тексте: ')
            for i in self.not_in_the_text:
                if len(self.dict_all_data[int(i.split('.')[0])]) == 1:
                    self.file_report2.write(str(i.split('.')[0]) + ', ')
                else:
                    self.file_report2.write(str(i) + ', ')
            self.file_report2.write('\nВсего: ' + str(len(self.not_in_the_text)) + '\n\n')
        penalty = (len(self.not_in_the_text) - 10) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty2_3 += penalty
        if penalty2_3 > 0.5:
            penalty2_3 = 0.5
        self.file_report2.write('Штрафной балл (ссылки, неописанные в тексте): ' + str(penalty) + '\n\n\n')
        self.all_penalty += penalty2_3

    def print_report_45678(self):
        penalty4_5_6 = 0
        self.file_report2.write('#4\nСсылки цифрой, которых нет в списке литературы: \n')
        if len(self.list_of_invalid_links) == 0:
            self.file_report2.write('отсутствуют\n\n')
        else:
            for j in self.list_of_invalid_links:
                self.file_report2.write(j)
            self.file_report2.write('Всего ссылок: ' + str(len(self.list_of_invalid_links) // 3) + '\n\n')
        penalty = (len(self.list_of_invalid_links) // 3) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty4_5_6 += penalty
        self.file_report2.write('Штрафной балл (неправильные ссылки): ' + str(penalty) + '\n\n\n')
        self.file_report2.write('#5\nСсылки в тексте, которых нет в списке литературы: \n')
        if len(self.missing_links) == 0:
            self.file_report2.write('отсутствуют\n\n')
        else:
            for j in self.missing_links:
                self.file_report2.write(j)
            self.file_report2.write('Всего уникальных ссылок: ' + str(len(self.set_of_missing_links)) + '\n\n')
        penalty = len(self.set_of_missing_links) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty4_5_6 += penalty
        self.file_report2.write('Штрафной балл (неуказанные ссылки): ' + str(penalty) + '\n\n\n')
        self.file_report2.write('#6\nСсылки на несколько источников: \n')
        if len(self.links_on_many_sources) == 0:
            self.file_report2.write('отсутствуют\n\n')
        else:
            for j in self.links_on_many_sources:
                self.file_report2.write(j)
            self.file_report2.write('\n\nВсего: ' + str(len(self.links_on_many_sources)) + '\n\n')
        penalty = len(self.links_on_many_sources) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty4_5_6 += penalty
        self.file_report2.write('Штрафной балл (ссылки на несколько источников): ' + str(penalty) + '\n\n\n')
        self.file_report2.write('#7\nГруппы авторов:\n')
        if len(self.without_penalty) == 0:
            self.file_report2.write('отсутствуют\n\n')
        else:
            for i in self.without_penalty:
                self.file_report2.write(i)
            self.file_report2.write('\n\n')
        if len(self.string_line) > 0:
            self.file_report2.write('Должны быть ссылки на авторов: \n')
            for i in self.string_line:
                self.file_report2.write(i)
            self.file_report2.write('Всего авторов: ' + str(len(self.set_of_authors_without_links)) + '\n\n')
        else:
            self.file_report2.write('На всех авторов в тексе есть ссылки\n\n')
        penalty = len(self.set_of_authors_without_links) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty4_5_6 += penalty
        self.file_report2.write('Штрафной балл (неописанные авторы): ' + str(penalty) + '\n\n\n')
        if len(self.grave) > 0:
            self.file_report2.write('#8\nВ работе есть "могила ссылок": \n')
            for i in self.grave:
                self.file_report2.write(i)
            self.file_report2.write('Всего: ' + str(len(self.set_grave)) + '\n\n')
        else:
            self.file_report2.write('#8\nВ работе нет "могил ссылок" \n\n')
        penalty = len(self.set_grave) / 20
        if penalty > 0.5:
            penalty = 0.5
        penalty4_5_6 += penalty
        if penalty4_5_6 > 0.5:
            penalty4_5_6 = 0.5
        self.file_report2.write('Штрафной балл ("могилы ссылок"): ' + str(penalty) + '\n\n\n')
        if self.all_chars != 0:
            self.file_report2.write('#9\nСреднее число ссылок в первой главе на количество страниц: '
                                    + str(self.n_links / (self.all_chars / 150)) + '\n\n\n')
        self.all_penalty += penalty4_5_6

    def print_result_penalty(self):
        if self.all_penalty > 2:
            self.all_penalty = 2
        self.file_report2.write('Сумма штрафных баллов: ' + str(self.all_penalty) + '\n\n\n')


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
        return [-1, i]
    return [number, i]


def transliteration(
        author):
    global const_list
    i = 0
    rus_author = ''
    while i < len(author):
        for j in const_list.words_transliteration:
            if author[i: i + len(j[0])].upper() == j[0]:
                rus_author = rus_author + j[1]
                i += len(j[0])
                break
    return rus_author[0] + rus_author[1:].lower()


def words_correction(
        author):
    words = [['A', 'А'], ['C', 'С'], ['E', 'Е'], ['K', 'К'], ['O', 'О'], ['P', 'Р'], ['X', 'Х'],
             ['a', 'а'], ['c', 'с'], ['e', 'е'], ['k', 'к'], ['o', 'о'], ['p', 'р'], ['x', 'х'],
             ['H', 'Н'], ['B', 'В'], ['M', 'М'], ['T', 'Т'], ['Ё', ' Е'], ['ё', 'е']]
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
        data, author, number):
    list_author = [author[0] + ' ' + author[1]]
    data.set_author.update(set(list_author))
    data.dict_all_data[number][-1][0].update(set(list_author))
    author_stemming = stemming_author(author)
    list_author_stemming = [author_stemming[0] + ' ' + author_stemming[1][0]]
    data.set_author_stemming.update(set(list_author_stemming))
    data.dict_all_data[number][-1][1].update(set(list_author_stemming))
    return list_author_stemming


def define_author(
        data, line, number, current_number):
    data.references_write[current_number]['authors'] = []
    authors_return = []
    regular_string = r'((?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s,]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2})|' \
                     r'(?:(?<!\w)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2}' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\-)(?!\–)))'
    set_upper = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    set_lower = set('abcdefghijklmnopqrstuvwxyz')
    if re.search(regular_string, line):
        authors = re.findall(regular_string, line)
        if number in data.dict_all_data:
            data.dict_all_data[number] = data.dict_all_data[number] + [[set(), set()]]
        else:
            data.dict_all_data[number] = [[set(), set()]]
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
                authors_return = authors_return + save_data_of_authors(data, trans, number)
            data.references_write[current_number]['authors'] += [split_auth[0] + ' ' + split_auth[1]]
            authors_return = authors_return + save_data_of_authors(data, split_auth, number)
    else:
        data.references_write[current_number]['authors'] = []
        if number in data.dict_all_data:
            data.dict_all_data[number] += [[set(), set()]]
        else:
            data.dict_all_data[number] = [[set(), set()]]
    return authors_return


def define_date(
        data, line, number, authors, date, current_number):
    data.references_write[current_number]['year'] = ''
    if re.search(r'(?<!\d)(?:\d{4})(?!\d)', line):
        all_date = re.findall(r'(?<!\d)(?:\d{4})(?!\d)', line)
        for i in all_date:
            if (int(i) > 1500) and (int(i) <= date):
                for j in authors:
                    if j in const_list.classics or j.split()[0] in const_list.classics:
                        if date - int(i) >= 10:
                            data.dict_all_data[number][-1] = [data.dict_all_data[number][-1], i]
                            data.list_date = data.list_date + [int(i)]
                            data.references_write[current_number]['year'] = i
                            break
                        else:
                            data.errors_in_date = data.errors_in_date + ['Автор ' + j + ' - классик, неправильный год '
                                                                         + i + '\n\n']
                            data.list_date = data.list_date + [-1]
                            data.dict_all_data[number][-1] = [data.dict_all_data[number][-1], i]
                            data.references_write[current_number]['year'] = i
                            break
                else:
                    data.dict_all_data[number][-1] = [data.dict_all_data[number][-1], i]
                    data.list_date = data.list_date + [int(i)]
                    data.references_write[current_number]['year'] = i
                break
        else:
            data.list_date = data.list_date + [-1]
            data.dict_all_data[number][-1] = [data.dict_all_data[number][-1], -1]
            data.references_write[current_number]['year'] = ''
    else:
        data.list_date = data.list_date + [-1]
        data.dict_all_data[number][-1] = [data.dict_all_data[number][-1], -1]
        data.references_write[current_number]['year'] = ''


def is_in_list_bibliography(
        word):
    global const_list
    fl_k = 0
    for lb in const_list.list_bibliography:
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


def define_author_in_footnote(
        data, line, number):
    data.footnotes_write[number]['authors'] = []
    authors_return = []
    regular_string = r'((?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s,]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2})|' \
                     r'(?:(?<!\w)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*){1,2}' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\-)(?!\–)))'
    set_upper = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    set_lower = set('abcdefghijklmnopqrstuvwxyz')
    if re.search(regular_string, line):
        authors = re.findall(regular_string, line)
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
            author_split_stemming = stemming_author(author_split(i))
            authors_return += [author_split_stemming[0] + ' ' + author_split_stemming[1]]
            data.footnotes_write[number]['authors'] += [author_split(i)[0] + ' ' + author_split(i)[1]]
    return authors_return


def define_date_in_footnote(
        data, line, date, number):
    data.footnotes_write[number]['year'] = ''
    if re.search(r'(?<!\d)(?:\d{4})(?!\d)', line):
        all_date = re.findall(r'(?<!\d)(?:\d{4})(?!\d)', line)
        for i in all_date:
            if (int(i) > 1500) and (int(i) <= date):
                data.footnotes_write[number]['year'] = i
                return int(i)
        return -1
    return -1


def analysis_footnotes(
        data, text, date):
    text = delete_tag(text)
    all_footnotes = re.findall(r'\[\d{1,3}\]', text)
    split_footnotes = re.split(r'\[\d{1,3}\]', text)[1:]
    for i in range(len(all_footnotes)):
        data.footnotes_write[all_footnotes[i][1:-1]] = {}
        data.footnotes_write[all_footnotes[i][1:-1]]['name'] = str(all_footnotes[i]) + split_footnotes[i].rstrip()
        authors = define_author_in_footnote(data, split_footnotes[i], all_footnotes[i][1:-1])
        date_of_footnote = define_date_in_footnote(data, split_footnotes[i], date, all_footnotes[i][1:-1])
        data.footnotes_write[all_footnotes[i][1:-1]]['positions'] = []
        data.data_footnotes[int(all_footnotes[i][1:-1])] = [authors, date_of_footnote]


def find_footnote(
        data, text, date):
    regular_string = r'#Сноска:\[\d{1,3}\]'
    if '#Сноска:' in text:
        footnotes_in_text = re.findall(regular_string, text)
        split_text = re.split(regular_string, text)
        text = ''.join(split_text)
        pos_list_of_footnote = text.find('Список сносок, упомянутых в работе')
        footnotes = text[pos_list_of_footnote + len('Список сносок, упомянутых в работе'):]
        analysis_footnotes(data, footnotes, date)
        text = text[:pos_list_of_footnote]
        for i in footnotes_in_text:
            i = i.split('[')[1].split(']')[0]
            data.found_footnotes += [int(i)]
    return text


def split_all_text_on_parts(
        data, text, date):
    global const_list
    text = text[text.find('</NOMORPH>') + 10:]
    text = text.replace('</table>', '@')
    text = text.replace('&#64285;', '').replace('&#1761;', '').replace('&#691;', '').replace('&#703;', '').\
        replace('&#694; ', '')
    text = text.replace(u'\xa0', u' ')
    text = find_footnote(data, text, date)
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
    for b in const_list.names_bibliography:
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
        data.file_report2.write('Нет списка литературы\n\nСумма штрафных баллов: 0')
        return [1, '', '']
    for p in const_list.names_pril:
        if p.lower() in text.lower():
            num_pril = text.lower().find(p.lower())
            text = text[:num_pril]
    return [0, main, text]


def analysis_found_footnotes(
        data, all_text):
    for i in data.found_footnotes:
        ff = 0
        pos = all_text[0].find('#Сноска:[' + str(i) + ']')
        pos_of_link = [str(pos) + ' ' + str(pos + len('#Сноска:[' + str(i) + ']'))]
        data.footnotes_write[str(i)]['positions'] += pos_of_link
        for j in data.data_footnotes[i][0]:
            if (j.split()[0] + ' ' + j.split()[1][0]) in data.set_author_stemming:
                for d in data.dict_all_data:
                    for sub_d in range(len(data.dict_all_data[d])):
                        if int(data.dict_all_data[d][sub_d][1]) == data.data_footnotes[i][1]:
                            if (j.split()[0] + ' ' + j.split()[1][0]) in data.dict_all_data[d][sub_d][0][1]:
                                ff = 1
                                if (str(d) + '.' + str(sub_d)) in data.not_in_the_text:
                                    data.not_in_the_text.remove(str(d) + '.' + str(sub_d))
                                if str(d) + '.' + str(sub_d) in data.references_write:
                                    data.references_write[str(d) + '.' + str(sub_d)]['positions'] += pos_of_link
                                else:
                                    data.references_write[str(d)]['positions'] += pos_of_link
                                break
                    if ff:
                        break
                if ff:
                    break


def create_list_of_sources_from_all_parts(
        data, text, date, all_text):
    global const_list
    text = text.replace('&quot;', '').lstrip().rstrip()
    regular_string = r'(?<!\S)(?<!:\s)(?<!,\s)(?<!—\s)(?<!\w\s)(?<!§\s)(?<!\d)(?<!№\s)(?<!;\s)(?<!№\s\s)(?<!\.\s\s)' \
                     r'(?<!—\s\s)(?<!»\s)(?<!\?\s)(?<!–\s)(?<!–\s\s)(?<!-\s)(?<!\.\s)(?<!-\s\s)(\d{1,3})' \
                     r'(?![А-ЯЁа-яёA-Za-z0-9«\-])(?!\.[0-9])'
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
            for subt in const_list.bibliography_subtitles:
                if subt in wl.lower():
                    ch += 1
                    break
        if ch >= len(current_line.split()) / 2:
            l_l += 1
            continue
        [number, _] = define_number(current_line)
        if re.search(regular_string, text[l_l][3:]):
            text_line = re.split(regular_string, text[l_l][3:])
            current_line = str(number) + ''.join(text_line[0:3])
            text[l_l] = ''.join(text_line[3:])
            l_l -= 1
        while True:
            l_l += 1
            if len(text) <= l_l:
                break
            if len(text[l_l]) == 0:
                continue
            [_, ind] = define_number(text[l_l])
            if len(text[l_l][ind:]) < 20:
                current_line = current_line + text[l_l]
                continue
            if re.search(regular_string, text[l_l]):
                line_split = re.split(regular_string, text[l_l])
                if len(line_split[0]) == 0:
                    break
                current_line = current_line + ''.join(line_split[0:3])
                text[l_l] = ''.join(line_split[3:])
                l_l -= 1
                continue
            ch = 0
            for wl in text[l_l].split():
                for subt in const_list.bibliography_subtitles:
                    if subt in wl.lower():
                        ch += 1
                        break
            if ch >= len(text[l_l].split()) / 2:
                l_l += 1
                break
            current_line = current_line + text[l_l]
        if str(number) in data.numbers_of_references and data.numbers_of_references[number] > 1:
            current_number = str(number) + '.' + str(data.numbers_of_references[number])
            data.numbers_of_references[number] += 1
        elif str(number) in data.numbers_of_references and data.numbers_of_references[number] == 1:
            data.references_write[str(number) + '.0'] = data.references_write[str(number)]
            del data.references_write[str(number)]
            data.numbers_of_references[number] += 1
            current_number = str(number) + '.1'
        else:
            data.numbers_of_references[number] = 1
            current_number = str(number)
        data.references_write[current_number] = {}
        data.references_write[current_number]['name'] = current_line.replace('\n', '')
        authors = define_author(data, current_line, number, current_number)
        data.not_in_the_text += [str(number)+'.'+str(len(data.dict_all_data[number])-1)]
        define_date(data, current_line, number, authors, date, current_number)
        data.references_write[current_number]['positions'] = []
        if re.search(r'http://[\S]+', current_line):
            error_link = re.split(r'http://[\S]+', current_line)
            for k in error_link:
                if re.search(r'[a-zA-Zа-яА-ЯёЁ]', k):
                    break
            else:
                data.error_links = data.error_links + [current_line.replace('\n', '') + '\n\n']
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', current_line):
            data.error_links = data.error_links + [current_line.replace('\n', '') + '\n\n']
    analysis_found_footnotes(data, all_text)
    year5, year10, year20, non = 0, 0, 0, 0
    for i in data.list_date:
        if i >= date - 5:
            year5 += 1
        if i >= date - 10:
            year10 += 1
        if i >= date - 20:
            year20 += 1
        if i == -1:
            non += 1
    data.file_report2.write('Текущий год: ' + str(date) + '\n\n')
    data.file_report2.write('#1\nОбщее количество ресурсов: ' + str(len(data.list_date)) + '\n')
    data.file_report2.write('Ресурсы за последние 5 лет: ' + str(year5) + '\n')
    data.file_report2.write('Ресурсы за последние 10 лет: ' + str(year10) + '\n')
    data.file_report2.write('Ресурсы ранее 20 лет: ' + str(len(data.list_date) - year20) + '\n')
    data.file_report2.write('Ресурсы, в которых не указан год: ' + str(non) + '\n\n')
    for i in data.errors_in_date:
        data.file_report2.write(i)


def analysis_links(
        data, line, i, new_line, flag_of_bracket, flag_of_type, authors_new_line, all_text):
    ff = 0
    if flag_of_type:
        current_line = authors_new_line
    else:
        current_line = new_line
    for j in data.set_author_stemming:
        if j.split()[0] in words_correction(current_line):
            for d in data.dict_all_data:
                for sub_d in range(len(data.dict_all_data[d])):
                    if str(data.dict_all_data[d][sub_d][1]) in new_line:
                        if (j.split()[0] + ' ' + j.split()[1]) in data.dict_all_data[d][sub_d][0][1]:
                            ff = 1
                            if (str(d) + '.' + str(sub_d)) in data.not_in_the_text:
                                data.not_in_the_text.remove(str(d) + '.' + str(sub_d))
                            pos = len(all_text[0][:all_text[1]]) + all_text[0][all_text[1]:].find(current_line)
                            pos_of_link = [str(pos) + ' ' + str(pos + len(current_line))]
                            if str(d) + '.' + str(sub_d) in data.references_write:
                                data.references_write[str(d) + '.' + str(sub_d)]['positions'] += pos_of_link
                            else:
                                data.references_write[str(d)]['positions'] += pos_of_link
                            all_text[1] = pos + 1
                            break
        if ff:
            break
    else:
        mis_line = line[i - 150 - len(new_line) - 2: i + 150]
        if flag_of_type:
            current_line += ' '
        else:
            current_line = ''
        if not flag_of_bracket:
            data.missing_links = data.missing_links + [current_line + '[' + new_line + ']\n' + mis_line + '\n\n']
        else:
            data.missing_links = data.missing_links + [current_line + '(' + new_line + ')\n' + mis_line + '\n\n']
        if not (new_line in data.set_of_missing_links):
            list_for_set = [current_line + new_line]
            data.set_of_missing_links.update(set(list_for_set))


def define_links(
        data, line, i, new_line, flag_of_bracket, all_text):
    global const_list
    regular_string = r'((?:(?:(?<!\w)(?<!\-)(?:[А-ЯЁA-Z][а-яёa-z]?\.\s*)(?:[А-ЯЁA-Z][а-яёa-z]?\.?\s*)?' \
                     r'[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*(?!\w))(?!\-)(?!\–))|' \
                     r'(?:(?<!\.\s)(?<!\.)(?<!\.\s\s)(?<!<p>\s)(?<!<p>)' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.)\s?(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?:(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z])(?![а-яёa-z])))|' \
                     r'(?:(?<!\w)(?:(?:[А-ЯЁA-Z][а-яёa-z]+(?:[\-\–][А-ЯЁA-Z][а-яёa-z]+)*[\s]*' \
                     r'(?:[А-ЯЁA-Z][а-яёa-z]?\.\s?)(?:[А-ЯЁA-Z][а-яёa-z]?\.?)?)' \
                     r'(?!\s[А-ЯЁA-Z])(?![А-ЯЁA-Z])(?!\.\s[А-ЯЁA-Z])(?!\.[А-ЯЁA-Z]))(?![а-яёa-z])(?!\w)))'
    regular_string_author_in_link = r'[A-ZА-ЯЁ][a-zа-яё]+'
    for lp in const_list.law:
        if lp in new_line.lower():
            break
    else:
        if re.search(regular_string_author_in_link, new_line) and re.search(r'(?<!\d)(?:\d{4})(?!\d)', new_line):
            analysis_links(data, line, i, new_line, flag_of_bracket, 0, '', all_text)
        else:
            if len(new_line) == 4 and new_line.isdigit():
                all_authors_new_line = re.findall(regular_string, line[:len(new_line) - 1])
                if len(all_authors_new_line) != 0:
                    split_current = re.split(regular_string, line[:len(new_line) - 1])
                    if len(split_current[-1]) <= 3:
                        analysis_links(data, line, i, new_line, flag_of_bracket, 1, all_authors_new_line[-1], all_text)


def search_links(
        data, line, all_text):
    regular_string = r'(\[(?:(?:\s*\d{1,3}\s*[,.][^\]]+)|(?:\s*\d{1,3}\s*))(?:(?:;\s*\d{1,3}\s*,[^\]]+)' \
                     r'|(?:[,.]\s*\d{1,3}\s*)|(?:;\s*\d{1,3}\s*))*\])'
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
                define_links(data, line, i, new_line, 0, all_text)
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
                define_links(data, line, i, new_line, 1, all_text)
                new_line = ''
            else:
                new_line = new_line + line[i]
        else:
            if line[i] == '(':
                flag = 6
            if line[i] == '[':
                flag = 3
    return [links, link_separation]


def help_analysis_penalty(
        data, list_of_authors, separation, ind):
    if len(list_of_authors) == 1:
        for i in list_of_authors:
            split_auth = author_split(words_correction(i))
            split_auth_stemming = stemming_author(split_auth)
            flag = def_flag_for_authors(separation, ind)
            if flag == 1:
                continue
            if not ((split_auth[0] + ' ' + split_auth[1]) in data.set_author):
                if not ((split_auth_stemming[0] + ' ' + split_auth_stemming[1][0]) in data.set_author_stemming):
                    for gg in data.string_line:
                        if split_auth[0] + ' ' + split_auth[1] + '\n' + separation[ind][-200:] + i + \
                                separation[ind+1][:200] + '\n\n' in gg:
                            break
                    else:
                        add_string = str(len(data.string_line) + 1) + '. ' + split_auth[0] + ' ' + split_auth[1] + '\n'\
                                     + separation[ind][-200:] + i + separation[ind+1][:200] + '\n\n'
                        data.string_line = data.string_line + [add_string]
                    list_author_stemming = [split_auth_stemming[0] + ' ' + split_auth_stemming[1]]
                    data.set_of_authors_without_links.update(set(list_author_stemming))
    elif len(list_of_authors) >= 2:
        sec = []
        body = []
        for i in list_of_authors:
            sec += [i + '; ']
            body += [separation[ind][-200:] + i]
            ind += 1
        body += [separation[ind][:200]]
        data.without_penalty += sec + ['\n'] + body + ['\n\n']


def analysis_text(
        data, line, all_text):
    global const_list
    line = line.replace('\n', ' ')
    list_of_links = search_links(data, line, [all_text[0], 0])
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
            count_without_penalty = []
            for j in range(len(authors)):
                if authors[j] == '':
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = []
                    continue
                split_auth = author_split(words_correction(authors[j]))
                flag_nta = 0
                for nta in const_list.not_the_author:
                    if nta in split_auth[0]:
                        flag_nta = 1
                        break
                if flag_nta:
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = []
                    continue
                split_auth_stemming = stemming_author(split_auth)
                if split_auth_stemming[0].lower() in const_list.all_names:
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = []
                    continue
                if split_auth[0][0] in set_upper_russian and \
                        not(split_auth[1][0] in set_upper_russian):
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = []
                    continue
                if split_auth[1][0] in set_upper_russian and \
                        not (split_auth[0][0] in set_upper_russian):
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = []
                    continue
                if len(authors_sep[j]) <= 3:
                    count_without_penalty += [authors[j]]
                else:
                    help_analysis_penalty(data, count_without_penalty, authors_sep, j - len(count_without_penalty))
                    count_without_penalty = [authors[j]]
    k_num = -1
    for i in range(len(links)):
        k_num += 1
        number = only_number(links[i])
        if len(number) > 3:
            string_cmp = links[i] + '\n' + link_separation[i][-150:] + links[i] + link_separation[i+1][:150] + '\n\n'
            if not (string_cmp in data.grave):
                data.grave = data.grave + [string_cmp]
            if not (links[i] in data.set_grave):
                list_link_for_set = [links[i]]
                data.set_grave.update(set(list_link_for_set))
        for j in number:
            if j in data.dict_all_data:
                for c in range(len(data.dict_all_data[j])):
                    if str(j) + '.' + str(c) in data.not_in_the_text:
                        data.not_in_the_text.remove(str(j) + '.' + str(c))
                    pos = len(all_text[0][:all_text[1]]) + all_text[0][all_text[1]:].find(links[i])
                    pos_of_link = [str(pos) + ' ' + str(pos + len(links[i])) + '; ']
                    if str(j) + '.' + str(c) in data.references_write:
                        data.references_write[str(j) + '.' + str(c)]['positions'] += pos_of_link
                    else:
                        data.references_write[str(j)]['positions'] += pos_of_link
                    all_text[1] = pos + 1
                if len(data.dict_all_data[j]) > 1:
                    if not ('[' + str(j) + ']; ' in data.links_on_many_sources):
                        data.links_on_many_sources += ['[' + str(j) + ']; ']
            else:
                data.list_of_invalid_links += ['[' + str(j) + ']\n']
                data.list_of_invalid_links += [link_separation[2+k_num][-200:] + '[' + str(j) + ']'] + \
                                              [link_separation[2*k_num + 2][:200] + '\n\n']


def analysis_references(
        data, args, date):
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
    text = line
    line = split_all_text_on_parts(data, line, date)
    if line[0]:
        return
    create_list_of_sources_from_all_parts(data, line[2], date, [text, 0])
    analysis_text(data, line[1], [text, 0])
    data.file_report1.write(json.dumps(data.references_write, ensure_ascii=False, indent=4))
    data.file_report1.write('\n\nСноски:\n\n')
    data.file_report1.write(json.dumps(data.footnotes_write, ensure_ascii=False, indent=4))
    data.print_report_1(date)
    data.print_report_23()
    data.print_report_45678()
    data.print_result_penalty()


def file_rewrite(text):
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
        direct, date):
    if direct[-1] != '/':
        direct += '/'
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
            data_of_vkr = DataOfVKR(direct + list_of_files[n] + '/' + m + '_bibl_list.json',
                                    direct + list_of_files[n] + '/' + m + '_bibl_remarks.txt')
            analysis_references(data_of_vkr, analysis_list, date)
            data_of_vkr.files_close()
        n += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("direct")
    parser.add_argument("date", type=int)
    args = parser.parse_args()
    endings = file_rewrite('endings.txt')
    const_list = ConstLists()
    main_analysis_references(args.direct, args.date)
