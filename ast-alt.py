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
    help="Hangi zaman için alt hesabı yapılacak",
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
    help="Hangi gözlem yeri için alt hesabı yapılacak tug ya da soao",
    type=str,
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
        vo="http://vo.imcce.fr/webservices/skybot/skybotresolver_query.php?-ep="+ep+"&-name="+name+"&-mime=text&-output=object&-loc=A84&-refsys=EQJ2000&-from=SkybotDoc"


        satir=asteroid_names(vo)[3]
        RA = float(satir.split("|")[2])*15
        DEC = float(satir.split("|")[3])
        MAG = float(satir.split("|")[5])


        if MAG <= mag_limit:

            LST = localsiderealtime(JD_hesaplama(zaman)[5],ut)
            
            HA = LST - RA

            altitude = 180*math.asin(math.sin(math.radians(DEC))* \
                       math.sin(math.radians(LAT))+math.cos(math.radians(DEC))*math.cos(math.radians(LAT))*math.cos(math.radians(HA)))/math.pi

            if altitude > 20:
                print(name,"%.1f" % round(altitude,2)+"°",MAG,RA,DEC)
            else:
                print(name, " Gözlenebilir Değil")
        else:
            print(name," Gözlenebilir Değil")
    except IndexError:
        print(name," Asteroid adı bulunamadı!")

