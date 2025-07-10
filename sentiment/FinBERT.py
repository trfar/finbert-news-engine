import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from torch.nn.functional import softmax

# Load FinBERT model and tokenizer
model_name = "yiyanghkust/finbert-tone"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
model.eval()  # Inference mode

# Load your CSV
df = pd.read_csv("master.csv")

# Ensure 'sentiment' column exists
if 'sentiment' not in df.columns:
    df['sentiment'] = None

# Inference only on rows where sentiment is NaN or missing
for i, row in df[df['sentiment'].isna()].iterrows():
    sentence = str(row['body'])[:512]  # Truncate to 512 tokens
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = softmax(logits, dim=1)

        # Compute continuous sentiment score: [-1, 0, +1] weighted
        score = (-1) * probs[0, 0] + 0 * probs[0, 1] + 1 * probs[0, 2]
        df.at[i, 'sentiment'] = round(score.item(), 4)  # Round for cleaner output

# Save updated CSV
df.to_csv("master.csv", index=False)
print("✅ Sentiment column updated with softmax-weighted scores.")
