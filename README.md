Before you use the API program with GUI, make sure you have already installed a Ollama Model. Any Models will do, in my case, I use the Llama3.2:1b-instruct-q3_K_M

Download models on: 
https://ollama.com/library

After installing model:
1. make sure you install tkinter, using pip
2. install pyinstaller(Optional) this will do if you want to make your program an .exe file.

If you're using a different Llama model, just change the value in the program

Pyinstaller:
1. Open the directory where your python program is located.
2. open it on CMD or Terminal
3. run the command: pyinstaller <python_fileName>.pyw --onefile
4. if you have an icon, you can use this command: pyinstaller --icon=<iconFileName>.ico <python_fileName>.pyw --onefile
