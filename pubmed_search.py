# performed at 2024.10.09
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time

def search_pubmed(query, max_results=1000):
    # Search PubMed using the provided query and return the list of PMIDs.
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml"
    }
    # response = requests.get(url, params=params)
    response = requests.get(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=1000&retmode=xml&term={query}')

    if response.status_code != 200:
        raise Exception("Error fetching data from PubMed.")
    
    # Parse XML response to get the list of PMIDs
    root = ET.fromstring(response.content)
    id_list = [id_elem.text for id_elem in root.findall(".//Id")]
    return id_list

def fetch_article_details(pmids, batch_size=50):
    # Fetch details for each article using a list of PMIDs, in batches

    api_key = 'YOUR_API_KEY_HERE'
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    all_articles = []
    
    # Split the list of PMIDs into batches
    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        ids = ",".join(batch_pmids)
        
        # Make the request for the current batch
        request_url = f"{url}?db=pubmed&retmode=xml&id={ids}&api_key={api_key}"
        response = requests.get(request_url)
        if response.status_code != 200:
            # raise Exception("Error fetching article details from PubMed.")
            print("retrying...")
            time.sleep(10)
            response = requests.get(request_url)
            if response.status_code != 200:
                print('Error again')
                # raise Exception("Error fetching article details from PubMed.")
                print("retrying...")
                time.sleep(10)
                response = requests.get(request_url)
                if response.status_code != 200:
                    print('Error again')
                    print("retrying...")
                    time.sleep(10)
                    response = requests.get(request_url)
                    if response.status_code != 200:
                        print('Error again')
                        return all_articles

        
        # Parse XML response to get article details
        root = ET.fromstring(response.content)
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")
            try :
                abstract = ET.tostring(article.find('./MedlineCitation/Article/Abstract'), encoding='unicode')
            except:
                abstract = article.findtext(".//Abstract/AbstractText")
            pub_date = article.findtext(".//PubDate/Year") or article.findtext(".//PubDate/MedlineDate")
            journal = article.findtext(".//Journal/Title")
            article_type = article.findtext(".//PublicationType")
            affiliation = article.findtext(".//AffiliationInfo/Affiliation")
            authors = []
            for author in article.findall(".//Author"):
                last_name = author.findtext("LastName")
                fore_name = author.findtext("ForeName")
                if last_name and fore_name:
                    authors.append(f"{fore_name} {last_name}")
            authors = ", ".join(authors)
            article_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            all_articles.append({
                "PMID": pmid,
                "Title": title,
                "Abstract": abstract,
                "Published Date": pub_date,
                "Journal": journal,
                "Article Type": article_type,
                "Authors": authors,
                "Affiliation": affiliation,
                "Article URL": article_url
            })
        time.sleep(10)
        
    
    return all_articles

def save_to_excel(articles, filename="pubmed_results.xlsx"):
    # Save the list of articles to an Excel file.
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")

# Search term
query = "%28%28artificial+intelligence%5BTitle%5D+OR+machine+learning%5BTitle%5D+OR+deep+learning%5BTitle%5D%29+AND+%28stroke%5BTitle%5D+OR+thrombectomy%5BTitle%5D+OR+thrombolysis%5BTitle%5D+OR+cerebral+infarction%5BTitle%5D%29%29"

# Step 1: Search PubMed
print("Searching PubMed...")
pmids = search_pubmed(query)
if not pmids:
    print("No articles found.")
    exit()
print(f"Found {len(pmids)} articles.")

# Step 2: Fetch article details
print("Fetching article details...")
articles = fetch_article_details(pmids)

# Step 3: Save results to Excel
print("Saving results to Excel...")
save_to_excel(articles)

