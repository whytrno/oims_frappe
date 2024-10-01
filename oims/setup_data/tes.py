import json
import os

def add_keys_to_json(file_path, source_key, new_key_nama, new_key_doctype):
    # Baca file JSON yang ada
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
        return
    except json.JSONDecodeError:
        print(f"Kesalahan dalam decoding file JSON di {file_path}.")
        return

    # Dapatkan nama doctype dari nama file (tanpa ekstensi dan huruf pertama kapital)
    doctype_value = os.path.splitext(os.path.basename(file_path))[0].capitalize()

    # Fungsi untuk menambahkan key baru
    def add_keys(data):
        if isinstance(data, list):
            for item in data:
                add_keys(item)  # Rekursif untuk item dalam list
        elif isinstance(data, dict):
            if source_key in data:
                data[new_key_nama] = data[source_key]  # Menambahkan key 'nama'
                data[new_key_doctype] = doctype_value    # Menambahkan key 'doctype'

    # Menambahkan key baru ke data
    add_keys(data)

    # Simpan kembali ke dalam file JSON
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)  # Simpan dengan indentasi yang rapi

    print(f"Key '{new_key_nama}' dan '{new_key_doctype}' telah ditambahkan di {file_path}.")

# Daftar file JSON yang akan diubah
json_files = [
    'data/provinsi.json',
    'data/kecamatan.json',
    'data/kabupaten.json',
    'data/desa.json'
]

# Menambahkan key nama dan doctype di semua file yang ditentukan
for file_path in json_files:
    add_keys_to_json(file_path, 'name', 'nama', 'doctype')
