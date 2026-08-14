from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import requests
import codecs
import os  # مكتبة للتعامل مع متغيرات البيئة

app = FastAPI()

# قراءة الرابط السري من بيئة Vercel بدلاً من كتابته مكشوفاً
SHEET_CSV_URL = os.getenv("SHEET_URL")

@app.get("/api/search")
def search_memo(query: str = ""):
    if not query:
        return JSONResponse(content={"results": []})
    
    # حماية إضافية: التأكد من أن الرابط موجود في إعدادات Vercel
    if not SHEET_CSV_URL:
        print("Error: SHEET_URL environment variable is missing.")
        raise HTTPException(status_code=500, detail="إعدادات قاعدة البيانات غير مكتملة في الخادم")
    
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        
        lines = (line.decode('utf-8') for line in response.iter_lines())
        reader = csv.DictReader(lines)
        
        results = []
        for row in reader:
            memo_num = str(row.get('رقم المذكرة', '')).strip()
            
            if query in memo_num:
                results.append({
                    "memo_number": memo_num,
                    "status": row.get('حالة المذكرة', ''),
                    "date": row.get('تاريخ التحديث', ''),
                    "notes": row.get('ملاحظات', '')
                })
                
        return JSONResponse(content={"results": results})
        
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="خطأ داخلي")
