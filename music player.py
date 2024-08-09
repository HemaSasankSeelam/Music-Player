from tkinter import *
from pynput import keyboard
import threading
import customtkinter
from tkinter import filedialog
import os,sys
import random
import pygame
from configparser import ConfigParser
from PIL import Image,ImageTk
from mutagen.id3 import APIC
from mutagen import File
from mutagen.mp3 import MP3
import eyed3
from eyed3 import id3
from tkinter import colorchooser
import shutil
from datetime import datetime
import subprocess
import time
from winotify import Notification,audio
import winsound
import webbrowser
from builtins import open
from pathlib import Path

class MUSIC_PLAYER:

    def __init__(self) -> None:
        self.root = Tk(className=" Music Player")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.state('zoomed')

        self.admin_name = os.getlogin()
        self.pre_admin_path = os.path.join(r"C:\Users",self.admin_name)
        self.post_admin_path = os.path.join(self.pre_admin_path,"AppData/Local")
        self.main_path = os.path.join(self.post_admin_path,'music_player')

        self.fg = "#FFFFFF"
        self.bg = "#454545"
        self.config = ConfigParser()

        self.songs_list = []

        self.current_song = None
        self.is_palying = False
        self.is_pause = False
        self.is_seek = False
        self.background_listen = False
        self.is_static = True
        self.is_repeating = False
        self.repeating_song_name = None
        self.static_color = None
        self.is_timed = False
        self.is_volume_limited = True
        self.value_seeked = 0
        self.is_muted = False
        self.is_searching = False
        self.current_time = time.time()
        self.index_count = -1  # for gif image
        self.is_gif_timer_cancled = True # because by default it is not intiated
        self.last_time_key_pressed = 0
        self.font_name = "MV Boli"
        self.volume_limit_value = 70

        self.all_functions()

        self.root.mainloop()
    
    def __del__(self):

        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        try:
            command = f'icacls {self.main_path} /remove {self.admin_name}'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

            time_text = str(self.left_time.cget('text'))
            h,m,s = map(int,time_text.split(":"))
            totol_mill_secs = h*36_00_000 + m*60_000 + s*1_000 

            self.config.set(section="DATA",option='last_pos',value=str(totol_mill_secs)) # it takes only strings
            # changing the last pos value in catch file

            with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
                self.config.write(fo)
        except:
            pass

        
        ## 'icacls file(or)folder /deny adminname:F'  # for blocking the permissions
        try:
            command = f'icacls {self.main_path} /deny {self.admin_name}:F'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except:
            pass

    
    def all_functions(self):
        self.divide_window_into_frames()
        self.divide_frames_into_sub()
        self.checking_user_preferences()

        
    
    """*************Divides the main window into frames and add menu bar to window************"""

    def divide_window_into_frames(self):
        self.main_frame = LabelFrame(self.root,width=1200,height=720,bg="#000000")
        self.main_frame.place(x=0,y=0)

        self.songs_list_frame = LabelFrame(self.root,width=335,height=720,bg="#FFFFFF")
        self.songs_list_frame.place(x=1200,y=0)

        self.slider_frame = LabelFrame(self.root,width=1535,height=30,bg=self.bg)
        self.slider_frame.place(x=0,y=720)

        self.controls_frame = LabelFrame(self.root,width=1535,height=70,bg=self.bg)
        self.controls_frame.place(x=0,y=750)

        self.my_menu = Menu(self.root,bg="SystemButtonface")
        self.file_menu = Menu(self.my_menu,tearoff=0,type='menubar',bg="SystemButtonface",font=(self.font_name,10))
        self.file_menu.add_command(label="Add Songs Folder",command=self.add_folder)
        self.file_menu.add_command(label="Remove Song Folder",command=self.remove_song_folder)

        self.shortcuts_menu = Menu(self.my_menu,tearoff=0,bg="SystemButtonface",font=(self.font_name,10))
        self.shortcuts_menu.add_cascade(label="ctrl+o   Open Folder")
        self.shortcuts_menu.add_cascade(label="ctrl+d   Remove Folder")
        self.shortcuts_menu.add_separator()
        self.shortcuts_menu.add_cascade(label="Space bar  Play/Pause")
        self.shortcuts_menu.add_separator()
        self.shortcuts_menu.add_cascade(label="Right Arrow (>)  Volume +")
        self.shortcuts_menu.add_cascade(label="Left  Arrow (<)  Volume -")
        self.shortcuts_menu.add_separator()
        self.shortcuts_menu.add_cascade(label="Up Arrow   (↑) PreviousTrack")
        self.shortcuts_menu.add_cascade(label="Down Arrow (↓) NextTrack")
        self.shortcuts_menu.add_separator()
        self.shortcuts_menu.add_cascade(label="letter   ('s') Shuffel's Song's List")
        self.shortcuts_menu.add_cascade(label="letter   ('r') Repeat/Unrepeat song")
        self.shortcuts_menu.add_cascade(label="letter   ('m') Mute/Unmute song")
        self.shortcuts_menu.add_separator()
        self.shortcuts_menu.add_cascade(label="Ctrl+Left  Arrow << 10 sec <<")
        self.shortcuts_menu.add_cascade(label="Ctrl+Right Arrow >> 10 sec >>")

        self.background_menu = Menu(self.my_menu,tearoff=0,bg="SystemButtonface",font=(self.font_name,10))
        self.background_menu.add_command(label='Static',command=self.change_to_static)
        self.background_menu.add_command(label='Dynamic',command=self.change_to_dynamic)
        self.background_menu.add_separator()
        self.background_menu.add_command(label='Change Static Color',command=self.change_static_color)
        self.background_menu.add_separator()
        self.string_var = StringVar()
        self.lister_option = Menu(self.background_menu,tearoff=0,bg="SystemButtonface")
        self.lister_option.add_radiobutton(label="OFF",value="OFF",variable=self.string_var,command=self.all_bindings)
        self.lister_option.add_radiobutton(label="ON",value='ON',variable=self.string_var,command=self.all_unbindings)
        self.string_var.set(value="OFF")
        self.background_menu.add_cascade(label="Background Listner",menu=self.lister_option)

        self.settings_menu = Menu(self.my_menu,tearoff=0,bg="SystemButtonface",font=(self.font_name,10))
        self.settings_menu.add_cascade(label="Reset all",command=self.reset_all)
        self.settings_menu.add_separator()
        self.int_var = IntVar()
        self.timer_menu = Menu(self.settings_menu,tearoff=0,bg="SystemButtonface")
        self.timer_menu.add_radiobutton(label="OFF",value=0,variable=self.int_var,command=self.set_timer)
        self.timer_menu.add_radiobutton(label="ON",value=1,variable=self.int_var,command=self.set_timer)
        self.int_var.set(0)
        self.settings_menu.add_cascade(label="Timer",menu=self.timer_menu)
        self.int_var2 = IntVar()
        self.volume_limit_menu = Menu(self.settings_menu,tearoff=0,bg="SystemButtonface")
        self.volume_limit_menu.add_radiobutton(label='OFF',value=0,variable=self.int_var2,command=self.on_off_volume_limit)
        self.volume_limit_menu.add_radiobutton(label='ON',value=1,variable=self.int_var2,command=self.on_off_volume_limit)
        self.int_var2.set(1)
        self.settings_menu.add_cascade(label='Volume Limit',menu=self.volume_limit_menu)
        self.settings_menu.add_separator()
        self.settings_menu.add_cascade(label="Change Cover Image",command=self.change_cover_image_delete)
        self.settings_menu.add_cascade(label="Delete Cover Image",command=lambda :self.change_cover_image_delete(delete=True))
        self.string_var2 = StringVar()
        self.font_menu = Menu(self.settings_menu,tearoff=0,bg='SystemButtonface')
        self.font_menu.add_radiobutton(label="Times New Roman",font=("Times New Roman",8),value="Times New Roman",variable=self.string_var2,command=self.change_font)
        self.font_menu.add_radiobutton(label="MV Boli",font=("MV Boli",8),value="MV Boli",variable=self.string_var2,command=self.change_font)
        self.font_menu.add_radiobutton(label="Tempus Sans ITC",font=("Tempus Sans ITC",8),value="Tempus Sans ITC",variable=self.string_var2,command=self.change_font)
        self.font_menu.add_radiobutton(label="Ink Free",font=("Ink Free",8),value="Ink Free",variable=self.string_var2,command=self.change_font)
        self.font_menu.add_radiobutton(label="Blackadder ITC",font=("Blackadder ITC",8),value="Blackadder ITC",variable=self.string_var2,command=self.change_font)
        self.string_var2.set(value='MV Boli')
        self.settings_menu.add_separator()
        self.settings_menu.add_cascade(label="Change Font",menu=self.font_menu)
        self.settings_menu.add_command(label="Change volume limit value",command=self.change_volume_limit_value)


        self.helpmenu = Menu(self.my_menu,tearoff=0,bg="SystemButtonface",font=(self.font_name,10))
        self.helpmenu.add_command(label="Download Helper File",command=self.helper)

        self.my_menu.add_cascade(label='File',menu=self.file_menu)
        self.my_menu.add_cascade(label='Short Cuts',menu=self.shortcuts_menu)
        self.my_menu.add_cascade(label="Background",menu=self.background_menu)
        self.my_menu.add_cascade(label="Help",menu=self.helpmenu)

        for _ in range(46):
            self.my_menu.add_separator()

        self.my_menu.add_cascade(label="Settings",menu=self.settings_menu)

        for _ in range(30):
            self.my_menu.add_separator()

        date = datetime.now().strftime("%a  %d-%m-%Y")
        time = datetime.now().strftime("%H:%M:%S")
        self.my_menu.add_cascade(label=f"{date}     {time}  IST",command=self.browser)
        self.update_date_and_time()


        self.root.config(menu=self.my_menu) ## adding menu bar to root window
    
    """ ********************************* Dividing frames into sub frames ********************"""

    def divide_frames_into_sub(self):
        self.song_image_frame = LabelFrame(self.main_frame,width=500,height=500,bd=0)
        self.song_image_frame.place(x=350,y=50)

        self.song_image = Label(self.song_image_frame,border=0,highlightthickness=0)
        self.song_image.pack(fill=BOTH,expand=True)
        self.song_image.bind("<Button-3>",self.create_menu_for_dowanload)

        self.left_time = customtkinter.CTkLabel(self.main_frame,text="00:00:00",font=("Times New Roman",20),
                                                width=20,height=25,
                                                text_color='#c92069',bg_color="#000000")
        self.left_time.place(x=0,y=690)

        self.timer_info_label = customtkinter.CTkLabel(self.main_frame,text=" "*50,font=("Times New Roman",20),
                                                width=20,height=25,
                                                text_color='#c92069',bg_color="#000000")
        self.timer_info_label.place(x=560,y=690)

        self.right_time = customtkinter.CTkLabel(self.main_frame,text="00:00:00",font=("Times New Roman",20),
                                                width=20,height=25,
                                                text_color='#c92069',bg_color="#000000")
        self.right_time.place(x=1120,y=690)

        self.list_box_frame = Frame(self.songs_list_frame,width=333,height=690,background=self.fg)
        self.list_box_frame.place(x=0,y=0)

        self.list_box_frame.pack_propagate(False) # for fixing the  place

        self.list_box_scroll_bar = Scrollbar(self.list_box_frame,background=self.fg)
        self.list_box_scroll_bar.pack(side=RIGHT,fill=Y)

        self.list_box = Listbox(self.list_box_frame,width=330,font=(self.font_name,15),yscrollcommand=self.list_box_scroll_bar.set,
                                activestyle='none',selectbackground='#808080',selectforeground='#07f592',cursor='hand2')
        self.list_box.pack(side=LEFT,fill=Y)

        self.list_box.bind("<Tab>",self.destroy_list_box)
        self.list_box.bind("<<ListboxSelect>>",self.custom_song)

        self.list_box_scroll_bar.configure(command=self.list_box.yview)
        
        self.search_bar = customtkinter.CTkEntry(self.songs_list_frame,width=334,height=20,corner_radius=50,
                                             fg_color="#FFFFFF",text_color="#000000",font=(self.font_name,16),
                                             placeholder_text="Search for song...",border_color="#000000")
        self.search_bar.place(x=0,y=693)
        self.search_bar.bind("<KeyRelease>",self.search)
        self.search_bar.bind("<Tab>",self.destroy_list_box)
        self.search_bar.bind("<Leave>",self.destroy_list_box)
        self.search_bar.bind("<Leave>",self.destroy_search_bar)

        self.song_s = customtkinter.CTkSlider(self.slider_frame,from_=0,to=100,width=1535,height=25,
                                              progress_color='#fa8f02',button_color='#bd2d75',hover=False,command=lambda value:self.set_slider(self.song_s.get()))
        self.song_s.set(0)
        self.song_s.pack()

        ## len max==40
        self.song_info_b = customtkinter.CTkButton(self.controls_frame,width=400,height=65,text="",font=(self.font_name,20),
                                                text_color="#34b7eb",fg_color='transparent',anchor='w',bg_color=self.bg,cursor="hand2")
        self.song_info_b.place(x=0,y=0)
        self.song_info_b.bind("<Button-1>",self.full_info)

        self.shuffle_b = customtkinter.CTkButton(self.controls_frame,width=0,height=0,text="\U0001F500",font=("TimeNewRoman",51),
                                                text_color='#f5f107',anchor='n',fg_color='transparent',command=self.shuffle_songs_list)
        self.shuffle_b.place(x=550,y=0)

        self.previous_b = customtkinter.CTkButton(self.controls_frame,width=0,height=0,text="\u23EE",font=("TimeNewRoman",51),
                                               text_color='#f5f107',anchor='n',fg_color='transparent',command=self.go_to_previous_track,
                                               )
        self.previous_b.place(x=620,y=0)

        self.play_b = customtkinter.CTkButton(self.controls_frame,width=0,height=0,text="\u25B6",font=("TimeNewRoman",51),
                                            text_color='#f5f107',anchor='n',fg_color='transparent',command=self.play_function)
        self.play_b.place(x=700,y=0)

        self.next_b = customtkinter.CTkButton(self.controls_frame,width=0,height=0,text="\u23ED",font=("TimeNewRoman",51),
                                            text_color='#f5f107',anchor='n',fg_color='transparent',command=self.go_to_next_track)
        self.next_b.place(x=780,y=0)

        self.repeat_b = customtkinter.CTkButton(self.controls_frame,width=0,height=0,text="\U0001F501",font=("TimeNewRoman",51),
                                            text_color='#f5f107',anchor='n',fg_color='transparent',command=self.repeat_song)
        self.repeat_b.place(x=860,y=0)

        self.reapeating_info = Label(self.controls_frame,font=(self.font_name,15),bg=self.bg,fg="#34b7eb")
        self.reapeating_info.place(x=1000,y=20)
        
        self.volume_frame = LabelFrame(self.controls_frame,text="Volume 70%",width=305,height=65,bg=self.bg,fg=self.fg,font=(self.font_name,10))
        self.volume_frame.place(x=1225,y=0)

        self.volume_s = customtkinter.CTkSlider(self.volume_frame,from_=0,to=100,number_of_steps=10,
                                                progress_color='#3cc920',width=300,command=lambda value:self.update_volume_bar(self.volume_s.get()))
        self.volume_s.place(x=0,y=10)
        self.volume_s.set(70)



    """********************************************* Menu bar functions *****************************************"""
    
    def add_folder(self,e:Event=None): # add a songs folder to list 
        ## opens the file dialoge we can select only the folder's
        self.input_folder = filedialog.askdirectory(title="Select Music Files Folder To Add To List")
        if self.input_folder != "": # if input_folder != ""  # if user not select the folder and closes the dialod it returns  ""
            for root,dirs,files in os.walk(self.input_folder): # walks through entire folder 
                song_flag = False
                #purpose  #if the folder doesn't have any songs songs_flag remains False only  if False means the song dir not added to catch files
                for filename in files:
                    pygame.init()
                    if os.path.splitext(filename)[-1].lower().strip() in (".mp3"): # returns song name and the song must be .mp3  formt only
                        if os.path.join(root,filename) not in self.songs_list:
                            # for not entering duplicates if the song already in list it wont be added
                            # if the same song in different folder will add to list it filters only in same folder
                            try:
                                audio = MP3(os.path.join(root,filename)) #opening the file path
                                if audio: # if True means any data in audio only it satisfies the if condition
                                    # Check if the audio has a valid duration
                                    self.songs_list.append(os.path.normpath(os.path.join(root,filename)))
                                    song_flag = True # changing flag to True for adding song folder to catch files
                                    self.double_check(song_flag=song_flag,root=root)
                            except:
                                pass
    def double_check(self,song_flag,root):
        ### Double check if the user adds the same files it doesn't add
        songs_list2 = self.songs_list.copy()
        self.songs_list.clear()
        for i in songs_list2:
            flag = 0
            max_count = len(self.songs_list)
            for j in self.songs_list:
                if os.path.normpath(i) != os.path.normpath(j):
                    # comparing the path in both lists
                    # if flag == max len of songs list the only the song adds into list
                    flag+=1
            if flag == max_count:
                self.songs_list.append(os.path.normpath(i)) # addes to song_list 

        self.songs_list = [Path(i).as_posix() for i in self.songs_list] # returna path as string in only forward slash

        if song_flag == True:
            # 'icacls file(or)folder /remove adminname' # for removing the permisions
            command = f'icacls {self.main_path} /remove {self.admin_name}'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            self.config.read(os.path.join(self.main_path,"user data.ini"),encoding='utf-8') # reads the catch file data
            l = self.config.get(section="DATA",option="songs_path").split(",") # selects the section of data returns list format because we use split func
            l = l[0:len(l)-1] # removes the last ","

            if l == []: # if l == [] means this is the first song to be entering into catch file
                self.config.set(section="DATA",option="songs_path",value=root+",") # settig to the catch file
                with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo: # make sue thst encoding = 'utf-8' for to add paths to catch file
                    self.config.write(fo) # writing to catch file

            elif l != []:
                flag = 0
                max_count = len(l)
                for i in l:
                    if os.path.normpath(i) != os.path.normpath(root):
                        flag+=1
                
                if flag == max_count:

                    my_str = ",".join(l)# joins every path by ","
                    my_str2 = my_str + "," + root + "," # the path ends with ',' that why we adding ',' for the last song
                    self.config.set(section="DATA",option="songs_path",value=my_str2)
                    with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                        self.config.write(fo)
                    # 'icacls file(or)folder /deny adminname:F' # for blocking the permissions
                    command = f'icacls {self.main_path} /deny {self.admin_name}:F'
                    subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        self.update_info_related_to_song() # update the songs added info in application

    def remove_song_folder(self,e:Event=None):
        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        folder = filedialog.askdirectory(title="Select Folder To Delete Songs From List") # opens file dialog
        path_lists = []
        if folder != None:
            # if only the folder != None 
            for root,dirs,files in os.walk(folder):
                for d in dirs:
                    path_lists.append(os.path.normpath(os.path.join(root,d))) # appends all sub folders if have

            songs_path = self.config.get(section="DATA",option="songs_path").split(",")
            songs_path_list2 = songs_path[0:len(songs_path)-1] # retuns all folders list in catch file

            c = 0
            indexes = []
            for paths in songs_path_list2:
                if path_lists != []:
                    # this condition is for when sub folder contains in you selected folder
                    for i in path_lists:
                        if os.path.normpath(i) == os.path.normpath(paths):
                            indexes.append(c) # appends all the matched folders

                elif path_lists == []:
                    # this condition if no sub folders contains 
                    if os.path.normpath(folder) == os.path.normpath(paths):
                        indexes.append(c)
                c+=1

            if len(indexes) == 1 and len(songs_path_list2) >= 1:
                # if and only if you selected only one folder to delete at a time and the application contains 
                # atleast one folder
                songs_path_list2.remove(songs_path_list2[indexes[0]]) # removes folder from list
                self.songs_list.clear() # delets all the list
                
                for i in songs_path_list2:

                    if os.path.normpath(i) == os.path.normpath(self.main_path):
                        self.songs_list.append(os.path.normpath(Path(self.main_path)/Path(r"Ye Mera Jahan.mp3")))

                    elif os.path.exists(i): # if only that path exixts in system
                        for j in os.listdir(i):
                            if os.path.splitext(j)[-1].lower().strip() in (".mp3"):
                                try:
                                    Audio = MP3(os.path.join(i,j))
                                    """ if the file is not able to play raises error"""
                                    if Audio:
                                        self.songs_list.append(os.path.normpath(os.path.join(i,j)))
                                except:
                                    pass
                self.songs_list = [Path(i).as_posix() for i in self.songs_list]

                current_song = self.config.get(section="DATA",option="current_song")# retuns current song from catch file
                current_song_folder = os.path.split(current_song)[0] # returns current song folder from current song 

                if os.path.normpath(current_song_folder) == os.path.normpath(folder):
                    # if the selected folder is current playing song folder
                    pygame.mixer_music.unload() # unloads the current song
                    self.current_song = None # setting the current song to None

                    self.left_time.configure(text="00:00:00") # change the text to default text
                    self.song_s.set(0) # setting slider position 0
                    self.reapeating_info.configure(text="") # setting the repeating song text to ""

                    self.update_info_related_to_song()

                    # setting current song data in catch file in above func the current song get selected
                    self.config.set(section="DATA",option="current_song",value=str(self.current_song))
                    with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                        self.config.write(fo)

                    pygame.mixer_music.load(self.current_song) # loades that current song
                    self.play_function()
                    self.pause_function()
                    self.left_time.configure(text="00:00:00")
                    
                elif os.path.normpath(current_song_folder) != os.path.normpath(folder): 
                    # if the selected folder is not current playing song folder
                    self.update_info_related_to_song(current_song)
                    
                my_str = ",".join(songs_path_list2)# joins every path by ","
                my_str2 = my_str + "," # the path ends with ',' that why we adding ',' for the last song
                self.config.set(section="DATA",option="songs_path",value=my_str2)
                with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                    self.config.write(fo)
            elif len(indexes)>1:
                """ if the len(indexes) >1 raises error message and beeep"""
                volume = self.volume_s.get()
                pygame.mixer_music.set_volume(0)

                winsound.Beep(frequency=350,duration=500)
                icons_path = os.path.join(self.main_path,'icons and photos')
                # sends the notification on desktop
                notify = Notification(app_id="Music Player",title="ERROR",msg="Only One Folder Choose At A Time",
                                        icon=os.path.join(icons_path,"icon.ico"))
                
                notify.set_audio(sound=audio.Mail,loop=False)
                notify.show()
                pygame.mixer_music.set_volume(volume/100) # pygame volume range min(0),max(1)

        else:
            #this condition is for if the folder not selected and close the dialog
            pass
        ## 'icacls file(or)folder /deny adminname:F'  # for blocking the permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    def update_info_related_to_song(self,Song=None):
        #currentSong=None  purpose for automatic select the last  current song when you closed before
        # this function is also calling from catch file in catch file we stores the currentsong info when you close the application
        # the current is the last song you played.
        # Song == last played song path when this function is called from checking_user_data func
        if self.current_song == None:
            if Song == None: # for any case the last played song gets deleted from the system the current song changes
                self.current_song = self.songs_list[0] # makes the curent song to the fisrt song that enteres in to songs_list
            if Song != None :# goes to last played song when you closes the app
                self.current_song = Song

            pygame.init()

            self.update_right_time()
            self.update_song_info()
            self.update_song_background()
            self.update_song_image()


            if self.is_palying == False: # checkes if the song is playing or not
                pygame.mixer_music.load(self.current_song) # loads the song into pygame
                pygame.mixer_music.set_volume(0.7) # settign the volume of app to 70 % max==1 means 100%
                try:
                    # for getting the entire song lenth and then we conreting into millisec
                    m,s =divmod(pygame.mixer.Sound(self.current_song).get_length(),60)
                    total = m*60000+s*1000 # convers min,sec to millisecs
                    self.song_s.configure(to=total) # changing the max len of slider  to total millisecs
                except:
                    """some audio fomat get exceptions but woks because of that we using try and except block"""
                    pass

        self.songs_list = [Path(i).as_posix() for i in self.songs_list]
        self.current_song = Path(self.current_song).as_posix() # return all slashes in forward only

        if self.songs_list.index(self.current_song) == len(self.songs_list)-1 and self.songs_list.index(self.current_song) == 0:
            # this conditon is for if only one song in the list
            # both buttons will disables
            self.previous_b.configure(state = DISABLED)
            self.next_b.configure(state = DISABLED)

        elif self.songs_list.index(self.current_song) == len(self.songs_list)-1:
            # if the current song is the last song the next button gets disabled
            # and activates the previous button by default it is in disabled mode
            self.next_b.configure(state = DISABLED)
            self.previous_b.configure(state = ACTIVE)

        elif self.songs_list.index(self.current_song) == 0:
            # if the current song is first song in the list the previous button gets disabled 
            # (By default it is in off mode ) but conformation
            # and activates the next button
            self.previous_b.configure(state = DISABLED)
            self.next_b.configure(state = ACTIVE)

        else:
            # for other cases both in active mode
            self.next_b.configure(state = ACTIVE)
            self.previous_b.configure(state = ACTIVE)
        
        self.add_items_to_listbox() # add the songs to list box that we see in right side
    

    def change_to_static(self):
        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        if self.is_static == False: # if the background mode is static
            self.is_static = True # making it true 
            
            #updating static data in catch file
            self.config.set(section='DATA',option="background",value="static")
            with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                self.config.write(fo)
            
            self.update_song_background()
        
        ## 'icacls file(or)folder /deny adminname:F'  # for blocking the permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)


    def change_to_dynamic(self):
        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        
        if self.is_static == True: # if the backgroung mode is static
            self.is_static = False # make to false
            
            # updating static data in catch data
            self.config.set(section='DATA',option="background",value='dynamic')
            with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                self.config.write(fo)
            self.update_song_background()
        
        ## 'icacls file(or)folder /deny adminname:F' # for blocking permisions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    

    def change_static_color(self):
        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        color = colorchooser.askcolor()[-1] # returns choosed color hexa code
        if color != None: # if color code not none
            self.static_color = color # changes the static color code

            if self.is_static == True:
                self.main_frame.configure(bg=self.static_color) # changes the main frame bg to color choosen
                self.song_image.configure(bg=self.static_color) # changes the song image bg to color choosen

            # updating the static color data in catch file
            self.config.set(section='DATA',option="static_color",value=f"{self.static_color}")
            with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                self.config.write(fo)

        ## 'icacls file(or)folder /deny adminname:F' # for blocking permisions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    

    def all_bindings_conditions(self,e:Event):
        """tkinter bindings"""
        is_search_foused = self.search_bar.focus_get().master # return's None if the search bar entry is Not foucused

        if e.keysym == "space" and is_search_foused == None:
            # splace bar is pressed
            if self.is_palying == True and self.current_song != None:
                # for song in play mode
                self.pause_function()
            elif self.is_pause == True and self.current_song != None:
                # for song is in pause mode
                self.unpause_function()
            elif self.is_palying == False and self.current_song != None:
                # for song is loaded and not pressed on play button in app
                self.play_function()
        elif e.keysym == "Right":
            # for volume up
            if self.current_song != None: # Base condition
                if self.volume_s.get() < 100:
                    self.update_volume_bar(self.volume_s.get()+10) # volume increse by 10% for every click
        elif e.keysym == "Left":
            # for volume down
            if self.current_song != None: # Base condition
                if self.volume_s.get()-10 > self.volume_limit_value and self.is_volume_limited == True:
                    self.is_volume_limited = False
                    self.update_volume_bar(self.volume_s.get()-10) 
                    # if the volume limit is in on raise a error notification so we change the value and again set to default

                    if self.int_var2.get() == 1:
                        self.is_volume_limited = True # means the volume limit is in on mode
                    
                elif self.volume_s.get() > 0:
                    self.update_volume_bar(self.volume_s.get()-10) # volume decresed by 10% for every click
        elif e.keysym == "Up":
            # for changing song
            song_index = self.songs_list.index(self.current_song)
            if song_index != 0:
               self.go_to_previous_track()
        elif e.keysym == "Down":
            # for changind song
            song_index = self.songs_list.index(self.current_song)
            if song_index != len(self.songs_list)-1:
               self.go_to_next_track()
        elif e.keysym == 's' and is_search_foused == None:
            self.shuffle_songs_list()
        elif e.keysym == 'm' and is_search_foused == None:
            self.volume_muting()
        elif e.keysym == 'r' and is_search_foused == None:
            self.repeat_song()


    
    def on_key_press(self, key):
        ### pynput listener
        ### it listens all keyboard presses
        "Key.space","Key.left","Key.right","Key.down","Key.up"
        """ The Base condtion is ***self.current song != None*** for all cases """
        if str(key) in ["Key.space"]:
            # if only these keys are pressed then only time changes
            self.current_time =  time.time() # return current time in milli seconds
        elif key in [keyboard.KeyCode(char='r'),keyboard.KeyCode(char='m'),keyboard.KeyCode(char='s')]:
            # if only these keys are pressed then only time changes
            self.current_time =  time.time() # return current time in milli seconds
        
        if self.current_time - self.last_time_key_pressed >= 0.1 and self.background_listen == True:
            """ this is useful when we press any key we will triger multipul times
                to reduce that we we using time.time - last time key pressed it should be 
                always greater the 0.1 seconds even though you presses two times
                less than 0.1 it will not triger"""
            self.last_time_key_pressed = self.current_time

            try:
                is_search_foused = self.search_bar.focus_get().master # return's None if the search bar entry is Not foucused 
            except:
                is_search_foused = None

            if str(key) == "Key.space" and is_search_foused == None:
                # splace bar is pressed
                if self.is_palying == True and self.current_song != None:
                    # for song in play mode    
                    self.pause_function()  
                elif self.is_pause == True and self.current_song != None:
                    # for song is in pause mode
                    self.unpause_function()
                elif self.is_palying == False and self.current_song != None:
                    # for song is loaded and not pressed on play button in app
                    self.play_function()
            
            elif key == keyboard.KeyCode(char='s') and is_search_foused == None:
                self.shuffle_songs_list()
            
            elif key == keyboard.KeyCode(char='r') and is_search_foused == None:
                self.repeat_song()
            
            elif key == keyboard.KeyCode(char='m') and is_search_foused == None:
                self.volume_muting()
            
    

    def background_listener(self):

        ## listens the events even the application in background for every click on keyboard it goes to (on_key_press) func
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
    

    def all_unbindings(self):
        ## 'icacls file(or)folder /remove adminname' # for removing permissions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        # unbinds all the tkinter bindings
        self.root.unbind("<space>")
        self.root.unbind("<s>")
        self.root.unbind("<m>")
        self.root.unbind("<r>")


        self.background_listen = True # turns on the backgroung listener to on mode

        self.string_var.set(value="ON") # setting the background listner radio button to ON mode

        # update the background listener data in catch file
        self.config.set(section='DATA',option='background_listner',value="True")
        with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
            self.config.write(fo)
        
        self.background_listener() # goes to (background_listener) func and stats listing the events

        ## 'icacls file(or)folder /deny adminname:F' 
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    

    def all_bindings(self):
        ## 'icacls file(or)folder /remove adminname' #for removing permissons
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        # binds to tkinter application
        self.root.bind("<Control-o>",self.add_folder)
        self.root.bind("<Control-d>",self.remove_song_folder)
        self.root.bind("<Left>",self.all_bindings_conditions)
        self.root.bind("<Right>",self.all_bindings_conditions)
        self.root.bind("<Up>",self.all_bindings_conditions)
        self.root.bind("<Down>",self.all_bindings_conditions)
        self.root.bind("<space>",self.all_bindings_conditions)
        self.root.bind("<s>",self.all_bindings_conditions)
        self.root.bind("<m>",self.all_bindings_conditions)
        self.root.bind("<r>",self.all_bindings_conditions)
        self.root.bind("<Control-Left>",self.backward_10sec)
        self.root.bind("<Control-Right>",self.forward_10sec)
        self.root.bind("<Tab>",self.destroy_list_box) 
        # this is for when ever tab is pressed the focus of entry box goes to list box but we dont want that  

        if self.background_listen == True: # if the background listener is in on mode

            self.background_listen = False # makes to false  
            self.string_var.set(value='OFF') # making the backgroung_lister radio button to "off" mode

            # updates the catch file
            self.config.set(section='DATA',option='background_listner',value="False")
            with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                self.config.write(fo)
            
            self.listener.stop()
            self.listener.stop() # stops listing events in background 

        ## 'icacls file(or)folder /deny adminname:F'  # for blocking permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    

    def reset_all(self):
        ## 'icacls file(or)folder /remove adminname' # for removing permissions
        try:
            command = f'icacls {self.main_path} /remove {self.admin_name}'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except:
            pass

        if self.is_palying == True : # if the song is playing make to pause
            self.pause_function()
        if self.current_song:
            pygame.mixer_music.unload()

        if os.path.exists(self.main_path):
            shutil.rmtree(f'{self.main_path}') # removes the entire catch files data from system

        self.root.destroy() # closes the application

    

    def close_application(self):

        if self.y_n.get() == 1: # y_n take the do you want the shut down the system if yes shutdows the system
            # 1 means on mode 0 means off moode by default 0
            os.system("shutdown /s /t 5") # shutdows the system in 5 secs

        self.root.destroy() # closes the application

    def change_timer(self,value):

        self.text_lable.configure(text=f'{int(value)} minutes from now') # changes the lable info to according to slider value
        
    def update_timer(self):

        time_in_millsec = int(self.timer.get())*60000 # converts in to millisecs
        self.timer_after = self.root.after(time_in_millsec,self.close_application) # calls the function after timeinmillsec
        self.is_timed = True # setting is_times to true uses 
       
        self.new_root.destroy() # destroyes the small window

    def cancleing_timer(self):

        if self.is_timed == True: # if only the is_tiemes to True means the user sets the tiemer for application

            self.is_timed = False
            self.root.after_cancel(self.timer_after)
    
    def checking_is_timer_setted(self,e=None):

        """ the main use of this func is when the user clicked on timer>>On mode the small window is poped up
            if user not set the timeing  and the small windows closed it makes a error that the timer radio button
            is in On mode only to make it off mode this func is useful"""
        
        # by defauly is_times is false only
        # is user sets the timer is_times is makes to true

        if self.is_timed == False:

            self.int_var.set(0) # if you doesn't check it is on on mode only

        self.new_root.destroy() # closes the small window

    
    def set_timer(self):

        if self.int_var.get() == 1 and self.is_timed == False : # On mode and is_timed to False
        
            self.new_root = Toplevel(self.root) # new small window opens
            # for focus on the new small window     
            # # if you not use this function we can't destroy the small window when it goes to background
            self.new_root.focus_force()

            icons_path = os.path.join(self.main_path,'icons and photos')
            self.new_root.iconbitmap(os.path.join(icons_path,"icon.ico"))
            self.new_root.geometry("400x400+400+150")
            self.new_root.resizable(width=False,height=False) # setting the small window to not resizeable
            
            
            self.timer = customtkinter.CTkSlider(self.new_root,width=400,from_=5,to=60,number_of_steps=11,
                                                 progress_color="#d4d65c",button_color="#d4d65c",hover=False,
                                                 command=lambda value:self.change_timer(self.timer.get()))
            self.timer.set(5) # by defalut setting to 5 minutes
            self.timer.place(x=0,y=0)

            self.text_lable = Label(self.new_root,text="5 minutes from now",font=(self.font_name,25),justify='center')
            self.text_lable.place(x=0,y=50)

            self.lable_frame = LabelFrame(self.new_root,width=400,height=200)
            self.lable_frame.place(x=0,y=100)

            self.info_lable = Label(self.lable_frame,text="close the system after time up",font=(self.font_name,16))
            self.info_lable.place(x=10,y=10)

            self.y_n = IntVar()
            self.radio_b = customtkinter.CTkRadioButton(self.lable_frame,text="Yes",value=1,variable=self.y_n,font=("Times New Roman",15),text_color='black')
            self.radio_b.place(x=0,y=100)
            self.radio_b = customtkinter.CTkRadioButton(self.lable_frame,text="No",value=0,variable=self.y_n,font=("Times New Roman",15),text_color='black')
            self.radio_b.place(x=250,y=100)
            self.y_n.set(0) # by default to no mode

            self.save_b = Button(self.new_root,text="Set",font=(self.font_name,25),width=10,highlightthickness=0,
                                 command=self.update_timer)
            self.save_b.place(x=0,y=330)

            self.close_b = Button(self.new_root,text="cancle",font=(self.font_name,25),width=11,
                                  highlightthickness=0,command=self.checking_is_timer_setted)
            self.close_b.place(x=200,y=330)

            self.new_root.attributes('-alpha',0.8) # for making window into transparent 0 means fulley transparent 1 means full white
            self.new_root.overrideredirect(True) # making the small window to does not having buttons like(close,minimize,maximize)
            
            # binds the small window focusout mode  
            ## when the small window goes to background  (checking_is_timer_setted)  and destroys in that func
            self.new_root.bind("<FocusOut>",self.checking_is_timer_setted)

            self.new_root.mainloop()
    
        
        elif self.int_var.get() == 0: # OFF mode

            self.cancleing_timer()

    def on_off_volume_limit(self):
        
        if self.int_var2.get() == 0: 
            # Means OFF Mode if you want to off you need to give the password default password is 0000
            self.new_root2 = Toplevel(self.root)
            # for focus on the new small window     
            # # if you not use this function we can't destroy the small window when it goes to background
            self.new_root2.focus_force()

            icons_path = os.path.join(self.main_path,'icons and photos')
            self.new_root2.iconbitmap(os.path.join(icons_path,"icon.ico"))
            self.new_root2.geometry("400x70+400+600")
            self.new_root2.configure(background="#FFFFFF")
            self.new_root2.resizable(width=False,height=False) # setting the small window to not resizeable

            self.volume_limit_password = customtkinter.CTkEntry(self.new_root2,width=400,height=20,
                                                                placeholder_text='Enter Volume limit password',font=(self.font_name,25),
                                                                placeholder_text_color='#d4d002',text_color='#7bb9e8',fg_color='#FFFFFF',
                                                                justify='center',border_width=0,show='*')
            self.volume_limit_password.place(x=0,y=0)
            self.password = customtkinter.CTkCheckBox(self.new_root2,width=100,height=10,text="Show Password",font=(self.font_name,15),
                                                      text_color='#000000',fg_color='#FFFFFF',command=self.show)
            self.password.place(x=0,y=40) 

            self.new_root2.bind('<Return>',self.checking_volume_limit)
            self.new_root2.bind('<FocusOut>',self.checking_volume_limit)

            self.new_root2.attributes('-alpha',0.5)
            self.new_root2.overrideredirect(True) # making the small window to does not having buttons like(close,minimize,maximize)
            self.new_root2.mainloop()
        
        elif self.int_var2.get() == 1:
            # Means On Mode
            self.is_volume_limited = True
            if self.volume_s.get()>=self.volume_limit_value:
                # if the volume value greater than limit value
                pygame.mixer_music.set_volume(self.volume_limit_value/100)
                self.volume_s.set(self.volume_limit_value)
                self.volume_s.configure(progress_color = '#3cc920')
                self.volume_frame.configure(text=f'Volume {self.volume_limit_value}%')
                
                self.config.set(section="DATA",option='volume',value=str(self.volume_limit_value))
                # changing the volume data in catch file
                with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
                    self.config.write(fo)
    def change_volume_limit_value(self):

        self.new_root3 = Toplevel(self.root)
        # for focus on the new small window     
        # # if you not use this function we can't destroy the small window when it goes to background
        self.new_root3.focus_force()

        self.new_root3.geometry("300x100+450+600")
        self.new_root3.resizable(width=False,height=False) # setting the small window to not resizeable

        
        self.lf = LabelFrame(self.new_root3,text="Volume Limit 60%",width=300,height=300,font=(self.font_name,15),
                        fg="#A31214")
        self.lf.place(x=10,y=0)
        sl = customtkinter.CTkSlider(self.lf,from_=40,to=80,number_of_steps=4,width=280,height=20,
                                     command=self.volume_limit_update_slider)
        sl.pack()
        sl.set(60)
        customtkinter.CTkButton(self.new_root3,width=300,height=15,fg_color=self.fg,
                                text_color="#50C763",hover_color="#94D1D1",
                                text="Set Limit Value",font=(self.font_name,25),
                                command=lambda :self.set_new_volume_limit(sl.get())).place(x=0,y=60)
        
        self.new_root3.bind("<FocusOut>",lambda x: self.new_root3.destroy())

        self.new_root3.attributes('-alpha',0.5)
        self.new_root3.overrideredirect(True) # making the small window to does not having buttons like(close,minimize,maximize)
        self.new_root3.mainloop()

    def volume_limit_update_slider(self,value):
        self.lf.configure(text=f"Volume Limit {int(value)}%")
    def set_new_volume_limit(self,value):
        # 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        self.volume_limit_value = int(value)
        original_value = int(self.config.get(section="DATA",option='volume'))
        if original_value >= self.volume_limit_value:
            # if volume is greater than limit value the progress bar color changes to red
            self.volume_s.configure(progress_color = "#f7020f")

        else:
            # sets to default green color
            self.volume_s.configure(progress_color = '#3cc920')

        self.config.set(section="DATA",option='volume_limit_value',value=str(int(value)))
        # changing the volume data in catch file
        with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
            self.config.write(fo)
        
        self.new_root3.destroy()
        
        ## 'icacls file(or)folder /deny adminname:F' # for blocking permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)


    
    def change_font(self):
        # 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)


        self.font_name = self.string_var2.get()

        self.list_box.configure(font=(self.font_name,15))
        self.song_info_b.configure(font=(self.font_name,20))
        self.search_bar.configure(font=(self.font_name,16))
        self.reapeating_info.configure(font=(self.font_name,15))
        self.volume_frame.configure(font=(self.font_name,10))

        self.file_menu.configure(font=(self.font_name,10))
        self.shortcuts_menu.configure(font=(self.font_name,10))
        self.settings_menu.configure(font=(self.font_name,10))
        self.background_menu.configure(font=(self.font_name,10))
        self.helpmenu.configure(font=(self.font_name,10))

        self.destroy_list_box() # destroys list and create it again

        self.config.set(section="DATA",option='font_name',value=str(self.font_name))
        # changing the volume data in catch file
        with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
            self.config.write(fo)
        
        
        ## 'icacls file(or)folder /deny adminname:F' # for blocking permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    
    def change_cover_image_delete(self,delete=False):
        song1 = self.current_song # returns the current song path
        
        try:
            img = None
            if delete == False:
                # if delete is false means to change the cover image so the file dialog is opens
                img = filedialog.askopenfile(mode='r',filetypes=(('PNG','*.png'),),title='Select Cover Image File').name

            if img != None or delete == True:
                song2 = self.current_song
                # this condition is for when you select the image at the last of the song the current song 
                # gets changed then the image cover data will not change
                if os.path.normpath(song1) == os.path.normpath(song2): 
                    #purpose #os.path.normpath() matches even though slases(//) is single or double both or same
                    # when we you == it will not math exarctly b/w two paths

                    play,pause = self.is_palying,self.is_pause # saves the values before changing in pause function the values change
                    self.pause_function()
                    pos = pygame.mixer_music.get_pos()+self.value_seeked # value seeked added because due to pygame error
                    pygame.mixer_music.unload() # unloads the song

                    if delete == False:
                        # this is for changing the cover image
                        self.image_changer(song_path=song2,img_path=img) 
                    elif delete == True:
                        # this is for deleting the cover image
                        self.delete_cover_image()
                    
                    pygame.mixer_music.load(song2) # Again loads the current song
                    self.update_song_image() # change the image in the image display part

                    m,ts = divmod(pos,60000) # changes to seconds because pygame takes only seconds
                    s,_ = divmod(ts,1000)
                    total_secs = m*60+s
                    
                    if play == False and pause == False:
                        #It is for starting of the app when not clicking and play/pause button's
                        self.is_palying = False
                        self.is_pause = False # again setting the is_playing ,is_pause to default mode
                        self.play_b.configure(command = self.play_function) 
                        # change the play button command to againg to play function
                        # in previous we use pause func in this func in that the command changed so that's why 
                        # we again changed to play function
                    elif pause == True:
                        # if the song is in pause mode
                        # first setting volume to 0 make work done again set the volume to again original
                        # Because due to while changing image the song play and then pause while playing the sound came out
                        pygame.mixer_music.set_volume(0)
                        pygame.mixer_music.play()
                        pygame.mixer_music.set_pos(total_secs)
                        self.is_seek = True
                        self.value_seeked = pos
                        self.pause_function()
                        volume = self.volume_s.get()
                        pygame.mixer_music.set_volume(volume/100) # pygame range min(0),max(1)
                    elif play == True:
                        # if the song is in play mode
                        pygame.mixer_music.play()
                        pygame.mixer_music.set_pos(total_secs) # sets the postion of the song
                        self.is_palying = True
                        self.is_pause = False
                        self.is_seek = True
                        self.value_seeked = pos

                        self.play_b.configure(text="\u23F8") # changes the text to pause unicode
                        self.play_b.configure(command = self.pause_function) # change the play button command
                        self.update_slider() # goes to update slider function
                        self.update_left_time() # goes to update left time lable
        except:
            "if you close the file dialog without selecting file it raises an error"
            pass
    
    def delete_cover_image(self):

        song = eyed3.load(self.current_song)

        for i in song.tag.frame_set:

            if b"APIC" == i:
                del song.tag.frame_set[i]
                break
        song.tag.save()
    
    def image_changer(self,song_path,img_path):
        # get's the all song data
        try:
            song_data = File(song_path)
            for i in song_data.tags.keys(): # loop through all keys in dict
                if 'APIC:' in i:
                    del song_data[i] # deletes that key
                    break
            song_data.save() # save's the song data

            # this is for saving the song in that location and made changes in image size
            # upload the image into song data
            path,name = os.path.split(img_path) # splits the path,song name with extension
            name,_ = os.path.splitext(name) # splits the songname,extension
            name = name+"qwertyuio.png" # adding some random text to the new path that doen't exits before
            second_path = os.path.join(path,name) # creating that path

            img = Image.open(img_path).resize((350,350)) # (350,350) is the original cover image size
            img.save(second_path) # saving the modified data in second path
            
            with open(second_path,'rb') as fo:
                data = fo.read() # reades the image data

            new_data = APIC(mime='image/jpeg',type=3,data=data)
            song_data.tags.add(new_data) # add the data to song data
            song_data.save() # save the data

            os.remove(second_path) # deleting the second path
        except:
            """ If the file is accessing some where else """
            volume = self.volume_s.get()
            pygame.mixer_music.set_volume(0)

            winsound.Beep(frequency=350,duration=500)

            pygame.mixer_music.set_volume(volume/100) # pygame volume range min(0),max(1)

        
    def show(self):

        if self.volume_limit_password.cget('show') == '*':
            self.volume_limit_password.configure(show='')
        
        elif self.volume_limit_password.cget('show') == '' and self.volume_limit_password.get() == '':
            self.volume_limit_password.configure(show='')

        else:
            self.volume_limit_password.configure(show='*')

    
    def checking_volume_limit(self,e:Event=None) ->None:

        if self.volume_limit_password.get() == '0000': # "0000" is the default password
            self.is_volume_limited = False
        
        elif self.volume_limit_password.get() == '':
            # if NO password enter
            #again set the radio button to ON Mode
            self.int_var2.set(1)
        else:
            # else again set the radio button to ON Mode
            self.int_var2.set(1)

            if str(e.char) != '??':
                # sends notification to desptop window
                icons_path = os.path.join(self.main_path,'icons and photos')
                notify = Notification(app_id="Music Player",title="Error",msg="Wrong password",
                                        icon=os.path.join(icons_path,"icon.ico"))
                notify.set_audio(sound=audio.Reminder,loop=False)
                notify.show()
        
        self.new_root2.destroy()
    
    def update_date_and_time(self):

        date = datetime.now().strftime("%a  %d-%b-%Y")
        time = datetime.now().strftime("%H:%M:%S")

        self.my_menu.delete(82,82) # deletes the label of date time which add previous
        self.my_menu.add_cascade(label=f"{date}     {time}  IST",command=self.browser)

        
        try:
            if self.is_timed:
                # if the timer is in on mode
                if int(datetime.now().strftime("%S"))%2 == 0:
                    self.timer_info_label = customtkinter.CTkLabel(self.main_frame,text="** TIMER ON **",font=("Times New Roman",20),
                                                            width=20,height=25,
                                                            text_color='#FF0000')
                    self.timer_info_label.place(x=560,y=690)
                else:
                    self.timer_info_label.configure(text=" "*28)
                    del self.timer_info_label
            else:
                self.timer_info_label.configure(text=" "*28)
                del self.timer_info_label
        except:
            pass


        self.root.after(1000,self.update_date_and_time)

    def browser(self):
        webbrowser.open("https://www.timeanddate.com/worldclock/india/vijayawada")



    """****************************************** MAIN FRAME FUNCTIONS ***************************************"""

    def update_song_background(self):

        if self.is_static == False: # if the backgroung is in dynamic mode

            red = random.randint(150, 255)
            green = random.randint(150, 255)
            blue = random.randint(150, 255)

            # Convert RGB values to a hexadecimal color code
            random_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)
            self.song_image.configure(bg=random_color) # accessing the first element
            self.main_frame.configure(bg=random_color) # accessing the first element

            self.root.after(5000,self.update_song_background) # for every 5 sec it goes to (update_song_background) func and genarates a random color again 

        elif self.is_static == True:

            ## 'icacls file(or)folder /remove adminname' # for remove permissions
            command = f'icacls {self.main_path} /remove {self.admin_name}'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

            # gets the static color that saved in catch file
            color = self.config.get(section='DATA',option='static_color')
            self.main_frame.configure(bg=color)
            self.song_image.configure(bg=color)

            ## 'icacls file(or)folder /deny adminname:F' # for blocking permissions
            command = f'icacls {self.main_path} /deny {self.admin_name}:F'
            subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    def animaee(self):

        if self.is_palying == True:
            self.index_count +=1
            if self.index_count == len(self.gif_images_list):
                self.index_count = 0
            self.song_image.configure(image=self.gif_images_list[self.index_count])

        self.is_gif_timer_cancled = False
        self.gif_timer = self.root.after(50,self.animaee)

        
    def update_song_image(self):
        
        ## 'icacls file(or)folder /adminname seela'  # for removing permisons
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        if self.is_gif_timer_cancled == False:
            # by default it deletes the timer func of the gif image
            self.is_gif_timer_cancled = True
        
            self.root.after_cancel(self.gif_timer)

        photes_path = os.path.join(self.main_path,"icons and photos") # returns the icons and photes path
        try:
            audio = eyed3.load(self.current_song) 
            if b"APIC" in audio.tag.frame_set: # if only "APIC:" data in audio

                cover_data = audio.tag.frame_set[b'APIC'][0].image_data

                with open(os.path.join(photes_path,"song cover photo.png"),'wb') as fo: # writing the data into sove cover photo in photes path
                    fo.write(cover_data)
                
                # changes the image that shown in main frame
                self.image = Image.open(os.path.join(photes_path,"song cover photo.png")).resize((500,500))
                self.photo_image = ImageTk.PhotoImage(self.image)
                self.song_image.configure(image=self.photo_image)
                self.song_image.configure(image=self.photo_image)
                    
            else:
                raise # Raises an exception 

        except Exception as e:
            self.index_count = 0
            self.song_image.configure(image=self.gif_images_list[self.index_count])
            self.animaee()
            

        ## 'icacls file(or)folder /deny adminname:F' # for blocking permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

    def download_image(self):
        # 'icacls file(or)foldername /remove adminname' # for removeing permissions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        folder_path = os.path.join(self.main_path,'icons and photos')

        aud = eyed3.load(self.current_song) 
        if b"APIC" in aud.tag.frame_set: # if only "APIC:" data in audio
            image_path = os.path.join(folder_path,"song cover photo.png")
        else:
            image_path = os.path.join(folder_path,"gif image.gif")

        output_folder = os.path.join(self.pre_admin_path,"Downloads")

        shutil.copy2(image_path,output_folder) # copyes the file data from sorce to destination folder

        x = datetime.now().strftime('%Y-%m-%d %H_%M_%S.%f') # date time format

        # remaned the copied file with respective to date time
        if b"APIC" in aud.tag.frame_set:
            os.rename(os.path.join(output_folder,"song cover photo.png"),os.path.join(output_folder,f'{x}.png'))
            # opens the renamed file and resize the image to (1000,1000) and save it in same folder
            i = Image.open(os.path.join(output_folder,f"{x}.png")).resize((1000,1000))
            i.save(os.path.join(output_folder,f"{x}.png"))
        else:
            os.rename(os.path.join(output_folder,"gif image.gif"),os.path.join(output_folder,f'{x}.gif'))

        # icacls file(or)folder name /deny seela:F # for blocking permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        icons_path = os.path.join(self.main_path,'icons and photos')
        # sends the notification on desktop
        notify = Notification(app_id="Music Player",title="Image",msg="Downloaded to this PC",
                                icon=os.path.join(icons_path,"icon.ico"))
        if b"APIC" in aud.tag.frame_set:
            notify.add_actions(label="OPEN",launch=os.path.join(output_folder,f"{x}.png"))
        else:
            notify.add_actions(label="OPEN",launch=os.path.join(output_folder,f"{x}.gif"))

        notify.set_audio(sound=audio.Mail,loop=False)
        notify.show()
        
    def create_menu_for_dowanload(self,e):

        self.dowanload_menu = Menu(self.root,tearoff=0,bg="#FFFFFF",fg="#000000",font=(self.font_name,10))
        self.dowanload_menu.add_command(label="Download image",command=self.download_image)
        self.dowanload_menu.tk_popup(e.x_root,e.y_root)    
    
    

    """****************************************** List box functions ***************************************"""

    def add_items_to_listbox(self):

        self.list_box.delete(0,END) # deletes all items

        for i in self.songs_list:

            name = os.path.split(i)[-1] # retuns song name with extension
            songname = os.path.splitext(name)[0] # returns only song name

            if len(songname) <= 40:
                self.list_box.insert(END,songname) # insert full song name to end of list 

            else:
                songname = songname[0:40] + "..."
                self.list_box.insert(END,songname) # insert song name upto 40 chars only then after "..." to to last

        self.update_list_box_view() # to scroll to current song
    
    def shuffle_list_box(self):

        self.list_box.delete(0,END) # deletes all items

        for i in self.songs_list:

            name = os.path.split(i)[-1] # retuns song name with extension
            songname = os.path.splitext(name)[0] # returns only song name

            if len(songname) <= 40:
                self.list_box.insert(END,songname) # insert full song name into list

            else:
                songname = songname[0:40] + "..." # insert song name upto 40 char only after that "..." added to name
                self.list_box.insert(END,songname)

        self.update_list_box_view() # to scroll to current song

    def custom_song(self,e):

        song_index = self.list_box.curselection()[0] # returns the index of the selected one in tuple format
        
        if self.is_searching == True:
            # this is for when user searched for song
            indexes_with_names = {}
            count = 0
            for i in range(len(self.songs_names)):
                if self.songs_names[i] == self.list_box.selection_get():
                    indexes_with_names.update({count:self.songs_list[i]})
                    count+=1
          
            try:
               # if the two song names are same this will work else raises error
               index = self.songs_list.index(indexes_with_names[song_index]) # returns index in self.songs_list
               self.search_bar.delete(0,END) # deletes the search bar text
               song_index = index
            except:
               # if only one song is exists it is the 0 th item in dict
               index = self.songs_list.index(indexes_with_names[0]) # returns index in self.songs_list
               self.search_bar.delete(0,END) # deletes the search bar text
               song_index = index

        if song_index == len(self.songs_list)-1 and song_index == 0:
            # for the case when the list box have only one song
            self.next_b.configure(state = DISABLED)
            self.previous_b.configure(state = DISABLED)

        elif song_index == len(self.songs_list)-1:
            # condition for the song is the last of the list
            self.next_b.configure(state = DISABLED)
            self.previous_b.configure(state = ACTIVE)

        elif song_index == 0:
            # condition for the song is the starting of the list
            self.previous_b.configure(state = DISABLED)
            self.next_b.configure(state = ACTIVE)

        else:
            # for all remianing cases both are in active mode
            self.next_b.configure(state = ACTIVE)
            self.previous_b.configure(state = ACTIVE)
        
        if song_index == self.songs_list.index(self.current_song):
            # if user clicked on current song 
            if self.is_palying == False and self.is_pause == False:
                """ this function is only for the 1st time when the user click
                    directly hilighted song in list box the the song gets played"""
                self.is_palying = True

                self.play_function()


        elif song_index != self.songs_list.index(self.current_song):
            # if only when the user clicks on differnt song not a current song 
            # then only this condition satisefies
            self.current_song = self.songs_list[song_index] # returns current song index

            """  By default all these are False or None before the new song gets played """
            self.is_pause = False # setting global is_pause to False
            self.is_seek = False # setting global is_seek to False 
            self.is_repeating = False # setting is_repating to false
            self.repeating_song_name = None # setting repeating song name to None


            pygame.mixer_music.load(self.current_song) # loads the current song
            self.left_time.configure(text="00:00:00") # change the text to default text

            self.play_function() # goes to play function
            self.song_s.set(0) # setting slider position 0
            self.update_right_time() # goes to update right time function
            self.update_song_info() # goes to update song info function
            self.reapeating_info.configure(text="") # setting the repeating song text to ""
             
            try:
                m,s =divmod(pygame.mixer.Sound(self.current_song).get_length(),60) # gets the entire song length in seconds
                total = m*60000+s*1000 # converts into milliseconds
                self.song_s.configure(to=total) # setting the max slider to = len of full song in milliseconds
            except:
                """some audio fomat get exceptions but woks because of that we using try and except block"""
                pass

        self.destroy_list_box()
        self.destroy_search_bar()
     
    def destroy_list_box(self,e=None):
        """
        We destroying list box every time when the user click on custom song and creating again
        because when the user select song by custom the list box song is selected due to that when
        ever you want to search the selected item will unselected due to that we cant use up and down 
        buttons to go to next/prev songs. Thats why we using this and we also bind the buttons to
        tkinter to go next/prev songs.
        """
        self.list_box.destroy()
        self.list_box = Listbox(self.list_box_frame,width=330,font=(self.font_name,15),yscrollcommand=self.list_box_scroll_bar.set,
                                activestyle='none',selectbackground='#808080',selectforeground='#07f592',cursor='hand2')
        self.list_box.pack(side=LEFT,fill=Y)

        self.list_box.bind("<<ListboxSelect>>",self.custom_song)
        self.list_box_scroll_bar.configure(command=self.list_box.yview)
        self.list_box.bind("<Tab>",self.destroy_list_box)
        self.add_items_to_listbox()
    
    def destroy_search_bar(self,e:Event=None):
        """
            Destroys search_bar and again creates because of to focus out from search bar
            if you not focus out when you enter space bar in search bar the song will pause 
        """
        self.search_bar.destroy()
        self.search_bar = customtkinter.CTkEntry(self.songs_list_frame,width=334,height=20,corner_radius=50,
                                            fg_color="#FFFFFF",text_color="#000000",font=(self.font_name,16),
                                            placeholder_text="Search for song...",border_color="#000000")
        self.search_bar.place(x=0,y=693)
        self.search_bar.bind("<KeyRelease>",self.search)
        self.search_bar.bind("<Tab>",self.destroy_list_box)
        self.search_bar.bind("<Leave>",self.destroy_list_box)
        self.search_bar.bind("<Leave>",self.destroy_search_bar)


    def update_list_box_view(self):

        index = self.songs_list.index(self.current_song) # returns currentsong index
        self.list_box.select_clear(first=0,last=END) # clears all selected one
        self.list_box.select_set(index,last=None) # select the song in list box
        self.list_box.see(index=index) # scrolled to the selected song where it placed in list box
    
    def search(self,e:Event):
        
        name = self.search_bar.get() 
        self.songs_names= []
        
        for i in self.songs_list:
               name_with_extension = os.path.split(i)[-1]
               song_name = os.path.splitext(name_with_extension)[0]
               self.songs_names.append(song_name)

        if name == "":
            self.list_box.delete(0,END)
            for i in self.songs_names:
                self.list_box.insert(END,i)
            self.is_searching = False
            self.update_list_box_view()

            self.destroy_search_bar()

        else:
          self.list_box.delete(0,END)
          for i in self.songs_names:
               if name.lower() in str(i).lower():
                   self.list_box.insert(END,i)
                   self.is_searching = True
    

    """ ************************************* Slider frame functions **************************"""

    def update_slider(self):
        
        # current_pos is for forwarding 10 sec and backwading 10 sec purpose only
        if self.is_seek == True: # if the self.is_seek if true
            """means the user attempted to seek the song"""
            """ There is an glich in pygame,mixer_music.get_pos() when we set the postion of song 
            to certain position the get_pos goes to 0 and start from there
            """
            # so we adding seeked value to get_pos to get exeart postion of song
            postion = pygame.mixer_music.get_pos()+self.value_seeked

        else:
            # if not seeked we taking from pygame function only
            postion = pygame.mixer_music.get_pos()

        self.song_s.set(postion) # setting the slider postion with respect to song postion


    def set_slider(self,value):
        flag = True #purpose    #when user directly user slider button to seek the song before click on play button

        # means current song not be empty and song in play mode not pause
        if self.current_song != None: 
            # cancles the self.left_after because we need to change the time with respective to slider postion
            # only when the song is in play mode
            if self.is_palying == True:
                self.root.after_cancel(self.left_after)  #cancles the left_after
                flag = False

            self.song_s.set(value) # set the slider postion  # here value is slider point where we click
            self.value_seeked = value # seeked value is the value that seeked from starting point means 0 

            """ we convets seeked value into seconds because pygame.mixer_music.set_pos() takes only seconds """
            m,ts = divmod(value,60000)
            s,_ = divmod(ts,1000)
            total_secs = m*60+s

            """ we are unload the currnet pygame and stop the song that we loaded prevoious
                then again load the current song and set the postion to value that we seeked from starting point 0"""
            
            pygame.mixer_music.unload()  # unloads the song # here only the the unloads from pygame
            pygame.mixer_music.stop() # stop playing the song  # need not do this step # your wish
            pygame.mixer_music.load(self.current_song) # again loads the same current song
            pygame.mixer_music.play() # strts playing
            pygame.mixer_music.set_pos(total_secs) # set the postion of song to seeked value

            self.is_seek = True # setting global is_seek to True
            self.update_slider() # goes to update slider function
            self.update_left_time() # goes to update left time function


            # if user access the slider without click on play button
            if flag == True:
                self.is_palying = True # setting global is_playing to true
                self.play_b.configure(text="\u23F8") # changes the text to pause unicode
                self.play_b.configure(command = self.pause_function) # changing the command to pause function from play fuction
    
    

    """**************************** control paneal functions *********************************"""

    def update_left_time(self):

        time = self.song_s.get() # getting the slider postion in millseconds

        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        self.config.set(section="DATA",option='last_pos',value=str(int(time)))
        # changing the last pos value in catch file

        with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
            self.config.write(fo)
        
        ## 'icacls file(or)folder /deny adminname:F'  # for blocking the permissions
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        """The slider length is length of the song Every time the song get's changed the slider length changes"""
        h,ts = divmod(time,3600000) # divides the postion of slider by 3600000 to get hours and minutes
        m,ts = divmod(ts,60000) # divided the postion of slider by 60000 to get mimutes,seconds
        s,_ =divmod(ts,1000)# divides the seconds and milliseconds into minutes and milliseconds

        if pygame.mixer_music.get_busy() == True: #if only the music is playing we update the left time lable
            
            self.left_time.configure(text=f"{round(h):02}:{round(m):02}:{round(s):02}")
            self.update_slider()# also updating the slider postion with respective to song

        elif (pygame.mixer_music.get_busy() == False and self.songs_list.index(self.current_song)!=len(self.songs_list)-1 ) and self.is_pause == False and self.is_repeating == False:#means completed current song
            
            """ we using active or normal mode because some it returns active and some times it returns normal """
            if self.next_b.cget("state") == ACTIVE or self.next_b.cget("state") == NORMAL: # if only next button state == active means the next song is avilable in list
                self.go_to_next_track() # go to next track
        
        # for the repeating song mode the # pygeme.get_busy==self.is_pause == False  and self.is_repeating == True
        elif pygame.mixer_music.get_busy() == False and self.is_pause == False and self.is_repeating == True:
            # repeating_song_name is the current song only
            pygame.mixer_music.load(self.repeating_song_name) # loads the current song again into pygame
            self.left_time.configure(text="00:00:00")
            self.song_s.set(0) # setting song scroll vale to 0 before going to next song

            """ default all these are the false and None"""
            self.is_pause = False
            self.is_seek = False
            self.is_repeating = False
            self.repeating_song_name = None

            self.reapeating_info.configure(text="") # setting the repeating song text to "" 
            self.play_function()
        
        elif pygame.mixer_music.get_busy() == False and self.songs_list.index(self.current_song) == len(self.songs_list)-1 and self.is_pause == False:
            """ This is for when the song was at last and completed playing"""
            """ index starting from 0 last song index == len(self.songs_list)-1"""

            self.is_palying = False
            self.left_time.configure(text=self.right_time.cget('text')) # change the text to right time text
            self.song_s.set(self.song_s.cget('to')) # setting the slider postion to last
            self.play_b.configure(text="\u25B6") # changes to play unicode
            self.play_b.configure(command=self.play_function)# changes to play function
        

        self.left_after=self.root.after(1000,self.update_left_time) # goes to update_left_time for every 1 sec

    
    def update_right_time(self):

        try:
            song_time = pygame.mixer.Sound(self.current_song).get_length() # gets the entire song length in minutes
            h,ts = divmod(song_time,3600) # divides the song into houres and minutes
            m,s = divmod(ts,60)# divide the ts  into minutes,seconds

        except:
            """some audio fomat get exceptions but woks because of that we using try and except block"""
            pass

        self.right_time.configure(text=f"{round(h):02}:{round(m):02}:{round(s):02}") # changes when the the song gets changed
    

    def update_song_info(self):

        song_name = os.path.split(self.current_song)[-1] # return the song name with extension like (.mp3,.wav)
        text = os.path.splitext(song_name)[0] # return song name only

        if len(text)<=40:
            self.song_info_b.configure(text=text) # prints the text in sonf_info_b

        else:
            # if the lenght of the song is greater than 40 charters after 40 charters it add .... to it 
            text = text[0:40] + "..."
            self.song_info_b.configure(text=text)# prints the text in sonf_info_b
            
        self.song_info_b.bind("<Button-1>",self.full_info)
    
    def full_info(self,e:Event=None):
        self.new_root4 = Toplevel(master=self.root,background="#91EDC0")
        self.new_root4.title(string="Song Information")
        self.new_root4.geometry(newGeometry="340x520+0+80")
        self.new_root4.resizable(width=False,height=False)
        self.new_root4.iconbitmap(bitmap=Path(self.main_path)/Path("icons and photos")/Path("icon.ico"))

        def on_enter(value):
            x:id3.tag.Tag = eyed3.load(self.current_song).tag
            match value:
                case "a":
                    value = x.artist
                case "b":
                    value = x.album
                case "c":
                    value = x.genre
                case "d":
                    value = x.publisher
                case "e":
                    value = x.composer
                case "f":
                    value = x.recording_date
                case "g":
                    value = f"{eyed3.load(self.current_song).info.size_bytes / (1024 * 1024):.2f} Mb"
                case "h":
                    if Path(self.current_song).parent != Path(self.main_path):
                        value = Path(self.current_song).parent
                    else:
                        value = Path(self.current_song).name
                case "i":
                    value = x.album_artist

            text_label.configure(text = f"{value}")
        def copy_text():
            self.new_root4.clipboard_clear()
            self.new_root4.clipboard_append(text_label.cget("text"))
        
        a = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Artist ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        b = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Album ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        c = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Genre ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        d = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Publisher ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        e = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Composer ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        f = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Year ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        g = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Size ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        h = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Path ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")
        i = customtkinter.CTkButton(master=self.new_root4,width=60,height=25,text="Album Artist ",font=(self.font_name,25)
                               ,text_color="#000000",corner_radius=500,fg_color="#F2C450")

        
        text_label = customtkinter.CTkLabel(master=self.new_root4,
                                            width=340,height=25,fg_color="#FFFFFF",corner_radius=50,
                                            text_color="#000000",text="")
        text_label.place(x=0,y=475)
        
        co = customtkinter.CTkButton(master=self.new_root4,width=340,height=2,fg_color="#FFFFFF",
                                     corner_radius=50,text="Copy Text",text_color="#000000",
                                     command=copy_text)
        co.place(x=0,y=500)

        a.place(x=10,y=5),b.place(x=120,y=5),c.place(x=230,y=5),d.place(x=10,y=60),e.place(x=170,y=60)
        f.place(x=10,y=115),g.place(x=120,y=115),h.place(x=230,y=115),i.place(x=10,y=165)
        
        a.bind("<Enter>",command=lambda x:on_enter("a"))
        b.bind("<Enter>",command=lambda x:on_enter("b"))
        c.bind("<Enter>",command=lambda x:on_enter("c"))
        d.bind("<Enter>",command=lambda x:on_enter("d"))
        e.bind("<Enter>",command=lambda x:on_enter("e"))
        f.bind("<Enter>",command=lambda x:on_enter("f"))
        g.bind("<Enter>",command=lambda x:on_enter("g"))
        h.bind("<Enter>",command=lambda x:on_enter("h"))
        i.bind("<Enter>",command=lambda x:on_enter("i"))

        self.new_root4.focus_force() # focusing the new root 4 by default it is not focus 
        self.new_root4.bind("<FocusOut>",lambda x: self.new_root4.destroy()) # if focus out we destroy it 
        self.new_root4.mainloop()
    

    def shuffle_songs_list(self):

        random.shuffle(self.songs_list)# shuffle the songs_list

        ### always keeping  the curresnt song in 0 index
        self.songs_list.remove(self.current_song)
        self.songs_list.insert(0,self.current_song)
        self.shuffle_list_box() # making changes in list box also

        if self.songs_list.index(self.current_song) == len(self.songs_list)-1:
            # means after shuffle if the current song song indxes goes to last one then the next button gets disables
            # and previous_b to disable mode
            self.previous_b.configure(state = DISABLED)
            self.next_b.configure(state = DISABLED)

        elif self.songs_list.index(self.current_song) == 0:
            # means after shuffle if the current song song indxes goes to first one then the previous button gets disables
            # and next_b to active mode
            self.previous_b.configure(state = DISABLED)
            self.next_b.configure(state = ACTIVE)

        else: 
            # else both should be in active mode 
            self.previous_b.configure(state = ACTIVE)
            self.next_b.configure(state = ACTIVE)
    
    def backward_10sec(self,e:Event):
        
        current_pos = pygame.mixer_music.get_pos()+self.value_seeked
        try:
            if current_pos >= 10000 and self.is_palying == True:
                # if only the postion of the song is greater then 10 sec or 10000 mill secs
                # and the song is play mode
                current_pos -= 10000
                self.is_seek = True
                pygame.mixer_music.set_pos(current_pos)
                self.set_slider(current_pos)
                self.update_left_time()
            elif current_pos >= 10000 and self.is_pause == True:
                # if only the postion of the song is greater then 10 sec
                # and the song is pause mode
                paused = True # in the below functions is_pause is going to change that's why we storeing the value
                current_pos -=10000
                self.is_seek = True

                pygame.mixer_music.set_volume(0) 
                # setting volume to 0 due some sound came while backwarding because it is in play mode while backwarding
                pygame.mixer_music.set_pos(current_pos)

                self.set_slider(current_pos)
                self.update_left_time()

                volume = self.volume_s.get()
                pygame.mixer_music.set_volume(volume/100) #pygame volume range 0,1

                if paused == True:
                    self.pause_function()

            else:
                # if the song postion is less than 10 sec before clicking on it it can't do anythnig
                pass
        except:
            # due to avoid some errors
            pass

    def go_to_previous_track(self):

        """ By defalut (or) before new song starts all these are False and None mode only """

        self.is_pause = False # setting the global is_pause to False 
        self.is_seek = False # setting the global is_seek to False      these two are False by default when the song starts
        self.is_repeating = False
        self.repeating_song_name = None

        song_index = self.songs_list.index(self.current_song) # returns the index of the current sond in songs list

        if song_index == 1: 
            # if the song index == 1 means when clicked on this it goes to zero index
            # we pre disabling the button after disable the the it goes to previous track
            self.previous_b.configure(state = DISABLED) # disables the previous track

        # changes the current song name
        self.current_song = self.songs_list[song_index-1] # reduce the song index -1 and add the song to current song

        if self.next_b.cget('state') == DISABLED and self.songs_list.index(self.current_song) != len(self.songs_list):
            """if the next buttons is disabled and the song index is != len of the song list the we activate the next button"""
            self.next_b.configure(state = ACTIVE) # activates the next button

        pygame.mixer_music.load(self.current_song) # loads the current song 

        self.left_time.configure(text="00:00:00") # cahange the text  to default 0
        self.song_s.set(0) # setting slider position 0
        self.play_function() # goes the play function
        self.update_right_time() # goes to update right time function
        self.update_song_info() # goes to update song info
        self.reapeating_info.configure(text="") # setting the repeating song text to ""

        try:
            # pygame.mixer.Sound(self.current_song).get_length() return song length in minutes only 
            m,s =divmod(pygame.mixer.Sound(self.current_song).get_length(),60) # gets full length of song it return in seconds
            total = m*60000+s*1000  # converts into milliseconds
            self.song_s.configure(to=total) # setting the max slider length = song length in milliseconds

        except:
            """some audio fomat get exceptions but woks because of that we using try and except block"""
            pass

        self.update_song_image()
        self.update_list_box_view()
    

    def play_function(self):

        self.value_seeked = 0
        ## 'icacls file(or)folder /remove adminname' # for removing permissions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        pygame.mixer_music.play() # playes the song
        self.is_palying = True # makes globlal is_playing to true
        self.is_pause = False #making global is_pause to False

        self.update_left_time() # updates left time lable
        self.play_b.configure(text="\u23F8") # changes the text to pause unicode
        self.play_b.configure(command = self.pause_function) # changing the command to pause function from play fuction
        self.update_song_image() # update image of song

        # changing the current song data in catch file
        self.config.set(section='DATA',option="current_song",value=str(self.current_song))
        with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
            self.config.write(fo)
        
        ## 'icacls file(or)folder /deny adminname:F'
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)


    def pause_function(self):

        pygame.mixer_music.pause()#puases songs

        self.is_palying = False # setting globall is_paying  to false
        self.is_pause = True #setting global is_pause = True to un_pause
        self.play_b.configure(text="\u25B6") # change the text to play unicode
        self.play_b.configure(command = self.unpause_function) # change the command to unpause function from pause function

    
    def unpause_function(self):

        if self.is_pause == True: # if only is pause == True

            pygame.mixer_music.unpause() # unpauses the songs countinues from stop 

            self.is_palying = True # setting global is_palying to True
            self.is_pause = False # setting global is_pause == False to pause
            self.play_b.configure(text="\u23F8") # change the text to pause unicode
            self.play_b.configure(command = self.pause_function) # change the command to puase_function agian from unpause_function
        
    
    def go_to_next_track(self):
        

        """ by defalut (or) before stating new song all these are False anf None mode only"""

        self.is_pause = False # setting global is_pause to False
        self.is_seek = False # setting global is_seek to False       by default the two are false when the song starts
        self.is_repeating = False
        self.repeating_song_name = None

        song_index = self.songs_list.index(self.current_song)# returns the current song index

        if song_index == len(self.songs_list)-2 :
            # don't eqate the song idex to len(song list)-1
            # because the index starts with 0 
            # but the len(song list) give the no of items in list thats why we use len(songs list -2)
            """ we are pre disabling the next button teh we go to the next song that means the last song """
            self.next_b.configure(state = DISABLED) # disbles the next song

        # changes the current song name
        self.current_song = self.songs_list[song_index+1] # adds the song index+1 and returns to current song

        if self.previous_b.cget('state') == DISABLED and self.songs_list.index(self.current_song) !=0:
            """if the previous button is disbled and current song index !=0 means  
               the song index >=1 that there is an song avilable"""
            self.previous_b.configure(state = ACTIVE) # activate the prevoius button

        pygame.mixer_music.load(self.current_song) # loads the current song

        self.left_time.configure(text="00:00:00") # change the text to default text
        self.song_s.set(0) # setting slider position 0
        self.play_function() # goes to play function
        self.update_right_time() # goes to update right time function
        self.update_song_info() # goes to update song info function
        self.reapeating_info.configure(text="") # setting the repeating song text to ""
        
        try:
            m,s =divmod(pygame.mixer.Sound(self.current_song).get_length(),60) # gets the entile song length in seconds
            total = m*60000+s*1000 # converts into milliseconds
            self.song_s.configure(to=total) # setting the max slider length = len of full song in milliseconds

        except:
            """some audio fomat get exceptions but woks because of that we using try and except block"""
            pass

        self.update_song_image()
        self.update_list_box_view()
    
    def forward_10sec(self,e:Event):
        try:
            current_pos = pygame.mixer_music.get_pos()+self.value_seeked
            h,m,s = str(self.right_time.cget('text')).split(':')
            total_time_in_milliseconds = (int(h)*3600+int(m)*60+int(s))*1000
            
            if current_pos <= (total_time_in_milliseconds - 12000) and self.is_palying == True:
                # if the remeaning time is > 12 sec or 120000 mill sec
                # and the song is in play mode
                current_pos +=10000
                self.is_seek = True
                pygame.mixer_music.set_pos(current_pos)
                self.set_slider(current_pos)
                self.update_left_time()
            elif current_pos <= (total_time_in_milliseconds - 12000) and self.is_pause == True:
                # if the remeaning time is > 12 sec or 120000 mill sec
                # and the song is in pause mode
                paused = True # in the below functions is_pause is going to change that's why we storeing the value
                current_pos +=10000
                self.is_seek = True

                pygame.mixer_music.set_volume(0) 
                # sets the volume to 0 because due to when forwarding the sound will come 
                pygame.mixer_music.set_pos(current_pos)
                self.set_slider(current_pos)
                self.update_left_time()
                self.pause_function() # pauses the playing song because the song is in pause mode

                volume = self.volume_s.get()
                pygame.mixer_music.set_volume(volume/100) # again sets the volume to back
                # pygame volume range min(0),max(1)

                if paused == True:
                    self.pause_function()
            else:
                # if the remaining time is less than 12 sec it doesn't do any thing
                pass
        except:
            #purpose  # when starting application the song will not play when we click ctrl+right it raises error
            pass

    def repeat_song(self): 

        # if the song is in play mode and the is_repeating is not is not True
        # the only it going to set the current song to repeate mode
        if self.is_palying == True and self.is_repeating == False:

            self.is_repeating = True
            self.repeating_song_name = self.current_song
            self.reapeating_info.configure(text="Repeating song") # diaplyes the repeating song in display

        else:
            # canceling the  repeating song
            self.is_repeating = False
            self.repeating_song_name = None
            self.reapeating_info.configure(text="") # replacing the repeatinf song text to ""
    
    def volume_muting(self):

        if self.is_muted == True:
            self.is_muted = False
            value = self.volume_s.get() # returns volume of the slider 
            pygame.mixer_music.set_volume(value/100) # sets the volume of the pygame
            # pygame volume range 0,1
            self.volume_frame.configure(text=f'Volume {int(value)}%')

        elif self.is_muted == False:
            self.is_muted = True
            pygame.mixer_music.set_volume(0)
            self.volume_frame.configure(text='🔇 MUTED 🔇')

    

    def update_volume_bar(self,value):
        ## 'icacls file(or)folder /remove adminname' # for removing permisions
        command = f'icacls {self.main_path} /remove {self.admin_name}'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

        if self.current_song != None:
            # if only pygame is initilsed if current song != none means pygame is intilised
            if self.is_volume_limited == False or (self.is_volume_limited == True and value<=self.volume_limit_value):
                # if the volume limited is true then we need to check the value of volume
                if self.is_muted == False:
                    # if the app is not muted
                    pygame.mixer_music.set_volume(value/100) # setting volume to app
                    self.volume_frame.configure(text=f'Volume {int(value)}%') # setting selected volume in frame

                self.volume_s.set(value) # for keyboard input only

                if value > self.volume_limit_value:
                    # if volume is greater than limit value the progress bar color changes to red
                    self.volume_s.configure(progress_color = "#f7020f")
                
                else:
                    # sets to default green color
                    self.volume_s.configure(progress_color = '#3cc920')
                
                self.config.set(section="DATA",option="volume",value=str(int(value)))

                # changing the volume data in catch file
                with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
                    self.config.write(fo)

            else:
                present_volume_value = int(self.config.get(section='DATA',option='volume'))
                self.volume_s.set(present_volume_value)

                icons_path = os.path.join(self.main_path,'icons and photos')
                # sends the notification on desktop
                notify = Notification(app_id="Music Player",title="Warning",msg="Turn OFF Volume Limit",
                                      icon=os.path.join(icons_path,"icon.ico"))
                notify.set_audio(sound=audio.SMS,loop=False)
                notify.show()
                


        ## 'icacls file(or)folder /deny adminname:F'
        command = f'icacls {self.main_path} /deny {self.admin_name}:F'
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    

    """ ********************************* Checking user catch file from system *****************"""
    def recursive(self,path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, path)

    def checking_user_preferences(self):
        "C:/Users/adminname/AppData/Local"
        self.main_path = os.path.join(self.post_admin_path,'music_player')
        
        try:
            if os.path.exists(self.main_path):
                # 'icacls file(or)foldername /remove adminname'
                command = f'icacls {self.main_path} /remove {self.admin_name}'
                subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

                icons_path = os.path.join(self.main_path,'icons and photos')
                self.root.iconbitmap(os.path.join(icons_path,"icon.ico"))
                
                # reading the catch file data
                self.config.read(os.path.join(self.main_path,"user data.ini"),encoding='utf-8')
                
                # gets the songs_path data in catch file
                songs_path = self.config.get(section="DATA",option="songs_path").split(",")
                songs_path_list = songs_path[0:len(songs_path)-1]
                
                # reading the gif image 
                info = Image.open(os.path.join(icons_path,"gif image.gif"))
                no = info.n_frames
                self.gif_images_list = []
                for i in range(0,no):
                    if i not in [8,16,17,18,19,23,24,25,26,45,46,47]: # these are the not perfect images indexs removing those and adding remaing
                        self.gif_images_list.append(PhotoImage(file=os.path.join(icons_path,"gif image.gif"),format=f'gif -index {i}'))
            
                for i in songs_path_list: # if the song folder is deleted after then we need to delete the folder from list
                    if not os.path.exists(i):
                        songs_path_list.remove(i)
                
                my_str2 = ",".join(songs_path_list) # update the info in cathc file
                self.config.set(section="DATA",option="songs_path",value=my_str2 + ",")
                with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo:
                    self.config.write(fo)

                flag = 0
                for i in songs_path_list:
                    flag = 1
                    for j in os.listdir(i):
                        if os.path.splitext(j)[-1].lower().strip() in (".mp3"):
                            try:
                                audio = MP3(os.path.join(i,j))
                                """ if the file is not able to play raises error"""
                                if audio:
                                    self.songs_list.append(os.path.join(i,j))   
                                    flag = 2
                            except:
                                pass
                current_song = os.path.normpath(self.config.get(section="DATA",option="current_song"))
                volume_value = int(self.config.get(section='DATA',option='volume'))

                if os.path.exists(current_song): # if only song exists in system

                    self.update_info_related_to_song(current_song)

                    last_pos = int(self.config.get(section="DATA",option='last_pos'))
                    pygame.mixer_music.set_volume(0)
                    self.set_slider(last_pos)
                    self.pause_function()
                    volume_value = int(self.config.get(section='DATA',option='volume'))
                    self.volume_s.set(volume_value)
                    pygame.mixer_music.set_volume(volume_value/100)

                    self.volume_frame.configure(text=f'Volume {int(volume_value)}%')

                elif flag == 2:# if song gets deleted after playing but the folder exists and the folder have atleast one song

                    self.update_info_related_to_song()

                    volume_value = int(self.config.get(section='DATA',option='volume'))
                    self.volume_s.set(volume_value)

                    pygame.mixer_music.set_volume(volume_value/100)

                    self.volume_frame.configure(text=f'Volume {int(volume_value)}%')

                self.volume_limit_value = int(self.config.get(section="DATA",option="volume_limit_value"))

                if volume_value>self.volume_limit_value:
                    self.is_volume_limited == True
                    # if the volume is greater than limit volume preset the volume to limit value
                    self.volume_s.set(self.volume_limit_value)
                    self.volume_frame.configure(text=f'Volume {self.volume_limit_value}%')

                    pygame.mixer_music.set_volume(self.volume_limit_value/100)

                    self.config.set(section="DATA",option='volume',value=str(self.volume_limit_value))
                    # changing the volume data in catch file
                    with open(os.path.join(self.main_path,'user data.ini'),'w',encoding='utf-8') as fo:
                        self.config.write(fo)


                backgroung_value = self.config.get(section="DATA",option='background_listner')

                if backgroung_value == "True":
                    self.string_var.set(value="ON")
                    self.all_bindings()
                    # first we go to all tkinter bindings beacause all conditions are not in background active listeners
                    # In backgroud only we use space bar ,r ,m ,s buttons only if you don't go only those buttons will work 
                    # because in all_unbindings() these are not those only present remaing will not there 
                    # But if first go to all bindings all will bind to tkinter then only the background active listeners are unbind
                    self.all_unbindings()

                static_dynamic = self.config.get(section='DATA',option="background")

                if "static" in static_dynamic:
                    color = self.config.get(section="DATA",option="static_color")
                    self.main_frame.configure(bg=color)
                    self.song_image.configure(bg=color)

                elif "dynamic" in static_dynamic:
                    self.is_static = False
                    self.update_song_background()

                self.font_name = self.config.get(section="DATA",option="font_name")
                self.string_var2.set(value=self.font_name)
                self.change_font()

                ## icacls file(or)folder name /deny adminname:F # for blocking permisions
                command = f'icacls {self.main_path} /deny {self.admin_name}:F'
                subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

            else:
                # this is for first time application openes

                # icon_url = "https://cdn0.iconfinder.com/data/icons/internet-2020/1080/Applemusicandroid-512.png"
                # icon_data = requests.get(icon_url).content

                # gif_url =  "https://i.gifer.com/LBXB.gif"
                # gif_data = requests.get(gif_url).content

                with open(file = self.recursive("logo image.png"),mode = 'rb') as fo:
                    icon_data = fo.read()
                with open(file = self.recursive("gif image.gif"),mode = 'rb') as fo:
                    gif_data = fo.read()
                with open(file = self.recursive("help file.txt"),mode='r') as fo:
                    text_data = fo.read()


                os.makedirs(self.main_path)
                os.makedirs(os.path.join(self.main_path,'icons and photos'))

                icons_path = os.path.join(self.main_path,'icons and photos')

                with open (os.path.join(icons_path,"image.png"),'wb') as fo:
                    fo.write(icon_data)
                Image.open(os.path.join(icons_path,"image.png")).save(os.path.join(icons_path,"icon.ico"),format='ICO')

                with open(os.path.join(icons_path,"gif image.gif"),"wb") as fo:
                    fo.write(gif_data)
                
                info = Image.open(os.path.join(icons_path,"gif image.gif"))
                no = info.n_frames
                self.gif_images_list = []
                for i in range(0,no):
                    if i not in [8,16,17,18,19,23,24,25,26,45,46,47]: # these are the not perfect images indexs removing those and adding remaing
                        self.gif_images_list.append(PhotoImage(file=os.path.join(icons_path,"gif image.gif"),format=f'gif -index {i}'))

                with open(os.path.join(self.main_path,"help file.txt"),'w') as fo:
                    fo.write(text_data)

                self.config ["DATA"] = {"songs_path":[],"current_song":"","background":"static","static_color":"#000000",
                                        "background_listner":False,"volume":70,"last_pos":0,"font_name":"MV Boli",
                                        "volume_limit_value":70}
                
                with open(os.path.join(self.main_path,"user data.ini"),'w') as fo:
                    self.config.write(fo)
                    
                self.root.iconbitmap(os.path.join(icons_path,"icon.ico"))

                audio = self.recursive("Ye Mera Jahan.mp3") # default song
                shutil.copy2(src=audio,dst=self.main_path)
                self.songs_list.append(os.path.join(self.main_path,r"Ye Mera Jahan.mp3"))
                self.current_song = None
                self.update_info_related_to_song()  

                self.config.set(section="DATA",option="songs_path",value=self.main_path+",") # setting to the catch file
                with open(os.path.join(self.main_path,"user data.ini"),'w',encoding='utf-8') as fo: # make sue thst encoding = 'utf-8' for to add paths to catch file
                    self.config.write(fo) # writing to catch file

                # set permisions to denied
                # icacls file(or)folder name /deny adminname:F # for blocking permissions
                command = f'icacls {self.main_path} /deny {self.admin_name}:F'
                subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

                self.__del__()

            if self.background_listen == True:
                self.t1 = threading.Thread(target=self.background_listener)
                self.t1.start()
            else:
                self.all_bindings() 

        except Exception as e:
            # incase of any error from the coumpter click on reset all button on settings
            print(e)
            Label(self.main_frame,text="Some Error While Downloading\n Check Internet\n",
                  font=("TimesNewRoman",45),width=30,fg='red',bg="#000000",anchor='center').place(x=0,y=100)
            Label(self.main_frame,text="Click on\nSettings -> Reset all\n",
                  font=("TimesNewRoman",45),width=30,fg='red',bg="#000000",anchor='center').place(x=0,y=350)
            Label(self.main_frame,text="reset all data To work the player again",
                  font=("TimesNewRoman",45),width=30,fg='red',bg="#000000",anchor='center').place(x=0,y=500)
            pass
                
    def helper(self):
        with open(os.path.join(self.main_path,"help file.txt"),'r') as fo:
            text = fo.read()

        output_folder = os.path.join(self.pre_admin_path,"Downloads")
        with open(os.path.join(output_folder,"Help file.txt"),'w') as fo:
            fo.write(text)
        
        icons_path = os.path.join(self.main_path,'icons and photos')
        # sends the notification on desktop
        notify = Notification(app_id="Music Player",title="Help File",msg="Downloaded to this PC",
                                icon=os.path.join(icons_path,"icon.ico"))
        notify.add_actions(label="OPEN",launch=os.path.join(output_folder,"Help file.txt"))
        notify.add_actions(label="Cancel",launch="")
        notify.set_audio(sound=audio.Mail,loop=False)
        notify.show()
    

if __name__ == "__main__":
    MUSIC_PLAYER()
