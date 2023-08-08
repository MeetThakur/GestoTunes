from tkinter import filedialog as fd
from tkinter import *
import os
import pygame.mixer as mixer
from cvzone.HandTrackingModule import HandDetector
import cv2
import customtkinter
from PIL import ImageTk, Image
import threading


def selectFolder():
    global playlist,file_path,song,current,folderopened
    file_path = fd.askdirectory()
    for file in os.listdir(file_path):
        if file.endswith('.mp3'):
            playlist.append(file)
    mixer.music.load(file_path+'/'+playlist[song])
    mixer.music.play()
    current.configure(text=playlist[0])
    folderopened = True


def Play():
    mixer.music.load(file_path+'/'+playlist[song])
    mixer.music.play()
    current.configure(text=playlist[song])

def playSong():
    global playlist,song,file_path,paused,pauseimg
    if len(playlist) == 0:
        pass 
    else:
        if paused == False:
            mixer.music.pause()
            play.configure(image=playimg)
            paused = True
        else:
            mixer.music.unpause()
            play.configure(image=pauseimg)    
            paused = False


def nextSong():
    global song,playlist,file_path
    if song == len(playlist) -1:
        song = 0
    else:
        song += 1
    Play()

def prevSong():
    global song,playlist,file_path
    if song == 0:
        song = len(playlist) -1
    else:
        song -= 1
        Play()

def showVideo():
    global showvid
    if showvid:
        showvid = False
    else:
        showvid = True



song = 0
paused = False
playlist = []
file_path = None
mixer.init()
detector = HandDetector(maxHands=1, detectionCon=0.8)
video = cv2.VideoCapture(0)
fc = 0
folderopened = False
dis = True
showvid = True



def main():
    global current,song,pauseimg,playimg,play
    mixer.init()
    win = customtkinter.CTk()
    customtkinter.set_appearance_mode("light")
    width = win.winfo_screenwidth()
    height = win.winfo_screenheight()
    size = str(width//3) + 'x' + str(height//3)
    win.geometry(size)
    
    playimg = Image.open("data/play.png")
    playimg = playimg.resize((width//25,width//25),Image.LANCZOS)
    playimg = ImageTk.PhotoImage(playimg)

    previmg = Image.open("data/prev.png")
    previmg = previmg.resize((width//25,width//25),Image.LANCZOS)
    previmg = ImageTk.PhotoImage(previmg)

    nextimg = Image.open("data/next.png")
    nextimg = nextimg.resize((width//25,width//25),Image.LANCZOS)
    nextimg = ImageTk.PhotoImage(nextimg)

    pauseimg = Image.open("data/pause.png")
    pauseimg = pauseimg.resize((width//25,width//25),Image.LANCZOS)
    pauseimg = ImageTk.PhotoImage(pauseimg)




    play = customtkinter.CTkButton(win,text='',image=playimg,width=width//27,fg_color='#ebebeb',border_width=0,command=playSong)
    play.place(relx=0.5,rely=0.6,anchor='center')

    prev = customtkinter.CTkButton(win,text='',image=previmg,width=width//25,fg_color='#ebebeb',border_width=0,command=prevSong)
    prev.place(relx=0.3,rely=0.6,anchor='center')

    nextb = customtkinter.CTkButton(win,text='',image=nextimg,width=width//27,fg_color='#ebebeb',border_width=0,command=nextSong)
    nextb.place(relx=0.7,rely=0.6,anchor='center')

    select = customtkinter.CTkButton(win,text="Select Folder",width=width//20,command=selectFolder)
    select.place(relx=0.5,rely=0.9,anchor='center')

    current = customtkinter.CTkLabel(win,text='select a song',width=width//4,height=height//8)
    current.place(relx=0.5,rely=0,anchor='n')
    current.configure(font=('arial',25,'bold'),wraplength=width//3)

    showv = customtkinter.CTkButton(win,text='Video',width=width//30,command=showVideo)
    showv.place(relx=0.9,rely=0.9)

    now = customtkinter.CTkLabel(win,text='Now Plaing')
    now.place(relx=0.5,rely=0,anchor='n')

    win.mainloop()






def main2():
    global folderopened,dis,paused,fc,current
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [0, 1, 0, 0, 0] and fc != 1 and folderopened == False:
                    selectFolder()
                    print('openend The Folder')
                    folderopened = True
                    fc = 1  

                if fingerup == [1, 1, 0, 0, 0] and fc != 2 and folderopened == True and dis == True:                
                    nextSong()
                    print('Next')
                    fc = 2

                    mixer.music.unpause()               
                if fingerup == [1, 0, 0, 0, 1] and fc != 3 and folderopened == True and dis == True:                
                    prevSong()
                    print('Prev')
                    fc = 3

                if fingerup == [0,0,0,0,0] and  fc != 5 and folderopened == True and dis == True:   
                    playSong()
                    print('Pause/Resume')
                    fc = 5

                if fingerup == [0,1,0,0,1] and folderopened == True and dis == True:   
                    dis = False
                    print('disabled')

                if fingerup == [0,0,0,0,1] and folderopened == True and dis == False:   
                    dis = True
                    print('enabled')             
                
                if fingerup == [1, 1, 1, 1, 1] and fc!=0:
                    fc = 0
                    print('ok')

        if mixer.music.get_busy() == False and paused == False and folderopened == True:
            nextSong()            

        cv2.imshow("Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if showvid == False:
            break
    
        
    video.release()
    cv2.destroyAllWindows()



x = threading.Thread(target=main)
y = threading.Thread(target=main2)

x.start()
y.start()


x.join()
y.join()