import os
from PIL import Image

def resize_dds_batch(input_folder, output_folder, length = 50):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".dds"):
            with Image.open(os.path.join(input_folder, filename)) as img:
                # 计算新尺寸
                new_size = (length, length)

                # 使用高质量重采样算法缩小
                # Image.Resampling.LANCZOS 适合保持细节
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

                # 保存结果
                # 注意：Pillow 写入 DDS 可能不支持原有的特殊压缩格式（如 BC7）
                # 如果引擎报错，建议先存为 PNG 再用工具压回 DDS
                resized_img.save(os.path.join(output_folder, filename))
                print(f"已处理: {filename} -> {new_size}")


INPUT_DIR = r"C:\Users\Estelle\Documents\Paradox Interactive\Stellaris\mod\better_colony_manage\gfx\interface\bca_districts\origin"
OUTPUT_DIR_50 = r"C:\Users\Estelle\Documents\Paradox Interactive\Stellaris\mod\better_colony_manage\gfx\interface\bca_districts\50"
OUTPUT_DIR_25 = r"C:\Users\Estelle\Documents\Paradox Interactive\Stellaris\mod\better_colony_manage\gfx\interface\bca_districts\25"
resize_dds_batch(INPUT_DIR, OUTPUT_DIR_50, length=50)
resize_dds_batch(INPUT_DIR, OUTPUT_DIR_25, length=25)
