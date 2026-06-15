print("starting injection..")
import os
def inject():
    return r"print('CODE HAS BEEN INJECTED!!')"

path = os.path.dirname(os.path.abspath(__file__))
new_file_path = os.path.join(path, "code.txt")
with open(new_file_path, "w") as f:
    code = inject()
    f.write(code)
           
        

