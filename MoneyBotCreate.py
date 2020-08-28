import telebot
import ssl
from aiohttp import web

api_token = '1318941045:AAFZvhv3Tdfa8JgdN99Z7ptAfRb64gmIor0'


def polling_bot():

    bot = telebot.TeleBot(api_token)

    bot.polling()
    return bot


def webhook_bot():
    webhook_host = '35.228.26.125'
    webhook_port = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
    webhook_listen = '0.0.0.0'  # In some VPS you may need to put here the IP addr

    webhook_ssl_cert = './url_cert.pem'  # Path to the ssl certificate
    webhook_ssl_priv = './url_private.key'  # Path to the ssl private key

    webhook_url_base = "https://{}:{}".format(webhook_host, webhook_port)
    webhook_url_path = "/{}/".format(api_token)

    bot = telebot.TeleBot(api_token)
    app = web.Application()
    app.router.add_post('/{token}/', handle)

    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    bot.set_webhook(url=webhook_url_base + webhook_url_path,
                    certificate=open(webhook_ssl_cert, 'r'))

    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(webhook_ssl_cert, webhook_ssl_priv)

    # Start aiohttp server
    web.run_app(
        app,
        host=webhook_listen,
        port=webhook_port,
        ssl_context=context,
    )


# Process webhook calls
async def handle(request, bot):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)
