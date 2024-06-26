import jieba
import os

# 创建停用词列表
def stopwordslist(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        stopwords = [line.strip() for line in file.readlines()]
    return stopwords

# 对句子进行分词
def seg_sentence(sentence, stopwords):
    sentence_seged = jieba.cut(sentence.strip())
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    return outstr

# 设置文件路径
stopwords_file_path = r'C:\Users\ivy42\Downloads\LDA_totoal\code\stopWords\1893（utf8）.txt'
input_dir = r'C:\Users\ivy42\Downloads\電子_國碩-20240531T092306Z-001\電子_國碩'
output_dir = 'output1_國碩'
os.makedirs(output_dir, exist_ok=True)

# 加载停用词
stopwords = stopwordslist(stopwords_file_path)

# 遍历输入文件夹中的所有文件
for filename in os.listdir(input_dir):
    input_filepath = os.path.join(input_dir, filename)
    
    # 检查是否为文件
    if os.path.isfile(input_filepath):
        try:
            with open(input_filepath, 'r', encoding='utf-8') as inputs:
                output_filepath = os.path.join(output_dir, f'processed_{filename}')
                with open(output_filepath, 'w', encoding='utf-8') as outputs:
                    for line in inputs:
                        line_seg = seg_sentence(line, stopwords)  # 这里的返回值是字符串
                        outputs.write(line_seg + '\n')
            print(f"Processed file: {input_filepath}")
        except Exception as e:
            print(f"Failed to process file: {input_filepath}, error: {e}")
    else:
        print(f"Skipping non-file: {input_filepath}")

print("Processing completed.")
