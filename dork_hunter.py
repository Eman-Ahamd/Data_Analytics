from googlesearch import search
import time

def get_pdf_links(query, num_files=5):
    dork_query = f'filetype:pdf site:edu "{query}"'
    print(f"Searching for: {dork_query}")
    
    links = []
    try:
        # البحث عن الروابط
        for url in search(dork_query, num_results=num_files):
            if url.endswith('.pdf'):
                links.append(url)
                print(f"Found: {url}")
            time.sleep(2) 
    except Exception as e:
        print(f"Error during search: {e}")
    
    return links

if __name__ == "__main__":
    
    found_links = get_pdf_links("Cloud Computing", num_files=3)
    print(f"\nTotal links found: {len(found_links)}")