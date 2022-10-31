class feature_builder_BOW:
    '''
    class - (仅保留construct_feature及关联部分函数)根据所有图像关键点描述子聚类建立图像视觉词袋，获取每一图像的特征（码本）映射的频数统计
    '''

    def __init__(self, num_cluster=32):
        self.num_clusters = num_cluster

    def extract_features(self, img):
        import cv2 as cv
        '''
        function - 提取图像特征

        Paras:
        img - 读取的图像
        '''
        star_detector = cv.xfeatures2d.StarDetector_create()
        key_points = star_detector.detect(img)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        kp, des = cv.xfeatures2d.SIFT_create().compute(img_gray, key_points)  # SIFT特征提取器提取特征
        return des

    def normalize(self, input_data):
        import numpy as np
        '''
        fuction - 归一化数据

        input_data - 待归一化的数组
        '''
        sum_input = np.sum(input_data)
        if sum_input > 0:
            return input_data / sum_input  # 单一数值/总体数值之和，最终数值范围[0,1]
        else:
            return input_data

    def construct_feature(self, img, kmeans):
        import numpy as np
        '''
        function - 使用聚类的视觉词袋构建图像特征（构造码本）

        Paras:
        img - 读取的单张图像
        kmeans - 已训练的聚类模型
        '''
        des = self.extract_features(img)
        labels = kmeans.predict(des.astype(np.float))  # 对特征执行聚类预测类标
        feature_vector = np.zeros(self.num_clusters)
        for i, item in enumerate(feature_vector):  # 计算特征聚类出现的频数/直方图
            feature_vector[labels[i]] += 1
        feature_vector_ = np.reshape(feature_vector, ((1, feature_vector.shape[0])))
        return self.normalize(feature_vector_)

class ImageTag_extractor:
    '''
    class - 图像识别器，基于图像分类模型，视觉词袋以及图像特征
    '''

    def __init__(self, ERF_clf_fp, visual_BOW_fp, visual_feature_fp):
        from sklearn import preprocessing
        import pickle
        with open(ERF_clf_fp, 'rb') as f:  # 读取存储的图像分类器模型
            self.clf = pickle.load(f)

        with open(visual_BOW_fp, 'rb') as f:  # 读取存储的聚类模型和聚类中心点
            self.kmeans = pickle.load(f)

        '''对标签编码'''
        with open(visual_feature_fp, 'rb') as f:
            self.feature_map = pickle.load(f)
        self.label_words = [x['object_class'] for x in self.feature_map]
        self.le = preprocessing.LabelEncoder()
        self.le.fit(self.label_words)

    def predict(self, img):
        import numpy as np
        feature_vector=feature_builder_BOW().construct_feature(img, self.kmeans)  # 提取图像特征，之前定义的feature_builder_BOW()类，可放置于util.py文件中，方便调用
        label_nums = self.clf.predict(np.asarray(feature_vector))  # 进行图像识别/分类
        image_tag = self.le.inverse_transform([int(x) for x in label_nums])[0]  # 获取图像分类标签
        return image_tag


class ImageTag_extractor_execution:
    def __init__(self,img_url):
        self.img_url=img_url
        self.ERF_clf_fp='app/visual_perception/vp_model/ERF_clf.pkl'
        self.visual_BOW_fp = 'app/visual_perception/vp_model/visual_BOW.pkl'
        self.visual_feature_fp = 'app/visual_perception/vp_model/visual_feature.pkl'

    def execution(self):
        import cv2 as cv
        print("*"*50)
        print(self.img_url)
        imgs_pred_tag=ImageTag_extractor(self.ERF_clf_fp, self.visual_BOW_fp, self.visual_feature_fp).predict(cv.imread(self.img_url))
        return  imgs_pred_tag




