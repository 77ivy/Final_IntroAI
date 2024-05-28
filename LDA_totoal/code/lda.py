#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import os

# 參數設置
alpha = 0.1
beta = 0.1
K = 10
iter_num = 50
top_words = 20

input_folder = r'C:\Users\ivy42\Downloads\LDA_totoal\output1'
output_folder = r'C:\Users\ivy42\Downloads\LDA_totoal\code\model'

class Document(object):
    def __init__(self):
        self.words = []
        self.length = 0

class Dataset(object):
    def __init__(self):
        self.M = 0
        self.V = 0
        self.docs = []
        self.word2id = {}
        self.id2word = {}

    def writewordmap(self, wordmapfile):
        with open(wordmapfile, 'w', encoding='utf-8') as f:
            for k, v in self.word2id.items():
                f.write(k + '\t' + str(v) + '\n')

class Model(object):
    def __init__(self, dset, modelfile_suffix):
        self.dset = dset
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iter_num = iter_num
        self.top_words = top_words
        self.modelfile_suffix = modelfile_suffix

        self.p = []
        self.Z = []
        self.nw = []
        self.nwsum = []
        self.nd = []
        self.ndsum = []
        self.theta = []
        self.phi = []

    def init_est(self):
        self.p = [0.0 for _ in range(self.K)]
        self.nw = [[0 for _ in range(self.K)] for _ in range(self.dset.V)]
        self.nwsum = [0 for _ in range(self.K)]
        self.nd = [[0 for _ in range(self.K)] for _ in range(self.dset.M)]
        self.ndsum = [0 for _ in range(self.dset.M)]
        self.Z = [[] for _ in range(self.dset.M)]
        for x in range(self.dset.M):
            self.Z[x] = [0 for _ in range(self.dset.docs[x].length)]
            self.ndsum[x] = self.dset.docs[x].length
            for y in range(self.dset.docs[x].length):
                topic = random.randint(0, self.K - 1)
                self.Z[x][y] = topic
                self.nw[self.dset.docs[x].words[y]][topic] += 1
                self.nd[x][topic] += 1
                self.nwsum[topic] += 1
        self.theta = [[0.0 for _ in range(self.K)] for _ in range(self.dset.M)]
        self.phi = [[0.0 for _ in range(self.dset.V)] for _ in range(self.K)]

    def estimate(self):
        print('Sampling %d iterations!' % self.iter_num)
        for x in range(self.iter_num):
            print('Iteration %d ...' % (x + 1))
            for i in range(len(self.dset.docs)):
                for j in range(self.dset.docs[i].length):
                    topic = self.sampling(i, j)
                    self.Z[i][j] = topic
        print('End sampling.')
        print('Compute theta...')
        self.compute_theta()
        print('Compute phi...')
        self.compute_phi()
        print('Saving model...')
        self.save_model()

    def sampling(self, i, j):
        topic = self.Z[i][j]
        wid = self.dset.docs[i].words[j]
        self.nw[wid][topic] -= 1
        self.nd[i][topic] -= 1
        self.nwsum[topic] -= 1
        self.ndsum[i] -= 1

        Vbeta = self.dset.V * self.beta
        Kalpha = self.K * self.alpha

        for k in range(self.K):
            self.p[k] = (self.nw[wid][k] + self.beta) / (self.nwsum[k] + Vbeta) * \
                        (self.nd[i][k] + alpha) / (self.ndsum[i] + Kalpha)
        for k in range(1, self.K):
            self.p[k] += self.p[k - 1]
        u = random.uniform(0, self.p[self.K - 1])
        for topic in range(self.K):
            if self.p[topic] > u:
                break
        self.nw[wid][topic] += 1
        self.nwsum[topic] += 1
        self.nd[i][topic] += 1
        self.ndsum[i] += 1
        return topic

    def compute_theta(self):
        for x in range(self.dset.M):
            for y in range(self.K):
                self.theta[x][y] = (self.nd[x][y] + self.alpha) / (self.ndsum[x] + self.K * self.alpha)

    def compute_phi(self):
        for x in range(self.K):
            for y in range(self.dset.V):
                self.phi[x][y] = (self.nw[y][x] + self.beta) / (self.nwsum[x] + self.dset.V * self.beta)

    def save_model(self):
        output_paths = {
            'theta': os.path.join(output_folder, 'output_theta'),
            'phi': os.path.join(output_folder, 'output_phi'),
            'twords': os.path.join(output_folder, 'output_twords'),
            'tassign': os.path.join(output_folder, 'output_tassign'),
            'others': os.path.join(output_folder, 'output_others')
        }

        for path in output_paths.values():
            if not os.path.exists(path):
                os.makedirs(path)

        with open(os.path.join(output_paths['theta'], self.modelfile_suffix + '_theta.txt'), 'w', encoding='utf-8') as ftheta:
            for x in range(self.dset.M):
                for y in range(self.K):
                    ftheta.write(str(self.theta[x][y]) + ' ')
                ftheta.write('\n')

        with open(os.path.join(output_paths['phi'], self.modelfile_suffix + '_phi.txt'), 'w', encoding='utf-8') as fphi:
            for x in range(self.K):
                for y in range(self.dset.V):
                    fphi.write(str(self.phi[x][y]) + ' ')
                fphi.write('\n')

        with open(os.path.join(output_paths['twords'], self.modelfile_suffix + '_twords.txt'), 'w', encoding='utf-8') as ftwords:
            if self.top_words > self.dset.V:
                self.top_words = self.dset.V
            for x in range(self.K):
                #ftwords.write('Topic ' + str(x) + 'th:\n')
                topic_words = []
                for y in range(self.dset.V):
                    topic_words.append((y, self.phi[x][y]))
                topic_words.sort(key=lambda x: x[1], reverse=True)
                total=0  
                for y in range(self.top_words):
                    total+=topic_words[y][1]/self.top_words
                    word = self.dset.id2word[topic_words[y][0]]
                ftwords.write(str(total) + '\n')
                
        with open(os.path.join(output_paths['tassign'], self.modelfile_suffix + '_tassign.txt'), 'w', encoding='utf-8') as ftassign:
            for x in range(self.dset.M):
                for y in range(self.dset.docs[x].length):
                    ftassign.write(str(self.dset.docs[x].words[y]) + ':' + str(self.Z[x][y]) + ' ')
                ftassign.write('\n')

        with open(os.path.join(output_paths['others'], self.modelfile_suffix + '_others.txt'), 'w', encoding='utf-8') as fothers:
            fothers.write('alpha = ' + str(self.alpha) + '\n')
            fothers.write('beta = ' + str(self.beta) + '\n')
            fothers.write('ntopics = ' + str(self.K) + '\n')
            fothers.write('ndocs = ' + str(self.dset.M) + '\n')
            fothers.write('nwords = ' + str(self.dset.V) + '\n')
            fothers.write('liter = ' + str(self.iter_num) + '\n')

def read_files_in_folder(folder_path):
    files = os.listdir(folder_path)
    txt_files = [f for f in files if f.endswith('.txt')]
    return [os.path.join(folder_path, f) for f in txt_files]

def lda_on_folder(folder_path):
    txt_files = read_files_in_folder(folder_path)
    for i, txt_file in enumerate(txt_files):
        modelfile_suffix = str(i + 1)
        dset = read_trn_file(txt_file, modelfile_suffix)
        model = Model(dset, modelfile_suffix)
        model.init_est()
        model.estimate()

def read_trn_file(trnfile, modelfile_suffix):
    print(f'Reading train data from {trnfile}...')
    with open(trnfile, 'r', encoding='utf-8') as f:
        docs = f.readlines()

    dset = Dataset()
    items_idx = 0
    for line in docs:
        if line.strip() != "":
            tmp = line.strip().split()
            doc = Document()
            for item in tmp:
                if item in dset.word2id:
                    doc.words.append(dset.word2id[item])
                else:
                    dset.word2id[item] = items_idx
                    dset.id2word[items_idx] = item
                    doc.words.append(items_idx)
                    items_idx += 1
            doc.length = len(tmp)
            dset.docs.append(doc)
    dset.M = len(dset.docs)
    dset.V = len(dset.word2id)
    print(f'There are {dset.M} documents')
    print(f'There are {dset.V} items')
    wordmapfile = os.path.join(output_folder, f'{modelfile_suffix}_wordmap.txt')
    print(f'Saving wordmap file to {wordmapfile}...')
    dset.writewordmap(wordmapfile)
    return dset

def lda():
    lda_on_folder(input_folder)

if __name__ == '__main__':
    lda()
