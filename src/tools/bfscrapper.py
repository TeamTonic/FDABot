import pandas as pd
import requests
import os
import json
from bs4 import BeautifulSoup
import re
import string

def clean_title(title):
    """
    Cleans the title string for URL construction by removing or replacing certain characters and words.
    """
    # Remove date and colon
    title_parts = title.split(':', 1)
    if len(title_parts) > 1:
        title = title_parts[1].strip()
    else:
        title = title_parts[0].strip()

    # Convert to lower case and remove punctuation
    title = title.lower()
    title = title.translate(str.maketrans('', '', string.punctuation))

    # Remove common articles, prepositions, and conjunctions.
    stopwords = {'a', 'an', 'and', 'or', 'the', 'in', 'to', 'of', 'for', 'on', 'at', 'by', 'with', 'as', 'from',
                 'ceo', 'fda', 'will', 'be', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'these', 'those',
                 'he', 'she', 'they', 'them', 'his', 'her', 'its', 'their', 'here', 'there', 'who', 'whom',
                 'which', 'do', 'does', 'did', 'done', 'has', 'have', 'having', 'had', 'not', 'but', 'if', 'than',
                 'then', 'else', 'when', 'so', 'because', 'man', 'woman', 'men', 'women', 'sent', 'us', 'company'}

    title_words = title.split()
    title_words = [word for word in title_words if word not in stopwords]

    # Limit the length of the title to a reasonable number of words (e.g., 15 words)
    title_words = title_words[:15]

    # Join words with hyphens
    cleaned_title = '-'.join(title_words)
    
    # Handle known issues with ending words in URLs by trimming unnecessary hyphens
    cleaned_title = cleaned_title.strip('-')

    # Remove any consecutive hyphens if any
    cleaned_title = re.sub(r'[-]+', '-', cleaned_title)

    return cleaned_title

def get_article_content(cleaned_title):
    """
    Fetch the content of an article given the cleaned title.
    """
    # Construct the URL based on FDA press release structure
    url = f"https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/press-releases/{cleaned_title}"
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article', id='main_content')
        if not article:
            article = soup.find('div', id='main-content')
        if article:
            return article.get_text(strip=True)
        else:
            print(f"No main content found for URL: {url}")
            return None
    else:
        print(f"Failed to fetch URL: {url} with status code: {response.status_code}")
        return None

def save_article_to_file(title, content, output_dir):
    """
    Saves the content of an article to a text file in the specified output directory.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Construct file path
    filename = f"{clean_title(title)}.txt"
    filepath = os.path.join(output_dir, filename)
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Saved article: {title} to {filepath}")

def main():
    # Path to the input CSV file
    csv_file_path = 'src/tools/article_titles.csv'
    # Directory to save the output articles
    output_dir = 'res/directory/articles'

    # Load the DataFrame
    df = pd.read_csv(csv_file_path, header=None, names=['Title'])

    articles = []
    for index, row in df.iterrows():
        title = row['Title']
        cleaned_title = clean_title(title)
        article_content = get_article_content(cleaned_title)
        if article_content:
            save_article_to_file(title, article_content, output_dir)
            articles.append({'title': title, 'content': article_content})
        else:
            print(f"Failed to retrieve content for: {title}")

    # Save all articles to a JSON file
    json_file = os.path.join(output_dir, 'articles.json')
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(articles, file, indent=4, ensure_ascii=False)

    print(f'Saved {len(articles)} articles to {json_file}')

if __name__ == "__main__":
    main()