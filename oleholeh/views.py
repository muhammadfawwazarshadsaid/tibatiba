import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import google.generativeai as genai
from django.contrib.gis.geoip2 import GeoIP2
from django.utils.http import unquote

# Konfigurasi Gemini AI
genai.configure(api_key="AIzaSyDw8pJxo89LRpKy6UVJ_79hQVbSvY1fvHY")
model = genai.GenerativeModel('gemini-1.5-flash')

@csrf_exempt
def getalloleholeh_similarplace(request):
    g = GeoIP2()
    address = "36.73.158.233"        
    # remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
    # if remote_addr:
    #     address = remote_addr.split(',')[-1].strip()
    # else:
    #     address = request.META.get('REMOTE_ADDR')

    try:
        city = g.city(address)
        city_name = city.get('city', 'Unknown')
    except Exception as e:
        return JsonResponse({
            'error': f"Gagal mendapatkan lokasi: {str(e)}"
        })

    # Query SQL untuk mendapatkan data berdasarkan city_place yang relevan
    query = """
    SELECT 
        a.price, 
        a.oleholeh_nama AS nama_oleholeh, 
        p.oleh_oleh_provider_name AS nama_pemilik,
        a.photo AS gambar
    FROM public."OlehOlehAffiliated" a
    JOIN public."OlehOlehProvider" p 
        ON a.oleholeh_provider_id = p.oleholeh_provider_id
    WHERE p.city_place LIKE %s
    """

    # Menggunakan Gemini AI untuk menyarankan nama kota yang relevan
    try:
        response = model.generate_content(f"Tentukan kemungkinan (satu atau bisa lebih) nama kota dalam jangkauan 100km yang relevan atau sama persis atau cocok atau typo sedikit atau serupa dengan '{city_name}'. Kota {city_name} suda pasti include. Masukkan ke dalam list dipisah koma tanpa penjelasan apapun (kata terakhir tanpa koma). Misal: Yogyakarta, serupa dengan Kota Jogja, DIY, DIY Jogjakarta, dan seterusnya")
        suggested_city_names = response.text.strip()
        print(f"Suggested City Names: {suggested_city_names}")
    except Exception as e:
        return JsonResponse({
            'error': f"Gagal mendapatkan nama kota yang relevan: {str(e)}"
        })

    # Pisahkan nama kota yang disarankan
    city_names = [name.strip() for name in suggested_city_names.split(',')]

    # Buat string query dengan beberapa pola LIKE
    like_patterns = [f"%{name}%" for name in city_names]
    print(f"LIKE Patterns: {like_patterns}")
    # Pisahkan nama kota yang disarankan
    city_names = [name.strip() for name in suggested_city_names.split(',')]

    # Buat string query dengan beberapa pola LIKE
    like_patterns = [f"%{name}%" for name in city_names]

    # Update query untuk menangani beberapa pola LIKE
    query = f"""
    SELECT 
        a.price, 
        a.oleholeh_nama AS nama_oleholeh, 
        p.oleh_oleh_provider_name AS nama_pemilik,
        a.photo AS gambar
    FROM public."OlehOlehAffiliated" a
    JOIN public."OlehOlehProvider" p 
        ON a.oleholeh_provider_id = p.oleholeh_provider_id
    WHERE {' OR '.join(['p.city_place LIKE %s'] * len(like_patterns))}
    """

    # Gabungkan semua pola LIKE dalam satu list
    parameters = like_patterns

    with connection.cursor() as cursor:
        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            print(f"Rows Retrieved: {rows}")
        except Exception as e:
            print(f"Database query error: {str(e)}")


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
    
    if results == [] :
        results.append("Tidak ada data yang cocok saat ini. Coba lagi")

    if not results:
        results = [{
            "error": "Tidak ada data yang cocok saat ini. Coba lagi"
        }]

    return JsonResponse({
        "ip_address": address,
        "city_name": city_name,
        "results": results
    }, safe=False)

@csrf_exempt
def gettopten(request):
    # Query to get top 10 providers based on the number of affiliated items
    query = """
    SELECT 
        p.oleholeh_provider_id,
        p.oleh_oleh_provider_name,
        COUNT(a.oleholeh_affiliated_id) AS jumlah_etalase
    FROM public."OlehOlehProvider" p
    LEFT JOIN public."OlehOlehAffiliated" a
        ON p.oleholeh_provider_id = a.oleholeh_provider_id
    GROUP BY p.oleholeh_provider_id
    ORDER BY jumlah_etalase DESC
    LIMIT 10
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            results = [
                {
                    "provider_id": row[0],
                    "provider_name": row[1],
                    "jumlah_etalase": row[2]
                }
                for row in rows
            ]

            return JsonResponse(results, safe=False)

        except Exception as e:
            return JsonResponse({'error': f"Database query error: {str(e)}"}, status=500)

@csrf_exempt
def getoleholeh_a_provider(request, provider_id):
    # Query untuk mendapatkan detail penyedia oleh-oleh
    provider_query = """
    SELECT 
        oleh_oleh_provider_name,
        oleholeh_provider_about,
        oleholeh_provider_sosmed,
        oleholeh_provider_photo,
        whatsapp_link,
        carapemesanan,
        city_place
    FROM public."OlehOlehProvider"
    WHERE oleholeh_provider_id = %s
    """

    # Query untuk mendapatkan detail oleh-oleh yang disediakan
    affiliated_query = """
    SELECT 
        a.price, 
        a.oleholeh_nama AS nama_oleholeh, 
        a.photo AS gambar, 
        a.weight_kg AS berat_per_kuantitas, 
        a.minimum_order AS minimal_order,
        CASE
            WHEN a.price <= 100000 THEN 1
            WHEN a.price <= 150000 THEN 2
            WHEN a.price <= 200000 THEN 3
            ELSE 4
        END AS tingkatkemurahan
    FROM public."OlehOlehAffiliated" a
    WHERE a.oleholeh_provider_id = %s
    """

    with connection.cursor() as cursor:
        try:
            # Mendapatkan informasi penyedia oleh-oleh
            cursor.execute(provider_query, [provider_id])
            provider_row = cursor.fetchone()
            if not provider_row:
                return JsonResponse({
                    'error': 'Provider not found.'
                }, status=404)

            # Mendapatkan informasi oleh-oleh terkait
            cursor.execute(affiliated_query, [provider_id])
            affiliated_rows = cursor.fetchall()

            # Struktur data untuk provider
            provider_data = {
                'nama_penyedia': provider_row[0],
                'tentang_toko': provider_row[1],
                'sosmed': provider_row[2],
                'foto_toko': provider_row[3],
                'link_whatsapp': provider_row[4],
                'cara_pemesanan': provider_row[5],
                'city_place': provider_row[6],
                'jumlah_jenis_oleh_oleh': len(affiliated_rows),
                'etalase_aktif': [
                    {
                        'harga': row[0],
                        'nama_oleh_oleh': row[1],
                        'gambar': row[2],
                        'berat_per_kuantitas': row[3],
                        'minimal_order': row[4],
                        'tingkatkemurahan': row[5]
                    } for row in affiliated_rows
                ]
            }

            return JsonResponse(provider_data, safe=False)

        except Exception as e:
            return JsonResponse({
                'error': f"Database query error: {str(e)}"
            }, status=500)

@csrf_exempt
def search_oleholeh(request, query):
    """Search for oleh-oleh providers and affiliated items based on the query string in the URL."""
    if request.method == 'GET':
        # Decode the query string from the URL
        decoded_query = unquote(query)
        print(f"Received query: {decoded_query}")

        # Menggunakan Gemini AI untuk menyarankan nama oleh-oleh dan toko yang relevan
        try:
            response = model.generate_content(f"Tentukan kemungkinan (satu atau bisa lebih) nama oleh-oleh dan nama toko yang relevan atau sama persis atau cocok atau typo sedikit atau serupa dengan '{decoded_query}'. Masukkan nama oleh-oleh dan toko ke dalam list dipisah koma tanpa penjelasan apapun (kata terakhir tanpa koma). Misal: Kue kering, Toko Kue Kering, serupa dengan kuekering, toko kue kering, dan seterusnya")
            suggested_names = response.text.strip()
            print(f"Suggested Names: {suggested_names}")
        except Exception as e:
            return JsonResponse({'error': f"Gagal mendapatkan nama yang relevan: {str(e)}"}, status=500)

        # Pisahkan nama oleh-oleh dan nama toko
        names = [name.strip() for name in suggested_names.split(',')]
        oleh_oleh_names = [name for name in names if 'toko' not in name.lower()]
        toko_names = [name for name in names if 'toko' in name.lower()]
        lokasi_names = [name for name in names if 'toko' in name.lower()]

        # Buat string query dengan beberapa pola LIKE
        like_patterns_oleh_oleh = [f"%{name}%" for name in oleh_oleh_names]
        like_patterns_toko = [f"%{name}%" for name in toko_names]
        like_patterns_lokasi = [f"%{name}%" for name in lokasi_names]
        print(f"LIKE Patterns Oleh-Oleh: {like_patterns_oleh_oleh}")
        print(f"LIKE Patterns Toko: {like_patterns_toko}")
        print(f"LIKE Patterns Lokasi: {like_patterns_lokasi}")

        # Update query untuk menangani pola LIKE untuk oleh-oleh dan toko
        query = f"""
        SELECT 
            a.price, 
            a.oleholeh_nama AS nama_oleholeh, 
            p.oleh_oleh_provider_name AS nama_pemilik,
            a.photo AS gambar,
            p.city_place AS lokasi
        FROM public."OlehOlehAffiliated" a
        JOIN public."OlehOlehProvider" p 
            ON a.oleholeh_provider_id = p.oleholeh_provider_id
        WHERE {' OR '.join(['a.oleholeh_nama ILIKE %s'] * len(like_patterns_oleh_oleh))}
            OR {' OR '.join(['p.oleh_oleh_provider_name ILIKE %s'] * len(like_patterns_toko))}
            OR {' OR '.join(['p.city_place ILIKE %s'] * len(like_patterns_lokasi))}
        """

        # Gabungkan semua pola LIKE dalam satu list
        parameters = like_patterns_oleh_oleh + like_patterns_toko + like_patterns_lokasi

        with connection.cursor() as cursor:
            try:
                cursor.execute(query, parameters)
                rows = cursor.fetchall()
                print(f"Rows Retrieved: {rows}")
            except Exception as e:
                return JsonResponse({'error': f"Database query error: {str(e)}"}, status=500)

        results = []
        for row in rows:
            # Update unpacking variabel sesuai dengan jumlah kolom
            price, nama_oleholeh, nama_pemilik, gambar, lokasi = row
            tingkat_kemurahan = 1 if price <= 100000 else 2 if price <= 150000 else 3 if price <= 200000 else 4
            results.append({
                "harga": price,
                "nama_oleholeh": nama_oleholeh,
                "nama_pemilik": nama_pemilik,
                "gambar": gambar,
                "lokasi": lokasi,  # Tambahkan lokasi ke hasil
                "tingkatkemurahan": tingkat_kemurahan
            })

        if not results:
            results.append({"message": "Tidak ada data yang cocok saat ini. Coba lagi"})

        return JsonResponse({
            "results": results
        }, safe=False)

    return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)



# def getall(request):
#     query = """
#     SELECT 
#         a.price, 
#         a.oleholeh_nama AS nama_oleholeh, 
#         p.oleh_oleh_provider_name AS nama_pemilik,
#         a.photo AS gambar
#     FROM public."OlehOlehAffiliated" a
#     JOIN public."OlehOlehProvider" p 
#         ON a.oleholeh_provider_id = p.oleholeh_provider_id
#     """

#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         rows = cursor.fetchall()

#     results = []
#     for row in rows:
#         price, nama_oleholeh, nama_pemilik, gambar = row
#         if price <= 100000:
#             tingkat_kemurahan = 1
#         elif price <= 150000:
#             tingkat_kemurahan = 2
#         elif price <= 200000:
#             tingkat_kemurahan = 3
#         else:
#             tingkat_kemurahan = 4
        
#         results.append({
#             "harga": price,
#             "nama_oleholeh": nama_oleholeh,
#             "nama_pemilik": nama_pemilik,
#             "gambar": gambar,
#             "tingkatkemurahan": tingkat_kemurahan
#         })

#     return JsonResponse(results, safe=False)


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
    
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.contrib.gis.geoip2 import GeoIP2

# def getlocation(request):
#     g = GeoIP2()
#     remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
#     if remote_addr:
#         address = remote_addr.split(',')[-1].strip()
#     else:
#         # address = request.META.get('103.60.233.178')
#         address = request.META.get('REMOTE_ADDR')
    
#     try:
#         # Mendapatkan lokasi berdasarkan IP
#         city = g.city(address)
#         city_name = city.get('city', 'Unknown')
#         region_name = city.get('region', 'Unknown')
        
#         # Mengembalikan hasil dalam format JSON
#         return JsonResponse({
#             'kota': city_name,
#             'provinsi': region_name
#         })
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e)
#         })