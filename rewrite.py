print("starting injection..")
import os
def inject():
    return print("CODE HAS BEEN INJECTED!!")

path = os.path.dirname(os.path.abspath(__file__))
new_file_path = os.path.join(path, "code.txt")
with open(new_file_path) as f:
    f.write(inject())
           
        

