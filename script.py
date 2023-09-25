## Import Library ##

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

## Data Loading ##

# Load data
anime_df = pd.read_csv("./anime.csv")
rating_df = pd.read_csv("./rating.csv")

# Melihat anime_df
anime_df.head()

# Info dari anime_df
anime_df.info()

# Melihat data rating_df
rating_df.head(100)

# Info dari rating_df
rating_df.info()

# Akan dilihat total unique value pada anime_id dan user_id agar diketahui jumlah totalnya
print(f"Total film anime pada anime_df sebanyak {len(anime_df['anime_id'].unique())}")
print(f"Jumlah user pada rating_df sebanyak {len(rating_df['user_id'].unique())}")

## Univariate EDA ##

## Feature Genre
# Define a function to handle the conversion
def convert_to_list(x):
    if isinstance(x, str):
        return x.split(', ')
    else:
        return []  # Handle non-string values

# Menggunakan .apply() untuk memisahkan teks menjadi daftar
anime_df['genre'] = anime_df['genre'].apply(convert_to_list)

# Mengekspansi kolom 'Genre' menjadi beberapa baris
df_genre_exploded = anime_df.explode('genre')

# Mengakses nilai unik dalam kolom 'Genre' yang sudah diexplode
unique_genres = df_genre_exploded['genre'].unique()

plt.figure(figsize=(12,8))
plt.xlabel('Frequency')
plt.ylabel("Count", fontsize=13)
plt.subplots_adjust(hspace=1, wspace=0.3)
plt.xticks(rotation=45)
plt.title("Top 10 Genre Anime")
plt.grid(True)
plt.xticks(rotation=45)
sns.barplot(x=df_genre_exploded["genre"].value_counts().index[:10], y=df_genre_exploded["genre"].value_counts().values[:10])

## Feature type

# Plot pie
labels = anime_df['type'].unique()
labels = labels[:-1]
value = anime_df['type'].value_counts().tolist()
tot = sum(value)
percentages = [(value / tot) * 100 for value in value]
# Create a pie chart with value percentages inside
plt.pie(value, labels=labels, autopct='%.1f%%', startangle=140)
# Draw center circle to make it look like a donut chart
centre_circle = plt.Circle((0,0),0.70,fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)
# Equal aspect ratio ensures that pie is drawn as a circle.
plt.tight_layout()
plt.title("Cholesterol suffer from cardiovascular disease")
plt.show()

## Feature Rating & Members
# Sort the DataFrame by 'Rating' in descending order
df_rating = anime_df.sort_values(by='rating', ascending=False).head(10)
# Set the 'Title' column as the index for plotting
df_rating.set_index('name', inplace=True)
# Select only the 'Members' and 'ScoredBy' columns
df_rating = df_rating[['members']]
# Create a multi bar plot
ax = df_rating.plot(kind='bar', figsize=(10, 6))
# Set labels and title
plt.xlabel('Title')
plt.ylabel('Values')
plt.title('Top 10 Highest Rated Anime by Members')
# Show the plot
plt.show()
df_rating

# Sort the DataFrame by 'Rating' in descending order
df_rating = anime_df.sort_values(by='members', ascending=False).head(10)
# Set the 'Title' column as the index for plotting
df_rating.set_index('name', inplace=True)
# Select only the 'Members' and 'ScoredBy' columns
df_rating = df_rating[['rating']]
# Create a multi bar plot
ax = df_rating.plot(kind='bar', figsize=(10, 6))
# Set labels and title
plt.xlabel('Title')
plt.ylabel('Values')
plt.title('Top 10 Highest Member Anime by Ratings')
# Show the plot
plt.show()
df_rating

## Data Preprocessing

# Menggabungkan rating_df dan anime_df berdasarkan anime_id
anime_all = np.concatenate((
    anime_df['anime_id'].unique(),
    rating_df['anime_id'].unique()
))
anime_all = np.short(np.unique(anime_all))
print(f"Jumlah seluruh data anime berdasarkan anime_id: {len(anime_all)}")

# Menggabungkan kedua dataframe berdasarkan anime_id
df = pd.merge(anime_df, rating_df, on='anime_id', how='left')
df.head()

# Cek missing value
df.isnull().sum()

# Drop missing value
df = df.dropna()

# Cek kembali missing value yang telah didrop
df.isnull().sum()

# Mengecek data yang duplikat
df['genre'] = df['genre'].apply(tuple)
df.duplicated().sum()

# drop data duplicates
df = df.drop_duplicates()

# Cek ulang duplikasi data
df.duplicated().sum()

# Mengurutkan data berdasarkan anime_id
df = df.sort_values('anime_id', ascending=True)
df.head()

# Drop duplikasi dari anime_id yang disebabkan penggabungan rating_df dan anime_df
df = df.drop_duplicates('anime_id')
df.head()

# Melihat jumlah data pada kolom anime_id, name, dan genre
anime_id = df['anime_id'].tolist()
name = df['name'].tolist()
genre = df['genre'].tolist()
print(len(anime_id))
print(len(name))
print(len(genre))

# Membuat dataset baru berdasarkan anime_id, title, dan genre
anime = pd.DataFrame({
    'anime_id': anime_id,
    "title": name,
    'genre': genre
})
anime.head()

## Model Development Content Based Filtering ##

# Inisialisasi TfidfVectorizer
tfidf = TfidfVectorizer()

# Convert lists of genres into text strings
anime['genre'] = anime['genre'].apply(lambda x: ' '.join(x))

# Melakukan perhitungan idf pada data cuisine
tfidf.fit(anime['genre'])

# Mapping array dari fitur index integer ke fitur nama
tfidf.get_feature_names_out()

# Melakukan fit lalu ditransformasikan ke bentuk matrix
tfidf_matrix = tfidf.fit_transform(anime['genre']) 
 
# Melihat ukuran matrix tfidf
tfidf_matrix.shape 

# Mengubah vektor tf-idf dalam bentuk matriks dengan fungsi todense()
tfidf_matrix.todense()

# Membuat dataframe untuk melihat tf-idf matrix
# Kolom diisi dengan genre
# Baris diisi dengan judul anime
pd.DataFrame(
    tfidf_matrix.todense(), 
    columns=tfidf.get_feature_names_out(),
    index=anime['title']
).sample(22, axis=1).sample(10, axis=0)

# Menghitung cosine similarity pada matrix tf-idf
cosine_sim = cosine_similarity(tfidf_matrix) 
cosine_sim

# Membuat dataframe dari variabel cosine_sim dengan baris dan kolom berupa nama resto
cosine_sim_df = pd.DataFrame(cosine_sim, index=anime['title'], columns=anime['title'])
print('Shape:', cosine_sim_df.shape)
 
# Melihat similarity matrix pada setiap resto
cosine_sim_df.sample(5, axis=1).sample(10, axis=0)

def anime_recommendations(nama_anime, similarity_data=cosine_sim_df, items=anime[['title', 'genre']], k=5):

    # Mengambil data dengan menggunakan argpartition untuk melakukan partisi secara tidak langsung sepanjang sumbu yang diberikan    
    # Dataframe diubah menjadi numpy
    # Range(start, stop, step)
    index = similarity_data.loc[:,nama_anime].to_numpy().argpartition(
        range(-1, -k, -1))
    
    # Mengambil data dengan similarity terbesar dari index yang ada
    closest = similarity_data.columns[index[-1:-(k+2):-1]]
    
    # Drop nama anime agar nama anime yang dicari tidak muncul dalam daftar rekomendasi
    closest = closest.drop(nama_anime, errors='ignore')
 
    return pd.DataFrame(closest).merge(items).head(k)

anime_recommendations('Kimi no Na wa.')

## Model Development dengan Collaborative Filtering ##

rating_df.head()

# liat value dari rating
rating_df['rating'].value_counts()

rating_df = rating_df[rating_df['rating']!= -1]
rating_df.reset_index(drop=True, inplace=True)
rating_df.head()

# Check kembali rating, apakah rating dengan nilai -1 masih ada atau tidak
rating_df['rating'].value_counts()

rating_df.head()

# Encoder user_id
user_ids = rating_df["user_id"].unique().tolist()
user2user_encoded = {x: i for i, x in enumerate(user_ids)}
userencoded2user = {i: x for i, x in enumerate(user_ids)}

# Encoder anime_id
anime_ids = rating_df["anime_id"].unique().tolist()
anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
anime_encoded2anime = {i: x for i, x in enumerate(anime_ids)}

# Menambahkan encoder anime_id dan user_id pada rating_df
rating_df["user"] = rating_df["user_id"].map(user2user_encoded)
rating_df["anime"] = rating_df["anime_id"].map(anime2anime_encoded)
rating_df.head()

# Mengetahui jumlah user dan anime
num_users = len(user2user_encoded)
num_animes = len(anime_encoded2anime)
print(num_animes)
print(num_users)

rating_df["rating"] = rating_df["rating"].values.astype(np.float32)
# min and max ratings will be used to normalize the ratings later
min_rating = min(rating_df["rating"])
max_rating = max(rating_df["rating"])
print(
    "Number of users: {}, Number of Movies: {}, Min rating: {}, Max rating: {}".format(
        num_users, num_animes, min_rating, max_rating
    )
)

rating_df = rating_df.sample(frac=1, random_state=42)

# Membagi data training dan testing
x = rating_df[["user", "anime"]].values
y = rating_df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
train_indices = int(0.8 * rating_df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:],
)

# Training

EMBEDDING_SIZE = 32
class RecommenderNet(keras.Model):
    def __init__(self, num_users, num_movies, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_movies = num_movies
        self.embedding_size = embedding_size
        self.user_embedding = layers.Embedding(
            num_users,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
            mask_zero=True
        )
        self.user_bias = layers.Embedding(num_users, 1)
        self.movie_embedding = layers.Embedding(
            num_movies,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
            mask_zero=True
        )
        self.movie_bias = layers.Embedding(num_movies, 1)
    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        movie_vector = self.movie_embedding(inputs[:, 1])
        movie_bias = self.movie_bias(inputs[:, 1])
        dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)
        # Add all the components (including bias)
        x = dot_user_movie + user_bias + movie_bias
        # The sigmoid activation forces the rating to between 0 and 1
        return tf.nn.sigmoid(x)
    
model = RecommenderNet(num_users, num_animes, EMBEDDING_SIZE)
# model compile
model.compile(
    loss = tf.keras.losses.BinaryCrossentropy(),
    optimizer = keras.optimizers.Adam(learning_rate=0.001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

history = model.fit(
    x=x_train,
    y=y_train,
    batch_size=64,
    epochs=5,
    verbose=1,
    validation_data=(x_val, y_val),
)

# Evaluate model dan summary model
model.summary()
test_loss = model.evaluate(x_val, y_val)
print('\\nTest Loss: {}'.format(test_loss))

anime.head()
rat_df = pd.read_csv('./rating.csv')
user_id = rat_df['user_id'].sample(1).iloc[0]
anime_watched_by_user = rat_df[rat_df['user_id']==user_id]
anime_not_watched = anime[~anime['anime_id'].isin(anime_watched_by_user['anime_id'].values)]['anime_id'] 
anime_not_watched = list(
    set(anime_not_watched)
    .intersection(set(anime2anime_encoded.keys()))
)
anime_not_watched = [[anime2anime_encoded.get(x)] for x in anime_not_watched]
user_encoder = user2user_encoded.get(user_id)
user_anime_array = np.hstack(
    ([[user_encoder]] * len(anime_not_watched), anime_not_watched)
)
ratings = model.predict(user_anime_array).flatten()

top_ratings_indices = ratings.argsort()[-10:][::-1]
recommended_anime_ids = [
    anime_encoded2anime.get(anime_not_watched[x][0]) for x in top_ratings_indices
]
print('Showing recommendations for users: {}'.format(user_id))
print('===' * 9)
print('Anime with high ratings from user')
print('----' * 8)
top_anime_user = (
    anime_watched_by_user.sort_values(
        by = 'rating',
        ascending=False
    )
    .head(5)
    .anime_id.values
)
anime_df_rows = anime[anime['anime_id'].isin(top_anime_user)]
for row in anime_df_rows.itertuples():
    print(row.title, ':', row.genre)
print('----' * 8)
print('Top 10 anime recommendation')
print('----' * 8) 
recommended_anime = anime[anime['anime_id'].isin(recommended_anime_ids)]
for row in recommended_anime.itertuples():
    print(row.title, ':', row.genre)