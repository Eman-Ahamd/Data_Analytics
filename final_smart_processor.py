import os
import requests
import pandas as pd
import docx
from PyPDF2 import PdfReader
from urllib.parse import quote
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import time

# 1. إعدادات السحاب
PROJECT_URL = "https://hlejdhvbvhtmqnbklpua.supabase.co"
API_KEY = "sb_publishable_achG6va9DwRxyLSRDmO1oQ_jydUcd9R "
BUCKET_NAME = "documents"

# 2. مخ الذكاء الاصطناعي (التدريب)
training_data = {
    'text': [
        "Artificial Intelligence", "Search", "Search Continued", "Supervised learning",
        "Cloud-Based Databases", "Cloud Platform Architecture over Virtualized Data Centers",
        "Course Title: Graduation Research (CSCI4108)", "Distributed System Models",
        "Cloud Programming", "Multitenant Data Platforms", "Data in the Cloud", "Virtual Machines"
    ],
    'label': [
        "Technical", "Technical", "Technical", "Technical", "Technical", 
        "Technical", "Technical", "Technical", "Technical", "Technical", 
        "Technical", "Technical"
    ]
}
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(training_data['text'])
clf = RandomForestClassifier().fit(X, training_data['label'])

def get_internal_title_and_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    full_text = ""
    internal_title = "Unknown"
    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            full_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            internal_title = lines[0] if lines else "Untitled PDF"
        elif ext == ".docx":
            doc = docx.Document(file_path)
            full_text = " ".join([p.text for p in doc.paragraphs])
            for para in doc.paragraphs:
                if para.text.strip():
                    internal_title = para.text.strip()
                    break
    except: pass
    return internal_title, full_text

def process_all_files(folder_path):
    processed_data = []
    total_size_bytes = 0
    
    print("--- 🚀 بدء معالجة الملفات وحساب المقاييس ---")
    
    # مقاييس الوقت
    start_total_process = time.time()
    classification_times = []

    # الخطوة 1: القراءة والاستخراج والتصنيف
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".pdf", ".docx")):
            path = os.path.join(folder_path, filename)
            file_size = os.path.getsize(path)
            total_size_bytes += file_size
            
            title, content = get_internal_title_and_content(path)
            
            # حساب وقت التصنيف لكل ملف
            start_clf = time.time()
            pred = clf.predict(vectorizer.transform([content[:500]]))[0]
            end_clf = time.time()
            classification_times.append(end_clf - start_clf)
            
            processed_data.append({
                "title": title,
                "content": content,
                "category": pred,
                "path": path,
                "filename": filename
            })

    # الخطوة 2: حساب وقت الفرز (Sorting Time)
    start_sort = time.time()
    processed_data.sort(key=lambda x: x['title'].lower())
    end_sort = time.time()
    
    sorting_duration = end_sort - start_sort
    avg_classification_time = sum(classification_times) / len(classification_times) if classification_times else 0
    total_process_duration = time.time() - start_total_process

    # الخطوة 3: الرفع للسحاب
    headers = {"Authorization": f"Bearer {API_KEY}", "apikey": API_KEY}
    for item in processed_data:
        storage_url = f"{PROJECT_URL}/storage/v1/object/{BUCKET_NAME}/{quote(item['filename'])}"
        with open(item['path'], 'rb') as f:
            if requests.post(storage_url, headers=headers, data=f).status_code in [200, 201]:
                db_payload = {
                    "file_name": item['title'],
                    "category": item['category'],
                    "full_content": item['content'],
                    "file_url": f"{PROJECT_URL}/storage/v1/object/public/{BUCKET_NAME}/{quote(item['filename'])}"
                }
                requests.post(f"{PROJECT_URL}/rest/v1/document_metadata", headers=headers, json=db_payload)

    #عرض النتائج
    print("\n" + "="*40)
    print("📊 إحصائيات المشروع (Statistics):")
    print(f"1. عدد الملفات المعالجة: {len(processed_data)} ملفات")
    print(f"2. الحجم الإجمالي للملفات: {total_size_bytes / 1024:.2f} KB")
    print(f"3. الوقت المقتطع للفرز الأبجدي: {sorting_duration:.6f} ثانية")
    print(f"4. متوسط وقت التصنيف لكل ملف: {avg_classification_time:.6f} ثانية")
    print(f"5. الوقت الإجمالي للمعالجة والرفع: {total_process_duration:.2f} ثانية")
    print("="*40)

if __name__ == "__main__":
    process_all_files("./data")