print("starting injection..")
import os
import time
def inject():
    return r"""

def hack(game): 
 import time
 print('CODE HAS BEEN INJECTED!!')
 for tank in game.tanks:
    if tank.name != "Nick's tank":
     print(f"killing {tank.name}")
     tank.health = 0
     tank.hp_lost = 100
     tank.alive = False
     time.sleep(1)
     print("bye bye tanks :]")
    elif tank.name == "Nick's tank":
     tank.score =+ 5000
     time.sleep(1)
hack(game)
"""

path = os.path.dirname(os.path.abspath(__file__))
new_file_path = os.path.join(path, "code.txt")
with open(new_file_path, "w") as f:
    code = inject()
    f.write(code)
           
        

