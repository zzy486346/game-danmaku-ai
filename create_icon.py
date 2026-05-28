"""Create B站-style danmaku icon."""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon():
    """Create a B站-style danmaku icon."""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # B站粉色
    bilibili_pink = (0, 161, 214)

    # 绘制圆角矩形背景
    margin = 20
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=40,
        fill=bilibili_pink
    )

    # 绘制弹幕气泡
    bubble_color = (255, 255, 255)
    # 第一条弹幕
    draw.rounded_rectangle([50, 60, 200, 90], radius=10, fill=bubble_color)
    # 第二条弹幕
    draw.rounded_rectangle([40, 100, 180, 130], radius=10, fill=bubble_color)
    # 第三条弹幕
    draw.rounded_rectangle([60, 140, 210, 170], radius=10, fill=bubble_color)

    # 绘制弹幕文字（使用系统字体）
    try:
        font = ImageFont.truetype("msyh.ttc", 18)
    except:
        font = ImageFont.load_default()

    # 弹幕文字
    draw.text([60, 63], "弹幕来了~", fill=bilibili_pink, font=font)
    draw.text([50, 103], "666 太强了!", fill=bilibili_pink, font=font)
    draw.text([70, 143], "哈哈哈 笑死", fill=bilibili_pink, font=font)

    # 保存为ico
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    img.save(icon_path, format='ICO', sizes=[(256, 256)])
    print(f"Icon saved to: {icon_path}")
    return icon_path


if __name__ == "__main__":
    create_icon()
