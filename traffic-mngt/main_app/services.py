import datetime
from main_app.repository import MongoRepository
from django.conf import settings


mongo_repo = MongoRepository(
    host=settings.DB_MONGO_HOST,
    port=settings.DB_MONGO_PORT,
    username=settings.DB_MONGO_USER,
    password=settings.DB_MONGO_PASSWORD,
    database=settings.DB_MONGO_DB
)

class MongoService:
    def __init__(self):
        self.repo = mongo_repo
    
    def get_latest_alerts(self, limit_days=5):
        today = datetime.datetime.now().date()
        alerts = []

        for i in range(limit_days):
            day = today - datetime.timedelta(days=i)
            collection_name = day.strftime('%Y%m%d')

            try:
                day_alerts = self.repo.find_documents(collection_name)
                for alert in day_alerts:
                    alert['_id'] = str(alert['_id'])  # convert ObjectId to str
                alerts.extend(day_alerts)
            except Exception as e:
                continue

        # Sắp xếp giảm dần theo detect_at nếu có
        alerts.sort(key=lambda x: x.get("detect_at", 0), reverse=True)
        return alerts
    
    def save_alert(self, collection_name, message) -> bool:
        try:
            self.repo.insert_one(collection_name, message)            
            return True
        except Exception as e:
            return False