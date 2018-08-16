from instaparser.agents import AgentAccount
from instaparser.entities import Media


agent = AgentAccount("vasiliyvasilenko8", "?naScar88")


def check_likes(username, media):
    media = Media(media)
    pointer = 0
    while not pointer is None:
        likes, pointer = agent.get_likes(media, pointer=pointer)
        for like in likes:
                if str(like) == username:
                    return True
    return False
