#coding:utf-8

import random
import math

#�������ᣬÿ���������������õķ���
dorms = ['Zeus','Athena','Hercules','Bacchus','Pluto'];

#����ѧ��������ѡ�ʹ�ѡ
prefs=[('Toby', ('Bacchus', 'Hercules')),
       ('Steve', ('Zeus', 'Pluto')),
       ('Karen', ('Athena', 'Zeus')),
       ('Sarah', ('Zeus', 'Pluto')),
       ('Dave', ('Athena', 'Bacchus')), 
       ('Jeff', ('Hercules', 'Pluto')), 
       ('Fred', ('Pluto', 'Athena')), 
       ('Suzie', ('Bacchus', 'Hercules')), 
       ('Laura', ('Bacchus', 'Hercules')), 
       ('James', ('Hercules', 'Athena'))]

# [(0,9),(0,8),(0,7),...,(0,0)]
domain = [(0,(len(dorms)*2)-i-1) for i in range(0,len(dorms)*2)]

def printsolution(vec):
	slots=[]
	#Ϊÿ�����Ὠ������
	for i in range(len(dorms)): slots += [i,i]
	
	#����ÿһ��ѧ���İ������
	for i in range(len(vec)):
		x = int(vec[i])
		
		#��ʣ��Ŀ�����ѡ��
		dorm = dorms[slots[x]]
		#���ѧ�����䱻���������
		print prefs[i][0],dorm
		#ɾ���ò�
		del slots[x]

def dormcost(vec):
	#vecΪ�գ�cost���úܸ�
	if(vec == None): 
		cost = 99999999
		print "dormcost: input is null"
		return cost
	cost = 0
	#����һ��������
	slots=[]
	for i in range(len(dorms)): slots += [i,i]
	
	#����ÿһ��ѧ��

		
	for i in range(len(vec)):
		x = int(vec[i])
		dorm = dorms[slots[x]]
		pref = prefs[i][1]
		#��ѡ�ɱ�ֵΪ0����ѡ�ɱ�ֵΪ1
		if pref[0]==dorm: cost += 0
		elif pref[1] == dorm: cost += 1
		else: cost += 3
		
		#ɾ��ѡ�еĲ�
		del slots[x]
	
	return cost