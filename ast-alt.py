#!/usr/bin/env python
import argparse
import sys
from time import strftime
import math
import urllib.request



def JD_hesaplama(zaman):
    if len(zaman) == 2: #Eğer arguman girildiyse
        tarih=zaman[0]
        saat=zaman[1]
    else:
        tarih_saat = zaman.split(" ") #Eğer argüman girilmediyse ve şimdiki zaman alınacaksa
        tarih = tarih_saat[0]
        saat = tarih_saat[1]

    ay=0
    if tarih[4:6] == "01":
        ay=0
    elif tarih[4:6] == "02":
        ay=31
    elif tarih[4:6] == "03":
        ay=59
    elif tarih[4:6] == "04":
        ay=90
    elif tarih[4:6] == "05":
        ay=120
    elif tarih[4:6] == "06":
        ay=151
    elif tarih[4:6] == "07":
        ay=181
    elif tarih[4:6] == "08":
        ay=212
    elif tarih[4:6] == "09":
        ay=243
    elif tarih[4:6] == "10":
        ay=273
    elif tarih[4:6] == "11":
        ay=304
    elif tarih[4:6] == "12":
        ay=334

    yil_gunsayisi=(int(tarih[0:4])-1998)*365-731.5+((int(tarih[0:4])-2000) // 4)+1
    if ((int(tarih[0:4])-2000) % 4) == 0:
        ay+=1
        yil_gunsayisi -= 1

    saat_gunsayisi = (int(saat[0:2])+ int(saat[2:4])/60+ float(saat[4:6])/3600)/24

    toplam_gun=yil_gunsayisi+ay+saat_gunsayisi+int(tarih[6:8])

    return tarih,saat,ay,yil_gunsayisi,saat_gunsayisi,toplam_gun

def localsiderealtime(gun,ut):
    lst = 100.46 + 0.985647 * gun + LON + 15*ut % 360
    if lst < 0:
        lst +=360
    return lst

def asteroid_names(url):
    asteroid = []
    data = urllib.request.urlopen(url)
    for line in data:
        line = str(line).replace("b'","")
        line = str(line).replace("\\n'","")
        asteroid.append(line)
    return asteroid


now=strftime("%Y%m%d %H%M%S")

parser = argparse.ArgumentParser(
        description="RA-Dec to Alt-Az"
    )

parser.add_argument(
    '-z', '--zaman',
    help="Hangi zaman için alt hesabı yapılacak, yilaygün saatdakikasaniye örnek: 20200215 222020",
    type=str,
    nargs=2,
    default=now
)
parser.add_argument(
    '-a', '--aile',
    help="Hangi aile için alt hesabı yapılacak",
    type=str,
)
parser.add_argument(
    '-c', '--cisim',
    help="Hangi cisim için alt hesabı yapılacak",
    type=str,
    nargs="*",
)
parser.add_argument(
    '-o', '--observatory',
    help="Gözlem yerini belirtiniz tug ya da soao",
    type=str,
)
parser.add_argument(
    '-l', '--limitless',
    help="Parlaklık ya da alt limiti yok",
    action='store_true',
)

arguments = parser.parse_args()

obs = arguments.observatory
if obs == "soao":
    LON = 128.45
    LAT = 36.93
    utfark = 9
    mag_limit = 16.5
elif obs == "tug":
    LON = 30.335555
    LAT = 36.824166
    utfark = 3
    mag_limit=18.5
else:
    print("-o ile tug ya da soao için arama yapınız!")
    exit()


if arguments.limitless:
    alt_limit = -99
    mag_limit = 99
else:
    alt_limit = 20

zaman=arguments.zaman

yil=JD_hesaplama(zaman)[0][0:4]
ay=JD_hesaplama(zaman)[0][4:6]
gun=JD_hesaplama(zaman)[0][6:8]

saat=JD_hesaplama(zaman)[1][0:2]
dakika=JD_hesaplama(zaman)[1][2:4]
saniye=JD_hesaplama(zaman)[1][4:6]

ut = (int(saat)-int(utfark)) + int(dakika)/60 + int(saniye)/3600
if ut < 0:
    ut += 24

ay = JD_hesaplama(zaman)[2]
yil_gun = JD_hesaplama(zaman)[3]

aile = str(arguments.aile)
cisim = str(arguments.cisim)
names = []
if arguments.aile:
    url = "http://193.140.96.170/~t100/orhan/families/" + aile + ".txt"
    names = asteroid_names(url)
elif arguments.cisim:
    names=arguments.cisim

else:
    print("-c ile tek bir cisim ya da -a ile aile adı giriniz!")
    exit()

for name in names:
    ep=str(JD_hesaplama(zaman)[5]+2451545.00000-3/24)

    try:
        vo="http://vo.imcce.fr/webservices/skybot/skybotresolver_query.php?-ep="+ep+"&-name="+name+"&-mime=text&-output=basic&-loc=A84&-refsys=EQJ2000&-from=SkybotDoc"
        
        satir=asteroid_names(vo)[3]
        RA = float(satir.split("|")[2])*15
        DEC = float(satir.split("|")[3])
        dRA = float(satir.split("|")[7])
        dDEC = float(satir.split("|")[8])
        MAG = float(satir.split("|")[5])
        RA_hh=int((RA/15 // 1))
        RA_mm=int(((RA/15-RA_hh) *60 //1))
        RA_ss=int((((RA/15-RA_hh)*60)-RA_mm) * 60 // 1)
        Dec_dd=int(math.modf(DEC)[1])
        Dec_mm=int(math.pow((math.modf(DEC)[0]),2)**(1/2) *60 // 1)
        Dec_ss=int(math.modf(math.pow((math.modf(DEC)[0]),2)**(1/2) *60)[0] * 60 // 1)

        if RA_mm < 10:
            RA_mm = "0"+str(RA_mm)
        if Dec_mm < 10:
            Dec_mm = "0"+str(Dec_mm)
        if RA_ss < 10:
            RA_ss = "0"+str(RA_ss)
        if Dec_ss < 10:
            Dec_ss = "0"+str(Dec_ss)


        if MAG <= mag_limit:

            LST = localsiderealtime(JD_hesaplama(zaman)[5],ut)

            HA = LST - RA

            altitude = 180*math.asin(math.sin(math.radians(DEC))* \
                       math.sin(math.radians(LAT))+math.cos(math.radians(DEC))*math.cos(math.radians(LAT))*math.cos(math.radians(HA)))/math.pi

            if altitude > alt_limit:
                print("\n"+name,"%.1f" % round(altitude,2)+"°",MAG,str(RA_hh)+":"+str(RA_mm)+":"+str(RA_ss)+" "+
                      str(Dec_dd)+":"+str(Dec_mm)+":"+str(Dec_ss)+"\n")
            else:
                print(name, " Gözlenebilir Değil")
        else:
            print(name," Gözlenebilir Değil")
    except IndexError:
        print(name," Asteroid adı bulunamadı!")

if arguments.cisim and altitude > alt_limit and MAG <= mag_limit:
    from urllib.request import urlretrieve
    r= str(RA_hh)+"+"+str(RA_mm)+"+"+str(RA_ss)
    d= str(Dec_dd)+"+"+str(Dec_mm)+"+"+str(Dec_ss)
    url = "https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r="+r+"&d="+d+"&e=J2000&h=21.0&w=21.0&f=gif&c=none&fov=NONE&v3="
    urlretrieve(url, "test.gif")
    from PIL import Image, ImageDraw
    image = Image.open('test.gif').convert("RGBA")
    draw = ImageDraw.Draw(image)
    center_x,center_y = image.size[0],image.size[1]
    dRA_len = dRA*60*21/1250
    dDEC_len = dDEC*60*21/1250

    aci = math.atan(dDEC_len/dRA_len)/math.pi*180
    if aci < 0 and aci > -90 and dRA_len < 0:
        aci = aci + 180
    elif dRA_len < 0 and dDEC_len < 0:
        aci = aci + 180

    draw.line((center_x/2,center_y/2, center_x/2+dRA_len, center_y/2+dDEC_len), fill="red", width=2)
    draw.arc((center_x/2-40,center_y/2-40,center_x/2+40,center_y/2+40), start=aci + 20, end=aci -20, fill=(255, 255, 0))
    image.show()

