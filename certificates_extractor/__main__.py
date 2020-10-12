from certificates_extractor.doc_parser import CertificateParser
import sys
import os 

folder = sys.argv[1] 

sub_folders = dict([(f.path,[]) for f in os.scandir(folder) if f.is_dir()])
for key in sub_folders:
    sub_folders[key].extend(os.listdir(key))

print(sub_folders)

for key in sub_folders:
    file_list = []
    mapping = None
    output_dir = key + '\\output'
    for f in sub_folders[key]:
        if 'mapping' in f:
            mapping = f
        elif '.xlsx' in f: 
            file_list.append(f)
        else:
            pass
    print(file_list)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for f in file_list: 
        output_file = f.replace('.xlsx','-result.xlsx')
        print(f)
        print(output_file)
        print(key + f'\\{mapping}')
        parser = CertificateParser(mapping = key + f'\\{mapping}')
        parser.create_import(input_path=key + f'\\{f}', output_path=output_dir + f'\\{output_file}')

# parser = CertificateParser()
# parser.create_import()

# parser = CertificateParser(mapping = '.\\input\\mapping2.xlsx')
# parser.create_import(input_path = '.\\input\\excel2.xlsx', output_path='.\\output\\import2.xlsx')