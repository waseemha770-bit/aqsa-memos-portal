from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import requests
import codecs

app = FastAPI()

# الرابط الجديد والمستقر جداً (Publish to the web)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTF1_wbO7ykf839iJGnoa6A5ekzwDRVioeL3OE992tdsLk0A4Q68l2H1RhTqxh-G1UZFgQyYZHT54qV/pub?output=csv"

@app.get("/api/search")
def search_memo(query: str = ""):
    if not query:
        return JSONResponse(content={"results": []})
    
    try:
        # جلب البيانات مباشرة (الرابط المنشور لا يحتاج إلى User-Agent معقد)
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        
        # قراءة البيانات سطراً بسطر
        lines = (line.decode('utf-8') for line in response.iter_lines())
        reader = csv.DictReader(lines)
        
        results = []
        for row in reader:
            # تنظيف المسافات وجلب البيانات
            memo_num = str(row.get('رقم المذكرة', '')).strip()
            
            if query in memo_num:
                results.append({
                    "memo_number": memo_num,
                    "status": row.get('حالة المذكرة', ''),
                    "date": row.get('تاريخ التحديث', ''),
                    "notes": row.get('ملاحظات', '')
                })
                
        return JSONResponse(content={"results": results})
        
    except requests.exceptions.RequestException as e:
        print("Network Error:", str(e))
        raise HTTPException(status_code=500, detail="خطأ في جلب البيانات من الملف المنشور")
    except Exception as e:
        print("General Error:", str(e))
        raise HTTPException(status_code=500, detail="خطأ داخلي في معالجة البيانات")
