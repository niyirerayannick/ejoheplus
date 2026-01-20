from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings
from accounts.models import User
from .models import Message
import json
import os


@login_required
@require_http_methods(["GET"])
def get_chat_messages(request, user_id):
    """API endpoint to get messages for a chat conversation"""
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Get last message ID from request (for polling updates)
    last_message_id = request.GET.get('last_message_id', 0)
    try:
        last_message_id = int(last_message_id)
    except (ValueError, TypeError):
        last_message_id = 0
    
    # Get messages after the last message ID
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user),
        id__gt=last_message_id
    ).select_related('sender', 'recipient').order_by('created_at')
    
    # Mark new messages from other user as read
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        id__gt=last_message_id,
        is_read=False
    ).update(is_read=True)
    
    messages_data = []
    for msg in messages:
        message_data = {
            'id': msg.id,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.get_full_name() or msg.sender.username,
            'body': msg.body,
            'created_at': msg.created_at.isoformat(),
            'created_at_formatted': msg.created_at.strftime('%I:%M %p'),
            'is_read': msg.is_read,
            'is_sent': msg.sender == request.user,
            'has_attachment': msg.has_attachment,
        }
        
        if msg.has_attachment:
            message_data['attachment'] = {
                'url': request.build_absolute_uri(msg.attachment.url) if msg.attachment else '',
                'name': msg.attachment_name,
                'size': msg.get_file_size_display(),
                'extension': msg.get_file_extension(),
            }
        
        messages_data.append(message_data)
    
    # Get last message ID in conversation (for future polling)
    last_msg = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('-id').first()
    
    return JsonResponse({
        'messages': messages_data,
        'last_message_id': last_msg.id if last_msg else 0,
        'has_new': len(messages_data) > 0,
    })


@login_required
@require_http_methods(["POST"])
def send_message_api(request, user_id):
    """API endpoint to send a message via AJAX (supports text and file attachments)"""
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    try:
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment', None)
        
        # Message must have either body or attachment
        if not body and not attachment:
            return JsonResponse({'error': 'Message body or attachment is required'}, status=400)
        
        # Validate file size (max 10MB)
        if attachment and attachment.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File size exceeds 10MB limit'}, status=400)
        
        message = Message.objects.create(
            sender=request.user,
            recipient=other_user,
            subject=f'Chat with {other_user.get_full_name() or other_user.username}',
            body=body,
        )
        
        # Handle file attachment
        if attachment:
            message.attachment = attachment
            message.attachment_name = attachment.name
            message.attachment_size = attachment.size
            message.save()
        
        # Create notification for recipient
        from .models import Notification
        notification_message = body[:100] if body else f"Shared a file: {message.attachment_name}"
        Notification.objects.create(
            user=other_user,
            notification_type='other',
            title=f'New message from {request.user.get_full_name() or request.user.username}',
            message=notification_message,
            related_url=f'/dashboard/chat/{request.user.id}/'
        )
        
        message_data = {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'body': message.body,
            'created_at': message.created_at.isoformat(),
            'created_at_formatted': message.created_at.strftime('%I:%M %p'),
            'is_read': message.is_read,
            'is_sent': True,
            'has_attachment': message.has_attachment,
        }
        
        if message.has_attachment:
            message_data['attachment'] = {
                'url': message.attachment.url,
                'name': message.attachment_name,
                'size': message.get_file_size_display(),
                'extension': message.get_file_extension(),
            }
        
        return JsonResponse({
            'success': True,
            'message': message_data,
            'last_message_id': message.id,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """API endpoint to get updated conversations list"""
    from django.db.models import Max
    
    conversations_query = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values('sender', 'recipient').annotate(
        last_message_time=Max('created_at')
    ).order_by('-last_message_time')
    
    conversations = []
    seen_users = set()
    
    for conv in conversations_query:
        if conv['sender'] == request.user.id:
            other_user_id = conv['recipient']
        else:
            other_user_id = conv['sender']
        
        if other_user_id not in seen_users:
            seen_users.add(other_user_id)
            try:
                conv_user = User.objects.get(id=other_user_id)
                last_message = Message.objects.filter(
                    Q(sender=request.user, recipient=conv_user) |
                    Q(sender=conv_user, recipient=request.user)
                ).order_by('-created_at').first()
                
                unread = Message.objects.filter(
                    sender=conv_user,
                    recipient=request.user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'user_id': conv_user.id,
                    'user_name': conv_user.get_full_name() or conv_user.username,
                    'user_role': conv_user.get_role_display(),
                    'is_student': conv_user.is_student,
                    'last_message': {
                        'body': last_message.body if last_message else '',
                        'created_at': last_message.created_at.strftime('%b %d') if last_message else '',
                        'sender_id': last_message.sender.id if last_message else None,
                    } if last_message else None,
                    'unread_count': unread,
                    'last_message_time': conv['last_message_time'].isoformat() if conv['last_message_time'] else None,
                })
            except User.DoesNotExist:
                continue
    
    conversations.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
    
    return JsonResponse({'conversations': conversations})
