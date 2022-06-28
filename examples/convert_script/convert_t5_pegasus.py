# t5_pegasus从tf转为bert4torch适配的pytorch版本
import torch
import tensorflow as tf
import json

# small
# tf_dir = 'F:/Projects/pretrain_ckpt/t5/[sushen_t5_pegasus_tf_small]--chinese_t5_pegasus_small/'
# torch_path = 'F:/Projects/pretrain_ckpt/t5/[sushen_t5_pegasus_torch_small]--chinese_t5_pegasus_small/pytorch_model.bin'

# base:
tf_dir = 'F:/Projects/pretrain_ckpt/t5/[sushen_t5_pegasus_tf_base]--chinese_t5_pegasus_base/'
torch_path = 'F:/Projects/pretrain_ckpt/t5/[sushen_t5_pegasus_torch_base]--chinese_t5_pegasus_base/pytorch_model.bin'


tf_path = tf_dir + 'model.ckpt'
with open(tf_dir + 'config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
num_layers = config['num_hidden_layers']
torch_state_dict = {}

mapping = {
'shared/embedding': 'shared.weight',
'encoder/block_000/layer_000/SelfAttention/relative_attention_bias': 'encoder.block.0.layer.0.SelfAttention.relative_attention_bias.weight##T', # 自定义标记，##T结尾表示要转置
'encoder/rms_norm/scale': 'encoder.final_layer_norm.weight',
'decoder/block_000/layer_000/SelfAttention/relative_attention_bias': 'decoder.block.0.layer.0.SelfAttention.relative_attention_bias.weight##T',
'decoder/rms_norm/scale': 'decoder.final_layer_norm.weight',
'decoder/logits/kernel': 'lm_head.weight##T'
}


for i in range(num_layers):
    i1 = str(i).rjust(3, '0')
    mapping.update({
        f'encoder/block_{i1}/layer_000/SelfAttention/q': f'encoder.block.{i}.layer.0.SelfAttention.q.weight##T',
        f'encoder/block_{i1}/layer_000/SelfAttention/k': f'encoder.block.{i}.layer.0.SelfAttention.k.weight##T',
        f'encoder/block_{i1}/layer_000/SelfAttention/v': f'encoder.block.{i}.layer.0.SelfAttention.v.weight##T',
        f'encoder/block_{i1}/layer_000/SelfAttention/o': f'encoder.block.{i}.layer.0.SelfAttention.o.weight##T',
        f'encoder/block_{i1}/layer_000/rms_norm/scale': f'encoder.block.{i}.layer.0.layer_norm.weight',
        f'encoder/block_{i1}/layer_001/DenseReluDense/wi_0/kernel': f'encoder.block.{i}.layer.1.DenseReluDense.wi_0.weight##T',
        f'encoder/block_{i1}/layer_001/DenseReluDense/wi_1/kernel': f'encoder.block.{i}.layer.1.DenseReluDense.wi_1.weight##T',
        f'encoder/block_{i1}/layer_001/DenseReluDense/wo/kernel': f'encoder.block.{i}.layer.1.DenseReluDense.wo.weight##T',
        f'encoder/block_{i1}/layer_001/rms_norm/scale': f'encoder.block.{i}.layer.1.layer_norm.weight',
        f'decoder/block_{i1}/layer_000/SelfAttention/q': f'decoder.block.{i}.layer.0.SelfAttention.q.weight##T',
        f'decoder/block_{i1}/layer_000/SelfAttention/k': f'decoder.block.{i}.layer.0.SelfAttention.k.weight##T',
        f'decoder/block_{i1}/layer_000/SelfAttention/v': f'decoder.block.{i}.layer.0.SelfAttention.v.weight##T',
        f'decoder/block_{i1}/layer_000/SelfAttention/o': f'decoder.block.{i}.layer.0.SelfAttention.o.weight##T',
        f'decoder/block_{i1}/layer_000/rms_norm/scale': f'decoder.block.{i}.layer.0.layer_norm.weight',
        f'decoder/block_{i1}/layer_001/EncDecAttention/q': f'decoder.block.{i}.layer.1.EncDecAttention.q.weight##T',
        f'decoder/block_{i1}/layer_001/EncDecAttention/k': f'decoder.block.{i}.layer.1.EncDecAttention.k.weight##T',
        f'decoder/block_{i1}/layer_001/EncDecAttention/v': f'decoder.block.{i}.layer.1.EncDecAttention.v.weight##T',
        f'decoder/block_{i1}/layer_001/EncDecAttention/o': f'decoder.block.{i}.layer.1.EncDecAttention.o.weight##T',
        f'decoder/block_{i1}/layer_001/rms_norm/scale': f'decoder.block.{i}.layer.1.layer_norm.weight',
        f'decoder/block_{i1}/layer_002/DenseReluDense/wi_0/kernel': f'decoder.block.{i}.layer.2.DenseReluDense.wi_0.weight##T',
        f'decoder/block_{i1}/layer_002/DenseReluDense/wi_1/kernel': f'decoder.block.{i}.layer.2.DenseReluDense.wi_1.weight##T',
        f'decoder/block_{i1}/layer_002/DenseReluDense/wo/kernel': f'decoder.block.{i}.layer.2.DenseReluDense.wo.weight##T',
        f'decoder/block_{i1}/layer_002/rms_norm/scale': f'decoder.block.{i}.layer.2.layer_norm.weight',
    })

transpose_layers = ['']
for k, v in mapping.items():
    ts = torch.from_numpy(tf.train.load_variable(tf_path, k))
    # if len(ts.shape)==2 and ts.shape[0] == ts.shape[1]:
    #     print(k, v)

    if v.endswith('##T'):
        torch_state_dict[v.rstrip('##T')] = ts.T
    else:
        torch_state_dict[v] = ts

torch.save(torch_state_dict, torch_path)
