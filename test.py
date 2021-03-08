from datetime import datetime


a = '19:58:21'
b = '20:00:19'

date1 = datetime.strptime(a,r'%H:%M:%S')
date2 = datetime.strptime(b,r'%H:%M:%S')

a = date2-date1

datetime()