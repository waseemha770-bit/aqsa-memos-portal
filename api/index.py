from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import urllib.request
import codecs

app = FastAPI()

# رابط ملف جوجل شيتس بصيغة CSV (تأكد أن الملف عام للقراءة)
# تم إضافة gid=0 للإشارة إلى الورقة الأولى (المذكرات)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1LWymAvzOBfwblAiWIWOsKpj0KTMx8MjaIBZTet12u5g/export?format=csv&gid=0"

@app.get("/api/search")
def search_memo(query: str = ""):
    if not query:
        return JSONResponse(content={"results": []})
    
    try:
        # جلب البيانات مباشرة من قوقل شيتس
        response = urllib.request.urlopen(SHEET_CSV_URL)
        reader = csv.DictReader(codecs.iterdecode(response, 'utf-8'))
        
        results = []
        for row in reader:
            # المفاتيح هنا يجب أن تطابق عناوين الأعمدة في ملف الشيتس تماماً
            memo_num = str(row.get('رقم المذكرة', '')).strip()
            if query in memo_num:
                results.append({
                    "memo_number": memo_num,
                    "link": row.get('رابط', ''),
                    "date": row.get('تاريخ التحديث', ''),
                    "notes": row.get('ملاحظات', '')
                })
                
        return JSONResponse(content={"results": results})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
