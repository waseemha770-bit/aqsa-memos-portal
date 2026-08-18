from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import requests
import os
import time

app = FastAPI()

SHEET_CSV_URL = os.getenv("SHEET_URL")

# ذاكرة التخزين المؤقت (Cache) لحماية جوجل شيت من الضغط
cache = {
    "data": [],
    "last_updated": 0
}

# تحديث البيانات كل 60 ثانية (يمكنك تغييرها)
CACHE_TTL = 60 

@app.get("/api/search")
def search_memo(query: str = ""):
    query = query.strip()
    if not query:
        return JSONResponse(content={"results": []})
    
    if not SHEET_CSV_URL:
        raise HTTPException(status_code=500, detail="متغير SHEET_URL مفقود")
    
    current_time = time.time()
    
    # التحقق مما إذا كانت البيانات في الذاكرة قديمة وتحتاج تحديث
    if current_time - cache["last_updated"] > CACHE_TTL:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            clean_url = SHEET_CSV_URL.strip()
            response = requests.get(clean_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            lines = (line.decode('utf-8') for line in response.iter_lines())
            reader = csv.DictReader(lines)
            
            # تخزين كل البيانات في الذاكرة المؤقتة
            cache["data"] = list(reader)
            cache["last_updated"] = current_time
            
        except Exception as e:
            # إذا فشل الاتصال بجوجل، سنحاول استخدام البيانات القديمة إن وجدت
            if not cache["data"]:
                raise HTTPException(status_code=500, detail="خطأ في جلب البيانات من جوجل")

    # البحث داخل الذاكرة المؤقتة (سريع جداً ولن يتصل بجوجل)
    results = []
    for row in cache["data"]:
        memo_num = str(row.get('رقم المذكرة', '')).strip()
        
        if query == memo_num:
            results.append({
                "memo_number": memo_num,
                "received_date": row.get('تاريخ إستلام المذكرة', ''),
                "status": row.get('حالة المذكرة', ''),
                "date": row.get('تاريخ التحديث', ''),
                "notes": row.get('ملاحظات', '')
            })
            
    return JSONResponse(content={"results": results})
