from channels.layers import get_channel_layer


user_channels = {}


def channels_add(channels_name, user_id):
    print('>>>>>>>>>>>add user in channels: ' + str(user_id))
    user_channels[user_id] = channels_name


def channels_remove(channels_name):
    user_channels.pop(channels_name)


def get_channels_name(user_id):
    return user_channels[str(user_id)]


async def send_notice(user_id, notice_type, message):
    channel_name = get_channels_name(str(user_id))
    channels_layout = get_channel_layer()
    await channels_layout.send(channel_name, {
        "type": "notice.message",
        "message": message,
        "notice_type": notice_type
    })

if __name__ == "__main__":
    channels_add("asdasdasd", 1)
    print(get_channels_name(1))