# encoding:utf-8
import requests
from selenium import webdriver
from fake_useragent import UserAgent
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from Ftp import read_txt


def get_cookie(groupnum):
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get('https://qun.qq.com/member.html#')
    driver.switch_to.frame('login_frame')
    driver.find_element_by_class_name("face").click()
    driver.switch_to_default_content()
    driver.get('https://qun.qq.com/member.html#gid={}'.format(groupnum))
    a = driver.get_cookies()
    list = []
    # print(a)
    skey = a[5].get('value')
    # print(a)
    b = 5381
    for i in range(0, len(skey)):
        b += (b << 5) + ord(skey[i])
    bkn = (b & 2147483647)
    # print(bkn)
    data = 'gc={}&st=0&end=2000&sort=0&bkn={}'.format(groupnum, bkn)
    for i in a:
        key = i.get('name')
        values = i.get('value')
        cookie = key + '=' + values + ''
        list.append(cookie)
    cookies = '; '.join(list)
    headers = {}
    us = UserAgent()
    ua = us.random
    headers['Cookie'] = cookies
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers['User-Agent'] = ua
    return headers, data, bkn
    # print(headers)


def getdata(headers, data, bkn):
    respone_groupmumid = requests.post('https://qun.qq.com/cgi-bin/qun_mgr/search_group_members', data=data,
                                       headers=headers)
    respone_groupid = requests.post('https://qun.qq.com/cgi-bin/qun_mgr/get_group_list', data='bkn={}'.format(bkn),
                                    headers=headers)
    # print(respone_groupid.json())
    g = respone_groupid.json()
    # print(g)
    for d in g.get('manage'):
        g.get('join').append(d)
    groupid_all = g.get('join')
    # print(groupid_all)
    # for group in groupid_all:
    #     print(group.get('gc'))
    # print(group.get('gn'))
    # print(group.get('owner'))
    # print(respone.json())
    r = respone_groupmumid.json()
    print('{}人群'.format(r.get('max_count')))
    print('管理员人数：{}'.format(r.get('adm_num') + 1))
    print('群里总共人数：{}'.format(r.get('count')))
    t = respone_groupmumid.json().get('mems')
    numlist = []
    for mum in t:
        numlist.append(mum)
    # print('-------------管理员如下----------------')
    # print('{0}{1}{2}{3}{4}{5}{6}'.format('昵称','群名片','QQ号','性别','Q龄','入群时间','最后发言时间'))
    # for a in adminlist:
    #     gname = a.get('card')
    #     jointime = a.get('join_time')
    #     last_speak = a.get('last_speak_time')
    #     qage = a.get('qage')
    #     qq = a.get('uin')
    #     qname = a.get('nick')
    #     if a.get('g') == 0:
    #         ssex = '男'
    #     elif a.get('g') == 255:
    #         ssex = '未知'
    #     else:
    #         ssex = '女'
    #     print('{0}{1}{2}{3}{4}{5}{6}'.format(qname,gname,qq,ssex,qage,jointime,last_speak))
    # print('----------------成员如下------------------')
    # print('{0}{1}{2}{3}{4}{5}{6}'.format('昵称', '群名片', 'QQ号', '性别', 'Q龄', '入群时间', '最后发言时间'))
    # for n in numlist:
    #     gname1 = n.get('card')
    #     jointime1 = n.get('join_time')
    #     last_speak1 = n.get('last_speak_time')
    #     qage1 = n.get('qage')
    #     qq1 = n.get('uin')
    #     qname1 = n.get('nick')
    #     if n.get('g') == 0:
    #         ssex1 = '男'
    #     elif n.get('g') == 255:
    #         ssex1 = '未知'
    #     else:
    #         ssex1 = '女'
    #     print('{0}{1}{2}{3}{4}{5}{6}'.format(qname1, gname1, qq1, ssex1, qage1, jointime1, last_speak1))
    return numlist, groupid_all


def save(numlist):
    # print('1111')
    # print(numlist)
    engine = create_engine('mysql+pymysql://root@localhost:3306/qq_group?charset=utf8mb4')
    Base = declarative_base()
    Base.metadata.drop_all(engine)
    DBSessin = sessionmaker(bind=engine)

    # class
    class QQgroupnum(Base):
        __tablename__ = 'qqgroup_{}'.format(groupid)
        id = Column(Integer, primary_key=True)
        qqname = Column(String(255), nullable=False)
        groupname = Column(String(255), nullable=True)
        qq = Column(String(14), nullable=False)
        sex = Column(String(5), nullable=False)
        qage = Column(Integer, nullable=False)
        ingrouptime = Column(String(25), nullable=False)
        last_speaktime = Column(String(25), nullable=False)

        def __repr__(self):
            return '%s(%r)' % (self.__class__.__name__, self.qqname)

    Base.metadata.create_all(engine)
    for a in numlist:
        gname = a.get('card')
        jointime = a.get('join_time')
        last_speak = a.get('last_speak_time')
        qage = a.get('qage')
        qq = a.get('uin')
        qname = a.get('nick')
        if a.get('g') == 0:
            ssex = '男'
        elif a.get('g') == 255:
            ssex = '未知'
        else:
            ssex = '女'
        session = DBSessin()
        number = QQgroupnum(qqname=qname, groupname=gname, sex=ssex, qage=qage, ingrouptime=jointime, qq=qq,
                            last_speaktime=last_speak)
        session.add(number)
        session.commit()

        def init_db():
            '''
            初始化数据库
            :return:
            '''
            Base.metadata.create_all(engine)

        def drop_db():
            '''
            删除所有数据库
            :return:
            '''
            Base.metadata.drop_all(engine)
        # init_db()
        # drop_db()
    session.close()


if __name__ == '__main__':
    print('你的所有群的群号如下：')
    print('---------------------------------------------------------')
    count = 0
    txt_lsit = []
    f_boot = 'group.txt'
    f = read_txt(f_boot)
    # print(f)
    for i in f:
        t = i.strip('\n')
        print(t)
    print('---------------------------------------------------------')
    groupid = input('请输入要查询的群号：')
    try:
        os.remove('./group.txt')
    except:
        pass
    a = get_cookie(groupid)
    b = getdata(a[0], a[1], a[2])
    for i in b[1]:
        # f.flush()
        # print(i)
        with open('group.txt', 'a+', encoding='utf-8') as f:
            title = str(i.get('gc')) + '(' + str(i.get('gn')) + ')'
            f.write(str(title))
            f.write('\n')

    save(b[0])
