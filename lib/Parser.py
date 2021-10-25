import os
import cv2
import configparser
import numpy as np

class ImageParser:

    def __init__(self, setting):
        self.config = configparser.ConfigParser()
        self.update_data(setting)
        # self.disect_data()

    def update_data(self, setting):
        """updates the style lettering
            :setting: dictionary of settings.json
        """
        self.settings = setting
        self.selected = setting["settings"]["Selected"]
        if self.selected in setting["profiles"]:
            try:
                self.style = setting["profiles"][self.selected]["style"].replace(".ini", "").strip()
                self.config.read(f'./Style/{self.style}.ini', encoding="utf-8")
                self.read_master()
            except:
                self.style = ""
        else:
            self.style = ""
        
    def disect_data(self):
        first = 0
        for section in self.config:
            if first == 0:
                # Ignore <DEFAULT> Section of ini that for some goddamn reason appears
                first +=1 
                continue

            data_list = self.data_to_text(self.config[section]["data"])
            rows = int(self.config[section]["rows"])
            columns = int(self.config[section]["collumns"])
            image = self.config[section]["image"]

            if not os.path.isfile(image):
                print(f"Skipping {section}. Image path {image} does not exists")
                continue
            img = cv2.imread(image)


            self.image_split(rows, columns, img, section, data_list)

    def data_to_text(self, data):
        """Ensures text is ultra clean
            :data: string
        """
        value=[]
        for i in data.strip().split(","):
            y = i.strip()
            if y: value.append(y)
        return value

    def image_split(self, rows, column, img, section, data_list):
        crop_points = []
        height_size = img.shape[0]/rows
        width_size = img.shape[1]/column

        for i in range(1, column+1):
            print(f"\n\nColumn {i}")
            path = f"./Data/{section}/{data_list[i-1]}/"

            if not os.path.exists(path):
                os.makedirs(path)

            print(path)
            for j in range(1, rows+1):
                a = ( int(width_size*(i-1))  , int(height_size*(j-1)))
                b = ( int(width_size*(i)), int(height_size*j))
                print(f"{a} {b}")

                roi = img[a[1]:b[1], a[0]:b[0]]
                roi = self.image_cleaner(roi)
                try:
                    cv2.imwrite(path + f"{j}.png", roi)
                except:
                    pass

    def image_cleaner(self, image):
        # image -> an opencv image file

        # Load image, grayscale, Gaussian blur, Otsu's threshold
        original = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (25,25), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Perform morph operations, first open to remove noise, then close to combine
        noise_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, noise_kernel, iterations=2)
        close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
        close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, close_kernel, iterations=3)

        # Find enclosing boundingbox and crop ROI
        coords = cv2.findNonZero(close)
        x,y,w,h = cv2.boundingRect(coords)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
        crop = original[y:y+h, x:x+w]

        # get the image dimensions (height, width and channels)
        h, w, c = crop.shape
        # append Alpha channel -- required for BGRA (Blue, Green, Red, Alpha)
        image_bgra = np.concatenate([crop, np.full((h, w, 1), 255, dtype=np.uint8)], axis=-1)
        # create a mask where white pixels ([255, 255, 255]) are True
        white = np.all(crop == [255, 255, 255], axis=-1)
        # change the values of Alpha to 0 for all the white pixels
        image_bgra[white, -1] = 0

        return image_bgra

    def listdir(self, mypath):
        return [f for f in os.listdir(mypath) if not os.path.isfile(os.path.join(mypath, f))]


    def parse_charsetting(self, section):
        table = {}
        all_ = self.config[section]["setting"].strip().replace("(", "").replace(")", "").split("|")
        for sett in all_:
            if sett.strip() == "":
                continue
            x = sett.split(",")
            letter = x[0].strip()
            table[letter] = {}
            for i in x[1:]:
                k = i.strip()
                if "l" in k:
                    table[letter]["left"] = int(k.replace("l", ""))
                    continue
                if "r" in k:
                    table[letter]["right"] = int(k.replace("r", ""))
                    continue
                if "v" in k:
                    table[letter]["vertical"] = int(k.replace("u", ""))
                    continue

        return table

    def read_master(self):

        self.master_table = {}
        self.space_settings = {}
        path_real = f"./Data/{self.style}"
        for section in self.listdir(path_real):
            filepath = f"{path_real}/{section}"
            if len(os.listdir(filepath)) == 0:
                print(f"Skipping {section}")
                continue 

            letters = self.listdir(filepath)
            for letter in letters:
                path = f"{path_real}/{section}/{letter}/"
                if not any(fname.endswith('.png') for fname in os.listdir(path)):
                    print("no file here lol ", path)
                    continue
                self.master_table[letter] = path

            if "setting" in self.config[section]:
                self.space_settings = self.parse_charsetting(section)

                print(f"{section}: Yup")

