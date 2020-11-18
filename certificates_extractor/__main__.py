from certificates_extractor.doc_parser import CertificateParser
import sys
import os 


input_arg = sys.argv[1] 
output_arg = sys.argv[2] if len(sys.argv) > 2 else None
log_name = sys.argv[3] if len(sys.argv) > 2 else None

sub_folders = dict([(f.path,[]) for f in os.scandir(input_arg) if f.is_dir()])
for key in sub_folders:
    sub_folders[key].extend(os.listdir(key))

if output_arg:
    for key in sub_folders:
        dir_name = output_arg + f'\\{os.path.basename(os.path.normpath(key))}'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

print(sub_folders)

for key in sub_folders:
    file_list = []
    mapping = None
    output_dir = output_arg + f'\\{os.path.basename(os.path.normpath(key))}' if output_arg else key + '\\output'
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
        print(f)
        print(key + f'\\{mapping}')
        parser = CertificateParser(mapping = key + f'\\{mapping}', log_name = log_name)
        parser.create_import(input_path=key + f'\\{f}', output_path=output_dir + '\\')

# parser = CertificateParser()
# parser.create_import()

# parser = CertificateParser(mapping = '.\\input\\mapping2.xlsx')
# parser.create_import(input_path = '.\\input\\excel2.xlsx', output_path='.\\output\\import2.xlsx')