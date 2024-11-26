import re
from bs4 import BeautifulSoup
import json


def extract_colors(html_content, css_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    colors = []

    # 从导航菜单中提取颜色名称
    nav_items = soup.select('#colors li a')
    names_dict = {}
    for item in nav_items:
        color_id = item.parent.parent.get('id')
        names = item.text.split(', ')
        if len(names) == 2:
            names_dict[color_id] = {
                'chinese': names[0],
                'english': names[1]
            }

    # 从CSS中提取CMYK值
    cmyk_values = {}
    for color_id in names_dict.keys():
        cmyk_pattern = '#' + color_id + r' dd\.c .+?rotate\((.+?)deg\).+?dd\.m .+?rotate\((.+?)deg\).+?dd\.y .+?rotate\((.+?)deg\).+?dd\.k .+?rotate\((.+?)deg\)'
        cmyk_match = re.search(cmyk_pattern, css_content, re.DOTALL)
        if cmyk_match:
            c = round(float(cmyk_match.group(1)) / 3.6, 1)  # 360度对应100%
            m = round(float(cmyk_match.group(2)) / 3.6, 1)
            y = round(float(cmyk_match.group(3)) / 3.6, 1)
            k = round(float(cmyk_match.group(4)) / 3.6, 1)
            cmyk_values[color_id] = {'C': c, 'M': m, 'Y': y, 'K': k}

    # 从CSS中提取颜色代码和位置信息
    for color_id in names_dict.keys():
        # 提取位置信息
        left_pattern = '#' + color_id + r'\s*{[^}]*left:\s*(\d+)px'
        top_pattern = '#' + color_id + r'\s*{[^}]*top:\s*(\d+)px'
        left_match = re.search(left_pattern, css_content)
        top_match = re.search(top_pattern, css_content)

        # 提取RGB颜色代码
        color_pattern = '#' + color_id + r' a[^}]*background-color: #([A-F0-9]+)'
        color_match = re.search(color_pattern, css_content)

        if left_match and top_match and color_match:
            hex_color = color_match.group(1)
            # 转换HEX到RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            color_info = {
                'id': color_id,
                'chinese_name': names_dict[color_id]['chinese'],
                'english_name': names_dict[color_id]['english'],
                'color': {
                    'hex': f'#{hex_color}',
                    'rgb': {'R': r, 'G': g, 'B': b},
                    'cmyk': cmyk_values.get(color_id, {})
                },
                'position': {
                    'left': int(left_match.group(1)),
                    'top': int(top_match.group(1))
                }
            }
            colors.append(color_info)

    return colors


def save_to_json(colors, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(colors, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 读取HTML和CSS文件
    with open('1.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    with open('2.css', 'r', encoding='utf-8') as f:
        css_content = f.read()

    # 提取颜色信息
    colors = extract_colors(html_content, css_content)

    # 保存为JSON文件
    save_to_json(colors, 'japanese_colors.json')

    # 打印前几个颜色作为示例
    print("Extracted first few colors:")
    for color in colors[:3]:
        print(json.dumps(color, ensure_ascii=False, indent=2))