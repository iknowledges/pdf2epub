import argparse
import fitz

def extract_pages(input_pdf, output_pdf, start_page, end_page):
    """
    从PDF文件中提取指定页面范围并保存为新PDF
    
    参数：
    input_pdf: 输入PDF文件路径
    output_pdf: 输出PDF文件路径
    start_page: 起始页码（从0开始计数）
    end_page: 结束页码（包含在内，从0开始计数）
    """
    try:
        # 打开源PDF文件
        doc = fitz.open(input_pdf)
        
        # 验证页码范围
        if start_page < 0 or end_page >= len(doc) or start_page > end_page:
            print(f"页码范围无效。文档共有 {len(doc)} 页。")
            doc.close()
            return False
        
        # 创建新的PDF文档
        new_doc = fitz.open()
        
        # 复制指定页面范围
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        
        # 保存新PDF
        new_doc.save(output_pdf)
        
        # 关闭文档
        doc.close()
        new_doc.close()
        
        print(f"成功提取第 {start_page} 到 {end_page} 页，保存为：{output_pdf}")
        print(f"共提取了 {end_page - start_page + 1} 页")
        return True
        
    except Exception as e:
        print(f"处理PDF时出错：{e}")
        return False

def main():
    parser = argparse.ArgumentParser(prog='parse_pdf')
    parser.add_argument('filename')
    parser.add_argument('--start', default=0)
    parser.add_argument('--end', default=None)
    args = parser.parse_args()

    # 设置参数
    input_file = args.filename  # 输入PDF文件
    output_file = "output.pdf"  # 输出PDF文件
    start = int(args.start)  # 起始页码（从0开始）
    end = int(args.end)    # 结束页码（包含在内）
    
    # 提取页面
    extract_pages(input_file, output_file, start, end)


if __name__ == "__main__":
    main()