#! -*- coding:utf-8 -*-
# 自定义fit()训练过程

from itertools import cycle
from bert4torch.tokenizers import Tokenizer
from bert4torch.models import build_transformer_model, BaseModel
from bert4torch.snippets import sequence_padding, text_segmentate, ListDataset, ProgbarLogger
import torch.nn as nn
import torch
import torch.optim as optim
from torch.utils.data import DataLoader


maxlen = 128
batch_size = 16
config_path = 'F:/Projects/pretrain_ckpt/bert/[google_tf_base]--chinese_L-12_H-768_A-12/bert_config.json'
checkpoint_path = 'F:/Projects/pretrain_ckpt/bert/[google_tf_base]--chinese_L-12_H-768_A-12/pytorch_model.bin'
dict_path = 'F:/Projects/pretrain_ckpt/bert/[google_tf_base]--chinese_L-12_H-768_A-12/vocab.txt'

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)

# 加载数据集
class MyDataset(ListDataset):
    @staticmethod
    def load_data(filenames):
        """加载数据，并尽量划分为不超过maxlen的句子
        """
        D = []
        seps, strips = u'\n。！？!?；;，, ', u'；;，, '
        for filename in filenames:
            with open(filename, encoding='utf-8') as f:
                for l in f:
                    text, label = l.strip().split('\t')
                    for t in text_segmentate(text, maxlen - 2, seps, strips):
                        D.append((t, int(label)))
        return D

def collate_fn(batch):
    batch_token_ids, batch_segment_ids, batch_labels = [], [], []
    for text, label in batch:
        token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
        batch_token_ids.append(token_ids)
        batch_segment_ids.append(segment_ids)
        batch_labels.append([label])

    batch_token_ids = torch.tensor(sequence_padding(batch_token_ids), dtype=torch.long, device=device)
    batch_segment_ids = torch.tensor(sequence_padding(batch_segment_ids), dtype=torch.long, device=device)
    batch_labels = torch.tensor(batch_labels, dtype=torch.long, device=device)
    return [batch_token_ids, batch_segment_ids], batch_labels.flatten()

# 加载数据集
train_dataloader = DataLoader(MyDataset(['E:/Github/bert4torch/examples/datasets/sentiment/sentiment.train.data']), batch_size=batch_size, shuffle=True, collate_fn=collate_fn) 
valid_dataloader = DataLoader(MyDataset(['E:/Github/bert4torch/examples/datasets/sentiment/sentiment.valid.data']), batch_size=batch_size, collate_fn=collate_fn) 
test_dataloader = DataLoader(MyDataset(['E:/Github/bert4torch/examples/datasets/sentiment/sentiment.test.data']),  batch_size=batch_size, collate_fn=collate_fn) 

# 定义bert上的模型结构
class Model(BaseModel):
    def __init__(self) -> None:
        super().__init__()
        self.bert, self.config = build_transformer_model(config_path=config_path, checkpoint_path=checkpoint_path, with_pool=True, return_model_config=True)
        self.dropout = nn.Dropout(0.1)
        self.dense = nn.Linear(self.config['hidden_size'], 2)

    def forward(self, token_ids, segment_ids):
        _, pooled_output = self.bert([token_ids, segment_ids])
        output = self.dropout(pooled_output)
        output = self.dense(output)
        return output
    
    def fit(self, train_dataloader, steps_per_epoch, epochs=1):
        '''自定义fit过程：适用于自带fit()不满足需求时，用于自定义训练过程
        '''
        # 实现进度条展示功能，不需要可以不用
        bar = ProgbarLogger(epochs, steps_per_epoch, ['loss']) 
        global_step, epoch, best_val_acc  = 0, 0, 0
        
        train_dataloader = cycle(train_dataloader)
        self.train()
        for epoch in range(epochs):
            bar.on_epoch_begin(epoch=epoch)
            for bti in range(steps_per_epoch):
                bar.on_batch_begin()
                train_X, train_y = next(train_dataloader)
                output = self.forward(*train_X)
                loss = self.criterion(output, train_y)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()
                bar.on_batch_end(logs={'loss': loss.item()})  # 和上面定义bar时候一致
                global_step += 1
            bar.on_epoch_end()
            
            # 评估
            val_acc = evaluate(valid_dataloader)
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                # model.save_weights('best_model.pt')
            print(f'val_acc: {val_acc:.5f}, best_val_acc: {best_val_acc:.5f}\n')
            
model = Model().to(device)

# 定义使用的loss和optimizer，这里支持自定义
model.compile(
    loss=nn.CrossEntropyLoss(),
    optimizer=optim.Adam(model.parameters(), lr=2e-5),
)

# 定义评价函数
def evaluate(data):
    total, right = 0., 0.
    for x_true, y_true in data:
        y_pred = model.predict(x_true).argmax(axis=1)
        total += len(y_true)
        right += (y_true == y_pred).sum().item()
    return right / total


if __name__ == '__main__':
    model.fit(train_dataloader, epochs=20, steps_per_epoch=100)
