import pandas as pd
df = pd.read_csv('tweets.csv', encoding='utf-8')

#print(df.head())

# prepare expressions
tokenizer        = lambda tweet : tweet.split()
to_lower_expr    = lambda tokens: [token.lower() for token in tokens]
del_digits_expr  = lambda tokens: [token for token in tokens if token.isnumeric() == False]
del_letters_expr = lambda tokens: [token for token in tokens if len(token) > 2]

# execute
df['token'] = df['text'].apply(tokenizer)
df['token'] = df['token'].apply(to_lower_expr)
df['token'] = df['token'].apply(del_digits_expr)
df['token'] = df['token'].apply(del_letters_expr)