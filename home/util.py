from pypdf import PageObject, PdfReader
from pathlib import Path
from shutil import rmtree
import os
import zipfile
import pathlib

import puremagic

class ImageExtractor:
    def __init__(self, pdfPath) -> None:
        self.pdfPath = pdfPath
        self.BASE_DIR = os.path.dirname(self.pdfPath)
    
    def __create_img_folder(self):
        imgDir = f'{Path(self.pdfPath).stem}-images'
        self.imgDirPath = os.path.join(self.BASE_DIR, imgDir)
        if not os.path.exists(self.imgDirPath):
            os.mkdir(self.imgDirPath)
    
    def __extract_pages(self):
        reader = PdfReader(self.pdfPath)
        for page in reader.pages:
            self.__extract_image(page)

    def __extract_image(self, page: PageObject):
        for count, image_file_object in enumerate(page.images):
            img_path_abs = os.path.join(self.imgDirPath, f'{count}_{image_file_object.name}')
            with open(img_path_abs, "wb") as fp:
                fp.write(image_file_object.data)
    
    def save_image(self):
        self.__create_img_folder()
        self.__extract_pages()


class ZipCreator:
    def __init__(self, dir_path) -> None:
        self.dir_path = pathlib.Path(dir_path)
        self.FILE_NAME = self.dir_path.name

    def create_zip(self):
        self.ZIP_PATH = f'{self.dir_path}.zip'
        with zipfile.ZipFile(self.ZIP_PATH, mode="w") as archive:
            for file_path in self.dir_path.iterdir():
                archive.write(file_path, arcname=file_path.name)
    
    def delete_used_folder(self):
        rmtree(self.dir_path)


class PdfValidator:
    def __init__(self, doc, max_mb):
        self.content = doc.read(2048)
        self.size_bytes = doc.size
        self.max_mb = max_mb

    def is_pdf(self):
        try:
            if puremagic.from_string(self.content, mime=True) in ('application/pdf', ):
                return True
        except Exception: ...
        return False
    
    def __sizebytesToMb(self):
        size_mb = self.size_bytes / (1<<20)
        return size_mb

    def valid_size(self):
        return self.__sizebytesToMb() <= 30