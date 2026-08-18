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

# تحديث البيانات كل 60 ثانية (يتحمل آلاف المراجعين في هذه الدقيقة دون الاتصال بجوجل)
CACHE_TTL = 60 

@app.get("/api/search")
def search_memo(query: str = ""):
    query = query.strip()
    if not query:
        return JSONResponse(content={"results": []})
    
    if not SHEET_CSV_URL:
        raise HTTPException(status_code=500, detail="متغير SHEET_URL مفقود في إعدادات Vercel")
    
    current_time = time.time()
    
    # التحقق مما إذا كانت البيانات في الذاكرة قديمة (مرت دقيقة) وتحتاج تحديث
    if current_time - cache["last_updated"] > CACHE_TTL:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            clean_url = SHEET_CSV_URL.strip()
            response = requests.get(clean_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            lines = (line.decode('utf-8') for line in response.iter_lines())
            reader = csv.DictReader(lines)
            
            # تخزين كل البيانات في الذاكرة المؤقتة
            cache["data"] = list(reader)
            cache["last_updated"] = current_time
            
        except Exception as e:
            # إذا فشل الاتصال بجوجل لسبب ما، سنحاول استخدام البيانات القديمة المخزنة إن وجدت
            if not cache["data"]:
                raise HTTPException(status_code=500, detail=f"خطأ في جلب البيانات من جوجل: {str(e)}")

    # البحث داخل الذاكرة المؤقتة (سريع جداً ولن يسبب حظر من جوجل)
    results = []
    for row in cache["data"]:
        memo_num = str(row.get('رقم المذكرة', '')).strip()
        
        # مطابقة تامة وحصرية لرقم المذكرة المدخل
        if query == memo_num:
            results.append({
                "memo_number": memo_num,
                "received_date": row.get('تاريخ إستلام المذكرة', ''),
                "status": row.get('حالة المذكرة', ''),
                "date": row.get('تاريخ التوجيه', ''), # تم التحديث إلى تاريخ التوجيه هنا
                "notes": row.get('ملاحظات', '')
            })
            
    return JSONResponse(content={"results": results})
