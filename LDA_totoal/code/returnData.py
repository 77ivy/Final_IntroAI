import os

def read_files_to_list(folder_path):
    
    big_list = []

    
    filenames = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    filenames.sort(key=lambda x: int(x.split('_')[0]))

    
    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        
        
        #print(f"Processing file: {filename}")
        
        
        with open(file_path, 'r') as file:
            small_list = [line.strip() for line in file]
            big_list.append(small_list)
    #print(big_list)
    return big_list


folder_path = r'C:\Users\ivy42\Downloads\LDA_totoal\code\model\output_twords'
result = read_files_to_list(folder_path)
#print(result)
