import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from database import User, Script, Review, init_db

class RecommendationEngine:
    def __init__(self):
        self.session = init_db()
        self.user_matrix = None
        self.script_matrix = None
        self.user_similarity = None
        self.script_similarity = None
        self.user_map = {}
        self.script_map = {}
        self.reverse_user_map = {}
        self.reverse_script_map = {}
    
    def build_matrices(self):
        # 获取所有用户和剧本
        users = self.session.query(User).all()
        scripts = self.session.query(Script).all()
        
        # 创建用户和剧本的映射
        for i, user in enumerate(users):
            self.user_map[user.id] = i
            self.reverse_user_map[i] = user.id
        
        for i, script in enumerate(scripts):
            self.script_map[script.id] = i
            self.reverse_script_map[i] = script.id
        
        # 创建评分矩阵
        user_script_matrix = np.zeros((len(users), len(scripts)))
        
        # 填充评分矩阵
        reviews = self.session.query(Review).all()
        for review in reviews:
            user_idx = self.user_map[review.user_id]
            script_idx = self.script_map[review.script_id]
            user_script_matrix[user_idx, script_idx] = review.rating
        
        # 转换为稀疏矩阵
        self.user_matrix = csr_matrix(user_script_matrix)
        self.script_matrix = csr_matrix(user_script_matrix.T)
        
        # 计算相似度矩阵
        self.user_similarity = cosine_similarity(self.user_matrix)
        self.script_similarity = cosine_similarity(self.script_matrix)
    
    def get_user_recommendations(self, user_id, n=5):
        if user_id not in self.user_map:
            return []
        
        user_idx = self.user_map[user_id]
        user_ratings = self.user_matrix[user_idx].toarray().flatten()
        
        # 获取用户未评分的剧本
        unrated_scripts = np.where(user_ratings == 0)[0]
        
        if len(unrated_scripts) == 0:
            return []
        
        # 计算预测评分
        predictions = []
        for script_idx in unrated_scripts:
            # 获取相似用户的评分
            similar_users = np.argsort(self.user_similarity[user_idx])[::-1][1:6]  # 取前5个相似用户
            similar_ratings = self.user_matrix[similar_users, script_idx].toarray().flatten()
            
            # 计算加权平均评分
            weights = self.user_similarity[user_idx][similar_users]
            weights = weights / np.sum(weights)  # 归一化权重
            pred_rating = np.sum(similar_ratings * weights)
            
            predictions.append((self.reverse_script_map[script_idx], pred_rating))
        
        # 按预测评分排序
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个推荐
        return [self.session.query(Script).get(script_id) for script_id, _ in predictions[:n]]
    
    def get_script_recommendations(self, script_id, n=5):
        if script_id not in self.script_map:
            return []
        
        script_idx = self.script_map[script_id]
        
        # 获取相似剧本
        similar_scripts = np.argsort(self.script_similarity[script_idx])[::-1][1:n+1]
        
        # 返回推荐剧本
        return [self.session.query(Script).get(self.reverse_script_map[idx]) for idx in similar_scripts]
    
    def get_popular_scripts(self, n=5):
        # 获取评分数量最多的剧本
        scripts = self.session.query(Script).all()
        script_scores = []
        
        for script in scripts:
            avg_rating = script.average_rating
            num_reviews = len(script.reviews)
            # 使用评分和评价数量的加权平均作为流行度分数
            popularity_score = (avg_rating * num_reviews) / (num_reviews + 1)  # 添加1作为平滑因子
            script_scores.append((script, popularity_score))
        
        # 按流行度分数排序
        script_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N个最受欢迎的剧本
        return [script for script, _ in script_scores[:n]] 