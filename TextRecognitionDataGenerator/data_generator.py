import os
import random
import math
import shutil
import numpy as np

from PIL import Image, ImageFilter

from computer_text_generator import ComputerTextGenerator

try:
    from handwritten_text_generator import HandwrittenTextGenerator
except ImportError as e:
    print('Missing modules for handwritten text generation.')
from background_generator import BackgroundGenerator
from distorsion_generator import DistorsionGenerator


class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """
        for i in list(t):
            cls.generate(*i)

    @classmethod
    def generate(cls, index, text, font, out_dir, size, extension, skewing_angle, random_skew, blur, random_blur,
                 background_type, distorsion_type, distorsion_orientation, is_handwritten, name_format, width,
                 alignment, text_color, orientation, space_width):
        image = None

        ##########################
        # Create picture of text #
        ##########################

        ##新建状态栏：表明具体添加的位置
        addChar = []
        for i in range(1000):
            charList = ['a', 'b', 'c', 'd', 'A', 'B', 'C', 'D']
            addChar.append(charList[random.randint(0, 7)])

        # 生成手写字符
        if orientation == 1:
            raise ValueError("Vertical handwritten text is unavilable!")
        imgHandWritten, Rows = HandwrittenTextGenerator.generate(addChar, text_color)
        assert len(imgHandWritten) == len(Rows)

        if os.path.exists("handChars"):
            shutil.rmtree("handChars")
        os.mkdir("handChars")

        # 将图片合并起来
        for i in range(len(Rows)):
            image = imgHandWritten[i]
            #print("51", image.size)
            random_angle = random.randint(0 - skewing_angle, skewing_angle)
            rotated_img = image.rotate(skewing_angle if not random_skew else random_angle, expand=1)
            #print("54rotate", rotated_img.size)
            #############################
            # Apply distorsion to image #
            #############################

            if distorsion_type == 0:
                distorted_img = rotated_img  # Mind = blown
            elif distorsion_type == 1:
                distorted_img = DistorsionGenerator.sin(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )
            elif distorsion_type == 2:
                distorted_img = DistorsionGenerator.cos(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )
            else:
                distorted_img = DistorsionGenerator.random(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )
            #print("78distorted_img", distorted_img.size)
            ##################################
            # Resize image to desired format #
            ##################################

            # Horizontal text
            if orientation == 0:
                new_width = int(float(distorted_img.size[0] + 10) * (float(size) / float(distorted_img.size[1] + 10)))
                resized_img = distorted_img.resize((new_width, size - 10), Image.ANTIALIAS)
                background_width = width if width > 0 else new_width + 10
                background_height = size
            # Vertical text
            elif orientation == 1:
                new_height = int(float(distorted_img.size[1] + 10) * (float(size) / float(distorted_img.size[0] + 10)))
                resized_img = distorted_img.resize((size - 10, new_height), Image.ANTIALIAS)
                background_width = size
                background_height = new_height + 10
            else:
                raise ValueError("Invalid orientation")
            print("97orientation", resized_img.size)
            #############################
            # Generate background image #
            #############################
            if background_type == 0:
                background = BackgroundGenerator.gaussian_noise(background_height, background_width)
            elif background_type == 1:
                background = BackgroundGenerator.plain_white(background_height, background_width)
            elif background_type == 2:
                background = BackgroundGenerator.quasicrystal(background_height, background_width)
            else:
                background = BackgroundGenerator.picture(background_height, background_width)

            #############################
            # Place text with alignment #
            #############################

            new_text_width, _ = resized_img.size

            if alignment == 0:
                background.paste(resized_img, (5, 5), resized_img)
            elif alignment == 1:
                background.paste(resized_img, (int(background_width / 2 - new_text_width / 2), 5), resized_img)
            else:
                background.paste(resized_img, (background_width - new_text_width - 5, 5), resized_img)
            #print("122background", background.size)
            ##################################
            # Apply gaussian blur #
            ##################################

            final_image = background.filter(
                ImageFilter.GaussianBlur(
                    radius=(blur if not random_blur else random.randint(0, blur))
                )
            )
            #print("132final_image", final_image.size)
            # #####################################
            # # Generate name for resulting image #
            # #####################################

            # # Save the image
            final_image.convert("RGB").save("handChars/"+addChar[i]+"_"+str(i)+".jpg")

