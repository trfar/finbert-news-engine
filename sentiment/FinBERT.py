from transformers import BertTokenizer, BertForSequenceClassification

# Loading FinBERT + Tokenizer
model_name = "yiyanghkust/finbert-tone"
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
tokenizer = BertTokenizer.from_pretrained(model_name)
