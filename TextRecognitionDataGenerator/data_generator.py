import os
import random
import math

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
        statusIndex = random.randint(0, len(text))
        charList = ['a', 'b', 'c', 'd', 'A', 'B', 'C', 'D']
        imgList = []
        imageFirst = ComputerTextGenerator.generate(text[:statusIndex] + "(", font, text_color, size, orientation,
                                                    space_width)

        # 生成手写字符
        addChar = charList[random.randint(0, 7)]
        if orientation == 1:
            raise ValueError("Vertical handwritten text is unavilable!")
        imgHandWritten = HandwrittenTextGenerator.generate(addChar, text_color)
        imgHandWritten.save("handwrittenchar.png")

        imageLast = ComputerTextGenerator.generate(")" + text[statusIndex:], font, text_color, size, orientation,
                                                   space_width)

        # 将图片合并起来
        w_first, h_first = imageFirst.size
        w_hand, h_hand = imgHandWritten.size
        w_last, h_last = imageLast.size

        try:
            if h_first == h_last:
                imgNewHandWritten = imgHandWritten.resize((math.ceil(w_hand * h_first / h_hand), h_first),
                                                          Image.ANTIALIAS)
                imageNewLast = imageLast
            else:
                imgNewHandWritten = imgHandWritten.resize((math.ceil(w_hand * h_first / h_hand), h_first),
                                                          Image.ANTIALIAS)
                imageNewLast = imageLast.resize((math.ceil(w_last * h_first / h_last), h_first), Image.ANTIALIAS)
        except Exception:

            raise ValueError
        finally:
            print("imageFirst:", imageFirst.getbands(), imageFirst.size)
            print("imgHandWritten:", imgHandWritten.getbands(), imgNewHandWritten.size)
            print("imageLast:", imageLast.getbands(), imageNewLast.size)

        to_image = Image.new("RGBA", (w_first + imgNewHandWritten.size[0] + imageNewLast.size[0], h_first))
        to_image.paste(imageFirst, (0, 0))
        to_image.paste(imgNewHandWritten, (w_first, 0))
        to_image.paste(imageNewLast, (w_first + imgNewHandWritten.size[0], 0))

        # if is_handwritten:
        #     if orientation == 1:
        #         raise ValueError("Vertical handwritten text is unavailable")
        #     image = HandwrittenTextGenerator.generate(text, text_color)
        # else:
        #     image = ComputerTextGenerator.generate(text, font, text_color, size, orientation, space_width)

        image = to_image
        random_angle = random.randint(0 - skewing_angle, skewing_angle)
        rotated_img = image.rotate(skewing_angle if not random_skew else random_angle, expand=1)

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

        ##################################
        # Apply gaussian blur #
        ##################################

        final_image = background.filter(
            ImageFilter.GaussianBlur(
                radius=(blur if not random_blur else random.randint(0, blur))
            )
        )

        # #####################################
        # # Generate name for resulting image #
        # #####################################
        if name_format == 0:
            image_name = '{}_{}.{}'.format(text, str(index), extension)
        elif name_format == 1:
            image_name = '{}_{}.{}'.format(str(index), text, extension)
        elif name_format == 2:
            image_name = '{}.{}'.format(str(index), extension)
        else:
            print('{} is not a valid name format. Using default.'.format(name_format))
            image_name = '{}_{}.{}'.format(text, str(index), extension)

        # # Save the image
        final_image.convert('RGB').save(os.path.join(out_dir, image_name))
        # to_image.convert("RGB").save(os.path.join(out_dir, image_name))
        imgHandWritten.convert("RGB").save(os.path.join(out_dir, "handChar" + image_name))
