# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 18:20:01 2021

@author: jayes
"""


from PIL import Image, ImageTk
import tkinter as tk
import cv2
#import os
#import numpy as np
from keras.models import model_from_json
import operator
#import time
import sys, os
#import matplotlib.pyplot as plt
from string import ascii_uppercase
from win32com.client import Dispatch
from tkinter import filedialog
from tkinter import messagebox
import textwrap

class Application:
    
    
    def __init__(self):
        self.directory='model'
	
      
        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.current_image2 = None
        
        self.json_file = open("model-bw.json", "r")
        self.model_json = self.json_file.read()
        self.json_file.close()
        self.loaded_model = model_from_json(self.model_json)
        self.loaded_model.load_weights("model-bw.h5")

        self.json_file_dru = open("model-bw_dru.json" , "r")
        self.model_json_dru = self.json_file_dru.read()
        self.json_file_dru.close()
        self.loaded_model_dru = model_from_json(self.model_json_dru)
        self.loaded_model_dru.load_weights("model-bw_dru.h5")

        self.json_file_tkdi = open("model-bw_tkdi.json" , "r")
        self.model_json_tkdi = self.json_file_tkdi.read()
        self.json_file_tkdi.close()
        self.loaded_model_tkdi = model_from_json(self.model_json_tkdi)
        self.loaded_model_tkdi.load_weights("model-bw_tkdi.h5")

        self.json_file_smn = open("model-bw_smn.json" , "r")
        self.model_json_smn = self.json_file_smn.read()
        self.json_file_smn.close()
        self.loaded_model_smn = model_from_json(self.model_json_smn)
        self.loaded_model_smn.load_weights("model-bw_smn.h5")
        
        self.ct = {}
        self.ct['blank'] = 0
        self.blank_flag = 0
        for i in ascii_uppercase:
          self.ct[i] = 0
        print("Loaded model from disk")
        
        '''Initialize Main Screen'''
        self.initialieGUI()
        
        
        
    '''Audio Output'''
    def speak(self,str):
            speak = Dispatch(("SAPI.SpVoice"))
            speak.Speak(str)
            
    '''Video Loop'''
    def video_loop(self):
        # def speak(str):
        #     speak = Dispatch(("SAPI.SpVoice"))
        #     speak.Speak(str)
        ok, frame = self.vs.read()
        if ok:
            cv2image = cv2.flip(frame, 1)
            x1 = int(0.5*frame.shape[1])
            y1 = 10
            x2 = frame.shape[1]-10
            y2 = int(0.5*frame.shape[1])
            cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
            cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
            self.current_image = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
            cv2image = cv2image[y1:y2, x1:x2]
            gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray,(5,5),2)
            th3 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
            ret, res = cv2.threshold(th3, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            self.predict(res)
            self.current_image2 = Image.fromarray(res)
            imgtk = ImageTk.PhotoImage(image=self.current_image2)
            self.panel2.imgtk = imgtk
            self.panel2.config(image=imgtk)
            self.panel3.config(text=self.current_symbol,font=("Courier",40))
            self.panel4.config(text=self.word,font=("Courier",35))
            self.panel5.config(text=self.str,font=("Courier",35))
            
        self.root.after(3, self.video_loop)
        
        
    '''Prediction Function'''
    def predict(self,test_image):
        test_image = cv2.resize(test_image, (128,128))
        result = self.loaded_model.predict(test_image.reshape(1, 128, 128, 1))
        result_dru = self.loaded_model_dru.predict(test_image.reshape(1 , 128 , 128 , 1))
        result_tkdi = self.loaded_model_tkdi.predict(test_image.reshape(1 , 128 , 128 , 1))
        result_smn = self.loaded_model_smn.predict(test_image.reshape(1 , 128 , 128 , 1))
        prediction={}
        prediction['blank'] = result[0][0]
        inde = 1
        for i in ascii_uppercase:
            prediction[i] = result[0][inde]
            inde += 1
        #LAYER 1
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        self.current_symbol = prediction[0][0]
        #LAYER 2
        if(self.current_symbol == 'D' or self.current_symbol == 'R' or self.current_symbol == 'U'):
        	prediction = {}
        	prediction['D'] = result_dru[0][0]
        	prediction['R'] = result_dru[0][1]
        	prediction['U'] = result_dru[0][2]
        	prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'D' or self.current_symbol == 'I' or self.current_symbol == 'K' or self.current_symbol == 'T'):
        	prediction = {}
        	prediction['D'] = result_tkdi[0][0]
        	prediction['I'] = result_tkdi[0][1]
        	prediction['K'] = result_tkdi[0][2]
        	prediction['T'] = result_tkdi[0][3]
        	prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        	self.current_symbol = prediction[0][0]

        if(self.current_symbol == 'M' or self.current_symbol == 'N' or self.current_symbol == 'S'):
        	prediction1 = {}
        	prediction1['M'] = result_smn[0][0]
        	prediction1['N'] = result_smn[0][1]
        	prediction1['S'] = result_smn[0][2]
        	prediction1 = sorted(prediction1.items(), key=operator.itemgetter(1), reverse=True)
        	if(prediction1[0][0] == 'S'):
        		self.current_symbol = prediction1[0][0]
        	else:
        		self.current_symbol = prediction[0][0]
        if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0
        self.ct[self.current_symbol] += 1
        if(self.ct[self.current_symbol] > 60):
            for i in ascii_uppercase:
                if i == self.current_symbol:
                    continue
                tmp = self.ct[self.current_symbol] - self.ct[i]
                if tmp < 0:
                    tmp *= -1
                if tmp <= 20:
                    self.ct['blank'] = 0
                    for i in ascii_uppercase:
                        self.ct[i] = 0
                    return
            self.ct['blank'] = 0
            for i in ascii_uppercase:
                self.ct[i] = 0
            if self.current_symbol == 'blank':
                if self.blank_flag == 0:
                    self.blank_flag = 1
                    if len(self.str) > 0:
                        self.str += " "
                    self.str += self.word
                   # st=self.str
                    self.speak(self.word)
                    self.savestr = ''
                    self.savestr += self.str
                    #self.speak(self.savestr)
                    self.word = ""
            else:
                if(len(self.str) > 20):
                    self.savestr += self.str
                    self.str = ""
                self.blank_flag = 0
                self.word += self.current_symbol
  
    
  
    
  
    ''' Word to sentance boutton'''            

    def append_word_sentance(self):
         print( "Word to sentance boutton")
         self.current_symbol = 'blank'
         if(self.current_symbol == 'blank'):
            for i in ascii_uppercase:
                self.ct[i] = 0
            self.ct['blank'] = 0
            for i in ascii_uppercase:
                self.ct[i] = 0
            if self.current_symbol == 'blank':
                if self.blank_flag == 0:
                    self.blank_flag = 1
                    if len(self.str) > 0:
                        self.str += " "
                    self.str += self.word
                   # st=self.str
                    self.speak(self.word)
                    #self.speak(self.savestr)
                    self.word = ""
            else:
                if(len(self.str) > 20):
                    self.append_sentance()
                    # self.savestr += self.str
                    # self.str = ""
                self.blank_flag = 0
                self.word += self.current_symbol
       # pass
   
    
   
    
   
    
    '''Append sentance to conversation boutton'''
   
    def append_sentance(self):
        print( "Append sentance to conversation boutton")
        # self.savestr += "\n"
        self.str1 = "qweweq"
        self.str12 = "vccx"
        self.str13 = "jgh"
        # x = len(self.savestr+self.str)
        #z = len(self.savestr)
        # if(z != 0):
        #     if(x > self.wraped_str ):    
        #         self.savestr += "\n"
        #         self.savestr += self.str1
        #         self.wraped_str += 20
        #         self.str = ""
        #     else:
        #         self.savestr += " "
        #         self.savestr += self.str12
        #         self.str = ""
        # else:
        #     self.savestr += self.str13
        #     self.str = ""
        # if(z != 0):
        #     self.savestr += self.str1
        #     self.savestr += " "
        #     self.str = ""
        # else:
        #     self.savestr += self.str12
        #     self.savestr += " "
        #     self.str = ""
        # self.savestr += self.str1
        print( "Save sentance to paragraph")
        test_str1 = self.str
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Sentance is empty")
        else : 
            print ("No")  
            print(self.str)
            self.savestr += self.str
            self.savestr += " "
            self.str = ""
        # self.wraped_str = textwrap.fill(self.savestr,100)
        # print(x)
        # print(self.y)
        print(self.savestr)
        
        
        
        
        '''Append Opened file to conversation'''
    
    def append_text_data(self):
        print( "Append Opened file to conversation")
        self.text_data += self.opstr
        test_str1 = self.text_data
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "File is empty")
        else : 
            print ("No")  
            print(self.text_data)
            self.savestr += "\n"
            self.savestr += self.text_data
            self.savestr += " "
        # self.wraped_str = textwrap.fill(self.savestr,100)
        print(self.savestr)
        
        
        
        
        
    '''Listen On Screen sentance '''
    
    def listen_sentance(self):
        print( "Listen On Screen sentance")
        test_str1 = self.str
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Sentance is empty")
        else : 
            print ("No")  
            print(self.str)
            self.speak(self.str)
            
            
            
        
    '''Listen Saved Paragraph'''
    
    def listen_Conversation(self):
        print( "Listen Saved Paragraph")
        test_str1 = self.savestr
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Nothing is saved message")
        else : 
            print ("No")  
            print(self.savestr)
            self.speak(self.savestr)
    
    
    
    
    
    '''Listen Paragraph from Opened File'''
    
    def listen_Opened_File(self):
        print( "Listen Saved Paragraph")
        test_str1 = self.opstr
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Nothing is saved message")
        else : 
            print ("No")  
            print(self.savestr)
            self.speak(self.opstr)
            
            
            
            
            
    '''Remove Sentance'''
    
    def clear_sentance(self):
        print( "Remove Sentance")
        test_str1 = self.str
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Sentance is blank")
        else : 
            print ("No")  
            print(self.str)
            self.str = ""
    
    
    
    '''Remove Word'''
    
    def clear_word(self):
        print( "Remove Word")
        test_str1 = self.word
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Word Field is blank")
        else : 
            print ("No")  
            print(self.word)
            self.word = ""
    
    
    '''Remove Paragraph'''
    
    def clear_conv(self):
        print( "Remove Paragraph")
        test_str1 = self.savestr
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Nothing in Conversasion ")
        else : 
            print ("No")  
            print(self.savestr)
            self.savestr = ""
            self.wraped_str =""
    
    
    '''Clear Open File data'''
    
    def close_win(self):
        self.opstr=""
        self.new_window_opFile.destroy()
    
    
    
    '''Clear Open File data'''
    
    def close_read_save_win(self):
        self.new_window.destroy()
    '''save saved Paragraph as file '''
    
    def saveFile(self):
        print( "save saved Paragraph as file")
        print(self.savestr)
        test_str1 = self.savestr
        if(not (test_str1 and test_str1.strip())): 
            print ("Yes") 
            messagebox.showwarning("Error", "Nothing in Conversasion ")
        else : 
            print ("No")  
            f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
            if f is None:
                return
            f.write(self.savestr)
            f.close()
            
    
    
    
    
    
    '''Open Previous file '''
    def openFile(self):
        try:
            filepath = filedialog.askopenfilename(
                                              title="Open file okay?",
                                              filetypes= (("text files","*.txt"),
                                              ("all files","*.*")))
            with open(filepath, 'r') as file:
                data = file.read().replace('\n', '')
            self.opstr += data
        except IOError:
            messagebox.showwarning("Error", "Please Select Proper file ")
        
        # print(self.opstr)
        else:
            self.new_window_opFile = tk.Toplevel()
            self.new_window_opFile.title("Gesture Vocolizer")
            self.new_window_opFile.iconbitmap(r'GV.ico')
            self.new_window_opFile.geometry("900x700") #(width x hight)
            
            self.lg1 = ImageTk.PhotoImage(Image.open("lg2.png"))
            self.LGI = tk.Label(self.new_window_opFile, image=self.lg1)
            self.LGI.place(x = 270,y = 10 )
            
            self.panel_opFile = tk.Label(self.new_window_opFile) # Sentence
            self.panel_opFile.place(x = 20,y=200)
            
            self.Title_opFile = tk.Label(self.new_window_opFile)
            self.Title_opFile.place(x = 10,y = 150)
            
            self.open_file_text = textwrap.fill(self.opstr,100)
            print(self.open_file_text)
            
            # print(self.opstr)
            self.Title_opFile.config(text ="Paragraph :",font=("Times",25,"bold"))
            self.panel_opFile.config(text=self.open_file_text,font=("Times",16))
            
            ''' save file Button '''
            self.save_btn=tk.Button(self.new_window_opFile,text =" Append " , command = self.append_text_data)
            self.save_btn.place(x = 300, y = 600)
            
            ''' Audio Button  '''
            self.listen_btn=tk.Button(self.new_window_opFile,text =" Listen " , command = self.listen_Opened_File)
            self.listen_btn.place(x = 400, y = 600)
            
            ''' clear Button  '''
            self.clear_btn=tk.Button(self.new_window_opFile,text =" Close " , command = self.close_win)
            self.clear_btn.place(x = 500, y = 600)
            
            file.close()
        
        
        
        
        
    ''' Read Saved Data '''    
        
    def saved_conv(self):
        # messagebox.showinfo("Title", self.savestr)
        #tk.Label(self.root, text = res).pack()
        self.new_window = tk.Toplevel()
        self.new_window.title("Gesture Vocolizer")
        self.new_window.iconbitmap(r'GV.ico')
        self.new_window.geometry("900x700") #(width x hight)
        
        self.lg1 = ImageTk.PhotoImage(Image.open("lg2.png"))
        self.LGI = tk.Label(self.new_window, image=self.lg1)
        self.LGI.place(x = 270,y = 10 )
        
        self.panel60 = tk.Label(self.new_window) # Sentence
        self.panel60.place(x = 15,y=250)
        
        self.T4 = tk.Label(self.new_window)
        self.T4.place(x = 10,y = 200)
        
        ''' save file Button '''
        self.save_btn=tk.Button(self.new_window,text =" Save As " , command = self.saveFile)
        self.save_btn.place(x = 300, y = 600)
        
        ''' Audio Button  '''
        self.listen_btn=tk.Button(self.new_window,text =" Listen " , command = self.listen_Conversation)
        self.listen_btn.place(x = 400, y = 600)
        
        ''' clear Button  '''
        self.clear_btn=tk.Button(self.new_window,text =" Close " , command = self.close_read_save_win)
        self.clear_btn.place(x = 500, y = 600)
        # self.st = "asdasdgfhgfghfgfhgfghg \n fhfhgfhghfhgfgfhgfhg"
        # self.st = self.savestr
        
        # self.saved_text_data = self.wraped_str
        self.saved_text_data = textwrap.fill(self.savestr,100)
        self.T4.config(text ="Paragraph :",font=("Times",25,"bold"))
        self.panel60.config(text=self.saved_text_data,font=("Times",16))
    
    
    
    
    
    
    def initialieGUI(self):
        self.root = tk.Tk()
        self.root.title("Gesture Vocolizer")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        # self.root.geometry("1300x1100")
        RWidth=self.root.winfo_screenwidth()
        RHeight=self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (RWidth, RHeight))#(width x hight)
        self.root.iconbitmap(r'GV.ico')
        
        self.panel = tk.Label(self.root)
        self.panel.place(x = 135, y = 27, width = 650, height = 550)
        
        self.panel2 = tk.Label(self.root) # initialize image panel
        self.panel2.place(x = 460, y = 75, width = 300, height = 300)
        
        self.T = tk.Label(self.root)
        self.T.place(x=200,y = 3)
        self.T.config(text = "Gesture Vocolizer",font=("courier",35,"bold"))
        
        self.panel3 = tk.Label(self.root) # Current SYmbol
        self.panel3.place(x = 400,y=560)
        
        self.T1 = tk.Label(self.root)
        self.T1.place(x = 10,y = 560)
        self.T1.config(text="Character :",font=("Courier",30,"bold"))
        
        self.panel4 = tk.Label(self.root) # Word
        self.panel4.place(x = 220,y=610)
        
        self.T2 = tk.Label(self.root)
        self.T2.place(x = 10,y = 610)
        self.T2.config(text ="Word :",font=("Courier",30,"bold"))
        
        self.panel5 = tk.Label(self.root) # Sentence
        self.panel5.place(x = 350,y=660)
        
        self.T3 = tk.Label(self.root)
        self.T3.place(x = 10,y = 660)
        self.T3.config(text ="Sentence :",font=("Courier",30,"bold"))
        
        ''' Speak Button '''
        self.photo1 = tk.PhotoImage(file="testbtn4.png")
        self.b1=tk.Button(text ="Save", image=self.photo1, command = self.listen_sentance, border=0)
        self.b1.place(x = 900, y = 75)
        
        
        ''' Word To Sentence Button '''
        self.b2=tk.Button(text ="append_word_sentance" , command = self.append_word_sentance)
        self.b2.place(x = 1000, y = 75)
        
        ''' save file Button '''
        self.b3=tk.Button(text =" Save As " , command = self.saveFile)
        self.b3.place(x = 900, y = 120)
        
        ''' Read all Sentence Button '''
        self.b4=tk.Button(text =" ReadSaved " , command = self.saved_conv)
        self.b4.place(x = 1000, y = 120 )
        
        ''' listen Conversation  '''
        self.b5=tk.Button(text =" ListenSaved " , command = self.listen_Conversation)
        self.b5.place(x = 900, y = 160 )
        
        ''' save all Sentence Button '''
        #'''Append sentance to conversation boutton'''
        self.b4=tk.Button(text =" append_sentance " , command = self.append_sentance)
        self.b4.place(x = 1000, y = 160 )
        
        ''' clear sentance  '''
        self.b5=tk.Button(text =" clear sentance " , command = self.clear_sentance)
        self.b5.place(x = 900, y = 200 )
        
        ''' clear word  '''
        self.b4=tk.Button(text =" clear word " , command = self.clear_word )
        self.b4.place(x = 1000, y = 200 )
        
        ''' clear all '''
        self.b5=tk.Button(text =" clear all " , command = self.clear_conv)
        self.b5.place(x = 900, y = 240 )
        ''' Open File '''
        self.b7=tk.Button(text =" Open File " , command = self.openFile)
        self.b7.place(x = 1000, y = 240 )
        
        # self.b1.pack()
        self.saved_text_data=""
        self.open_file_text = ""
        self.text_data = ""
        self.wraped_str = ""
        self.opstr=""
        self.str=""
        self.word=""
        self.savestr=""
        self.current_symbol="Empty"
        self.photo="Empty"
        self.video_loop()
        
        
        
        
    def destructor(self):
        print("Closing Application...")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()
    
    
    
    
    def destructor1(self):
        print("Closing Application...")
        self.root1.destroy()
        
        
        
        
        
        
print("Starting Application...")
pba = Application()
pba.root.mainloop()
