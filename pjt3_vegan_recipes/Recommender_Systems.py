## 0. 라이브러리 불러오기

#데이터 핸들링에 사용되는 라이브러리
import pandas as pd
import numpy as np
import json

#데이터 시각화 라이브러리
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
plt.rcParams.update({'font.family':'AppleGothic'})
import plotly.express as px
from sklearn.decomposition import PCA

#데이터 전처리용 라이브러리
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 정규표현식 함수들
import re

# 텍스트에 포함된 특수문자 제거함수
#단 &는 재료의 최소단위를 구분짓는 경계로 사용할것이기 때문에 제거에서 제외한다
def RemoveSpecialChar(readData):
    text = re.sub('[-=+,#/\?:^.@*\"※~%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》|\u0080-\uffef]',' ', readData)
    return text

#숫자 제거 함수
def RemoveNum(readData):
    text=re.sub(r'[0-9]+', '',readData)
    return text

#유니코드 제거 함수 (예:†¼½¾⅓⅔)
def RemoveUnicode(readData):
    #encode() method
    strencode = readData.encode("ascii", "replace")
    #decode() method
    strdecode = strencode.decode()
    return strdecode

#총 특수문자/숫자/유니코드 제거하도록 통합시킨 함수
def PreprocessText(readData):
    readData=RemoveUnicode(readData)
    readData=RemoveSpecialChar(readData)
    result=RemoveNum(readData)
    return result

# 추천시스템 구현을 위한 라이브러리
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#임베딩 벡터와 관련된 라이브러리
import gensim
from gensim.models import doc2vec
from gensim.models.doc2vec import TaggedDocument
from gensim.test.utils import get_tmpfile

#딥러닝을 위한 라이브러리
import keras
from sklearn.utils import shuffle
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dot, Add, Flatten
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import SGD, Adam, Adamax

#AWS MySQL 데이터베이스 연결
# from .models import *

#기타 함수
#난수함수
import random

#%%
# 1.클러스터링

#%% 1-1. 데이터 셋 불러오기
# 파이썬에서 MySql 연결을 위한 함수


def Download_dataset(table_nm='recipe'):
    from sqlalchemy import create_engine
    user_nm = 'root'
    user_pw = 't0101'
    host_nm = '35.79.107.247'
    host_address = '3306'
    db_nm = 'team01'
    # 데이터베이스 연결
    db_connection_path = f'mysql+mysqldb://{user_nm}:{user_pw}@{host_nm}:{host_address}/{db_nm}'
    db_connection = create_engine(db_connection_path, encoding='utf-8')
    conn = db_connection.connect()
    # 데이터 로딩
    df = pd.read_sql_table(table_nm, con=conn)
    df['ingredients']= df['ingredients'].apply(lambda x: x.split(','))
    return df

def Upload_dataset(df,table_nm):
    from sqlalchemy import create_engine
    user_nm = 'root'
    user_pw = 't0101'
    host_nm = '35.79.107.247'
    host_address = '3306'
    db_nm = 'team01'
    # 데이터베이스 연결
    db_connection_path = f'mysql+mysqldb://{user_nm}:{user_pw}@{host_nm}:{host_address}/{db_nm}'
    db_connection = create_engine(db_connection_path, encoding='utf-8')
    conn = db_connection.connect()
    # 데이터 적재
    df.to_sql(name=table_nm ,con=conn,  if_exists='replace')
    return df



#%% 1-2.레시피 총 데이터셋에서 title,ingredients 열만 추출, ingredients를 클러스터링을 위해 전처리 하기

def C2_get_preprocessed_recipe(df):
    #레시피와 재료만 추출
    recipe_N_ingredients= df[['title','ingredients']]
    recipe_N_ingredients

    #재료 데이터의 복잡한 데이터구조 [레시피:[재료]] [재료1,재료2,...,재료_n] 재료_j는 str거나 dict인 구조.
    #재료가 dict인 경우 안의 원재료명만 추출하는 방식을 사용

    ingredients_lst=[' ' for i in range(len(recipe_N_ingredients))]
    title_lst=[]

    for i in range(len(recipe_N_ingredients)):
        title_lst.append(recipe_N_ingredients.iloc[i]['title'])
        try:
            for j in range(len(recipe_N_ingredients.iloc[i]['ingredients'])):
                if type(recipe_N_ingredients.iloc[i]['ingredients'][j]) == str:
                    ingredients_lst[i]= ingredients_lst[i]+PreprocessText(str(recipe_N_ingredients.iloc[i]['ingredients'][j]))+' '
                    ingredients_lst[i] = re.sub(',',' ', ingredients_lst[i])

                elif type(recipe_N_ingredients.iloc[i]['ingredients'][j]) == dict:
                    ingredients_lst[i]= ingredients_lst[i] + \
                                        PreprocessText(str([x + '  ' for x in list(recipe_N_ingredients.iloc[i]['ingredients'][j].values())[0]])) +' '
                    ingredients_lst[i] = re.sub(',',' ', ingredients_lst[i])
        except:
            ingredients_lst[i]='Not Found'

    #전처리된 결과를 데이터프레임에 담기
    recipe_N_ingredients_2= pd.DataFrame([title_lst,ingredients_lst],index=['title','ingredients'])
    recipe_N_ingredients_2= recipe_N_ingredients_2.T
    recipe_N_ingredients_2['ingredients']= recipe_N_ingredients_2['ingredients'].apply(lambda x: x.lower())
    recipe_N_ingredients_2

    # 요리 측량 단위 레퍼런스: https://en.wikibooks.org/wiki/Cookbook:Units_of_measurement
    #요리 측정 단위 단어들을 불용어로 지정하기 위해 다음과 같은 단어 리스트들을 지정해둔다
    ingredient_stopwords=['fresh','optional','sliced','cubes','hot','frozen','juiced','syrup','taste','unsweetened',
                          'soft','removed','plant','based','choice','tspground','turmeric','pinchground','black','canned',''
        ,'granulated','vegan','pure','extract','brown','boilng','powder','syrupagave','crushed','whole',
                          'cloves','dairy','free','dark','drained','ground','medium','vegatable','bouillon','cooked',
                          'small','yellow','bell','sauce','nutritional','chopped','red','cut','thinly','dry','white',
                          'baking','minced','dried','peeled','purpose','roasted','oregano','rolled','diced','raw',
                          'extra','large','water','leaves','green','plus','juice','light','divided','melted','plain',
                          'rinsed','fat','seeds','toasted','clove','flakes','shredded','finely','grated','roughly',
                          'freshly','sweet','sea','packed','ripe','like','virgin','smoked','organic','bought','use',
                          'needed','serve','pinch','recipe','sub','gf','adjust','ounces','tablespoons','handful','used',
                          'teaspoons','chips','slices','pieces','less','soaked','half','pitted','low','thin','store',
                          'baby','see','kosher','non','fine','not','found','tablespoon','ice','cooking','full','firm',
                          'gluten','paste','garnish','bunch','yields','written','halved','stock','spice','mix','cayenne',
                          'spray','spring','heaped','vegetable','powdered','topping','mixed','caster']

    volume=['ml','mL','cc','l','L','liter','dl','dL','teaspoon','t','tsp','tablespoon', \
            'T','tbl','tbs','tsp','Tbsp','tbsp','fl oz','gill','cup','cups','c','pint','p','pt','fl pt','quart', \
            'q','qt','fl qt','gallon','g','gal','large','small','medium','half']
    weight=['mg','g','gram','kg','pound','lb','ounce','oz','lbs','pounds']
    length=['mm','cm','m','inch','in','\"','yard','inches','length']
    temperature=['°C','°F','C','F']
    time_ =['year','years','month','weeks','week','days','day','hours','hour','mintus','seconds','second']
    Etc=[' ']
    adjective=['diced' , 'divided','Raw','sized','yellow','white','White','black','heavy','mature','sub','trimmed','top', \
               'Peeled','delicious','one']
    preposition=['depending']
    verb=['cut','see','note','use']
    noun=['Cups','temperature','Temperature']

    ##medium, cut, yellow, white, Cups, heavy ,length , mature, black, half, room, see, note, use

    measurements= volume+weight+length+temperature+time_+Etc +adjective+preposition+verb+noun+ingredient_stopwords
    set_measurements= set(measurements)

    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    stop_words= stop_words | set_measurements

    #리스트 내 원소들을 합치기용 함수 - apply를 통해 row 단위에 적용
    def lst_to_str(lst):
        result=''
        for item in lst:
            result=result+' '+item
        return result

    #단어들을 뛰어쓰기 단위로 쪼개기 => 하나의 레시피에 하나의 재료 리스트가 대응되게 됨
    splited_sr= pd.Series(recipe_N_ingredients_2['ingredients']).apply(lambda x: x.split())
    #불용어를 이용한 필터링
    filtered_sr= splited_sr.apply(lambda x: [item for item in x if item not in stop_words])
    #행에 중복된 단어 삭제
    unique_df= filtered_sr.apply(lambda x: list(set(x)))
    #stemming하기
    from nltk.stem import WordNetLemmatizer
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    lemmatizer = WordNetLemmatizer()
    lemmatized_df= unique_df.apply(lambda x: [lemmatizer.lemmatize(word,'n') for word in x])

    #다시 리스트를 문자열로 합치기
    preprocessed_sr= lemmatized_df.apply(lst_to_str)
    # 이제 원래 목표인 '&를 경계로 재료명을 구분짓기'를 시행
    tokened_sr= preprocessed_sr.apply(lambda x:x.split('&'))

    tokened_df= pd.DataFrame([title_lst,list(preprocessed_sr.values)],index=['title','ingredients'])
    tokened_df= tokened_df.T


    return tokened_df,recipe_N_ingredients_2

#%% 1-3.빈도순으로 주요 단어 50개를 선정하고, 주요단어에 대한 레시피들의 TF-IDF를 계산하기
def C3_TF_IDF(tokened_df,selected_feature=50):
    token_lst= tokened_df['ingredients'].tolist()
    vocab = list(set(w for doc in token_lst for w in doc.split()))

    from sklearn.feature_extraction.text import TfidfVectorizer

    ingredient_stopwords=['fresh','optional','sliced','cubes','hot','frozen','juiced','syrup','taste','unsweetened',
                          'soft','removed','plant','based','choice','tspground','turmeric','pinchground','black','canned',''
        ,'granulated','vegan','pure','extract','brown','boilng','powder','syrupagave','crushed','whole',
                          'cloves','dairy','free','dark','drained','ground','medium','vegatable','bouillon','cooked',
                          'small','yellow','bell','sauce','nutritional','chopped','red','cut','thinly','dry','white',
                          'baking','minced','dried','peeled','purpose','roasted','oregano','rolled','diced','raw',
                          'extra','large','water','leaves','green','plus','juice','light','divided','melted','plain',
                          'rinsed','fat','seeds','toasted','clove','flakes','shredded','finely','grated','roughly',
                          'freshly','sweet','sea','packed','ripe','like','virgin','smoked','organic','bought','use',
                          'needed','serve','pinch','recipe','sub','gf','adjust','ounces','tablespoons','handful','used',
                          'teaspoons','chips','slices','pieces','less','soaked','half','pitted','low','thin','store',
                          'baby','see','kosher','non','fine','not','found','tablespoon','ice','cooking','full','firm',
                          'gluten','paste','garnish','bunch','yields','written','halved','stock','spice','mix','cayenne',
                          'spray','spring','heaped','vegetable','powdered','topping','mixed','caster']


    tfidfv = TfidfVectorizer(max_features=selected_feature,stop_words=ingredient_stopwords).fit(token_lst)

    # selected_feature의 TF_IDF matrix 계산하기
    TF_IDF_matrix= tfidfv.transform(token_lst).toarray()
    from sklearn.cluster import KMeans

    n_cluster=9
    kmeans= KMeans(n_clusters=n_cluster,init='k-means++',max_iter=300,random_state=0)
    kmeans.fit(TF_IDF_matrix)
    TF_IDF_matrix= TF_IDF_matrix.astype(float)
    TF_IDF_matrix= pd.DataFrame(TF_IDF_matrix)
    TF_IDF_matrix['cluster']= kmeans.labels_
    TF_IDF_matrix

    #나중에 빈도순 중요단어가 무엇인지 알려줄때 사용
    vocabs=tfidfv.vocabulary_

    return TF_IDF_matrix,tfidfv,vocabs

#%% 1-R1.여러개의 클러스터링 개수를 list로 입력받아 실루엣 계수를 시각화하는 함수
# X_features= TF_IDF_matrix.iloc[:,0:selected_feature] 필요

def Visualize_silhouette(cluster_lists, selected_feature=50):

    df=Download_dataset()
    tokened_df,recipe_N_ingredients_2=C2_get_preprocessed_recipe(df)
    TF_IDF_matrix,tfidfv,vocabs= C3_TF_IDF(tokened_df,selected_feature)
    X_features= TF_IDF_matrix.iloc[:,0:selected_feature]

    from sklearn.datasets import make_blobs
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_samples, silhouette_score

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import math

    # 입력값으로 클러스터링 갯수들을 리스트로 받아서, 각 갯수별로 클러스터링을 적용하고 실루엣 개수를 구함
    n_cols = len(cluster_lists)

    # plt.subplots()으로 리스트에 기재된 클러스터링 수만큼의 sub figures를 가지는 axs 생성
    plt.figure(dpi=300)
    fig, axs = plt.subplots(figsize=(4*n_cols, 4), nrows=1, ncols=n_cols)

    # 리스트에 기재된 클러스터링 갯수들을 차례로 iteration 수행하면서 실루엣 개수 시각화
    for ind, n_cluster in enumerate(cluster_lists):

        # KMeans 클러스터링 수행하고, 실루엣 스코어와 개별 데이터의 실루엣 값 계산.
        clusterer = KMeans(n_clusters = n_cluster, max_iter=500, random_state=0)
        cluster_labels = clusterer.fit_predict(X_features)

        sil_avg = silhouette_score(X_features, cluster_labels)
        sil_values = silhouette_samples(X_features, cluster_labels)

        y_lower = 10
        axs[ind].set_title('Number of Cluster : '+ str(n_cluster)+'\n' \
                                                                  'Silhouette Score :' + str(round(sil_avg,3)) )
        axs[ind].set_xlabel("The silhouette coefficient values")
        axs[ind].set_ylabel("Cluster label")
        axs[ind].set_xlim([-0.1, 1])
        axs[ind].set_ylim([0, len(X_features) + (n_cluster + 1) * 10])
        axs[ind].set_yticks([])  # Clear the yaxis labels / ticks
        axs[ind].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])

        # 클러스터링 갯수별로 fill_betweenx( )형태의 막대 그래프 표현.
        for i in range(n_cluster):
            ith_cluster_sil_values = sil_values[cluster_labels==i]
            ith_cluster_sil_values.sort()

            size_cluster_i = ith_cluster_sil_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_cluster)
            axs[ind].fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_sil_values, \
                                   facecolor=color, edgecolor=color, alpha=0.7)
            axs[ind].text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            y_lower = y_upper + 10

        axs[ind].axvline(x=sil_avg, color="red", linestyle="--")


    plt.savefig('./Output/Clustering/silhouette.jpg')

#%% 1-R2. 클러스터링하고, 그 결과를 json파일로 저장하기
#레시피 df, 클러스터 df, 빈도수 주요단어를 반환한다
def Make_Clusters(selected_feature=50):
    df=Download_dataset()
    tokened_df,recipe_N_ingredients_2=C2_get_preprocessed_recipe(df)
    TF_IDF_matrix,tfidfv,vocabs= C3_TF_IDF(tokened_df,selected_feature)

    # 클러스터로으로 나누어졌을 떄의 각각 클러스터별 특징 살피기
    Cluster_df= TF_IDF_matrix.iloc[:,0:selected_feature+1].groupby('cluster').mean()

    #각각 클러스터별 상위 ingredients_len개 재료 선택
    ingredieints_len=10
    cluster1_feature= list(Cluster_df.iloc[0].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster2_feature= list(Cluster_df.iloc[1].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster3_feature= list(Cluster_df.iloc[2].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster4_feature= list(Cluster_df.iloc[3].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster5_feature= list(Cluster_df.iloc[4].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster6_feature= list(Cluster_df.iloc[5].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster7_feature= list(Cluster_df.iloc[6].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster8_feature= list(Cluster_df.iloc[7].sort_values(ascending=False).index)[0:ingredieints_len]
    cluster9_feature= list(Cluster_df.iloc[8].sort_values(ascending=False).index)[0:ingredieints_len]
    #cluster10_feature= list(Cluster_df.iloc[9].sort_values(ascending=False).index)[0:ingredieints_len]


    #정수 인코딩된 재료명을 다시 원래의 자연어 재료명으로 변환
    ingredients_int = list(tfidfv.vocabulary_.values())
    ingredients_name= list(tfidfv.vocabulary_.keys())
    ingredients_name
    ingredient_df= pd.DataFrame([ingredients_int,ingredients_name],index=['인코딩된 정숫값','재료명']).T
    ingredient_df=ingredient_df.sort_values(by='인코딩된 정숫값').set_index('인코딩된 정숫값')


    #각 재료명을 추출 후 데이터프레임에 담기
    cluster1_df= ingredient_df.iloc[cluster1_feature].values.flatten()
    cluster2_df= ingredient_df.iloc[cluster2_feature].values.flatten()
    cluster3_df= ingredient_df.iloc[cluster3_feature].values.flatten()
    cluster4_df= ingredient_df.iloc[cluster4_feature].values.flatten()
    cluster5_df= ingredient_df.iloc[cluster5_feature].values.flatten()
    cluster6_df= ingredient_df.iloc[cluster6_feature].values.flatten()
    cluster7_df= ingredient_df.iloc[cluster7_feature].values.flatten()
    cluster8_df= ingredient_df.iloc[cluster8_feature].values.flatten()
    cluster9_df= ingredient_df.iloc[cluster9_feature].values.flatten()
    #cluster10_df= ingredient_df.iloc[cluster9_feature].values.flatten()

    clusters_df= pd.DataFrame([cluster1_df,cluster2_df,cluster3_df,cluster4_df,cluster5_df,cluster6_df,cluster7_df, \
                               cluster8_df,cluster9_df],
                              index=['클러스터1','클러스터2','클러스터3','클러스터4','클러스터5','클러스터6','클러스터7','클러스터8', \
                                     '클러스터9']) #

    #각 클러스터에 대응되는 레시피 붙이기

    #군집값이 0,1,2,3,4,5,6,7 이니 경우 마다 별도의 인덱스로 추출
    cluster1_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==0].index.tolist()
    cluster2_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==1].index.tolist()
    cluster3_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==2].index.tolist()
    cluster4_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==3].index.tolist()
    cluster5_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==4].index.tolist()
    cluster6_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==5].index.tolist()
    cluster7_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==6].index.tolist()
    cluster8_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==7].index.tolist()
    cluster9_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==8].index.tolist()
    #cluster10_index= TF_IDF_matrix[TF_IDF_matrix['cluster']==9].index.tolist()

    ingredient_names= recipe_N_ingredients_2['title']
    cluster1_title=ingredient_names.iloc[cluster1_index].values.tolist()
    cluster2_title=ingredient_names.iloc[cluster2_index].values.tolist()
    cluster3_title=ingredient_names.iloc[cluster3_index].values.tolist()
    cluster4_title=ingredient_names.iloc[cluster4_index].values.tolist()
    cluster5_title=ingredient_names.iloc[cluster5_index].values.tolist()
    cluster6_title=ingredient_names.iloc[cluster6_index].values.tolist()
    cluster7_title=ingredient_names.iloc[cluster7_index].values.tolist()
    cluster8_title=ingredient_names.iloc[cluster8_index].values.tolist()
    cluster9_title=ingredient_names.iloc[cluster9_index].values.tolist()
    #cluster10_title=ingredient_names.iloc[cluster10_index].values.tolist()


    clusters_df['recipe']=[cluster1_title,cluster2_title,cluster3_title,cluster4_title,cluster5_title,cluster6_title,
                           cluster7_title,cluster8_title,cluster9_title]
    #,cluster5_title,cluster6_title,\ cluster7_title, cluster8_title, cluster9_title
    #                 cluster6_title,cluster7_title,cluster8_title,cluster9_title]


    ## 클러스터 네이밍
    #  특정 재료가 3개 이상 있으면 해당 클러스터에 네이밍을 한다
    cluster_indian=None
    cluster_asian=None
    cluster_western= None
    cluster_dessert=None
    indian_index=[]
    asian_index=[]
    western_index=[]
    dessert_index=[]

    n_cluster=9
    for i in range(1,n_cluster+1):
        if clusters_df.loc[f'클러스터{i}'].str.contains("lime|coriander|cilantro|cumin|avocado|onion").sum() >=3:
            if type(cluster_western) is None:
                cluster_indian=  clusters_df.loc[f'클러스터{i}']
                indian_index= indian_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

            else:
                cluster_indian = pd.concat([cluster_indian,clusters_df.loc[f'클러스터{i}']],axis=1)
                indian_index= indian_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

        elif clusters_df.loc[f'클러스터{i}'].str.contains("sesame|rice|soy|tofu").sum() >=3:
            if type(cluster_western) is None:
                cluster_asian=  clusters_df.loc[f'클러스터{i}']
                asian_index= asian_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

            else:
                cluster_asian = pd.concat([cluster_asian,clusters_df.loc[f'클러스터{i}']],axis=1)
                asian_index= asian_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

        elif clusters_df.loc[f'클러스터{i}'].str.contains("sugar|milk|coconut|vanilla|butter|almond|cinnamon|yogurt").sum() >=3:
            if type(cluster_western) is None:
                cluster_dessert=  clusters_df.loc[f'클러스터{i}']
                dessert_index= dessert_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

            else:
                cluster_dessert = pd.concat([cluster_dessert,clusters_df.loc[f'클러스터{i}']],axis=1)
                dessert_index= dessert_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

        else:
            if type(cluster_dessert) is None:
                cluster_western=  clusters_df.loc[f'클러스터{i}']
                western_index=  western_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()

            else:
                cluster_western = pd.concat([ cluster_western,clusters_df.loc[f'클러스터{i}']],axis=1)
                western_index= western_index + TF_IDF_matrix[TF_IDF_matrix['cluster']==(i-1)].index.tolist()


    cluster_indian= cluster_indian.T
    cluster_asian= cluster_asian.T
    cluster_western= cluster_western.T
    cluster_dessert= cluster_dessert.T

    #저장하기
    #각 카테고리 명 붙이기
    #[식 for 변수1 in 리스트1 if 조건식1     for 변수2 in 리스트2 if 조건식2     ...     for 변수n in 리스트n if 조건식n]
    # n if n>0 else 0 for n in array

    cluster_lst=[]
    for i in range(len(tokened_df)):
        if i in indian_index:
            cluster_lst.append('1.인도+남아시아+남미 <주재료: 큐민/고수/라임/아보카도/양파>')
        elif i in asian_index:
            cluster_lst.append('2.동아시아 <주재료: 쌀/간장/참깨/두부>')
        elif i in dessert_index:
            cluster_lst.append('3.디저트+제과제빵 <주재료: 설탕/우유/코코넛/바닐라/버터/아몬드>')
        else:
            cluster_lst.append('4.서양+기타')

    df['카테고리']=pd.Series(cluster_lst)

    #결과들 저장
    df.to_json('./Output/Clustering/Preprocessed_Recipes.json',orient='table')
    clusters_df.to_json('./Output/Clustering/clusters.json',orient='table')
    vocabs= pd.Series(vocabs)
    vocabs.to_json('./Output/Clustering/main_keywords.json',orient='table')
    TF_IDF_matrix.to_json('./Output/Clustering/TF_IDF_matrix.json',orient='table')

    print('저장이 완료되었습니다')

#%% 2 더미데이터 제작

#%% 2-1. 더미데이터 제작

def Make_dummy_5stars():
    df= Download_dataset()

    #무작위 200개 레시피 추출하여 데이터프레임의 컬럼명으로 쓰기
    selected_recipe_len=200
    np.random.seed(1)
    random_sampled_recipe=np.random.choice(range(1, len(df)),selected_recipe_len, replace=False)
    recipe_names= list(df.iloc[random_sampled_recipe]['title'].values)

    # 더미 유저수 결정하기
    dummy_user_len= 20000
    dummy_df = pd.DataFrame(index=range(0,dummy_user_len), columns=recipe_names)
    dummy_df
    # 리뷰 안 단 비율과 단 비율을 0.95: 0.05로 설정

    r=0.05
    random_numbers = [np.random.choice(np.arange(6),len(recipe_names), p=[1-r,0.05*r,0.15*r,0.2*r,0.35*r,0.25*r])for i in range(
        dummy_user_len)]

    #무작위로 리뷰한 결과
    random_reviews= pd.DataFrame(random_numbers, columns=recipe_names)

    #더미 고객 한명이 리뷰를 남긴 갯수
    #pd.DataFrame(random_numbers).sum(axis=1)

    random_reviews.to_csv('Output/Dummy_Data.csv')
    return random_reviews

#%% 2-2. 더미 유저 데이터 전처리하여 불러오기
def User_preprocessing():
    ratings= None
    try:
        # 레시피 평가 데이터(rating_matrix) 불러오기
        # 행: 사용자 ID
        # 열: 레시피 ID
        rating_dummy = pd.read_csv('Output/Dummy_Data.csv', index_col=False)
        rating_dummy.rename(columns = {'Unnamed: 0':'user_id'}, inplace=True)
        rating_dummy.set_index('user_id', inplace=True)

        # 딥러닝 학습을 위한 레시피명 변경
        rating_dummy_int = rating_dummy.copy().T
        rating_dummy_int.reset_index(drop=True, inplace=True)
        rating_dummy_int = rating_dummy_int.T
        rating_dummy_int

        # rating_matrix의 형태 변환
        rating_dummy_int = rating_dummy_int.replace(0, np.NaN)
        ratings = rating_dummy_int.stack()

        # ratings 데이터프레임 생성
        ratings = pd.DataFrame(ratings)
        ratings.reset_index(inplace = True)
        ratings.rename(columns={'level_0':'user_id', 'level_1':'selected_recipe_id', 0:'stars'}, inplace=True)

    except:
        print('사용자 데이터가 존재하지 않습니다')
    return  ratings


#%% 3
# 콘텐츠 기반 필터링

#%%
def CBF(User_ID,model_loc='Output/CBF_Recommender/CBF_Model'):
    CBF_df= None
    selected_recipe_len=200
    try:
        #유저들의 평가 데이터 불러오기
        #그중 4점 이상 평가한 것으로 추린다
        ratings= User_preprocessing()
        user_rating_lst= ratings[ratings['user_id']==User_ID]
        user_rating_lst = user_rating_lst[user_rating_lst['stars']>=4]
        user_rating_lst = user_rating_lst['selected_recipe_id']

        #200개로 추려진 요리 목록을 딕셔너리 형태로 담기
        dummy= pd.read_csv('Output/Dummy_Data.csv')
        selected_recipes_names= list(dummy.columns)[1:]
        recipe_ranges= list(range(selected_recipe_len))
        selected_recipes_dict= dict(zip(recipe_ranges,selected_recipes_names))

        #유저 아이디를 이용해서 유저가 선호한 음식 찾기
        user_preferred_recipe= [selected_recipes_dict[j] for j in user_rating_lst]

        # 모델 불러오기
        model = doc2vec.Doc2Vec.load(model_loc)
        #임베딩 벡터 평균치로써 유저가 가장 좋아할만한 레시피 10개를 추천한다
        recommend_result=model.dv.most_similar(user_preferred_recipe,topn=10)

        #이때 데이터는 (레시피명,유사도) 튜플 형태로 반환된다
        #추천된 레시피와 유사도 점수를 분리해서 담기
        recipe_name=[recommend_result[i][0] for i in range(len(recommend_result))]
        similarity_score=[recommend_result[i][1] for i in range(len(recommend_result))]
        CBF_df= pd.DataFrame([recipe_name,similarity_score,user_preferred_recipe],
                             index=['recommended_recipe','ingredinets_cosine_similarity','user_preferred_recipe']).T

        CBF_df.to_json('./Output/CBF_Recommender/'+'User_ID_'+ str(User_ID)+'_CBF_results.json' ,orient= 'table')
    except:
        pass




#%% 3-R2. CBF 추천 알고리즘 모델 파일 만들기
#절대 경로 /각자 컴퓨터에 맞게 수정 부탁드립니다

def Make_CBF_model():
    df= Download_dataset()
    tokened_df,recipe_N_ingredients_2=C2_get_preprocessed_recipe(df)
    #레시피-재료 document를 doc2vec 하여 레시피간 재료의 유사도를 고려하는 모델 생성하기

    #doc2Vec을 적용하기 위해 문자열로 구성된 ingredient 성분들을 띄워쓰기를 기준으로 list로 쪼갠다
    splited_lst= pd.Series(tokened_df['ingredients']).apply(lambda x: x.split()).tolist()
    #doc2Vec을 적용시키기 위한 데이터구조로 만들고, 적용시킨다
    #이때 모델학습에 사용되는 데이터는 레시피 데이터셋이다
    taggedDocs = [TaggedDocument(words=splited_lst[i], tags=tokened_df['title'][{i}]) for i in range(len(splited_lst))]

    #Doc2Ve
    #레시피 데이터셋을 활용하여 학습하였다
    #각 레시피는 구성되는 재료들을 활용하여 유사도를 측정한다
    model = gensim.models.doc2vec.Doc2Vec(taggedDocs, dm=1, vector_size=50, epochs=10, hs=0,seed=0)
    model.train(taggedDocs, total_examples=model.corpus_count, epochs=model.epochs)

    #모델 저장하기
    fname = get_tmpfile('C://workspaces/project3/multi_project3_vegan/pjt3_vegan_recipes/Output/CBF_Recommender/CBF_Model')
    model.save(fname)

#%%
# 4.협업 필터링 추천 알고리즘

#%% 4-2. 훈련-데이터셋 분리
def CF2_spliting_train_test(ratings,TRAIN_SIZE = 0.75):
    ratings = shuffle(ratings)
    cutoff = int(TRAIN_SIZE * len(ratings))
    ratings_train = ratings.iloc[:cutoff]
    ratings_test = ratings.iloc[cutoff:]

    return ratings_train,ratings_test

#%% 4-3.

def CF3_get_unseen_recipes(user_id):
    ratings= User_preprocessing()

    #입력값으로 들어온 user_id에 해당하는 사용자가 평점을 매긴 모든 recipe를 리스트로 생성
    seen_recipes = ratings[ratings['user_id']== user_id]['selected_recipe_id'].tolist()
    print(seen_recipes)

    dummy= pd.read_csv('Output/Dummy_Data.csv')
    selected_recipe_names= list(dummy.columns)[1:]
    recipe_ranges= list(range(200))
    selected_recipe= dict(zip(recipe_ranges,selected_recipe_names))

    # 모든 recipe들의 recipe_id중 이미 평점을 매긴 recipe의 recipe_id를 제외하여 리스트로 생성
    unseen_recipes= [recipe for recipe in selected_recipe if recipe not in seen_recipes]
    print('평점 매긴 recipe 수:',len(seen_recipes), '추천 대상 recipe 수:',len(unseen_recipes), \
          '샘플 recipe 수:',len(selected_recipe))

    return unseen_recipes

#%% 4-4. 평가 척도: RMSE

def RMSE(y_true, y_pred):
    return tf.sqrt(tf.reduce_mean(tf.square(y_true - y_pred)))

#%% 4-R1 협업 필터링 적용
    #특정 유저의 좋아요 기록을 불러오기
def CF(user_id, model_loc="./Output/CF_Recommender/CF_Model.h5",top_n=10):

    selected_recipe_len=200
    def RMSE(y_true, y_pred):
        return tf.sqrt(tf.reduce_mean(tf.square(y_true - y_pred)))

    #유저들의 평가 데이터 불러오기
    #그중 4점 이상 평가한 것으로 추린다
    ratings= User_preprocessing()
    user_rating_lst= ratings[ratings['user_id']== user_id]
    user_rating_lst = user_rating_lst[user_rating_lst['stars']>=4]
    user_rating_lst = user_rating_lst['selected_recipe_id']

    #200개로 추려진 요리 목록을 딕셔너리 형태로 담기
    dummy= pd.read_csv('Output/Dummy_Data.csv')
    selected_recipes_names= list(dummy.columns)[1:]
    recipe_ranges= list(range(selected_recipe_len))
    selected_recipes_dict= dict(zip(recipe_ranges,selected_recipes_names))
    #유저 아이디를 이용해서 유저가 선호한 음식 찾기
    user_preferred_recipe= [selected_recipes_dict[j] for j in user_rating_lst]

    #모델 불러오기
    top_n=10
    model = tf.keras.models.load_model(filepath=model_loc ,custom_objects={'RMSE':RMSE})

    #이미 평점을 메긴 정보를 제외하는 함수 불러오기
    unseen_recipes= CF3_get_unseen_recipes(user_id)

    #mu값을 구하기 위한 계산
    ratings=User_preprocessing()
    ratings_train,ratings_test= CF2_spliting_train_test(ratings)
    mu=ratings_train.stars.mean()    # 전체 평균

    #레시피와 사용자 정보 배열로 만듬
    tmp_recipe_data = np.array(list(unseen_recipes))
    tmp_user = np.array([user_id for i in range(len(tmp_recipe_data))])

    # predict() list 객체로 저장
    predictions = model.predict([tmp_user, tmp_recipe_data])
    predictions = np.array([p[0] for p in predictions])

    # 정렬하여 인덱스 값 추출
    recommended_recipe_ids = (-predictions).argsort()[:top_n]
    top_recipe = [selected_recipes_dict[id] for id in recommended_recipe_ids]
    top_recipe


    #임베딩 벡터 평균치로써 유저가 가장 좋아할만한 레시피 10개를 추천한다
    recommend_result=top_recipe

    #이때 데이터는 (레시피명,유사도) 튜플 형태로 반환된다
    #추천된 레시피와 유사도 점수를 분리해서 담기
    recipe_name=[]
    similarity_score=[]
    for i in range(len(recommend_result)):
        recipe_name.append(recommend_result[i])
        CF_df= pd.DataFrame([recipe_name,user_preferred_recipe],
                            index=['recommended_recipe','user_preferred_recipe']).T

    CF_df.to_json('./Output/CF_Recommender/'+'User_ID_'+ str(user_id)+'_CF_results.json' ,orient= 'table')



#%% 4-R2. 딥러닝 모델 설계 및 학습 & 저장

def Make_CF_model():
    ratings= User_preprocessing()
    ratings_train, ratings_test= CF2_spliting_train_test(ratings)

    # Variable 초기화
    K = 200                             # Latent factor 수
    mu = ratings_train.stars.mean()      # 전체 평균
    M = ratings.user_id.max() + 1      # Number of users
    N = ratings.selected_recipe_id.max() + 1      # Number of recipe

    # Keras model
    user = Input(shape=(1, ))                                               # User input
    item = Input(shape=(1, ))                                               # Item input
    P_embedding = Embedding(M, K, embeddings_regularizer=l2())(user)        # (M, 1, K)
    Q_embedding = Embedding(N, K, embeddings_regularizer=l2())(item)        # (N, 1, K)
    user_bias = Embedding(M, 1, embeddings_regularizer=l2())(user)          # User bias term (M, 1, )
    item_bias = Embedding(N, 1, embeddings_regularizer=l2())(item)          # Item bias term (N, 1, )

    # Concatenate layers
    from tensorflow.keras.layers import Dense, Concatenate, Activation
    P_embedding = Flatten()(P_embedding)                                    # (K, )
    Q_embedding = Flatten()(Q_embedding)                                    # (K, )
    user_bias = Flatten()(user_bias)                                        # (1, )
    item_bias = Flatten()(item_bias)                                        # (1, )
    R = Concatenate()([P_embedding, Q_embedding, user_bias, item_bias])     # (2K + 2, )

    # Neural network
    R = Dense(2048)(R)
    R = Activation('relu')(R)
    R = Dense(256)(R)
    R = Activation('linear')(R)
    R = Dense(1)(R)

    #설계된 모델
    model = Model(inputs=[user, item], outputs=R)
    model.compile(
        loss=RMSE,
        optimizer=SGD(),
        #optimizer=Adamax(),
        metrics=[RMSE]
    )

    #모델 학습
    model.fit(
        x=[ratings_train.user_id.values, ratings_train.selected_recipe_id.values],
        y=ratings_train.stars.values - mu,
        epochs=65,
        batch_size=512,
        validation_data=(
            [ratings_test.user_id.values, ratings_test.selected_recipe_id.values],
            ratings_test.stars.values - mu
        )
    )
    #모델 저장
    filepath = "Output/CF_Recommender/CF_Model.h5"
    model.save(filepath)

#%% 폐기 장소
# 혹 몰라 일단 여기 둠. 서버에 올릴땐 삭제해도 상관없을 듯