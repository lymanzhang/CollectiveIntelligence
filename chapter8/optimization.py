#coding: utf-8
import time 
import random
import math

people = [('Seymour','BOS'),
          ('Franny','DAL'),
          ('Zooey','CAK'),
          ('Walt','MIA'),
          ('Buddy','ORD'),
          ('Les','OMA')]

#Ŀ�ĵأ�ŦԼ��LaGuardia ����
destination='LGA'
flights = {}
#
#for line in file('schedule.txt'):
#	origin, dest, depart, arrive, price = line.strip().split(',')
#	flights.setdefault((origin, dest),[])
	
	#������������ӵ������б���
#	flights[(origin, dest)].append((depart, arrive, int(price)) )


def getminutes(t):
	#����struct_time���� ���꣬�£��գ�ʱ���֣��룬wday,yday,isdst��
	x = time.strptime(t, '%H:%M')
	#x[3]Ϊʱ��x[4]Ϊ��
	return x[3]*60 + x[4]

def printschedule(r):
	for d in range(len(r)/2):
		name = people[d][0]
		origin = people[d][1]
		out = flights[(origin, destination)][r[2*d]]
		ret = flights[(destination, origin)][r[2*d+1]]
		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (
			name,origin,out[0],out[1],out[2],ret[0],ret[1],ret[2])
			
def schedulecost(sol):
	totalprice = 0
	latestarrival = 0
	earliestdep = 24 * 60
	if sol == None:
		totalprice = 999999999
		return totalprice
	
	for d in range(len(sol)/2):
		#�õ����̺���ͷ��̺���
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2*d])]
		returnf = flights[(destination, origin)][int(sol[2*d+1])]
		
		#�ܼ۸�����������̺���ͷ��̺���۸�֮��
		totalprice += outbound[2]
		totalprice += returnf[2]
		
		#��¼������ʱ��������뿪ʱ��
		if latestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])
		if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])
		
	#ÿ���˱����ڻ����ȴ�ֱ�����һ���˵���Ϊֹ
	#����Ҳ��������ͬʱ�䵽����������Ⱥ����ǵķ��̺���
	totalwait = 0
	for d in range(len(sol)/2):
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2*d])]
		returnf = flights[(destination, origin)][int(sol[2*d+1])]
		totalwait += latestarrival - getminutes(outbound[1])
		totalwait += getminutes(returnf[0]) - earliestdep
	
	if latestarrival < earliestdep: totalprice += 50
	
	return totalprice+totalwait
	
def randomoptimize(domain, costf):
	best = 999999999
	bestr = None
	
	for i in range(1000):
		#����һ�������
		r = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
		
		#�õ��ɱ�
		cost = costf(r)
		
		#�뵽Ŀǰδ֪�����Ž���бȽ�
		if cost < best:
			best = cost
			bestr = r
		return bestr

def hillclimb(domain, costf):
	#����һ�������
	sol = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
	
	#��ѭ��
	while(1):
		#�������ڽ���б�
		neighbors = []
		for j in range(len(domain)):
			#��ÿһ�������������ԭֵƫ��һ��
			if sol[j] > domain[j][0]:
				neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j+1:])
			if sol[j] < domain[j][1]:
				neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j+1:])
		
		#�����ڽ���Ѱ�����Ž�
		current =costf(sol)
		best = current
		for j in range(len(neighbors)):
			cost = costf(neighbors[j])
			if cost < best:
				best = cost
				sol = neighbors[j]
		#���û�и��õĽ⣬���˳�ѭ��
		if best == current:
			break
		
	return sol

def annealingoptimize(domain, costf, T = 10000.0, cool = 0.95, step = 1):
	#�����ʼ��ֵ
	vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
	
	while T > 0.1:
		#ѡ��һ������ֵ
		i = random.randint(0, len(domain) -1)
		
		#ѡ��һ���ı�����ֵ�ķ���
		dir = random.randint(-step,step)
		
		#����һ�������������б��ı�����һ��ֵ
		vecb = vec[:]
		vecb[i] += dir
		if vecb[i] < domain[i][0]: vecb[i] = domain[i][0]
		if vecb[i] > domain[i][1]: vecb[i] = domain[i][1]
		
		#���㵱ǰ�ɱ����µĳɱ�
		ea = costf(vec)
		eb = costf(vecb)
		
		#���Ǹ��õĽ��𣿻������������Ž�Ŀ��ܵ��ٽ����
		if (eb < ea or random.random() < pow(math.e,-(eb-ea)/T)):
			vec =vecb
		
		#�����¶�
		T = T * cool
	return vec

def geneticoptimize(domain, costf,popsize =50, step =1,mutprob = 0.2,elite = 0.2, maxiter = 100):
	#�������
	def mutate(vec):
		i = random.randint(0,len(domain) -1)
		if random.random() < 0.5 and vec[i] > domain[i][0]:
			return vec[0:i] + [vec[i] - step] + vec[i+1: ]
		elif vec[i] < domain[i][1]:
			return vec[0:i] + [vec[i] + step] + vec[i+1: ]
		else: 
			return vec
	
	#�������
	def crossover(r1,r2):
		i = random.randint(1,len(domain) - 2)
		return r1[0:i] + r2[i:]
	
	#�����ʼ��Ⱥ
	pop = []
	for i in range(popsize):
		vec = [random.randint(domain[j][0],domain[j][1]) for j in range(len(domain))]
		pop.append(vec)
	
	#ÿһ���ж���ʤ���ߣ�
	topelite = int(popsize * elite)
	
	#��ѭ��
	for i in range(maxiter):
		scores = [(costf(v),v) for v in pop]
		scores.sort()
		ranked = [v for (s,v) in scores]
		#�Ӵ����ʤ���߿�ʼ
		pop = ranked[0:topelite]
		
		#��ӱ������Ժ��ʤ����
		while len(pop) < popsize:
			if random.random() < mutprob:
				#����
				c = random.randint(0, topelite)
				pop .append(mutate(ranked[c]))
			else:
				#����
				c1 = random.randint(0, topelite)
				c2 = random.randint(0, topelite)
				pop.append(crossover(ranked[c1],ranked[c2]))
		
		print scores[0][0]
	
	return scores[0][1]
	