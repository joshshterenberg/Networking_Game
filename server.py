import socket
from _thread import *
import pickle
from game import Game

# Defines the server and port that the game will run on.
server = "192.168.0.11"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# Creates connection to server, listening
s.listen()
print("Waiting for a connection, Server Started")

# Stores the IP addresses of the connected client, the games and their unique ids
connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount # keep track of stuff in case someone leaves
    conn.send(str.encode(str(p))) # what player are we

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()
            # Check if game still exists
            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)

                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()


# Once we accept a connection this runs
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1 # increment number of games
    p = 0 # current player
    gameId = (idCount - 1)//2 # keeps track of how many games
    if idCount % 2 == 1: # odd num of players, make new game
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True # 2 players connected, ready to play
        p = 1


    start_new_thread(threaded_client, (conn, p, gameId))
