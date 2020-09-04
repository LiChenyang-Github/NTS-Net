# -*- coding: utf-8 -*-
# @Author: lee.lcy
# @Date:   2020-09-04 07:55:13
# @Last Modified by:   lee.lcy
# @Last Modified time: 2020-09-04 08:06:08


import os
import shutil

import os.path as osp


def rewrite_img():
"""
Rewrite the img and replace the ' ' with '_'    
"""
    src_img_root_dir = "/mnt/data2/lee.lcy/Datasets/dami/data/images/"
    dst_img_root_dir = "/mnt/data2/lee.lcy/Datasets/dami/NTS_DATA/images/"

    dataset_names = os.listdir(src_img_root_dir)


    for dataset_name in dataset_names:
        src_dataset_dir = osp.join(src_img_root_dir, dataset_name)
        dst_dataset_dir = osp.join(dst_img_root_dir, dataset_name)

        if not osp.isdir(dst_dataset_dir):
            os.makedirs(dst_dataset_dir)

        img_names = os.listdir(src_dataset_dir)

        for img_name in img_names:

            src_img_path = osp.join(src_dataset_dir, img_name)
            dst_img_path = osp.join(dst_dataset_dir, img_name.replace(' ', '_'))

            shutil.copy(src_img_path, dst_img_path)








if __name__ == '__main__':
    rewrite_img()