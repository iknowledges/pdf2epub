import os
import argparse
from pathlib import Path
from mineru.cli.common import do_parse, read_fn


def parse_doc(path_list: list[Path], start_page_id, end_page_id, lang):
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
    parser = argparse.ArgumentParser(prog='parse_pdf')
    parser.add_argument('filename')
    parser.add_argument('--start', default=0)
    parser.add_argument('--end', default=None)
    # 'ch', 'en'
    parser.add_argument('--lang', default='en')
    args = parser.parse_args()
    filename = Path(args.filename)
    parse_doc([filename], args.start, args.end, args.lang)


if __name__ == '__main__':
    main()
