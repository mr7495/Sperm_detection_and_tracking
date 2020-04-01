#Modified CSR-DCF Tracker
#note: This code has been written based on 25 frames per video. If you like to change 25, refer to the points highlighted by ###
#a sample of annotation exist in this repository.
import csv
import cv2
import os
import numpy as np
import time

# This code reads the annotation for evaluating the results of the tracker
def get_anno(address='Path to the Ground-truth'):
      y=[[]]
      anno={}
      z=None
      address=address
      with open(address, newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            j=0
            for row in csvreader:
                  if z is not None and row[0][:-7]!=z[0][:-7]:
                        y=[]
                        j=-1
                  if z is not None and int(row[0][-6:-4])<int(z[0][-6:-4]):
                        y.append([])
                        j=j+1
                  X=(int(row[1])+int(row[3]))/2
                  Y=(int(row[2])+int(row[4]))/2
                  y[j].append([X,Y])
                  z=row
                  anno[row[0][:-7]]=y  
      return(anno)  
        
        
        
        
#This function is the tracker function (Modified CSR-DCF)        
def get_tracks(videos_path='Path to the folder containing video samples',anno_path='Path to the detections or Ground-Truth'):
      path=videos_path
      files=[]
      for r,d,f in os.walk(path):
            for file in f:
                  if '.avi' in file: #if your video format is something other than avi change avi to your video foramt.
                        files.append(os.path.join(r,file))
    
      videos=files.copy()
      all_tracks={}
      all_tracks_details={}
      frame_index_list=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25']
      ### Line above must be changed if you have more or less than 25 frames in a video sample.
      for video in videos:
            i=1
            read_flag = True
            vs = cv2.VideoCapture(video)
            while(read_flag):
                  read_flag,frame = vs.read()
                  if frame is not None:
                        globals()['frame%s'%i]=frame
                        i=i+1
            name = video[len(path)+1:-4]
            for i in frame_index_list:
                  globals()['frame%s_sperms'%i]=[]
            for i in range(len(frame_index_list)):
                  globals()['frame%s_selected_sperms'%(i+1)]=[]
            for i in range(len(frame_index_list)):
                  globals()['frame%s_non_selected_sperms'%(i+1)]=[]
            for i in range(len(frame_index_list)):
                  globals()['frame%s_selected_details'%(i+1)]=[]
            frames_sperms=[]
            with open(anno_path, newline='') as csvfile:
                  csvreader = csv.reader(csvfile)
                  for row in csvreader:
                        if row[0][:-7]==name:
                              for frame_index in frame_index_list:
                                    if row[0][-6:-4]==frame_index:
                                          x=int(row[1])
                                          y=int(row[2])
                                          w=int(row[3])-int(row[1])
                                          h=int(row[4])-int(row[2])
                                          globals()['frame%s_sperms'%frame_index].append((x,y,w,h))
            for i in frame_index_list:
                  frames_sperms.append(globals()['frame%s_sperms'%i])
           
      
            
            tracks=[] 
            tracks_details=[]
            frame_num=0
            for frame_sperms in frames_sperms :
                  j=-1
                  frame_num+=1
                  if frame_num==25: ### Last frame of a video sample.
                        continue
                  for initBB_index,initBB in enumerate(frame_sperms):
                        j=j+1
                        if frame_num==1:
                              tracks.append([])
                              tracks_details.append([])
                              X=int(initBB[0]+(initBB[2]/2))
                              Y=int(initBB[1]+(initBB[3]/2))
                              point=[X,Y]
                              tracks_details[j].append([frame_num,point,point,initBB_index,0])
                              tracks[j].append(point)      
                        tracker = cv2.TrackerCSRT_create()
                        tracker.init(globals()['frame%s'%frame_num], initBB)
                        tracker.update(globals()['frame%s'%frame_num])
                        (success, box) = tracker.update(globals()['frame%s'%(frame_num+1)])
                        if success:
                              X=int(box[0]+(box[2]/2))
                              Y=int(box[1]+(box[3]/2))
                              point=[X,Y]
                              if (frame_num+1)<10:
                                    frame_ind='0'+str(frame_num+1)
                              else:
                                    frame_ind=str(frame_num+1)
                              result=overlap(point,globals()['frame%s_sperms'%frame_ind])
                              if result[0] == 'matched' and result[2] not in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                                    globals()['frame%s_selected_sperms'%(frame_num+1)].append(result[2])
                                    globals()['frame%s_selected_details'%(frame_num+1)].append([point,result[1],result[2],result[3],initBB_index])
                              elif result[0] == 'matched' and result[2] in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                                    for g in globals()['frame%s_selected_details'%(frame_num+1)]:
                                          if g[2]==result[2]: # lost 
                                                if result[3]<g[3]:
                                                      g[1]='F'
                                                      g[2]='F'
                                                      g[3]='F'
                                                      globals()['frame%s_selected_details'%(frame_num+1)].append([point,result[1],result[2],result[3],initBB_index])
                                                
                                                elif result[3]>=g[3]:
                                                      globals()['frame%s_selected_details'%(frame_num+1)].append([point,'F','F','F',initBB_index])
                                                      
                              elif result =='not matched':
                                    pass
                              

                  for fs in globals()['frame%s_selected_details'%(frame_num+1)]:
                        if 'F' in fs:
                              sec_result=overlap(fs[0],globals()['frame%s_sperms'%frame_ind])
                              if sec_result[0] == 'matched' and sec_result[2] not in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                                    globals()['frame%s_selected_sperms'%(frame_num+1)].append(sec_result[2])
                                    fs[1]=sec_result[1]
                                    fs[2]=sec_result[2]
                                    fs[3]=sec_result[3]
                              elif sec_result[0] == 'matched' and sec_result[2] in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                                    for g in globals()['frame%s_selected_details'%(frame_num+1)]:
                                          if g[2]==sec_result[2]: # lost 
                                                if sec_result[3]<g[3]:
                                                      g[1]='F'
                                                      g[2]='F'
                                                      g[3]='F'
                                                      fs[1]=sec_result[1]
                                                      fs[2]=sec_result[2]
                                                      fs[3]=sec_result[3]

                              elif sec_result =='not matched':
                                    pass       
                                
                  for nu in range(len(globals()['frame%s_sperms'%frame_ind])):
                        if nu not in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                              globals()['frame%s_non_selected_sperms'%(frame_num+1)].append(globals()['frame%s_sperms'%frame_ind][nu])     
                
                  for fs in globals()['frame%s_selected_details'%(frame_num+1)]:
                        assign=0
                        if 'F' not in fs:
                              for td_num,td in enumerate(tracks_details):
                                    for t in td:
                                          if t[0]==frame_num and t[3]==fs[4]:
                                                td.append([frame_num+1,fs[0],fs[1],fs[2],fs[3]])
                                                tracks[td_num].append(fs[0])
                                                assign=1
                                                
                  if assign==0:
                        pass
                  for nu in range(len(globals()['frame%s_sperms'%frame_ind])):
                        if nu not in globals()['frame%s_selected_sperms'%(frame_num+1)]:
                              new_sperm=globals()['frame%s_sperms'%frame_ind][nu]
                              X=int(new_sperm[0]+(new_sperm[2]/2))
                              Y=int(new_sperm[1]+(new_sperm[3]/2))
                              tracks_details.append([[frame_num+1,[X,Y],[X,Y],nu,0]])
                              tracks.append([[X,Y]])

            for x in range(50):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25: ### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])
                                   
            for w in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25:### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_fp(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track[1:])
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num][1:])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                                
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
              
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])            
            for y in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25: ### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_second(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])

            for z in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25:### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_third(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])

            for q in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25:### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_fourth(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])
            for e in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25:### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_fifth(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])



            for ee in range(20):
                  remove=[]
                  for track_num,track in enumerate(tracks_details):
                        if len(track)<25:### change if you have more or less than 25 frames in a video.
                              result=lost_sperms_join_border(track,tracks_details)
                              if result == 'Fail':
                                    continue
                              elif result[0]=='Success':
                                    new_inp = tracks_details[result[1]].copy()
                                    new_inp.extend(track)
                                    tracks_details[result[1]].extend(track)
                                    #tracks_details.remove(track)
                                    tracks[result[1]].extend(tracks[track_num])
                                    #tracks.remove(tracks[track_num])
                                    remove.append(track_num)
                  tracks2=tracks.copy()
                  tracks_details2=tracks_details.copy()
                  
                  for r in remove:
                      tracks.remove(tracks2[r])
                      tracks_details.remove(tracks_details2[r])            

                      
            for tra in tracks.copy():
                  if len(tra)<9:
                        tracks.remove(tra)
            for trad in tracks_details.copy():
                  if len(trad)<9:
                        tracks_details.remove(trad)


            all_tracks[name]=tracks
            all_tracks_details[name]=tracks_details
            print(name,' done')
      return(all_tracks,all_tracks_details)


# This function computes the overlap between a track and a ground truth       
def overlap(point,frame_sperms):
      sperm_distance_matrix=[]
      modified_frame_sperms=frame_sperms.copy()
      for num,data in enumerate(modified_frame_sperms): 
            x_data=int(data[0]+(data[2]/2))
            y_data=int(data[1]+(data[3]/2))
            modified_frame_sperms[num]=[x_data,y_data]
      x=point[0]
      y=point[1]
      for sperm_loc in modified_frame_sperms:
            sperm_distance= (((sperm_loc[0]-x)**2)+((sperm_loc[1]-y)**2))**0.5
            sperm_distance_matrix.append(sperm_distance)
      min_sperm_distance=np.min(sperm_distance_matrix)
      min_sperm_distance_loc=np.argmin(sperm_distance_matrix)
      min_sperm=modified_frame_sperms[min_sperm_distance_loc]
      if min_sperm_distance<=15:
            return ['matched',min_sperm,min_sperm_distance_loc,min_sperm_distance]
      else:
            return 'not matched'

def avg_mov(track):
    move=0
    for i in range(len(track)-1):
        move+=(((track[i][1][0]-track[i+1][1][0])**2)+((track[i][1][1]-track[i+1][1][1])**2))**0.5
    move/=len(track)
    return(move)
def max_mov(track):
    move=[]
    if len(track)==1:
        return(0)
    for i in range(len(track)-1):
        move.append((((track[i][1][0]-track[i+1][1][0])**2)+((track[i][1][1]-track[i+1][1][1])**2))**0.5)
    maxmove=max(move)
    return(maxmove)
###########################################################################################        
def lost_sperms_join(track,tracks_details_copy): 
      
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-1,start_frame)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  if len(track)>=3 and len(compare_track)>=3:
                      avg_mov1=avg_mov(track)
                      avg_mov2=avg_mov(compare_track)
                      max_move=max(max_mov(track),max_mov(compare_track))
                      if abs(avg_mov2-avg_mov1)<=10:
                          x1=compare_track[-1][1][0] 
                          y1=compare_track[-1][1][1]
                          x2=track[0][1][0]
                          y2=track[0][1][1]
                          distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                          if distance <= max_move+10:
                                inf.append(distance)
                                inf_num.append(compare_track_num)
                                
                  elif len(track)<3 or len(compare_track)>=3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= max_move+10:
                          inf.append(distance)
                          inf_num.append(compare_track_num)
                         
                  elif len(track)>=3 or len(compare_track)<3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= max_move+10:
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                          
                  else:
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 10:
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                        
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])    
      
      
      
      
#############################################################################################################


###########################################################################################        
def lost_sperms_join_second(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-2,start_frame-1)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)

      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  if len(track)>=3 and len(compare_track)>=3:
                      avg_mov1=avg_mov(track)
                      avg_mov2=avg_mov(compare_track)
                      max_move=max(max_mov(track),max_mov(compare_track))
                      if abs(avg_mov2-avg_mov1)<=10:
                          x1=compare_track[-1][1][0] 
                          y1=compare_track[-1][1][1]
                          x2=track[0][1][0]
                          y2=track[0][1][1]
                          distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                          if distance <= 2*(max_move+5):
                                inf.append(distance)
                                inf_num.append(compare_track_num)
                                
                  elif len(track)<3 or len(compare_track)>=3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 2*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num)
                         
                  elif len(track)>=3 or len(compare_track)<3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 2*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                          
                  else:
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 20:
                          inf.append(distance)

                        
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])    
      
      
      
      
#############################################################################################################
   
###########################################################################################        
def lost_sperms_join_third(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-3,start_frame-2)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  if len(track)>=3 and len(compare_track)>=3:
                      avg_mov1=avg_mov(track)
                      avg_mov2=avg_mov(compare_track)
                      max_move=max(max_mov(track),max_mov(compare_track))
                      if abs(avg_mov2-avg_mov1)<=10:
                          x1=compare_track[-1][1][0] 
                          y1=compare_track[-1][1][1]
                          x2=track[0][1][0]
                          y2=track[0][1][1]
                          distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                          if distance <= 3*(max_move+5):
                                inf.append(distance)
                                inf_num.append(compare_track_num)
                                
                  elif len(track)<3 or len(compare_track)>=3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 3*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num)
                         
                  elif len(track)>=3 or len(compare_track)<3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 3*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                          
                  else:
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 30:
                          inf.append(distance)
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])    
      
      
      
      
#############################################################################################################
   
###########################################################################################        
def lost_sperms_join_fourth(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-4,start_frame-3)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  if len(track)>=3 and len(compare_track)>=3:
                      avg_mov1=avg_mov(track)
                      avg_mov2=avg_mov(compare_track)
                      max_move=max(max_mov(track),max_mov(compare_track))
                      if abs(avg_mov2-avg_mov1)<=10:
                          x1=compare_track[-1][1][0] 
                          y1=compare_track[-1][1][1]
                          x2=track[0][1][0]
                          y2=track[0][1][1]
                          distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                          if distance <= 4*(max_move+5):
                                inf.append(distance)
                                inf_num.append(compare_track_num)
                                
                  elif len(track)<3 or len(compare_track)>=3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 4*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num)
                         
                  elif len(track)>=3 or len(compare_track)<3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 4*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                          
                  else:
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 40:
                          inf.append(distance)
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])    
      
      
      
      
#############################################################################################################  
###########################################################################################        
def lost_sperms_join_fifth(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-5,start_frame-4)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  if len(track)>=3 and len(compare_track)>=3:
                      avg_mov1=avg_mov(track)
                      avg_mov2=avg_mov(compare_track)
                      max_move=max(max_mov(track),max_mov(compare_track))
                      if abs(avg_mov2-avg_mov1)<=10:
                          x1=compare_track[-1][1][0] 
                          y1=compare_track[-1][1][1]
                          x2=track[0][1][0]
                          y2=track[0][1][1]
                          distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                          if distance <= 5*(max_move+5):
                                inf.append(distance)
                                inf_num.append(compare_track_num)
                                
                  elif len(track)<3 or len(compare_track)>=3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 5*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num)
                         
                  elif len(track)>=3 or len(compare_track)<3:
                      max_move=max(max_mov(track),max_mov(compare_track))
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 5*(max_move+5):
                          inf.append(distance)
                          inf_num.append(compare_track_num) 
                          
                  else:
                      x1=compare_track[-1][1][0] 
                      y1=compare_track[-1][1][1]
                      x2=track[0][1][0]
                      y2=track[0][1][1]
                      distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                      if distance <= 50:
                          inf.append(distance)
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])   
      
      
      
      
#############################################################################################################  
###########################################################################################        
def lost_sperms_join_fp(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame,start_frame+1)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  x1=compare_track[-1][1][0] 
                  y1=compare_track[-1][1][1]
                  x2=track[0][1][0]
                  y2=track[0][1][1]
                  distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                  if distance <= 10:
                        inf.append(distance)
                        inf_num.append(compare_track_num)
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])     
      
      
      
      
#############################################################################################################      
   
###########################################################################################        
def lost_sperms_join_border(track,tracks_details_copy): 
      
      import numpy as np
      inf=[]
      inf_num=[]
      start_frame=track[0][0]
      ended_frames=np.arange(start_frame-5,start_frame)
      nums=[]
      for num_ind,num in enumerate(ended_frames):
            if num < 1:
                  nums.append(num_ind)
      ended_frames=np.delete(ended_frames,nums)
      for compare_track_num,compare_track in enumerate(tracks_details_copy):
            if compare_track[-1][0] in ended_frames:
                  absent_frames=start_frame-compare_track[-1][0]
                  x1=compare_track[-1][1][0] 
                  y1=compare_track[-1][1][1]
                  x2=track[0][1][0]
                  y2=track[0][1][1]
                  distance=(((x1-x2)**2)+((y1-y2)**2))**0.5
                  if distance <= 5*absent_frames:
                        inf.append(distance)
                        inf_num.append(compare_track_num)
      if len(inf)==0:
            return 'Fail'
      index=np.argmin(np.array(inf))
      return('Success',inf_num[index])    
      
      
      
      
#############################################################################################################      
   
      
      
def distance(a,b):
  if len(a)==len(b):
      d= len(a)
      dis_matrix=[]
      for num in range(d):
          single_dis=(((a[num][0]-b[num][0])**2)+((a[num][1]-b[num][1])**2))**0.5
          dis_matrix.append(single_dis)
      return(dis_matrix)
      
  else:
      raise NameError('given lists dont have same length')
   
# Interpolation for equalization
def interpolate(t,a):
  ta= len(t)-len(a)
  at= len(a)-len(t)
  if ta>0 and ta<=5:
        a=equalize_matrix(a,ta,t)
  elif at>0 and at<=5:
        t=equalize_matrix(t,at,a)
  elif ta >= 6 or at >= 6:
      t='stop'
      a='stop'
  else:
        pass
  
  return[t,a]
  
  
  
def equalize_matrix(matrix,number,compare_matrix):
    e_matrix=[]
    for place in range(len(matrix)):
          if place == len(matrix)-1:
                break
          e_matrix.append([(matrix[place][0]+matrix[place+1][0])/2,(matrix[place][1]+matrix[place+1][1])/2])
    for end_place in range(number) :
          e_matrix.append(matrix[len(matrix)-1])
    selected_matrix = best_places(e_matrix,number,matrix,compare_matrix)
    return selected_matrix
  
      

def best_places(e_matrix,number,matrix,compare_matrix):
    import random
    import math
    import numpy as np
    conditions = math.factorial(len(e_matrix))/(math.factorial(number)*math.factorial(len(e_matrix)-number))
    samples=[]
    all_t_matrixes=[]
    dis_value=[]
    num_e_matrix=[i for i in range(len(e_matrix))]
    while(True):
          x=random.sample(num_e_matrix,number)
          x.sort()
          if x not in samples:
                samples.append(x)
          if len(samples)==conditions:
                break
    for sample in samples:
          t_matrix=matrix.copy()
          for s in sample:
                t_matrix.insert(s+1,e_matrix[s])
          distancee = distance(t_matrix,compare_matrix)
          distancee=np.mean(distancee)
          t_matrix.append(distancee)
          all_t_matrixes.append(t_matrix)
    for a in all_t_matrixes:
          dis_value.append(a[-1:])
    selected_matrix=all_t_matrixes[np.argmin(dis_value)]
    selected_matrix=selected_matrix[0:-1]
    return selected_matrix


#Simple equalization method
def equalize(t,a):
      
      ta= len(t)-len(a)
      at= len(a)-len(t)
      if ta>0 and ta<=5:
            for d in range (ta):
                a.append(a[len(a)-1])
      elif ta >= 6 or at >= 6:
            t='stop'
            a='stop'
      elif at>0 and at<=5:
            for d in range (at):
                t.append(t[len(t)-1])
      else:
            pass
      return[t,a]

def evaluate(tracks,anno):
  dist_list=[]
  dist_list_index=[]      
  distance_values={}
  notselected_annotations={}
  fp_matrix={}
  #matching_ind={}
  tp=0
  fp=0
  fn=0
  sperms_nums=0
  video_tracks=tracks
  for video__name in video_tracks:
      sperms_nums+=len(anno[video__name])
  for video_name in video_tracks:
      if video_name in anno:
          video_anno=anno[video_name]
      else:
          raise NameError('given Track doesnt exist in annotations')
      video__tracks= video_tracks[video_name]
      selected_annotations_indexs=[]
      finally_selected_anno=[]
      for track_index,track in enumerate(video__tracks):
          
          for anno_index,single_anno in enumerate(video_anno):
              outp=equalize(track,single_anno) #You can use interpolate(track,single_anno) for interplaotion instead of simple equalization.
              if outp[0]=='stop' or outp[1] == 'stop':
                  continue
              modified_track=outp[0]
              single_anno= outp[1]
              first_dist=distance([modified_track[0]],[single_anno[0]])
              last_dist=distance(modified_track[-1:],single_anno[-1:])
              if first_dist[0] >25 and last_dist[0] >25:
                  continue
              all_dist =  distance(modified_track,single_anno)
              mean_dis= np.mean(all_dist)
              if mean_dis>15 or anno_index in finally_selected_anno:
                  continue
              else:

                  dist_list.append(mean_dis)
                  dist_list_index.append(anno_index)
          try:
              selected_dist = np.min(dist_list)
              index=dist_list.index(selected_dist)
              selected_dist_annoindex=dist_list_index[index] 
              tp+=1
              #matching_ind[video_name].append([dist_list_index[index],track_index])
          except(ValueError):
              fp+=1
              if video_name not in fp_matrix:
                  fp_matrix[video_name]=[track_index]
              fp_matrix[video_name].append(track)
              continue
          if video_name not in distance_values:
              distance_values[video_name]=[]
          distance_values[video_name].append(selected_dist)
          distance_values[video_name].append(track_index)
          distance_values[video_name].append(selected_dist_annoindex)
          selected_annotations_indexs.append(selected_dist_annoindex)
          finally_selected_anno.append(selected_dist_annoindex)
          dist_list=[]
          dist_list_index=[]
          #matching_ind[video_name].append([selected_dist_annoindex,track_index])
      fn+=(len(video_anno)-len(selected_annotations_indexs))
      all_anno_indexes=[i for i in range(len(video_anno))]
      for ai in all_anno_indexes:
          if ai not in selected_annotations_indexs:
              if video_name not in notselected_annotations:
                  notselected_annotations[video_name]=[]
              notselected_annotations[video_name].append(video_anno[ai])
               
  return [distance_values,tp,fp,fn,sperms_nums,notselected_annotations,fp_matrix]
  

def main():
    anno=get_anno()
    tracks_r=get_tracks()
    tracks=tracks_r[0].copy()
    tracks_details=tracks_r[1].copy()
    modified_tracks={}
    for key in tracks.keys():
        tracks1=tracks[key].copy()
        for track in tracks[key]:
            if len(track)<9:
                tracks1.remove(track)
        modified_tracks[key]=tracks1
    modified_tracks_details={}
    for key in tracks_details.keys():
        tracks_details1=tracks_details[key].copy()
        for track_details in tracks_details[key]:
            if len(track_details)<9:
                tracks_details1.remove(track_details)
        modified_tracks_details[key]=tracks_details1
    eresult=evaluate(modified_tracks.copy(),anno)
    return(modified_tracks,modified_tracks_details,eresult,anno)
     
      
if __name__ == '__main__':
    start=time.time()
    output = main()
    tracks=output[0]
    tracks_details=output[1]
    anno=output[3]
    result=output[2]
    stop=time.time()
    print(stop-start)
    print('Correct Tracks:',result[1])
    print('Wrong Tracks:',result[2])
    print('Missed Tracks:',result[3])
    print('Tracks Numbers:',result[4])
    
    
   
#This functions are for visualizing one tracked sperm and one ground-trueh sperm in a video
# Use like this : track_tail1('video-name.avi',tracks['video-name'][0],anno['video-name'][0])
######################################################################################
def track_tail1(video,track1,anno):
      vs = cv2.VideoCapture(video)
      for i in range(25): ### number of frames in a video sample
            read_flag,frame = vs.read()
            if len(track1)>=i+1:
                  x1=int(track1[i][0]-10)
                  y1=int(track1[i][1]-10)
                  x2=int(track1[i][0]+10)
                  y2=int(track1[i][1]+10)
                  cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255))
            if len(anno)>=i+1:
                  X1=int(anno[i][0]-10)
                  Y1=int(anno[i][1]-10)
                  X2=int(anno[i][0]+10)
                  Y2=int(anno[i][1]+10)
                  cv2.rectangle(frame,(X1,Y1),(X2,Y2),(255,255,255))
            cv2.imshow("Frame", frame)
            #cv2.imwrite("f{}.jpg".format(i),frame)
            key=cv2.waitKey(1000)&0xFF
            if key==ord('q'): # Press q to break
                  break
      cv2.destroyAllWindows()        

######################################################################################
def track_tail2(startframe,endframe,video,anno,track1):
      vs = cv2.VideoCapture(video)
      for j in range(startframe-1):
            read_flag,frame = vs.read()
      for i in range(endframe-startframe+1):
            read_flag,frame = vs.read()
            x1=int(track1[i][0]-10)
            y1=int(track1[i][1]-10)
            x2=int(track1[i][0]+10)
            y2=int(track1[i][1]+10)
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255))
            X1=int(anno[i+startframe-1][0]-10)
            Y1=int(anno[i+startframe-1][1]-10)
            X2=int(anno[i+startframe-1][0]+10)
            Y2=int(anno[i+startframe-1][1]+10)
            cv2.rectangle(frame,(X1,Y1),(X2,Y2),(255,255,255))
            cv2.imshow("Frame", frame)
            key=cv2.waitKey(1000)&0xFF
            if key==ord('q'):
                  break
      cv2.destroyAllWindows()   
        
###################################################################################      