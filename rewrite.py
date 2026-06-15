print("starting injection..")
import os
def inject():
    return r"""

def hack(game): 
 print('CODE HAS BEEN INJECTED!!')
 for tank in game.tanks:
    if tank.name != "Nick's tank":
     print(f"killing {tank.name}")
     tank.health = 0
     print("bye bye tanks :]")
hack(game)
"""

path = os.path.dirname(os.path.abspath(__file__))
new_file_path = os.path.join(path, "code.txt")
with open(new_file_path, "w") as f:
    code = inject()
    f.write(code)
           
        

