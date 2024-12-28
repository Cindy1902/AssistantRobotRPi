from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
from plyer import notification
import pytz

class GoogleCalendarScheduler:
    def __init__(self):
        # Nếu chỉnh sửa scope, xóa file token.pickle
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.creds = None
        self.service = None
        self.timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        self.initialize_credentials()

    def initialize_credentials(self):
        """Khởi tạo và xác thực với Google Calendar API"""
        # Token đã lưu
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # Nếu không có credentials hoặc không hợp lệ
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Lưu credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def add_appointment(self, title, date_time, description="", location=""):
        """
        Thêm cuộc hẹn mới vào Google Calendar
        
        Args:
            title (str): Tiêu đề cuộc hẹn
            date_time (datetime): Thời gian cuộc hẹn
            description (str): Mô tả cuộc hẹn
            location (str): Địa điểm cuộc hẹn
        """
        try:
            # Chuyển đổi thời gian địa phương sang UTC
            local_time = self.timezone.localize(date_time)
            start_time = local_time.isoformat()
            end_time = (local_time + timedelta(hours=1)).isoformat()

            # Tạo thông báo trước 1 ngày và 1 giờ
            reminders = {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # 1 ngày
                    {'method': 'popup', 'minutes': 60}        # 1 giờ
                ]
            }

            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'Asia/Ho_Chi_Minh',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'Asia/Ho_Chi_Minh',
                },
                'reminders': reminders
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f'Đã tạo sự kiện: {event.get("htmlLink")}')
            return True
            
        except Exception as e:
            print(f'Lỗi khi tạo sự kiện: {e}')
            return False

    def get_upcoming_events(self, max_results=10):
        """
        Lấy danh sách các sự kiện sắp tới
        
        Args:
            max_results (int): Số lượng sự kiện tối đa cần lấy
        
        Returns:
            list: Danh sách các sự kiện
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except Exception as e:
            print(f'Lỗi khi lấy danh sách sự kiện: {e}')
            return []

    def delete_event(self, event_id):
        """
        Xóa một sự kiện
        
        Args:
            event_id (str): ID của sự kiện cần xóa
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f'Đã xóa sự kiện: {event_id}')
            return True
        except Exception as e:
            print(f'Lỗi khi xóa sự kiện: {e}')
            return False

    def update_event(self, event_id, title=None, date_time=None, description=None, location=None):
        """
        Cập nhật thông tin sự kiện
        
        Args:
            event_id (str): ID của sự kiện cần cập nhật
            title (str): Tiêu đề mới (tùy chọn)
            date_time (datetime): Thời gian mới (tùy chọn)
            description (str): Mô tả mới (tùy chọn)
            location (str): Địa điểm mới (tùy chọn)
        """
        try:
            # Lấy thông tin sự kiện hiện tại
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Cập nhật các thông tin mới
            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            if date_time:
                local_time = self.timezone.localize(date_time)
                event['start']['dateTime'] = local_time.isoformat()
                event['end']['dateTime'] = (local_time + timedelta(hours=1)).isoformat()

            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            print(f'Đã cập nhật sự kiện: {updated_event.get("htmlLink")}')
            return True
            
        except Exception as e:
            print(f'Lỗi khi cập nhật sự kiện: {e}')
            return False

def show_notification(title, message):
    """Hiển thị thông báo desktop"""
    notification.notify(
        title=title,
        message=message,
        app_icon=None,
        timeout=10,
    )

# def main():
#     """Test các chức năng của scheduler"""
#     scheduler = GoogleCalendarScheduler()

#     # Thêm một cuộc hẹn mới
#     appointment_time = datetime.now() + timedelta(days=1)
#     scheduler.add_appointment(
#         "Cuộc họp test",
#         appointment_time,
#         "Cuộc họp test Google Calendar API",
#         "Phòng họp A"
#     )
    
#     # Lấy danh sách sự kiện sắp tới
#     events = scheduler.get_upcoming_events(5)
#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         print(f"{event['summary']} ({start})")
