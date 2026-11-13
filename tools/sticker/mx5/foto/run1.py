from cut import *
door('oz',2,1375,1528,1790,1918); door('kenwood',2,1356,1494,1934,1996,ks=3.2,lo=.5,hi=.62); door('alpine',2,1350,1482,2017,2054)
door('nos',2,1346,1476,2084,2200,ks=3.2,lo=.5,hi=.62); door('momo',2,1347,1466,2206,2266); door('sparco',2,1352,1465,2284,2356)
door('yokohama',2,1358,1480,2372,2424); door('greddy',2,1368,1480,2444,2500)
cut('pirelli',2,[(1570,1804),(1738,1824),(1710,1932),(1542,1902)],int(183*2.0*3),int(95*3))
sheet(['oz','pirelli','kenwood','alpine','nos','momo','sparco','yokohama','greddy'],'s1.png')
