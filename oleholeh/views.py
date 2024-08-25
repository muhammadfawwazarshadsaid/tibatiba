from django.http import JsonResponse
from django.db import connection

def getall(request):
    query = """
    SELECT 
        a.price, 
        a.oleholeh_nama AS nama_oleholeh, 
        p.oleh_oleh_provider_name AS nama_pemilik,
        a.photo AS gambar
    FROM public."OlehOlehAffiliated" a
    JOIN public."OlehOlehProvider" p 
        ON a.oleholeh_provider_id = p.oleholeh_provider_id
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    results = []
    for row in rows:
        price, nama_oleholeh, nama_pemilik, gambar = row
        if price <= 100000:
            tingkat_kemurahan = 1
        elif price <= 150000:
            tingkat_kemurahan = 2
        elif price <= 200000:
            tingkat_kemurahan = 3
        else:
            tingkat_kemurahan = 4
        
        results.append({
            "harga": price,
            "nama_oleholeh": nama_oleholeh,
            "nama_pemilik": nama_pemilik,
            "gambar": gambar,
            "tingkatkemurahan": tingkat_kemurahan
        })

    return JsonResponse(results, safe=False)


# def getlocation(request):
#     remote_addr = "request.META.get('HTTP_X_FORWARDED_FOR')"
#     if remote_addr:
#         address = remote_addr.split(',')[-1].strip()
#     else:
#         address = request.META.get('REMOTE_ADDR')

#     try:
#         # API endpoint untuk batch processing
#         batch_endpoint = 'http://ip-api.com/batch'
        
#         # Membuat payload untuk request POST
#         payload = [address]
        
#         # Mengirimkan request POST ke API
#         response = requests.post(batch_endpoint, json=payload)
#         data = response.json()
        
#         # Memeriksa apakah ada hasil untuk IP yang diminta
#         if data:
#             result = data[0]  # Mengambil hasil dari batch response
#             city_name = result.get('city', 'Unknown')
#             region_name = result.get('regionName', 'Unknown')
            
#             return JsonResponse({
#                 'alamatip': remote_addr,
#                 'kota': city_name,
#                 'provinsi': region_name
#             })
#         else:
#             return JsonResponse({
#                 'error': 'No data returned from IP-API'
#             })
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e)
#         })
    
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.geoip2 import GeoIP2

def getlocation(request):
    g = GeoIP2()
    remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
    if remote_addr:
        address = remote_addr.split(',')[-1].strip()
    else:
        # address = request.META.get('103.60.233.178')
        address = request.META.get('REMOTE_ADDR')
    
    try:
        # Mendapatkan lokasi berdasarkan IP
        city = g.city(address)
        city_name = city.get('city', 'Unknown')
        region_name = city.get('region', 'Unknown')
        
        # Mengembalikan hasil dalam format JSON
        return JsonResponse({
            'kota': city_name,
            'provinsi': region_name
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })
