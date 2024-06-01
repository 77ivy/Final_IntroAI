import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
import transformers
import os
import csv

config = {
    'model_name': 'bert-base-chinese',
    'epoch': 20,
    'batch_size': 32,
    'lr': 1e-5,
    'seed': 1234,
    'maxlen': 500,
    'dropout': 0.3,
}

class BertClassifier(nn.Module):
    def __init__(self, dropout=None):
        super(BertClassifier, self).__init__()
        self.bert = transformers.BertModel.from_pretrained(config['model_name'])
        unfreeze_layers = ['layer.10', 'layer.11', 'pooler']
        for name, param in self.bert.named_parameters():
            param.requires_grad = False
            for layer in unfreeze_layers:
                if layer in name:
                    param.requires_grad = True
                    break
        self.dropout = dropout
        self.linear = nn.Linear(768, 2)

    def forward(self, input_ids, token_type_ids, attention_mask):
        output = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, return_dict=False)[1]
        if self.dropout is not None:
            output = F.dropout(output, p=self.dropout, training=self.training)
        output = self.linear(output)
        output = F.softmax(output, dim=1)
        return output





tokenizer = transformers.BertTokenizer.from_pretrained(config['model_name'])

# 載入訓練好的模型
model = BertClassifier(dropout=config['dropout'])
model.load_state_dict(torch.load('model.pth'))
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 設定公司名稱和資料夾路徑
semiconductor = ["半導體_台積電", "半導體_聯發科", "半導體_京元電子", "半導體_聯電", "半導體_矽統"]

Electronics = ["電子_佳能", "電子_群創", "電子_中環", "電子_友達", "電子_國碩"]



# for s in semiconductor:

def run_directory(company_name):
    results = []

    folder_path = f"/home/kkerstin/Final_IntroAI/BERT/news_data/{company_name}"

    # 遍歷資料夾
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            positive_score = 0.5
            negative_score = 0.5
        else:
            inputs = tokenizer(
                text,
                max_length=config['maxlen'],
                truncation=True,
                padding='max_length',
                return_tensors='pt'
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = model(**inputs)
            positive_score = outputs[:, 1].item()
            negative_score = outputs[:, 0].item()
        date = filename.split("News.txt")[0]
        results.append([date, positive_score, negative_score])
    return results, company_name


def output(results, company_name):
    # 寫入 CSV
    output_filename = f"result_{company_name}.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Name", "Positive Score", "Negative Score"])

        sorted_results = sorted(results, key=lambda x: x[0])
        writer.writerows(sorted_results)

    print(f"Results saved to {output_filename}")

def run_for_all_companies(industry):
    for company in industry:
        results, company_name = run_directory(company)
        output(results, company_name)

def run_for_one_company(company_name):
    results, company_name = run_directory(company_name)
    output(results, company_name)


run_for_all_companies(Electronics)