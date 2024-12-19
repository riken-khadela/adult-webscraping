from driver.get_driver import StartDriver
import json, random, os, time, requests, urllib, shutil
from utils.mail import SendAnEmail
from bs4 import BeautifulSoup
from app.models import cetegory, configuration, videos_collection, VideosData
from dateutil import parser
from datetime import datetime, timedelta
import pandas as pd

# selenium imports
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from anticaptchaofficial.imagecaptcha import *


class Bot(StartDriver):
    
    def login(self):
        
        
        solver = imagecaptcha()
        solver.set_verbose(1)
        solver.set_key("e49c2cc94651faab912d635baec6741f")
        solver.set_soft_id(0)
        url = self.driver.current_url
        print('Started Login process')
        for i in range(5):
            self.driver.refresh()
            
            try :
                if not self.find_element('Login form', "//input[@name='username']", timeout=4):
                    self.driver.refresh()
                    
                if not self.find_element('Login form', "//input[@name='username']", timeout=4):
                    if  self.find_element('Login proof', "//input[@placeholder='Search update']", timeout=4):
                        return True
                    else:
                        self.driver.refresh()
                
                if not self.find_element('Login form', "//input[@name='username']", timeout=4):
                    continue
                    
                self.input_text(self.Maturenl.username,'username', "//input[@name='username']")
                self.input_text(self.Maturenl.password,'password', "//input[@name='password']")
                
                img = self.find_element('links','imgAccountLoginCaptcha',By.ID)
                captcha = img.screenshot_as_png
                
                with open('captcha.png', 'wb') as file: 
                    file.write(captcha)
                    
                # this captcha.png has two words in the image and i need two seprate word to solve the captcha
                captcha_text = None
                captcha_text = solver.solve_and_return_solution('captcha.png')
                
                if not ' ' in captcha_text :
                    continue
                
                if captcha_text :
                    self.input_text(captcha_text,'captcha input', "//input[@name='captcha']")
                    self.click_element('login btn', "//input[@type='submit']")

                if  self.find_element('Login proof', "//input[@placeholder='Search update']", timeout=4):
                    return True
            except : 
                pass
        return False
    
    def download_videos(self):
        
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.Maturenl)]
        
        
        for category in self.Maturenl.category.all() :
            max_video_download_number = self.Maturenl.numbers_of_download_videos
            self.driver.get(category.link)
            
            downloadable_links = []
            if self.find_element('username', "//input[@name='username']") :
                if not self.login() :
                    breakpoint()
                    continue
            
            
            all_grid_items = self.driver.find_elements(By.XPATH, "//div[@class='grid-tile-update']") 
            for grid_items in all_grid_items :  
                grid_items_href = None
                grid_items_href = grid_items.find_element(By.TAG_NAME,'a')
                if grid_items_href :
                    grid_items_href = grid_items_href.get_attribute('href')
                    
                if not grid_items_href in df_url:
                    downloadable_links.append(grid_items_href)
                    
            if not downloadable_links :
                continue
            
            for download_link in downloadable_links :
                self.driver.get(download_link)    
                video_download_link = self.driver.find_elements(By.XPATH,"//a[contains(text(), 'HD')]")
                if not video_download_link:
                    continue
                
                video_download_link = random.choice(video_download_link)
                video_download_link.click()
                
                downloaded_file_name = self.wait_for_file_download()
                title = self.find_element("Title name",'h1',By.TAG_NAME)
                if title :
                    title =title.text
                else :
                    title = ""    
                    
                Likes_ele = self.find_element('Likes count', "/html/body/div[3]/div[2]/div/div[2]/button[1]/span[2]")
                if Likes_ele :
                    like = Likes_ele.text
                else :
                    like = 0
                    
                descriptions_ele = self.find_element('descriptions', "/html/body/div[3]/div[2]/div/div[1]")
                if descriptions_ele :
                    description = descriptions_ele.text
                else :
                    description = ""
                    
                if description:
                    Release_Date =description.split('•')[0].strip()
                else :
                    Release_Date = ""
                    
                pornstar_ele = self.find_element("Pornstarts", '/html/body/div[3]/div[2]/div')
                if pornstar_ele and description:
                    pornstars = pornstar_ele.text.split(description)[0].replace('\n','').strip()
                else :
                    pornstars= ""
                
                media_path = os.path.join(os.getcwd(),'media')
                video_media_path = os.path.join(media_path,'videos','Maturenl_category_videos',self.sanitize_title(category.category))
                image_media_path = os.path.join(media_path,'image','Maturenl_category_videos',self.sanitize_title(category.category))
                os.makedirs(video_media_path, exist_ok=True)
                os.makedirs(image_media_path, exist_ok=True)
                
                final_video_media_path = os.path.join(video_media_path,f'{self.sanitize_title(title)}.mp4')
                final_image_media_path = os.path.join(image_media_path,f'{self.sanitize_title(title)}.jpg')
                
                download_video_file = os.path.join(os.getcwd(),'downloads',downloaded_file_name)
                if os.path.exists(download_video_file) :
                    shutil.move(download_video_file,final_video_media_path)
                
                video_image_src = ""
                video_image = self.find_element('Video Image url', "/html/body/div[3]/div[1]/div/div[1]/a/img[1]") 
                if video_image:
                    video_image_src = video_image.get_attribute('src')
                
                if video_image_src:
                    response = requests.get(video_image_src)
                    with open(final_image_media_path, 'wb') as f: 
                        f.write(response.content)
                
                image_object_path = os.path.join('image','Maturenl_category_videos',self.sanitize_title(category.category),f'{self.sanitize_title(title)}.jpg')
                videos_object_path = os.path.join('videos','Maturenl_category_videos',self.sanitize_title(category.category),f'{self.sanitize_title(title)}.mp4')
                print("Image file : ",image_object_path)
                print("Video file : ",videos_object_path)
                
                if  os.path.exists(final_image_media_path) and os.path.exists(final_video_media_path) :
                    
                    videos_data_obj = VideosData.objects.create( 
                        video = videos_object_path,
                        image = image_object_path,
                        Username = self.Maturenl.username,
                        Likes = int(like) if like.isdigit() else 0,
                        Disclike = 0,
                        Url = self.driver.current_url,
                        Title = title,
                        Discription = description,
                        Release_Date = Release_Date,
                        Video_name = f'{title}.mp4',
                        Photo_name = f'{title}.jpg',
                        Pornstarts = pornstars,
                        configuration = self.Maturenl,
                        cetegory = category
                        )
                    max_video_download_number -= 1
                
                if 0 <= max_video_download_number :
                        break
    
        return False