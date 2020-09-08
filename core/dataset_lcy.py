import numpy as np
import scipy.misc
import os
from PIL import Image
from torchvision import transforms
from config import INPUT_SIZE

import imageio
from tqdm import tqdm

import pdb
import os.path as osp

class CUB():
    def __init__(self, root, is_train=True, data_len=None, center_crop=False):
        self.root = root
        self.is_train = is_train
        img_txt_file = open(os.path.join(self.root, 'images.txt'))
        label_txt_file = open(os.path.join(self.root, 'image_class_labels.txt'))
        train_val_file = open(os.path.join(self.root, 'train_test_split.txt'))
        bad_img_file = os.path.join(self.root, 'bad_imgs_list.txt')
        has_bad_imgs = False
        if os.path.isfile(bad_img_file):
            has_bad_imgs = True
            with open(bad_img_file, 'r') as f:
                lines = f.readlines()
                bad_imgs = [x.strip() for x in lines]

        if not has_bad_imgs:
            img_name_list = []
            for line in img_txt_file:
                img_name_list.append(line[:-1].split(' ')[-1])
            label_list = []
            for line in label_txt_file:
                label_list.append(int(line[:-1].split(' ')[-1]) - 1)
            train_test_list = []
            for line in train_val_file:
                train_test_list.append(int(line[:-1].split(' ')[-1]))
            train_file_list = [x for i, x in zip(train_test_list, img_name_list) if i]
            test_file_list = [x for i, x in zip(train_test_list, img_name_list) if not i]
            # if self.is_train:
            #     self.train_img = [scipy.misc.imread(os.path.join(self.root, 'images', train_file)) for train_file in
            #                       train_file_list[:data_len]]
            #     self.train_label = [x for i, x in zip(train_test_list, label_list) if i][:data_len]
            # if not self.is_train:
            #     self.test_img = [scipy.misc.imread(os.path.join(self.root, 'images', test_file)) for test_file in
            #                      test_file_list[:data_len]]
            #     self.test_label = [x for i, x in zip(train_test_list, label_list) if not i][:data_len]
            if self.is_train:
                self.train_img = [imageio.imread(os.path.join(self.root, 'images', train_file)) for train_file in
                                  tqdm(train_file_list[:data_len])]
                self.train_label = [x for i, x in zip(train_test_list, label_list) if i][:data_len]
            if not self.is_train:
                self.test_img = [imageio.imread(os.path.join(self.root, 'images', test_file)) for test_file in
                                 tqdm(test_file_list[:data_len])]
                self.test_label = [x for i, x in zip(train_test_list, label_list) if not i][:data_len]
        else:
            img_name_list = []
            for line in img_txt_file:
                img_name_list.append(line[:-1].split(' ')[-1])
            label_list = []
            for line in label_txt_file:
                label_list.append(int(line[:-1].split(' ')[-1]) - 1)
            train_test_list = []
            for line in train_val_file:
                train_test_list.append(int(line[:-1].split(' ')[-1]))
            
            # Skip the bad imgs
            bad_imgs_ids = []
            for bad_img in bad_imgs:
                img_id = img_name_list.index(bad_img)
                bad_imgs_ids.append(img_id)
            bad_imgs_ids = sorted(bad_imgs_ids)

            img_name_list = [x for i, x in enumerate(img_name_list) if i not in bad_imgs_ids]
            label_list = [x for i, x in enumerate(label_list) if i not in bad_imgs_ids]
            train_test_list = [x for i, x in enumerate(train_test_list) if i not in bad_imgs_ids]


            train_file_list = [x for i, x in zip(train_test_list, img_name_list) if i]
            test_file_list = [x for i, x in zip(train_test_list, img_name_list) if not i]
            if self.is_train:
                self.train_img = [imageio.imread(os.path.join(self.root, 'images', train_file)) for train_file in
                                  tqdm(train_file_list[:data_len])]
                self.train_label = [x for i, x in zip(train_test_list, label_list) if i][:data_len]
            if not self.is_train:
                self.test_img = [imageio.imread(os.path.join(self.root, 'images', test_file)) for test_file in
                                 tqdm(test_file_list[:data_len])]
                self.test_label = [x for i, x in zip(train_test_list, label_list) if not i][:data_len]

            if center_crop:
                print("_"*50, "Use center crop.")
                if self.is_train:
                    img_list = self.train_img
                    file_list = train_file_list[:data_len]
                else:
                    img_list = self.test_img
                    file_list = test_file_list[:data_len]

                crop_img_list = []

                for img_path, img in zip(file_list, img_list):
                    dst_img_path = osp.join(vis_root_dir, img_path)
                    crop_size = int(min(img.shape[:2]) / 2)
                    h_0 = int((img.shape[0] - crop_size) / 2)
                    h_1 = int((img.shape[0] + crop_size) / 2)
                    w_0 = int((img.shape[1] - crop_size) / 2)
                    w_1 = int((img.shape[1] + crop_size) / 2)

                    crop_img = img[h_0:h_1, w_0:w_1, :]

                    crop_img_list.append(crop_img)

                if self.is_train:
                    self.train_img = crop_img_list
                else:
                    self.test_img = crop_img_list






                

    def __getitem__(self, index):
        if self.is_train:
            img, target = self.train_img[index], self.train_label[index]
            if len(img.shape) == 2:
                img = np.stack([img] * 3, 2)
            img = Image.fromarray(img, mode='RGB')
            img = transforms.Resize((600, 600), Image.BILINEAR)(img)
            img = transforms.RandomCrop(INPUT_SIZE)(img)
            img = transforms.RandomHorizontalFlip()(img)
            img = transforms.ToTensor()(img)
            img = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(img)

        else:
            img, target = self.test_img[index], self.test_label[index]
            if len(img.shape) == 2:
                img = np.stack([img] * 3, 2)
            img = Image.fromarray(img, mode='RGB')
            img = transforms.Resize((600, 600), Image.BILINEAR)(img)
            img = transforms.CenterCrop(INPUT_SIZE)(img)
            img = transforms.ToTensor()(img)
            img = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(img)

        return img, target

    def __len__(self):
        if self.is_train:
            return len(self.train_label)
        else:
            return len(self.test_label)


if __name__ == '__main__':
    dataset = CUB(root='./CUB_200_2011')
    print(len(dataset.train_img))
    print(len(dataset.train_label))
    for data in dataset:
        print(data[0].size(), data[1])
    dataset = CUB(root='./CUB_200_2011', is_train=False)
    print(len(dataset.test_img))
    print(len(dataset.test_label))
    for data in dataset:
        print(data[0].size(), data[1])
