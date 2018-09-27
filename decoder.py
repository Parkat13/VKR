# -*- coding: utf-8 -*-

for i in range(21):
    f_t = open('000' + str("{0:0=2}".format(i)) + '.htm', 'r', encoding = 'cp1251')
    f_1 = open('000' + str("{0:0=2}".format(i)) + '_all.txt', 'w')
    f_2 = open('000' + str("{0:0=2}".format(i)) + '_chapter1.txt', 'w')
    f_3 = open('000' + str("{0:0=2}".format(i)) + '_bibliography.txt', 'w')
    a = f_t.read()

    f.write(a)
    f.close()
    f_t.close()
    f_2.close()
    f_3.close()
