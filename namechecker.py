import os
from tabnanny import check
import requests
from requests.sessions import Session
import ctypes
from threading import Thread,local
from queue import Queue      
from colorama import Fore
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup

os.system('color')


print(" _   _                             _               _           ")
print("| \ | |                           | |             | | ")
print("|  \| | __ _ _ __ ___   ___    ___| |__   ___  ___| | ")
print("| . ` |/ _` | '_ ` _ \ / _ \  / __| '_ \ / _ \/ __| |/ / _ \ '__| ")
print("| |\  | (_| | | | | | |  __/ | (__| | | |  __/ (__|   <  __/ |  ")
print("|_| \_|\__,_|_| |_| |_|\___|  \___|_| |_|\___|\___|_|\_\___|_| \n")

url_list = []
total_words = 0
working_words = []

with open('testingwords.txt', 'r') as file:
    
    for line in file:

        for word in line.split():

            link = "https://mcnames.net/username/" + word + "/"
            url_list.append((link, word))      
            total_words += 1  

ctypes.windll.kernel32.SetConsoleTitleW(f"Minecraft name checker [0 | {total_words}]")

q = Queue(maxsize=0)            #Use a queue to store all URLs
for url in url_list:    
    q.put(url)
thread_local = local()           #The thread_local will hold a Session object

def get_session() -> Session:
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session() # Create a new Session if not exists
    return thread_local.session

def title_update():
    gang = 0
    for i in working_words:
        gang += 1
    ctypes.windll.kernel32.SetConsoleTitleW(f"Minecraft name checker [{gang} | {total_words}]")

def download_link() -> None:
    session = get_session()
    while True: 
        url = q.get() 
        with session.get(url[0]) as response:
            
            a_info = [] 
            isdate = 0
            delta = 0
            s = response.text

            soup = BeautifulSoup(response.text, features="html.parser")
            for node in soup.findAll('td'):
                a_info.append(''.join(node.findAll(text=True)))

            #print(a_info)

            while isdate == 0:
                targeted_date = 0
                counting = 0
                for items in a_info:
                    if items == url[1]:
                        targeted_date = counting - 1
                    counting += 1
                try:
                    date_format = "%Y-%m-%d  %H:%M:%S"
                    a = datetime.strptime(a_info[targeted_date], date_format)
                    isdate = 1
                except:
                    isdate = 2  
    
            if isdate == 1:
                
                now = datetime.now()
                d1 = now.strftime("%Y-%m-%d  %H:%M:%S")
                d2 = datetime.strptime(d1, date_format)

                checkdate = d2 - timedelta(days=37)
                
                if a > checkdate:
                    change = a + timedelta(days=37)
                    changedate = datetime.strptime(str(change), date_format)
                            
                    a = datetime.strptime(d1, date_format)
                    b = datetime.strptime(str(changedate), date_format)
                    delta = b - a
                    
    
            if "Username is available" in response.text:
                if delta != 0:
                    status = "Cooldown"
                    print(f"{Fore.YELLOW}{url[1]} : {status} : {delta}")
                    working_words.append(url[1])
                    title_update()
                    results =  open("cooldown.txt", "a")
                    results.write(f"{url[1]} : {status} : {delta}\n")
                    results.close()                
                else:
                    status = "Working"
                    print(f"{Fore.GREEN}{url[1]} : {status}")
                    working_words.append(url[1])
                    title_update()
                    results =  open("results.txt", "a")
                    results.write(f"{url[1]} : {status}\n")
                    results.close()
                
            if "Username is not available" in response.text:
                status = "Not working"
                print(f"{Fore.RED}{url[1]} : {status}")

        q.task_done()          # tell the queue, this url downloading work is done

def download_all(urls) -> None:
    thread_num = 20
    for i in range(thread_num):
        t_worker = Thread(target=download_link)
        t_worker.start()
    q.join()                   # main thread wait until all url finished downloading


download_all(url_list)  