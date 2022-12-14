import argparse
import string
import random
import numpy as np
import cv2
from PIL import Image
from crypto import encrypt_file, decrypt_file
from crypto2 import encrypt_file_cbc, decrypt_file_cbc
import os
import random

def get_noise_model(noise_type="gaussian,0,50"):
    tokens = noise_type.split(sep=",")

    if tokens[0] == "gaussian":
        min_stddev = int(tokens[1])
        max_stddev = int(tokens[2])

        def gaussian_noise(img):
            noise_img = img.astype(np.float)
            stddev = np.random.uniform(min_stddev, max_stddev)
            noise = np.random.randn(*img.shape) * stddev
            noise_img += noise
            noise_img = np.clip(noise_img, 0, 255).astype(np.uint8)
            return noise_img
        return gaussian_noise
    elif tokens[0] == "clean":
        return lambda img: img
    elif tokens[0] == "text":
        min_occupancy = int(tokens[1])
        max_occupancy = int(tokens[2])

        def add_text(img):
            img = img.copy()
            h, w, _ = img.shape
            font = cv2.FONT_HERSHEY_SIMPLEX
            img_for_cnt = np.zeros((h, w), np.uint8)
            occupancy = np.random.uniform(min_occupancy, max_occupancy)

            while True:
                n = random.randint(5, 10)
                random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
                font_scale = np.random.uniform(0.5, 1)
                thickness = random.randint(1, 3)
                (fw, fh), baseline = cv2.getTextSize(random_str, font, font_scale, thickness)
                x = random.randint(0, max(0, w - 1 - fw))
                y = random.randint(fh, h - 1 - baseline)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                cv2.putText(img, random_str, (x, y), font, font_scale, color, thickness)
                cv2.putText(img_for_cnt, random_str, (x, y), font, font_scale, 255, thickness)

                if (img_for_cnt > 0).sum() > h * w * occupancy / 100:
                    break
            return img
        return add_text
    elif tokens[0] == "impulse":
        min_occupancy = int(tokens[1])
        max_occupancy = int(tokens[2])

        def add_impulse_noise(img):
            occupancy = np.random.uniform(min_occupancy, max_occupancy)
            mask = np.random.binomial(size=img.shape, n=1, p=occupancy / 100)
            noise = np.random.randint(256, size=img.shape)
            img = img * (1 - mask) + noise * mask
            return img.astype(np.uint8)
        return add_impulse_noise
    elif tokens[0] == "aes":
        def add_encryption_noise(img):
            # print(type(img))
            im = Image.fromarray(img)
            im.save("temp.ppm")
            f = open("temp.ppm", "rb")
            lines = f.readlines()
            header = lines[0:3]
            body = lines[3:]
            # print(lines)
            f2 = open("temp2.txt", "wb")
            f2.writelines(body)
            # f2.writelines(f.readlines()[3:])
            f.close()
            f2.close()
            encrypt_file('abcdefghji123456'.encode('utf8'), 'temp2.txt')
            f3 = open("temp2.txt.encrypted", "rb")
            enclines = f3.readlines()
            f4 = open("enctemp.ppm", "wb")
            f4.writelines(header)
            f4.writelines(enclines)
            f3.close()
            f4.close()
            img = cv2.imread("enctemp.ppm")
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            # !head -n 3 temp.ppm > header.txt
            # !tail -n +4 temp.ppm > body.bin

            # !openssl enc -aes-128-cbc -nosalt -pass pass:"random" -in body.bin -out body.ecb.bin 2> random
            # !cat header.txt body.ecb.bin > temp.ecb.ppm
            # img = cv2.imread("temp.ecb.ppm")
            return img
        return add_encryption_noise
    elif tokens[0] == "aes_byte_error":
        def add_encryption_noise(img):
            # print(type(img))
            im = Image.fromarray(img)
            im.save("temp.ppm")
            f = open("temp.ppm", "rb")
            lines = f.readlines()
            header = lines[0:3]
            body = lines[3:]
            # print(lines)
            f2 = open("temp2.txt", "wb")
            f2.writelines(body)
            # f2.writelines(f.readlines()[3:])
            f.close()
            f2.close()
            # iv, filesize = encrypt_file_cbc('abcdefghji123456'.encode('utf8'), 'temp2.txt')
            filesize = encrypt_file('abcdefghji123456'.encode('utf8'), 'temp2.txt')
            fh = open("temp2.txt.encrypted", "r+b")
            file_size = os.path.getsize('/content/ece595ml-project/temp2.txt.encrypted')
            # print(file_size, int(tokens[1]))
            for i in range(int(tokens[1])):
              fh.seek(random.randint(9, file_size-40))
              fh.write(b'a')
            fh.close()
            file_size = os.path.getsize('/content/ece595ml-project/temp2.txt.encrypted')
            # print(file_size)
            # decrypt_file_cbc('abcdefghji123456'.encode('utf8'), 'temp2.txt.encrypted', iv, filesize)
            decrypt_file('abcdefghji123456'.encode('utf8'), 'temp2.txt.encrypted', filesize)
            f6 = open("temp2.txt", "rb")
            f5 = open("enctemp.ppm", "wb")
            f5.writelines(header)
            f5.writelines(f6.readlines())
            f5.close()
            f6.close()
            img = cv2.imread("enctemp.ppm")
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            # !head -n 3 temp.ppm > header.txt
            # !tail -n +4 temp.ppm > body.bin

            # !openssl enc -aes-128-cbc -nosalt -pass pass:"random" -in body.bin -out body.ecb.bin 2> random
            # !cat header.txt body.ecb.bin > temp.ecb.ppm
            # img = cv2.imread("temp.ecb.ppm")
            return img
        return add_encryption_noise
    else:
        raise ValueError("noise_type should be 'gaussian', 'clean', 'text', or 'impulse'")


def get_args():
    parser = argparse.ArgumentParser(description="test noise model",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--image_size", type=int, default=256,
                        help="training patch size")
    parser.add_argument("--noise_model", type=str, default="gaussian,0,50",
                        help="noise model to be tested")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    image_size = args.image_size
    noise_model = get_noise_model(args.noise_model)

    while True:
        image = np.ones((image_size, image_size, 3), dtype=np.uint8) * 128
        noisy_image = noise_model(image)
        cv2.imshow("noise image", noisy_image)
        key = cv2.waitKey(-1)

        # "q": quit
        if key == 113:
            return 0


if __name__ == '__main__':
    main()
