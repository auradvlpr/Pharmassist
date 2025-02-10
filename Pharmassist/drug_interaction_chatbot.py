from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import re
import os

# Modify the search query generation function to use Hugging Face
def generate_search_query(drugs):
    """Uses Hugging Face's pipeline to generate a search query for drug interactions."""
    # Load GPT-2 or another suitable model from Hugging Face
    generator = pipeline('text-generation', model='gpt2')
    
    prompt = f"List the side effects and possible interactions of taking {', '.join(drugs)} together."
    
    # Use the model to generate the search query
    result = generator(prompt, max_length=100, num_return_sequences=1)
    
    return result[0]['generated_text'].strip()

# Google search function (using the Google API)
def google_search(query, api_key, cx):
    """Uses Google Custom Search API to get search results."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    data = response.json()
    return [item['link'] for item in data.get("items", [])]

# Scraping function for extracting text from URLs
def scrape_page(url):
    """Extracts relevant content from a webpage."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    text = ' '.join([p.text for p in soup.find_all('p')])
    return text

# Function to extract side effects from the text
def extract_side_effects(text):
    """Extracts possible side effects using regex."""
    pattern = r"(dizziness|nausea|vomiting|headache|fatigue|rash|diarrhea|seizures|confusion)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return list(set(matches))

# Main chatbot function
def chatbot():
    """Main chatbot function to interact with users."""
    api_key = "AIzaSyBDeZsinAXgroG8zO8cvTfFSCHrWzSb3Xk"  # Your Google API Key
    cx = "d26957b980f1247ccD"  # Your Google Custom Search Engine ID

    while True:
        user_input = input("Enter drug names (comma separated) or 'exit': ")
        if user_input.lower() == 'exit':
            break

        drugs = [d.strip() for d in user_input.split(",")]
        search_query = generate_search_query(drugs)
        
        # Add this line to print the generated search query
        print(f"Search Query: {search_query}")

        search_results = google_search(search_query, api_key, cx)
        
        # Add this line to print the search results
        print(f"Search Results: {search_results}")

        extracted_info = []
        for url in search_results[:3]:  # Scraping top 3 results
            text = scrape_page(url)
            side_effects = extract_side_effects(text)
            if side_effects:
                extracted_info.extend(side_effects)

        if extracted_info:
            print(f"⚠️ Possible Side Effects of {', '.join(drugs)}: {', '.join(set(extracted_info))}")
        else:
            print("No clear interactions found. Please consult a medical professional.")


# Run the chatbot
if __name__ == "__main__":
    chatbot()
