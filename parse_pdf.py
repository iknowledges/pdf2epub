import os
import sys
from pathlib import Path
from mineru.cli.common import do_parse, read_fn


def parse_doc(path_list: list[Path]):
    # 'ch', 'en'
    lang = "en"
    start_page_id = 0
    end_page_id = None
    formula_enable = True
    table_enable = True
    output_dir = "./output"
    # 'auto', 'txt', 'ocr'
    method = 'auto'
    backend = 'pipeline'
    server_url = None
    # 'huggingface', 'modelscope', 'local'
    model_source = 'local'

    if os.getenv('MINERU_MODEL_SOURCE', None) is None:
        os.environ['MINERU_MODEL_SOURCE'] = model_source
    try:
        file_name_list = []
        pdf_bytes_list = []
        lang_list = []
        for path in path_list:
            file_name = str(Path(path).stem)
            pdf_bytes = read_fn(path)
            file_name_list.append(file_name)
            pdf_bytes_list.append(pdf_bytes)
            lang_list.append(lang)
        do_parse(
            output_dir=output_dir,
            pdf_file_names=file_name_list,
            pdf_bytes_list=pdf_bytes_list,
            p_lang_list=lang_list,
            backend=backend,
            parse_method=method,
            formula_enable=formula_enable,
            table_enable=table_enable,
            server_url=server_url,
            start_page_id=start_page_id,
            end_page_id=end_page_id,
        )
    except Exception as e:
        print(e)

def main():
    if len(sys.argv) < 2:
        print("Please set a pdf file path!")
        return
    arg = sys.argv[1]
    file_path = Path(arg)
    parse_doc([file_path])


if __name__ == '__main__':
    main()
