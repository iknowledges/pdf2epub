import json
from pathlib import Path
from ebooklib import epub
import base64

def inline_equation(content):
    return '<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi></mi><mrow><mi>a</mi><mo>,</mo><mi>c</mi><mo>,</mo><mi>*</mi></mrow></msup><annotation encoding="application/x-tex">' + content + '</annotation></semantics></math>'

def interline_equation(content):
    return '<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>Q</mi><mi>%</mi></msub><mo>=</mo><mi>f</mi><mo stretchy="false" form="prefix">(</mo><mi>P</mi><mo stretchy="false" form="postfix">)</mo><mo>+</mo><mi>g</mi><mo stretchy="false" form="prefix">(</mo><mi>T</mi><mo stretchy="false" form="postfix">)</mo></mrow><annotation encoding="application/x-tex">' + content + '</annotation></semantics></math>'

def image_to_base64(image_path):
    image_root = Path("./demo2/auto/images")
    try:
        # 读取图片文件
        with open(image_root.joinpath(image_path), 'rb') as image_file:
            # 将图片转换为base64
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 获取图片格式
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif image_path.lower().endswith('.gif'):
            mime_type = 'image/gif'
        elif image_path.lower().endswith('.svg'):
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/jpeg'  # 默认
        
        # 生成HTML img标签
        html_img = f'<img role="img" src="data:{mime_type};base64,{base64_data}" />'
        return html_img
    except Exception as e:
        print(f"转换失败: {e}")
        return ''

def handle_title(block_lines):
    result = ''
    for line in block_lines:
        result += '<h1>'
        for span in line["spans"]:
            content = span["content"]
            result += content
        result += '</h1>'
    return result

def handle_text_spans(spans):
    result = ''
    for span in spans:
        span_type = span["type"]
        if 'text' == span_type:
            result += span["content"]
        elif 'inline_equation' == span_type:
            result += inline_equation(span["content"])
    return result

def handle_text_lines(lines):
    result = ''
    for line in lines:
        result += '<p>' + handle_text_spans(line["spans"]) + '</p>'
    return result

def handle_interline_equation(lines):
    result = ''
    for line in lines:
        result += '<p>'
        for span in line["spans"]:
            if 'interline_equation' == span["type"]:
                result += interline_equation(span['content'])
        result += '</p>'
    return result

def handle_image_blocks(blocks):
    result = '<p>'
    for block in blocks:
        block_type = block["type"]
        if 'image_body' == block_type:
            for line in block["lines"]:
                for span in line["spans"]:
                    result += image_to_base64(span["image_path"])
        elif 'image_caption' == block_type:
            for line in block["lines"]:
                for span in line["spans"]:
                    result += span["content"]
        result += '<br>'
    result += '</p>'
    return result

def handle_table_blocks(blocks):
    result = ''
    for block in blocks:
        if 'table_caption' == block["type"]:
            result += '<p>'
            for line in block["lines"]:
                for span in line["spans"]:
                    if 'text' == span["type"]:
                        result += span["content"]
            result += '</p>'
        elif 'table_body' == block["type"]:
            for line in block["lines"]:
                for span in line["spans"]:
                    if 'table' == span["type"]:
                        result += span["html"]
        elif 'table_footnote' == block["type"]:
            result += '<p>'
            for line in block["lines"]:
                for span in line["spans"]:
                    if 'text' == span["type"]:
                        result += span["content"]
            result += '</p>'
    return result

def handle_para_blocks(para_blocks):
    result = ""
    for block in para_blocks:
        block_type = block["type"]
        if 'title' == block_type:
            result += handle_title(block["lines"])
        elif 'text' == block_type:
            result += handle_text_lines(block["lines"])
        elif 'interline_equation' == block_type:
            result += handle_interline_equation(block["lines"])
        elif 'image' == block_type:
            result += handle_image_blocks(block["blocks"])
        elif 'table' == block_type:
            result += handle_table_blocks(block["blocks"])
    return result

def generate_epub(filename):
    with open(filename, 'r') as f:
        json_data = json.load(f)
    pdf_info = json_data["pdf_info"]

    book = epub.EpubBook()
    nav_list = ["nav"]
    for info in pdf_info:
        page_idx = info["page_idx"]
        para_blocks = handle_para_blocks(info["para_blocks"])

        c = epub.EpubHtml(title=f"page{page_idx}", file_name=f"page{page_idx}.xhtml", lang="en")
        c.content = str(para_blocks).encode("utf-8")
        book.add_item(c)
        nav_list.append(c)
        
    book.spine = nav_list
    # book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())
    output_file = filename.replace(".json", ".epub")
    epub.write_epub(output_file, book)

if __name__ == '__main__':
    generate_epub("./demo2/auto/demo2_middle.json")
