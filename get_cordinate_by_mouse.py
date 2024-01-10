import tkinter
from PIL import Image, ImageTk
import cv2
from os import path

PATH = path.join(path.dirname(__file__), 'map.png')

class MouseChaser:

    def __init__(self, master, outputFile, x, y, meter_per_pixel, sampling_time, window_size_magnification):
        self.master = master  # 親ウィジェット
        self.mouse_x = None  # マウスのx座標
        self.mouse_y = None  # マウスのy座標
        self.count = 0
        self.state = 0
        self.textFile = outputFile
        self.xDiff = x
        self.yDiff = y
        self.meter_per_pixel = meter_per_pixel
        self.sampling_time = sampling_time
        self.window_size_magnification = window_size_magnification

        self.image = cv2.imread(PATH)
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

        # キャンバスを作成
        self.canvas = tkinter.Canvas(
            master,
            width=self.width * self.window_size_magnification, height=self.height * self.window_size_magnification,
        )
        self.canvas.pack()

        self.image = Image.open(PATH)
        self.image = self.image.resize((self.width * self.window_size_magnification, self.height * self.window_size_magnification))
        self.image = ImageTk.PhotoImage(self.image) # 画像ファイルのオブジェクトを作成
        self.canvas.create_image(0, 0, image=self.image, anchor=tkinter.NW) # 画像を描画

        # 1s後にdirectionを実行する
        self.canvas.bind("<Motion>", self.get_mouse_position)
        self.canvas.bind("<Button-1>", self.start_sampling)

    def start_sampling(self, event):
        self.state += 1
        # print(self.state)


    def get_mouse_position(self, event):
        # print("a")
        # マウスの座標を覚えておく
        self.mouse_x = event.x
        self.mouse_y = event.y
        # print(self.mouse_x, self.mouse_y)
        # print(self.count)
        # print((self.mouse_x / self.window_size_magnification + self.xDiff) * self.meter_per_pixel, (self.height - (self.mouse_y / self.window_size_magnification - self.yDiff)) * self.meter_per_pixel)
        if(self.state == 1 and self.count == self.sampling_time and 0 <= (self.mouse_x / self.window_size_magnification + self.xDiff) * self.meter_per_pixel <= 2 and 0 <= (self.height - (self.mouse_y / self.window_size_magnification - self.yDiff)) * self.meter_per_pixel <= 2):
            self.count = 0

            #マウス座標を表示
            # print("Mouse position: ", (self.mouse_x / self.window_size_magnification + self.xDiff) * self.meter_per_pixel, (self.height - (self.mouse_y / self.window_size_magnification - self.yDiff)) * self.meter_per_pixel)
            self.canvas.create_oval(self.mouse_x - 2, self.mouse_y - 2,  self.mouse_x + 2, self.mouse_y + 2)
            self.textFile.write(f"{(self.mouse_x / self.window_size_magnification + self.xDiff) * self.meter_per_pixel}, {(self.height - (self.mouse_y / self.window_size_magnification - self.yDiff)) * self.meter_per_pixel}, 0\n")


def set_timer(app, chaser):
    # アプリを開始してからの時間をタイマーにセット
    if(chaser.count < chaser.sampling_time):
        chaser.count += 1
    # print(chaser.timer)
    app.after(1, set_timer, app, chaser)

def main():
    x = input("原点から見た画像の左下のx座標を(単位はmで)入力してください: ")
    y = input("原点から見た画像の左下のy座標を(単位はmで)入力してください: ")
    meter_per_pixel = input("1ピクセルあたりの実際の長さを(単位はmで)入力してください: ")  # ピクセルあたりの実際の長さ
    sampling_time = input("点を取得する時間間隔(単位はms)を入力して下さい: ")
    window_size_magnification = input("ウィンドウサイズの倍率(単位は整数)を入力してください: ")
    x = float(x)
    y = float(y)
    meter_per_pixel = float(meter_per_pixel)
    sampling_time = float(sampling_time)
    window_size_magnification = int(window_size_magnification)
    x /= meter_per_pixel
    y /= meter_per_pixel
    # ファイルを開く
    outputFile = open('myfile.txt', 'w')

    # メインウィンドウを作成
    app = tkinter.Tk()
    #インスタンス生成
    # map = Map(app)
    chaser = MouseChaser(app, outputFile, x, y, meter_per_pixel, sampling_time, window_size_magnification)
    app.after(1, set_timer, app, chaser)
    # メインループ
    app.mainloop()

    outputFile.close

if __name__ == "__main__":
    main()