from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import csv
import requests
import codecs

app = FastAPI()

# الرابط الجديد لملف Google Sheets بصيغة CSV
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1uuWTYznUJ8mthH5nQggig4vA5l8EDhwq4aDrgTNaXyA/export?format=csv&gid=0"

@app.get("/api/search")
def search_memo(query: str = ""):
    if not query:
        return JSONResponse(content={"results": []})
    
    try:
        # استخدام مكتبة requests مع User-Agent يحاكي متصفحاً حقيقياً لمنع حظر الطلب من خوادم جوجل
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(SHEET_CSV_URL, headers=headers)
        
        # التحقق من نجاح جلب البيانات
        response.raise_for_status()
        
        # قراءة البيانات كملف CSV سطراً بسطر
        lines = (line.decode('utf-8') for line in response.iter_lines())
        reader = csv.DictReader(lines)
        
        results = []
        for row in reader:
            # استخدام .strip() لإزالة أي مسافات زائدة قد تكون موجودة في الإكسل بالخطأ
            memo_num = str(row.get('رقم المذكرة', '')).strip()
            
            # البحث إذا كان الرقم المدخل موجوداً ضمن رقم المذكرة
            if query in memo_num:
                results.append({
                    "memo_number": memo_num,
                    "status": row.get('حالة المذكرة', ''),
                    "date": row.get('تاريخ التحديث', ''),
                    "notes": row.get('ملاحظات', '')
                })
                
        return JSONResponse(content={"results": results})
        
    except requests.exceptions.RequestException as e:
        print("Network or Fetch Error:", str(e))
        raise HTTPException(status_code=500, detail="خطأ في الشبكة أو في جلب البيانات من Google Sheets")
    except Exception as e:
        print("General Error:", str(e))
        raise HTTPException(status_code=500, detail="خطأ داخلي في الخادم")
