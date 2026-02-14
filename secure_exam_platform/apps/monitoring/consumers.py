import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from apps.exams.models import ExamSession
from .models import SecurityEvent, ProctorSnapshot


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'session_{self.session_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        event = payload.get('type')
        data = payload.get('data', {})
        await self.handle_event(event, data)

    async def handle_event(self, event, data):
        session = await sync_to_async(ExamSession.objects.get)(id=self.session_id)
        session.last_activity = timezone.now()
        if event == 'heartbeat':
            session.webcam_active = data.get('webcam_active', True)
            session.fullscreen_status = data.get('fullscreen', True)
        elif event in {'fullscreen_exit', 'tab_change', 'focus_change', 'copy_attempt', 'paste_attempt', 'session_closed'}:
            session.violations_count += 1
            if event == 'tab_change':
                session.tab_switch_count += 1
        elif event in {'snapshot_upload', 'screen_upload'}:
            await sync_to_async(ProctorSnapshot.objects.create)(
                session=session,
                snapshot_type='webcam' if event == 'snapshot_upload' else 'screen',
                image=data.get('image', ''),
            )
        await sync_to_async(session.save)()
        await sync_to_async(SecurityEvent.objects.create)(
            session=session,
            event_type=event,
            severity=data.get('severity', 'medium'),
            metadata=data,
        )

        await self.channel_layer.group_send('admins', {'type': 'admin.broadcast', 'payload': {
            'session_id': session.id,
            'student': session.student.username,
            'event': event,
            'violations_count': session.violations_count,
            'fullscreen_status': session.fullscreen_status,
            'webcam_active': session.webcam_active,
            'timestamp': timezone.now().isoformat(),
        }})

    async def session_message(self, event):
        await self.send(text_data=json.dumps(event['payload']))


class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add('admins', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('admins', self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)
        target = payload.get('session_id')
        if target:
            await self.channel_layer.group_send(
                f'session_{target}',
                {'type': 'session.message', 'payload': {'type': 'admin_command', 'data': payload}}
            )

    async def admin_broadcast(self, event):
        await self.send(text_data=json.dumps(event['payload']))
