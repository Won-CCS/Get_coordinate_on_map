import tkinter as tk
from PIL import Image, ImageTk
import cv2
from os import path
import os

PATH = path.join(path.dirname(__file__), 'map.png')

class MouseChaser:
    def __init__(self, master, outputFile, x, y, meter_per_pixel, sampling_time):
        self.master = master
        self.mouse_x = None
        self.mouse_y = None
        self.count = 0
        self.state = 0
        self.textFile = outputFile
        self.xDiff = x
        self.yDiff = y
        self.meter_per_pixel = meter_per_pixel
        self.sampling_time = sampling_time

        self.image = cv2.imread(PATH)
        self.original_image_height = self.image.shape[0]
        self.original_image_width = self.image.shape[1]
        self.image_height = self.image.shape[0]
        self.image_width = self.image.shape[1]
        self.image_aspect_ratio = self.image_width / self.image_height

        self.canvas = tk.Canvas(
            master,
            width=self.image_width,
            height=self.image_height,
            # bg = "cyan",
        )
        self.canvas.pack()

        self.image = Image.open(PATH)
        self.image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.image, anchor=tk.NW, tags="img")
        
        self.master.geometry(str(self.image_width + 30)+"x"+str(self.image_height + 30))
        
        self.prev_window_width = self.master.winfo_width()
        self.prev_window_height = self.master.winfo_height()

        self.canvas.bind("<Motion>", self.get_mouse_position)
        self.canvas.bind("<Button-1>", self.start_sampling)
        self.master.bind("<Configure>", self.on_window_resize)

    def start_sampling(self, event):
        self.state += 1

    def get_mouse_position(self, event):
        self.image_size_magnification = self.image_width / self.original_image_width
        self.mouse_x = self.canvas.canvasx(event.x)
        self.mouse_y = self.canvas.canvasy(event.y)
        if self.state == 1 and self.count == self.sampling_time:
            self.count = 0
            self.canvas.create_oval(self.mouse_x - 2, self.mouse_y - 2,  self.mouse_x + 2, self.mouse_y + 2)
            self.textFile.write(f"{(self.mouse_x / self.image_size_magnification + self.xDiff) * self.meter_per_pixel}, {(self.original_image_height - (self.mouse_y / self.image_size_magnification - self.yDiff)) * self.meter_per_pixel}, 0\n")
        elif self.state == 2:
            self.state += 1
            self.textFile.close()


    def on_window_resize(self, event):
        # 変更されたウィンドウサイズを取得
        new_width = event.width
        new_height = event.height

        if new_width != self.prev_window_width or new_height != self.prev_window_height:        
            self.resize_image(new_width, new_height)
            self.prev_window_width = new_width
            self.prev_window_height = new_height

    def resize_image(self, new_width, new_height):
        # 画像のアスペクト比を保ちつつ、ウィンドウサイズに合わせて画像をリサイズ
        new_image_width = new_width
        new_image_height = int(new_width / self.image_aspect_ratio)

        if new_image_height > new_height:
            new_image_height = new_height
            new_image_width = int(new_height * self.image_aspect_ratio)

        resized_image = ImageTk.PhotoImage(
            Image.open(PATH).resize((new_image_width, new_image_height), Image.LANCZOS)
        )

        self.image = resized_image
        self.image_width = new_image_width
        self.image_height = new_image_height
        self.canvas.config(width=new_image_width, height=new_image_height)
        self.canvas.itemconfig("img", image=resized_image)

def set_timer(app, chaser):
    if chaser.count < chaser.sampling_time:
        chaser.count += 1
    app.after(1, set_timer, app, chaser)

def main():
    output_file_name = input("出力するファイル名(拡張子抜き)を入力してください: ")
    x = float(input("原点から見た画像の左下のx座標を(単位はmで)入力してください: "))
    y = float(input("原点から見た画像の左下のy座標を(単位はmで)入力してください: "))
    meter_per_pixel = float(input("1ピクセルあたりの実際の長さを(単位はmで)入力してください: "))
    sampling_time = float(input("点を取得する時間間隔(単位はms)を入力してください: "))

    x /= meter_per_pixel
    y /= meter_per_pixel
    outputFile = open(output_file_name + ".txt", 'w')

    app = tk.Tk()
    chaser = MouseChaser(app, outputFile, x, y, meter_per_pixel, sampling_time)
    app.after(1, set_timer, app, chaser)
    app.mainloop()

    number_of_lines = sum([1 for _ in open(output_file_name + ".txt")])
    with open(output_file_name + '.txt', 'r+', encoding='utf-8') as file:
        # 全行取得
        line = file.readlines()
        # 途中に挿入
        line.insert(0, str(number_of_lines) + '\n\n')
        # ファイルデータ全削除
        file.truncate(0)
        # 先頭にストリームを移動
        file.seek(0, os.SEEK_SET)
        # 書き込み
        file.writelines(line)


if __name__ == "__main__":
    main()
