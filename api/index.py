from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import requests
import os

app = FastAPI()

SHEET_CSV_URL = os.getenv("SHEET_URL")

@app.get("/api/search")
def search_memo(query: str = ""):
    query = query.strip()
    if not query:
        return JSONResponse(content={"results": []})
    
    if not SHEET_CSV_URL:
        raise HTTPException(status_code=500, detail="متغير SHEET_URL مفقود في إعدادات Vercel")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        clean_url = SHEET_CSV_URL.strip()
        response = requests.get(clean_url, headers=headers)
        response.raise_for_status()
        
        lines = (line.decode('utf-8') for line in response.iter_lines())
        reader = csv.DictReader(lines)
        
        results = []
        for row in reader:
            memo_num = str(row.get('رقم المذكرة', '')).strip()
            
            # مطابقة تامة وحصرية لرقم المذكرة المدخل
            if query == memo_num:
                results.append({
                    "memo_number": memo_num,
                    "received_date": row.get('تاريخ إستلام المذكرة', ''),
                    "status": row.get('حالة المذكرة', ''),
                    "date": row.get('تاريخ التحديث', ''),
                    "notes": row.get('ملاحظات', '')
                })
                
        return JSONResponse(content={"results": results})
        
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"جوجل رفض الرابط: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"تفاصيل الخطأ الدقيقة: {str(e)}")
