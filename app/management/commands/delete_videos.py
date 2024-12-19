from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from app.models import RunScript, VideosData
from django.utils import timezone  
from datetime import datetime, timedelta
import os

class Command(BaseCommand):
    
    def delete_videos_file(self, video_obj) :
        
        video_obj.video.delete()
        
        return 
    
    
    
    def handle(self, *args, **options):

        
        
        current_datetime = timezone.now()
        all_videos = VideosData.objects.all()
        for videos in all_videos : 
            if not videos.deleted_or_not :
                if videos.created_at + timedelta(days=videos.configuration.delete_old_days) < current_datetime :
                    videos.deleted_or_not = True 
                    videos.save()
                    videos.video.delete()
                    videos.image.delete()
                    
            
            if videos.deleted_or_not :
                videos.video.delete()
                videos.image.delete()
                
                
    # 10 */6 * * * cd /home/sajal/adult-webscraping && /home/sajal/adult-webscraping/env/bin/python manage.py tasks_commands >> /home/sajal/adult-webscraping/logs/cron.log 2>&1
    
    # 1 */6 * * * cd /home/sajal/adult-webscraping && /home/sajal/adult-webscraping/env/bin/python manage.py  delete_videos >> /home/sajal/adult-webscraping/logs/delete_videos.log 2>&1