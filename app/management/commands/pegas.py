from django.core.management.base import BaseCommand, CommandError
from Scrape.settings import BASE_DIR
from django.core.files.base import ContentFile
from app.models import videos_collection, configuration, VideosData
import requests, os, time
from driver.Bots.pegas import Bot
from utils.mail import SendAnEmail

class Command(BaseCommand, Bot):
    help = "Closes the specified poll for voting"
    def add_arguments(self, parser):
        parser.add_argument("--only_login", default=False, type=bool)

    def make_init(self):
        self.driver_type = "normal"     
        self.base_path = os.getcwd()
        
        self.download_path = os.path.join(os.getcwd(),'downloads')
        [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload') or i.endswith('.mp4') ]
        
        # Configurations
        self.pegas = configuration.objects.get(website_name='pegas')
        self.pegas_category_path = self.create_or_check_path('pegas_category_videos')

        self.csv_folder_path = self.create_or_check_path('csv',main=True)
        self.cookies_path = self.create_or_check_path('cookies',main=True)
        self.csv_name = "pegas.csv"
        self.csv_path = os.path.join(self.csv_folder_path,f'{self.csv_name}')
        
    def handle(self, *args, **options):
        VideosData.delete_older_videos()
        self.make_init()
        self.driver = self.get_driver()
        if not self.driver :
            SendAnEmail('Could not open up the driver')
            return
        
        only_login = options["only_login"]
        if only_login :
            print('only login')
            if self.pegas_login():
                self.pegas.lastime_able_to_login_or_not = True
                self.pegas.save()
            else :
                self.pegas.lastime_able_to_login_or_not = False
                self.pegas.save()
        else :
            print('Not only login')
            
        if self.pegas_login():
            self.pegas.lastime_able_to_login_or_not = True
            self.pegas.save()
            self.pegas_download_videos()
        else :
            self.pegas.lastime_able_to_login_or_not = False
            self.pegas.save()

        # self.download_and_save_file("http://208.122.217.49:8000/csv/vip4k_debt4k_videos_details.csv")