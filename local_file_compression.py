import zipfile

dirs = [
    "./src/handlers/company/get_company_handler.py",
    "./src/service/company/company_service.py",
    "./src/utils/query_builder.py",
    "./src/utils/response_sql.py",
    "./db/utils/connection.py",
    "./src/utils/company_anonymization.py",
]

folder_name = "dist/get_company_handler"


def zipfolder(foldername, target_dirs: list):
    zipobj = zipfile.ZipFile(foldername + ".zip", "w", zipfile.ZIP_DEFLATED)
    for target_dir in target_dirs:
        filename = target_dir.split("/")[-1]
        zipobj.write(target_dir, arcname=filename)
    zipobj.close()


zipfolder(folder_name, dirs)
