# Don't forget to explain your code to the audience
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from bs4 import BeautifulSoup
import re
import pandas as pd
import mysql.connector
import time
import requests


service = Service(executable_path="chromedriver.exe")
#driver = webdriver.Chrome(Service=service) is not necessary, as selenium does it automatically
driver = webdriver.Chrome(service=service)

wait = WebDriverWait(driver,10)

e_store = []
record = []

my_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="restuarant_edin"
)
my_cusor = my_db.cursor()


class Restaurants():
    #stores the values from the google maps
    def __init__(self):
        self.name = None
        self.address = None
        self.rating = None
        self.website = None
        self.count = 0 
    
        self.price = None
        self.category = None
        self.wheelchair_acc = None
        self.img = None


    def open_browser(self):
        #To open the chrome web browser 
            
        driver.maximize_window()
        driver.get('https://www.google.com/maps')
        time.sleep(40)
        try:
            but =  wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Accept all']"))) # make sure to make your input into a single tuple 
            but.click()
            print("Cookie popup accepted")
        
        except Exception as e:
            print("Element not found", e)



    def search_term(self):
        add_term = driver.find_element(By.XPATH, "//input[@name='q']")
        ActionChains(driver)\
            .send_keys_to_element(add_term, "Restaurants in Edinburgh")\
            .key_down(Keys.RETURN)\
            .perform()
           
        
        time.sleep(4)

  

  
        
       

    def get_all(self):

        #looking for restaurant profile
        terms = driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")
        #This allows selenium to simulate user actions
        action =  ActionChains(driver)

        # I think this is the code for scrolling
        while len(terms) < 1000:
            
            length = len(terms)
            #scroll away from staring profile
            scroll_origin = ScrollOrigin.from_element(terms[length-1])
            action.scroll_from_origin(scroll_origin, 0, 1000).perform()
            #wait for 2 seconds
            time.sleep(2)
            terms = driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")

            #count --> self.count
            if len(terms) == length:
                self.count += 1
                if self.count > 20:
                    break
            else:
                self.count = 0
        # I believe this one is for information extraction
        for i in range(len(terms)):

            scroll_origin =  ScrollOrigin.from_element(terms[i])
            action.scroll_from_origin(scroll_origin, 0,100).perform()
            action.move_to_element(terms[i]).perform()
            terms[i].click()
            time.sleep(2)
            source = driver.page_source # This can give different html
            soup = BeautifulSoup(source, 'html.parser')
     
     
            try:
                div_find = soup.find_all('div', class_="XltNde tTVLSc") # Did returns a list of tags

                # parsing html elements to get the text version
                for divs in div_find:
                    self.name = divs.find("span", class_="a5H0ec").next_sibling
                    self.address = divs.find("div", class_="RcCsl")
                    self.rating = divs.find("div",class_="F7nice")
                    self.price = divs.find("span", class_="fjHK4").next_sibling
                    
                    
                    self.website = divs.find("a",class_="CsEnBe")
                    find_web = self.website['href']
                    self.category = divs.find("button",class_="DkEaL")
                    self.img = divs.find("img",decoding_="async")
                    get_img = self.img['src']
               
              
                    if divs.find("span",class_="wmQCje"):
                        self.wheelchair_acc = True
                    else:
                        self.wheelchair_acc = False

                    # tag to text
                    address_text = self.address.get_text(strip=True)
                    new_rating = self.rating.text.strip()
                    if new_rating[3]:
                       new_rating = new_rating[0:3]
                    
                    clean = re.sub(r'[\uE000-\uF8FF]', '', address_text)


                    if self.price:
                        pass
                  
                    new_name,new_clean,rating,new_price,new_web,new_cat,new_wheelchair = self.name.text.strip(),clean.strip(),new_rating,self.price.text.strip(),find_web,self.category.text.strip(),self.wheelchair_acc


                    if self.name:
                        add_db = "INSERT INTO restaurant(rest_ID ,name,addresss,rating,website,price_range,category, wheelchair_acc) VALUES('',%s,%s,%s,%s,%s,%s,%s)"
                        data = (new_name,new_clean,rating,new_web,new_price,new_cat,new_wheelchair)
                        my_cusor.execute(add_db,data)

                        my_db.commit()
                    print(my_cusor.rowcount, "record inserted")
                       
            

            except Exception as e:
                print("Failed:", e)
                continue



# main program
if __name__ == "__main__":
  
    get_details = Restaurants()
    get_details.open_browser()
    
    get_details.search_term()
  
    get_details.get_all()
