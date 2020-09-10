import os
from torch.autograd import Variable
import torch.utils.data
from torch.nn import DataParallel
# from config import BATCH_SIZE, PROPOSAL_NUM, test_model
from config_lcy import BATCH_SIZE, PROPOSAL_NUM, test_model
from core import model, dataset_lcy
from core.utils import progress_bar

import pdb
from collections import defaultdict 

# os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3'
if not test_model:
    raise NameError('please set the test_model file to choose the checkpoint!')
# read dataset
# testset = dataset.CUB(root='./dami', is_train=False, data_len=None)
# testset = dataset.CUB(root='./dami', is_train=False, data_len=10)
testset = dataset_lcy.CUB(root='./dami', is_train=False, data_len=None, center_crop=False)
# testset = dataset_lcy.CUB(root='./dami_test', is_train=False, data_len=None, center_crop=False)


testloader = torch.utils.data.DataLoader(testset, batch_size=BATCH_SIZE,
                                         shuffle=False, num_workers=8, drop_last=False)
# define model
net = model.attention_net(topN=PROPOSAL_NUM)
ckpt = torch.load(test_model)
net.load_state_dict(ckpt['net_state_dict'])
net = net.cuda()
net = DataParallel(net)
creterion = torch.nn.CrossEntropyLoss()


gt_num_dict = defaultdict(int)
pred_num_dict = defaultdict(int)
correct_num_dict = defaultdict(int)



# evaluate on test set
test_loss = 0
test_correct = 0
total = 0
net.eval()


for i, data in enumerate(testloader):
    with torch.no_grad():
        img, label = data[0].cuda(), data[1].cuda()
        batch_size = img.size(0)
        # pdb.set_trace()
        _, concat_logits, _, _, _ = net(img)
        # calculate loss
        concat_loss = creterion(concat_logits, label)
        # calculate accuracy
        _, concat_predict = torch.max(concat_logits, 1)
        # pdb.set_trace()

        for j in range(batch_size):
            gt = int(label[j])
            pred = int(concat_predict[j])
            gt_num_dict[gt] += 1
            pred_num_dict[pred] += 1
            if gt == pred:
                correct_num_dict[gt] += 1

        total += batch_size
        test_correct += torch.sum(concat_predict.data == label.data)
        test_loss += concat_loss.item() * batch_size
        progress_bar(i, len(testloader), 'eval on test set')


# pdb.set_trace()
print("GT Number: {}".format(gt_num_dict))
for i in range(4):
    precision = correct_num_dict[i] / pred_num_dict[i]
    recall = correct_num_dict[i] / gt_num_dict[i]
    print(f"Cls {i}, precision: {precision}, recall: {recall}.")



test_acc = float(test_correct) / total
test_loss = test_loss / total
print('test set loss: {:.3f} and test set acc: {:.3f} total sample: {}'.format(test_loss, test_acc, total))

print('finishing testing')
