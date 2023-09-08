# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:55:38 2023

@author: dschmidt
"""


import os
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.path import Path
from matplotlib import pyplot as plt
from matplotlib import transforms

SavePlots = True
RangeBearing = True
PB3config = False
offset = 0
verts = [
    (0., 1.),
    (0.5, -1.),
    (0., -0.25),
    (-0.5, -1.),
    (0, 1)
    ]

codes = [
    Path.MOVETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CLOSEPOLY
    ]

PB3 = [40.04246833,-73.97525333] 
TB1 = [ 39.958247, -73.996408] 
if PB3config:
    ## Currently measured manually in image which is stupid - needs to be programmatic
    pixel2NM = 102
else:
    pixel2NM = 100

m2nm = 1.0 / 1852.0
path = Path(verts, codes)


def polarNormY( brng_d, rng_m, yOrigin ):
    ## Add 90 for bearing to unit circle alignment, where unit circle 90deg == bearing 0deg
    y = yOrigin + ( np.sin( np.deg2rad( 1*((brng_d - 90 + offset) % 360)) ) * rng_m * m2nm * pixel2NM )
    return int(y)

def polarNormX( brng_d, rng_m, xOrigin ):
    ## Add 90 for bearing to unit circle alignment, where unit circle 90deg == bearing 0deg
    x = xOrigin + (np.cos( np.deg2rad( 1*((brng_d - 90 + offset) % 360)) ) * rng_m * m2nm * pixel2NM )
    return int(x)
    
def normalizeLong( lon, longspan, w, base):
    return int( ( base + lon ) / float( longspan ) * w )

def normalizeLat( lat, latspan, h, base):
    return int( ( base - lat ) / float( latspan ) * h )

    
def reduce( df ): 
    meta = df['meta'].values
    lat = []
    lon = []
    brng = []
    rng = []
    created = []
    sender = []
    mmsi = []
    cog = []
    sog = []
    for row in meta:
        row = row.replace("true","True")
        row = row.replace("false","False")
        row = row.replace("null","None")
        full = dict(eval(row))
        try:
            mmsi.append(full['Mmsi'])
        except:
            mmsi.append(full['TargetNumber'])
        try:
            lat.append(full['TargetLatitude'])
        except:
            lat.append(full['Latitude'])
        try:
            lon.append(full['TargetLongitude'])
        except:
            lon.append(full['Longitude'])
        try:
            brng.append(full['ConningBearingDeg'])
        except:
            brng.append(0)
        try:
            rng.append(full['ConningDistanceM'])
        except:
            rng.append(0)
        try:
            sender.append(full['SenderId'])
        except:
            sender.append(full['SenderID'])
        try: 
            cog.append(full['CourseOverGround'])
        except:
            try: 
                cog.append(full['TrueTargetCourseDeg'])
            except:
                cog.append(0)
        try:
            sog.append(full['TrueTargetSpeedMs'])
        except:
            try: 
                sog.append(full['SpeedOverGround'])
            except:
                sog.append(0)
            
    created = df['created'].values
    created = [elem.split(" ")[1] for elem in created]
    filtered = pd.DataFrame({
        'created':created,
        'sender': sender,
        'mmsi': mmsi,
        'lat': lat,
        'lon': lon,
        'brng': brng,
        'rng': rng,
        'cog': cog,
        'sog': sog
        })
    print("CSV filtered to dataframe")
    return filtered


NWhemi = np.asarray(Image.open(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NWhemi.jpg'))
#TB1png = np.asarray(Image.open(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\TB1_test_area.png'))
#PB3png = np.asarray(Image.open(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\PB3NJ_test_theatre.PNG"))
PB3png = np.asarray(Image.open(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\PB3_NJ_DHS.PNG"))
TB1png = np.asarray(Image.open(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\ARPAclocking\TB1_Theatre_3NM.PNG"))


#df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\Test_Videos\KnownAIS\dbWrites_fromFathom5_testdata2.csv")
#df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\Reduced\NJ_DHS_AISday1_8_23_23.csv")
#fname = r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\NJ_DHS_ARPAday1_8_23_23.csv'
#fname = r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\ARPAclocking\TB1_9_5_23_ARPA_traffic.csv"
fname = r"C:/Users/dschmidt.OCEANPOWERTECH/Documents/Test_Data/ARPAclocking/ARPArotation_ARPA.csv"
df = pd.read_csv(fname)
fig = plt.figure(0)

filtered = reduce( df )
#filtered = df

class PlotVals:
    colorDict = {}
    chooseColor = []
    labels = set()
    mmsi_count = {}
    def __init__(self, mmsi_count ):
        self.chooseColor = [(np.round(np.random.rand(),1),
                             np.round(np.random.rand(),1),
                             np.round(np.random.rand(),1)) for i in range(100)]    
        self.mmsi_count = mmsi_count
    def mmsi_color_picker(self, mmsi):
        if mmsi not in self.colorDict.keys():
            self.colorDict[ mmsi ] = self.chooseColor.pop(0)
        return self.colorDict[ mmsi ]
    def labelin( self, name):
        if name in self.labels:
            return "__nolegend__"
        else:
            self.labels.add( name )
            if ARPAswitch:
                return str(name) + " " +  str(self.mmsi_count[ name ]) +'x'
            else:
                sub = str(name)
                remain = 9-len(sub)
                sub = "0"*remain + sub
                return str(sub) + " " +  str(self.mmsi_count[ name ]) +'x'

###############################################################################
#### Map of lat long writes for all assets ####################################
###############################################################################
ax = fig.add_subplot(111)
fig.tight_layout()
plt.ion()
ax.grid(False)
# longBounds = [ -180, 15 ]
# latBounds = [ 0, 90 ]
# longspan = longBounds[ 1 ] - longBounds[ 0 ]
# latspan = latBounds[ 1 ] - latBounds[ 0 ]
# h,w,_ = NWhemi.shape
# a,b = -1*longBounds[0], latBounds[1]

## Config settings
if "ARPA" in fname:
    ARPAswitch = True
else:
    ARPAswitch = False

if PB3config:
    h1,w1,_ = PB3png.shape
    longBounds1 = [-74.10, -73.86]
    latBounds1 = [39.97, 40.12]
    longspan1 = longBounds1[ 1 ] - longBounds1[ 0 ]
    latspan1 = latBounds1[ 1 ] - latBounds1[ 0 ]
    a1,b1 = -1*longBounds1[0], latBounds1[1]
    assetNorm = [ normalizeLat(  PB3[0],  latspan1, h1, b1 ), 
                  normalizeLong( PB3[1], longspan1, w1, a1 )]
    img = PB3png
    assetName = "PB3-005"
else:
    h1,w1,_ = TB1png.shape
    longBounds1 = [-74.10, -73.866666667]
    latBounds1 = [39.8666666666667, 40.10]
    longspan1 = longBounds1[ 1 ] - longBounds1[ 0 ]
    latspan1 = latBounds1[ 1 ] - latBounds1[ 0 ]
    a1,b1 = -1*longBounds1[0], latBounds1[1]
    assetNorm = [ normalizeLat(  TB1[0],  latspan1, h1, b1 ), 
                  normalizeLong( TB1[1], longspan1, w1, a1 )]
    img = TB1png
    assetName = "TB1"

if RangeBearing:
    filtered['normLon'] = filtered.apply( lambda x: polarNormX( x[ 'brng' ], x['rng'], assetNorm[1] ), axis=1)
    filtered['normLat'] = filtered.apply( lambda x: polarNormY( x[ 'brng' ], x['rng'], assetNorm[0] ), axis=1)
else:
    filtered['normLon'] = filtered.apply( lambda x: normalizeLong( x[ 'lon' ], longspan1, w1, a1 ), axis=1)
    filtered['normLat'] = filtered.apply( lambda x: normalizeLat(  x[ 'lat' ], latspan1,  h1, b1 ), axis=1)

#import pdb; pdb.set_trace()
###############################################################################
#### Full hemisphere map of datawrites ########################################
###############################################################################
ax.set_title("Fathom5 DB Writes: NJ Testing Day1")
ax.set_xlabel("Lon - deg")
ax.set_ylabel("Lat - deg")
print(filtered['sender'].value_counts())
ax.imshow(img)
for asset, data in filtered.groupby('sender'):
    t = np.arange(len(data['lat']))
    ax.scatter(data['normLon'], data['normLat'], 5, label=asset, linewidth=0.5, ec='k', color = 'b', marker = 'o') #, c=t)    
    sub = data['sender'].values[0].split(":")[0] #+ " " + data['created'].values[0]
    ax.text(data['lon'].values[-1],
            data['lat'].values[-1],
            sub,
            horizontalalignment="right",
            verticalalignment='top',
            fontsize=6,color='k')
    
ax.scatter(assetNorm[1], assetNorm[0], s=50,marker="^",c="r", label="PB3 TruPos")

ax.legend(loc='lower right')
ax.set_xlim( 0, w1 )
ax.set_ylim( h1, 0 )
plt.show()


#import pdb;pdb.set_trace()
###############################################################################
############## Specific asset uploads== gss-desktop:#### is TB1 ###############
###############################################################################
### Truth Map



for mmsi, subfilt in filtered.groupby(by='mmsi'):
    fig2 = plt.figure()
    fig2.tight_layout()
    ax = fig2.add_subplot(111)
    plt.ion()
    ax.imshow(img)
    working_title = f"{mmsi}_" + os.path.basename(fname).split(".")[0]
    ax.set_title( working_title )
    ax.set_xlabel("Lon - deg")
    ax.set_ylabel("Lat - deg")
    thisAsset = subfilt 
    #filtered #[ filtered['sender'] == "gss-desktop:1914" ]
    #thisAsset = filtered [ filtered['sender'] == "gss-desktop:1914" ] 
    #thisAsset = thisAsset [ thisAsset['mmsi'] == "367327080"]
    t = np.arange( len(thisAsset['lat'].values) )
    tstep = 4
    count = tstep
    alt = 0 
    thisPlot = PlotVals( thisAsset['mmsi'].value_counts() )
    for l,i,j,mm, rot in zip(thisAsset['lat'],thisAsset['normLat'], thisAsset['normLon'],
                               thisAsset['mmsi'],thisAsset['cog']):
        if l == 91:
            ## Position unknown declaration, throw this away ## 
            continue
        thisColor = color = thisPlot.mmsi_color_picker(mm)
        ### Correct method ###
        if rot:
            thisMarker = path.transformed(transforms.Affine2D().rotate_deg( -1*(rot + offset) ))
            ax.plot(j,i,marker = thisMarker, markersize= 11, mfc = thisColor, 
                    linestyle = '', color = 'k',linewidth=0.05,
                    label= thisPlot.labelin( mm ))
        else:
            ax.scatter(j,i,s= 20, # max(20, int(  thisPlot.mmsi_count[mm] / 2.0 )),
                        marker = 'o', color = thisColor, label= thisPlot.labelin( mm ))
        ### Incorrect method ####
        
        count += 1
        
    ## Plot Target circles
    
    # radii = [0.01666666666,2*0.01666666666,3*0.01666666666]  ## 1deg lat = 60NM, so 1deg/60 = 1NM
    # center = (PB3[1], PB3[0])
    # t = np.linspace(0, 2*np.pi, 100)
    # for rad in radii:
    #     x = normalizeLat(center[0] + rad * np.cos(t), latspan, h, b)
    #     y = normalizeLong(center[1] + rad * np.sin(t), longspan, w, a)
    #     ax.plot(y,x, color = 'y', linewidth=0.25, linestyle='--', dashes=(5, 2))
    
    ## Plot first and final contact reported time
    
    xval = 15 #fixed xval
    ax.text(w1-xval,-xval, "Final Contact",
                         horizontalalignment="right",
                         verticalalignment='top',
                         rotation = 0,
                         fontsize=6.5,fontweight='bold',
                         color='k', 
                         bbox=dict(facecolor='c', edgecolor='k', boxstyle='round,pad=0.2'))
    ax.text(xval,-xval, "Initial Contact",
                         horizontalalignment="left",
                         verticalalignment='top',
                         rotation = 0,
                         fontsize=6.5,fontweight='bold',
                         color='w', 
                         bbox=dict(facecolor='k', edgecolor='k', boxstyle='round,pad=0.2'))
    #for mmsi, dat in thisAsset.groupby(by="mmsi"):
    if True:
        dat = thisAsset
        lat = dat['lat'].values[0]
        if lat == 91:
            continue
        if ARPAswitch:
            sub = mmsi
        else:
            sub = str(mmsi)
            remain = 9-len(sub)
            sub = "0"*remain + sub
        try: 
            cr0 = dat["created"].values[0].split(" ")[1]
            deleted = dat["created"].values[-1].split(" ")[1]
        except: 
            cr0 =dat["created"].values[0]
            deleted =dat["created"].values[-1]
        i0 = dat['normLat'].values[0]
        i1 = dat['normLat'].values[-1]
        j0 = dat['normLon'].values[0]
        j1 = dat['normLon'].values[-1]
        ## Correct method ##
        
        if sub == 24:
            yshift = int(0.8*i0)
        else: yshift = i0
        ax.plot([xval,j0],[yshift,i0],color='w',linestyle=(0, (5, 10)),linewidth=0.4)
        ax.text(xval,yshift, f"{cr0}",
                              horizontalalignment="left",
                              verticalalignment='center',
                              rotation = 0,
                              fontsize=5.5,color='w', 
                              bbox=dict(facecolor='k', edgecolor='k', boxstyle='round,pad=0.2'))
        
        ax.plot([w1-xval,j1],[i1,i1],color='w',linestyle=(0, (5, 10)),linewidth=0.4)
        ax.text(w1-xval,i1, f"{deleted}",
                              horizontalalignment="right",
                              verticalalignment='center',
                              rotation = 0,
                              fontsize=5.5,color='k', 
                              bbox=dict(facecolor='c', edgecolor='k', boxstyle='round,pad=0.2'))

    print(sub)
    ax.set_facecolor('black')
    ax.set_xticklabels((str(val) for val in np.around( np.linspace( longBounds1[0], longBounds1[1], 6 ), 2) ))
    ax.set_yticklabels((str(val) for val in np.around( np.linspace( latBounds1[1], latBounds1[0], 6 ), 2) ))
    ax.scatter(assetNorm[1], assetNorm[0], s=50,marker="^",c="r", label=f"{assetName} TruPos")
    ## Known AIS Test lat long bounds
    ax.set_xlim( 0, w1 )
    ax.set_ylim( h1, 0 )     
    
    ## AIS Jitter test bounds
    l = ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.1,1.0))
    if SavePlots:
        plt.savefig(os.path.join( 
            os.path.dirname( fname ), working_title + ".png"),
                    bbox_inches ="tight",
                    pad_inches = 0.25,
                    dpi=250,
                    orientation ='landscape')
    #plt.tight_layout()
    # l.set_title("MMSI \ndbWrite Density")
    # l.get_frame().set_facecolor((0.9,0.9,0.9))
    # l.get_frame().set_edgecolor("k")
    # for text in l.get_texts():
    #     text.set_color("k")
    
    plt.show()

print( "---------------------------------------------------------\n\t")
print( "ARPA Detection Statistics")
print( "Mean ARPA detection range:", filtered['rng'].mean() * m2nm,"NM")
print( "Stdev ARPA detection range:", filtered['rng'].std() * m2nm,"NM")
print( "Median ARPA detection range:", filtered['rng'].median(),"m")
    

    
