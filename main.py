from tkinter import *
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
import struct

def main():
    root = Tk()
    root.geometry("300x250")
    open_button = ttk.Button(text="Открыть", command=open_picture_dialog)
    open_button.grid(row=0, column=0, padx=10)
    process_button = ttk.Button(text="Обработать", command=process_picture)
    process_button.grid(row=0, column=1, padx=10)
    save_button = ttk.Button(text="Сохранить", command=save_picture)
    save_button.grid(row=0, column=2, padx=10)
    root.mainloop()

def open_picture_dialog():
    global pixels
    global width
    global height
    global bits_per_pixel
    bits_per_pixel = 0
    file_path = filedialog.askopenfilename(
        title="Выберите BMP файл",
        filetypes=[
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
    )
    with open(file_path, 'rb') as file:
        signature = file.read(2)
        if signature != b'BM':
            raise ValueError("Это не BMP файл")

        file.seek(10)
        data_offset = struct.unpack('<I', file.read(4))[0]
        file.seek(18)
        width = struct.unpack('<i', file.read(4))[0]
        height = struct.unpack('<i', file.read(4))[0]
        file.seek(28)
        bits_per_pixel = struct.unpack('<H', file.read(2))[0]
        bytes_per_pixel = bits_per_pixel // 8
        row_size = width * bytes_per_pixel
        padding = (4 - (row_size % 4)) % 4
        file.seek(data_offset)
        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                blue = file.read(1)[0]
                green = file.read(1)[0]
                red = file.read(1)[0]
                alpha = file.read(1)[0]
                row.append((red, green, blue, alpha))
            if padding > 0:
                file.read(padding)
            pixels.append(row)
        pixels.reverse()
        show_picture()

def process_picture():
    pixels[0][0] = (0, 127, 255, 255)
    pixels[0][-1] = (127, 0, 255, 255)
    pixels[height//2][width//2] = (127, 255, 0, 255)
    showinfo("Успех", "Файл обработан успешно")

def save_picture():
    if pixels is None:
        print("Нет данных для сохранения!")
        return
    file_path = filedialog.asksaveasfilename(
        title="Сохранить BMP файл",
        defaultextension=".bmp",
        filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
    )
    pixels_to_save = pixels[::-1]
    height = len(pixels_to_save)
    width = len(pixels_to_save[0]) if height > 0 else 0
    bytes_per_pixel = 4
    row_size = width * bytes_per_pixel
    padding = (4 - (row_size % 4)) % 4
    image_size = height * (row_size + padding)
    file_size = 54 + image_size
    with open(file_path, 'wb') as file:
        file.write(b'BM')
        file.write(struct.pack('<I', file_size))
        file.write(struct.pack('<I', 0))
        file.write(struct.pack('<I', 54))
        file.write(struct.pack('<I', 40))
        file.write(struct.pack('<i', width))
        file.write(struct.pack('<i', height))
        file.write(struct.pack('<H', 1))
        file.write(struct.pack('<H', 32))
        file.write(struct.pack('<I', 0))
        file.write(struct.pack('<I', image_size))
        file.write(struct.pack('<I', 0))
        file.write(struct.pack('<I', 0))
        file.write(struct.pack('<I', 0))
        file.write(struct.pack('<I', 0))
        for y in range(height):
            for x in range(width):
                if y < len(pixels_to_save) and x < len(pixels_to_save[y]):
                    r, g, b, a = pixels_to_save[y][x]
                    file.write(struct.pack('BBBB', b, g, r, a))
                else:
                    file.write(b'\x00\x00\x00\x00')
            if padding > 0:
                file.write(b'\x00' * padding)

    showinfo("Успех", "Файл успешно сохранен")


def show_picture():
    window = Toplevel()
    window.title("Изображение")
    canvas = Canvas(window, width=width, height=height)
    canvas.pack()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x][:3]
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline="")

if __name__ == "__main__":
    main()