import sys
import json
import base64
from pathlib import Path
from typing import Any, List
from ebooklib import epub


def inline_equation(content: str) -> str:
    return '<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi></mi><mrow><mi>a</mi><mo>,</mo><mi>c</mi><mo>,</mo><mi>*</mi></mrow></msup><annotation encoding="application/x-tex">' + content + '</annotation></semantics></math>'

def interline_equation(content: str) -> str:
    return '<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>Q</mi><mi>%</mi></msub><mo>=</mo><mi>f</mi><mo stretchy="false" form="prefix">(</mo><mi>P</mi><mo stretchy="false" form="postfix">)</mo><mo>+</mo><mi>g</mi><mo stretchy="false" form="prefix">(</mo><mi>T</mi><mo stretchy="false" form="postfix">)</mo></mrow><annotation encoding="application/x-tex">' + content + '</annotation></semantics></math>'

def image_to_base64(image_path: str, root_path: Path) -> str:
    file_path = root_path.joinpath("images").joinpath(image_path)
    try:
        # 读取图片文件
        with open(file_path, 'rb') as image_file:
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

def handle_title(block_lines: List) -> str:
    result = ''
    for line in block_lines:
        result += '<h1>'
        for span in line["spans"]:
            content = span["content"]
            result += content
        result += '</h1>'
    return result

def handle_text_spans(spans: List) -> str:
    result = ''
    for span in spans:
        span_type = span["type"]
        if 'text' == span_type:
            result += span["content"]
        elif 'inline_equation' == span_type:
            result += inline_equation(span["content"])
    return result

def handle_text_lines(lines: List) -> str:
    result = ''
    for line in lines:
        result += '<p>' + handle_text_spans(line["spans"]) + '</p>'
    return result

def handle_interline_equation(lines: List) -> str:
    result = ''
    for line in lines:
        result += '<p>'
        for span in line["spans"]:
            if 'interline_equation' == span["type"]:
                result += interline_equation(span['content'])
        result += '</p>'
    return result

def handle_image_blocks(blocks, root_path: Path) -> str:
    result = '<p>'
    for block in blocks:
        block_type = block["type"]
        if 'image_body' == block_type:
            for line in block["lines"]:
                for span in line["spans"]:
                    result += image_to_base64(span["image_path"], root_path)
        elif 'image_caption' == block_type:
            for line in block["lines"]:
                for span in line["spans"]:
                    result += span["content"]
        result += '<br>'
    result += '</p>'
    return result

def handle_table_blocks(blocks) -> str:
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

def handle_para_blocks(para_blocks: List, root_path: Path) -> str:
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
            result += handle_image_blocks(block["blocks"], root_path)
        elif 'table' == block_type:
            result += handle_table_blocks(block["blocks"])
    return result

def read_pdf_info(filename: Path) -> List:
    with open(filename, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data["pdf_info"]

def read_css() -> str:
    with open("nav.css", 'r', encoding='utf-8') as f:
        css = f.read()
    return css

def generate_epub(filename: Path) -> None:
    pdf_info = read_pdf_info(filename)

    book = epub.EpubBook()
    toc_list = []
    nav_list: List[Any] = ["nav"]
    for info in pdf_info:
        page_idx = info["page_idx"]
        para_blocks = handle_para_blocks(info["para_blocks"], filename.parent)
        if para_blocks.strip() != "":
            page_title = f"page{page_idx}"
            page_file = f"page{page_idx}.xhtml"
            c = epub.EpubHtml(title=page_title, file_name=page_file, lang="en")
            c.content = para_blocks
            book.add_item(c)
            toc_list.append(epub.Link(page_file, str(page_idx + 1), page_title))
            nav_list.append(c)

    css_content = read_css()
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=css_content,
    )
    book.add_item(nav_css)

    book.toc = toc_list
    book.spine = nav_list
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    output_file = filename.with_suffix(".epub")
    epub.write_epub(output_file, book)

def main():
    if len(sys.argv) < 2:
        print("Please set the middle json file!")
        return
    generate_epub(Path(sys.argv[1]))

if __name__ == '__main__':
    main()
