# -*- coding: utf8 -*-

import json
import urllib3
import re

import telepot
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import InstPost, LikeQty, Description
from .instaparse import check_likes


proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (
    urllib3.ProxyManager,
    dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30)
)


TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

chat_id = '-1001220052715'

def welcome_message(user_id):
    status = TelegramBot.getChatMember(chat_id, user_id)['status']
    TelegramBot.sendMessage(chat_id, 'Welcome')
    if status != 'creator' and status != 'administrator':
        TelegramBot.restrictChatMember(
            chat_id,
            user_id,
            can_send_messages=True,
            can_add_web_page_previews=False,
        )


def missed_engagement(status, message_id, username):
    if status != 'creator' and status != 'administrator':
        description = Description.objects.filter(name='engagement_missed')[0].description
        text = description.format(username)
        TelegramBot.sendMessage(chat_id, text)
        TelegramBot.deleteMessage((chat_id, message_id))


def check_cmd(cmd, username, message_id, user_id):
    status = TelegramBot.getChatMember(chat_id, user_id)['status']
    likes_qty = LikeQty.objects.all()[0].qty
    splited_cmd = cmd.split(" ")
    if len(splited_cmd) == 3:
        if splited_cmd[0].lower() == 'l50':
            if splited_cmd[1][0] == '@':
                media = splited_cmd[2]
                media = re.sub('https://www.instagram.com/p/', '', media)
                media = media.split("/")
                if media[1] != "":
                    missed_engagement(status, message_id, username)
                else:
                    query_set = InstPost.objects.all().order_by('-id')[:likes_qty]
                    arr = []
                    for line in query_set:
                        media2 = line.media
                        arr.append(check_likes(splited_cmd[1][1:], media2))
                    if arr.__contains__(False):
                        missed_engagement(status, message_id, username)
                        if status == 'creator' or status == 'administrator':
                            InstPost.objects.create(media=media[0])
                    else:
                        InstPost.objects.create(media=media[0])
            else:
                missed_engagement(status, message_id, username)
        else:
            missed_engagement(status, message_id, username)
    else:
        missed_engagement(status, message_id, username)


# def _start_message(username):
#     text = "Hello, %s" % username
#     TelegramBot.sendMessage(chat_id, text)


class CommandReceiveView(View):

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        raw = request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            if chat_id != str(payload['message']['chat']['id']):
                return HttpResponseForbidden("Invalid chat")
            cmd = payload['message'].get('text')
            username = payload['message']['from']['first_name']
            user_id = payload['message']['from']['id']
            message_id = payload['message']['message_id']

            try:
                user_id = payload['message']['new_chat_participant']['id']
            except KeyError:
                try:
                    user_id = payload['message']['left_chat_participant']
                except KeyError:
                    check_cmd(cmd, username, message_id, user_id)
            else:
                welcome_message(user_id)

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
# Create your views here.
