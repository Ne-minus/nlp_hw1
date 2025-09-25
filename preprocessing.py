from email import policy
from email.parser import Parser
from email.generator import BytesGenerator
import pandas as pd
from pandarallel import pandarallel
import re
import nltk
nltk.download('punkt_tab')



def create_eml_from_string(raw_email_string, filename="output.eml"):
    msg = Parser(policy=policy.default).parsestr(raw_email_string)

    body = msg.get_body(preferencelist=('plain', 'html'))
    if body:
        text = body.get_content()       
    else:
        text = msg.get_content()

    text = re.sub(r"\s+", " ", text).strip() 
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"http\S+|www\. \S+", " ", text)
    text = re.sub(r"-{2,}.*forwarded by.*", " ", text, flags=re.IGNORECASE|re.DOTALL)
    text = text.lower()
    return text
  
  
def clean_docs(raw_corpus_path: str) -> pd.DataFrame:
  emails = pd.read_csv(raw_corpus_path)
  pandarallel.initialize(progress_bar=True, nb_workers=6)
  emails["clean"] = emails["message"].parallel_apply(create_eml_from_string)
  emails["clean"] = emails["clean"].parallel_apply(nltk.word_tokenize)
  
  return emails["clean"]


if __name__ == "__main__":
  texts = clean_docs("emails_clean.csv")
  texts.to_csv("emails_clean_last.csv")