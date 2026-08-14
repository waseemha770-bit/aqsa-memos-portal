from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import urllib.request
import codecs

app = FastAPI()

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1LWymAvzOBfwblAiWIWOsKpj0KTMx8MjaIBZTet12u5g/export?format=csv&gid=0"

@app.get("/api/search")
def search_memo(query: str = ""):
    if not query:
        return JSONResponse(content={"results": []})
    
    try:
        # إضافة User-Agent حتى لا تقوم سيرفرات جوجل بحظر الطلب
        req = urllib.request.Request(SHEET_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        
        # قراءة البيانات كملف CSV
        reader = csv.DictReader(codecs.iterdecode(response, 'utf-8'))
        
        results = []
        for row in reader:
            # مطابقة العناوين حرفياً كما هي في الصف الأول من الإكسل
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
        raise HTTPException(status_code=500, detail="خطأ في قراءة قاعدة البيانات")
