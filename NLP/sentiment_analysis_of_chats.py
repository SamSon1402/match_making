# -*- coding: utf-8 -*-
"""Sentiment_Analysis_of_chats.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XbaZvLhWx_QvRa7j_MDim556GN698Xjy
"""

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from string import punctuation
from nltk.tokenize import word_tokenize
from nltk.stem import LancasterStemmer

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import re
import warnings
warnings.filterwarnings('ignore')

# Set display options for pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Load the training and test data
train_data = pd.read_csv('/content/train.csv', encoding='latin1')
test_data = pd.read_csv('/content/test.csv', encoding='latin1')

# Combine train and test data
df = pd.concat([train_data, test_data])

# Display the first few rows of the dataframe
df.head()

# Display information about the dataframe
df.info()

# Function to remove unnecessary characters from text
def remove_unnecessary_characters(text):
    text = re.sub(r'<.*?>', '', str(text))  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s]', '', str(text))  # Remove non-alphanumeric characters
    text = re.sub(r'\s+', ' ', str(text)).strip()  # Remove extra whitespace
    return text

# Apply the function to create a new 'clean_text' column
df['clean_text'] = df['text'].apply(remove_unnecessary_characters)

# Function to tokenize text
def tokenize_text(text):
    try:
        text = str(text)
        tokens = word_tokenize(text)
        return tokens
    except Exception as e:
        print(f"Error tokenizing text: {e}")
        return []

# Apply the tokenization function to create a 'tokens' column
df['tokens'] = df['text'].apply(tokenize_text)

# Function to normalize text
def normalize_text(text):
    if isinstance(text, str):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
    else:
        text = str(text)
    return text

# Apply the normalization function to create a 'normalized_text' column
df['normalized_text'] = df['text'].apply(normalize_text)

# Remove rows with missing values
df.dropna(inplace=True)

# Plot sentiment distribution
df['sentiment'].value_counts(normalize=True).plot(kind='bar')

# Display sentiment value counts
df['sentiment'].value_counts()

# Convert sentiment to numeric codes and plot distribution
df['sentiment_code'] = df['sentiment'].astype('category').cat.codes
sentiment_distribution = df['sentiment_code'].value_counts(normalize=True)
sentiment_distribution.plot(kind='bar')
plt.show()

# Plot histogram of sentiment distribution
sns.histplot(df['sentiment'], kde=True, color='r')
plt.show()

# Download NLTK stopwords
import nltk
nltk.download('stopwords')

# Prepare stopwords and stemmer
stuff_to_be_removed = list(stopwords.words('english')) + list(punctuation)
stemmer = LancasterStemmer()
corpus = df['text'].tolist()
print(len(corpus))
print(corpus[0])

# Download NLTK punkt for tokenization
nltk.download('punkt')

# Plot word frequency distribution
word_freq = FreqDist(word_tokenize(' '.join(df['sentiment'])))
plt.figure(figsize=(10, 6))
word_freq.plot(20, cumulative=False)
plt.title('Word Frequency Distribution')
plt.xlabel('Word')
plt.ylabel('Frequency')
plt.show()

# Prepare final corpus and create a new dataframe for EDA
final_corpus = df['text'].astype(str).tolist()
data_eda = pd.DataFrame()
data_eda['text'] = final_corpus
data_eda['sentiment'] = df["sentiment"].values
data_eda.head()

# Convert categorical columns to numeric
df['Time of Tweet'] = df['Time of Tweet'].astype('category').cat.codes
df['Country'] = df['Country'].astype('category').cat.codes
df['Age of User'] = df['Age of User'].replace({'0-20':18, '21-30':25, '31-45':38, '46-60':53, '60-70':65, '70-100':80})

# Drop unnecessary columns
df = df.drop(columns=['textID', 'Time of Tweet', 'Age of User', 'Country', 'Population -2020', 'Land Area (Km²)', 'Density (P/Km²)'])

# Function to preprocess text
import string
def wp(text):
    text = re.sub('https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub('<.*?>+', '', text)  # Remove HTML tags
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)  # Remove punctuation
    text = re.sub('\n', '', text)  # Remove newlines
    text = re.sub('\w*\d\w*', '', text)  # Remove words containing numbers
    return text

# Apply preprocessing to 'selected_text' column
df['selected_text'] = df["selected_text"].apply(wp)

# Prepare features and target
X = df['selected_text']
y = df['sentiment']

# Split data into training and testing sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize text data
from sklearn.feature_extraction.text import TfidfVectorizer
vectorization = TfidfVectorizer()
XV_train = vectorization.fit_transform(X_train)
XV_test = vectorization.transform(X_test)

# Calculate baseline score
score_baseline = df['sentiment'].value_counts(normalize=True).max()
score_baseline

# Train Logistic Regression model
from sklearn.linear_model import LogisticRegression
lr = LogisticRegression(n_jobs=-1)
lr.fit(XV_train, y_train)

# Make predictions using Logistic Regression
pred_lr = lr.predict(XV_test)

# Calculate accuracy score for Logistic Regression
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
score_lr = accuracy_score(y_test, pred_lr)
score_lr

# Train Decision Tree Classifier
from sklearn.tree import DecisionTreeClassifier
dt = DecisionTreeClassifier()
dt.fit(XV_train, y_train)

# Make predictions using Decision Tree
pred_dt = dt.predict(XV_test)

# Calculate accuracy score for Decision Tree
score_dt = dt.score(XV_test, y_test)
score_dt

# Print classification report for Decision Tree
print(classification_report(y_test, pred_dt))

# Display confusion matrix for Decision Tree
ConfusionMatrixDisplay.from_predictions(y_test, pred_dt)

# Train Random Forest Classifier
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(random_state=0)
rfc.fit(XV_train, y_train)

# Make predictions using Random Forest
pred_rfc = rfc.predict(XV_test)

# Calculate accuracy score for Random Forest
score_rfc = rfc.score(XV_test, y_test)
score_rfc

# Print classification report for Random Forest
print(classification_report(y_test, pred_rfc))

# Display confusion matrix for Random Forest
ConfusionMatrixDisplay.from_predictions(y_test, pred_rfc)

# Print accuracy scores for all models
print(f'Baseline model: {score_baseline}\nLogistic regression: {score_lr}\nDecision Tree Classification: {score_dt}\nRandom Forest Classifier: {score_rfc}')

# Function to output sentiment label
def output_lable(n):
    if n == 0:
        return "The Text Sentiment is Negative"
    elif n == 1:
        return "The Text Sentiment is Neutral"
    elif n == 2:
        return "The Text Sentiment is Positive"

# Function for manual testing of sentiment analysis
def manual_testing(news):
    testing_news = {"text": [news]}
    new_def_test = pd.DataFrame(testing_news)
    new_def_test["text"] = new_def_test["text"].apply(wp)
    new_x_test = new_def_test["text"]
    new_xv_test = vectorization.transform(new_x_test)
    pred_lr = lr.predict(new_xv_test)
    pred_dt = dt.predict(new_xv_test)
    pred_rfc = rfc.predict(new_xv_test)

    return print((output_lable(pred_lr[0])))

# Example usage of manual testing
text = "I am Sad"
manual_testing(text)