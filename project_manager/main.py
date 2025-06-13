from tkinter import Tk
from database import Base, engine
from gui import App

if __name__ == "__main__":
    Base.metadata.create_all(engine)  
    root = Tk()
    app = App(root)
    root.mainloop()
