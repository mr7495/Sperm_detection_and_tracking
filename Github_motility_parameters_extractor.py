# This code extracts 6 motility parameters from the tracked sperms
# and clusters the tarcked sperms into 6 categories (Rapid,Medium,Slow,Non-Progressive,Progressive,Immotile)
# for more details see https://arxiv.org/abs/2002.04034
# the number 25 refers to 25 frames of the videos in our dataset.
# the number 0.833 refers to the point that each pixel of the videos in our dataset is 0.833um.
import numpy as np
import os
import csv
import json
import matplotlib.pyplot as plt

# Configuring the thresholds
degree=7
mvv=50
lvv=30
min_str=70

name='Detections_test_tracks.json' #Here we load the tracks
with open(name, 'r') as fp:
    tracks = json.load(fp)

#This function calculates the distance between two points
def distance(a,b):
    return(np.sqrt(((a[0]-b[0])**2)+((a[1]-b[1])**2)))
      
#This function uses smoothing for calculating a smoothed average path 
def average_path(track):
    x=[]
    y=[]
    for t in track:
        x.append(t[0])
        y.append(t[1])
    z=np.poly1d(np.polyfit(x,y,deg=degree))
    maxx=max(x)
    minx=min(x)
    newx=list(np.linspace(minx,maxx,1000))
    newy=[]
    for n in newx:
        newy.append(z(n))
    new_track=[]
    for i in range(len(newx)):
        new_track.append([newx[i],newy[i]])
    return(new_track)
    
#This function calculates the VAP value if the smoothed path be given as the first input
#It also can calculate the VCL value if the track be given to it instead
def vap_calculator(smoothed_path,track_length):
    movements=[]
    for i in range(len(smoothed_path)-1):
        move=abs(distance(smoothed_path[i],smoothed_path[i+1]))
        movements.append(move)
    sum_move=np.sum(movements)##3
    mean_velocity=sum_move/((0.5/25)*track_length)
    mean_velocity=mean_velocity*0.833
    return(mean_velocity)
    
#This function calvulates the ALH parameter Value    
def alh_calculator(smoothed_path,track):
    alh_list=[]
    for ntr,tr in enumerate(track):
        distances=[]
        for nsmp,smp in enumerate(smoothed_path):
            distances.append(distance(tr,smp))
        alh_list.append(min(distances))
    mean_alh=np.mean(alh_list)
    return(mean_alh*0.833)
    
    
#Getting the vsl(um/s) value for each video sample  
vsl={}
for key in tracks.keys():
    vsl[key]=[]
    for track in tracks[key]:
        movement=abs(distance(track[0],track[-1]))
        movement_velocity=movement/((0.5/25)*len(track))
        movement_velocity=movement_velocity*0.833
        vsl[key].append(movement_velocity)


#Getting the vcl(um/s) value for each video sample  
vcl={}
for key in tracks.keys():
    vcl[key]=[]
    for track in tracks[key]:
        vcl_calculated=vap_calculator(track,len(track))
        vcl[key].append(vcl_calculated)

#Getting the vap(um/s) value for each video sample  
vap={}
for key in tracks.keys():
    vap[key]=[]
    for num_track,track in enumerate(tracks[key]):
        smoothed_path=average_path(track)
        vap_calculated=vap_calculator(smoothed_path,len(track))
        if vap_calculated < vsl[key][num_track]:
            vap_calculated=vsl[key][num_track]
        if vap_calculated > vcl[key][num_track]:
            vap_calculated=vcl[key][num_track]
        vap[key].append(vap_calculated)

#Getting the LIN(%) value for each video sample  
lin={}
for key in tracks.keys():
    lin[key]=[]
    for num_track,track in enumerate(tracks[key]):
        LIN=(vsl[key][num_track]/vcl[key][num_track])*100
        lin[key].append(LIN)

#Getting the STR(%) value for each video sample  
sstr={}
for key in tracks.keys():
    sstr[key]=[]
    for num_track,track in enumerate(tracks[key]):
        STR=(vsl[key][num_track]/vap[key][num_track])*100
        if vsl[key][num_track]==0:
            STR=0
        sstr[key].append(STR)
        
#Getting the ALH(um) value for each video sample    
alh_mean={}
for key in tracks.keys():
    alh_mean[key]=[]
    for num_track,track in enumerate(tracks[key]):
        smoothed_path=average_path(track)
        alh_calculated_mean=alh_calculator(smoothed_path,track)
        alh_mean[key].append(alh_calculated_mean)



#Clustering into 6 categories(Rapid,Medium,Slow,Non-Progressive,Progressive,Immotile)
motility_params1={}
for key in tracks.keys():
    motility_params1[key]=[]
    for num_track,track in enumerate(tracks[key]):
        vap_value=vap[key][num_track]
        vcl_value=vcl[key][num_track]
        if vap_value>=mvv:
            motility_params1[key].append('rapid')
        elif vap_value<mvv and vap_value>=lvv:
            motility_params1[key].append('medium')        
        elif vap_value<lvv:
            if vap_value>8.33:
                motility_params1[key].append('slow')   
            else:
                motility_params1[key].append('immotile')
                
numbers1={}
percent1={}
for key in motility_params1.keys():
    numbers1[key]={'immotile':0,'slow':0,'medium':0,'rapid':0}
    percent1[key]={'immotile':0,'slow':0,'medium':0,'rapid':0}
    for value in motility_params1[key]:
        numbers1[key][value]+=1
    all_counted=(numbers1[key]['immotile']+numbers1[key]['slow']+numbers1[key]['medium']+numbers1[key]['rapid'])
    percent1[key]['immotile']=(numbers1[key]['immotile']/all_counted)*100
    percent1[key]['slow']=(numbers1[key]['slow']/all_counted)*100
    percent1[key]['medium']=(numbers1[key]['medium']/all_counted)*100
    percent1[key]['rapid']=(numbers1[key]['rapid']/all_counted)*100
    
    
motility_params2={}
for key in tracks.keys():
    motility_params2[key]=[]
    for num_track,track in enumerate(tracks[key]):
        vap_value=vap[key][num_track]
        vcl_value=vcl[key][num_track]
        str_value=sstr[key][num_track]
        if vap_value>=mvv and str_value>=min_str: 
            motility_params2[key].append('progressive')
        else:
            if vap_value>8.33:
                motility_params2[key].append('non-progressive')
            else:
                motility_params2[key].append('immotile')

numbers2={}
percent2={}
for key in motility_params2.keys():
    numbers2[key]={'immotile':0,'non-progressive':0,'progressive':0}
    percent2[key]={'immotile':0,'non-progressive':0,'progressive':0}
    for value in motility_params2[key]:
        numbers2[key][value]+=1
    all_counted=len(motility_params2[key])
    percent2[key]['immotile']=(numbers2[key]['immotile']/all_counted)*100
    percent2[key]['non-progressive']=(numbers2[key]['non-progressive']/all_counted)*100
    percent2[key]['progressive']=(numbers2[key]['progressive']/all_counted)*100

    
#This part outputs a csv file containing all of the data for each video
with open('Motility_data.csv', 'w',newline='') as csvfile:
    csvwriter=csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(['Video Name','Immotile Sperms','Slow Sperms','Medium Velocity Sperms','Rapid Sperms',
    'Immotile Sperms','Non-Progressive Sperms','Progressive Sperms',
    'VSL','VAP','VCL','STR','LIN','ALH'])
    for key in tracks.keys():
        data=[key]
        for n1key in numbers1[key]:
            inputt=str(numbers1[key][n1key])+'/'+str(len(tracks[key]))+'({}%)'.format(percent1[key][n1key])
            data.append(inputt)
        for n2key in numbers2[key]:
            inputt=str(numbers2[key][n2key])+'/'+str(len(tracks[key]))+'({}%)'.format(percent2[key][n2key])
            data.append(inputt)
        data.append(np.mean(vsl[key]))
        data.append(np.mean(vap[key]))
        data.append(np.mean(vcl[key]))
        data.append(np.mean(sstr[key]))
        data.append(np.mean(lin[key]))
        data.append(np.mean(alh_mean[key]))
        csvwriter.writerow(data)



#This function plots the smoothed path and the tracked points
track=tracks['af_7'][0] #You can choose any sperm track of any video
def visualize_smoothed_path(track=track):
    smoothed_path=average_path(track)
    x=[]
    y=[]
    sx=[]
    sy=[]
    for i in range(len(track)):
        x.append(track[i][0])
        y.append(track[i][1])
    for i in range(len(smoothed_path)):
        sx.append(smoothed_path[i][0])
        sy.append(smoothed_path[i][1])
    plt.plot(x,y,'r',linestyle='--', marker='*', markersize=11)
    plt.plot(sx,sy,'b',linestyle='--', marker='o', markersize=1)
    plt.grid()




#You can use this function for saving all of the smoothed pathes of every tracked sperm
def save_smoothed_pathes(tracks=tracks):
    try:
        os.mkdir('plots')
    except:
        pass
    key_num=0
    for key in tracks.keys():
        try:
            os.mkdir(os.path.join('plots',key))
        except:
            pass
        for numt,track in enumerate(tracks[key]):
            smoothed_path=average_path(track)
            x=[]
            y=[]
            sx=[]
            sy=[]
            for i in range(len(track)):
                x.append(track[i][0])
                y.append(track[i][1])
            for i in range(len(smoothed_path)):
                sx.append(smoothed_path[i][0])
                sy.append(smoothed_path[i][1])
            plt.figure(numt+key_num)
            plt.plot(x,y,'r',linestyle='--', marker='*', markersize=11)
            plt.plot(sx,sy,'b',linestyle='--', marker='o', markersize=1)
            plt.grid()
            address='plots/'+key+'/'+str(numt)+'.png'
            plt.savefig(address)
        key_num+=len(tracks[key])

