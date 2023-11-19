import re
from tkinter import Tk, ttk, StringVar, Canvas
import serial.tools.list_ports
import tkinter.messagebox as mb
import threading
from serial import SerialException


root = Tk()
port_label = None
nums = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
nums_amount = 0
ser = None
com_entry = None
listen_thread = None
thread_barrier = False


def validate_input(n):
    return re.fullmatch("\\d*", n) is not None


def init_window():
    global com_entry, port_label, root
    root.minsize(900, 530)
    root.resizable(False, False)
    root.title('RND')
    label = ttk.Label(text='Номер COM порта:')
    label.place(rely=0, relx=0.3)
    check = (root.register(validate_input), "%P")
    com_entry = ttk.Entry(validate="key", validatecommand=check)
    com_entry.place(rely=0, relx=0.45)
    btn_connect = ttk.Button(text="Подключиться", command=connect_button_pressed)
    btn_connect.place(rely=0, relx=0.6)
    port_label = ttk.Label(text='')
    port_label.place(rely=0, relx=0.9)
    update_gist()
    return root


def connect_button_pressed():
    global listen_thread, thread_barrier
    thread_barrier = False
    if listen_thread is not None:
        listen_thread.join()
    thread_barrier = True
    listen_thread = threading.Thread(target=connect_to_com_port)
    listen_thread.daemon = True
    listen_thread.start()


def update_gist():
    canvas = Canvas(root, width=900, height=500, bg="lightblue", cursor="pencil")
    canvas.place(rely=0.05, relx=0)
    canvas.create_line(20, 480, 20, 20, width=2, arrow="last")
    canvas.create_line(20, 480, 880, 480, width=2, arrow="last")
    for i in range(0, 5):
        canvas.create_line(15, 405 - i * 75, 25, 405 - i * 75, width=2)
        canvas.create_text(17, 405 - i * 75, text=f'{round(0.2 + 0.2 * i, 1)}')
    for i in range(1, 7):
        chance = nums[i] / nums_amount
        height = 375 * (1 - chance)
        canvas.create_text(120 * i, 495, text=f'{i}')
        canvas.create_rectangle(120 * i - 40, 478, 120 * i + 40, height, fill="blue", outline="blue")
        canvas.create_text(120 * i, height - 10, text=f'{chance}')
    return canvas


def connect_to_com_port():
    global ser, port_label, com_entry, thread_barrier, nums_amount
    com_number = f'COM{com_entry.get()}'
    try:
        ser = serial.Serial(com_number, 115200, timeout=0)
        port_label['text'] = com_number
        while thread_barrier:
            data = ser.readline().decode('utf8').strip()
            if len(data) > 0:
                key = int(data)
                if key == 0:
                    for i in range(1, 7):
                        nums[i] = 0
                        nums_amount = 0
                else:
                    nums_amount += 1
                    nums[key] += 1
                update_gist()
    except SerialException:
        mb.showerror('Ошибка', f'Не удалось открыть порт {com_number}')


if __name__ == '__main__':
    app = init_window()
    app.mainloop()
