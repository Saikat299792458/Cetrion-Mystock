import os,sys,requests
from bs4 import BeautifulSoup as bs
from datetime import datetime,timedelta
dn=datetime.now()
def extract(dls,dle,inst='All Instrument'):
    payload,ldate = {'startDate': (dn-timedelta(dls)).strftime('%Y-%m-%d'),
            'endDate': (dn-timedelta(dle)).strftime('%Y-%m-%d'),
            'inst': inst,
            'archive': 'data'}, (dn - timedelta(dle+30))
    try:
        data=requests.get('https://www.dsebd.org/dse_close_price_archive.php',params=payload).text
    except Exception as e:
        print(e)
        quit()
    print('Parsing HTML...')
    soup,cstock,clist,list=bs(data,'html5lib'),'',[],[]
    del data
    print('Finding Data...')
    table=soup.find('table',class_='table table-bordered background-white')
    b,nm=table.tbody.find_all('tr'),False
    del table
    def append():
        nonlocal clist, ldate, cstock, list
        tempdate=datetime.strptime(clist[0].split(',')[0],'%Y-%m-%d')
        if (tempdate-ldate).days>=0:
            ldate=tempdate
        list.append({'Name':cstock,'Data':clist})
        print('Data listed for '+cstock,end='\r')
    for i in b:
        name=i.find('a').text.split()[0]
        if cstock!=name:
            if clist!=[]:
                append()
            cstock,clist=name,[]
        j,temp=i.find_all('td'),[]
        temp=[l.text for k,l in enumerate(j) if k in [1,3]]
        clist.append(','.join(temp)+'\n')
    append()
    print()
    del b
    ldate,ul=ldate.strftime('%Y-%m-%d'),[]
    print('Updating list...')
    for i in list:
        if i['Data'][0].split(',')[0] == ldate:
            ul.append(i)
    del list
    return ul
os.chdir(sys.path[0])
if os.path.isdir('csv'):
    try:
        e=open('Date.txt','r')
        Day=(dn-datetime.strptime(e.read(),'%Y-%m-%d')).days
        e.close()
    except Exception as e:
        print(e)
        quit()
    if Day < 0:#Do not lose Date.txt, I don't want to add a date recovery function just for this missing date log
        print('Data already updated!')
        quit()
    os.chdir('csv')
    list=extract(Day,0)
    files=[f for f in os.listdir() if os.path.isfile(f)]
    for i in list:
        fstream=open(i['Name']+'.csv','a')
        if fstream.name not in files:
            i=extract(730,0,inst=i['Name'])[0]
            fstream.write('Date,Close\n')
        else:
            files.remove(fstream.name)
        print('Writing in '+fstream.name,end='\r')
        i['Data'].reverse()
        for j in i['Data']:
            fstream.write(j)
        fstream.close()
    if len(list)>0:
        for i in files:
            os.remove(i)
else:
    list1=extract(365,0)
    list2=extract(730,366)
    os.mkdir('csv')
    os.chdir('csv')
    for i in list1:
        for j in list2:
            if i['Name']==j['Name']:
                i['Data']+=j['Data']
                break
        fstream=open(i['Name']+'.csv','w')
        print('Writing in '+fstream.name,end='\r')
        fstream.write('Date,Close\n')
        i['Data'].reverse()
        for j in i['Data']:
            fstream.write(j)
        fstream.close()
#Save Checkpoint
print()
os.chdir(sys.path[0])
with open('Date.txt','w') as e:
    e.write((dn+timedelta(1)).strftime('%Y-%m-%d'))
    e.close()
print('Done!')
quit()
