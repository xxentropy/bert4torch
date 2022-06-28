# sequence_labeling
- 人民日报数据集+bert预训练模型
- valid集指标

| solution | epoch | f1_token | f1_entity | comment | 
| ---- | ---- | ---- | ---- | ---- | 
| bert+crf | 4/20 | 97.06 | 95.90 | —— | 
| bert+crf+init | 4/20 | 97.35 | 96.42 | 用训练数据初始化crf权重 | 
| bert+crf+freeze | 10/20 | 97.15 | 95.92 | 用训练数据生成crf权重(不训练) | 
| bert+cascade+crf | 15/20 | 98.11 | 96.23 | crf类别少所以f1_token偏高 | 
| bert+posseg+crf | 8/20 | 97.30 | 96.09 | 加了词性输入 | 
| bert+global_pointer | 18/20 | —— | 95.66 | —— | 
| bert+efficient_global_pointer | 17/20 | —— | 96.55 | —— | 
| bert+mrc | 7/20 | —— | 95.75 | —— |
| bert+span | 13/20 | —— | 96.31 | —— |
| bert+tplinker_plus | 20/20 | —— | 95.71 | 长度限制明显 |


# sentence_embedding
## unsupervised
- bert预训练模型+无监督finetune
- 五个中文数据集+5个epoch取最优值
- 继续finetune, 部分数据集有小幅提升
- 实验显示dropout_rate对结果影响较大

|     solution    |   ATEC  |  BQ  |  LCQMC  |  PAWSX  |  STS-B  |   comment   |
|       ----      |   ----  | ---- |   ----  |   ----  |   ----  |     ----    |
|        CT       |  30.65  | 44.50|  68.67  |  16.20  |  69.27  | dropout=0.1, 收敛慢跑了10个epoch |
| CT_In_Batch_Neg |  32.47  | 47.09|  68.56  |  27.50  |  74.00  | dropout=0.1 |
|       TSDAE     |    ——   | 46.65|  65.30  |  12.54  |    ——   | dropout=0.1, ——表示该指标异常未记录 |
|      SimCSE     |  33.90  | 50.29|  71.81  |  13.14  |  71.09  | dropout=0.3 |
|      ESimCSE    |  34.05  | 50.54|  71.58  |  12.53  |  71.27  | dropout=0.3 |
|    PromptBert   |  33.98  | 49.89|  73.18  |  13.30  |  73.42  | dropout=0.3 |

## supervised
待整理

# sentence_classfication
- 情感分类数据集+cls位分类

| solution | epoch | valid_acc | test_acc | comment | 
| ---- | ---- | ---- | ---- | ---- | 
| albert_small | 10/10 | 94.46 | 93.98 | small版本 | 
| bert | 6/10 | 94.72 | 94.11 | —— | 
| nezha | 7/10 | 95.07 | 94.72 | —— | 
| xlnet | 6/10 | 95.00 | 94.24 | —— | 
| electra | 10/10 | 94.94 | 94.78 | —— | 
| roformer | 9/10 | 94.85 | 94.42 | —— | 
| roformer_v2 | 3/10 | 95.78 | 96.09 | —— | 
| gau_alpha | 2/10 | 95.25 | 94.46 | —— | 